from common import *
from acquire import fetch
import concurrent.futures

def main():
 listing=fetch('census-vtd-directory','https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/','primary-official-search','https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/',discovery='Official Census directory returned by web search, not filename/ID enumeration')
 for fips in ['10001','10003','10005']:
  matches=[l for l in listing.get('literal_links',[]) if l['literal']==f'tl_2020_{fips}_vtd20.zip'];assert len(matches)==1
  l=matches[0];fetch('census-vtd-'+fips,l['url'],listing['id'],l['literal'],qualification='2020 Census county-based full-resolution VTD; no cross-vintage or current ED identity approved')
 fetch('census-techdoc','https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020pl/TGRSHP2020PL_TechDoc.pdf','primary-official-search','https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020pl/TGRSHP2020PL_TechDoc.pdf')
 for ch in ['c019','c041']:
  url=f'https://delcode.delaware.gov/title15/{ch}/index.html';fetch('law-title15-'+ch,url,'primary-official-search',url,qualification='Current retrieved legal companion; not same-vintage signed boundary instrument')
 home=read(M/'source/maps-home-network.receipt.json')
 l=next(l for l in home['literal_links'] if '/maps/wilm/'in l['url']);r=fetch('wilmington-parent',l['url'],home['id'],l['literal'])
 pdfs={l['url']:l for l in r.get('literal_links',[]) if l['url'].lower().endswith('.pdf') and '/wilm/' in l['url']}
 for j,l in enumerate(pdfs.values()):fetch(f'wilmington-pdf-{j:02}',l['url'],r['id'],l['literal'],qualification='Municipal council geography, shared context only; no ED or poll-site equivalence')
if __name__=='__main__':main()
