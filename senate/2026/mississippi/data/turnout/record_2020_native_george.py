"""Direct all-three Senate candidate grids from George 2020 original pages2–4."""
from record_2020_native_manual_original import build,NAMES
def page(a,b,c):return dict(zip(NAMES,(a,b,c)))
def main():
    build('george','george',{
      2:page([156,48,33,52,37,60,104,36,26,41,223],
             [1115,216,288,290,189,407,745,368,347,157,813],
             [29,8,2,3,7,13,22,12,13,2,17]),
      3:page([44,121,135,89,126,21,234,39,141,15,63],
             [310,651,606,616,304,84,277,190,436,168,234],
             [12,15,18,25,12,0,15,8,12,6,9]),
      4:page([1844]+[None]*10,[8811]+[None]*10,[260]+[None]*10)
    },{
      2:['Rocky Creek','Multi Mart','Ward','Shipman','Courthouse','Pine Level','Agricola','Howell','Movella','Multi-Purpose','Basin'],
      3:['Davis','Barton','City Hall','Shady Grove','Bexley','Salem','Middle School','Central','Benndale','Broome','Twin Creek'],
      4:['TOTAL']+['']*10
    },22,hint_version='v3')
if __name__=='__main__':main()
