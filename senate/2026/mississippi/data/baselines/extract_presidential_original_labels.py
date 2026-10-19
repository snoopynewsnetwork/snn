"""Fresh candidate-label OCR on unchanged original raster crops, no vote data.

The former rule-removed full-page aid can erase letters too. Retain it and
read the actual source labels separately. A missing candidate remains missing.
"""
import concurrent.futures,gzip,json,re,subprocess
from PIL import Image
from sources import OUT,BASE,save,sha
from extract_replay_president import NAMES,source_layouts
from compile_vision_grid import pixels
PAT=[r'\bHarris\b',r'\bOliver\b',r'\bStein\b',r'\bTerry\b',r'\bTrump\b',r'\bShiva\b',r'\bClaudia\b',r'\bKennedy\b',r'\bSonsk[i1l]?\b']
def main():
    layouts,_=source_layouts('native-2024-senate-reviewed-84views.json');tasks=[];folder=OUT/'extracts/presidential-original-labels';folder.mkdir(exist_ok=True)
    for s in layouts:
        for p in s['pages']:
            raw=json.loads(gzip.decompress((OUT/'extracts/reviewed-replay'/s['source_id']/f'p{p["page"]:04d}.json.gz').read_bytes()));im=Image.open(BASE/raw['raster_path']);left=min(c['header_bounds'][0] for c in p['columns']);top=min(c['header_bounds'][3] for c in p['columns']);bottom=min(c['candidate_bounds']['Ty Pinkins'][1] for c in p['columns']);box=[0,max(0,top-10),left+3,bottom];ident=f'{s["source_id"]}-p{p["page"]:04d}';path=folder/(ident+'.png');dest=folder/(ident+'.json.gz')
            if not path.exists():im.crop(tuple(box)).save(path)
            tasks.append(dict(source_id=s['source_id'],raw_sha256=s['raw_sha256'],page=p['page'],render_size=raw['render_size'],rotation_ccw=raw['rotation_ccw'],deskew_angle_ccw=raw['deskew_angle_ccw'],full_original_render_path=raw['raster_path'],render_sha256=raw['raster_sha256'],original_crop_box=box,crop_path=str(path.relative_to(BASE)),crop_sha256=sha(path.read_bytes()),dest=dest))
    def read(task):
        dest=task['dest'];path=BASE/task['crop_path']
        if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
        result=subprocess.run([str(OUT/'qa/vision-ocr'),str(path)],capture_output=True,text=True,check=True);v=json.loads(result.stdout);im=Image.open(path);w,h=im.size;left,top,_,_=task['original_crop_box'];obs=[]
        for z in v['observations']:
            b=pixels(z,w,h);obs.append(dict(literal=z['text'],original_raster_box=[b[0]+left,b[1]+top,b[2]+left,b[3]+top],confidence=z['confidence']))
        fields=[]
        for name,pat in zip(NAMES,PAT):
            hits=[z for z in obs if re.search(pat,z['literal'],re.I)];fields.append(dict(candidate=name,raw_source_label_hits=hits,status='unique_original_label' if len(hits)==1 else 'missing_original_label' if not hits else 'ambiguous_original_label'))
        x={k:v for k,v in task.items() if k!='dest'};x.update(raw_observations=v,source_observations_with_original_bounds=obs,fields=fields,qualification='Fresh original field-label crop, no line removal, no expected-order identity fill, no candidate number or peer derivative/control read. Original-image review and row bounds remain separate.');dest.write_bytes(gzip.compress(json.dumps(x,ensure_ascii=False).encode(),mtime=0));print(task['source_id'],task['page'],[r['candidate'] for r in fields if r['status']!='unique_original_label'],flush=True);return x
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(read,tasks))
    save(OUT/'source/presidential-original-label-inventory.json',dict(source_pages=len(results),qualification='Original-only label/position aids, not accepted field identity from order alone or a completed all-presidential/native source audit.',pages=[{k:v for k,v in x.items() if k not in ['raw_observations','source_observations_with_original_bounds']} for x in results]))
if __name__=='__main__':main()
