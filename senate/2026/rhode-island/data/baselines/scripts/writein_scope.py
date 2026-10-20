"""Independent full-detail scope versus captured peer's row-six-onward scope.
Do not omit an actual source row to manufacture agreement.
"""
import io,json,re,xml.etree.ElementTree as ET,zipfile,gzip
from common import *
def main():
    b=body('board2024-writeins-xlsx');z=zipfile.ZipFile(io.BytesIO(b));member='xl/worksheets/sheet7.xml';raw=z.read(member)
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    ss=[''.join(t.text or '' for t in x.iter('{'+ns['m']+'}t')) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    parsed={int(r.get('r')):r for r in ET.fromstring(raw).findall('.//m:row',ns)}
    proof={'source_raw_sha256':sha(b),'member':member,'member_sha256':sha(raw),'sheet_scope':'Cranston; D3 U.S. Senator in Congress:', 'rows':[]}
    for n in [1,3,4,5,6,78]:
        m=re.search(rb'<row\b[^>]*\br="'+str(n).encode()+rb'"[^>]*>.*?</row>',raw,re.S);cells=[]
        for c in parsed[n]:
            v=c.find('m:v',ns);value=v.text if v is not None else None
            if c.get('t')=='s' and value is not None:value=ss[int(value)]
            if re.sub(r'\d','',c.get('r')) in ['A','D','E']:
                cm=re.search(rb'<c\b[^>]*\br="'+c.get('r').encode()+rb'"[^>]*>.*?</c>',raw,re.S)
                cells.append({'cell':c.get('r'),'literal':value,'original_cell_xml':cm[0].decode() if cm else None,
                              'xml_byte_start':cm.start() if cm else None,'xml_byte_end':cm.end() if cm else None})
        proof['rows'].append({'row':n,'xml_byte_start':m.start(),'xml_byte_end':m.end(),'cells':cells})
    require=lambda x: None if x else (_ for _ in ()).throw(AssertionError('Cranston row5 source'))
    row5=next(r for r in proof['rows'] if r['row']==5)
    require(next(c['literal'] for c in row5['cells'] if c['cell']=='D5')=='Mario Frioli ')
    require(next(c['literal'] for c in row5['cells'] if c['cell']=='E5')=='1')
    write_json('extracts/writein-row5-source-proof.json',proof)
    wi=json.loads((BASE/'extracts/2024-senate-writein-reconciliation.json').read_text());cells=json.loads((BASE/'extracts/2024-senate-writein-literal-cells.json').read_text())
    cap=json.loads((BASE/'reciprocal/capture-additional.json').read_text());entry=next(x for x in cap if x['path']=='data/turnout/extracts/writein-scope-comparison.json')
    peer=json.loads(gzip.decompress((BASE/entry['frozen_path']).read_bytes()));pindex={r['municipality'].lower():r for r in peer}
    out=[]
    for t in wi['municipalities']:
        rr=[c for c in cells if c['member']==t['member'] and c['row']>=6 and c['name_literal'] and c['name_literal'].strip().lower()!='total' and c['votes_literal'] is not None]
        six=sum(int(c['votes_literal']) for c in rr);p=pindex[t['municipality_literal'].lower()]
        require(six==p['detail_sum'])
        out.append({'municipality':t['municipality_literal'],'source_all_details_from_row5':t['literal_detail_sum'],
            'row6_onward_details':six,'captured_peer_detail':p['detail_sum'],'generic':t['generic_municipal'],
            'full_detail_minus_generic':t['detail_minus_generic'],'row6_minus_generic':six-t['generic_municipal']})
    write_json('extracts/writein-detail-scope-comparison.json',{'full_source_details_sum':sum(x['source_all_details_from_row5'] for x in out),
        'full_source_discrepancies':[x for x in out if x['full_detail_minus_generic']],
        'row6_onward_sum':sum(x['row6_onward_details'] for x in out),'row6_discrepancies':[x for x in out if x['row6_minus_generic']],
        'municipal_generic':wi['municipal_generic_sum'],'state_generic':wi['state_generic'],'municipalities':out,
        'interpretation':'Complete literal named/count detail includes Cranston D5 Mario Frioli / E5 1. Captured peer detail begins row6 and omits this actual row. Preserve 1227/full8 discrepancies and1226/row6scope9 separately; neither is an eligible named universe or allocation.'})
    print('Full original detail1227/8 discrepancies; peer row6-onward1226/9. Cranston original D5/E5 preserved.')
if __name__=='__main__':main()
