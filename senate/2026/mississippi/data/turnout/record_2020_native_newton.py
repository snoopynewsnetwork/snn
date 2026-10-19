"""Direct three-candidate native reading from the complete Newton 2020 original."""
from record_2020_native_manual_original import build,NAMES

def page(a,b,c): return dict(zip(NAMES,(a,b,c)))

def main():
    build('newton','newton',{
      2:page([43,161,214,101,142,58,361,370,50,715,455],
             [390,288,393,397,475,494,853,600,681,57,511],
             [11,13,7,12,7,14,17,19,17,4,24]),
      3:page([245,28,200,72,75,3290]+[None]*5,
             [279,370,126,448,297,6659]+[None]*5,
             [2,9,3,10,7,176]+[None]*5)
    },{
      2:['Chunky','Conehatta','Decatur #1','Decatur #2','Decatur #3/Scanlan','Duffee','Hickory','Lawrence','Little Rock','Newton #1','Newton #4'],
      3:['Newton #5','Prospect','Union #1','Union #2','Union #3','TOTAL']+['']*5
    },16,hint_version='v3')

if __name__=='__main__':main()
