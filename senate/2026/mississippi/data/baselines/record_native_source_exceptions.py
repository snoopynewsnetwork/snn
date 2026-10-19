"""Complete original page readings of Tunica/Kemper, preserving source scopes.

All eleven candidate vectors below were independently read from complete
unaltered original pages. Kemper's unofficial page remains non-additive.
"""
from collections import Counter
from PIL import Image
from sources import OUT,BASE,original,sha,save
NAMES=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski','Ty Pinkins','Roger F. Wicker']
T7=[[36,233,207,6,219,166,130,232,123,173,200],[0,0,0,0,0,0,0,1,0,1,0],[0,0,0,0,0,0,0,0,0,1,0],[0,1,0,0,0,1,0,0,0,0,0],[33,95,8,61,46,30,265,33,105,31,49],[0,0,0,0,0,0,0,0,0,0,1],[0,0,1,0,0,0,0,1,0,0,1],[0,5,1,0,2,1,1,0,5,4,0],[0,0,0,0,0,1,0,0,0,0,0],[30,226,202,7,225,168,129,212,126,169,195],[38,95,10,60,47,27,265,44,111,34,50]]
T8=[[111,1836],[1,3],[0,1],[0,2],[43,799],[0,1],[0,3],[2,21],[0,1],[108,1797],[46,827]]
K7=[[365,80,26,42,117,92,247,281,83,139,348],[0,0,0,0,0,1,1,0,0,1,0],[0,0,0,0,0,0,1,0,0,0,0],[1,0,0,0,0,0,0,0,0,0,0],[136,222,35,185,52,14,117,195,177,63,108],[0,0,0,0,0,0,0,1,0,0,0],[1,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,1],[0,0,0,0,0,0,0,1,0,0,0],[348,74,24,42,119,89,234,259,74,130,321],[153,228,36,183,57,17,126,208,182,73,123]]
K8=[[166,226,169,2381],[0,1,1,5],[0,0,0,1],[0,0,0,1],[168,113,106,1691],[1,0,0,2],[0,0,0,1],[1,0,0,3],[0,0,0,1],[164,208,148,2234],[176,134,128,1824]]
TL=['Austin Park','Dundee Community\nCenter','Hambrick','Mhoon Landing','New Sub Park','Robinsonville\nCommunity Center','Tunica','Tunica Auditorium','Tunica Economic\nComplex','Verner Park','White Oak Rec.\nCenter']
KL=['Courthouse','Damascus','Farmers Market','Fort Stephens','Kellis Store','Kemper Springs','Library','Little Rock Comm Ctr','Lynville','Mount Nebo','Porterville']
def page(key,n,labels,values,parallel=False,unused=0):
    p=OUT/'qa'/f'{key}-full-original-p{n}.png';assert len(values)==11 and all(len(v)==len(labels) for v in values)
    return dict(page=n,full_original_render_path=str(p.relative_to(BASE)),render_sha256=sha(p.read_bytes()),render_size=list(Image.open(p).size),labels_literal=labels,roles=['parallel_native_observation' if parallel else 'source_TOTAL' if l=='TOTAL' else 'source_native_reporting_constituent' for l in labels]+['unused_template_column']*unused,fields=[dict(candidate=name,printed_row_index=i+1,values=v+[None]*unused) for i,(name,v) in enumerate(zip(NAMES,values))],unused_blank_columns=unused,position_scope='Physical source columns in displayed left-to-right order; complete original page preserves exact printed rules/labels/parties. Source-specific coordinate ledger separately retains accepted Senate bounds; no cross-year join.')
def main():
    sources=[]
    for county in ['tunica','kemper']:
        key='sos-2024-county-'+county
        pages=[page(key,7,TL,T7),page(key,8,['Workforce Center','TOTAL'],T8,unused=9)] if county=='tunica' else [page(key,6,KL,K7,parallel=True),page(key,7,KL,K7),page(key,8,['Preston','Scooba A-L','Scooba M-Z','TOTAL'],K8,unused=7)]
        sums=Counter();totals={}
        for p in pages:
            for f in p['fields']:
                for role,v in zip(p['roles'],f['values']):
                    if role=='source_native_reporting_constituent':sums[f['candidate']]+=v
                    elif role=='source_TOTAL':totals[f['candidate']]=v
        assert dict(sums)==totals
        sources.append(dict(source_id=key,raw_sha256=sha(original(key)),pages=pages,native_sums=dict(sums),printed_TOTAL=totals))
    summary=OUT/'qa/sos-2024-county-tunica-full-original-p3.png'
    save(OUT/'native-source-exception-readings.json',dict(qualification='Two complete source-native eleven-candidate original readings, plus all eleven repeated unofficial Kemper vectors retained non-additively. Tunica discrepancy is source-scoped, not allocated or normalized.',sources=sources,tunica_summary=dict(page=3,full_original_render_path=str(summary.relative_to(BASE)),render_sha256=sha(summary.read_bytes()),status_literal='Official Results',report_clock_literal='Election Summary - 11/15/2024 3:18 PM',timezone=None,summary_named_candidates={**dict(zip(NAMES[:9],[1837,3,1,2,799,1,3,21,1])),'Ty Pinkins':1798,'Roger F. Wicker':827},Senate_generic_write_in_totals=3,Senate_total_votes_cast=2628,Senate_contest_totals=2745,President_generic_write_in_totals=4,President_total_votes_cast=2672,President_contest_totals=2745,SEMS_minus_summary={'Kamala D. Harris':-1,'Ty Pinkins':-1},qualification='Exact primary source differences. Generic marks remain separate from named/certified write-ins. No native residual unit or county/state denominator mutation.'),kemper_publication_status=dict(PDF6='UnOfficial Recapitulation; printed Page:1',PDF7='Official Recapitulation; printed Page:2',PDF8='Official Recapitulation; printed Page:3',eleven_PDF6_observations_nonadditive=True,no_chronology_inferred=True)))
    print('Two additional all11 native views:26disjoint native constituents;11nonadditive parallel observations;all22 vectors close printedTOTAL;Tunica2named source differences explicit')
if __name__=='__main__':main()
