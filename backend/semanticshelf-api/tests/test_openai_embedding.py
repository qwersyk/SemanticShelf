import pytest
from app import embedding

def test_openai_query_cached_without_e5_prefix(monkeypatch):
    embedding._cache.clear();calls=[]
    monkeypatch.setattr(embedding,'OPENAI_API_KEY','test-key')
    class Response:
        def raise_for_status(self):pass
        def json(self):return {'data':[{'embedding':[0.1]*1536}]}
    def post(url,**kw):calls.append(kw['json']);return Response()
    monkeypatch.setattr(embedding.requests,'post',post)
    first=embedding.embed_openai_query('  Schach  und Isolation ')
    second=embedding.embed_openai_query('Schach und Isolation')
    assert first==second and len(calls)==1
    assert calls[0]['input']=='Schach und Isolation'
    assert calls[0]['dimensions']==1536

def test_reject_incompatible_openai_vector(monkeypatch):
    embedding._cache.clear()
    monkeypatch.setattr(embedding,'OPENAI_API_KEY','test-key')
    class Response:
        def raise_for_status(self):pass
        def json(self):return {'data':[{'embedding':[0.1]*384}]}
    monkeypatch.setattr(embedding.requests,'post',lambda *a,**k:Response())
    with pytest.raises(RuntimeError,match='dimensions'):embedding.embed_openai_query('dimensions test')
