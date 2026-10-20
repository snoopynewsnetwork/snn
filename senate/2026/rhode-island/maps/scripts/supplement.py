from acquire import *
import concurrent.futures
JOBS=[
 ('cranston-map-directory','https://www.cranstonri.gov/departments/canvassing-department/voting-districts-and-district-maps/default.aspx','search:official-map-directory'),
 ('cranston-current-roster','https://www.cranstonri.gov/nov-3-2026-general-election-warrant-and-polling-places/','municipal-cranston'),
 ('woonsocket-map-directory','https://www.woonsocketri.gov/593/Voting-District-Map','search:official-map-directory'),
 ('warwick-gis-directory','https://www.warwickri.gov/615/GIS-Maps-Graphs','search:official-map-directory'),
 ('johnston-canvassers','https://www.johnstonri.gov/1196/Board-of-Canvassers','deepen-johnston-00'),
 ('pawtucket-canvassers','https://pawtucketri.gov/board-of-canvassers/','deepen-pawtucket-00'),
 ('little_compton-clerk','https://www.littlecomptonri.org/departments/town_clerk/index.php','municipal-little_compton'),
 ('north_providence-canvassers','https://northprovidenceri.gov/town-clerk/board-of-canvassers/','deepen-north_providence-00'),
 ('statute-voting-districts','https://webserver.rilegislature.gov/Statutes/TITLE17/17-11/17-11-1.htm','rigis-layer-pre:explicit-statute-citation'),
]
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(lambda x:fetch(*x),JOBS):print(r['id'],last(r).get('status'),last(r).get('raw_bytes'),flush=True)
if __name__=='__main__':main()
