"""Reusable direct-original ledger for distinct 2018 special/runoff grids.

The caller types every candidate/source cell and literal header while viewing
the complete original PDF pages. The independent peer is never a value input.
"""
import csv
import gzip
import io
import json
from PIL import Image
import fitz
from acquire_sources import BASE,OUT,receipts,sha,savejson

def build(county,fips,stages,labels,native_count,total_page,total_column):
    controls=[r for r in csv.DictReader((OUT/'historical-county-candidate-votes.csv').open())
              if r['fips']==fips and r['election_date'] in ('2018-11-06','2018-11-27')]
    sources=[];flat=[]
    for stage in stages:
        sid=stage['source_id'];receipt=next(r for r in receipts if r['id']==sid)
        raw=gzip.decompress((BASE/receipt['path']).read_bytes())
        assert sha(raw)==receipt['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf')
        assert set(stage['candidate_values'])==set(stage['candidate_order'])
        source_pages=sorted(labels[sid]);pages={}
        for number in source_pages:
            im=Image.open(io.BytesIO(doc[number-1].get_pixmap(
                matrix=fitz.Matrix(2.2,2.2),colorspace=fitz.csGRAY).tobytes('png')))
            raster=OUT/f'qa/2018-native-original-probe/{sid}/p{number:04d}-original.png'
            raster.parent.mkdir(parents=True,exist_ok=True);im.save(raster)
            pages[number]=dict(source_pdf_page=number,
                               original_raster=str(raster.relative_to(BASE)),
                               raster_sha256=sha(raster.read_bytes()),
                               render_size=list(im.size))
        rows=[];checks={}
        for candidate in stage['candidate_order']:
            by_page=stage['candidate_values'][candidate]
            assert set(by_page)==set(source_pages)
            native_sum=0;printed=[]
            for page in source_pages:
                values=by_page[page];literal=labels[sid][page]
                assert len(values)==len(literal)
                for ordinal,(header,value) in enumerate(zip(literal,values),1):
                    role='source_TOTAL' if page==total_page and ordinal==total_column else 'source_native_reporting_constituent' if header else 'unused_template_column'
                    if role=='source_TOTAL':
                        assert header=='TOTAL' and isinstance(value,int)
                        printed.append(value)
                    elif role=='source_native_reporting_constituent':
                        assert isinstance(value,int) and value>=0
                        native_sum+=value
                    else:assert value is None and header==''
                    rows.append(dict(source_id=sid,election_date=stage['date'],county=county,
                                     county_fips=fips,source_raw_sha256=receipt['raw_sha256'],
                                     source_pdf_page=page,physical_source_column=ordinal,
                                     source_native_key=f'{fips}:{sid}:p{page}:c{ordinal}',
                                     literal_source_header=header,role=role,
                                     office_context_literal=stage['office'],candidate=candidate,
                                     party_field_literal=None,votes=value,
                                     original_raster=pages[page]['original_raster'],
                                     reading_basis='direct_complete_original_page_visual' if value is not None else 'visibly_unprinted_template_cell'))
            assert len(printed)==1 and native_sum==printed[0],(sid,candidate,native_sum,printed)
            ctl=next(r for r in controls if r['source_id']==sid and r['candidate']==candidate)
            assert int(ctl['votes'])==printed[0] and ctl['raw_sha256']==receipt['raw_sha256'] and int(ctl['source_page'])==total_page
            checks[candidate]=dict(native_sum=native_sum,printed_TOTAL=printed[0],
                                   county_control=ctl['votes'],passes=True,
                                   earlier_county_control_TOTAL_column_hint=ctl.get('source_TOTAL_column'),
                                   earlier_county_control_TOTAL_column_hint_status='unaccepted_locator_if_different_from_direct_original_physical_column')
        assert len(rows)==len(stage['candidate_order'])*sum(len(labels[sid][p]) for p in source_pages)
        assert sum(r['role']=='source_native_reporting_constituent' for r in rows)==native_count*len(stage['candidate_order'])
        sources.append(dict(source_id=sid,election_date=stage['date'],contest=stage['office'],
                            source_raw_sha256=receipt['raw_sha256'],source_original_path=receipt['path'],
                            source_pdf_page_count=len(doc),pages=[pages[p] for p in source_pages],
                            native_constituents=native_count,physical_TOTAL_page=total_page,
                            physical_TOTAL_column=total_column,candidate_checks=checks,rows=rows,
                            scope='Source-native special-stage identities and literal headers only; no party field printed beside selected rows, no regular ClassI pooling or cross-stage/current geographic join.'))
        flat.extend(rows)
    assert len(sources)==2 and len({s['source_id'] for s in sources})==2
    output=dict(scope='Distinct 2018 ClassII special-election Nov6 and Nov27 runoff original native source grids, separately read and reconciled. Peer comparison is subsequent.',
                sources=sources,total_candidate_positions=len(flat),
                native_constituents_per_stage=native_count)
    savejson(OUT/f'2018-{county.lower()}-two-stage-native-original-readings.json',output)
    with (OUT/f'2018-{county.lower()}-two-stage-native-original-cells.csv').open('w',newline='') as f:
        fields=list(flat[0]);writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(flat)
    print('2018',county,'distinct special stages',len(flat),'positions;',
          native_count,'native per stage, physical TOTAL',total_page,total_column)
