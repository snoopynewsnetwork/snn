#!/usr/bin/env python3
"""Execute exact retained preflight logic with ONLY output paths redirected into ownership."""
from pathlib import Path
import json,runpy
from extract import BASE,DATA,SRC,js
def main():
 primary=(DATA/'preflight_primary_sources.py').read_text()
 primary=primary.replace("D=Path(__file__).resolve().parent;N=D/'news'",f"D=Path({str(DATA)!r});N=D/'news';OUT=Path({str(SRC)!r})")
 primary=primary.replace("N/'extracts/sos-2020-general-canvass.txt'","OUT/'preflight-2020-general-canvass.txt'").replace("D/'coordinator-primary-preflight.json'","OUT/'preflight-primary-reproduction.json'")
 native=(DATA/'preflight_2024_public_native_export.py').read_text()
 native=native.replace('DATA=Path(__file__).resolve().parent',f'DATA=Path({str(DATA)!r})\nOUT=Path({str(SRC)!r})')
 native=native.replace("NEWS/'extracts/2024-public-presidential-native-original-positions.jsonl.gz'","OUT/'preflight-native-positions.jsonl.gz'")
 native=native.replace("NEWS/'extracts/2024-public-exports-complete-OOXML-rows.json.gz'","OUT/'preflight-complete-OOXML.json.gz'")
 native=native.replace("DATA/'coordinator-2024-public-native-export-preflight.json'","OUT/'preflight-native-reproduction.json'")
 for name,s in [('primary',primary),('native',native)]:
  p=BASE/'scripts'/f'preflight_{name}_owned.py';p.write_text(s);runpy.run_path(str(p),run_name='__main__')
 own=json.loads((SRC/'preflight-primary-reproduction.json').read_text());shared=json.loads((DATA/'coordinator-primary-preflight.json').read_text())
 assert own['tables']==shared['tables']
 n=json.loads((SRC/'preflight-native-reproduction.json').read_text());sharedn=json.loads((DATA/'coordinator-2024-public-native-export-preflight.json').read_text())
 for k in ['public_source_candidate_totals','retained_source_native_rows','county_source_controls','counties_with_actual_source_differences','separate_workbook_header_conflicts']:assert n[k]==sharedn[k],k
 js(SRC/'preflight-independent-check.json',dict(status='pass',shared_tables_exact=True,public_native_controls_exact=True,only_modifications='Output destinations redirected into owned source directory; original preflight source input locations unchanged. Independently authored extraction runs separately.'))
if __name__=='__main__':main()
