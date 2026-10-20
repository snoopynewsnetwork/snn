"""Literal 2024 Senate write-in worksheet cells; no spelling merge or eligibility inference."""
import io,zipfile,xml.etree.ElementTree as E,re,subprocess
from common import *
def run():
    r=json.loads((ROOT/'source/acquired/board2024-writeins-xlsx.receipt.json').read_text());b=original(r);z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip()is None
    dump(ROOT/'source/writein-workbook-members.json',[dict(member=i.filename,sha256=sha(z.read(i)),bytes=i.file_size,crc=i.CRC,source_id=r['id'])for i in z.infolist()])
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};rel={'r':'http://schemas.openxmlformats.org/package/2006/relationships'}
    strings=[''.join(si.itertext()) for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
    rels={x.attrib['Id']:x.attrib['Target'] for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};out=[];summaries=[]
    for sheet in E.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns):
        sid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'];target=rels[sid];member=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        cells={}
        for row in E.fromstring(z.read(member)).findall('.//m:row',ns):
            for c in row:
                v=c.find('m:v',ns);f=c.find('m:f',ns);t='' if v is None else v.text;value=strings[int(t)] if c.attrib.get('t')=='s' else t
                cells[c.attrib['r']]=dict(value=value,raw_v=None if v is None else v.text,formula=None if f is None else f.text,xml_type=c.attrib.get('t'))
        assert cells['D3']['value']=='U.S. Senator in Congress:'
        selected={k:v for k,v in cells.items() if k[0]in ['D','E'] and re.fullmatch(r'[DE]\d+',k)}
        rows=[]
        for rn in sorted({int(k[1:]) for k in selected}):
            rows.append(dict(row=rn,name_cell=selected.get('D'+str(rn)),count_cell=selected.get('E'+str(rn))))
        summary=int(cells['E4']['value']);footer=[x for x in rows if x['name_cell'] and clean(x['name_cell']['value']).lower()=='total']
        # Keep each literal detail row, including repeated Blank/None labels, as a separate source record.
        detail=[x for x in rows if x['row']>=6 and x['name_cell'] and x['name_cell']['value'] and clean(x['name_cell']['value']).lower()!='total' and x['count_cell'] and x['count_cell']['value']!='']
        detail_sum=sum(int(x['count_cell']['value']) for x in detail)
        summaries.append(dict(municipality=sheet.attrib['name'],printed_top_total=summary,detail_sum=detail_sum,difference=detail_sum-summary,footer_rows=footer))
        out.append(dict(source_id=r['id'],source_raw_sha256=r['raw_sha256'],member=member,sheet=sheet.attrib['name'],header_cells={k:cells[k] for k in ['A1','D3','E3','E4'] if k in cells},rows=rows,legal_eligibility=None,methods=None,native_precinct_ids=None,join_to_generic='source-scoped comparison only; no detail added to generic totals'))
    dump(ROOT/'extracts/2024-senate-writein-cells.json',out);dump(ROOT/'extracts/writein-scope-comparison.json',summaries)
    print('2024 write-in municipal printed totals',sum(x['printed_top_total'] for x in summaries),'detail',sum(x['detail_sum'] for x in summaries),'disagreements',[(x['municipality'],x['difference']) for x in summaries if x['difference']])
    for year in ['2022','2020']:
        r=json.loads((ROOT/f'source/acquired/board{year}-writeins-pdf.receipt.json').read_text());b=original(r)
        text=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True).stdout
        gzwrite(ROOT/f'source/board-{year}-writeins.layout.txt.gz',text);print(year,'text bytes',len(text),'sample',text[:400])
if __name__=='__main__':run()
