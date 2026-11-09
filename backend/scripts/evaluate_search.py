"""Small fixed regression suite; diagnostic labels are not a human relevance benchmark."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
import os
from pathlib import Path
import time
import requests
from catalog import Catalog

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--provider',choices=['legacy','openai'],required=True)
    p.add_argument('--url',default='http://semanticshelf-semanticshelfapidev-97gfol:8000')
    p.add_argument('--output',required=True)
    p.add_argument('--model',default='text-embedding-3-large')
    p.add_argument('--run',default='2026-11-09-initial')
    p.add_argument('--cases',default=str(Path(__file__).with_name('search-evaluation.json')))
    args=p.parse_args()
    cases=json.loads(Path(args.cases).read_text())
    catalog=Catalog(args.run)
    if args.provider=='openai':
        from app.openai_catalog import search_books
    def check(case):
        start=time.monotonic()
        if args.provider=='legacy':
            response=requests.get(args.url+'/api/books/search',params={'q':case['query'],'limit':10},timeout=90)
            response.raise_for_status();items=response.json()['items']
        else:
            data,_=catalog.call('embeddings',{'model':args.model,'dimensions':1536,'encoding_format':'float','input':case['query']},'evaluation_query')
            vector=json.dumps(data['data'][0]['embedding'])
            items,_=search_books(vector,args.model,0,10,query=case['query'])
        ids=[b['id'] for b in items];relevant=set(case['relevant_ids'])
        first=next((i+1 for i,x in enumerate(ids) if x in relevant),None)
        dcg=sum(1/math.log2(i+2) for i,x in enumerate(ids) if x in relevant)
        ideal=sum(1/math.log2(i+2) for i in range(min(10,len(relevant))))
        return {**case,'top10':[{'id':b['id'],'title':b['title']} for b in items],
            'hit5':bool(first and first<=5),'hit10':bool(first),'reciprocal_rank':1/first if first else 0,
            'ndcg10':dcg/ideal if ideal else 0,'seconds':round(time.monotonic()-start,3)}
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,cases))
    summary={}
    for category in ['all']+sorted({r['category'] for r in results}):
        subset=[r for r in results if category=='all' or r['category']==category]
        summary[category]={'count':len(subset),**{k:sum(r[k] for r in subset)/len(subset) for k in ['hit5','hit10','reciprocal_rank','ndcg10','seconds']}}
    output={'provider':args.provider,'embedding_model':args.model,'limitations':'Diagnostic examples with automatically expanded matching editions; not independently human-graded and not an unbiased quality percentage. nDCG can penalize intentional edition deduplication.','summary':summary,'results':results}
    Path(args.output).write_text(json.dumps(output,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
