"""Restore a catalog JSONL export into an EMPTY PostgreSQL database."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from sqlalchemy import create_engine,text

def import_catalog(path):
    path=Path(path);manifest=json.loads((path/'manifest.json').read_text())
    for name,info in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Invalid manifest path')
        with (path/name).open('rb') as f:checksum=hashlib.file_digest(f,'sha256').hexdigest()
        if checksum!=info['sha256']:raise ValueError('Checksum mismatch: '+name)
        if sum(1 for _ in (path/name).open())!=info['rows']:raise ValueError('Row count mismatch: '+name)
    url=os.environ['DATABASE_URL']
    if url.startswith('postgresql://'):url=url.replace('postgresql://','postgresql+psycopg2://',1)
    engine=create_engine(url)
    with engine.begin() as c:
        c.exec_driver_sql((Path(__file__).parent.parent/'database/schema.sql').read_text())
        c.exec_driver_sql((Path(__file__).parent.parent/'database/migrations/001_openai_catalog.sql').read_text().replace('BEGIN;','').replace('COMMIT;',''))
        if c.execute(text('SELECT count(*) FROM semanticshelf.book')).scalar_one():raise ValueError('Target database must be empty')
        def insert(table,row,json_fields=(),vector_fields=()):
            # Table/column names are from our fixed schema, never user SQL.
            allowed={r[0] for r in c.execute(text('SELECT column_name FROM information_schema.columns WHERE table_schema=\'semanticshelf\' AND table_name=:t AND is_generated=\'NEVER\''),{'t':table})}
            if not set(row)<=allowed:raise ValueError('Unexpected columns in '+table)
            fields=list(row);values=[];params={}
            for key in fields:
                if key in json_fields:values.append('CAST(:'+key+' AS jsonb)');params[key]=json.dumps(row[key],ensure_ascii=False)
                elif key in vector_fields:values.append('CAST(:'+key+' AS public.vector)');params[key]=row[key] if isinstance(row[key],str) else json.dumps(row[key])
                else:values.append(':'+key);params[key]=row[key]
            c.execute(text('INSERT INTO semanticshelf.'+table+' ('+','.join('"'+x+'"' for x in fields)+') VALUES ('+','.join(values)+')'),params)
        def rows(name):
            with (path/name).open() as f:
                for line in f:yield json.loads(line)
        for row in rows('runs.jsonl'):insert('catalog_run',row)
        for row in rows('requests.jsonl'):insert('catalog_request',row,('usage','response'))
        active=[]
        for book in rows('books.jsonl'):
            version=book.pop('enrichment');locked=book.pop('manual_locked');authors=book.pop('authors')
            insert('book',book)
            for name in authors:
                aid=c.execute(text('INSERT INTO semanticshelf.author(name) VALUES (:n) ON CONFLICT(name) DO UPDATE SET name=EXCLUDED.name RETURNING id'),{'n':name}).scalar_one()
                c.execute(text('INSERT INTO semanticshelf.book_author(book_id,author_id) VALUES (:b,:a) ON CONFLICT DO NOTHING'),{'b':book['id'],'a':aid})
            if version:active.append({'book_id':book['id'],'version_id':version['id'],'manual_locked':locked})
        for row in rows('description-history.jsonl'):insert('book_description_version',row,('topics','sources','metadata_snapshot'))
        for row in active:insert('book_enrichment',row)
        for row in rows('vectors.jsonl'):
            row.pop('search_tsv',None)
            insert('book_search_document',row,vector_fields=('embedding_vector','metadata_vector'))
        for table in ('book','author','book_description_version'):
            c.execute(text("SELECT setval(pg_get_serial_sequence('semanticshelf."+table+"','id'),greatest(coalesce((SELECT max(id) FROM semanticshelf."+table+"),1),1))"))
    print(json.dumps({'imported':{k:v['rows'] for k,v in manifest['files'].items()}},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory');args=p.parse_args();import_catalog(args.directory)
