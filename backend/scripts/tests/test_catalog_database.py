"""Integration tests: run only against an explicitly isolated catalog test database."""
import os
import uuid
import pytest
from sqlalchemy import text
from catalog import Catalog,BudgetExceeded
from catalog_common import fallback

pytestmark=pytest.mark.skipif(os.environ.get('CATALOG_TEST_DATABASE')!='true',reason='isolated DB required')

@pytest.fixture
def catalog():
    assert 'test' in os.environ['DATABASE_URL'].lower()
    c=Catalog('test-'+uuid.uuid4().hex,1)
    c.key='fake-key';c.init();return c

def test_paid_result_is_cached_across_runs(catalog,monkeypatch):
    calls=[]
    class Response:
        ok=True
        def json(self):return {'data':[{'index':0,'embedding':[1,0]}],'usage':{'prompt_tokens':2,'total_tokens':2}}
    monkeypatch.setattr('catalog.requests.post',lambda *a,**k:calls.append(1) or Response())
    body={'model':'text-embedding-3-small','input':uuid.uuid4().hex}
    a,h=catalog.call('embeddings',body,'test')
    b,h2=catalog.call('embeddings',body,'test')
    assert a==b and h==h2 and len(calls)==1

def test_budget_blocks_before_network(catalog,monkeypatch):
    with catalog.engine.begin() as c:c.execute(text('UPDATE semanticshelf.catalog_run SET budget_usd=0.000001 WHERE id=:r'),{'r':catalog.run_id})
    monkeypatch.setattr('catalog.requests.post',lambda *a,**k:pytest.fail('request sent after budget exhausted'))
    with pytest.raises(BudgetExceeded):catalog.call('responses',{'model':'gpt-6-luna','input':uuid.uuid4().hex,'max_output_tokens':1000},'test')

def test_manual_description_survives_automatic_write(catalog):
    book=catalog.books([24])[0]
    result=fallback(book);result.update(description_de='Eine manuell geprüfte Beschreibung über Schach und Isolation.',basis='manual',confidence=3,needs_review=False,sources=[])
    catalog.save_description(book,result,'manual',manual=True)
    replacement={**result,'description_de':'Dieser automatische Ersatz darf nicht übernommen werden.','basis':'model_knowledge'}
    assert catalog.save_description(book,replacement,'gpt-6-luna') is False
    assert catalog.books([24])[0]['description_de']==result['description_de']

def test_timeout_retains_budget_reservation(catalog,monkeypatch):
    import requests
    from catalog import UncertainRequest
    monkeypatch.setattr('catalog.requests.post',lambda *a,**k:(_ for _ in ()).throw(requests.Timeout()))
    with pytest.raises(UncertainRequest):catalog.call('responses',{'model':'gpt-6-luna','input':uuid.uuid4().hex,'max_output_tokens':100},'test')
    with catalog.engine.connect() as c:
        row=c.execute(text('SELECT status,charged_usd,reserved_usd FROM semanticshelf.catalog_request WHERE run_id=:r'),{'r':catalog.run_id}).mappings().one()
    assert row['status']=='uncertain' and row['charged_usd'] is None and row['reserved_usd']>0

def test_direct_sql_edit_is_versioned_and_locked(catalog):
    with catalog.engine.begin() as c:
        c.execute(text('UPDATE semanticshelf.book_enrichment SET manual_locked=false WHERE book_id=25'))
    book=catalog.books([25])[0]
    result=fallback(book);result.update(basis='model_knowledge',confidence=1,needs_review=True,sources=[])
    catalog.save_description(book,result,'gpt-6-luna')
    assert catalog.books([25])[0]['manual_locked'] is False
    with catalog.engine.begin() as c:
        c.execute(text('UPDATE semanticshelf.book SET description=:d WHERE id=25'),{'d':'Eine durch einen Menschen überarbeitete Beschreibung der Novelle.'})
    updated=catalog.books([25])[0]
    assert updated['manual_locked'] is True and updated['basis']=='manual'

def test_exact_isbn_search_works_without_provider(catalog):
    from app.openai_catalog import search_books
    items,total=search_books(None,None,0,5,query='9783150189337')
    assert items[0]['id']==24 and total>=1
    assert all(b['id']==24 for b in items)

def test_author_filter_does_not_require_embedding(catalog):
    from app.openai_catalog import search_books
    items,total=search_books(None,None,0,5,author_filter='Zweig',query='')
    assert total>0 and items
    assert all(any('Zweig' in name for name in b['authors']) for b in items)

def test_edit_reuses_metadata_vector_and_replaces_content_vector(catalog,monkeypatch):
    from types import SimpleNamespace
    args=SimpleNamespace(ids=[24],embedding_model='text-embedding-3-large',limit=None,shards=1,shard_index=0)
    # A fresh fixture state for this book, confined to the isolated clone.
    with catalog.engine.begin() as c:c.execute(text('DELETE FROM semanticshelf.book_search_document WHERE book_id=24'))
    batches=[]
    def fake_call(endpoint,body,purpose,**kwargs):
        batches.append(body['input'])
        return {'data':[{'index':i,'embedding':[0.1]*1536} for i in range(len(body['input']))]},None
    monkeypatch.setattr(catalog,'call',fake_call)
    catalog.embed(args)
    assert len(batches[0])==2
    book=catalog.books([24])[0]
    result=fallback(book);result.update(description_de='Eine neue manuell geprüfte Beschreibung über Schach, Gefangenschaft und Isolation.',basis='manual',confidence=3,needs_review=False,sources=[])
    catalog.save_description(book,result,'manual',manual=True)
    catalog.embed(args)
    assert len(batches[1])==1 and 'Beschreibung:' in batches[1][0]
    catalog.embed(args)
    assert len(batches)==2

def test_preexisting_description_is_preserved_without_api(catalog,monkeypatch):
    from types import SimpleNamespace
    bid=900000000+int(uuid.uuid4().hex[:7],16)
    with catalog.engine.begin() as c:
        c.execute(text('INSERT INTO semanticshelf.book(id,title,description) VALUES (:id,:t,:d)'),
                  {'id':bid,'t':'Manuell erfasster Band','d':'Eine bereits vorhandene, von Menschen erfasste Beschreibung.'})
    monkeypatch.setattr('catalog.requests.post',lambda *a,**k:pytest.fail('manual text must not be regenerated'))
    args=SimpleNamespace(ids=[bid],preview=False,research=False,limit=None,model='gpt-6-luna',workers=2,batch_size=8)
    catalog.describe(args)
    book=catalog.books([bid])[0]
    assert book['manual_locked'] is True and book['basis']=='manual'
    assert 'bereits vorhandene' in book['description_de']

def test_recommendations_use_vector_aggregate_with_restricted_search_path(catalog,monkeypatch):
    from types import SimpleNamespace
    from app.openai_catalog import get_relevant_books_for_history
    def fake_call(endpoint,body,purpose,**kwargs):
        return {'data':[{'index':i,'embedding':[0.1]*1536} for i in range(len(body['input']))]},None
    monkeypatch.setattr(catalog,'call',fake_call)
    catalog.embed(SimpleNamespace(ids=[24,25],embedding_model='text-embedding-3-large',limit=None,shards=1,shard_index=0))
    results=get_relevant_books_for_history([24],0,5)
    assert results and results[0]['id']==25
    assert get_relevant_books_for_history([24,25],0,5)==[]
