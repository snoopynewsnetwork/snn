"""Independent original-header visual readings for the final24-source replay."""
import json
from sources import OUT,save
LABELS=['Bywy','Southwest Ackerman']+['']*9+['County Precinct 1-B','County Precinct 3-A','County Precinct 3-B','County Precinct 4-B','County Precinct 5-A','','4th District West\nTylertown','Darbun','Dexter']
LABELS+=['Dinan','Lexie','Mesa','North Knoxo','Varnel','TOTAL','','Lone Star / Black\nJack','Richmond','Rock Hill','South Collins','Station Creek','Bassfield 26','Bassfield Highway\n42- 31','Good Hope/Melba 33','Gwinville/Old\nHebron- 51','East Starkville','Hickory Grove','Needmore','North Starkville\nDistrict 3']
LABELS+=['Oktibbeha Co Storm\nShelter','Oktoc','TOTAL','','Courthouse','Fort Stephens','Courthouse','Preston','Scooba A-L']+['']*6+['Tunica','Tunica Auditorium','Tunica Economic\nComplex','','']
LABELS+=['','','','East Quitman','North Quitman','Oakgrove','Pachuta','Shubuta','Snell','Souinlovie','Beaumont District 1\n1030','Beaumont Voting\nPrecinct 5120','Richton Holly Street\n3060','Richton Multi Purpose\n4080']+['']*5+['Coopers Creek (A-Z)']
LABELS+=['Jayess','New Hebron','Oma','Stringer/N Pleasant\nHill','Topeka','West District 5','Gallman','Georgetown South','Hazlehurst West','Eucutta','Leland Rotary Club','Metcalfe Municipal\nBuilding','Mount Bethel Baptist\nChurch','','','Big Black','Eupora No. 1','Eupora No. 3','Grady','Tomnolen']
LABELS+=['Walthall','TOTAL','','','','Hurricane Hu','Pontotoc 5 P5','Sherman Sh','','','','Nanih Waiya','','','','','Lambert','West Lambert','Four Coffeeville','Three North West']
LABELS+=['Benton','Center Ridge','Deasonville','East Bentonia','Eden','Free Run','Fugates','Holly Bluff','Jonestown','Lake City','Little Yazoo','Mechanicsburg','Midway','Mound St. Building','N.D. Taylor Gym','Satartia','Teen Center','Valley','Webster Street\nSchool','Welfare Office']
LABELS+=['West Bentonia','Zion','TOTAL','','','Clarksdale\nCourthouse','Coahoma','TOTAL','','','','(04) Mlk Center','(09) Magnolia Comm\nCtr.','','','','']
LABELS[17]='4th Distrct West\nTylertown'
def main():
    rows=json.loads((OUT/'replay-84views-label-comparison.json').read_text())['disagreements'];assert len(LABELS)==len(rows),(len(LABELS),len(rows))
    save(OUT/'replay-84views-header-repairs.json',dict(qualification='Literal independently visually read original headers; no typed peer label appeared on review cards. Empty source-template header remains blank, not an invented named unit.',metadata_correction_history=[dict(source_id='sos-2024-county-walthall',page=2,source_column=2,prior_manual_label='4th District West\nTylertown',accepted_source_literal='4th Distrct West\nTylertown',basis='Expanded unaltered original shows printed Distrct without the second i',evidence='qa/walthall-district-source-header.png')],readings=[{k:r[k] for k in ['source_id','page','source_column','header_bounds']}|dict(label_literal=label,evidence='qa/walthall-district-source-header.png' if i==17 else f'qa/replay-84views-original-headers-{i//20+1}.png',basis='Independent unaltered original expanded header visual reading') for i,(r,label) in enumerate(zip(rows,LABELS))]))
if __name__=='__main__':main()
