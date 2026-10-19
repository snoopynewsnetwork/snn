"""Amite: independently read complete original pages; mixed scan orientation repaired."""
from record_native_review import record
from own_page_geometry import geometry,evidence

def main():
 gg={p:geometry('amite',p,619,1870,[224,452],{'Ty Pinkins':(1160,1222),'Roger F. Wicker':(1222,1278)},rotation_override=90,candidate_header_grid=True) for p in [2,3,4]}
 record('amite',[(2,['Amite River','Ariel','Berwick','Crosby Public Library','East Centreville','East Fork','East Gloster','East Liberty','Gloster','Homochitto','Liberty'],[158,205,172,72,118,39,100,56,362,7,109],[57,92,70,73,256,321,137,117,119,58,416],None),(3,['New Zion','Oneil','Riceville','Smithdale','South Liberty','Street','Tangipahoa','Tickfaw','Vance Park','Walls','Zion Hill'],[42,12,125,120,122,51,61,141,21,138,63],[286,258,177,279,132,248,415,166,140,406,291],None),(4,['TOTAL']+['']*10,[2294]+[None]*10,[4514]+[None]*10,1)],page_overrides=gg);evidence('amite',[2,3,4])
if __name__=='__main__':main()
