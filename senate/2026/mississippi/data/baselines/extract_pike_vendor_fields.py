"""Own original Pike profile office/label/TOTAL-column field positions.

Candidate order varies by profile; labels identify fields. All42 pages are
inventoried. Missing/ambiguous labels/numbers remain explicit, never zeros.
"""
import gzip,json,re
from collections import defaultdict,Counter
from PIL import Image,ImageDraw
from sources import OUT,BASE,save
from compile_vision_grid import pixels
NAMES=[('Harris','pres_Harris'),('Trump','pres_Trump'),('Kennedy','pres_Kennedy'),('Terry','pres_Terry'),('Shiva','pres_Shiva'),('Oliver','pres_Oliver'),('Stein','pres_Stein'),('Claudia','pres_Claudia'),('Sonsk','pres_Sonski')]
FIELDS=['registration','ballots_cast','blank_ballots','printed_turnout','pres_Harris','pres_Oliver','pres_Stein','pres_Terry','pres_Trump','pres_Shiva','pres_Claudia','pres_Kennedy','pres_Sonski','pres_generic_write_in','pres_total_votes_cast','pres_contest_total','sen_Pinkins','sen_Wicker','sen_generic_write_in','sen_total_votes_cast','sen_contest_total']
def main():
    inv=json.loads((OUT/'pike-vendor-page-inventory.json').read_text());profiles=defaultdict(lambda:dict(pages=[],headers=[],fields=[]));unassigned=[];allobservations=[]
    for p in inv['pages']:
        raw=json.loads(gzip.decompress((BASE/p['own_raw_OCR_path']).read_bytes()));w,h=raw['render_size'];obs=[dict(literal=z['text'],box=pixels(z,w,h),confidence=z['confidence']) for z in raw['observations']];heads=[z for z in obs if re.match(r'^\(\d{1,2}\)',z['literal'])]
        if len(heads)!=1:unassigned.append(dict(source_page=p['source_page'],header_candidates=heads,qualification='No inferred profile from neighboring pages or expected order'));continue
        code=re.match(r'^\((\d{1,2})\)',heads[0]['literal']).group(1);profile=profiles[code];profile['pages'].append(p['source_page']);profile['headers'].append(dict(source_page=p['source_page'],literal=heads[0]['literal'],box=heads[0]['box']));context=None
        for z in sorted(obs,key=lambda z:((z['box'][1]+z['box'][3])/2,z['box'][0])):
            lit=z['literal'];left=z['box'][0];field=None
            if left>.265*w:continue
            if re.match(r'^President United States',lit,re.I):context='president';continue
            if re.match(r'^Senate United States',lit,re.I):context='senate';continue
            if re.match(r'^Statistics',lit,re.I):context='statistics';continue
            if re.search(r'Congress|House.*Represent|Supreme|Circuit|Court of Appeals|School Board|School District|Justice Court|Election Commissioner|Chancery|District Attorney|County Court',lit,re.I):context='other';continue
            if context=='statistics':
                if re.search(r'Registered Voters',lit,re.I):field='registration'
                elif re.search(r'Ballots Cast.*Blank',lit,re.I):field='blank_ballots'
                elif re.search(r'Ballots Cast.*Total',lit,re.I):field='ballots_cast'
                elif re.search(r'Voter T.*out',lit,re.I):field='printed_turnout'
            elif context=='president':
                for token,name in NAMES:
                    if re.search(token,lit,re.I):field=name;break
                if re.search(r'Write.?[Il1]n.*Tota[li]',lit,re.I):field='pres_generic_write_in'
                elif re.search(r'Total Votes Cast',lit,re.I):field='pres_total_votes_cast'
                elif re.search(r'Contest Totals',lit,re.I):field='pres_contest_total'
            elif context=='senate':
                if re.search('Pinkins',lit,re.I):field='sen_Pinkins'
                elif re.search('Wicker',lit,re.I):field='sen_Wicker'
                elif re.search(r'Write.?[Il1]n.*Tota[li]',lit,re.I):field='sen_generic_write_in'
                elif re.search(r'Total Votes Cast',lit,re.I):field='sen_total_votes_cast'
                elif re.search(r'Contest Totals',lit,re.I):field='sen_contest_total'
            if not field:continue
            if field in ['pres_contest_total','sen_contest_total']:context='between_required_offices'
            cy=(z['box'][1]+z['box'][3])/2;rh=z['box'][3]-z['box'][1];pattern=r'[\d,.]+%' if field=='printed_turnout' else r'[\d,.]+'
            values=[v for v in obs if .265*w<v['box'][0]<.345*w and v['box'][2]<.35*w and abs((v['box'][1]+v['box'][3])/2-cy)<max(8,.65*rh) and re.fullmatch(pattern,v['literal'])]
            vb=values[0]['box'] if len(values)==1 else None;literal=values[0]['literal'] if len(values)==1 else None;value=int(literal) if literal and literal.isdigit() else None;rowbox=[max(0,int(z['box'][0]-5)),max(0,int(min([z['box'][1]]+([vb[1]] if vb else []))-5)),int(.35*w),min(h,int(max([z['box'][3]]+([vb[3]] if vb else []))+5))];record=dict(source_page=p['source_page'],field=field,office_context=context,source_label_literal=lit,source_label_box=z['box'],source_value_literal=literal,source_value_candidates=values,source_value_box=vb,complete_original_row_reading_box=rowbox,value_proposal=value,full_original_render_path=p['full_original_render_path'],render_sha256=p['render_sha256'],render_size=p['render_size'],status='Integer raw OCR pending original glyph review' if value is not None else 'Rate/punctuation/unresolved original review required');profile['fields'].append(record);allobservations.append(record)
    cards=[];gaps=[]
    for i,(code,p) in enumerate(sorted(profiles.items()),1):
        index=defaultdict(list)
        for r in p['fields']:index[r['field']].append(r)
        card=Image.new('RGB',(810,850),'white');d=ImageDraw.Draw(card);d.text((5,5),f'{i}. Pike original profile({code}), pages{p["pages"]}; own original glyphs',fill='black');y=30
        for field in FIELDS:
            matches=index[field];d.text((5,y+8),field,fill='black')
            if len(matches)!=1:gaps.append(dict(profile_code=code,field=field,source_matches=len(matches)));d.text((180,y+8),f'UNRESOLVED:{len(matches)} original label matches',fill='black');y+=37;continue
            r=matches[0];im=Image.open(BASE/r['full_original_render_path']);box=r['complete_original_row_reading_box'];crop=im.crop(tuple(box));crop=crop.resize((crop.width*2,crop.height*2));crop.thumbnail((600,33));card.paste(crop,(180,y));y+=37
        cards.append(card)
    for start in range(0,len(cards),4):
        atlas=Image.new('RGB',(1620,1700),'#eeeeee')
        for j,c in enumerate(cards[start:start+4]):atlas.paste(c,((j%2)*810,(j//2)*850))
        atlas.save(OUT/'qa'/f'pike-vendor-original-field-cards-{start//4+1}.png')
    save(OUT/'pike-vendor-field-extract.json',dict(source_id=inv['source_id'],raw_sha256=inv['raw_sha256'],qualification='Original-only independent label/TOTAL-column positions. Candidate field order is identified by own source labels, not assumed ballot/neighbor order. Profile grouping uses exact printed code on each actual page, not page stride. These are reading aids, no accepted numerical cells yet.',source_pages=42,profile_views=len(profiles),required_fields_per_profile=21,profiles=dict(sorted(profiles.items())),unassigned_pages=unassigned,missing_or_duplicate_field_labels=gaps));print('42pages;',len(profiles),'printed profilecodes;',len(allobservations),'requiredfieldobservations;',len(gaps),'labelgaps;',len(unassigned),'unassignedpages')
if __name__=='__main__':main()
