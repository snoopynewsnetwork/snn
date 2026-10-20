"""Reconcile literal historical ZIP views to their actual primary HTML controls."""
from pathlib import Path
import collections,gzip,hashlib,io,json,subprocess,zipfile
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(DATA.parent)),bytes=len(b),sha256=sha(b))
def keep(p,b):
 assert len(b)<40000000
 if p.exists():assert p.read_bytes()==b,('Previously retained preflight changed',p)
 else:p.write_bytes(b)
 return pin(p)
def main():
 manifest={r['id']:r for r in json.loads((NEWS/'manifest.json').read_bytes())}
 def body(sid):
  r=manifest[sid];z=(NEWS/r['asset']).read_bytes();b=gzip.decompress(z);assert sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256']and len(b)==r['bytes'];assert r['status']==200;return b
 results=[];derivative=[];all_inventories={};htmlchecks=[];sourcepins={}
 for year in ['2020','2022']:
  long_id=f'ri-{year}-observed-long-zip';short_id=f'ri-{year}-observed-short-zip'
  lz=zipfile.ZipFile(io.BytesIO(body(long_id)));sz=zipfile.ZipFile(io.BytesIO(body(short_id)));assert lz.testzip()is None and sz.testzip()is None
  for sid,z in [(long_id,lz),(short_id,sz)]:
   sourcepins[sid]=manifest[sid]
   all_inventories[sid]=[dict(member_ordinal=n,member_name=i.filename,raw_bytes=i.file_size,CRC32=i.CRC,member_sha256=sha(z.read(i)),ZIP_member_timestamp=i.date_time)for n,i in enumerate(z.infolist())]
  if year=='2020':
   members=[('root','rigen2020l.asc','rigen2020.asc'),('nested_results','rigen2020l/rigen2020l_results.ASC','rigen2020/rigen2020s_results.ASC'),('setup','rigen2020l/rigen2020l_setup.ASC','rigen2020/rigen2020s_setup.ASC')]
   wanted=['Presidential Electors For:','Senator in Congress'];summary_id='ri-2020-observed-state-summary'
  else:
   members=[('root','rigen2022l.txt','rigen2022.txt'),('nested_results','rigen2022l/rigen2022l_result.txt','rigen2022/rigen2022s_result.txt'),('setup','rigen2022l/rigen2022l_setup.txt','rigen2022/rigen2022s_setup.txt')]
   wanted=['Governor'];summary_id='ri-2022-observed-historical-seed'
  views={};rootrows=None
  for label,ln,sn in members:
   raw=lz.read(ln);longlines=raw.splitlines(keepends=True);shortlines=sz.read(sn).splitlines(keepends=True);assert len(longlines)==len(shortlines);assert all(len(r.rstrip(b'\r\n'))==263 for r in longlines);assert all(len(r.rstrip(b'\r\n'))==101 for r in shortlines);assert [r[:101]for r in longlines]==[r[:101]for r in shortlines]
   assert len({r[:11]for r in longlines})==len(longlines)
   controls=collections.Counter();groups=collections.defaultdict(lambda:[0]*14);units=collections.defaultdict(dict);selected=[];offset=0
   for ordinal,full in enumerate(longlines,1):
    r=full.rstrip(b'\r\n');title=r[111:167].decode('latin1');total=int(r[11:17]);g=[int(r[i:i+6])for i in range(17,101,6)];assert sum(g)==total
    if title.strip()in wanted:
     name=r[167:205].decode('latin1');native=r[205:235].decode('latin1');key=(r[:4].decode(),r[4:7].decode(),name.strip());controls[key]+=total;groups[key]=[a+b for a,b in zip(groups[key],g)];code=r[7:11].decode();old=units[title.strip()].setdefault(code,native);assert old==native
     a=dict(year=year,view=label,long_member=ln,short_member=sn,source_row=ordinal,source_byte_offset=offset,raw_record_latin1=r.decode('latin1'),raw_record_sha256=sha(r),original_record_terminator_latin1=full[len(r):].decode('latin1'),contest_id=r[:4].decode(),candidate_id=r[4:7].decode(),native_code=code,total=total,groups=g,party_literal=r[101:104].decode('latin1'),district_type_id=r[104:107].decode('latin1'),district_code=r[107:111].decode('latin1'),contest_title_literal=title,candidate_name_literal=name,native_name_literal=native,district_name_literal=r[235:260].decode('latin1'),votes_allowed_literal=r[260:262].decode('latin1'),referendum_flag_literal=r[262:].decode('latin1'))
     selected.append(a)
     if label=='root':derivative.append(a)
    offset+=len(full)
   assert offset==len(raw)
   views[label]=dict(long_member=ln,short_member=sn,all_source_rows=len(longlines),selected_rows=len(selected),literal_native_contexts={k:len(v)for k,v in units.items()},controls=[dict(contest_code=k[0],candidate_code=k[1],literal_candidate=k[2],total=v,groups=groups[k])for k,v in controls.items()])
   if label=='setup':assert all(v==0 for v in controls.values())
   if label=='root':rootrows=selected;rootcontrols=controls;rootgroups=groups;rootunits=units
   else:
    root_bykey={(r['contest_id'],r['candidate_id'],r['native_code']):r for r in rootrows}
    assert set(root_bykey)=={(r['contest_id'],r['candidate_id'],r['native_code'])for r in selected}
    views[label]['positions_with_total_or_groups_different_from_root']=sum((root_bykey[r['contest_id'],r['candidate_id'],r['native_code']]['total'],root_bykey[r['contest_id'],r['candidate_id'],r['native_code']]['groups'])!=(r['total'],r['groups'])for r in selected)
  soup=BeautifulSoup(body(summary_id),'html.parser');sourcepins[summary_id]=manifest[summary_id]
  for title in wanted:
   table=soup.find('table',attrs={'summary':title});assert table;checks=[]
   office_codes={r['contest_id']for r in rootrows if r['contest_title_literal'].strip()==title};assert len(office_codes)==1;office_code=next(iter(office_codes))
   for row in table.select('tbody tr'):
    namecell=row.select_one('td.candidate');span=namecell.find('span');party=span.get_text(' ',strip=True)if span else None
    if span:span.extract()
    name=namecell.get_text(' ',strip=True);total=int(row.select_one('td.total.votes').get_text(strip=True));method=[]
    for li in row.select('ul.mailinbreakout li'):
     label,value=li.get_text(' ',strip=True).rsplit(':',1);method.append(dict(label=label.strip(),votes=int(value.strip())))
    keys=[k for k in rootcontrols if k[0]==office_code and k[2]==name];assert len(keys)==1;key=keys[0];assert rootcontrols[key]==total;assert [m['votes']for m in method]==rootgroups[key][:3];assert all(v==0 for v in rootgroups[key][3:]);assert sum(m['votes']for m in method)==total
    checks.append(dict(literal_candidate_without_HTML_party_suffix=name,HTML_party_suffix=party,total=total,HTML_methods=method,original_contest_code=key[0],original_candidate_code=key[1],total_and_three_method_comparisons=4))
   assert len(checks)==sum(k[0]==checks[0]['original_contest_code']for k in rootcontrols)
   htmlchecks.append(dict(year=year,office_title_literal=title,source_HTML=summary_id,candidate_controls=checks))
  fmt_id=f'ri-{year}-observed-format-description';sourcepins[fmt_id]=manifest[fmt_id];fmt=subprocess.run(['pdftotext','-layout','-','-'],input=body(fmt_id),check=True,capture_output=True).stdout.decode()
  if year=='2020':assert 'Early Voting'not in fmt and 'Emergency'not in fmt
  else:assert 'Early Voting'in fmt
  diffs=[]
  if year=='2020':
   pres=rootunits['Presidential Electors For:'];sen=rootunits['Senator in Congress'];assert not set(sen)-set(pres);diffs=[dict(code=k,source_name=pres[k])for k in sorted(set(pres)-set(sen))];assert len(diffs)==39
  results.append(dict(year=year,views=views,all_original_selected_rows=len(rootrows),root_source_total=sum(rootcontrols.values()),presidential_only_native_contexts_not_in_Senate=diffs,format_source_text=fmt,root_selection_basis='Root long/short prefixes agree at every source row and selected candidate/method controls exactly match actual primary official-results HTML. Nested nonzero results and all-zero setup files remain distinct original views; no source release chronology or genuine counts implied by filenames.'))
 fieldpin=keep(DATA/'coordinator-historical-native-fields.jsonl.gz',gzip.compress(('\n'.join(json.dumps(r,ensure_ascii=True,separators=(',',':'))for r in derivative)+'\n').encode(),mtime=0))
 out=dict(status='pass_bounded_historical_original_ZIP_and_primary_HTML_controls_only',original_response_receipts=sourcepins,ZIP_member_inventories=all_inventories,year_views=results,root_selected_fields=fieldpin,primary_HTML_candidate_and_method_checks=htmlchecks,root_selected_native_candidate_rows=len(derivative),total_plus_fourteen_group_fields=len(derivative)*15,qualification='Complete downloaded originals and all ZIP members/CRCs preserved once, including nonzero nested and zero setup views. Root selected rows reproduce primary official-results HTML; the data index itself calls raw technical data courtesy material and says official results are posted by the Board. Full BOE certification/amendment review remains a worker task. Long records use explicit lossless Latin1 byte roundtrip, not an asserted semantic charset. Group3 on the2020 linked2016formatPDF is unlabelled; actual2020 HTML labels matching group3 Emergency ballots. The2022 linked description and matching HTML label it Early Voting. No cross-year/current method equivalence follows. The39 source contexts named Presidential in2020 are absent from Senate; no Senate0 or physical precinct is invented. Native codes are publication-scoped; no geographic/cross-year join, generic-write-in validity, ballots/registration pool or current cadence is accepted.',historical_native_question_complete=False,current_geography_approved=False,formal_priority_accepted=False)
 result=keep(DATA/'coordinator-historical-native-preflight.json',(json.dumps(out,indent=2)+'\n').encode());print(json.dumps(dict(output=result,selected_rows=len(derivative),field_derivative=fieldpin,views=[dict(year=r['year'],views=r['views'])for r in results])))
if __name__=='__main__':main()
