"""Acquire only linked historical/native/context sources, with complete originals."""
from acquire_sources import *
def main():
    for key,parent in [('2018','sos-2018-general-county-index'),('2018-runoff','sos-2018-runoff-county-index')]:
        r=next(x for x in receipts if x['id']==parent);inv=[]
        for label,url in links(source(parent),r['final_url']):
            if '.pdf' not in url.lower():continue
            sid='sos-'+key+'-county-'+re.sub('[^a-z0-9]+','-',label.lower()).strip('-')
            inv.append(dict(literal=label,url=url,source_id=sid));source(sid,url,parent)
        savejson(OUT/'source'/('county-links-'+key+'.json'),inv)
    for key,url,parent in [
      ('eac-2022-csv-parent','https://www.eac.gov/media/258536','eac-studies'),
      ('eac-2022-codebook-parent','https://www.eac.gov/media/256316','eac-studies'),
      ('sos-yallvote','https://www.sos.ms.gov/yall-vote','sos-elections-current'),
      ('sos-2022-voter-guide','https://www.sos.ms.gov/content/documents/elections/yallvotedocs/Mississippi%20Voter%20Information%20Guide%202022.pdf','sos-results')]:source(key,url,parent)
    for parent,filterfn,prefix in [
      ('eac-2022-csv-parent',lambda x,y:'.zip' in y,'eac-2022-csv'),
      ('eac-2022-codebook-parent',lambda x,y:'.xlsx' in y,'eac-2022-codebook'),
      ('eac-studies',lambda x,y:'2024_EAVS_for_Public_Release_nolabel_V2_csv.zip' in y,'eac-2024-csv'),
      ('eac-studies',lambda x,y:'2024_EAVS_Codebook.xlsx' in y,'eac-2024-codebook'),
      ('sos-yallvote',lambda x,y:x in ['Election Code','2026 Elections Calendar','County Election Handbook'],'sos-authority'),
      ('sos-active-voter-count-index',lambda x,y:x in ['November 2024 Voter Count','November 2022 Voter Count','September 2026 Voter Count'],'sos-registration')]:
        r=next(x for x in receipts if x['id']==parent)
        for label,url in links(source(parent),r['final_url']):
            if filterfn(label,url):source(prefix+'-'+re.sub('[^a-z0-9]+','-',label.lower()).strip('-'),url,parent)

if __name__=='__main__':main()
