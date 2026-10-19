"""Separate direct original Washington 2020 Senate page2–3 publication reads."""
from record_2020_native_manual_original import build,NAMES
def page(a,b,c):return dict(zip(NAMES,(a,b,c)))
ORIGINAL={
 2:page([274,1475,384,27,1852,478,194,847,946,797,861],
        [170,290,741,40,66,17,249,186,9,241,428],
        [0,10,11,0,10,0,2,5,2,7,11]),
 3:page([643,411,519,1384,116,307,975,665,13155,None,None],
        [400,10,9,517,587,81,653,197,4891,None,None],
        [8,1,6,10,7,3,12,4,109,None,None]),
}
AMENDED={
 2:page([274,1475,384,27,1852,478,194,847,946,797,861],
        [170,290,741,40,66,17,249,186,9,241,428],
        [0,10,11,0,10,0,2,5,2,7,11]),
 3:page([643,411,519,1384,116,307,975,665,13155,None,None],
        [400,10,9,517,587,81,653,197,4891,None,None],
        [8,1,6,10,7,3,12,4,109,None,None]),
}
ORIGINAL_LABELS={
 2:['Arcola Technology Center','Buster Brown Community Center','Covenant Presbyterian Church','Darlove','Elks Lodge','Extension Building','Glen Allan Library','Hollandale City Hall',"Jake's Chapel MB Church",'Lake Vista Masonic Lodge','Leland Health Department'],
 3:['Leland Rotary Club','Metcalfe Municipal Building','Mount Bethel Baptist Church','St. James Episcopal Church','Swiftwater Baptist Church','Tampa Drive',"Ward's Recreation Center",'Washington County Convention Center','TOTAL','',''],
}
AMENDED_LABELS={
 2:['Arcola Technology Center','Buster Brown Community Center','Covenant Presbyterian Church','Darlove','Elks Lodge','Extension Building','Glen Allan Library','Hollandale City Hall',"Jake's Chapel MB Church",'Lake Vista Masonic Lodge','Leland Health Department'],
 3:['Leland Rotary Club','Metcalfe Municipal Building','Mount Bethel Baptist Church','St. James Episcopal Church','Swiftwater Baptist Church','Tampa Drive',"Ward's Recreation Center",'Washington County Convention Center','TOTAL','',''],
}
def main():
    build('washington','washington-original',ORIGINAL,ORIGINAL_LABELS,19,hint_version='v4')
    build('washington-amended','washington-amended',AMENDED,AMENDED_LABELS,19,hint_version='v4')
if __name__=='__main__':main()
