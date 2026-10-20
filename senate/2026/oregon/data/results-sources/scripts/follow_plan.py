from acquire import R,fetch
from inspect_sources import inspect
import json,sys,concurrent.futures
items=json.loads((R/sys.argv[1]).read_bytes())
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(lambda x:fetch(*x),items):
  d=inspect(r);print(d['key'],d['status'],d['error'],flush=True)
