import hashlib,json,subprocess,tempfile,gzip
from pathlib import Path
from html_tools import ROOT,receipts,entity

def extract():
    out=ROOT/'pdf';out.mkdir(exist_ok=True);index=[]
    version=subprocess.run(['pdftotext','-v'],capture_output=True)
    (out/'runtime.json').write_text(json.dumps({'command':['pdftotext','-v'],'exit':version.returncode,
        'stdout':version.stdout.decode(),'stderr':version.stderr.decode()},indent=2)+'\n')
    seen=set()
    for receipt,r in receipts():
        if not r['hops'] or r['hops'][-1]['status']!=200:continue
        _,b=entity(receipt)
        if not b.startswith(b'%PDF'):continue
        h=hashlib.sha256(b).hexdigest()
        if h in seen:continue
        seen.add(h)
        with tempfile.TemporaryDirectory(prefix='al-official-pdf-') as tmp:
            p=Path(tmp)/'original.pdf';p.write_bytes(b)
            run=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True)
            (out/(h+'.txt.gz')).write_bytes(gzip.compress(run.stdout,mtime=0))
            (out/(h+'.stderr.txt')).write_bytes(run.stderr)
            info=subprocess.run(['pdfinfo',str(p)],capture_output=True)
            (out/(h+'.info.txt')).write_bytes(info.stdout)
            (out/(h+'.info.stderr.txt')).write_bytes(info.stderr)
            index.append({'receipt':receipt,'url':r['requested_url'],'original_bytes':len(b),'original_sha256':h,
                'command':['pdftotext','-layout','ORIGINAL.pdf','-'],'exit':run.returncode,
                'text':'pdf/'+h+'.txt.gz','text_bytes':len(run.stdout),'text_sha256':hashlib.sha256(run.stdout).hexdigest(),
                'stderr':'pdf/'+h+'.stderr.txt','text_only_formfeeds_or_whitespace':not run.stdout.strip(),
                'pdfinfo_exit':info.returncode})
    (ROOT/'pdf-index.json').write_text(json.dumps(index,indent=2)+'\n')
    print('complete PDFs',len(index),'no embedded text',sum(x['text_only_formfeeds_or_whitespace'] for x in index))
if __name__=='__main__':extract()
