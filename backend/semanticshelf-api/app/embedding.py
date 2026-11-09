import requests
from collections import OrderedDict
from threading import Lock
from time import monotonic
import math

from app.settings import EMBEDDING_API_KEY, EMBEDDING_API_URL
from app.settings import (SEARCH_PROVIDER,OPENAI_API_KEY,OPENAI_EMBEDDING_MODEL,OPENAI_EMBEDDING_DIMENSIONS)

EXPECTED_DIMENSIONS = 384
_cache=OrderedDict()
_lock=Lock()


def embed_query(query):
    if SEARCH_PROVIDER == 'openai':
        return embed_openai_query(query)
    response = requests.post(
        f"{EMBEDDING_API_URL}/embed",
        headers={"x-api-key": EMBEDDING_API_KEY},
        json={"texts": [f"query: {query.strip()}"]},
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    if data["dimensions"] != EXPECTED_DIMENSIONS:
        raise RuntimeError(f"Expected {EXPECTED_DIMENSIONS} dimensions, got {data['dimensions']}")

    return data["model"], "[" + ",".join(str(value) for value in data["vectors"][0]) + "]"


def embed_openai_query(query):
    query=' '.join(query.strip().split())
    key=(OPENAI_EMBEDDING_MODEL,OPENAI_EMBEDDING_DIMENSIONS,query)
    with _lock:
        cached=_cache.get(key)
        if cached and cached[0]>monotonic():
            _cache.move_to_end(key)
            return cached[1]
    if not OPENAI_API_KEY:raise RuntimeError('Search is not configured')
    response=requests.post('https://api.openai.com/v1/embeddings',
        headers={'Authorization':'Bearer '+OPENAI_API_KEY},
        json={'model':OPENAI_EMBEDDING_MODEL,'dimensions':OPENAI_EMBEDDING_DIMENSIONS,
              'input':query,'encoding_format':'float'},timeout=(5,25))
    response.raise_for_status()
    data=response.json()
    try:vector=data['data'][0]['embedding']
    except (KeyError,IndexError,TypeError):raise RuntimeError('Invalid search embedding response') from None
    if len(vector)!=OPENAI_EMBEDDING_DIMENSIONS or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in vector):
        raise RuntimeError('Invalid search embedding dimensions')
    result=OPENAI_EMBEDDING_MODEL,'['+','.join(str(v) for v in vector)+']'
    with _lock:
        _cache[key]=(monotonic()+3600,result)
        _cache.move_to_end(key)
        while len(_cache)>512:_cache.popitem(last=False)
    return result
