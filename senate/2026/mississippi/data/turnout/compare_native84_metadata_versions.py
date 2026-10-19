"""Pin later literal printed-ID parses separately from immutable84 vote replay."""
import json
from acquire_sources import BASE,OUT,savejson,sha

def index(p):
 d=json.loads(p.read_text());return {(sid,page['page'],c['source_column']):(s,c) for sid,s in d['sources'].items() for page in s['pages'] for c in page['columns']}

def main():
 frozen=OUT/'qa/milestones/native-2024-84views/native-reviewed-2024.json';working=OUT/'native-reviewed-2024.json';a=index(frozen);b=index(working);assert a.keys()==b.keys() and len(a)==2321
 additions=[];other=[]
 for k,(s,c) in a.items():
  t,d=b[k]
  assert s['raw_sha256']==t['raw_sha256'] and c['Ty_Pinkins']==d['Ty_Pinkins'] and c['Roger_F_Wicker']==d['Roger_F_Wicker'] and c['label_literal']==d['label_literal'] and c['role']==d['role'],k
  old,new=c['printed_native_id'],d['printed_native_id']
  if old!=new:
   record=dict(source_id=k[0],source_page=k[1],source_column=k[2],source_raw_sha256=s['raw_sha256'],label_literal=c['label_literal'],frozen84_printed_ID=old,working_printed_ID=new)
   if old is None and new is not None and new in c['label_literal']:additions.append(record)
   else:other.append(record)
 assert not other,other
 result=dict(frozen_84_ledger_path=str(frozen.relative_to(BASE)),frozen_84_ledger_sha256=sha(frozen.read_bytes()),working_ledger_path=str(working.relative_to(BASE)),working_ledger_sha256=sha(working.read_bytes()),compared_source_columns=len(a),literal_printed_ID_additions=additions,other_printed_ID_changes=other,qualification='Later original-header ID parses are exact substrings of unchanged literal labels and preserve candidate values/source hashes. Frozen84 peer comparison remains pinned to its original null-ID version. Geometry revisions are separate and not certified by this ID check.')
 savejson(OUT/'native-84-working-metadata-differences.json',result);print('Native frozen-to-working printed-ID additions',len(additions),'other',len(other))

if __name__=='__main__':main()
