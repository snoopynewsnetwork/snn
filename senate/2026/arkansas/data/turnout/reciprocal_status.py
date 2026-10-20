#!/usr/bin/env python3
"""The only authorized canonical-contract change is this explicit review status.

Every other semantic field and the full native CSV must match its whole
captured old body. This imports no peer counts, parser or transcription.
"""
import json
from reciprocal import Capture,Checks,P,S
STATUS='captured-final baseline source/field/order reciprocal passed; coordinator review pending; historical source inventory only; no legal/current geographic approval'
def verify():
    cap=Capture('own');old=json.loads(cap.own('priority-set.json'));now=json.loads((P/'priority-set.json').read_text())
    old_status=old.pop('acceptance_status');new_status=now.pop('acceptance_status');Checks().eq(old,now,'all-other-whole-canonical-contract-fields')
    assert new_status in [old_status,STATUS]
    assert cap.read('data/county-turnout.csv')==(S/'data/county-turnout.csv').read_bytes()
    return now
def main():
    result=json.loads((P/'reciprocal.json').read_text());assert result['status']=='pass' and not result['errors']
    verify();obj=json.loads((P/'priority-set.json').read_text());obj['acceptance_status']=STATUS
    (P/'priority-set.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');verify()
    print('Changed only explicit acceptance_status; every other canonical field and native CSV remains exact')
if __name__=='__main__':main()
