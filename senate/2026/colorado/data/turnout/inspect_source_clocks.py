#!/usr/bin/env python3
"""Retain source clocks separately; no timestamp is promoted to a live result-release clock."""
from pathlib import Path
import json,gzip,subprocess,zipfile,io
O=Path(__file__).resolve().parent;N=O.parent/'news';M={x['id']:x for x in json.loads((N/'manifest.json').read_text())}
def raw(sid):return gzip.decompress((N/M[sid]['asset']).read_bytes())
def main():
 result=[]
 for sid in ['sos-2024-abstract','sos-2020-signed-archive','sos-2020-booklet-archive']:
  b=raw(sid);info=subprocess.check_output(['pdfinfo','-'],input=b).decode();result.append(dict(source_id=sid,raw_sha256=M[sid]['raw_sha256'],pdfinfo_literal=info,retrieved_at_utc=M[sid]['retrieved_at_utc'],HTTP_headers=M[sid]['headers'],certificate_date='2020-12-08'if sid=='sos-2020-signed-archive'else None,qualification='PDF metadata, archive capture, signature and HTTP/retrieval clocks are independent; none is an election-night release/cadence measurement.'))
 z=zipfile.ZipFile(io.BytesIO(raw('sos-2024-native-turnout')));result.append(dict(source_id='sos-2024-native-turnout',OOXML_core_properties_literal=z.read('docProps/core.xml').decode(),qualification='workbook author/creation/modification properties are document metadata, not field extraction or November reporting timestamps'))
 cat=json.loads((O/'extracts/candidate-universes.json').read_text())
 for year,r in cat.items():
  c=r['page_properties']['contest'];result.append(dict(year=year,event=c['event'],verifiedAt_literal=c['verifiedAt'],publicNote=c['publicNote'],disclaimer=c['disclaimer'],hasVoteChannels=c['hasVoteChannels'],hasBallots=r['page_properties']['hasBallots'],source_file_objects=c['files'],qualification='Historical public-client verification clock, not actual upload cadence or legal ballot status'))
 (O/'source/source-clocks.json').write_text(json.dumps(result,indent=2)+'\n')
 print('retained clock records',len(result))
if __name__=='__main__':main()
