"""Reproduce the three selected PDF previews, without claiming visual review."""
import gzip,subprocess,tempfile
from freeze import R
def main():
    (R/'previews').mkdir(exist_ok=True)
    for sid,page in [('calendar',9),('brochure',2),('recent-absentee-opinion',20)]:
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            f.write(gzip.decompress((R/f'raw/{sid}.body.gz').read_bytes()));f.flush()
            subprocess.run(['pdftoppm','-f',str(page),'-singlefile','-scale-to','1400','-png',f.name,str(R/'previews'/f'{sid}-p{page}')],check=True)
    print('Rendered three selected pages; actual inspection separately recorded')
if __name__=='__main__':main()
