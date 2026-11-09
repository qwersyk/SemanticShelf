"""Hybrid retrieval over one consistent, versioned OpenAI index."""
import re
from sqlalchemy import text
from app.database import engine, books_from_rows
from app.settings import OPENAI_EMBEDDING_MODEL

SEARCH_SQL='''
WITH scope AS MATERIALIZED (
 SELECT b.id,b.title,b.year,b.language,b.cover_url,d.embedding_vector,d.metadata_vector,
        d.title_normalized,d.authors_text,d.isbn_normalized,d.search_tsv,
        coalesce(d.work_key,b.id::text) AS work_key,
        CASE WHEN :isbn<>'' AND regexp_replace(coalesce(b.isbn13,''),'[^0-9]','','g')=:isbn THEN 2
             WHEN lower(b.title)=lower(:query) AND :query<>'' THEN 1 ELSE 0 END AS exact
 FROM book b LEFT JOIN book_enrichment e ON e.book_id=b.id
 LEFT JOIN book_search_document d ON d.book_id=b.id AND d.model=:model AND d.version_id=e.version_id
 WHERE (:author IS NULL OR EXISTS (SELECT 1 FROM book_author ba JOIN author a ON a.id=ba.author_id
          WHERE ba.book_id=b.id AND a.name ILIKE '%' || :author || '%'))
), semantic AS (
 SELECT id,row_number() OVER (ORDER BY embedding_vector OPERATOR(public.<=>) CAST(:vector AS public.vector),id) AS rank
 FROM scope WHERE :isbn='' AND :vector IS NOT NULL AND embedding_vector IS NOT NULL
 ORDER BY embedding_vector OPERATOR(public.<=>) CAST(:vector AS public.vector),id LIMIT 120
), metadata AS (
 SELECT id,row_number() OVER (ORDER BY metadata_vector OPERATOR(public.<=>) CAST(:vector AS public.vector),id) AS rank
 FROM scope WHERE :isbn='' AND :vector IS NOT NULL AND metadata_vector IS NOT NULL
 ORDER BY metadata_vector OPERATOR(public.<=>) CAST(:vector AS public.vector),id LIMIT 120
), lexical AS (
 SELECT id,row_number() OVER (ORDER BY exact DESC,
   CASE WHEN :query<>'' AND strpos(lower(title),lower(:query))>0 THEN 1 ELSE 0 END DESC,
   coalesce(ts_rank_cd(search_tsv,websearch_to_tsquery('german',:query)),0)
    + public.similarity(lower(title),lower(:query)) DESC,id) AS rank
 FROM scope WHERE (:isbn<>'' AND exact=2) OR (:isbn='' AND (:query='' OR exact>0 OR
   (:query<>'' AND (search_tsv @@ websearch_to_tsquery('german',:query)
    OR strpos(lower(title),lower(:query))>0
    OR public.word_similarity(lower(:query),lower(title))>0.35
    OR public.similarity(lower(title),lower(:query))>0.18
    OR public.word_similarity(lower(:query),lower(coalesce(authors_text,'')))>0.5))))
 ORDER BY rank LIMIT CASE WHEN :query='' THEN 1000000 ELSE 120 END
), contributions AS (
 SELECT id,1.0/(60+rank) AS value FROM semantic UNION ALL
 SELECT id,:metadata_weight/(60+rank) FROM metadata UNION ALL
 SELECT id,:lexical_weight/(60+rank) FROM lexical
), fused AS (
 SELECT s.id,s.title,s.year,s.language,s.cover_url,s.work_key,
        (1.0/(1+sum(c.value)+s.exact))::double precision AS score
 FROM contributions c JOIN scope s ON s.id=c.id
 GROUP BY s.id,s.title,s.year,s.language,s.cover_url,s.work_key,s.exact
), unique_works AS (
 SELECT *,row_number() OVER (PARTITION BY work_key ORDER BY score,id) AS copy_rank FROM fused
), ranked AS (SELECT * FROM unique_works WHERE copy_rank=1)
SELECT id,title,year,language,cover_url,CASE WHEN :query='' THEN NULL ELSE score END AS score,
       count(*) OVER () AS total FROM ranked ORDER BY score,id OFFSET :offset LIMIT :limit
'''

def search_books(query_vector,model_name,offset,limit,author_filter=None,query=''):
    isbn=re.sub(r'[-\s]','',query)
    if re.fullmatch(r'\d{9}[\dXx]',isbn):
        stem='978'+isbn[:9]
        isbn=stem+str((-sum(int(v)*(1 if i%2==0 else 3) for i,v in enumerate(stem)))%10)
    params={'vector':query_vector,'model':model_name or OPENAI_EMBEDDING_MODEL,'query':query.strip(),
            'isbn':isbn if re.fullmatch(r'\d{13}',isbn) else '',
            'author':author_filter,'offset':offset,'limit':limit,
            # In a full sentence, isolated title keywords must not outweigh its meaning.
            'metadata_weight':0.05 if len(re.findall(r'\w+',query))>4 else 0.2,
            'lexical_weight':0.1 if len(re.findall(r'\w+',query))>4 else 1.0}
    with engine.connect() as c:
        rows=list(c.execute(text(SEARCH_SQL),params).mappings())
        if rows:total=rows[0]['total']
        elif offset:
            first=c.execute(text(SEARCH_SQL),{**params,'offset':0,'limit':1}).mappings().first()
            total=first['total'] if first else 0
        else:total=0
        books=books_from_rows(c,rows)
        for b in books:b.pop('total',None)
    return books,total

def get_book(book_id):
    with engine.connect() as c:
        row=c.execute(text('''SELECT b.*,v.id AS description_version,v.basis AS description_basis,
          v.confidence AS description_confidence,v.needs_review AS description_needs_review,
          v.review_reason AS description_review_reason,v.sources AS description_sources
          FROM book b LEFT JOIN book_enrichment e ON e.book_id=b.id
          LEFT JOIN book_description_version v ON v.id=e.version_id WHERE b.id=:id'''),{'id':book_id}).mappings().first()
        return books_from_rows(c,[row])[0] if row else None

def get_relevant_books_for_history(book_ids,offset,limit):
    book_ids=list(dict.fromkeys(book_ids))[:100]
    if not book_ids:
        from app.database import get_random_books
        return get_random_books(offset,limit)
    with engine.connect() as c:
        rows=c.execute(text('''WITH source AS (
          SELECT avg(d.embedding_vector) AS content,avg(d.metadata_vector) AS metadata
          FROM book_search_document d JOIN book_enrichment e ON e.book_id=d.book_id AND e.version_id=d.version_id
          WHERE d.book_id=ANY(:ids) AND d.model=:model
        ), candidates AS (
          SELECT b.id,b.title,b.year,b.language,b.cover_url,d.work_key,
            (0.9*(d.embedding_vector OPERATOR(public.<=>) s.content)
             +0.1*(d.metadata_vector OPERATOR(public.<=>) s.metadata))::double precision AS score
          FROM source s JOIN book_search_document d ON d.model=:model
          JOIN book_enrichment e ON e.book_id=d.book_id AND e.version_id=d.version_id
          JOIN book b ON b.id=d.book_id
          WHERE s.content IS NOT NULL AND NOT(d.book_id=ANY(:ids)) AND NOT EXISTS (
             SELECT 1 FROM book_search_document src WHERE src.book_id=ANY(:ids) AND src.work_key=d.work_key)
        ), ranked AS (SELECT *,row_number() OVER (PARTITION BY work_key ORDER BY score,id) AS copy_rank FROM candidates)
        SELECT id,title,year,language,cover_url,score FROM ranked WHERE copy_rank=1
        ORDER BY score,id OFFSET :offset LIMIT :limit'''),
        {'ids':book_ids,'model':OPENAI_EMBEDDING_MODEL,'offset':offset,'limit':limit}).mappings()
        return books_from_rows(c,rows)

def get_relevant_books_for_book(book_id,offset,limit):
    return get_relevant_books_for_history([book_id],offset,limit)
