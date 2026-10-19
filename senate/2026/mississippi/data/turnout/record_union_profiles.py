"""Explicit independent original-image readings of all20 Union profiles.

Input vectors typed from the unaltered original reading panels, not county
residuals or peer derivatives. Original text-layer discrepancies remain visible.
"""
import json
from acquire_sources import OUT,savejson,sha
from read_physical_native import PRES24

# page,label,statistics(registration,ballots,blank,printed %),
# nine President rows,generic,total; two Senate rows,generic,total
READINGS=[
 (16,'Macedonia - 101',[415,308,0,74.22],[13,0,0,0,294,0,0,0,0,0,308],[10,290,8,308]),
 (18,'Blythe - 102',[355,255,0,71.83],[19,0,1,0,235,0,0,0,0,0,255],[22,230,1,255]),
 (20,'Myrtle - 103',[1434,1055,0,73.57],[144,1,4,1,900,1,0,2,0,1,1055],[136,902,5,1055]),
 (22,'Glenfield - 104',[1062,738,0,69.49],[154,2,1,1,572,0,2,3,0,0,738],[145,586,2,738]),
 (24,'Pinedale - 201',[548,404,0,73.72],[20,0,0,0,380,0,0,1,0,0,404],[17,381,3,404]),
 (26,'West Union - 202',[851,695,0,81.67],[39,1,0,0,653,0,0,0,0,0,695],[36,646,4,695]),
 (28,'Sportsplex - 203',[1051,769,0,73.17],[185,1,2,0,566,2,0,9,0,3,769],[189,553,9,769]),
 (30,'Ingomar - 204',[1221,956,0,78.30],[115,1,0,1,834,0,0,2,0,2,956],[115,826,3,956]),
 (32,"King's Chapel - 301",[604,485,0,80.30],[59,0,1,0,420,1,1,1,0,1,485],[69,402,4,485]),
 (34,'Courthouse - 302',[1105,748,0,67.69],[158,0,0,1,577,0,1,5,1,3,748],[147,574,10,748]),
 (36,'Central Maintenance - 303',[1004,764,0,76.10],[67,0,1,2,688,0,0,4,0,1,764],[70,682,5,764]),
 (38,'Beacon Hill - 304',[925,714,0,77.19],[126,2,0,0,585,0,0,1,0,0,714],[118,578,1,714]),
 (40,'Blue Springs - 401',[642,498,1,77.57],[46,1,0,0,446,0,0,1,0,1,498],[45,431,3,498]),
 (42,'Hillcrest Church - 402',[900,561,0,62.33],[160,1,3,2,382,0,0,4,2,3,561],[163,380,6,561]),
 (44,'Center - 403',[511,411,0,80.43],[23,0,0,0,387,0,0,0,0,0,411],[24,384,0,411]),
 (46,'Ellistown Baptist Church - 404',[1101,818,0,74.30],[113,0,0,0,699,0,0,2,2,1,818],[119,680,5,818]),
 (48,'Watson Grove Baptist Church - 501',[1703,1187,0,69.70],[287,1,3,4,866,0,1,11,3,1,1187],[285,879,7,1187]),
 (50,'Keownville - 502',[743,543,0,73.08],[34,1,0,0,504,0,1,2,0,0,543],[30,504,6,543]),
 (52,'Pleasant Ridge - 503',[377,247,0,65.52],[18,0,0,0,229,0,0,0,0,0,247],[19,224,0,247]),
 (54,'Jericho - 504',[532,377,0,70.86],[27,0,1,0,342,0,0,4,1,1,377],[20,352,2,377]),
]

def main():
 extraction=json.loads((OUT/'native-profile-union-extraction.json').read_text());by={p['source_page']:p for p in extraction['profiles']};profiles=[];differences=[]
 fields=PRES24+['president_generic_write_in','president_contest_total','Ty Pinkins','Roger F. Wicker','senate_generic_write_in','senate_contest_total','registration_total','ballots_cast_total','ballots_blank','voter_turnout_percent']
 for page,label,stats,pres,sen in READINGS:
  p=by[page];p['native_label_text_layer_literal']=p['native_label_literal'];p['native_label_literal']=label
  if p['native_label_text_layer_literal']!=label:differences.append(dict(page=page,field='native_label_literal',raw_text_layer=p['native_label_text_layer_literal'],original_visual=label,qualification='Source image reading retains label; text-layer spacing/case differs.'))
  for name,value in zip(fields,pres+sen+stats):
   f=p['fields'][name];old=f['value'];f['text_layer_value']=old;f['value']=value;f['reading_basis']='Direct unaltered original profile image, all fields independently read'
   if old!=value:differences.append(dict(page=page,field=name,raw_text_layer=f['literal'],text_layer_value=old,original_visual=value,qualification='Explicit source image reading, no punctuation normalization or county residual allocation.'))
  pointer=OUT/f'qa/union-profiles/original-p{page}-pointer.json';p['original_visual_evidence']=json.loads(pointer.read_text());p['original_visual_evidence']['pointer_sha256']=sha(pointer.read_bytes());p['review_status']='independent_original_visual_review_all_required_profile_fields'
  p['printed_native_id_scope']='Source profile precinct code only; no SEMS/current/crossyear identity equivalence established.'
  p['candidate_identity_mapping']=dict(president=dict(zip(PRES24,['D Kamala D. Harris / Tim Walz','L Chase Oliver / Mike ter Maat','G Jill Stein / Rudolph Ware','C Randall Terry / Stephen E. Broden','R Donald J. Trump / JD Vance','I Shiva Ayyadurai / Crystal Ellis','I Claudia De la Cruz / Karina Garcia','I Robert F. Kennedy Jr. / Nicole','I Peter Sonsk / Lauren Onak'])),senate={'Ty Pinkins':'D Ty Pinkins','Roger F. Wicker':'R Roger F. Wicker'})
  p['candidate_identity_qualification']='Canonical candidate identity follows source office and printed row position; literal printed abbreviated/truncated ticket labels and parties retained separately. Sonsk printed without final i; Kennedy ticket prints Nicole without surname. No invented source text.'
  p['unallocated_contest_residuals']={office:p['fields'][office+'_contest_total']['value']-sum(p['fields'][n]['value'] for n in names)-p['fields'][office+'_generic_write_in']['value'] for office,names in [('president',PRES24),('senate',['Ty Pinkins','Roger F. Wicker'])]}
  profiles.append(p)
 sums={n:sum(p['fields'][n]['value'] for p in profiles) for n in fields if n!='voter_turnout_percent'}
 savejson(OUT/'native-profile-union-readings.json',dict(source_id=extraction['source_id'],raw_sha256=extraction['raw_sha256'],profiles=profiles,field_sums=sums,text_layer_original_visual_differences=differences,qualification='20 disjoint source-native ES&S profile views. Alternative to SEMS; never added together or joined by names/counts. Generic marks not adjudicated named write-ins. Under/over and method breakdown unprinted and null; displayed contest residuals remain unallocated.'))
 print('20 Union profiles independently original-read;',len(fields)*20,'numeric fields;',len(differences),'explicit source-text-layer differences');print(json.dumps(sums))

if __name__=='__main__':main()
