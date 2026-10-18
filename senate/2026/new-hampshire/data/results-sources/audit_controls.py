#!/usr/bin/env python3
"""Read-only independent federal publication controls, original bytes and positions."""
import gzip,json,re,subprocess
from acquire import ROOT,dump,sha
from extract_history import STATE,TURN,read_original,gzwrite

def main():
    inv={r['source_id']:r for r in json.load(open(TURN/'source-inventory.json'))}
    refs=[];texts={};positions={}
    ids=['house-clerk-2020','house-clerk-2022','house-clerk-2024','fec-pres-2024','nara-2024-index','nara-2024-NH-ascertainment']
    for sid in ids:
        r=inv[sid];b=read_original(r);mp=(TURN/r['metadata_path']).resolve()
        ref={**r,'path':str((TURN/r['path']).resolve().relative_to(STATE)),'metadata_path':str(mp.relative_to(STATE)),'metadata_sha256':sha(mp.read_bytes()),'metadata_bytes':mp.stat().st_size,'path_base':'state directory'}
        refs.append(ref)
        if not b.startswith(b'%PDF'):continue
        t=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True).stdout.decode()
        texts[sid]=t
        lines=[{'page':pi,'line':li,'text':s} for pi,p in enumerate(t.split('\f'),1) for li,s in enumerate(p.splitlines(),1)]
        gzwrite(ROOT/'derived'/(sid+'-control-original-positions.jsonl.gz'),lines)
        (ROOT/'derived'/(sid+'-control.txt.gz')).write_bytes(gzip.compress(t.encode(),mtime=0))
        if sid.startswith('house'):
            selected=[]
            for pi,p in enumerate(t.split('\f'),1):
                if 'NEW HAMPSHIRE' not in p:continue
                p=p[p.index('NEW HAMPSHIRE'):]
                if 'NEW JERSEY' in p:p=p[:p.index('NEW JERSEY')]
                selected.extend({'page':pi,'text':p} for _ in [0])
            positions[sid]=selected
        elif sid=='fec-pres-2024':positions[sid]=[r for r in lines if re.match(r'^\s*NH\s',r['text'])]
        else:positions[sid]=lines
    # House data are panel scoped. Repeated recap rows and electors are never added.
    expected={
        'house-clerk-2020':{'shaheen':450778,'messner':326229,'odonnell':18421,'scatter':486},
        'house-clerk-2022':{'bolduc':275928,'hassan':332193,'kauffman':12390,'scatter':464},
        'house-clerk-2024':{'trump_vance':395523,'harris_walz':418488,'undervotes':4482,'oliver_ter_maat':4425,'generic_write_ins':4073,'stein_ware':3680,'overvotes':362}}
    for sid,fields in expected.items():
        panel='\n'.join(p['text'] for p in positions[sid])
        for v in fields.values():assert f'{v:,}' in panel,(sid,v)
    rows=positions['fec-pres-2024'];assert len(rows)==5
    for page,values in [(3,[418488]),(4,[4425,3680]),(5,[395523]),(6,[4073,826189])]:
        r=next(r for r in rows if r['page']==page)
        assert [int(v.replace(',','')) for v in re.findall(r'\d[\d,]*',r['text'])]==values,(page,r)
    dump(ROOT/'source/control-original-references.json',refs)
    dump(ROOT/'independent-controls.json',{
        'status':'pass_with_preserved_2022_disagreement','house_fields':expected,'raw_panel_positions':positions,
        'fec_nh_reported_numeric_total':826189,'house_2024_recap_including_under_over':831033,
        'house_2020_senate_sum':sum(expected['house-clerk-2020'].values()),'house_2022_senate_sum':620975,
        '2022_house_minus_linked_sos5':{'bolduc':297,'hassan':-297,'kauffman':0,'scatter':0},
        'nara_visual_scope':'Page1 independently viewed: four electoral slates repeat each ticket vote four times, not four vote universes. Amended certificate bears Dec4,2024 testimony. No generic-write-in/under/over universe on this certificate; no additions from repeated elector names.',
        'cross_publication_limit':'House2022 agrees earlierSOS_2, not linkedSOS_5/remediatedPDF. Federal publication is an independent control, not a license to rescale either original. FEC826189 includes reported generic/scattered write-ins, not proof all are valid named votes.'})
    print('PASS: House2020/2022/2024 panels and FEC2024 five NH positions; independent controls preserve2022 discrepancy')
if __name__=='__main__':main()
