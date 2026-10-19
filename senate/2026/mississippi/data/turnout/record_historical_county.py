"""Record direct visual readings of original historical county TOTAL columns."""
import json
from acquire_sources import OUT,savejson

def record(stage,values):
 prefix='sos-2018-runoff-county-' if stage=='runoff' else 'sos-2018-county-';positions=json.loads((OUT/'source'/('historical-total-positions-'+prefix.rstrip('-')+'.json')).read_text());file=OUT/'historical-county-readings.json';data=json.loads(file.read_text()) if file.exists() else dict(qualification='Manual direct-original source TOTAL readings. Missing readings are not zero; candidates and special-election stages are not combined. Native constituent reconciliation remains separately required.',readings=[])
 names=['Mike Espy','Cindy Hyde-Smith'] if stage=='runoff' else ['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
 for county,vector in values.items():
  sid=prefix+county;assert len(vector)==len(names);pos=next(x for x in positions if x['source_id']==sid);assert not any(x['source_id']==sid for x in data['readings']),sid
  data['readings'].append(dict(source_id=sid,election_date='2018-11-27' if stage=='runoff' else '2018-11-06',contest_literal='United States-Senate Unexpired Term' if stage=='runoff' else 'United States-Senate Special / Unexpired Term (literal heading varies by county; see original)',raw_sha256=pos['raw_sha256'],page=pos['source_page'],source_column=pos['proposed_source_column'],source_TOTAL_heading_visually_verified=True,candidate_votes=dict(zip(names,vector)),party_scope='Source special-election party fields remain source scoped; no Democratic or Republican pool is inferred from these named totals.',source_positions=pos,reading_basis='Direct visual original TOTAL header and every displayed candidate row/cell read independently. No residual allocation.'))
 savejson(file,data);print('reviewedcountyviews',len(data['readings']))

def record_direct(stage,values):
 """Read full originals when machine bounds miss the TOTAL page/field."""
 import gzip
 from acquire_sources import receipts
 prefix='sos-2018-runoff-county-' if stage=='runoff' else 'sos-2018-county-';file=OUT/'historical-county-readings.json';data=json.loads(file.read_text());names=['Mike Espy','Cindy Hyde-Smith'] if stage=='runoff' else ['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']
 for county,reading in values.items():
  pg,col,*vector=reading;assert len(vector)==len(names);sid=prefix+county;assert not any(x['source_id']==sid for x in data['readings']);r=next(x for x in receipts if x['id']==sid);probe=json.loads(gzip.decompress((OUT/'extracts'/(sid+'-historical-probe.json.gz')).read_bytes()));page=next(p for p in probe['pages'] if p['page']==pg)
  data['readings'].append(dict(source_id=sid,election_date='2018-11-27' if stage=='runoff' else '2018-11-06',contest_literal='United States-Senate Unexpired Term' if stage=='runoff' else 'United States-Senate Special / Unexpired Term (literal heading varies by county; see original)',raw_sha256=r['raw_sha256'],page=pg,source_column=col,source_TOTAL_heading_visually_verified=True,candidate_votes=dict(zip(names,vector)),party_scope='Source special-election party fields remain source scoped; no Democratic or Republican pool is inferred from these named totals.',source_positions=dict(page=pg,source_rect=page['source_rect'],rotation_ccw=page['rotation_ccw'],deskew_angle_ccw=page.get('deskew_angle_ccw'),render_size=page['render_size'],evidence_original_preview=page.get('preview'),source_position=f'Full original page{pg}, printed TOTAL column{col}; individual cell boxes not assigned when machine grid was unresolved.'),reading_basis='Complete original page/header and all requested named TOTAL cells directly visually read independently; no peer numeric transcription or residual allocation.'))
 savejson(file,data);print('reviewedcountyviews',len(data['readings']))
