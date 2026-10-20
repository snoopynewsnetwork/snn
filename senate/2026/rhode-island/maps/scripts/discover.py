from acquire import *
import concurrent.futures,re,html
# Literal URLs exposed in the Secretary's LocalBoards page by web reader on 2026-10-20;
# direct entity returned 403. No body reconstruction is claimed for that reader view.
HOMES={
'barrington':'https://www.barrington.ri.gov/','bristol':'https://www.bristolri.gov/','burrillville':'https://www.burrillville.org/','central_falls':'https://www.centralfallsri.gov/','charlestown':'https://charlestownri.gov/','coventry':'https://coventryri.gov/','cranston':'https://www.cranstonri.gov/','cumberland':'https://www.cumberlandri.org/','east_greenwich':'https://www.eastgreenwichri.com/','east_providence':'https://eastprovidenceri.gov/','exeter':'https://www.exeterri.gov/','foster':'https://www.townoffoster.com/','glocester':'https://www.glocesterri.org/','hopkinton':'https://www.hopkintonri.org/','jamestown':'https://www.jamestownri.gov/','johnston':'https://townofjohnstonri.com/','lincoln':'https://www.lincolnri.gov/','little_compton':'https://www.littlecomptonri.org/','middletown':'https://www.middletownri.com/','narragansett':'https://www.narragansettri.gov/','newport':'https://www.cityofnewport.com/','new_shoreham':'https://www.newshorehamri.gov/','north_kingstown':'https://www.northkingstownri.gov/','north_providence':'https://northprovidenceri.gov/','north_smithfield':'https://www.nsmithfieldri.org/','pawtucket':'https://pawtucketri.com/','portsmouth':'https://www.portsmouthri.gov/','providence':'https://www.providenceri.gov/','richmond':'https://www.richmondri.com/','scituate':'https://www.scituateri.gov/','smithfield':'https://www.smithfieldri.gov/','south_kingstown':'https://www.southkingstownri.com/','tiverton':'https://www.tiverton.ri.gov/','warren':'https://www.townofwarren-ri.gov/','warwick':'https://www.warwickri.gov/','west_greenwich':'https://www.wgtownri.org/','west_warwick':'https://www.westwarwickri.org/','westerly':'https://westerlyri.gov/','woonsocket':'https://www.woonsocketri.gov/'}
def main():
 a=parsed(S/AUTHORITY);order=[x.split(':')[-1] for x in a['ordered_priority_parent_keys']]
 assert len(order)==37 and set(order)<=set(HOMES)
 dump(M/'source/directory-observation.json',dict(url='https://vote.sos.ri.gov/Elections/LocalBoards',transport='web reader exposed published hyperlinks; direct complete entity 403 is retained as sos-municipal-directory',observed_utc='2026-10-20',literal_municipal_links=HOMES,priority_order=order))
 jobs=[('municipal-'+k,HOMES[k],'sos-municipal-directory:web-reader') for k in order]
 jobs += [('rigis-precinct-page','https://www.rigis.org/datasets/edc::voting-precincts-2022/about','sos-maps-hub'),('board-directory','https://elections.ri.gov/canvassers/index.php',None)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(lambda args:fetch(*args),jobs):print(r['id'],last(r).get('status'),last(r).get('raw_bytes'),flush=True)
if __name__=='__main__':main()
