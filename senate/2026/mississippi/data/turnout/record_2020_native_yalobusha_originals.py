"""Separate complete-original 2020 Yalobusha and amended Senate readings."""
from record_2020_native_manual_original import build,NAMES

def page(a,b,c): return dict(zip(NAMES,(a,b,c)))

ORIGINAL={
    2:page([436,160,777,273,62,43,386,438,35,8,274],
           [569,220,371,377,122,155,78,394,42,56,633],
           [13,7,6,12,0,5,3,10,1,1,18]),
    3:page([113,3005,None,None,None,None,None,None,None,None,None],
           [398,3415,None,None,None,None,None,None,None,None,None],
           [12,88,None,None,None,None,None,None,None,None,None]),
}
AMENDED={
    2:page([436,160,777,273,62,43,386,438,35,8,274],
           [569,220,371,377,122,155,78,394,42,56,633],
           [13,7,6,12,0,5,3,10,1,1,18]),
    3:page([113,3005,None,None,None,None,None,None,None,None,None],
           [398,3415,None,None,None,None,None,None,None,None,None],
           [12,88,None,None,None,None,None,None,None,None,None]),
}
ORIGINAL_LABELS={
    2:['Beat One North','Beat One South','Beat Two Water Valley','Five Coffeeville','Five Scobey','Five Tillatoba','Four Coffeeville','Four Oakland',"Scuna - Vann's Mill North","Scuna - Vann's Mill South",'Three North West'],
    3:['Three Sylva Rena','TOTAL','','','','','','','','',''],
}
AMENDED_LABELS={
    2:['Beat One North','Beat One South','Beat Two Water Valley','Five Coffeeville','Five Scobey','Five Tillatoba','Four Coffeeville','Four Oakland',"Scuna - Vann's Mill North","Scuna - Vann's Mill South",'Three North West'],
    3:['Three Sylva Rena','TOTAL','','','','','','','','',''],
}

def main():
    build('yalobusha','yalobusha-original',ORIGINAL,ORIGINAL_LABELS,12,hint_version='v4')
    build('yalobusha-amended','yalobusha-amended',AMENDED,AMENDED_LABELS,12,hint_version='v4')
if __name__=='__main__': main()
