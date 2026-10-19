"""Join independent Vision tokens to original physical grid bounds, never ordinals.

Candidate labels are independently recognized on the original page. No voting
field is chosen to fit a control; all ambiguous tokens and missing cells survive.
"""
import csv,gzip,json,re,statistics
from collections import defaultdict
from sources import *
from extract_native import cell_key
PAT={'Ty Pinkins':r'\b(?:ty\s+)?pinkins\b','Roger F. Wicker':r'\bwicker\b','Mike Espy':r'\bespy\b','Cindy Hyde-Smith':r'hyde.?smith','Jimmy L. Edwards':r'jimmy.*edwards','Tobey Bernard Bartee':r'bartee','Chris McDaniel':r'chris.*mcdaniel'}
def pixels(z,w,h):
 b=z['box'];return [b[0]*w,(1-b[3])*h,b[2]*w,(1-b[1])*h]
def main():
 expected={}
 for r in csv.DictReader((OUT/'candidate-votes.csv').open()):expected[(r['source_id'],r['candidate_literal'])]=int(r['votes'])
 county={r['county'].lower():r for r in csv.DictReader((BASE/'data/county-baselines.csv').open())};out=[];checks=[]
 for directory in sorted((OUT/'extracts/vision-pages').iterdir()):
  key=directory.name
  if not key.startswith('sos-2024-'):continue
  names=['Ty Pinkins','Roger F. Wicker'];pages=[];sums=defaultdict(int);missing=defaultdict(int);units=0
  for path in sorted(directory.glob('*.json.gz')):
   v=json.loads(gzip.decompress(path.read_bytes()));x=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/path.name).read_bytes()));w,h=v['render_size'];xs=x.get('grid_x',[])
   candidates=[z for i,z in enumerate(xs) if i and .23*w<z<.43*w and z-xs[i-1]>.15*w]
   if not candidates or len(xs)<8:continue
   split=candidates[0];bounds=[z for z in xs if z>=split-3]
   labels={}
   for c in x.get('columns',[]):labels[(c['bounds'][0],c['bounds'][2])]=c['ocr_label']
   fieldanchors={}
   for name in names:
    hits=[]
    for z in v['observations']:
     box=pixels(z,w,h)
     if box[0]<split and re.search(PAT[name],z['text'],re.I):hits.append((box,z['text']))
    if len(hits)==1:fieldanchors[name]=hits[0]
   if len(fieldanchors)!=2:continue
   columns=[]
   for ordinal,(l,r) in enumerate(zip(bounds,bounds[1:]),1):
    label=labels.get((l,r),'');typ='summary_TOTAL' if re.search(r'\btotal\b',label,re.I) else 'blank_or_unresolved_label' if not re.search('[A-Za-z0-9]',label) else 'source_native_label_OCR_pending_review';fields={}
    for name,(anchor,labeltext) in fieldanchors.items():
     cy=(anchor[1]+anchor[3])/2;tokens=[]
     for z in v['words']:
      box=pixels(z,w,h);cx=(box[0]+box[2])/2;y=(box[1]+box[3])/2
      if l<cx<r and abs(y-cy)<max(16,.013*h):tokens.append(dict(text=z['text'],box=box,confidence=z['confidence']))
     literal=' '.join(z['text'] for z in sorted(tokens,key=lambda z:z['box'][0]));s=literal.replace(',','').strip();val=int(s) if re.fullmatch(r'\d+',s) else None
     fields[name]=dict(value=val,raw_vision=literal,tokens=tokens,source_field_label=labeltext,label_box=anchor,selection='Original physical x bounds and independently recognized candidate-label row; not control-fitted')
     if typ not in ['summary_TOTAL','blank_or_unresolved_label']:
      if val is None:missing[name]+=1
      else:sums[name]+=val
    if typ not in ['summary_TOTAL','blank_or_unresolved_label']:units+=1
    columns.append(dict(source_column=ordinal,x_bounds=[l,r],native_label_ocr=label,unit_type=typ,fields=fields))
   pages.append(dict(page=x['page'],render_size=[w,h],rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],columns=columns))
  label=key.removeprefix('sos-2024-county-').removesuffix('-updated').replace('-',' ');c=county.get(label);isoriginalpike=key=='sos-2024-county-pike'
  if c:
   expectedvals={name:int(c['2024-senate_'+role]) for name,role in zip(names,['A','B'])}
   if isoriginalpike:expectedvals={'Ty Pinkins':5898,'Roger F. Wicker':6719}
   checks.append(dict(source_id=key,native_labeled_positions=units,numeric_sums=dict(sums),unresolved_values=dict(missing),county_controls=expectedvals,differences={n:sums[n]-expectedvals[n] for n in names},qualification='OCR numeric/label inventory, not accepted transcription. Missing/unlabeled positions and generic/method panels must be reviewed.'))
  out.append(dict(source_id=key,raw_sha256=sha(original(key)),pages=pages,qualification='Independent Vision-source physical-grid reading aid; no peer values imported; all raw words/boxes preserved separately.'))
 save(OUT/'vision-grid-checks.json',checks);(OUT/'extracts/vision-native-grid.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0))
 print(len(out),'sources;',sum(not any(r['differences'].values()) and not any(r['unresolved_values'].values()) for r in checks),'both-candidate numeric closures pending geometry/label review')
 for r in checks:print(r['source_id'].removeprefix('sos-2024-county-'),r['native_labeled_positions'],r['differences'],r['unresolved_values'])
if __name__=='__main__':main()
