"""Apply only bounded captured-peer status/report metadata after numeric build."""
import json
from pathlib import Path
def apply(state,here):
 path=here/'review/peer-settings.json'
 if not path.exists():return
 cfg=json.loads(path.read_text());contract=here/'priority-set.json';o=json.loads(contract.read_text());o['peer']=cfg['peer_metadata'];contract.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n')
 p=state/'turnout.md';text=p.read_text()
 for e in cfg['report_replacements']:
  assert text.count(e['before'])==1,e['before'];text=text.replace(e['before'],e['after'])
 p.write_text(text)
