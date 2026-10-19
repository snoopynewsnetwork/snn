"""Independent source-specific Simpson / Marshall native readings."""
from record_native_review import record

def main():
 record('simpson',[(2,['Bowie','Braxton','Bridgeport',"D'Lo",'Dry Creek','Fork Church','Harrisville','Jupiter','Magee 1','Magee 2','Magee 4'],[85,41,193,20,63,183,77,337,417,176,217],[190,489,130,245,552,100,548,258,160,764,986],None),(3,['Mendenhall 1','Mendenhall 3','Merit','New Hope','Oak Grove','Pearl','Pinola','Saratoga','Shivers','Sumrall','Weathersby'],[119,140,53,98,233,76,98,124,138,69,432],[80,705,513,138,301,366,228,139,197,344,123],None),(4,['TOTAL']+['']*10,[3389]+[None]*10,[7556]+[None]*10,1)],physical_pages=[2,3,4])
 record('marshall',[(2,['1 North Holly Springs','1 Red Banks','1 West Holly Springs','2 Cayce','2 Early Grove','2 Hudsonville','2 Mt Pleasant','2 North Holly Springs','2 Slayden','3 Barton','3 Byhalia'],[516,343,701,207,105,175,275,388,194,161,509],[71,522,198,301,136,179,799,210,377,727,1013],None),(3,['3 Cayce','4 Chulahoma','4 Laws Hill','4 Marianna','4 Victoria','4 Wall Hill','4 Warsaw','4 Watson','5 Bethlehem','5 Cornersville','5 Potts Camp'],[238,298,79,229,178,311,245,159,37,8,228],[290,114,121,264,155,230,322,255,283,133,474],None),(4,['5 South Holly Springs','5 Waterford','TOTAL']+['']*8,[839,211,6634]+[None]*8,[618,308,8100]+[None]*8,3)],physical_pages=[3])
if __name__=='__main__':main()
