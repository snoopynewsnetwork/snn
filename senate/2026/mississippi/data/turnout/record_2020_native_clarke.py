"""Complete Clarke 2020 three-candidate Senate native grid, original pages2–4."""
from record_2020_native_manual_original import build
E='Mike Espy';H='Cindy Hyde-Smith';J='Jimmy L. Edwards'
LABELS={
 2:['Beaverdam','Carmichael','Desoto','East Quitman','Energy','Enterprise','HOPEWELL','Harmony Dist. 1','Harmony Dist. 2','Langsdale','Manassa'],
 3:['North Quitman','Oakgrove','Pachuta','Rolling Creek','Shubuta','Snell','Souinlovie','South Quitman','Springs','Stonewall Dist. 3','Stonewall Dist. 1'],
 4:['Union','TOTAL','','','','','','','','',''],
}
GRIDS={
 2:{
 E:[150,77,140,170,12,252,77,52,116,39,4],
 H:[60,153,108,984,145,952,70,88,174,16,107],
 J:[1,3,2,26,1,18,2,3,5,0,0],
 },
 3:{
 E:[86,241,204,29,432,7,35,463,75,98,250],
 H:[253,36,91,186,78,160,164,271,63,330,88],
 J:[7,1,2,1,7,0,7,8,3,10,5],
 },
 4:{
 E:[44,3053,None,None,None,None,None,None,None,None,None],
 H:[592,5169,None,None,None,None,None,None,None,None,None],
 J:[13,125,None,None,None,None,None,None,None,None,None],
 },
}
if __name__=='__main__':build('clarke','clarke',GRIDS,LABELS,23,'v2')
