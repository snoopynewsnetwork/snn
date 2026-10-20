import collections,gzip,io,json,re,subprocess,xml.etree.ElementTree as ET,zipfile
from common import *
def main():
    native=read_gz('extracts/native-baselines.jsonl.gz');lookup={r['source_unit_key']:r for r in native if r['observed']};out=[]
    settings=json.loads((BASE/'scenario-settings.json').read_text())
    for setting in settings:
        name=setting['id']
        for goal in ['tie','Aplus1']:
            r=json.loads((BASE/f'scenarios/{name}-{goal}.result.json').read_text());ps=collections.defaultdict(list)
            for u in r['units']:ps[lookup[u['key']]['parent_key']].append(u)
            for p,rows in ps.items():
                t=sum(u['pair_volume'] for u in rows);f=sum(u['all_volume'] for u in rows)
                base=sum(u['baseline_net_votes'] for u in rows);net=sum(u['target_net_votes'] for u in rows)
                out.append({'scenario':name,'target':goal,'parent_key':p,'native_children':len(rows),
                    'pair_volume':t,'all_volume':f,'pair_participation':t/f if f else None,'pair_weight':t/r['pair_denominator'],
                    'all_candidate_weight':f/r['all_candidate_denominator'],'baseline_net_votes':base,'target_net_votes':net,'net_vote_gain':net-base,
                    'target_A_share':(net/t+1)/2 if t else None,'target_pair_margin':net/t if t else None,
                    'target_all_candidate_margin':net/f if f else None,'nominal_plus1_share_point_net_votes':.02*t,
                    'bounded_plus1_baseline_share_point_net_votes':sum(2*u['pair_volume']*(min(1,u['baseline_a_share']+.01)-u['baseline_a_share']) for u in rows if u['baseline_a_share'] is not None),
                    'clipped_native_children':sum(u['clipped'] for u in rows)})
    write_csv('parent-contributions.csv',out)
    # Source chain evidence is parsed from original bodies, with literal requested link byte positions.
    chains=[]
    for ident,r in inputs().items():
        b=body(ident)
        if not b.lstrip().startswith(b'<!DOCTYPE') and not b.lstrip().startswith(b'<html'):continue
        s=b.decode('utf8',errors='replace');links=[]
        for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',s,re.S|re.I):
            if any(x in m[1].lower() for x in ['general_election','data_description','write','summary','rigen','elections.ri.gov']):
                links.append({'href_literal':m[1],'label_literal':re.sub('<[^>]+>','',m[2]).strip(),
                              'byte_start':len(s[:m.start()].encode()),'byte_end':len(s[:m.end()].encode())})
        clocks=re.findall(r'(?:updated_at">|Last updated:\s*</?[^>]*>)([^<]+)',s)
        chains.append({'input':ident,'url':r['url'],'raw_sha256':r['raw_sha256'],'status':r['status'],'retrieved_at_utc':r['retrieved_at_utc'],
            'published_clock_literals':clocks,'timezone_asserted':None,'links':links})
    write_json('source/chains.json',chains)
    # New public-source observations are fixed individually, never read through a directory glob on reproduction.
    ids=['authority-network-initial','authority-current','current-candidate-search','current-candidate-search-alt',
         'publications-current','declared-candidates-xlsx','writein-guide','general-candidate-summary','federal-plurality']
    receipts=[json.loads((BASE/f'source/acquired/{i}.receipt.json').read_text()) for i in ids]
    write_json('source/current-inputs.json',receipts)
    decl=next(x for x in receipts if x['id']=='declared-candidates-xlsx');b=gzip.decompress((BASE/decl['stored_path']).read_bytes())
    z=zipfile.ZipFile(io.BytesIO(b));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    strings=[''.join(t.text or '' for t in x.iter('{'+ns['m']+'}t')) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    rows=[]
    for member in z.namelist():
        if not re.fullmatch('xl/worksheets/sheet[0-9]+.xml',member):continue
        for row in ET.fromstring(z.read(member)).findall('.//m:row',ns):
            values={}
            for c in row:
                v=c.find('m:v',ns);v=v.text if v is not None else None
                if c.get('t')=='s' and v is not None:v=strings[int(v)]
                values[re.sub(r'\d','',c.get('r'))]=v
            if values.get('T')=='SENATOR IN CONGRESS':
                # Do not copy voter IDs, contact or residential fields into the derivative.
                kept={k:values.get(k) for k in ['A','B','C','D','F','S','T','U','V','W','Z','AA','AB','AC','AD','AE','AF']}
                rows.append({'member':member,'row':int(row.get('r')),'fields':kept})
    write_json('extracts/declared-candidate-scope.json',{'source':decl['requested_url'],'raw_sha256':decl['raw_sha256'],'selected_rows':rows,
        'final_current_ballot_mapping':None,'status':'Declared workbook includes primary records; general-election summary HTTP403. No primary nominee or old ID is promoted into a final current candidate mapping.',
        'live_candidate_ids':None,'closed_writein_universe':None})
    guide=next(x for x in receipts if x['id']=='writein-guide');raw=gzip.decompress((BASE/guide['stored_path']).read_bytes())
    text=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout
    (BASE/'witness/writein-guide.layout.txt.gz').write_bytes(gzip.compress(text,mtime=0))
    print('Parent contributions',len(out),'source chain bodies',len(chains),'new source receipts',len(receipts))
if __name__=='__main__':main()
