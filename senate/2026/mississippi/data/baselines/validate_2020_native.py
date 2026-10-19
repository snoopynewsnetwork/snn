"""Offline validation of source-specific original 2020 native Senate readings.

The accepted universe is bounded explicitly; unknown native universes are never
filled from county controls, 2024 names, or a matching amendment vector.
"""
import copy,csv,gzip,io,json,re
from collections import Counter
from PIL import Image,ImageChops
from sources import OUT,BASE,original,save,sha

NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
PARTIES=['Democrat','Republican','Libertarian']

def versioned_source_relation(prior,later):
    """Require exact prior bytes' semantics, except explicit source-glyph metadata history.

    This does not normalize labels. It checks the precise old/new strings,
    retains the old witness, and rejects any other semantic/number/bounds change.
    """
    if prior==later:return []
    reverted=copy.deepcopy(later);changes=[]
    prior_pages={p['page']:p for p in prior['pages']}
    for page in reverted['pages']:
        pp=prior_pages[page['page']];kept=[]
        for evidence in page.get('header_reading_evidence',[]):
            if evidence in pp.get('header_reading_evidence',[]):kept.append(evidence);continue
            assert evidence.get('correction_kind')=='literal_header_glyph_reread'
            i=evidence['source_column']-1;old=pp['columns'][i]['label_literal'];new=page['columns'][i]['label_literal']
            assert old==evidence['initial_manual_literal'] and new==evidence['accepted_literal'] and old!=new
            changes.append(dict(source_id=later['source_id'],source_page=page['page'],source_column=i+1,prior_literal=old,accepted_literal=new,evidence_path=evidence['evidence_path'],evidence_sha256=evidence['evidence_sha256']))
            page['columns'][i]['label_literal']=old
        if kept:page['header_reading_evidence']=kept
        else:page.pop('header_reading_evidence',None)
    assert changes and reverted==prior,(later['source_id'],'Unexpected change beyond source-glyph metadata history')
    return changes

def main():
    additional=json.loads((OUT/'native-2020-additional-readings.json').read_text())
    coverage=json.loads((OUT/'native-2020-coverage.json').read_text())
    publication={r['source_id']:r for r in json.loads((OUT/'county-2020-publication-controls.json').read_text())['readings']}
    counties={r['county'].lower().replace(' ','-'):r['fips'] for r in csv.DictReader((BASE/'data/county-baselines.csv').open())}
    observed=list(csv.DictReader((OUT/'native-2020-additional-candidate-votes.csv').open()))
    rows={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in observed}
    assert len(rows)==len(observed)
    seen=set();counts=Counter();corrections=[];header_evidence=[];raster_paths=set()
    for source in additional['sources']:
        sid=source['source_id'];control=publication[sid];raw=original(sid)
        assert sid not in seen and sha(raw)==source['raw_sha256']==control['raw_sha256'];seen.add(sid)
        assert source['county_fips']==counties[control['county_key']]
        assert all(source[k]==control[k] for k in ['publication_label','publication_variant','parent_source_id','requested_url','final_url'])
        sums=Counter();totals={};total_positions=[];physical=set()
        for page in source['pages']:
            pg=page['page'];path=BASE/page['full_original_render_path'];raster_paths.add(str(path));assert sha(path.read_bytes())==page['render_sha256']
            receipt=json.loads(path.with_name(f'p{pg:04d}-render.json').read_text())
            assert receipt['PDFpage']==pg and receipt['raw_sha256']==source['raw_sha256'] and receipt['render_sha256']==page['render_sha256']
            assert receipt['original_bytes']==len(raw) and receipt['render_size']==page['render_size'] and receipt['PDFpage_count']>=pg
            w,h=page['render_size'];columns=page['columns'];assert [c['source_column'] for c in columns]==list(range(1,len(columns)+1))
            assert [f['candidate'] for f in page['fields']]==NAMES and [f['party_literal'] for f in page['fields']]==PARTIES
            previous_right=None
            for col in columns:
                pos=(pg,col['source_column']);assert pos not in physical;physical.add(pos)
                l,t,r,b=col['header_bounds'];assert 0<=l<r<=w and 0<=t<b<=h
                if previous_right is not None:assert l==previous_right
                previous_right=r;role=col['role'];counts[role]+=1
                assert role in ['source_native_reporting_constituent','source_administrative_reporting_column','source_TOTAL','unused_template_column']
                if role in ['source_native_reporting_constituent','source_administrative_reporting_column']:assert col['label_literal']
                elif role=='source_TOTAL':assert col['label_literal']=='TOTAL';total_positions.append(pos)
                else:assert col['label_literal']=='' and col['literal_printed_id'] is None
            for field in page['fields']:
                name=field['candidate'];assert len(field['values'])==len(columns)
                l,t,r,b=field['row_bounds'];assert 0<=l<r<=w and 0<=t<b<=h
                for col,value in zip(columns,field['values']):
                    role=col['role'];row=rows.pop((sid,pg,col['source_column'],name))
                    assert row['source_key']==f'{sid}:p{pg}:c{col["source_column"]}' and row['source_raw_sha256']==source['raw_sha256']
                    assert row['county_fips']==source['county_fips'] and row['role']==role and row['literal_native_label']==col['label_literal']
                    assert row['literal_printed_id']==(col['literal_printed_id'] or '')
                    counts['optional_printed_id_absent_positions']+=col['literal_printed_id'] is None
                    assert row['party_literal']==field['party_literal'] and row['full_original_render_path']==page['full_original_render_path'] and row['render_sha256']==page['render_sha256']
                    assert json.loads(row['header_bounds_pixels'])==col['header_bounds']
                    assert json.loads(row['candidate_reading_window_pixels'])==[col['header_bounds'][0],t,col['header_bounds'][2],b]
                    if role=='unused_template_column':assert value is None and row['votes']=='';counts['unused_null_positions']+=1
                    else:
                        assert type(value) is int and value>=0 and int(row['votes'])==value;counts['candidate_numeric_positions']+=1
                        if role in ['source_native_reporting_constituent','source_administrative_reporting_column']:sums[name]+=value
                        else:totals[name]=value
            for correction in page.get('numeric_correction_history',[]):
                field=next(f for f in page['fields'] if f['candidate']==correction['candidate'])
                assert field['values'][correction['source_column']-1]==correction['accepted_original_reading']
                assert correction['initial_manual_reading']!=correction['accepted_original_reading']
                crop=BASE/correction['evidence_crop_path'];assert sha(crop.read_bytes())==correction['evidence_crop_sha256'] and crop.stat().st_size==correction['evidence_crop_bytes']
                assert ImageChops.difference(Image.open(path).crop(correction['evidence_crop_bounds']),Image.open(crop)).getbbox() is None
                corrections.append(dict(source_id=sid,source_page=pg,**correction))
            for reading in page.get('header_reading_evidence',[]):
                assert columns[reading['source_column']-1]['label_literal']==reading['accepted_literal']
                crop=BASE/reading['evidence_path'];assert sha(crop.read_bytes())==reading['evidence_sha256'] and crop.stat().st_size==reading['evidence_bytes']
                assert ImageChops.difference(Image.open(path).crop(reading['bounds']).rotate(reading.get('rotate_ccw',0),expand=True),Image.open(crop)).getbbox() is None
                header_evidence.append(dict(source_id=sid,source_page=pg,**reading))
            if page.get('header_rule_probe'):
                probe=page['header_rule_probe'];p=BASE/probe['path'];assert p.stat().st_size==probe['bytes'] and sha(p.read_bytes())==probe['sha256'];q=json.loads(p.read_text());assert q['source_id']==sid and q['PDFpage']==pg and q['raw_sha256']==source['raw_sha256'] and q['render_sha256']==page['render_sha256'];assert q['accepted_physical_rule_x']==[columns[0]['header_bounds'][0]]+[c['header_bounds'][2] for c in columns]
        assert len(total_positions)==1 and total_positions[0]==(source['metadata_acceptance']['actual_TOTAL_PDFpage'],source['metadata_acceptance']['actual_TOTAL_physical_column'])
        assert dict(sums)==totals==control['candidate_values']==source['controls']['printed_TOTAL']
    assert not rows and len(seen)==additional['counts']['source_views']
    for key,value in additional['counts'].items():
        if key=='source_views':continue
        assert counts[key]==value,(key,counts[key],value)
    statuses=coverage['all104_publication_status'];assert len(statuses)==len({r['source_id'] for r in statuses})==104
    assert sum(r['selected_for_82_county_amended_where_explicit_control'] for r in statuses)==82
    for status in statuses:
        assert status['native_three_candidate_original_review_complete']==(status['source_id'] in {r['source_id'] for r in coverage['reviewed_sources']})
        if not status['native_three_candidate_original_review_complete']:assert status['reviewed_native_constituents'] is None
    complete104=all(r['native_three_candidate_original_review_complete'] for r in statuses)
    assert coverage['complete_all104_native_Senate_three_candidates']==complete104
    assert coverage['complete_selected82_native_Senate_three_candidates']==all(r['native_three_candidate_original_review_complete'] for r in statuses if r['selected_for_82_county_amended_where_explicit_control'])
    ta=json.loads((OUT/'native-2020-physical-TOTAL-audit.json').read_text());assert ta['complete_all104']==complete104 and ta['source_publications']==coverage['counts']['reviewed_source_publications']
    if complete104:assert ta['physical_locator_counts']==dict(prior_accepted=51,prior_accepted_disagreements=0,prior_unaccepted=53,prior_unaccepted_proposal_disagreements=10,all_nonnull_proposals=55,all_nonnull_proposal_disagreements=11)
    reviewed={s['source_id']:s for s in coverage['reviewed_sources']}
    for a in ta['readings']:
        source=reviewed[a['source_id']];c=publication[a['source_id']]
        assert a['actual_original_reviewed_TOTAL']==source['physical_TOTAL_positions'][0]
        assert a['raw_sha256']==c['raw_sha256'] and a['candidate_values']==c['candidate_values']
        assert a['earlier_county_control_accepted_physical_column']==c['source_column_accepted'] and a['earlier_machine_proposed_column']==c['source_column_proposed']
    if complete104:assert coverage['selected82_native_candidate_sums']==ta['selected82_native_candidate_sums']=={'Mike Espy':578691,'Cindy Hyde-Smith':709511,'Jimmy L. Edwards':23152}
    witnesses=[];previous={}
    folders=sorted((p for p in (OUT/'source').glob('native-2020-*views-v*/snapshot.json') if re.fullmatch(r'native-2020-[0-9]+views-v[0-9]+',p.parent.name)),key=lambda p:int(p.parent.name.split('-')[2].split('views')[0]))
    for sp in folders:
        witness=json.loads(sp.read_text());assert len(witness['pins'])==4;frozen_additional=None
        for pin in witness['pins']:
            body=(BASE/pin['stored_path']).read_bytes();assert len(body)==pin['stored_bytes']<40000000 and sha(body)==pin['stored_sha256']
            raw=gzip.decompress(body);assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
            if pin['original_path'].endswith('/native-2020-additional-readings.json'):frozen_additional=json.loads(raw)
        current={r['source_id']:r for r in frozen_additional['sources']};metadata_changes=[]
        for k,v in previous.items():metadata_changes.extend(versioned_source_relation(v,current[k]))
        previous=current
        witnesses.append(dict(path=str(sp.relative_to(BASE)),sha256=sha(sp.read_bytes()),bytes=sp.stat().st_size,counts=witness['counts'],all4_lossless_pins_verified=True,prior_source_objects_unchanged=not metadata_changes,explicit_source_header_corrections=metadata_changes,prior_witness_bytes_unchanged=True))
    working_metadata_changes=[]
    for k,v in previous.items():working_metadata_changes.extend(versioned_source_relation(v,next(r for r in additional['sources'] if r['source_id']==k)))
    save(OUT/'native-2020-validation.json',dict(status='pass_bounded_original_publication_scopes',additional_source_publications=len(seen),additional_flat_candidate_positions=len(observed),additional_counts=dict(counts),combined_counts=coverage['counts'],original_rasters_verified=len(raster_paths),correction_histories=corrections,header_reading_evidence=header_evidence,working_source_header_corrections=working_metadata_changes,immutable_witnesses=witnesses,optional_absent_id_qualification='Empty CSV versus null JSON representations do not establish positive printed-ID agreement',exact_candidate_numeric_polygons_approved=False,unreviewed_native_counts_unknown=True,complete_all104_native_Senate_three_candidates=complete104,complete_selected82_native_Senate_three_candidates=coverage['complete_selected82_native_Senate_three_candidates'],complete2020_native=False,complete_historical_methods=False,current2026_geography_approved=False))
    print('PASS bounded2020 native:',coverage['counts'],'additional flat positions',len(observed),'immutable witnesses',len(witnesses))

if __name__=='__main__':main()
