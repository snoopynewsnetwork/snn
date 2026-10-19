#!/usr/bin/env python3
"""Recover complete source labels from original PDF word boxes, without cross-year joins."""
import csv,gzip,json,re,subprocess,tempfile,xml.etree.ElementTree as E
from extract import BASE,SRC,NEWS,original,csvout,gz,js
def main():
 mf=json.loads((SRC/'shared-news-receipts.json').read_text());a=next(a for a in mf if a['id']=='sos-2022-precinct-canvass')
 rows=list(csv.DictReader((BASE/'native-2022.csv').open()));evidence={};audit=[]
 with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
  f.write(original(a,NEWS));f.flush()
  for pg in sorted({int(r['pdf_page'])for r in rows}):
   raw=subprocess.run(['pdftotext','-f',str(pg),'-l',str(pg),'-bbox-layout',f.name,'-'],capture_output=True,check=True).stdout
   evidence[str(pg)]=raw.decode();root=E.fromstring(raw);ns={'h':'http://www.w3.org/1999/xhtml'}
   words=[dict(text=w.text,x0=float(w.get('xMin')),x1=float(w.get('xMax')),y0=float(w.get('yMin')),y1=float(w.get('yMax')))for w in root.findall('.//h:word',ns)]
   for w in words:w.update(x=(w['x0']+w['x1'])/2,y=(w['y0']+w['y1'])/2)
   dem=next(w for w in words if w['text']=='DEM');name=next(w for w in words if w['text']=='Name')
   anchors=[w for w in words if re.fullmatch(r'[\d,]+',w['text']or'')and abs(w['x']-dem['x'])<1 and w['y0']>=name['y1']-0.1]
   rr=[r for r in rows if int(r['pdf_page'])==pg];assert len(anchors)in[len(rr),len(rr)+1],(pg,len(anchors),len(rr))
   anchors.sort(key=lambda w:w['y']);triples=[]
   for w in anchors:
    nums=sorted([v for v in words if re.fullmatch(r'[\d,]+',v['text']or'')and abs(v['y']-w['y'])<.1 and v['x']>=dem['x']-1],key=lambda v:v['x']);assert len(nums)==3,(pg,nums)
    triples.append(nums)
   for i,r in enumerate(rr):assert [int(w['text'].replace(',',''))for w in triples[i]]==[int(r[k])for k in ['a_votes','lesnar_lib','b_votes']]
   cutoff=triples[0][0]['x']-(triples[0][1]['x']-triples[0][0]['x'])/2
   # No rounding of coordinates. Keep every original word and its selected anchor.
   labels=[[]for r in rr];total_y=anchors[len(rr)]['y0']if len(anchors)>len(rr)else 780
   for w in words:
    if w['x1']>=cutoff or w['y0']<name['y1']-.1 or w['y0']>=total_y-.1:continue
    i=min(range(len(rr)),key=lambda i:abs(anchors[i]['y']-w['y']))
    labels[i].append(w)
   for r,ww in zip(rr,labels):
    ww.sort(key=lambda w:(round(w['y0'],3),w['x0']))
    label=' '.join(w['text']for w in ww);assert label,(pg,r,cutoff,name,anchors)
    audit.append(dict(key=r['native_key'],page=pg,old_label=r['native_label'],bbox_label=label,original_words=ww))
    r['native_label']=label;r['label_recovery']='original_word_boxes_full_precision_nearest_numeric_row; see label audit'
 gz(SRC/'native2022-original-bbox.xml.json.gz',evidence);gz(SRC/'native2022-label-audit.json.gz',audit);csvout(BASE/'native-2022.csv',rows)
 print(json.dumps(dict(rows=len(rows),changed=sum(r['old_label']!=r['bbox_label']for r in audit))))
if __name__=='__main__':main()
