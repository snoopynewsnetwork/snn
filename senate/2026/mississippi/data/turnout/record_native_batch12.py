"""Independent source-native Senate labels/counts, with separate printed IDs."""
from record_native_review import record
from own_page_geometry import geometry,evidence

def main():
 record('walthall',[(2,['3rd District Tylertown','4th Distrct West\nTylertown','4th District Tylertown','Darbun','Dexter','Dinan','East Tylertown','Enon','Hope','Improve','Lexie'],[107,69,24,15,100,439,6,25,168,79,87],[292,345,281,90,420,220,50,176,34,314,498],None),(3,['Mesa','Midway','North Kirklin','North Knoxo','Sartinsville','South Kirklin','St Paul','Varnel','West Tylertown','TOTAL',''],[13,43,216,445,57,33,126,101,166,2319,None],[45,193,190,94,134,135,72,391,184,4158,None],10)],physical_pages=[2,3])
 record('covington',[(2,['Collins','Dry Creek','Gilmer / Yawn','Lone Star / Black\nJack','Mitchell','Mt Olive','Okahay','Richmond','Rock Hill','Sanford','Seminary/West\nCollins'],[590,248,376,65,8,485,406,61,11,70,200],[813,96,269,192,182,483,106,746,109,723,1504],None),(3,['South Collins','Station Creek','Strahan','Williamsburg','TOTAL']+['']*6,[48,244,29,38,2879]+[None]*6,[267,126,84,224,5924]+[None]*6,5)])
 gg={3:geometry('jeff-davis',3,630,1909,[224,442],{'Ty Pinkins':(1162,1224),'Roger F. Wicker':(1224,1278)},rotation_override=0,candidate_header_grid=True)}
 record('jeff-davis',[(2,['11-Granby','Bassfield 26','Bassfield Highway\n42- 31','Carson 22','Clem 41','Good Hope/Melba 33',"Green'S Creek 23",'Gwinville/Old\nHebron- 51','Mt Carmel 42','North East Prentiss\n43','North West Prentiss\n53'],[55,144,596,48,76,90,71,133,153,338,149],[59,169,217,139,79,196,190,90,24,186,60],None),(3,['Red House 55',"Son's\nAcademy/Hathorn 25",'South Prentiss 12','South Prentiss 13','Whiting 56','Williamson Mill 44','TOTAL']+['']*4,[220,183,223,206,201,84,2970]+[None]*4,[97,200,264,165,65,183,2383]+[None]*4,7)],page_overrides=gg);evidence('jeff-davis',[3])
if __name__=='__main__':main()
