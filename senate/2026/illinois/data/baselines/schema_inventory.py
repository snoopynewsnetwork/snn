"""Exact column order/row-count inventory for every owned generated CSV."""
import csv,gzip,io,json
from source_io import ROOT,STATE,dump
def main():
    out=[]
    paths=[STATE/'data/county-baselines.csv']+[p for p in ROOT.rglob('*')if p.name.endswith('.csv')or p.name.endswith('.csv.gz')]
    for p in sorted(paths):
        b=p.read_bytes();b=gzip.decompress(b)if p.name.endswith('.gz')else b;r=csv.DictReader(io.StringIO(b.decode()));fields=r.fieldnames;count=sum(1 for _ in r)
        out.append(dict(path=str(p.relative_to(STATE)),columns_in_order=fields,data_rows=count,format='UTF-8 CSV; empty derived cell=null/unavailable; source literal zero stays0',compression='gzip'if p.name.endswith('.gz')else'none'))
    dump(ROOT/'schema-inventory.json',dict(csv_files=out,structured_semantics='source/SCHEMA.md'))
    print(json.dumps({'CSV_schemas':len(out)}))
if __name__=='__main__':main()
