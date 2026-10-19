"""Keep all104 historical publications visible while native source review grows."""
import json
from collections import Counter,defaultdict
from sources import OUT,BASE,save,sha,original
def main():
    sources=[];pins=[]
    for filename in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']:
        p=OUT/filename;raw=p.read_bytes();pins.append(dict(path=str(p.relative_to(BASE)),bytes=len(raw),sha256=sha(raw)))
        for s in json.loads(raw)['sources']:
            assert sha(original(s['source_id']))==s['raw_sha256'];sums=Counter();totals={};native=total=unused=numeric=null=admin=0;admin_sums=Counter()
            for pg in s['pages']:
                for col in pg['columns']:
                    r=col['role'];native+=r=='source_native_reporting_constituent';total+=r=='source_TOTAL';unused+=r=='unused_template_column';admin+=r=='source_administrative_reporting_column'
                for f in pg['fields']:
                    assert len(f['values'])==len(pg['columns'])
                    for c,v in zip(pg['columns'],f['values']):
                        if c['role']=='unused_template_column':assert v is None;null+=1
                        else:
                            assert isinstance(v,int) and v>=0;numeric+=1
                            if c['role']=='source_native_reporting_constituent':sums[f['candidate']]+=v
                            elif c['role']=='source_administrative_reporting_column':admin_sums[f['candidate']]+=v
                            else:totals[f['candidate']]=v
            assert total==1 and {k:sums[k]+admin_sums[k] for k in totals}==totals and len(totals)==3
            sources.append(dict(source_id=s['source_id'],raw_sha256=s['raw_sha256'],physical_TOTAL_positions=[dict(PDFpage=pg['page'],physical_column=col['source_column'],header_bounds=col['header_bounds']) for pg in s['pages'] for col in pg['columns'] if col['role']=='source_TOTAL'],original_reading_path=str(p.relative_to(BASE)),original_pages=[pg['page'] for pg in s['pages']],native_constituents=native,administrative_columns=admin,administrative_candidate_sums=dict(admin_sums),TOTAL_columns=total,unused_columns=unused,numeric_positions=numeric,unused_null_positions=null,candidate_sums={k:sums[k]+admin_sums[k] for k in totals},all_three_native_vectors_close_source_TOTAL=True))
    accepted={s['source_id']:s for s in sources};assert len(accepted)==len(sources);publications=json.loads((OUT/'county-2020-publication-controls.json').read_text())['readings'];bycounty=defaultdict(list)
    for p in publications:bycounty[p['county_key']].append(p)
    selected={next((p['source_id'] for p in rr if p['source_id'].endswith('-amended')),rr[0]['source_id']) for rr in bycounty.values()};assert len(selected)==82;status=[]
    for p in publications:
        s=accepted.get(p['source_id'])
        if s:assert s['raw_sha256']==p['raw_sha256'] and s['candidate_sums']==p['candidate_values']
        status.append(dict(source_id=p['source_id'],raw_sha256=p['raw_sha256'],publication_label=p['publication_label'],publication_variant=p['publication_variant'],county_key=p['county_key'],selected_for_82_county_amended_where_explicit_control=p['source_id'] in selected,native_three_candidate_original_review_complete=s is not None,reviewed_native_constituents=s['native_constituents'] if s else None,county_candidate_TOTAL_control=p['candidate_values'],qualification='Source-specific original native review complete for threeSenate candidates; vendor/method/ballot/registration coverage separate' if s else 'Native unit universe/fields not yet accepted; unknown count, not zero or copied from2024'))
    assert len(status)==104;counts={k:sum(s[k] for s in sources) for k in ['native_constituents','administrative_columns','TOTAL_columns','unused_columns','numeric_positions','unused_null_positions']};counts.update(reviewed_source_publications=len(sources),total_source_publications=104,reviewed_selected82_publications=sum(s['source_id'] in selected for s in sources),selected82_reviewed_native_constituents=sum(s['native_constituents'] for s in sources if s['source_id'] in selected))
    complete104=len(accepted)==104;selected_complete=all(sid in accepted for sid in selected)
    selected_native_sums={name:sum(accepted[sid]['candidate_sums'][name] for sid in selected if sid in accepted) for name in ['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']}
    if selected_complete:assert selected_native_sums=={'Mike Espy':578691,'Cindy Hyde-Smith':709511,'Jimmy L. Edwards':23152}
    total_audit=[]
    for p in publications:
        s=accepted.get(p['source_id'])
        if not s:continue
        actual=s['physical_TOTAL_positions'];assert len(actual)==1 and actual[0]['PDFpage']==p['source_page']
        total_audit.append(dict(source_id=p['source_id'],raw_sha256=p['raw_sha256'],publication_label=p['publication_label'],publication_variant=p['publication_variant'],actual_original_reviewed_TOTAL=actual[0],earlier_county_control_accepted_physical_column=p['source_column_accepted'],earlier_machine_proposed_column=p['source_column_proposed'],earlier_accepted_column_agrees=p['source_column_accepted'] in [None,actual[0]['physical_column']],earlier_proposal_agrees=p['source_column_proposed']==actual[0]['physical_column'],candidate_values=s['candidate_sums'],selected_for82=p['source_id'] in selected))
    save(OUT/'native-2020-physical-TOTAL-audit.json',dict(qualification='Fresh complete original native-grid physical TOTAL positions; earlier county-control accepted/proposed locator fields preserved separately without mutating that earlier ledger. All native three-candidate closures are source-publication scoped, not a chronology/common-vintage or method/native2026 approval.',source_publications=len(total_audit),physical_locator_counts=dict(prior_accepted=sum(a['earlier_county_control_accepted_physical_column'] is not None for a in total_audit),prior_accepted_disagreements=sum(a['earlier_county_control_accepted_physical_column'] is not None and not a['earlier_accepted_column_agrees'] for a in total_audit),prior_unaccepted=sum(a['earlier_county_control_accepted_physical_column'] is None for a in total_audit),prior_unaccepted_proposal_disagreements=sum(a['earlier_county_control_accepted_physical_column'] is None and not a['earlier_proposal_agrees'] for a in total_audit),all_nonnull_proposals=sum(a['earlier_machine_proposed_column'] is not None for a in total_audit),all_nonnull_proposal_disagreements=sum(a['earlier_machine_proposed_column'] is not None and not a['earlier_proposal_agrees'] for a in total_audit)),complete_all104=complete104,readings=total_audit,selected82_native_candidate_sums=selected_native_sums,selected82_complete=selected_complete))
    save(OUT/'native-2020-coverage.json',dict(qualification='All104 county-index publication vintages stay separate; only explicitly reviewed native3candidate scopes accepted. Selected82 chooses actual linked amendment where present for comparison with countyCSV, without a common release chronology inference. Unreviewed native counts/fields are unknown, no2024identity join or zero-fill.',inputs=pins,counts=counts,complete_all104_native_Senate_three_candidates=complete104,complete_selected82_native_Senate_three_candidates=selected_complete,selected82_native_candidate_sums=selected_native_sums,complete2020_native_qualification='The broad flag remains false for remaining vendor/method/ballot/registration dimensions; the narrow three-named-Senate-candidate publication flags above state actual completion.',reviewed_sources=sources,all104_publication_status=status,complete2020_native=False,complete_historical_methods=False,current2026_geography_approved=False));print('2020 native publication coverage',counts)
if __name__=='__main__':main()
