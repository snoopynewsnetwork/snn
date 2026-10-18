"""Select only observed link positions: python queue_links.py output id:parent:position ..."""
import json,pathlib,sys
r=pathlib.Path(__file__).parent
out=[]
for arg in sys.argv[2:]:
 i,p,n=arg.split(':'); l=next(x for x in json.loads((r/'extracts'/f'{p}.links.json').read_text()) if x['position']==int(n))
 out.append({'id':i,'url':l['url'],'parent':p,'link_position':l['position'],'link_label':l['label']})
(r/sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n')
