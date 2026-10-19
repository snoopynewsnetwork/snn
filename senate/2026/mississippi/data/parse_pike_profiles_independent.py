"""Strict parsing of saved independent original OCR; no zero substitution."""
from pathlib import Path
import gzip
import json
import re

DATA=Path(__file__).resolve().parent
DEST=DATA/'coordinator-qa/pike-profile-review'
NAMES={'Kamala D. Harris':'harris','Chase Oliver':'chase','Jill Stein':'stein',
       'Randall Terry':'randall','Donald J. Trump':'trump','Shiva Ayyadurai':'shiva',
       'Claudia De la Cruz':'claudia','Robert F. Kennedy Jr.':'kennedy','Peter Sonski':'sonsk',
       'Ty Pinkins':'pinkins','Roger F. Wicker':'wicker'}

def parse_line(line, percent=False, has_percent=False):
    if line is None:return {'raw_line':None,'token':None,'value':None}
    if percent:
        m=re.search(r'(\d+\.\d+)%\s*$',line)
        return {'raw_line':line,'token':m[1] if m else None,'value':float(m[1]) if m else None}
    tail=line
    if has_percent:
        m=re.search(r'\d+[.,]\d+%',line)
        tail=line[:m.start()] if m else ''
    token=tail.split()[-1] if tail.split() else None
    value=int(token.replace(',','')) if token and re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)',token) else None
    return {'raw_line':line,'token':token,'value':value}

def main():
    original=json.loads(gzip.decompress((DEST/'independent-original-ocr.json.gz').read_bytes()))
    out=[]
    for p in original['pages']:
        lines=p['text'].splitlines()
        pi=next(i for i,l in enumerate(lines) if 'President United States' in l)
        si=next(i for i,l in enumerate(lines) if 'Senate United States' in l)
        ei=next(i for i,l in enumerate(lines) if i>si and 'Congressional' in l)
        before,pres,sen=lines[:pi],lines[pi:si],lines[si:ei]
        fields={}
        def single(section,pattern):
            hits=[l for l in section if re.search(pattern,l,re.I)]
            return hits[0] if len(hits)==1 else None
        for name,alias in NAMES.items():
            fields[name]=parse_line(single(sen if name in ['Ty Pinkins','Roger F. Wicker'] else pres,alias),has_percent=True)
        for prefix,section in [('president',pres),('senate',sen)]:
            for name,pattern,pct in [('generic_write_in',r'(?:wr?ite|white)[- ]?in\s+tot',True),
                                     ('total_votes_cast',r'total votes cast',True),('contest_total',r'contest tot',False)]:
                fields[prefix+'_'+name]=parse_line(single(section,pattern),has_percent=pct)
        for name,pattern in [('registration_total','registered voters'),('ballots_cast_total',r'ballots cast\s*-\s*total'),
                             ('ballots_blank',r'ballots cast\s*-\s*blank')]:
            fields[name]=parse_line(single(before,pattern))
        fields['voter_turnout_percent']=parse_line(single(before,r'voter (turnout|tumout)'),percent=True)
        label=next((l for l in before if re.match(r'^\(\d\d\)',l)),None)
        out.append({'source_page':p['source_page'],'literal_label_OCR':label,'fields':fields})
    (DEST/'independent-parsed-fields.json').write_text(json.dumps(out,indent=2)+'\n')
    peer=json.loads(gzip.decompress((DEST/'turnout-ledger-snapshot.json.gz').read_bytes()))
    comparison=[]
    for p,q in zip(out,peer['profiles']):
        assert p['source_page']==q['source_page']
        for field,item in p['fields'].items():
            if item['value']!=q['fields'][field]['value']:
                comparison.append({'page':p['source_page'],'field':field,**item,'worker_value':q['fields'][field]['value']})
    (DEST/'initial-OCR-comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
    print(json.dumps({'pages':len(out),'fields':sum(len(p['fields']) for p in out),'strict_differences_or_missing':comparison},indent=2))

if __name__=='__main__':main()
