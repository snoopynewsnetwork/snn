"""Independent original-image readings of every Union vendor-native profile.

Literal thousands commas below are typed from original glyph panels, never
inferred by normalizing a text-layer decimal or county residual.
"""
import csv,json,re
from collections import Counter
from sources import OUT,BASE,save,sha,original
from build_counties import writecsv
from extract_union_native_profiles import FIELDS
LABELS=['Macedonia - 101','Blythe - 102','Myrtle - 103','Glenfield - 104','Pinedale - 201','West Union - 202','Sportsplex - 203','Ingomar - 204',"King's Chapel - 301",'Courthouse - 302','Central Maintenance - 303','Beacon Hill - 304','Blue Springs - 401','Hillcrest Church - 402','Center - 403','Ellistown Baptist Church - 404','Watson Grove Baptist Church - 501','Keownville - 502','Pleasant Ridge - 503','Jericho - 504']
VALUES=[
[415,308,0,'74.22%',13,0,0,0,294,0,0,0,0,0,308,10,290,8,308],
[355,255,0,'71.83%',19,0,1,0,235,0,0,0,0,0,255,22,230,1,255],
['1,434','1,055',0,'73.57%',144,1,4,1,900,1,0,2,0,1,'1,055',136,902,5,'1,055'],
['1,062',738,0,'69.49%',154,2,1,1,572,0,2,3,0,0,738,145,586,2,738],
[548,404,0,'73.72%',20,0,0,0,380,0,0,1,0,0,404,17,381,3,404],
[851,695,0,'81.67%',39,1,0,0,653,0,0,0,0,0,695,36,646,4,695],
['1,051',769,0,'73.17%',185,1,2,0,566,2,0,9,0,3,769,189,553,9,769],
['1,221',956,0,'78.30%',115,1,0,1,834,0,0,2,0,2,956,115,826,3,956],
[604,485,0,'80.30%',59,0,1,0,420,1,1,1,0,1,485,69,402,4,485],
['1,105',748,0,'67.69%',158,0,0,1,577,0,1,5,1,3,748,147,574,10,748],
['1,004',764,0,'76.10%',67,0,1,2,688,0,0,4,0,1,764,70,682,5,764],
[925,714,0,'77.19%',126,2,0,0,585,0,0,1,0,0,714,118,578,1,714],
[642,498,1,'77.57%',46,1,0,0,446,0,0,1,0,1,498,45,431,3,498],
[900,561,0,'62.33%',160,1,3,2,382,0,0,4,2,3,561,163,380,6,561],
[511,411,0,'80.43%',23,0,0,0,387,0,0,0,0,0,411,24,384,0,411],
['1,101',818,0,'74.30%',113,0,0,0,699,0,0,2,2,1,818,119,680,5,818],
['1,703','1,187',0,'69.70%',287,1,3,4,866,0,1,11,3,1,'1,187',285,879,7,'1,187'],
[743,543,0,'73.08%',34,1,0,0,504,0,1,2,0,0,543,30,504,6,543],
[377,247,0,'65.52%',18,0,0,0,229,0,0,0,0,0,247,19,224,0,247],
[532,377,0,'70.86%',27,0,1,0,342,0,0,4,1,1,377,20,352,2,377]]
def main():
    path=OUT/'union-native-profile-original-extract.json';raw=json.loads(path.read_text());assert sha(original(raw['source_id']))==raw['raw_sha256'];profiles=[];flat=[];totals=Counter();differences=[]
    for i,(p,label,vs) in enumerate(zip(raw['pages'],LABELS,VALUES)):
        assert len(vs)==len(p['fields'])==19;assert sha((BASE/p['full_original_render_path']).read_bytes())==p['render_sha256'];code=re.search(r'(\d{3})$',label).group(1);fields=[];evidence=OUT/'qa/union-independent-profiles'/f'original-field-cards-{i//4+1}.png';assert evidence.exists()
        for f,v in zip(p['fields'],vs):
            lit=str(v);value=float(lit[:-1]) if f['field']=='printed_turnout' else int(lit.replace(',',''));rec=f|dict(printed_literal=lit,value=value,basis='Independent original glyph review, including explicit printed commas/zero glyphs; text-layer punctuation not normalized as authority',evidence_path=str(evidence.relative_to(BASE)),evidence_sha256=sha(evidence.read_bytes()));fields.append(rec)
            if f['field']!='printed_turnout':totals[f['field']]+=value
            if lit!=f['text_layer_literal']:differences.append(dict(source_page=p['source_page'],printed_profile_code=code,field=f['field'],text_layer_literal=f['text_layer_literal'],printed_literal=lit,accepted_original_value=value,original_word_bounds_points=f['text_layer_word_bounds_points'],evidence=rec['evidence_path']))
            flat.append(dict(source_id=raw['source_id'],raw_sha256=raw['raw_sha256'],source_page=p['source_page'],vendor_profile_code=code,native_label_literal=label,native_view='ES&S Precinct Summary vendor profile; separate source view, no SEMS/current crosswalk',field=f['field'],value=value,printed_literal=lit,text_layer_literal=f['text_layer_literal'],original_word_bounds_points=json.dumps(f['text_layer_word_bounds_points']),full_original_render_path=p['full_original_render_path'],render_sha256=p['render_sha256'],evidence_path=rec['evidence_path'],evidence_sha256=rec['evidence_sha256']))
        profiles.append({k:p[k] for k in ['source_page','text_layer_header_literal','full_original_render_path','render_sha256','render_size','render_scale']}|dict(printed_profile_code=code,native_label_literal=label,fields=fields,registration_scope='Printed Registered Voters - Total; active/inactive/status date unspecified on profile',status_literal='Official RESULTS; pre by pre',clock_literal='Precinct Summary - 11/14/2024 4:58 PM',timezone=None,unprinted_undervotes=None,unprinted_overvotes=None))
    summary=next(r for r in json.loads((OUT/'canvass-readings.json').read_text())['readings'] if r['source_id']==raw['source_id']);stats=next(r for r in json.loads((OUT/'canvass-statistics-readings.json').read_text())['readings'] if r['source_id']==raw['source_id']);expected=dict(zip(FIELDS[4:13],[v[0] for v in summary['president']['candidates']]));expected.update(registration=stats['registered_voters_total'],ballots_cast=stats['ballots_cast_total'][0],blank_ballots=stats['ballots_cast_blank'][0],pres_generic_write_in=summary['president']['generic_write_in_marks'][0],pres_contest_total=summary['president']['contest_opportunities'][0],sen_Pinkins=summary['senate']['candidates'][0][0],sen_Wicker=summary['senate']['candidates'][1][0],sen_generic_write_in=summary['senate']['generic_write_in_marks'][0],sen_contest_total=summary['senate']['contest_opportunities'][0]);assert dict(totals)==expected,(totals,expected)
    residuals=dict(president=totals['pres_contest_total']-sum(totals[k] for k in FIELDS[4:14]),senate=totals['sen_contest_total']-sum(totals[k] for k in ['sen_Pinkins','sen_Wicker','sen_generic_write_in']));assert residuals=={'president':37,'senate':186}
    save(OUT/'union-native-profile-readings.json',dict(source_id=raw['source_id'],raw_sha256=raw['raw_sha256'],county_fips='28145',native_view='ES&S Precinct Summary profile, distinct from the SEMS native grid; no cross-view geometry equivalence inferred',qualification='All20 actual original profiles and19required fields each independently visually read. Complete original bytes retain all other offices. Printed turnout is a nonadditive percentage, not a ballot count. Generic marks are not certified named/valid write-ins. Unprinted under/over fields remain unknown; contest residuals are arithmetic only.',original_extract_path=str(path.relative_to(BASE)),original_extract_sha256=sha(path.read_bytes()),profiles=profiles,text_layer_original_literal_differences=differences,controls=dict(profiles=20,required_numeric_fields=380,additive_count_field_vectors=18,printed_turnout_fields_nonadditive=20,field_sums=dict(totals),independent_county_summary_controls=expected,all18_count_field_vectors_match_county_summary=True,contest_unallocated_arithmetic_residuals=residuals,profile_clock='11/14/2024 4:58 PM',county_summary_clock=summary['clock_literal'],no_release_chronology_inferred=True,no_SEMS_or_current_crosswalk_claim=True)))
    writecsv(OUT/'union-native-profile-fields.csv',flat);print('20profiles/380originalfields;18countfieldvectorsclosecounty;literaltextdifferences',len(differences))
if __name__=='__main__':main()
