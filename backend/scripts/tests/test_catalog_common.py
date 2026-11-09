import pytest
from catalog_common import digest,documents,fallback,metadata,validate_description,valid_isbn

BOOK={'id':24,'title':'Schachnovelle','authors':['Zweig, Stefan'],'year':2013,'isbn13':'9783150189337','language':'deutsch','publisher':'Reclam','pages':112}

@pytest.mark.parametrize('value',['9783150189337','978-3-15-018933-7'])
def test_isbn_checksum(value):assert valid_isbn(value)

@pytest.mark.parametrize('value',['9783150189338','',None,'123'])
def test_reject_invalid_isbn(value):assert not valid_isbn(value)

@pytest.mark.parametrize('text',[
 'Es tut mir leid, ich konnte das Buch nicht finden.',
 'Weitere Angaben zum konkreten Werk oder zu seinem Inhalt liegen nicht vor.',
 'Die vorliegenden bibliografischen Angaben erlauben keine sichere Bestimmung der Ausgabe.',
 'Als KI habe ich keine zuverlässige Beschreibung.',
])
def test_reject_public_failure_messages(text):
    with pytest.raises(ValueError):validate_description({'description_de':text,'topics':[],'recognition':'metadata_only'})

def test_fallback_contains_only_catalog_facts():
    result=fallback({'title':'DDR','authors':[],'language':'deutsch'})
    assert 'Geschichte' not in result['description_de']
    assert result['topics']==[]
    assert validate_description(result)

def test_document_hash_changes_after_description_edit():
    first,meta=documents(BOOK,'Eine Novelle über Schach und Isolation.',['Schach'])
    second,meta2=documents(BOOK,'Eine Novelle über Gefangenschaft und psychische Belastung.',['Schach'])
    assert meta==meta2 and digest(first)!=digest(second)
    assert 'query:' not in first and 'passage:' not in first
    assert 'ISBN' not in first

def test_metadata_hash_ignores_database_identity_and_description():
    assert digest(metadata(BOOK))==digest(metadata({**BOOK,'id':5986,'description':'other'}))

def test_book_title_is_not_mistaken_for_an_assistant_refusal():
    assert validate_description({'description_de':'Das Buch „Ich kann nicht schweigen“ versammelt Erinnerungen und persönliche Erfahrungen.','topics':[],'recognition':'identified'})
