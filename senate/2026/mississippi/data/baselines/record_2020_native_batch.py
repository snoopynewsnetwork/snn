"""Independent complete-original 2020 native Senate readings, publication scoped.

Candidate glyphs and literal headers are typed from whole originals. Machine
grid positions are retained only after physical page review; no 2024 name join.
"""
import csv,gzip,json
from collections import Counter
from sources import OUT,BASE,save,sha,original
from build_counties import writecsv
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
PARTIES=['Democrat','Republican','Libertarian']
VALUES={'sos-2020-county-alcorn':{
 2:dict(labels=['2nd District Central\nPrecinct','Bethel','Biggersville','College Hill','East Corinth','Five Points 1st Dist','Glen','Jacinto','Kossuth','North Corinth','Pinecrest'],native=11,total=None,x=[664,784,904,1024,1148,1268,1388,1511,1631,1750,1872,1991],header_y=[252,478],row_y=[[1204,1264],[1264,1317],[1317,1372]],values=[
 [237,11,192,289,439,249,159,33,174,218,138],
 [1089,73,600,401,840,1218,777,311,1367,830,326],
 [43,0,19,17,24,39,34,10,33,18,11]]),
 3:dict(labels=['Rienzi','Shady Grove','South Corinth','Union Center','Wenasoga','West Corinth','TOTAL','','','',''],native=6,total=7,x=[658,779,900,1021,1142,1264,1384,1506,1626,1745,1865,1985],header_y=[245,470],row_y=[[1196,1256],[1256,1309],[1309,1364]],values=[
 [200,172,611,133,207,179,3641],
 [748,679,440,889,614,414,11616],
 [27,31,15,24,20,13,378]])}}
VALUES['sos-2020-county-benton']={2:dict(
 labels=['Ashland Precinct\nDistrict 3','Canaan Precinct\nDistrict 1','Floyd Precinct Dist 4','Hickory Flat Prec\nDist 5','Lamar Precinct\nDistrict 2','TOTAL','','','','',''],
 native=5,total=6,x=[699,818,936,1055,1176,1294,1413,1530,1648,1766,1885,2003],header_y=[280,520],
 row_y=[[1260,1460],[1260,1460],[1260,1460]],
 row_window_status='Broad entire Senate-band reading window only, deliberately not an exact candidate-row/cell polygon. Complete original page and named printed row are numeric authority; machine grid failed and is retained unchanged.',
 values=[[397,468,229,157,617,1868],[451,344,562,743,220,2320],[22,8,14,39,9,92]])}
VALUES['sos-2020-county-benton-amended']={2:dict(
 labels=['Ashland Precinct\nDistrict 3','Canaan Precinct\nDistrict 1','Floyd Precinct Dist 4','Hickory Flat Prec\nDist 5','Lamar Precinct\nDistrict 2','TOTAL','','','','',''],
 native=5,total=6,x=[707,826,944,1063,1184,1303,1422,1540,1658,1777,1896,2016],header_y=[282,523],row_y=[[1260,1465],[1260,1465],[1260,1465]],
 row_window_status='Broad entire Senate-band reading window, not an exact candidate-row/cell polygon; complete original named row is authority.',
 values=[[397,468,229,157,617,1868],[451,344,562,743,220,2320],[22,8,14,39,9,92]])}
VALUES['sos-2020-county-greene']={
 2:dict(labels=['Leakesville','North Leakesville','State Line','Mutual Rights','Wade','Jones','Piave','Maples','Vernal','Washington Neely','Leaf'],native=11,total=None,x=[723,843,962,1081,1199,1317,1435,1553,1670,1788,1907,2027],header_y=[310,542],row_y=[[1270,1470],[1270,1470],[1270,1470]],row_window_status='Broad entire Senate-band original reading windows, not exact candidate polygons. Machine header grid merged multiple columns; complete original physical11column layout supplies separate identities.',values=[
 [134,177,353,16,42,8,13,86,93,19,46],
 [948,137,306,179,468,193,333,543,424,281,95],
 [35,7,5,7,15,4,5,16,9,8,4]]),
 3:dict(labels=['McLain','Jonathan','TOTAL','','','','','','','',''],native=2,total=3,x=[718,836,955,1073,1190,1309,1427,1546,1662,1780,1899,2017],header_y=[310,542],row_y=[[1270,1470],[1270,1470],[1270,1470]],row_window_status='Broad entire Senate-band original reading windows, not exact candidate polygons; complete original visibly2constituents thenTOTALc3 and8unused.',values=[
 [183,26,1196],[128,360,4395],[6,8,129]])}
VALUES['sos-2020-county-wilkinson']={2:dict(
 labels=['Centreville 1st 1020','Centreville 3rd 3010','Cold Springs 4020','Fort Adams 2020','Longmire 5020','Woodville 5th 5010','Woodville 4th 4010','Woodville 1010','Woodville 2nd 2010','TOTAL',''],
 ids=['1020','3010','4020','2020','5020','5010','4010','1010','2010',None,None],
 native=9,total=10,x=[709,828,948,1066,1183,1303,1420,1539,1657,1774,1891,2008],header_y=[282,512],row_y=[[1249,1420],[1249,1420],[1249,1420]],
 row_window_status='Broad entire Senate-band reading windows, not exact row/cell polygons. Machine grid omitted first constituent and merged several headers/three candidate rows; every physical header/candidate vector read directly from full original.',values=[
 [372,445,98,245,144,298,508,216,376,2702],
 [83,289,102,69,210,205,95,130,112,1295],
 [13,10,3,3,9,14,10,5,13,80]])}
VALUES['sos-2020-county-issaquena']={2:dict(
 labels=['Addie Voting Precinct','Grace Voting Precinct','Mayersville\nCourthouse','Tallula Community\nCenter','Valley Park\nCommunity Center','TOTAL','','','','',''],
 native=5,total=6,x=[707,826,947,1066,1183,1302,1422,1538,1654,1771,1886,2004],header_y=[260,489],row_y=[[1234,1405],[1234,1405],[1234,1405]],
 row_window_status='Broad entire Senate-band original reading windows, not exact candidate-row polygons; full original printed named rows are authority.',values=[
 [79,51,157,60,20,367],[63,84,12,83,67,309],[0,1,2,1,1,5]])}
VALUES['sos-2020-county-noxubee']={2:dict(
 labels=['Brooksville','Cliftonville','District 3 Central','Mashulaville','Noxubee Human\nResource Bldg','Prairie Point','Shuqualak','Summerville','TOTAL','',''],native=8,total=9,
 x=[701,820,940,1059,1177,1297,1416,1534,1652,1770,1886,2004],header_y=[272,505],row_y=[[1243,1304],[1304,1359],[1359,1414]],
 values=[[777,424,1047,157,799,355,542,37,4138],[259,27,153,192,186,138,123,100,1178],[6,1,6,1,1,1,5,0,21]])}
VALUES['sos-2020-county-sharkey']={2:dict(
 labels=['Anguilla Fifth District','Anguilla Fourth\nDistrict','Cary Second District','Delta City Fifth\nDistrict','Rolling Fork First\nDistrict','Rolling Fork Fourth\nDistrict','Rolling Fork Second\nDistrict','Rolling Fork Third\nDistrict','Spanish Fort First\nDistrict','Straight Bayou\nFourth District','TOTAL'],native=10,total=11,
 x=[674,791,912,1028,1148,1266,1384,1502,1618,1736,1852,1970],header_y=[271,499],row_y=[[1234,1296],[1296,1350],[1350,1406]],
 row_window_status='Source candidate row reading windows on complete original; machine extra column1970..2128 is outer-page whitespace beyond actual table, excluded as no printed column.',
 values=[[176,185,228,150,267,100,48,321,3,33,1511],[30,119,80,88,243,4,0,20,30,49,663],[2,1,0,0,1,1,0,2,0,0,7]])}
VALUES['sos-2020-county-sharkey-amended']={2:dict(
 labels=['Anguilla Fifth District','Anguilla Fourth\nDistrict','Cary Second District','Delta City Fifth\nDistrict','Rolling Fork First\nDistrict','Rolling Fork Fourth\nDistrict','Rolling Fork Second\nDistrict','Rolling Fork Third\nDistrict','Spanish Fort First\nDistrict','Straight Bayou\nFourth District','TOTAL'],native=10,total=11,
 x=[676,800,924,1048,1173,1298,1422,1546,1669,1794,1917,2042],header_y=[238,481],row_y=[[1256,1320],[1320,1379],[1379,1437]],
 values=[[176,185,228,150,267,100,48,321,3,33,1511],[30,119,80,88,243,4,0,20,30,49,663],[2,1,0,0,1,1,0,2,0,0,7]])}
VALUES['sos-2020-county-calhoun']={2:dict(
 labels=['Banner','Bruce #3','Calhoun City #1','Calhoun City 4','Derma # 4','Derma #5','Northeast Calhoun','Pittsboro #1','Pittsboro #2','Vardaman','TOTAL'],native=10,total=11,
 x=[694,814,934,1056,1176,1297,1418,1539,1658,1776,1893,2014],header_y=[267,502],row_y=[[1246,1308],[1308,1364],[1364,1420]],
 values=[[59,255,436,272,77,117,125,394,160,243,2138],[374,715,290,716,290,359,629,95,390,483,4341],[8,16,11,16,3,6,19,3,16,14,112]])}
VALUES['sos-2020-county-tishomingo']={
 2:dict(labels=['Iuka','Belmont','Burnsville','Coles Mill','Cotton Springs','Dennis','East Iuka','Golden','Hubbard Salem','North Belmont','North Burnsville'],native=11,total=None,
 x=[671,790,909,1028,1148,1268,1386,1505,1624,1742,1862,1982],header_y=[273,504],row_y=[[1246,1307],[1307,1362],[1362,1418]],values=[
 [343,106,107,83,25,24,296,53,17,35,95],
 [1391,779,643,452,206,204,917,472,111,257,411],
 [55,19,25,8,2,4,43,13,5,12,8]]),
 3:dict(labels=['Paden','Springhill','Tishomingo','TOTAL','','','','','','',''],native=3,total=4,
 x=[658,776,896,1016,1134,1254,1374,1493,1612,1730,1848,1966],header_y=[248,480],row_y=[[1220,1282],[1282,1337],[1337,1392]],values=[
 [41,102,267,1594],[207,334,832,7216],[15,18,29,256]])}
VALUES['sos-2020-county-smith']={
 2:dict(labels=['Ag-Complex','Burns','Cedar Grove','Center Ridge','Clear Springs-\nPineville','Lorena - Spinola','Mize','North Raleigh','Polkville','Shady Grove','Summerland'],native=11,total=None,
 x=[656,781,905,1030,1155,1279,1404,1528,1651,1774,1898,2022],header_y=[245,493],row_y=[[1250,1460],[1250,1460],[1250,1460]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate-row polygons. Physical eleven-column header grid independently reviewed; original machine grid omitted two internal rules.',values=[
 [77,90,56,31,23,66,53,264,35,21,435],
 [483,197,107,389,252,299,549,402,448,386,220],
 [12,2,0,10,5,3,11,18,7,5,0]]),
 3:dict(labels=['Sylvarena','Taylorsville','Union-New Home','Warren Hill','West Raleigh','White Oak','Zion Hill - New Haven','TOTAL','','',''],native=7,total=8,
 x=[659,784,909,1033,1158,1282,1407,1531,1655,1778,1901,2025],header_y=[248,490],row_y=[[1264,1328],[1328,1387],[1387,1445]],values=[
 [21,110,142,339,26,19,169,1977],
 [172,708,314,43,317,343,573,6202],
 [6,10,13,0,8,5,15,130]])}
VALUES['sos-2020-county-carroll']={
 2:dict(labels=['430 School','Black Hawk','Calvary','Carrollton','East Vaiden','Fire Tower','Gravel Hill','Jefferson','McCarley','North Carrollton','Rays Shop'],native=11,total=None,
 x=[684,802,921,1040,1160,1279,1398,1517,1635,1752,1870,1988],header_y=[251,488],row_y=[[1230,1290],[1290,1346],[1346,1402]],values=[
 [183,92,10,69,289,461,59,31,163,81,93],[89,192,158,299,288,219,373,149,269,347,716],[2,3,5,6,6,11,3,1,5,11,20]]),
 3:dict(labels=['Salem','West Carroll','West Vaiden','TOTAL','','','','','','',''],native=3,total=4,
 x=[689,807,926,1045,1163,1283,1402,1520,1639,1756,1874,1992],header_y=[264,498],row_y=[[1240,1302],[1302,1357],[1357,1413]],
 row_window_status='Source named-row reading windows; machine extra1992..2126column is outside actual table and excluded.',values=[[163,42,187,1923],[67,356,194,3716],[1,5,5,84]])}
VALUES['sos-2020-county-clay']={
 2:dict(labels=['Cairo','Caradine','Cedar Bluff','Central-West Point','East-West Point','North-West Point','Pheba','Pine Bluff','Siloam','South-West Point','Tibbee'],native=11,total=None,
 x=[694,812,930,1048,1166,1284,1402,1521,1638,1756,1874,1992],header_y=[233,468],row_y=[[1195,1390],[1195,1390],[1195,1390]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons. Incomplete machine grid supplies only some rules; all eleven physical columns independently read from full original.',values=[
 [159,568,27,541,593,833,250,288,338,781,206],[176,102,145,327,846,531,208,64,506,252,113],[6,5,7,18,11,6,6,2,12,14,6]]),
 3:dict(labels=['Union Star','Vinton','West-West Point','TOTAL','','','','','','',''],native=3,total=4,
 x=[700,817,935,1053,1171,1290,1408,1526,1644,1761,1878,1996],header_y=[238,472],row_y=[[1205,1395],[1205,1395],[1205,1395]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; actual three constituents/TOTAL/seven unused columns read on complete original.',values=[
 [309,305,973,6171],[254,220,262,4006],[6,4,6,109]])}
VALUES['sos-2020-county-jefferson']={
 2:dict(labels=['CANNONSBURG','CHURCH HILL','CITY HALL','COMMUNITY GARDEN\nCENTER','HARRISTON','LOCUST GROVE\nBAPTIST CHURCH','LORMAN','MT. ISREAL BAPTIST\nCHURCH','MULTIPURPOSE\nCENTER','RED LICK','STAMPLEY'],native=11,total=None,
 x=[686,812,936,1060,1184,1310,1434,1558,1680,1804,1926,2050],header_y=[240,482],row_y=[[1256,1320],[1320,1378],[1378,1436]],values=[
 [192,63,473,391,204,521,192,414,297,281,236],[17,101,13,46,12,13,46,39,6,42,7],[1,0,3,2,1,1,0,0,0,1,1]]),
 3:dict(labels=['UNION CHURCH','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[678,802,926,1051,1175,1300,1424,1548,1671,1794,1918,2040],header_y=[240,485],row_y=[[1250,1445],[1250,1445],[1250,1445]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; extra2040..2126machine column is outer whitespace beyond actual table.',values=[[164,3428],[134,476],[2,12]])}
VALUES['sos-2020-county-claiborne']={
 2:dict(labels=['County Precinct 1-A','County Precinct 1-B','County Precinct 2-A','County Precinct 2-B','County Precinct 3-A','County Precinct 3-B','County Precinct 4-A','County Precinct 4-B','County Precinct 4-D','County Precinct 5-A','County Precinct 5-B'],ids=['1-A','1-B','2-A','2-B','3-A','3-B','4-A','4-B','4-D','5-A','5-B'],native=11,total=None,
 x=[722,840,959,1077,1196,1315,1434,1554,1672,1790,1909,2028],header_y=[244,479],row_y=[[1218,1280],[1280,1336],[1336,1392]],values=[
 [588,326,398,219,682,17,351,388,28,497,413],[78,3,74,30,135,17,26,43,70,19,60],[1,4,3,1,8,0,3,2,2,0,2]]),
 3:dict(labels=['TOTAL','','','','','','','','','',''],native=0,total=1,
 x=[720,836,956,1075,1193,1313,1432,1551,1668,1786,1904,2024],header_y=[243,476],row_y=[[1215,1276],[1276,1333],[1333,1390]],values=[[3907],[555],[26]])}
VALUES['sos-2020-county-sunflower']={
 2:dict(labels=['11-Inverness','12-Moorhead','13-Indianola #1\nSoutheast','21-Indianola #2 West','22-Indianola #2 East','31-Indianola #3\nSouth','32-Indianola #3\nNorth','33-Indianola #3\nNortheast','41-Fairview-Hale','42-Boyer-Linn','43-Doddsville'],ids=['11','12','13','21','22','31','32','33','41','42','43'],native=11,total=None,
 x=[672,788,904,1024,1142,1259,1376,1496,1612,1728,1846,1966],header_y=[244,471],row_y=[[1198,1385],[1198,1385],[1198,1385]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; machine extra1966..2122column is page/fax margin outside actual table.',values=[
 [322,679,470,519,1492,538,278,224,21,173,118],[405,111,5,182,31,428,166,202,85,180,20],[2,3,1,3,6,4,1,3,0,0,0]]),
 3:dict(labels=['44-Ruleville','45-Sunflower 4','51-Ruleville North','52-Sunflower\nPlantation','53-Rome','54-Drew','TOTAL','','','',''],ids=['44','45','51','52','53','54',None,None,None,None,None],native=6,total=7,
 x=[678,796,912,1031,1150,1268,1386,1505,1624,1740,1856,1976],header_y=[250,482],row_y=[[1210,1395],[1210,1395],[1210,1395]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; full original named rows supply authority.',values=[
 [778,387,182,18,74,747,7020],[66,83,217,130,59,253,2623],[6,2,2,0,3,6,42]])}
VALUES['sos-2020-county-choctaw']={
 2:dict(labels=['Bywy','Chester','District 5','East Weir','Fentress','French Camp','Hebron','Kenego','Panhandle','Reform','Sherwood'],native=11,total=None,
 x=[702,823,941,1062,1182,1300,1420,1539,1656,1774,1890,2008],header_y=[277,508],row_y=[[1250,1312],[1312,1368],[1368,1423]],values=[
 [66,71,203,219,81,61,36,24,102,98,20],[141,186,736,73,187,256,174,224,126,194,291],[2,0,22,4,5,7,6,6,5,2,10]]),
 3:dict(labels=['Southwest Ackerman','West Weir','TOTAL','','','','','','','',''],native=2,total=3,
 x=[705,825,944,1064,1184,1304,1423,1542,1658,1775,1893,2010],header_y=[272,504],row_y=[[1246,1308],[1308,1363],[1363,1419]],values=[[248,91,1320],[47,176,2811],[5,4,78]])}
VALUES['sos-2020-county-sunflower-amended']={
 2:dict(labels=['11-Inverness','12-Moorhead','13-Indianola #1\nSoutheast','21-Indianola #2 West','22-Indianola #2 East','31-Indianola #3\nSouth','32-Indianola #3\nNorth','33-Indianola #3\nNortheast','41-Fairview-Hale','42-Boyer-Linn','43-Doddsville'],ids=['11','12','13','21','22','31','32','33','41','42','43'],native=11,total=None,
 x=[672,789,906,1024,1142,1261,1378,1495,1614,1732,1848,1964],header_y=[254,484],row_y=[[1210,1390],[1210,1390],[1210,1390]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; each amended-original glyph freshly read. Missing internal machine rules restored by actual full original header grid, not source-column ordinal matching.',values=[
 [322,679,470,519,1492,538,278,224,21,173,118],[405,111,5,182,31,428,166,202,85,180,20],[2,3,1,3,6,4,1,3,0,0,0]]),
 3:dict(labels=['44-Ruleville','45-Sunflower 4','51-Ruleville North','52-Sunflower\nPlantation','53-Rome','54-Drew','TOTAL','','','',''],ids=['44','45','51','52','53','54',None,None,None,None,None],native=6,total=7,
 x=[670,786,904,1024,1142,1260,1378,1496,1616,1732,1848,1967],header_y=[238,470],row_y=[[1208,1270],[1270,1322],[1322,1376]],values=[
 [778,387,182,18,74,747,7020],[66,83,217,130,59,253,2623],[6,2,2,0,3,6,42]])}
VALUES['sos-2020-county-choctaw-amended']={
 2:dict(labels=['Bywy','Chester','District 5','East Weir','Fentress','French Camp','Hebron','Kenego','Panhandle','Reform','Sherwood'],native=11,total=None,
 x=[717,836,955,1076,1195,1316,1436,1555,1674,1793,1912,2032],header_y=[258,488],row_y=[[1228,1290],[1290,1344],[1344,1400]],values=[
 [66,71,203,219,81,61,36,24,102,98,20],[141,186,736,73,187,256,174,224,126,194,291],[2,0,22,4,5,7,6,6,5,2,10]]),
 3:dict(labels=['Southwest Ackerman','West Weir','TOTAL','','','','','','','',''],native=2,total=3,
 x=[720,840,960,1080,1200,1320,1440,1560,1680,1798,1918,2038],header_y=[260,492],row_y=[[1231,1292],[1292,1348],[1348,1402]],values=[[248,91,1320],[47,176,2811],[5,4,78]])}
VALUES['sos-2020-county-perry']={
 2:dict(labels=['Arlington 4100','Beaumont District 1\n1030','Beaumont Senior\nCitizens 5120','Courthouse 5110','Deep Creek 5150','Hintonville 4090','Indian Springs 1010','Janice 5140','Miracle Temple\nCOGIC 1040','New Augusta\nCommunity Center','Prospect 2050'],ids=['4100','1030','5120','5110','5150','4090','1010','5140','1040',None,'2050'],native=11,total=None,
 x=[706,824,940,1058,1176,1292,1410,1528,1643,1759,1874,1989],header_y=[279,508],row_y=[[1246,1307],[1307,1361],[1361,1416]],values=[
 [86,391,47,43,19,90,136,74,103,116,24],[375,95,109,249,53,184,143,459,33,114,200],[10,4,4,9,1,7,7,16,1,7,9]]),
 3:dict(labels=['Richton Holly Street\n3060','Richton Multi Purpose\n4080','Runnelstown 2040','Thompson Hill 5130','TOTAL','','','','','',''],ids=['3060','4080','2040','5130',None,None,None,None,None,None,None],native=4,total=5,
 x=[716,834,952,1069,1186,1303,1420,1538,1654,1768,1884,2000],header_y=[280,509],row_y=[[1230,1420],[1230,1420],[1230,1420]],
 row_window_status='Broad complete Senate-band original reading windows, not exact polygons. Machine Senate row locator targeted a presidential row and merged physical columns; complete original supplies the accepted candidate/column observations.',values=[
 [220,119,83,4,1555],[1031,239,858,62,4204],[42,6,18,1,142]])}
VALUES['sos-2020-county-yalobusha']={
 2:dict(labels=['Beat One North','Beat One South','Beat Two Water\nValley','Five Coffeeville','Five Scobey','Five Tillatoba','Four Coffeeville','Four Oakland',"Scuna - Vann's Mill\nNorth","Scuna - Vann's Mill\nSouth",'Three North West'],native=11,total=None,
 x=[683,802,921,1038,1156,1275,1393,1511,1629,1747,1864,1982],header_y=[293,524],row_y=[[1259,1320],[1320,1376],[1376,1432]],values=[
 [436,160,777,273,62,43,386,438,35,8,274],[569,220,371,377,122,155,78,394,42,56,633],[13,7,6,12,0,5,3,10,1,1,18]]),
 3:dict(labels=['Three Sylva Rena','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[680,798,917,1036,1154,1272,1390,1508,1626,1744,1860,1978],header_y=[290,521],row_y=[[1255,1316],[1316,1372],[1372,1427]],values=[[113,3005],[398,3415],[12,88]])}
VALUES['sos-2020-county-webster']={
 2:dict(labels=['Bellefontaine','Big Black','Bluff Springs','Cadaretta','Clarkson','Cumberland','Eupora No. 1','Eupora No. 2','Eupora No. 3','Fame','Fay'],native=11,total=None,
 x=[696,816,932,1051,1169,1288,1406,1525,1642,1760,1878,1997],header_y=[265,498],row_y=[[1234,1294],[1294,1349],[1349,1404]],values=[
 [32,23,57,8,27,64,455,46,78,23,7],[227,176,76,98,290,264,369,215,164,195,99],[3,6,0,3,4,8,15,18,5,8,1]],
 numeric_correction_history=[dict(candidate='Mike Espy',source_column=6,label_literal='Cumberland',initial_manual_reading=54,accepted_original_reading=64,basis='Initial vector failed county closure; subsequent enlarged complete original Senate-row reading visibly64. Source glyph, not residual allocation, supplies correction.',evidence_crop_bounds=[690,1225,2002,1409],evidence_crop_name='p0002-complete-senate-rows-original.png')]),
 3:dict(labels=['Grady','Maben','Mantee','Mathiston','Tomnolen','Walthall','TOTAL','','','',''],native=6,total=7,
 x=[691,809,928,1044,1164,1282,1400,1518,1636,1756,1872,1992],header_y=[260,495],row_y=[[1229,1290],[1290,1345],[1345,1400]],values=[
 [47,129,43,92,37,30,1198],[191,330,307,466,278,322,4067],[5,10,6,7,8,6,113]])}
VALUES['sos-2020-county-yalobusha-amended']={
 2:dict(labels=['Beat One North','Beat One South','Beat Two Water\nValley','Five Coffeeville','Five Scobey','Five Tillatoba','Four Coffeeville','Four Oakland',"Scuna - Vann's Mill\nNorth","Scuna - Vann's Mill\nSouth",'Three North West'],native=11,total=None,
 x=[678,797,916,1034,1153,1272,1390,1508,1624,1741,1857,1976],header_y=[266,497],row_y=[[1232,1294],[1294,1350],[1350,1405]],values=[
 [436,160,777,273,62,43,386,438,35,8,274],[569,220,371,377,122,155,78,394,42,56,633],[13,7,6,12,0,5,3,10,1,1,18]]),
 3:dict(labels=['Three Sylva Rena','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[680,799,918,1036,1155,1273,1391,1509,1626,1743,1859,1976],header_y=[274,506],row_y=[[1240,1303],[1303,1358],[1358,1413]],
 row_window_status='Complete original physical review restores first constituent omitted by machine grid. TOTAL is physical column2, not earlier unaccepted county-TOTAL locator proposal1; old proposal retained separately, candidate values unchanged.',values=[[113,3005],[398,3415],[12,88]])}
VALUES['sos-2020-county-covington']={
 2:dict(labels=['Collins','Dry Creek','Gilmer / Yawn','Lone Star / Black\nJack','Mitchell','Mt Olive','Okahay','Richmond','Rock Hill','Sanford','Seminary/West\nCollins'],native=11,total=None,
 x=[705,824,940,1060,1178,1292,1412,1526,1644,1760,1872,1984],header_y=[294,523],row_y=[[1245,1435],[1245,1435],[1245,1435]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; machine named candidate row detection failed.',values=[
 [732,295,508,73,10,598,540,69,19,91,249],[711,80,241,180,165,472,81,729,117,683,1418],[20,4,10,0,3,15,7,13,1,26,15]]),
 3:dict(labels=['South Collins','Station Creek','Strahan','Williamsburg','TOTAL','','','','','',''],native=4,total=5,
 x=[706,824,942,1057,1176,1292,1410,1528,1644,1760,1872,1984],header_y=[292,520],row_y=[[1254,1316],[1316,1370],[1370,1425]],values=[
 [56,308,35,54,3637],[302,110,97,218,5604],[10,1,0,6,131]])}
VALUES['sos-2020-county-covington-amended']={
 2:dict(labels=['Collins','Dry Creek','Gilmer / Yawn','Lone Star / Black\nJack','Mitchell','Mt Olive','Okahay','Richmond','Rock Hill','Sanford','Seminary/West\nCollins'],native=11,total=None,
 x=[694,812,930,1046,1164,1281,1399,1516,1636,1754,1872,1992],header_y=[264,494],row_y=[[1220,1410],[1220,1410],[1220,1410]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; amended original candidate vectors freshly read from complete page, not copied from matching earlier publication.',values=[
 [732,295,508,73,10,598,540,69,19,91,249],[711,80,241,180,165,472,81,729,117,683,1418],[20,4,10,0,3,15,7,13,1,26,15]]),
 3:dict(labels=['South Collins','Station Creek','Strahan','Williamsburg','TOTAL','','','','','',''],native=4,total=5,
 x=[696,812,930,1047,1164,1282,1400,1518,1636,1754,1873,1994],header_y=[264,494],row_y=[[1220,1415],[1220,1415],[1220,1415]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; missing internal header rule restored by complete original physical review.',values=[
 [56,308,35,54,3637],[302,110,97,218,5604],[10,1,0,6,131]])}
VALUES['sos-2020-county-prentiss']={
 2:dict(labels=['Baldwyn','Blackland','Booneville/Ag-Ctr','Cairo','Cross Roads','East Booneville','Hills Chapel- New\nHope','Ingram','Marietta','New Site','North\nBooneville/Sunflower'],native=11,total=None,
 x=[684,804,923,1042,1162,1281,1401,1520,1640,1761,1880,2001],header_y=[262,497],row_y=[[1247,1308],[1308,1364],[1364,1420]],values=[
 [483,59,204,51,117,249,102,28,88,72,472],[484,313,839,292,421,518,727,202,512,487,202],[14,8,19,4,18,19,26,7,19,15,7]]),
 3:dict(labels=['Thrasher','Tuscumbia-New\nCandler','West Booneville','Wheeler','TOTAL','','','','','',''],native=4,total=5,
 x=[684,804,922,1042,1161,1281,1401,1521,1640,1760,1879,2001],header_y=[258,494],row_y=[[1230,1420],[1230,1420],[1230,1420]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; full original named rows authority.',values=[
 [146,120,345,158,2694],[316,478,1249,563,7603],[13,17,26,15,227]])}
VALUES['sos-2020-county-prentiss-amended']={
 2:dict(labels=['Baldwyn','Blackland','Booneville/Ag-Ctr','Cairo','Cross Roads','East Booneville','Hills Chapel- New\nHope','Ingram','Marietta','New Site','North\nBooneville/Sunflower'],native=11,total=None,
 x=[688,808,926,1046,1164,1284,1404,1523,1642,1759,1878,1998],header_y=[247,483],row_y=[[1234,1296],[1296,1352],[1352,1407]],values=[
 [489,59,204,51,117,253,102,28,89,72,476],[486,313,839,293,421,524,739,202,521,487,207],[14,8,19,4,18,20,26,7,19,15,7]]),
 3:dict(labels=['Thrasher','Tuscumbia-New\nCandler','West Booneville','Wheeler','TOTAL','','','','','',''],native=4,total=5,
 x=[712,830,949,1068,1186,1304,1424,1541,1659,1776,1893,2011],header_y=[248,484],row_y=[[1220,1410],[1220,1410],[1220,1410]],
 row_window_status='Broad complete Senate-band amended-original reading windows, not exact candidate polygons; all source glyphs independently read, no residual allocation or copy from earlier packet.',values=[
 [146,120,348,160,2714],[316,478,1257,568,7651],[13,17,27,15,229]])}
VALUES['sos-2020-county-adams']={
 3:dict(labels=['Dist. 1, Bellemont\nPrecinct','Dist. 1, By-Pass Fire\nPrecinct','Dist. 1, Courthouse\nPrecinct','Dist. 2, Beau Pre\nPrecinct','Dist. 2, Duncan Park\nPrecinct','Dist. 2, Kingston\nPrecinct','Dist. 2, Liberty Park\nPrecinct','Dist. 3, Concord\nPrecinct','Dist. 3, Maryland\nHgts. Precinct','Dist. 3, Nps Multi\nPurpose Bldg.','Dist. 3, Palestine\nPrecinct'],native=11,total=None,
 x=[663,783,902,1024,1144,1264,1384,1505,1624,1746,1866,1986],header_y=[241,475],row_y=[[1222,1286],[1286,1342],[1342,1398]],values=[
 [947,248,385,471,410,105,222,31,431,240,507],[947,248,385,471,432,513,503,31,16,132,351],[22,9,12,11,19,10,9,4,1,5,15]]),
 4:dict(labels=['Dist. 4, Carpenter\nPrecinct','Dist. 4, Morgantown\nPrecinct','Dist. 4, Northside\nPrecinct','Dist. 4, Pine Ridge\nPrecinct','Dist. 5, Airport\nPrecinct','Dist. 5, Foster Mound\nPrecinct','Dist. 5, Oakland\nPrecinct','Dist. 5, Washington\nPrecinct','TOTAL','',''],native=8,total=9,
 x=[661,780,901,1022,1141,1262,1382,1502,1622,1742,1862,1983],header_y=[241,475],row_y=[[1210,1405],[1210,1405],[1210,1405]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; original printed values retained even where two candidate rows print identical cells.',values=[
 [125,362,1069,369,192,831,586,205,7736],[125,99,55,80,192,38,457,341,5416],[1,2,6,3,3,5,9,6,152]])}
VALUES['sos-2020-county-adams-amended']={
 2:dict(labels=['Dist. 1, Bellemont\nPrecinct','Dist. 1, By-Pass Fire\nPrecinct','Dist. 1, Courthouse\nPrecinct','Dist. 2, Beau Pre\nPrecinct','Dist. 2, Duncan Park\nPrecinct','Dist. 2, Kingston\nPrecinct','Dist. 2, Liberty Park\nPrecinct','Dist. 3, Concord\nPrecinct','Dist. 3, Maryland\nHgts. Precinct','Dist. 3, Nps Multi\nPurpose Bldg.','Dist. 3, Palestine\nPrecinct'],native=11,total=None,
 x=[677,792,908,1023,1138,1254,1368,1483,1598,1713,1828,1942],header_y=[250,477],row_y=[[1206,1267],[1267,1322],[1322,1377]],
 row_window_status='Complete original candidate row reading windows; machine grid omitted first and several internal physical columns, restored by full original header review.',values=[
 [553,539,199,332,410,105,222,534,431,240,507],[947,248,385,471,432,513,503,31,16,132,351],[22,9,12,11,19,10,9,4,1,5,15]]),
 3:dict(labels=['Dist. 4, Carpenter\nPrecinct','Dist. 4, Morgantown\nPrecinct','Dist. 4, Northside\nPrecinct','Dist. 4, Pine Ridge\nPrecinct','Dist. 5, Airport\nPrecinct','Dist. 5, Foster Mound\nPrecinct','Dist. 5, Oakland\nPrecinct','Dist. 5, Washington\nPrecinct','TOTAL','',''],native=8,total=9,
 x=[682,797,912,1027,1142,1257,1372,1486,1603,1718,1832,1946],header_y=[255,479],row_y=[[1200,1385],[1200,1385],[1200,1385]],
 row_window_status='Broad complete Senate-band amended-original reading windows, not exact numeric polygons; every candidate glyph independently read from complete original.',values=[
 [287,362,1069,369,409,831,586,205,8190],[125,99,55,80,192,38,457,341,5416],[1,2,6,3,3,5,9,6,152]])}
VALUES['sos-2020-county-lawrence']={
 2:dict(labels=['Arm','Armory','Center','Coopers Creek (A-Z)','Courthouse A-Z','Grange','Hooker','Jayess','Monticello-Beat 5','New Hebron','Nola'],native=11,total=None,
 x=[719,837,957,1076,1194,1313,1432,1551,1669,1786,1904,2022],header_y=[262,498],row_y=[[1236,1298],[1298,1352],[1352,1408]],values=[
 [269,28,5,36,193,44,131,40,92,80,2],[189,79,143,395,878,165,45,414,6,282,50],[4,0,0,6,6,0,0,10,0,1,0]]),
 3:dict(labels=['Nola 91','Oakvale','Oma','Peyton Town','Silver Creek','Sontag','Stringer/N Pleasant\nHill','Tilton','Topeka','Wanilla','Wanilla 91'],native=11,total=None,
 x=[717,836,955,1074,1193,1311,1431,1549,1666,1784,1902,2021],header_y=[262,498],row_y=[[1225,1415],[1225,1415],[1225,1415]],
 row_window_status='Broad complete original Senate-band reading windows, not exact candidate polygons; physical eleven-column header grid independently read after machine omissions.',values=[
 [47,19,251,135,237,105,195,40,20,13,45],[2,107,54,23,142,244,128,133,217,57,8],[0,2,3,1,7,5,0,2,2,3,0]]),
 4:dict(labels=['West District 1','West Monticello (A-Z)','TOTAL','','','','','','','',''],native=2,total=3,
 x=[719,838,957,1076,1195,1313,1432,1551,1668,1786,1903,2022],header_y=[262,498],row_y=[[1225,1415],[1225,1415],[1225,1415]],
 row_window_status='Broad complete original Senate-band reading windows, not exact candidate polygons. A-Z/91 suffixes remain literal source labels, not a normalized split-style or current geography claim.',values=[[12,279,2318],[164,297,4222],[2,3,57]])}
VALUES['sos-2020-county-lawrence-amended']={
 2:dict(labels=['Arm','Armory','Center','Coopers Creek (A-Z)','Courthouse A-Z','Grange','Hooker','Jayess','Monticello-Beat 5','New Hebron','Nola'],native=11,total=None,
 x=[689,807,927,1046,1164,1283,1402,1519,1638,1756,1875,1994],header_y=[270,505],row_y=[[1230,1425],[1230,1425],[1230,1425]],
 row_window_status='Broad complete Senate-band amended-original reading windows, not exact numeric polygons. Faint machine grid/rows failed; all physical columns and three named vectors independently read from complete original.',values=[
 [269,28,5,36,193,44,131,40,92,80,2],[189,79,143,395,878,165,45,414,6,282,50],[4,0,0,6,6,0,0,10,0,1,0]]),
 3:dict(labels=['Nola 91','Oakvale','Oma','Peyton Town','Silver Creek','Sontag','Stringer/N Pleasant\nHill','Tilton','Topeka','Wanilla','Wanilla 91'],native=11,total=None,
 x=[697,815,934,1053,1172,1291,1409,1527,1646,1764,1883,2002],header_y=[278,513],row_y=[[1240,1435],[1240,1435],[1240,1435]],
 row_window_status='Broad complete Senate-band amended-original reading windows, not exact numeric polygons; full original reading supplies each glyph, not matching earlier-source equality.',values=[
 [47,19,251,135,237,105,195,40,20,13,45],[2,107,54,23,142,244,128,133,217,57,8],[0,2,3,1,7,5,0,2,2,3,0]]),
 4:dict(labels=['West District 1','West Monticello (A-Z)','TOTAL','','','','','','','',''],native=2,total=3,
 x=[696,816,934,1054,1172,1291,1409,1527,1646,1765,1883,2002],header_y=[278,515],row_y=[[1240,1435],[1240,1435],[1240,1435]],
 row_window_status='Broad complete Senate-band amended-original reading windows, not exact numeric polygons; A-Z/91 source suffixes retain unresolved split/administrative meaning.',values=[[12,279,2318],[164,297,4222],[2,3,57]])}
VALUES['sos-2020-county-quitman']={2:dict(
 labels=['Crenshaw','Crowder','Darling','District 3 North','District 3 South','Lambert','North West Marks','Sledge','South West Marks','West Lambert','TOTAL'],native=10,total=11,
 x=[680,797,916,1034,1152,1272,1391,1510,1628,1746,1866,1986],header_y=[255,485],row_y=[[1229,1290],[1290,1346],[1346,1402]],values=[
 [110,57,134,230,191,296,414,347,259,269,2307],[3,189,33,160,175,48,91,41,75,68,883],[1,2,5,2,6,7,8,7,6,4,48]])}
VALUES['sos-2020-county-jefferson-amended']={
 2:dict(labels=['CANNONSBURG','CHURCH HILL','CITY HALL','COMMUNITY GARDEN\nCENTER','HARRISTON','LOCUST GROVE\nBAPTIST CHURCH','LORMAN','MT. ISREAL BAPTIST\nCHURCH','MULTIPURPOSE\nCENTER','RED LICK','STAMPLEY'],native=11,total=None,
 x=[580,677,774,870,966,1062,1159,1255,1350,1447,1543,1638],header_y=[400,582],row_y=[[1150,1300],[1150,1300],[1150,1300]],
 row_window_status='Broad complete Senate-band reading windows, not exact candidate polygons; amended original has smaller table embedded in full page. Entire page/header/candidate vectors independently read; no earlier-publication coordinate equivalence.',values=[
 [192,63,473,391,204,521,192,414,297,281,236],[17,101,13,46,12,13,46,39,6,42,7],[1,0,3,2,1,1,0,0,0,1,1]]),
 3:dict(labels=['UNION CHURCH','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[578,674,770,867,963,1059,1155,1252,1347,1443,1540,1635],header_y=[400,582],row_y=[[1150,1300],[1150,1300],[1150,1300]],
 row_window_status='Broad complete Senate-band reading windows within smaller embedded amended table, not exact candidate polygons; nine actual unused columns retained null.',values=[[164,3428],[134,476],[2,12]])}
VALUES['sos-2020-county-clay-amended']={
 2:dict(labels=['Cairo','Caradine','Cedar Bluff','Central-West Point','East-West Point','North-West Point','Pheba','Pine Bluff','Siloam','South-West Point','Tibbee'],native=11,total=None,
 x=[699,818,937,1055,1173,1291,1409,1528,1646,1764,1882,2001],header_y=[286,520],row_y=[[1255,1445],[1255,1445],[1255,1445]],
 row_window_status='Broad complete Senate-band amended-original reading windows, not exact numeric polygons; all eleven physical columns and candidate vectors independently read after incomplete machine grid.',values=[
 [159,568,27,541,593,833,250,288,338,781,206],[176,102,145,327,846,531,208,64,506,252,113],[6,5,7,18,11,6,6,2,12,14,6]]),
 3:dict(labels=['Union Star','Vinton','West-West Point','TOTAL','','','','','','',''],native=3,total=4,
 x=[698,817,936,1055,1173,1291,1409,1527,1645,1763,1881,2000],header_y=[286,520],row_y=[[1255,1445],[1255,1445],[1255,1445]],
 row_window_status='Broad complete Senate-band amended-original reading windows, not exact candidate polygons; actual three native/TOTAL/seven unused physically reviewed.',values=[
 [309,305,973,6171],[254,220,262,4006],[6,4,6,109]])}
VALUES['sos-2020-county-franklin']={
 2:dict(labels=['Antioch','Bad Bayou','Bude','Cains','Eddiceton','Hamburg','Knoxville','Lucien','McCall','Meadville','Pine Grove'],native=11,total=None,
 x=[690,808,928,1047,1166,1286,1406,1525,1644,1762,1881,2001],header_y=[292,524],row_y=[[1250,1440],[1250,1440],[1250,1440]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; eleven physical header columns restored after machine mergers. Extra outer page-edge machine column excluded.',values=[
 [206,19,407,55,41,204,61,25,60,78,11],[198,375,254,191,317,65,108,143,276,318,117],[5,2,10,3,5,3,4,2,7,3,1]]),
 3:dict(labels=['Roxie','Wesley Chapel','Whittington','TOTAL','','','','','','',''],native=3,total=4,
 x=[685,804,924,1043,1162,1281,1401,1520,1639,1758,1877,1997],header_y=[278,509],row_y=[[1225,1425],[1225,1425],[1225,1425]],
 row_window_status='Broad complete Senate-band original reading windows, not exact candidate polygons; source TOTAL physicalc4/seven unused separate, extra2076page-edge machine column excluded.',values=[[292,71,40,1570],[166,43,262,2833],[2,2,5,54]])}
VALUES['sos-2020-county-humphreys']={
 2:dict(labels=['Belzoni - 4010','Belzoni North - 1bn\n1020','Belzoni North - 2bn\n2020','Belzoni South - 3bs\n3010','Belzoni South - 5bs\n5010','Fourmile North - 1fn\n1010','Gooden Lake North -\n2gn 2030','Isola North - 2In\n2010','Lake City South - 3ls\n3030','Louise South - 5ls\n5030','Midnight South - 5ms\n5020'],ids=['4010','1020','2020','3010','5010','1010','2030','2010','3030','5030','5020'],native=11,total=None,
 x=[632,750,868,986,1104,1222,1342,1460,1579,1698,1818,1938],header_y=[254,484],row_y=[[1216,1278],[1278,1330],[1330,1386]],
 header_qualification='All complete literal printed headers retained in original raster; Isola suffix second glyph in2In can be capitalI/lowercasel in this font and is not a normalized ID. Separate four-digit2010 is visibly printed. Machine column inventory omitted firstBelzoni4010; physical first column restored.',values=[
 [670,625,110,311,294,2,15,463,13,317,56],[214,140,2,10,3,34,38,156,62,87,57],[4,7,0,0,1,1,0,6,0,7,0]]),
 3:dict(labels=['Putnam South - 4ps\n4030','Silver City South -\n3ss 3020','TOTAL','','','','','','','',''],ids=['4030','3020',None,None,None,None,None,None,None,None,None],native=2,total=3,
 x=[628,747,864,983,1102,1219,1338,1458,1576,1696,1814,1935],header_y=[250,481],row_y=[[1213,1274],[1274,1327],[1327,1382]],values=[[51,208,3135],[117,103,1023],[1,2,29]])}
VALUES['sos-2020-county-humphreys-amended']={
 2:dict(labels=['Belzoni - 4010','Belzoni North - 1bn\n1020','Belzoni North - 2bn\n2020','Belzoni South - 3bs\n3010','Belzoni South - 5bs\n5010','Fourmile North - 1fn\n1010','Gooden Lake North -\n2gn 2030','Isola North - 2In\n2010','Lake City South - 3ls\n3030','Louise South - 5ls\n5030','Midnight South - 5ms\n5020'],ids=['4010','1020','2020','3010','5010','1010','2030','2010','3030','5030','5020'],native=11,total=None,
 x=[654,773,891,1010,1128,1247,1366,1484,1604,1723,1842,1962],header_y=[282,512],row_y=[[1244,1304],[1304,1357],[1357,1412]],
 header_qualification='Amended original headers independently read; source raster retains complete lettering. Isola suffix second glyph in2In is font-ambiguous capitalI/lowercasel; only clearly printed four-digit2010 parsed as optional source ID, no semantic/current crosswalk.',values=[
 [670,625,110,311,294,2,15,463,13,317,56],[214,140,2,10,3,34,38,156,62,87,57],[4,7,0,0,1,1,0,6,0,7,0]]),
 3:dict(labels=['Putnam South - 4ps\n4030','Silver City South -\n3ss 3020','TOTAL','','','','','','','',''],ids=['4030','3020',None,None,None,None,None,None,None,None,None],native=2,total=3,
 x=[650,768,887,1005,1124,1242,1361,1480,1600,1718,1838,1958],header_y=[281,510],row_y=[[1242,1302],[1302,1355],[1355,1410]],values=[[51,208,3135],[117,103,1023],[1,2,29]])}
VALUES['sos-2020-county-hinds']={
 2:dict(labels=['Bolton','Brownsville','Byram 1','Byram 2','Byram 3','Cayuga','Chapel Hill','Clinton 1','Clinton 2','Clinton 3','Clinton 4'],native=11,total=None,
 x=[673,792,911,1029,1148,1266,1383,1502,1620,1737,1855,1974],header_y=[267,499],row_y=[[1237,1298],[1298,1354],[1354,1410]],values=[
 [759,216,1809,970,1108,178,354,564,966,1006,591],[265,217,377,819,250,98,318,600,1245,824,340],[6,8,21,13,2,0,4,17,43,32,22]]),
 3:dict(labels=['Clinton 5','Clinton 6','Clinton 7','Cynthia','Dry Grove','Edwards','Learned','Old Byram','Pinehaven','Pocahontas','Precinct 01'],ids=[None]*10+['01'],native=11,total=None,
 x=[672,792,911,1028,1148,1266,1384,1503,1620,1739,1856,1975],header_y=[265,496],row_y=[[1235,1296],[1296,1352],[1352,1408]],values=[
 [417,836,716,372,294,1184,193,915,1198,319,581],[488,417,792,41,481,368,301,592,1042,176,94],[19,25,39,0,15,6,5,30,36,3,8]]),
 4:dict(labels=['Precinct '+s for s in ['02','04','06','08','09','10','11','13','14','16','18']],ids=['02','04','06','08','09','10','11','13','14','16','18'],native=11,total=None,
 x=[673,791,910,1029,1147,1265,1384,1501,1620,1738,1856,1974],header_y=[266,498],row_y=[[1236,1298],[1298,1354],[1354,1409]],values=[
 [156,339,388,408,571,219,304,789,397,1080,323],[9,9,60,203,348,1,3,13,320,316,4],[1,0,4,14,12,1,1,4,11,26,4]]),
 5:dict(labels=['Precinct '+s for s in ['19','20','21','22','23','25','26','27','28','29','30']],ids=['19','20','21','22','23','25','26','27','28','29','30'],native=11,total=None,
 x=[672,790,908,1027,1144,1262,1381,1498,1617,1735,1854,1972],header_y=[267,499],row_y=[[1238,1299],[1299,1354],[1354,1410]],values=[
 [316,357,682,940,688,831,1040,903,713,443,369],[4,7,19,12,5,25,48,8,12,6,1],[2,1,3,5,1,11,8,3,4,1,0]]),
 6:dict(labels=['Precinct '+s for s in ['31','32','33','34','35','36','37','38','39','40','41']],ids=['31','32','33','34','35','36','37','38','39','40','41'],native=11,total=None,
 x=[672,791,910,1028,1146,1264,1382,1500,1618,1735,1855,1971],header_y=[262,494],row_y=[[1233,1294],[1294,1350],[1350,1406]],values=[
 [584,278,315,501,409,640,507,535,657,832,1174],[6,372,616,897,795,167,111,23,11,12,10],[2,11,8,31,22,7,4,3,3,3,1]]),
 7:dict(labels=['Precinct '+s for s in ['42','43','44','45','46','47','49','51','54','55','56']],ids=['42','43','44','45','46','47','49','51','54','55','56'],native=11,total=None,
 x=[672,792,911,1028,1147,1265,1382,1500,1619,1737,1855,1973],header_y=[264,496],row_y=[[1235,1296],[1296,1352],[1352,1408]],values=[
 [780,1119,985,695,1436,343,405,984,287,458,182],[35,51,279,662,642,23,2,15,3,9,5],[7,10,8,22,13,2,1,5,2,0,1]]),
 8:dict(labels=['Precinct '+s for s in ['57','58','59','60','61','62','63','64','68','69','70']],ids=['57','58','59','60','61','62','63','64','68','69','70'],native=11,total=None,
 x=[673,793,912,1030,1148,1267,1385,1502,1621,1739,1856,1976],header_y=[264,496],row_y=[[1235,1297],[1297,1352],[1352,1408]],values=[
 [423,760,683,233,339,822,291,271,1231,693,307],[7,8,13,6,3,18,5,6,59,44,11],[1,5,1,2,3,7,0,0,4,2,3]]),
 9:dict(labels=['Precinct '+s for s in ['71','72','73','74','76','77','78','79','80','81','82']],ids=['71','72','73','74','76','77','78','79','80','81','82'],native=11,total=None,
 x=[675,794,912,1032,1149,1268,1386,1503,1622,1740,1857,1974],header_y=[267,499],row_y=[[1238,1300],[1300,1355],[1355,1410]],values=[
 [489,357,436,430,331,649,696,1125,1076,1387,891],[38,16,19,31,50,117,373,126,30,28,7],[3,5,4,2,6,3,9,8,5,4,1]]),
 10:dict(labels=['Precinct '+s for s in ['83','84','85','86','88','90','91','92','93','94','96']],ids=['83','84','85','86','88','90','91','92','93','94','96'],native=11,total=None,
 x=[674,793,912,1031,1150,1268,1386,1504,1622,1740,1858,1976],header_y=[264,496],row_y=[[1235,1296],[1296,1352],[1352,1408]],values=[
 [1779,166,1496,812,862,1568,1390,1327,682,1754,1039],[26,4,18,5,38,99,76,90,53,133,164],[2,0,4,6,10,12,5,10,2,12,11]]),
 11:dict(labels=['Raymond 1','Raymond 2','Springridge','St Thomas','Terry 1','Terry 2','Tinnin','Utica 1','Utica 2','TOTAL',''],native=9,total=10,
 x=[675,794,913,1031,1150,1268,1386,1505,1622,1741,1859,1976],header_y=[266,498],row_y=[[1237,1298],[1298,1354],[1354,1410]],values=[
 [664,738,1590,319,1161,1173,290,314,515,75467],[895,960,840,17,275,1635,631,269,94,23661],[19,20,14,1,9,32,22,4,0,910]])}
VALUES['sos-2020-county-tunica']={
 2:dict(labels=['Banks/Hambrick','Mhoon Landing','New Sub Park','Prichard','Robinsonville\nCommunity Center','Tunica','Tunica Auditorium','Tunica Co. Supt. of\nEduc.','Two Mile Lake','Westend Store','White Oak Rec.\nCenter'],native=11,total=None,
 x=[678,794,910,1028,1144,1261,1378,1496,1611,1728,1845,1962],header_y=[268,494],row_y=[[1223,1284],[1284,1339],[1339,1394]],values=[
 [202,16,273,281,331,251,351,170,320,40,306],[1,67,132,23,30,192,30,99,84,33,70],[0,2,4,2,4,11,6,7,3,0,2]]),
 3:dict(labels=['Win Job Center','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[681,798,916,1032,1148,1266,1382,1500,1616,1732,1850,1967],header_y=[266,490],row_y=[[1219,1280],[1280,1334],[1334,1389]],values=[[176,2717],[53,814],[1,42]])}
VALUES['sos-2020-county-stone']={
 2:dict(labels=['Bond','National Guard','Old Health\nDepartment','Courthouse','American Legion','New Hope','Perkinston','Magnolia','Mchenry Library','Elarbee','Tuxechana'],native=11,total=None,
 x=[674,794,914,1033,1154,1273,1392,1514,1632,1752,1870,1990],header_y=[258,491],row_y=[[552,613],[613,669],[669,725]],values=[
 [20,41,103,108,403,578,65,40,55,38,112],[105,267,379,353,264,220,251,350,356,352,949],[4,11,12,15,11,6,11,14,10,9,24]]),
 3:dict(labels=['McHenry Community\nCenter','Flint Creek','Big Level','Pleasant Hill','TOTAL','','','','','',''],native=4,total=5,
 x=[678,797,916,1036,1154,1274,1394,1514,1632,1752,1870,1988],header_y=[259,490],row_y=[[550,612],[612,668],[668,724]],values=[[178,166,111,33,2051],[428,620,528,187,5609],[23,15,22,11,198]])}
VALUES['sos-2020-county-attala']={
 2:dict(labels=['Berea','Carmack','East','Ethel','Hesterville','Liberty Chapel','Mcadams','Mccool','Newport','North Central','North East'],native=11,total=None,
 x=[726,845,964,1084,1203,1321,1439,1558,1676,1793,1911,2029],header_y=[267,498],row_y=[[1238,1300],[1300,1356],[1356,1410]],
 row_window_status='Complete original physical eleven-column layout supplies source positions; machine grid omitted first and several internal rules. Named candidate rows read directly, without fitting county residuals.',values=[
 [14,13,213,125,23,66,158,115,139,38,875],[118,191,553,196,191,184,132,152,152,246,264],[2,1,11,3,1,7,4,3,1,6,6]]),
 3:dict(labels=['North West','Possumneck','Providence','Sallis','South Central','South West','Thompson','Williamsville','Zama','TOTAL',''],native=9,total=10,
 x=[722,841,960,1080,1198,1316,1434,1552,1671,1788,1905,2024],header_y=[268,500],row_y=[[1240,1302],[1302,1356],[1356,1412]],
 row_window_status='Complete original ten printed populated columns plus one unused template column; actualTOTAL is physical10, not earlier unaccepted machine proposal4. Earlier locator history remains unchanged.',values=[
 [290,81,35,558,364,254,9,365,89,3824],[397,125,234,251,356,93,129,740,184,4888],[13,1,8,7,14,2,3,9,6,108]])}
VALUES['sos-2020-county-amite']={
 2:dict(labels=['Amite River','Ariel','Berwick','Crosby','East Centreville','East Fork','East Gloster','East Liberty','Gloster','Homochitto','Liberty'],native=11,total=None,
 x=[708,828,946,1066,1184,1303,1420,1538,1656,1773,1891,2008],header_y=[270,510],row_y=[[1250,1445],[1250,1445],[1250,1445]],
 row_window_status='Broad entire Senate-band reading windows only, not exact candidate-row/cell polygons. Faint original defeats machine rule/row discovery; actual eleven headers and all three named vectors read directly from full original.',values=[
 [195,224,224,96,154,83,83,66,455,9,150],[141,69,105,92,225,359,155,173,124,55,403],[2,0,4,2,2,7,4,4,7,1,8]]),
 3:dict(labels=['New Zion','Oneil','Riceville','Smithdale','South Liberty','Tangipahoa','Tickfaw','Vance Park','Walls','Zion Hill','TOTAL'],native=10,total=11,
 x=[708,828,946,1066,1186,1304,1422,1540,1657,1775,1892,2010],header_y=[270,510],row_y=[[1250,1445],[1250,1445],[1250,1445]],
 row_window_status='Broad entire Senate-band reading windows only, not exact candidate polygons. Complete faint original has ten constituents andTOTALphysical11; every header and all candidate glyphs directly read, with no2024native-count/identity import.',values=[
 [46,15,157,137,201,61,120,25,184,65,2750],[275,234,188,230,99,382,121,194,388,335,4347],[5,1,0,5,5,5,2,0,6,4,74]])}
VALUES['sos-2020-county-clarke']={
 2:dict(labels=['Beaverdam','Carmichael','Desoto','East Quitman','Energy','Enterprise','HOPEWELL','Harmony Dist. 1','Harmony Dist. 2','Langsdale','Manassa'],native=11,total=None,
 x=[692,811,930,1048,1167,1285,1405,1524,1641,1759,1877,1996],header_y=[278,508],row_y=[[1246,1308],[1308,1364],[1364,1418]],values=[
 [150,77,140,170,12,252,77,52,116,39,4],[60,153,108,984,145,952,70,88,174,16,107],[1,3,2,26,1,18,2,3,5,0,0]]),
 3:dict(labels=['North Quitman','Oakgrove','Pachuta','Rolling Creek','Shubuta','Snell','Souinlovie','South Quitman','Springs','Stonewall Dist. 3','Stonewall Dist. 1'],native=11,total=None,
 x=[693,812,931,1050,1169,1287,1406,1526,1643,1762,1880,1998],header_y=[280,512],row_y=[[1248,1310],[1310,1364],[1364,1419]],values=[
 [86,241,204,29,432,7,35,463,75,98,250],[253,36,91,186,78,160,164,271,63,330,88],[7,1,2,1,7,0,7,8,3,10,5]]),
 4:dict(labels=['Union','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[688,806,924,1042,1160,1280,1398,1516,1635,1753,1871,1989],header_y=[265,496],row_y=[[1234,1294],[1294,1350],[1350,1404]],
 row_window_status='Complete original physical header grid restores first two columns omitted by machine discovery; actualUnion followed byTOTALphysical2. Not a same-name/current precinct identity claim.',values=[[44,3053],[592,5169],[13,125]])}
VALUES['sos-2020-county-jefferson-davis']={
 2:dict(labels=['11-Granby','Bassfield 26','Bassfield Highway\n42 - 31','Carson 22','Clem 41','Good Hope/Melba 33',"Green's Creek 23",'Gwinville/Old\nHebron- 51','Mt Carmel 42','North East Prentiss\n43','North West Prentiss\n53'],ids=['11','26','42 - 31','22','41','33','23','51','42','43','53'],native=11,total=None,
 x=[687,807,926,1045,1163,1283,1403,1523,1641,1760,1880,1999],header_y=[250,488],row_y=[[1200,1420],[1200,1420],[1200,1420]],
 header_qualification='Original form heading literallyOfficialRecapitulation/Presidential and countyJeffDavis; selected lower office heading isUnitedStates-Senate. Printed numbers are retained as source substrings only; BassfieldHighway literally42 -31 has no assigned district/ID semantics.',
 row_window_status='Broad entire Senate-band original reading windows, not exact candidate polygons. Machine grid and named candidate locator failed; complete original directly supplies eleven physical columns and every candidate vector.',values=[
 [79,173,724,71,83,117,98,165,187,433,212],[49,174,197,148,83,220,199,87,17,184,57],[1,4,11,5,1,2,1,0,0,3,0]]),
 3:dict(labels=['Red House 55',"Son's\nAcademy/Hathorn 25",'South Prentiss 12','South Prentiss 13','Whiting 56','Williamson Mill 44','TOTAL','','','',''],ids=['55','25','12','13','56','44',None,None,None,None,None],native=6,total=7,
 x=[687,807,927,1046,1164,1284,1404,1524,1643,1762,1882,2001],header_y=[255,488],row_y=[[1200,1410],[1200,1410],[1200,1410]],
 row_window_status='Broad original Senate-band reading windows, not exact candidate polygons. Six constituents thenTOTALphysical7/four unused columns independently read from complete original.',values=[[261,240,259,287,247,122,3758],[89,180,311,161,48,196,2400],[1,7,2,3,1,2,44]])}
VALUES['sos-2020-county-jefferson-davis-amended']={
 2:dict(labels=['11-Granby','Bassfield 26','Bassfield Highway\n42 - 31','Carson 22','Clem 41','Good Hope/Melba 33',"Green's Creek 23",'Gwinville/Old\nHebron- 51','Mt Carmel 42','North East Prentiss\n43','North West Prentiss\n53'],ids=['11','26','42 - 31','22','41','33','23','51','42','43','53'],native=11,total=None,
 x=[657,770,884,998,1112,1224,1338,1453,1568,1681,1796,1910],header_y=[267,484],row_y=[[1178,1236],[1236,1288],[1288,1340]],
 header_qualification='Amended full original separately rendered/read; form headingPresidential, countyJeffDavis, lower selected officeUnitedStates-Senate. Fax12/01/2020TUE11:32 retained in full original, not assigned a publication chronology or timezone. Printed substrings have no current geographic identity claim.',values=[
 [79,173,724,71,83,117,98,165,187,433,212],[49,174,197,148,83,220,199,87,17,184,57],[1,4,11,5,1,2,1,0,0,3,0]]),
 3:dict(labels=['Red House 55',"Son's\nAcademy/Hathorn 25",'South Prentiss 12','South Prentiss 13','Whiting 56','Williamson Mill 44','TOTAL','','','',''],ids=['55','25','12','13','56','44',None,None,None,None,None],native=6,total=7,
 x=[662,776,890,1003,1116,1231,1344,1458,1574,1688,1802,1917],header_y=[274,491],row_y=[[1186,1244],[1244,1296],[1296,1348]],values=[[261,240,259,287,247,122,3758],[89,180,311,161,48,196,2400],[1,7,2,3,1,2,44]])}
VALUES['sos-2020-county-chickasaw']={
 2:dict(labels=['Anchor 001','Buena Vista 002','East Okolona 004','Egypt 003','North Houlka 005','North Okolona 006','Northwest Houston\n007','Pearsall 009','Pleasant Grove\nThorn 008','South Houlka 011','Southeast Houston\n010'],ids=['001','002','004','003','005','006','007','009','008','011','010'],native=11,total=None,
 x=[680,800,920,1040,1160,1279,1399,1518,1638,1758,1878,1997],header_y=[268,496],row_y=[[1236,1299],[1299,1354],[1354,1410]],values=[
 [166,411,689,236,213,284,713,80,96,147,296],[489,93,70,115,112,237,177,238,495,305,879],[8,7,2,2,3,6,8,9,15,11,25]]),
 3:dict(labels=['Sparta 012','Van Vleet 013','West Okolona 014','Woodland 015','TOTAL','','','','','',''],ids=['012','013','014','015',None,None,None,None,None,None,None],native=4,total=5,
 x=[681,801,921,1041,1161,1280,1400,1520,1640,1760,1880,2000],header_y=[270,499],row_y=[[1239,1301],[1301,1356],[1356,1412]],values=[[70,132,464,137,4134],[133,171,284,115,3913],[3,2,9,2,112]])}
VALUES['sos-2020-county-chickasaw-amended']={
 2:dict(labels=['Anchor 001','Buena Vista 002','East Okolona 004','Egypt 003','North Houlka 005','North Okolona 006','Northwest Houston\n007','Pearsall 009','Pleasant Grove\nThorn 008','South Houlka 011','Southeast Houston\n010'],ids=['001','002','004','003','005','006','007','009','008','011','010'],native=11,total=None,
 x=[700,819,939,1058,1178,1297,1416,1536,1655,1774,1894,2013],header_y=[276,504],row_y=[[1243,1305],[1305,1360],[1360,1416]],
 row_window_status='Amended complete original independently read; missing internal machine rules restored by actual full-page eleven-column header grid. Repeated candidate values do not establish publication chronology or native identity equivalence.',values=[
 [166,411,689,236,213,284,713,80,96,147,296],[489,93,70,115,112,237,177,238,495,305,879],[8,7,2,2,3,6,8,9,15,11,25]]),
 3:dict(labels=['Sparta 012','Van Vleet 013','West Okolona 014','Woodland 015','TOTAL','','','','','',''],ids=['012','013','014','015',None,None,None,None,None,None,None],native=4,total=5,
 x=[701,820,940,1060,1179,1299,1418,1537,1656,1775,1895,2014],header_y=[272,500],row_y=[[1240,1302],[1302,1358],[1358,1412]],values=[[70,132,464,137,4134],[133,171,284,115,3913],[3,2,9,2,112]])}
VALUES['sos-2020-county-kemper']={
 2:dict(labels=['Band Building','Courthouse','Damascus','Farmers Market','Fort Stevens','Kellis Store','Kemper Springs','LITTLE ROCK\nCOMMUNITY CENTER','Lynville','Mount Nebo','Porterville'],native=11,total=None,
 x=[724,844,962,1081,1200,1318,1436,1555,1672,1789,1906,2025],header_y=[282,512],row_y=[[1253,1315],[1315,1370],[1370,1426]],values=[
 [264,500,112,65,27,135,113,308,133,216,407],[123,157,241,47,116,25,14,193,180,107,106],[3,2,6,0,3,1,0,5,2,3,4]],
 header_reading_evidence=[dict(source_column=9,bounds=[1672,282,1789,512],rotate_ccw=-90,name='p0002-header-c09-original-upright.png',accepted_literal='Lynville',initial_manual_literal='Lynnville',correction_kind='literal_header_glyph_reread',supersedes_immutable_versions=['55views-v1','60views-v1','65views-v1'],basis='Fresh hash-checked whole original PDF2 and unchanged-pixel upright physical-column9 header read one n. Earlier immutable witnesses retain Lynnville. Candidate133/180/2, source key, raw/raster hashes and all bounds remain unchanged; no ID, geography or chronology inference.')]),
 3:dict(labels=['Preston','Scooba A-L','Scooba M-Z','TOTAL','','','','','','',''],native=3,total=4,
 x=[738,858,976,1094,1214,1332,1450,1568,1685,1802,1920,2038],header_y=[284,514],row_y=[[1255,1317],[1317,1373],[1373,1428]],values=[[230,252,203,2965],[170,119,122,1720],[3,4,4,40]])}
VALUES['sos-2020-county-jasper']={
 2:dict(labels=['Antioch','Bay Springs Beat 3','Bay Springs Beat 4','Claiborne','Fellowship','Heidelberg','Holders','Louin','Midway','Montrose','Moss'],native=11,total=None,
 x=[687,807,926,1046,1166,1286,1407,1527,1646,1764,1884,2004],header_y=[260,492],row_y=[[1230,1420],[1230,1420],[1230,1420]],
 row_window_status='Broad complete original Senate-band reading windows, not exact candidate polygons; faint original machine grid/row locator failed. Each actual eleven-column vector directly read from complete original.',values=[
 [41,483,423,294,11,856,261,326,164,149,179],[233,353,334,170,86,126,254,250,113,153,540],[7,7,7,10,1,4,6,10,2,5,13]]),
 3:dict(labels=['Palestine','Paulding','Philadelphia','Rose Hill','Stringer','Vossburg','TOTAL','','','',''],native=6,total=7,
 x=[694,814,934,1054,1173,1292,1412,1532,1650,1768,1887,2006],header_y=[260,491],row_y=[[1220,1410],[1220,1410],[1220,1410]],
 row_window_status='Broad complete original Senate-band reading windows, not exact candidate polygons. Six actual source constituents thenTOTALphysical7; four unused template columns are null.',values=[[73,577,251,161,109,198,4556],[11,251,64,204,945,15,4102],[1,3,2,0,13,1,92]])}
VALUES['sos-2020-county-jasper-amended']={
 2:dict(labels=['Antioch','Bay Springs Beat 3','Bay Springs Beat 4','Claiborne','Fellowship','Heidelberg','Holders','Louin','Midway','Montrose','Moss'],native=11,total=None,
 x=[688,808,928,1048,1168,1288,1408,1528,1647,1765,1884,2003],header_y=[250,486],row_y=[[1220,1415],[1220,1415],[1220,1415]],
 row_window_status='Broad amended original Senate-band windows, not exact candidate polygons. Amended complete raster separately reviewed despite matching candidate vectors; no copy from original publication or county residual allocation.',values=[
 [41,483,423,294,11,856,261,326,164,149,179],[233,353,334,170,86,126,254,250,113,153,540],[7,7,7,10,1,4,6,10,2,5,13]]),
 3:dict(labels=['Palestine','Paulding','Philadelphia','Rose Hill','Stringer','Vossburg','TOTAL','','','',''],native=6,total=7,
 x=[690,810,930,1049,1169,1289,1409,1528,1647,1765,1883,2001],header_y=[260,491],row_y=[[1220,1420],[1220,1420],[1220,1420]],
 row_window_status='Broad complete amended original Senate-band reading windows, not exact polygons. Source-specific seventeen constituents, oneTOTAL/fourunused retained independently.',values=[[73,577,251,161,109,198,4556],[11,251,64,204,945,15,4102],[1,3,2,0,13,1,92]])}
VALUES['sos-2020-county-leake']={
 2:dict(labels=['Conway','East Carthage','Edinburg','Freeny','Good Hope','HARMONY','Lena','Madden','North Carthage','Ofahoma','Renfroe'],native=11,total=None,
 x=[682,802,922,1041,1160,1280,1400,1520,1638,1756,1874,1994],header_y=[248,483],row_y=[[1226,1288],[1288,1343],[1343,1399]],values=[
 [290,192,26,114,132,208,213,91,349,279,83],[116,463,397,429,418,118,180,354,359,48,273],[4,6,2,5,6,1,2,5,15,2,6]]),
 3:dict(labels=['Salem','Singleton','South Carthage','Sunrise','Thomastown','Walnut Grove','West Carthage','Wiggins','TOTAL','',''],native=8,total=9,
 x=[682,804,924,1042,1162,1282,1402,1522,1640,1758,1876,1994],header_y=[250,485],row_y=[[1228,1290],[1290,1346],[1346,1401]],values=[[60,186,114,31,241,580,662,272,4123],[290,424,226,336,158,170,126,106,4991],[2,12,3,4,3,3,7,4,92]])}
VALUES['sos-2020-county-winston']={
 2:dict(labels=['American Legion','County Agent','East Winston','Fairground','Lovorn Tractor','Mars Hill','Mill Creek','Nanih Waiya','New National Guard','Noxapater','Shiloh'],native=11,total=None,
 x=[697,816,935,1055,1174,1293,1413,1532,1649,1767,1885,2003],header_y=[256,488],row_y=[[1228,1290],[1290,1343],[1343,1400]],values=[
 [715,761,174,665,190,274,435,210,97,271,98],[96,153,423,972,219,350,688,883,252,482,277],[6,5,8,29,4,7,8,14,11,16,5]]),
 3:dict(labels=['Zion Ridge','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[703,822,941,1060,1180,1299,1418,1537,1655,1773,1891,2007],header_y=[264,498],row_y=[[1236,1297],[1297,1352],[1352,1408]],values=[[413,4303],[51,4846],[1,114]])}
VALUES['sos-2020-county-lafayette']={
 2:dict(labels=['Abbeville','Airport Grocery','Anchor-Taylor 4','Burgess','College Hill','Denmark-Laf\nSprings-Pine Bluff','Harmontown','Oxford 1','Oxford 2','Oxford 3','Oxford 4'],native=11,total=None,
 x=[684,804,922,1042,1162,1282,1402,1522,1640,1756,1872,1990],header_y=[260,493],row_y=[[1234,1296],[1296,1351],[1351,1406]],values=[
 [587,195,113,152,856,91,71,1324,2532,1340,1666],[393,442,450,320,972,465,380,1629,2380,937,1437],[15,16,11,10,40,12,21,34,75,29,58]]),
 3:dict(labels=['Oxford 5','Paris','Philadelphia','Taylor 3','Tula','Union West 4','Yocona Community\nCenter','TOTAL','','',''],native=7,total=8,
 x=[687,806,924,1044,1164,1284,1402,1522,1641,1758,1874,1992],header_y=[260,492],row_y=[[1232,1294],[1294,1349],[1349,1404]],
 row_window_status='Complete original named Senate rows directly read. Machine MikeEspy locator targeted the presidential office heading; rejected. Actual lower Senate row/rules independently located on original.',values=[[1014,36,103,426,52,90,158,10806],[704,261,134,186,266,211,560,12127],[49,8,5,8,9,6,26,432]])}
VALUES['sos-2020-county-lafayette-amended']={
 2:dict(labels=['Abbeville','Airport Grocery','Anchor-Taylor 4','Burgess','College Hill','Denmark-Laf\nSprings-Pine Bluff','Harmontown','Oxford 1','Oxford 2','Oxford 3','Oxford 4'],native=11,total=None,
 x=[664,782,900,1020,1136,1256,1376,1495,1614,1732,1850,1972],header_y=[262,492],row_y=[[1230,1291],[1291,1346],[1346,1401]],values=[
 [587,195,113,152,856,91,71,1324,2532,1340,1666],[393,442,450,320,972,465,380,1629,2380,937,1437],[15,16,11,10,40,12,21,34,75,29,58]]),
 3:dict(labels=['Oxford 5','Paris','Philadelphia','Taylor 3','Tula','Union West 4','Yocona Community\nCenter','TOTAL','','',''],native=7,total=8,
 x=[668,786,904,1024,1141,1260,1380,1498,1618,1736,1853,1974],header_y=[276,504],row_y=[[1240,1301],[1301,1356],[1356,1412]],values=[[1014,36,103,426,52,90,158,10806],[704,261,134,186,266,211,560,12127],[49,8,5,8,9,6,26,432]])}
VALUES['sos-2020-county-newton']={
 2:dict(labels=['Chunky','Conehatta','Decatur #1','Decatur #2','Decatur #3/Scanlan','Duffee','Hickory','Lawrence','Little Rock','Newton #1','Newton #4'],native=11,total=None,
 x=[686,808,929,1050,1174,1294,1416,1538,1658,1779,1900,2020],header_y=[252,478],row_y=[[1202,1261],[1261,1316],[1316,1369]],values=[
 [43,161,214,101,142,58,361,370,50,715,455],[390,288,393,397,475,494,853,600,681,57,511],[11,13,7,12,7,14,17,19,17,4,24]]),
 3:dict(labels=['Newton #5','Prospect','Union #1','Union #2','Union #3','TOTAL','','','','',''],native=5,total=6,
 x=[686,808,929,1051,1173,1294,1416,1538,1658,1779,1900,2019],header_y=[256,481],row_y=[[1205,1266],[1266,1319],[1319,1374]],
 row_window_status='Complete original five native constituents thenTOTALphysical6. Machine omitted internal grid rule and proposedTOTAL5; old locator retained unaccepted. Extra2019..2130machine band is right outer paper, not a twelfth printed column.',values=[[245,28,200,72,75,3290],[279,370,126,448,297,6659],[2,9,3,10,7,176]])}
VALUES['sos-2020-county-simpson']={
 2:dict(labels=['Bowie','Braxton','Bridgeport',"D'Lo",'Dry Creek','Fork Church','Harrisville','Jupiter','Magee 1','Magee 2','Magee 4 North'],native=11,total=None,
 x=[692,811,930,1051,1172,1290,1411,1530,1650,1768,1886,2005],header_y=[258,491],row_y=[[1233,1294],[1294,1350],[1350,1406]],values=[
 [102,72,226,44,64,252,99,416,459,252,95],[174,624,116,248,448,101,548,140,82,803,369],[3,11,0,3,7,2,10,4,4,11,8]]),
 3:dict(labels=['Magee 4 South','Mendenhall 1','Mendenhall 3','Merit','New Hope','Oak Grove','Pearl','Pinola','Saratoga','Shivers','Sumrall'],native=11,total=None,
 x=[688,808,926,1048,1166,1286,1406,1525,1644,1762,1881,2000],header_y=[253,486],row_y=[[1230,1292],[1292,1347],[1347,1402]],values=[
 [204,183,187,70,115,282,98,102,136,166,96],[604,83,697,541,134,283,360,223,126,204,331],[14,1,21,13,2,6,7,2,0,2,6]]),
 4:dict(labels=['Weathersby','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[692,811,930,1050,1170,1288,1408,1528,1646,1765,1883,2002],header_y=[256,489],row_y=[[1232,1294],[1294,1350],[1350,1406]],values=[[583,4303],[142,7381],[1,138]])}
VALUES['sos-2020-county-george']={
 2:dict(labels=['Rocky Creek','Multi Mart','Ward','Shipman','Courthouse','Pine Level','Agricola','Howell','Movella','Multi-Purpose','Basin'],native=11,total=None,
 x=[684,803,923,1042,1161,1280,1399,1518,1636,1755,1874,1993],header_y=[269,500],row_y=[[1238,1301],[1301,1356],[1356,1410]],values=[
 [156,48,33,52,37,60,104,36,26,41,223],[1115,216,288,290,189,407,745,368,347,157,813],[29,8,2,3,7,13,22,12,13,2,17]]),
 3:dict(labels=['Davis','Barton','City Hall','Shady Grove','Bexley','Salem','Middle School','Central','Benndale','Broome','Twin Creek'],native=11,total=None,
 x=[680,799,918,1037,1156,1275,1394,1513,1632,1750,1869,1987],header_y=[268,498],row_y=[[1237,1298],[1298,1356],[1356,1409]],values=[
 [44,121,135,89,126,21,234,39,141,15,63],[310,651,606,616,304,84,277,190,436,168,234],[12,15,18,25,12,0,15,8,12,6,9]]),
 4:dict(labels=['TOTAL','','','','','','','','','',''],native=0,total=1,
 x=[675,795,914,1033,1152,1271,1390,1508,1626,1745,1863,1982],header_y=[261,490],row_y=[[1220,1420],[1220,1420],[1220,1420]],
 row_window_status='Broad complete original Senate-band windows, not exact candidate polygons. This page printsTOTALphysical1 only and ten unprinted template slots; no native unit or zero is fabricated from them.',values=[[1844],[8811],[260]])}
VALUES['sos-2020-county-jackson']={
 2:dict(labels=['Big Point','Carterville','East Central','Eastlawn','Escatawpa','Fair','Fontainebleau','Gautier','Grace Baptist Church','Gulf Park Estates','Hickory Hills'],native=11,total=None,
 x=[692,812,932,1052,1170,1292,1412,1532,1650,1768,1886,2005],header_y=[244,481],row_y=[[1225,1286],[1286,1341],[1341,1396]],values=[
 [193,8,495,240,611,1531,1096,1928,800,753,658],[1434,129,3759,717,1468,738,2094,2231,1529,1437,1027],[57,2,74,31,36,36,111,94,72,64,38]]),
 3:dict(labels=['Hwy 57','Jefferson Street','Larue','Latimer','North Pascagoula','North Vancleave','OS Civic Ctr','OS Community Ctr','Orange Grove','Pinecrest','Presbyterian'],native=11,total=None,
 x=[692,812,932,1053,1172,1293,1414,1534,1652,1770,1887,2006],header_y=[244,478],row_y=[[1224,1285],[1285,1340],[1340,1395]],values=[
 [35,1206,36,510,96,337,1083,107,168,273,283],[359,348,226,1732,295,1349,1966,135,693,577,740],[12,14,9,86,10,49,90,4,18,24,17]]),
 4:dict(labels=['Rec Center','Red Hill','Ryan Youth Center','Sacred Heart','South Vancleave','St Martin','Sue Ellen','Villa Maria','West Jackson','YMBC-Dantzler','TOTAL'],native=10,total=11,
 x=[693,813,932,1053,1173,1294,1414,1534,1652,1770,1888,2006],header_y=[240,474],row_y=[[1219,1280],[1280,1334],[1334,1390]],values=[
 [979,24,538,475,289,756,1656,183,1232,755,19334],[164,271,1007,1005,1934,1501,55,292,1987,409,33608],[6,14,40,43,73,79,5,8,97,12,1325]])}
VALUES['sos-2020-county-hancock']={
 2:dict(labels=['Arlington','Bayou Philip','Catahoula','City Hall','Courthouse','Crane Creek','Dedeaux','Diamondhead East','Diamondhead West','Edwardsville','Fenton'],native=11,total=None,
 x=[674,793,912,1031,1150,1269,1388,1507,1626,1745,1864,1983],header_y=[258,490],row_y=[[1220,1415],[1220,1415],[1220,1415]],
 row_window_status='Broad complete original Senate-band reading windows, not exact numeric polygons. Faint source has no accepted machine rule/row detection; eleven physical headers and three candidate vectors directly read from whole raster.',values=[
 [119,121,22,490,71,105,85,880,358,91,124],[255,144,124,173,140,700,474,2545,967,420,645],[14,6,7,8,0,38,18,62,44,20,24]]),
 3:dict(labels=['Flat Top','Garden Isle','Kiln East','Kiln West','Lakeshore','Lee Town','North Bay East','North Bay West','Pearlington','South Bay','Standard'],native=11,total=None,
 x=[680,799,918,1037,1156,1275,1394,1513,1632,1751,1870,1989],header_y=[268,500],row_y=[[1225,1420],[1225,1420],[1225,1420]],
 row_window_status='Broad complete original Senate-band windows only, not exact numeric polygons; no source-native absence/zero inferred from failed machine detection.',values=[
 [105,139,85,151,323,132,298,264,229,418,141],[602,385,487,586,915,669,303,608,328,710,761],[21,16,15,24,45,22,11,33,24,20,26]]),
 4:dict(labels=['Waveland East','Waveland West','West Shoreline Park','TOTAL','','','','','','',''],native=3,total=4,
 x=[675,794,913,1032,1151,1270,1389,1508,1627,1746,1865,1984],header_y=[258,490],row_y=[[1220,1415],[1220,1415],[1220,1415]],
 row_window_status='Broad original Senate-band windows, not exact polygons. Three actual constituents thenTOTALphysical4; seven unused blank template columns retained as null, not zero.',values=[[379,408,113,5651],[595,752,249,14537],[25,37,13,573]])}
VALUES['sos-2020-county-lee']={
 2:dict(labels=['Auburn','Baldwyn','Beech Springs','Belden','Birmingham Ridge','Bissell','Brewer','Cedar Hill','Eggville','Euclatubba','Fellowship'],native=11,total=None,
 x=[687,808,926,1046,1164,1284,1406,1524,1644,1760,1878,1996],header_y=[272,501],row_y=[[1244,1305],[1305,1360],[1360,1416]],values=[
 [152,357,219,650,248,1163,66,312,39,31,93],[918,327,314,1142,1104,2896,317,1132,408,250,419],[36,4,8,31,35,80,4,34,7,7,15]],
 header_reading_evidence=[dict(source_column=10,bounds=[1750,260,1882,505],rotate_ccw=-90,name='p0002-header-c10-reading.png',accepted_literal='Euclatubba',basis='Complete original header additionally enlarged/rotated for literal lettering; no name gazetteer or2024label substitution.')]),
 3:dict(labels=['Friendship','Gilvo','Guntown','Hebron','Kedron','Mooreville','Nettleton','Old Union','Palmetto','Petersburg','Plantersville'],native=11,total=None,
 x=[688,807,928,1048,1168,1288,1408,1529,1648,1764,1882,2000],header_y=[264,495],row_y=[[1242,1304],[1304,1358],[1358,1414]],values=[
 [15,26,246,38,144,188,140,184,364,34,428],[171,119,536,311,327,1225,554,214,411,238,349],[0,6,32,9,10,39,17,10,14,4,9]]),
 4:dict(labels=['Pleasant Grove','Pratts','Richmond','Saltillo','Shannon','Tupelo 1','Tupelo 2','Tupelo 3','Tupelo 4 North','Tupelo 4 South','Tupelo 5'],native=11,total=None,
 x=[690,808,926,1044,1163,1282,1402,1520,1640,1755,1872,1988],header_y=[280,516],row_y=[[1249,1311],[1311,1366],[1366,1421]],values=[
 [522,36,74,544,340,115,1077,1226,1450,1194,460],[267,281,312,1677,221,426,1535,1627,318,122,294],[9,3,13,44,4,12,70,54,26,10,16]]),
 5:dict(labels=['Unity','Verona','Veterans Park','TOTAL','','','','','','',''],native=3,total=4,
 x=[677,797,916,1035,1154,1274,1394,1514,1632,1750,1866,1984],header_y=[260,492],row_y=[[1230,1291],[1291,1346],[1346,1402]],values=[[47,654,496,13372],[424,323,1230,22739],[18,12,43,745]])}
VALUES['sos-2020-county-jones']={
 2:dict(labels=['ANTIOCH','BIG CREEK','BLACKWELL','CALHOUN','CENTERVILLE','CURRIE','ERATA','FIRST ASSEMBLY OF\nGOD','GEORGE HARRISON','GITANO','GLADE'],native=11,total=None,
 x=[680,799,918,1037,1156,1276,1394,1514,1632,1750,1868,1987],header_y=[260,490],row_y=[[1236,1298],[1298,1354],[1354,1408]],values=[
 [42,28,16,136,16,175,235,349,414,66,76],[330,418,282,1319,157,26,150,345,921,172,772],[10,6,14,42,4,3,5,12,37,6,22]]),
 3:dict(labels=['HEBRON','JOHNSON','L T ELLIS CENTER','LANDRUM','MAGNOLIA CENTER','MATTHEWS','MOSELLE','MYRICK','NORTH LAUREL','OAK PARK SCHOOL','OVETT'],native=11,total=None,
 x=[683,802,920,1040,1158,1278,1396,1516,1634,1752,1870,1990],header_y=[254,485],row_y=[[1230,1292],[1292,1347],[1347,1403]],values=[
 [363,48,1279,31,1227,48,221,87,964,634,69],[198,494,30,330,272,388,703,934,1083,8,595],[6,24,5,6,13,10,33,31,24,1,24]]),
 4:dict(labels=['PARKVIEW BAPTIST\nCHURCH','PINE GROVE','PLEASANT RIDGE','POWERS','RAINEY','RUSTIN','SAND HILL','SANDERSVILLE','SHADY GROVE','SHARON','SHELTON'],native=11,total=None,
 x=[692,812,930,1050,1170,1288,1406,1526,1644,1762,1878,1998],header_y=[264,496],row_y=[[1242,1304],[1304,1358],[1358,1414]],values=[
 [419,65,52,240,71,38,78,142,672,198,193],[380,693,487,702,846,499,640,487,1336,879,406],[14,28,12,25,18,12,11,14,47,37,10]]),
 5:dict(labels=['SOSO','SPRINGHILL/\nMAULDIN','TUCKERS','UNION','TOTAL','','','','','',''],native=4,total=5,
 x=[682,802,921,1040,1159,1278,1397,1517,1634,1753,1871,1990],header_y=[258,490],row_y=[[1232,1292],[1292,1348],[1348,1404]],values=[[374,223,73,60,9422],[475,857,642,661,19917],[15,12,29,19,641]])}
VALUES['sos-2020-county-desoto']={
 2:dict(labels=['Alphaba-Cockrum',"Baker's Chapel",'Bridgetown','Colonial Hills','Cumberland','Desoto Central','Elmore','Eudora','Fairhaven','Greenbrook North','Greenbrook South'],native=11,total=None,
 x=[943,1040,1136,1232,1328,1426,1522,1618,1713,1808,1904,2000],header_y=[380,555],row_y=[[1140,1188],[1188,1232],[1232,1275]],header_rule_probe=dict(x_range=[900,2050],y_range=[380,555],dark_threshold=225,minimum_dark_fraction=.65),values=[
 [147,175,488,331,1060,1028,926,306,888,1607,1337],[949,655,1564,495,615,1630,1014,991,850,930,1620],[41,25,72,28,43,69,35,47,28,51,76]],
 numeric_correction_history=[dict(candidate='Mike Espy',source_column=5,label_literal='Cumberland',initial_manual_reading=1050,accepted_original_reading=1060,basis='Initial manually typed vector was ten below printedTOTAL. Enlarged complete original three-Senate-row strip visibly prints1060 at Cumberland; original glyph supplies correction, not residual allocation.',evidence_crop_bounds=[500,1125,2010,1285],evidence_crop_name='p0002-complete-senate-rows-original.png')]),
 3:dict(labels=['Hacks Cross Road','Hernando Central','Hernando East','Hernando West','Horn Lake Central','Horn Lake East','Horn Lake High\nSchool','Horn Lake\nIntermediate','Horn Lake North','Horn Lake West','Ingrams Mill'],native=11,total=None,
 x=[946,1042,1140,1236,1332,1428,1525,1620,1716,1812,1908,2004],header_y=[395,565],row_y=[[1151,1199],[1199,1242],[1242,1286]],header_rule_probe=dict(x_range=[900,2050],y_range=[395,565],dark_threshold=225,minimum_dark_fraction=.65),values=[
 [853,639,932,902,722,756,694,907,924,738,349],[916,1745,3098,2355,521,338,1056,568,433,369,887],[59,85,118,90,22,20,34,47,23,37,20]]),
 4:dict(labels=['Lake Cormorant','Lewisburg','Lewisburg East','Love','Miller','Mineral Wells','Nesbit East','Nesbit West','Northwest\nCommunity College','Olive Branch East','Olive Branch North'],native=11,total=None,
 x=[942,1038,1134,1230,1327,1424,1520,1615,1710,1808,1902,1998],header_y=[382,555],row_y=[[1142,1190],[1190,1232],[1232,1276]],header_rule_probe=dict(x_range=[900,2050],y_range=[382,555],dark_threshold=225,minimum_dark_fraction=.65),values=[
 [169,1032,88,232,774,1175,812,423,1191,830,988],[339,2241,384,1085,1190,1234,1213,948,862,704,985],[13,59,11,35,45,37,41,30,39,29,32]]),
 5:dict(labels=['Olive Branch South','Olive Branch West','Pleasant Hill North','Southaven North','Southaven South','Southaven West','Summershill','Walls','TOTAL','',''],native=8,total=9,
 x=[944,1040,1136,1233,1330,1424,1522,1618,1713,1809,1904,2000],header_y=[380,550],row_y=[[1136,1184],[1184,1227],[1227,1270]],header_rule_probe=dict(x_range=[900,2050],y_range=[380,550],dark_threshold=225,minimum_dark_fraction=.65),values=[
 [922,415,1014,773,623,1040,935,970,31115],[1644,516,1960,1021,165,637,1538,906,43171],[73,12,62,58,18,27,44,33,1768]])}
VALUES['sos-2020-county-washington']={
 2:dict(labels=['Arcola Technology\nCenter','Buster Brown\nCommunity Center','Covenant\nPresbyterian Church','Darlove','Elks Lodge','Extension Building','Glen Allan Library','Hollandale City Hall',"Jake's Chapel MB\nChurch",'Lake Vista Masonic\nLodge','Leland Health\nDepartment'],native=11,total=None,
 x=[694,816,936,1057,1177,1299,1418,1538,1658,1777,1896,2017],header_y=[294,528],row_y=[[1270,1465],[1270,1465],[1270,1465]],
 row_window_status='Broad complete original Senate-band reading windows only, not exact numeric polygons. Machine named-row discovery omitted Senate rows; all eleven physical headers and three vectors read directly from full original.',values=[
 [274,1475,384,27,1852,478,194,847,946,797,861],[170,290,741,40,66,17,249,186,9,241,428],[0,10,11,0,10,0,2,5,2,7,11]]),
 3:dict(labels=['Leland Rotary Club','Metcalfe Municipal\nBuilding','Mount Bethel Baptist\nChurch','St. James Episcopal\nChurch','Swiftwater Baptist\nChurch','Tampa Drive',"Ward's Recreation\nCenter",'Washington County\nConvention Center','TOTAL','',''],native=8,total=9,
 x=[696,816,938,1058,1179,1299,1419,1540,1658,1777,1896,2016],header_y=[286,520],row_y=[[1270,1465],[1270,1465],[1270,1465]],
 row_window_status='Broad original Senate-band windows, not exact numeric polygons. Eight constituents andTOTALphysical9/twounused; machine extra2016..2132band is outer paper, not a printed column.',values=[[643,411,519,1384,116,307,975,665,13155],[400,10,9,517,587,81,653,197,4891],[8,1,6,10,7,3,12,4,109]])}
VALUES['sos-2020-county-washington-amended']={
 2:dict(labels=['Arcola Technology\nCenter','Buster Brown\nCommunity Center','Covenant\nPresbyterian Church','Darlove','Elks Lodge','Extension Building','Glen Allan Library','Hollandale City Hall',"Jake's Chapel MB\nChurch",'Lake Vista Masonic\nLodge','Leland Health\nDepartment'],native=11,total=None,
 x=[709,828,949,1069,1190,1309,1429,1550,1672,1791,1913,2036],header_y=[263,497],row_y=[[1242,1304],[1304,1360],[1360,1416]],values=[
 [274,1475,384,27,1852,478,194,847,946,797,861],[170,290,741,40,66,17,249,186,9,241,428],[0,10,11,0,10,0,2,5,2,7,11]]),
 3:dict(labels=['Leland Rotary Club','Metcalfe Municipal\nBuilding','Mount Bethel Baptist\nChurch','St. James Episcopal\nChurch','Swiftwater Baptist\nChurch','Tampa Drive',"Ward's Recreation\nCenter",'Washington County\nConvention Center','TOTAL','',''],native=8,total=9,
 x=[680,801,922,1042,1162,1282,1403,1524,1644,1765,1886,2009],header_y=[276,510],row_y=[[1258,1320],[1320,1376],[1376,1432]],
 row_window_status='Complete amended original physical review restores first and two internal columns missed by machine locator. TOTAL is physical9, not earlier unaccepted proposal7. Original amended stamp/full bytes retained without release chronology or identity inference.',values=[[643,411,519,1384,116,307,975,665,13155],[400,10,9,517,587,81,653,197,4891],[8,1,6,10,7,3,12,4,109]])}
VALUES['sos-2020-county-forrest']={
 2:dict(labels=['Bar Mac','Brooklyn','Camp','Carnes','Court Street','Dantzler','Dixie','Dixie Pine Central','Eatonville','Eureka School','Glendale'],native=11,total=None,
 x=[694,808,921,1034,1148,1262,1376,1488,1600,1712,1822,1932],header_y=[294,514],row_y=[[1210,1395],[1210,1395],[1210,1395]],row_window_status='Broad whole Senate-band original reading windows, not exact candidate polygons. All physical headers and three named vectors read directly on complete original PDF2.',values=[
 [421,47,357,67,447,57,197,751,215,388,742],[1680,445,206,657,67,482,1033,184,538,8,250],[68,10,19,24,3,9,41,13,10,3,11]]),
 3:dict(labels=['Hardy Street','Hattiesburg Cultural\nCenter','Highland Park','Leeville','Lillie Burney','Maxie','Mclaurin','North Heights','Petal Civic Center','Petal Masonic','Pinecrest'],native=11,total=None,
 x=[692,807,920,1034,1148,1261,1374,1488,1600,1710,1822,1932],header_y=[298,520],row_y=[[1215,1395],[1215,1395],[1215,1395]],row_window_status='Broad complete original Senate-band reading windows, not exact numeric polygons; printed Mclaurin lettering retained without gazetteer normalization.',values=[
 [700,618,657,190,1539,49,63,808,369,295,824],[385,39,191,1016,51,141,309,80,907,813,365],[39,5,11,25,14,6,6,6,58,43,28]]),
 4:dict(labels=['Rawls Springs','Richburg','Rowan','Sheeplo','Sigler Center','Sunrise','Thames','Timberton','Train Depot','West Hills','West Petal'],native=11,total=None,
 x=[686,800,914,1028,1142,1255,1368,1482,1594,1704,1815,1926],header_y=[300,520],row_y=[[1215,1395],[1215,1395],[1215,1395]],row_window_status='Broad complete original Senate-band reading windows, not exact candidate polygons; machine named Senate-row locator failed. Full original numeric rows separately read.',values=[
 [473,201,527,294,760,491,696,255,325,283,252],[454,352,6,524,161,1916,1124,692,41,336,323],[13,12,1,9,17,66,41,18,7,17,24]]),
 5:dict(labels=['Westside','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[689,802,916,1030,1144,1257,1370,1483,1596,1706,1816,1928],header_y=[301,520],row_y=[[1229,1287],[1287,1338],[1338,1390]],values=[[513,14871],[303,16079],[18,695]])}
VALUES['sos-2020-county-madison']={
 2:dict(labels=['Camden Community\nCenter','Cameron Bethel M. B.\nChurch','Canton Anderson\nLodge','Canton Bible Church','Canton Community\nCenter','Canton Fire Station\n#4','Canton National\nGuard Armory','Canton South Liberty\nBaptist Church','Canton St. Paul\nMethodist Church','Cedar Grove Baptist\nChurch','China Grove A.M.E.\nChurch'],native=11,total=None,
 x=[670,791,910,1030,1150,1270,1390,1510,1628,1746,1865,1984],header_y=[273,498],row_y=[[1224,1284],[1284,1338],[1338,1392]],values=[
 [648,73,1010,374,1262,279,153,913,160,16,430],[88,77,13,5,136,94,90,498,2,133,1120],[3,2,6,1,8,4,5,7,2,3,22]]),
 3:dict(labels=['Colonial Heights\nBaptist Church','Couparle United\nMethodist Church','Fairview MB Church','Farmhaven Fire\nStation','Fearns Chapel\nFreewill Baptist','Fellowship Bible\nChurch','First Presbyterian\nMadison','Franklin Baptist\nChurch','Gluckstadt @ St Joe\nCatholic','Greater Mt Levi Full\nGospel','Highland Colony\nBaptist Church'],native=11,total=None,
 x=[674,796,915,1035,1154,1274,1394,1515,1634,1752,1871,1990],header_y=[286,511],row_y=[[1235,1296],[1296,1350],[1350,1404]],values=[
 [712,34,1330,663,424,608,538,24,1065,481,1292],[374,16,1779,91,827,287,1326,272,1989,8,2272],[21,0,56,6,15,7,35,0,50,3,39]]),
 4:dict(labels=['Jimmie M. Goodloe\nElem School','Lake Caroline\nClubhouse','Mad.Co.Baptist\nFamily Life Ct.','Magnolia Heights','Mark Apartments','Mt. Hope M. B.\nChurch','New Life Baptist\nChurch','Northbay Bayview\nClubhouse','Parkway Pentecostal\nChurch','Pilgrim Rest MB\nChurch','Pleasant Gift Baptist\nChurch'],native=11,total=None,
 x=[676,798,918,1036,1156,1276,1396,1516,1634,1752,1871,1990],header_y=[263,509],row_y=[[1234,1295],[1295,1349],[1349,1404]],values=[
 [896,510,675,706,1623,61,425,236,1056,852,429],[230,2362,9,264,430,289,1438,586,2587,1699,326],[8,44,3,10,33,5,29,20,55,48,8]]),
 5:dict(labels=['Pleasant Green M.B.\nChurch',"Ridgel'D 1st\nMethodist Church",'Ridgeland Recreation\nCenter','Sunnybrook\nRetirement Village','Tougaloo','Trace Ridge Baptist\nChurch','Twin Lakes Baptist\nChurch','Vertical Church','Victory Baptist\nChurch','Victory Christian\nCommunity','TOTAL'],native=10,total=11,
 x=[678,798,918,1037,1156,1275,1396,1517,1635,1752,1872,1989],header_y=[286,510],row_y=[[1236,1296],[1296,1350],[1350,1405]],row_window_status='Complete original named Senate rows read below presidential fields; machine MikeEspy locator incorrectly targeted a presidential row on this page. Actual physicalTOTALcolumn11, no unused printed columns.',values=[
 [542,800,845,182,92,890,540,754,305,466,25374],[73,811,1423,387,0,961,731,1714,830,1391,30038],[3,27,49,11,0,35,14,46,22,58,823]])}
VALUES['sos-2020-county-harrison']={
 2:dict(labels=['Advance','Bay Central','Bayou View','Biloxi # 11','Biloxi # 8','Biloxi 10','Biloxi Bay','Biloxi Central','County Farm/Gulf\nHaven','Delisle','E Orange Grove'],native=11,total=None,
 x=[677,791,904,1020,1135,1249,1364,1479,1593,1709,1822,1937],header_y=[235,468],row_y=[[1174,1234],[1234,1286],[1286,1340]],values=[
 [176,516,381,1251,307,678,492,532,433,576,1134],[873,893,1294,1745,463,771,484,548,1387,789,1196],[28,45,50,96,25,35,36,23,54,39,70]]),
 3:dict(labels=['E Pass Christian','East Biloxi','East Handsboro','East Long Beach','East Miss City','East North Gulfport','Gulfport # 13','Gulfport # 14','Gulfport # 16','Gulfport # 3','Gulfport # 4'],native=11,total=None,
 x=[674,790,904,1018,1132,1248,1362,1477,1592,1706,1820,1936],header_y=[240,466],row_y=[[1174,1234],[1234,1288],[1288,1340]],values=[
 [743,847,404,598,791,588,873,1019,647,383,129],[713,317,725,1268,1197,22,190,54,83,53,255],[36,12,35,68,68,5,17,12,3,4,15]]),
 4:dict(labels=['Gulfport # 5','Gulfport # 8','Howard Creek','Invalid Addresses\n9999','Ladner','Long Beach # 5','Long Beach # 6','Lyman','Magnolia Grove','Margaret Sherry','New Hope'],native=11,total=None,roles_by_column={4:'source_administrative_reporting_column'},ids=[None,None,None,'9999',None,None,None,None,None,None,None],
 x=[674,788,902,1017,1131,1246,1360,1475,1591,1706,1819,1934],header_y=[239,460],row_y=[[1168,1228],[1228,1282],[1282,1334]],row_window_status='Complete original physical column4 prints Invalid Addresses9999 and explicit0/0/0. Retained separately as administrative reporting column, not a precinct, unused blank or current ID; ten source-native constituents on this page.',values=[
 [328,630,675,0,196,475,302,1135,603,652,670],[326,218,2053,0,854,1303,815,2453,141,1289,730],[23,25,100,0,35,65,47,117,12,77,31]]),
 5:dict(labels=['New Popps Ferry','North Bay','North Bel-Aire','Outside Long Beach','Peace','Pineville','Poplar Head','Riceville','Saucier','South Bel-Aire','Stonewall'],native=11,total=None,
 x=[675,790,904,1019,1134,1248,1362,1478,1592,1706,1821,1935],header_y=[239,464],row_y=[[1172,1231],[1231,1284],[1284,1337]],header_rule_probe=dict(x_range=[660,1960],y_range=[260,450],dark_threshold=180,minimum_dark_fraction=.4),values=[
 [422,1595,1847,75,260,338,58,17,215,1008,574],[635,2569,962,317,1507,1170,328,185,1042,510,1005],[27,138,67,15,47,45,12,4,28,45,42]]),
 6:dict(labels=['Vidalia','W Pass Christian','West Handsboro','West Lizana','West Long Beach','West Mississippi City','West North Gpt','West Orange Grove','Westside','White Plains','TOTAL'],native=10,total=11,
 x=[676,792,905,1020,1135,1249,1364,1480,1593,1708,1822,1938],header_y=[238,460],row_y=[[1169,1228],[1228,1282],[1282,1334]],values=[
 [65,431,420,85,731,351,1080,1174,317,140,30367],[439,721,1215,559,1369,510,27,1593,364,651,43180],[15,30,38,22,103,38,4,75,24,25,2152]])}
VALUES['sos-2020-county-copiah']={
 2:dict(labels=['Beauregard','Carpenter','Centerpoint','Crystal Springs East','Crystal Springs North','Crystal Springs South','Crystal Springs West','Dentville','Gallman','Georgetown North','Georgetown South'],native=11,total=None,
 x=[678,794,910,1026,1141,1256,1372,1487,1602,1717,1832,1947],header_y=[276,495],row_y=[[1200,1261],[1261,1312],[1312,1366]],values=[
 [155,126,323,699,254,983,364,62,801,170,145],[428,51,520,1075,82,425,515,151,656,86,223],[7,0,6,26,4,6,10,4,15,3,3]]),
 3:dict(labels=['Hazlehurst East','Hazlehurst North','Hazlehurst South','Hazlehurst West','Martinsville','Shady Grove','Stronghope Union','Wesson','TOTAL','',''],native=8,total=9,
 x=[680,795,912,1027,1143,1259,1374,1490,1604,1718,1834,1949],header_y=[282,501],row_y=[[1206,1264],[1264,1316],[1316,1368]],row_window_status='Complete original eleven physical table columns; far-right fax/paper rule2093 is not a twelfth column. Eight constituents thenTOTALphysical9/twounused.',values=[[978,125,197,864,239,106,38,101,6730],[43,29,107,192,242,330,381,526,6062],[4,2,3,9,0,4,2,10,118]])}
VALUES['sos-2020-county-holmes']={
 2:dict(labels=['1 Acona','1 Durant St Anderson','Beat 1 Lexington','Beat 2 Durant','Beat 2 Sub Durant','Beat 2 West','Beat 3 Coxburg (A-Z)','Beat 3 Ebenezer (A-\nZ)','Beat 3 Goodman','Beat 3 Pickens','Beat 4 Lexington'],native=11,total=None,
 x=[697,816,937,1056,1176,1296,1414,1536,1652,1770,1888,2006],header_y=[274,508],row_y=[[1247,1308],[1308,1363],[1363,1419]],row_window_status='Full original candidate rows below Senate heading directly read. Machine locator incorrectly proposed a presidential office band for MikeEspy; prior aid unchanged. Beat prefixes retained as labels, not unique IDs.',values=[
 [465,218,844,388,412,287,51,205,455,584,1057],[38,20,115,124,44,126,118,64,60,63,121],[1,0,2,4,1,8,4,1,6,4,2]]),
 3:dict(labels=['Beat 4 Thornton (A-\nZ)','Beat 4 Walden\nChapel (A-Z','Beat 5 Cruger (A-Z)','Beat 5 Lexington (A-\nZ)','Beat 5 Tchula','TOTAL','','','','',''],native=5,total=6,
 x=[708,828,948,1068,1186,1306,1428,1547,1665,1784,1902,2022],header_y=[286,518],row_y=[[1259,1320],[1320,1376],[1376,1431]],row_window_status='Direct full original lower Senate rows, not failed machine presidential-row target. Literal bracket/wrap lettering retained without normalizing partition labels.',values=[[263,166,187,227,989,6798],[40,14,58,154,71,1230],[0,1,0,1,1,36]])}
VALUES['sos-2020-county-leflore']={
 2:dict(labels=['Central Gwd','East Gwd','Minter City','Money','Morgan City','Mvsu','Ne Gwd','North Gwd','North Itta Bena','Rising Sun','Schlater'],native=11,total=None,
 x=[699,816,934,1054,1172,1290,1410,1528,1647,1764,1882,2002],header_y=[260,492],row_y=[[1228,1289],[1289,1340],[1340,1395]],row_window_status='Complete original physical eleven-column table; machine2002..2124band is fax/page margin, not an extra source column.',values=[
 [253,1136,85,36,107,256,660,829,909,428,133],[52,12,102,92,60,19,92,1881,72,13,90],[7,6,0,3,0,1,4,25,1,2,1]]),
 3:dict(labels=['Sidon','South Gwd','South Itta Bena','Southeast Gwd','Southwest Gwd','Swiftown','West Gwd','TOTAL','','',''],native=7,total=8,
 x=[694,812,930,1049,1168,1286,1406,1524,1642,1760,1878,1998],header_y=[245,478],row_y=[[1214,1275],[1275,1328],[1328,1382]],values=[[170,310,270,1083,349,22,900,7936],[52,4,48,165,4,21,135,2914],[3,0,1,1,1,0,1,57]])}
VALUES['sos-2020-county-montgomery']={
 2:dict(labels=['DUCK HILL','EAST WINONA','KILMICHAEL','Lodi','Mt. Pisgah','NORTH DUCK HILL','NORTH KILMICHAEL','NORTH MT PISGAH\nSWEETHOME','NORTH WINONA','Nations','Poplar Creek'],native=11,total=None,source_status_literal='Unofficial Recapitulation',printed_footer_page_literal='Page : 1',
 x=[680,800,920,1040,1160,1280,1400,1522,1640,1760,1878,2000],header_y=[274,506],row_y=[[1245,1306],[1306,1362],[1362,1417]],values=[
 [219,326,221,141,18,105,68,53,173,32,8],[257,177,235,47,132,95,15,82,563,241,91],[5,7,5,2,4,1,0,2,20,5,4]]),
 3:dict(labels=['SOUTH WINONA','SOUTHEAST WINONA','Stewart','WEST WINONA','TOTAL','','','','','',''],native=4,total=5,source_status_literal='Unofficial Recapitulation',printed_footer_page_literal='Page : 2',
 x=[686,805,926,1046,1165,1286,1406,1526,1646,1765,1884,2006],header_y=[278,510],row_y=[[1248,1310],[1310,1364],[1364,1420]],row_window_status='Complete original PDF3 footerPage2. Printed UnofficialRecapitulation retained despite index/publication authority; four constituents thenTOTALphysical5/sixunused, not a different election or release chronology inference.',values=[[645,95,8,152,2264],[211,86,73,433,2738],[13,3,1,14,86]])}
VALUES['sos-2020-county-lowndes']={
 2:dict(labels=['Airbase','Artesia','Brandon','Caledonia','Coleman','Crawford','East Columbus Gym','Fifteenth Street\nChurch','First Assembly','Hunt','Immanuel'],native=11,total=None,
 x=[686,806,926,1046,1164,1285,1405,1524,1644,1762,1879,1997],header_y=[271,504],row_y=[[1242,1304],[1304,1358],[1358,1413]],row_window_status='Complete original physical eleven-column header grid restores one internal rule omitted by machine locator. Named candidate rows directly read from full original.',values=[
 [527,284,887,536,251,667,1439,578,1012,1301,290],[494,49,793,2339,6,165,517,93,1730,33,417],[15,0,27,79,0,5,20,3,39,7,16]]),
 3:dict(labels=['New Hope','Plum Grove','Rural Hill','Southside Church','Steens','Townsend Park','Trinity','University','West Lowndes','TOTAL',''],native=9,total=10,
 x=[693,812,932,1052,1171,1291,1410,1529,1647,1766,1884,2002],header_y=[268,500],row_y=[[1238,1300],[1300,1356],[1356,1410]],values=[[922,292,636,2069,83,803,624,349,293,13843],[2942,30,1306,346,436,70,186,305,753,13010],[60,1,31,18,7,1,9,16,15,369]])}
VALUES['sos-2020-county-rankin']={
 2:dict(labels=['Antioch-Mayton','Brandon Central','Brandon City Hall','Briar Hill','Castlewoods East','Castlewoods West','Cato','City Hall','Clear Branch','Cleary','Crest Park'],native=11,total=None,
 x=[696,815,934,1054,1174,1294,1414,1533,1651,1768,1885,2003],header_y=[247,482],row_y=[[1222,1284],[1284,1340],[1340,1394]],row_window_status='Original physical eleven-column header grid directly read; machine locator omitted first and several internal boundaries. Reading windows not exact numeric polygons.',values=[
 [76,355,1412,228,783,852,226,407,162,195,373],[397,1161,2697,441,1707,1632,681,828,534,1245,841],[6,36,77,18,54,61,21,39,21,34,41]]),
 3:dict(labels=['Crossroads','Cunningham Heights','Dry Creek','East Crossgates','East Steen Creek','Eldorado','Fannin','Flowood Library',"Grant's Ferry",'Greenfield','Highlands/Patrick\nFarms'],native=11,total=None,
 x=[698,818,938,1057,1177,1298,1418,1538,1655,1774,1891,2008],header_y=[250,488],row_y=[[1228,1290],[1290,1345],[1345,1400]],values=[
 [70,238,552,537,445,519,386,708,911,979,828],[492,468,640,2031,1537,1201,1347,1397,1730,1373,943],[18,18,19,72,55,42,33,61,77,48,24]]),
 4:dict(labels=['Johns','Lakeland','Leesburg','Liberty','Mountain Creek','North Brandon','North Mclaurin','North Richland','Northeast Brandon','Northshore','Oakdale'],native=11,total=None,
 x=[688,808,928,1048,1168,1288,1408,1528,1646,1764,1881,1999],header_y=[244,478],row_y=[[1222,1283],[1283,1338],[1338,1394]],values=[
 [138,276,45,591,93,756,173,356,574,497,747],[434,587,614,1445,339,1476,535,785,1739,1746,1781],[12,26,16,33,2,36,23,26,37,60,68]]),
 5:dict(labels=['Pelahatchie','Pisgah','Puckett','Reservoir East','Reservoir West','Shiloh','South Brandon','South Mclaurin','South Pearson','South Richland','Springhill'],native=11,total=None,
 x=[699,819,938,1060,1179,1300,1420,1540,1658,1776,1894,2013],header_y=[249,484],row_y=[[1229,1290],[1290,1346],[1346,1402]],values=[
 [435,249,123,324,394,92,123,243,694,581,184],[1105,583,476,1025,1118,202,673,621,141,1386,848],[37,18,3,45,66,6,32,32,6,62,22]]),
 6:dict(labels=['Star','West Crossgates','West Pearl','West Steen Creek','TOTAL','','','','','',''],native=4,total=5,
 x=[696,817,936,1056,1176,1296,1415,1536,1654,1772,1888,2007],header_y=[246,475],row_y=[[1216,1278],[1278,1334],[1334,1389]],row_window_status='Complete original four named constituents thenTOTALphysical5/sixunused, rather than earlier unaccepted merged-grid proposal4. Actual48native source constituents, no2024/current count or name join.',values=[[159,368,478,380,20315],[586,1121,572,1241,48502],[11,58,22,30,1664]])}
VALUES['sos-2020-county-tallahatchie']={
 2:dict(labels=['Blue Cane','Brazil','Cascilla','Charleston Beat #1','Charleston Beat #2','Charleston Beat #3','Enid','Glendora','Leverette','Murphreesbore','Paynes'],native=11,total=None,
 x=[702,822,942,1064,1182,1302,1420,1540,1660,1778,1898,2017],header_y=[248,491],row_y=[[1266,1330],[1330,1388],[1388,1446]],header_reading_evidence=[dict(source_column=10,bounds=[1778,248,1898,491],rotate_ccw=-90,name='p0002-c10-header-original-upright.png',accepted_literal='Murphreesbore',basis='Exact full-original unchanged-pixel upright header read final e, not a gazetteer spelling normalization.')],values=[
 [251,28,97,356,567,274,130,258,47,25,31],[55,19,240,204,234,148,202,7,39,156,131],[2,0,3,9,11,6,9,3,0,1,2]]),
 3:dict(labels=['Phillip','Rosebloom','Springhill','Sumner Beat #2','Sumner Beat #5','Teasdale','Tippo','Tutwiler','Webb Beat #4','Webb Beat #5','TOTAL'],native=10,total=11,
 x=[707,826,948,1066,1186,1304,1424,1546,1664,1784,1902,2020],header_y=[253,496],row_y=[[1272,1336],[1336,1392],[1392,1450]],values=[[103,7,24,66,100,76,59,455,86,276,3316],[53,122,143,113,30,233,84,39,23,34,2309],[1,1,3,1,0,4,2,3,1,2,64]])}
VALUES['sos-2020-county-tate']={
 2:dict(labels=['Arkabutla','Coldwater 3','Evansville','Independence','Looxahoma','Palestine','Poagville 4','Poagville 5','Sarah','Senatobia 1','Senatobia 2'],native=11,total=None,
 x=[691,810,929,1047,1166,1286,1405,1524,1641,1760,1878,1995],header_y=[258,486],row_y=[[1223,1282],[1282,1337],[1337,1392]],row_window_status='Original named Senate rows beneath printed PresidentialGeneralElection title. Physical eleven-column grid independently reviewed despite sparse machine header proposals.',values=[
 [254,790,56,493,380,45,160,98,21,729,404],[455,429,129,1075,483,281,600,186,157,1275,788],[19,26,2,33,13,3,20,1,4,24,25]]),
 3:dict(labels=['Senatobia 3','Senatobia 4','Sherrod','Strayhorn 1','Strayhorn 2','Taylor','Thyatira','Tyro','Wyatte','TOTAL',''],native=9,total=10,
 x=[680,798,917,1036,1154,1272,1393,1512,1630,1748,1865,1984],header_y=[252,479],row_y=[[1210,1268],[1268,1322],[1322,1378]],values=[[427,255,34,76,44,125,72,169,62,4694],[74,622,278,425,321,55,195,116,127,8071],[6,20,7,18,15,2,6,8,4,256]])}
VALUES['sos-2020-county-union']={
 2:dict(labels=['Macedonia','Blythe','Myrtle','Glenfield','Pinedale','West Union','Sportsplex','Ingomar',"King's Chapel",'Courthouse','Central Maintenance'],native=11,total=None,
 x=[699,818,936,1055,1173,1292,1410,1528,1645,1762,1879,1998],header_y=[280,510],row_y=[[1235,1425],[1235,1425],[1235,1425]],header_rule_probe=dict(x_range=[670,2030],y_range=[300,480],dark_threshold=225,minimum_dark_fraction=.4),row_window_status='Broad entire Senate-band original reading windows, not exact candidate polygons. Faint original machine grid/row locator returns no usable fields; all eleven actual headers and three candidate vectors directly read from full original. Source-specific header-only pixel proposals retain false lettering strokes separately.',values=[
 [26,33,193,206,35,60,314,159,76,256,123],[279,198,809,461,323,540,581,711,354,562,667],[17,14,39,30,32,27,28,24,19,21,31]]),
 3:dict(labels=['Beacon Hill','Blue Springs','Hillcrest Church','Center','Ellistown Baptist\nChurch','Watson Grove Baptist\nChurch','Keownville','Pleasant Ridge','Jericho','TOTAL',''],native=9,total=10,
 x=[696,814,933,1051,1170,1288,1407,1527,1644,1761,1877,1994],header_y=[280,510],row_y=[[1235,1425],[1235,1425],[1235,1425]],header_rule_probe=dict(x_range=[670,2030],y_range=[300,480],dark_threshold=225,minimum_dark_fraction=.4),row_window_status='Broad original Senate-band reading windows, not exact numeric polygons. Nine actual constituents thenTOTALphysical10/oneunused; no2024 vendor profile/name/current geometry join.',values=[[158,61,288,31,154,362,53,32,40,2660],[525,403,381,360,652,738,468,224,336,9572],[18,13,18,14,17,33,7,13,9,424]])}
VALUES['sos-2020-county-walthall']={
 2:dict(labels=['3rd District Tylertown','4th District West\nTylertown','4th District Tylertown','Darbun','Dexter','Dinan','East Tylertown','Enon','Hope','Improve','Lexie'],native=11,total=None,
 x=[702,817,932,1046,1160,1273,1387,1501,1613,1725,1836,1950],header_y=[286,508],row_y=[[566,624],[624,678],[678,730]],row_window_status='Original source prints Senate first, before President. All three selected Senate rows directly read; district prefixes are literal labels, not normalized unique IDs.',values=[
 [152,100,33,19,147,563,17,45,217,114,115],[287,323,275,89,436,189,50,171,30,322,459],[1,5,6,2,6,7,3,6,1,5,9]]),
 3:dict(labels=['Mesa','Midway','North Kirklin','North Knoxo','Sartinsville','South Kirklin','St Paul','Varnel','West Tylertown','TOTAL',''],native=9,total=10,
 x=[721,837,952,1065,1178,1293,1407,1521,1632,1746,1858,1972],header_y=[291,512],row_y=[[571,630],[630,684],[684,738]],values=[[12,49,231,543,72,46,160,134,224,2993],[49,184,185,65,122,132,71,389,177,4005],[3,3,6,2,2,3,3,6,7,86]])}
VALUES['sos-2020-county-oktibbeha']={
 2:dict(labels=['Bell Schoolhouse','Central Starkville','Craig Springs','Double Springs','East Starkville','Hickory Grove','Maben','Needmore\nCommunity Center','North Adaton','North Longview','North Starkville\nDistrict 2'],native=11,total=None,
 x=[668,785,902,1022,1140,1258,1378,1496,1614,1734,1852,1971],header_y=[262,500],row_y=[[1230,1291],[1291,1346],[1346,1402]],values=[
 [212,795,21,91,247,1113,123,757,307,210,608],[105,188,189,366,159,718,106,260,280,491,124],[2,13,3,5,6,59,2,13,11,12,5]]),
 3:dict(labels=['North Starkville\nDistrict 3','Oktoc','Osborn','Sessums','South Adaton','South Longview','South Starkville','Sturgis','West Starkville','TOTAL',''],native=9,total=10,
 x=[672,790,910,1026,1144,1264,1382,1501,1620,1738,1856,1976],header_y=[264,494],row_y=[[1226,1287],[1287,1342],[1342,1396]],values=[[943,437,605,684,169,51,1658,220,1619,10870],[654,290,245,281,220,97,2308,534,977,8592],[31,11,9,6,2,3,55,11,54,313]])}
VALUES['sos-2020-county-panola']={
 2:dict(labels=['Batesville Courthouse','Blackjack Community\nCenter','Cliff Finch Building','Como Library','Courtland Baptist\nChurch','Crenshaw Old City\nHall','Crowder Wastewater\nTreatment Building','Enon Water Building','Eureka Community\nCenter','Longtown Fire\nStation','Macedonia-Concord\nCommunity Center'],native=11,total=None,
 x=[699,821,943,1064,1186,1308,1430,1552,1672,1793,1913,2035],header_y=[258,492],row_y=[[1237,1298],[1298,1354],[1354,1410]],values=[
 [681,354,124,754,835,258,163,44,240,139,649],[1178,722,425,340,324,124,52,79,709,110,117],[31,33,7,16,11,1,1,4,14,2,7]]),
 3:dict(labels=['Mt Olivet Fire Dept.','Panola County\nExtension Building','Patton Lane\nCommunity Center','Pleasant Grove Fire\nStation','Pope City Hall','Sardis Courthouse','Sardis Lake Fire\nDepartment','Sardis Library','Tocowa Community\nCenter','Union Fire Station','TOTAL'],native=10,total=11,
 x=[696,817,938,1060,1182,1304,1425,1548,1667,1788,1909,2030],header_y=[258,490],row_y=[[1234,1296],[1296,1350],[1350,1407]],values=[[335,160,894,72,285,653,168,778,142,225,7953],[581,405,95,141,571,333,84,231,584,220,7425],[19,7,8,3,16,9,2,8,13,8,220]])}
VALUES['sos-2020-county-grenada']={
 2:dict(labels=['Box 1 Southside\nChurch of Christ','Elliott Vol Fire Station','Sweethome Holt#2\nFire Stat','Box 2 Grenada Co\nOffice','Gore Springs Comm\nCenter','Futheyville 1st\nPentecost','Box 3 City\nAuditorium',"Mt. Nebo Young's\nLanding",'Pleasant Grove\nCommun Cen','Box 4 Taylor Hall','Geeslin Friendship\nBapt Church'],native=11,total=None,
 x=[743,863,982,1102,1221,1340,1460,1579,1695,1811,1927,2046],header_y=[287,516],row_y=[[1250,1450],[1250,1450],[1250,1450]],row_window_status='Broad complete original Senate-band reading windows, not exact candidate polygons. Machine grid named-row discovery stops above Senate. Actual eleven table columns end2046;2172is external paper/fax border.',values=[
 [637,122,102,284,96,194,1180,17,324,1374,148],[1049,371,254,260,433,567,351,98,82,106,533],[18,10,5,6,12,10,18,1,2,11,11]]),
 3:dict(labels=['Holcomb Community\nCenter','Box 5 EOC Building','TOTAL','','','','','','','',''],native=2,total=3,
 x=[732,852,971,1090,1210,1328,1448,1566,1682,1799,1915,2034],header_y=[278,508],row_y=[[1250,1450],[1250,1450],[1250,1450]],row_window_status='Broad entire original Senate-band windows, not exact numeric polygons. Two native constituents thenTOTALphysical3/eightunused, external paper border2164not an extra template column.',values=[[204,438,5120],[532,1018,5654],[20,33,157]])}
VALUES['sos-2020-county-bolivar']={
 2:dict(labels=['Benoit','Beulah','Boyle','Choctaw','Cleveland Courthouse','Duncan-Alligator','East Central\nCleveland','East Cleveland','East Rosedale','Eastgate','Gunnison'],native=11,total=None,
 x=[692,810,930,1048,1166,1284,1402,1522,1639,1755,1872,1988],header_y=[262,494],row_y=[[1234,1295],[1295,1350],[1350,1404]],values=[
 [195,146,206,142,125,158,438,911,498,524,184],[83,25,510,29,163,58,3,21,30,51,79],[2,0,5,0,6,2,1,1,0,2,1]]),
 3:dict(labels=['Longshot','Merigold','Mound Bayou','North Cleveland','North West Cleveland','Pace','Renova','Scott','Shaw','Shelby','Skene'],native=11,total=None,
 x=[688,806,924,1042,1160,1280,1398,1516,1633,1751,1866,1985],header_y=[266,498],row_y=[[1238,1299],[1299,1354],[1354,1409]],values=[
 [25,164,923,414,166,243,267,66,871,859,15],[52,123,68,80,729,54,10,78,122,56,187],[0,3,3,4,17,1,1,0,5,7,4]]),
 4:dict(labels=['South Cleveland','Stringtown','West Central\nCleveland','West Cleveland','West Rosedale','Winstonville','TOTAL','','','',''],native=6,total=7,
 x=[682,802,919,1037,1156,1274,1393,1512,1628,1746,1862,1978],header_y=[260,493],row_y=[[1232,1292],[1292,1347],[1347,1402]],values=[[822,9,213,295,246,205,9330],[36,26,589,989,56,10,4317],[7,0,12,16,1,1,102]])}
VALUES['sos-2020-county-itawamba']={
 2:dict(labels=['American Legion','Armory','Banner-Pineville','Bounds','Cardsville','Carolina','Centerville','Clay','Courthouse','Dorsey','Evergreen'],native=11,total=None,
 x=[694,814,934,1055,1174,1294,1414,1534,1652,1769,1886,2004],header_y=[247,480],row_y=[[1226,1288],[1288,1343],[1343,1398]],values=[
 [213,88,71,21,19,50,38,83,36,62,135],[912,384,521,138,143,217,302,647,177,518,250],[25,15,12,3,6,8,5,16,8,14,10]]),
 3:dict(labels=['Fairview-Pleasanton','Fawn Grove','Friendship','Friendship 1D','Friendship-4D','Friendship-5D','Greenwood','Icdc','James Creek','Kirkville','Mantachie'],native=11,total=None,
 x=[688,810,929,1050,1169,1288,1408,1528,1646,1762,1880,1999],header_y=[236,468],row_y=[[1215,1277],[1277,1332],[1332,1386]],values=[
 [17,57,25,13,6,10,144,200,11,63,65],[119,395,131,87,76,102,261,442,162,633,547],[6,13,2,2,3,3,1,14,4,12,20]]),
 4:dict(labels=['Mantachie-3D','Ratliff','Ryan','Salem-Copeland','Tilden','Tremont','TOTAL','','','',''],native=6,total=7,
 x=[694,814,936,1056,1176,1295,1414,1534,1652,1769,1886,2004],header_y=[252,483],row_y=[[1229,1291],[1291,1345],[1345,1402]],row_window_status='Actual printed district/split suffixes retained separately from unsuffixed observations. No name-only2024/current join or inferred unique geographic ID.',values=[[19,14,44,48,78,50,1680],[140,199,269,363,310,373,8818],[3,7,6,11,14,8,251]])}
VALUES['sos-2020-county-marion']={
 2:dict(labels=['Balls Mill','Carley','Cedar Grove','City Hall','Courthouse','Darbun','East Columbia','Foxworth','Goss','Hub','Jefferson School'],native=11,total=None,
 x=[698,818,938,1058,1178,1298,1418,1538,1655,1771,1890,2007],header_y=[254,484],row_y=[[1230,1292],[1292,1347],[1347,1403]],values=[
 [134,85,131,132,177,48,705,308,70,231,160],[416,656,266,129,314,209,262,566,331,158,5],[5,13,6,7,16,5,9,15,15,5,0]]),
 3:dict(labels=['Kokomo','Little Rock','Morgantown','Morris','National Guard','Pine Burr','Pittman','Popetown','Sandy Hook','South Columbia','Union'],native=11,total=None,
 x=[698,817,938,1058,1178,1296,1416,1534,1653,1769,1886,2006],header_y=[252,482],row_y=[[1227,1289],[1289,1345],[1345,1400]],values=[
 [147,221,30,461,197,118,39,509,129,128,17],[386,228,406,799,1093,297,441,373,226,10,250],[12,5,9,13,13,7,8,8,6,2,8]]),
 4:dict(labels=['TOTAL','','','','','','','','','',''],native=0,total=1,
 x=[700,820,938,1059,1179,1298,1418,1537,1655,1772,1890,2008],header_y=[254,485],row_y=[[1230,1292],[1292,1348],[1348,1404]],row_window_status='Complete original22constituents on prior two pages, followed by separateTOTAL-onlyPDF4/physical1 and ten unused columns; no implied missing constituent or2024/current join.',values=[[4177],[7821],[187]])}
VALUES['sos-2020-county-marion-amended']={
 2:dict(labels=['Balls Mill','Carley','Cedar Grove','City Hall','Courthouse','Darbun','East Columbia','Foxworth','Goss','Hub','Jefferson School'],native=11,total=None,
 x=[676,792,908,1024,1138,1256,1372,1488,1604,1718,1832,1944],header_y=[251,475],row_y=[[1189,1248],[1248,1302],[1302,1354]],row_window_status='Fresh complete amended original read independently, not copied from matching earlier publication. Separate source hash/layout and candidate glyph basis retained; matching vectors not a chronology or unit-equivalence proof.',values=[
 [134,85,131,132,177,48,705,308,70,231,160],[416,656,266,129,314,209,262,566,331,158,5],[5,13,6,7,16,5,9,15,15,5,0]]),
 3:dict(labels=['Kokomo','Little Rock','Morgantown','Morris','National Guard','Pine Burr','Pittman','Popetown','Sandy Hook','South Columbia','Union'],native=11,total=None,
 x=[692,808,924,1040,1154,1272,1387,1504,1618,1731,1845,1960],header_y=[267,487],row_y=[[1200,1260],[1260,1313],[1313,1366]],values=[
 [147,221,30,461,197,118,39,509,129,128,17],[386,228,406,799,1093,297,441,373,226,10,250],[12,5,9,13,13,7,8,8,6,2,8]]),
 4:dict(labels=['TOTAL','','','','','','','','','',''],native=0,total=1,
 x=[684,800,916,1032,1148,1264,1380,1496,1610,1724,1838,1952],header_y=[253,474],row_y=[[1189,1247],[1247,1298],[1298,1353]],values=[[4177],[7821],[187]])}
VALUES['sos-2020-county-marshall']={
 2:dict(labels=['1 North Holly Springs','1 Red Banks','1 West Holly Springs','2 Early Grove','2 Hudsonville','2 Mt Pleasant','2 North Cayce','2 North Holly Springs','2 Slayden','3 Barton','3 Byhalia'],native=11,total=None,source_clock_literal='09:13:26 a.m. 11-14-2020',source_clock_qualification='Printed margin fax clock, zone absent; not an established publication/release clock.',
 x=[593,688,784,882,979,1078,1175,1270,1366,1460,1556,1652],header_y=[401,582],row_y=[[1161,1209],[1209,1253],[1253,1298]],header_rule_probe=dict(x_range=[550,2050],y_range=[410,550],dark_threshold=200,minimum_dark_fraction=.45),row_window_status='Complete original smaller embedded table. Beat prefixes retained literal, not asserted unique IDs. Header-only probe false text strokes distinct from manually reviewed physical rules.',values=[
 [653,472,898,129,217,308,265,565,234,188,578],[40,405,136,121,162,629,252,157,348,665,759],[6,22,10,2,9,14,14,9,4,13,29]]),
 3:dict(labels=['3 Cayce','4 Chulahoma','4 Laws Hill','4 Marianna','4 Victoria','4 Wall Hill','4 Warsaw','4 Watson','5 Bethlehem','5 Cornersville','5 Potts Camp'],native=11,total=None,source_clock_literal='09:13:45 a.m. 11-14-2020',source_clock_qualification='Printed margin fax clock, zone absent; not an established release clock.',
 x=[586,682,778,875,972,1071,1167,1263,1359,1453,1548,1645],header_y=[392,573],row_y=[[1150,1198],[1198,1242],[1242,1287]],values=[
 [281,437,99,313,250,412,325,194,48,10,326],[254,98,99,224,131,158,269,243,266,110,494],[11,1,1,7,6,4,4,5,3,4,12]]),
 4:dict(labels=['5 South Holly Springs','5 Waterford','TOTAL','','','','','','','',''],native=2,total=3,source_clock_literal='09:14:03 a.m. 11-14-2020',source_clock_qualification='Printed margin fax clock, zone absent; not an established release clock.',
 x=[593,688,784,882,978,1077,1174,1270,1365,1460,1555,1652],header_y=[405,586],row_y=[[1163,1212],[1212,1256],[1256,1300]],values=[[1136,252,8590],[603,281,6904],[16,6,212]])}
VALUES['sos-2020-county-marshall-amended']={
 2:dict(labels=['1 North Holly Springs','1 Red Banks','1 West Holly Springs','2 Early Grove','2 Hudsonville','2 Mt Pleasant','2 North Cayce','2 North Holly Springs','2 Slayden','3 Barton','3 Byhalia'],native=11,total=None,source_clock_literal='12:52:23 p.m. 11-30-2020',source_clock_qualification='Printed margin fax clock, zone absent; not an established publication/release clock or chronology proof.',
 x=[974,1070,1166,1262,1358,1455,1550,1646,1741,1836,1932,2027],header_y=[377,558],row_y=[[1120,1275],[1120,1275],[1120,1275]],header_rule_probe=dict(x_range=[550,2050],y_range=[410,550],dark_threshold=200,minimum_dark_fraction=.45),row_window_status='Broad complete original Senate-band windows, not exact numeric polygons. This separate amended source prints smaller table at a different page offset; all actual candidate glyphs/headers freshly read independently.',values=[
 [653,472,898,129,217,308,265,565,234,188,578],[40,405,136,121,162,629,252,157,348,665,759],[6,22,10,2,9,14,14,9,4,13,29]]),
 3:dict(labels=['3 Cayce','4 Chulahoma','4 Laws Hill','4 Marianna','4 Victoria','4 Wall Hill','4 Warsaw','4 Watson','5 Bethlehem','5 Cornersville','5 Potts Camp'],native=11,total=None,source_clock_literal='12:52:40 p.m. 11-30-2020',source_clock_qualification='Printed margin fax clock, zone absent; not an established release clock.',
 x=[958,1055,1151,1247,1344,1440,1537,1631,1727,1822,1917,2013],header_y=[365,546],row_y=[[1123,1171],[1171,1214],[1214,1258]],values=[
 [281,437,99,313,250,412,325,194,48,10,326],[254,98,99,224,131,158,269,243,266,110,494],[11,1,1,7,6,4,4,5,3,4,12]]),
 4:dict(labels=['5 South Holly Springs','5 Waterford','TOTAL','','','','','','','',''],native=2,total=3,source_clock_literal='12:52:58 p.m. 11-30-2020',source_clock_qualification='Printed margin fax clock, zone absent; not an established release clock.',
 x=[974,1070,1166,1263,1359,1454,1551,1646,1741,1836,1932,2027],header_y=[378,560],row_y=[[1131,1178],[1178,1220],[1220,1263]],values=[[1136,252,8590],[603,281,6904],[16,6,212]])}
VALUES['sos-2020-county-pike']={
 2:dict(labels=['(01) New Hope\nBaptist Church','(02) S MCCOMB\nBAPTIST CHURCH','(03)First Bapt.\nChurch, Summit','(04) Mlk Center','(05) North McComb\nBaptist Church','(06) LifePointe\nNazarene Church','(07) St Mary Free\nWill Bapt. Ch.','(08) Fernwood\nBaptist Church','(09) Magnolia Comm\nCtr.','(10) Braswell\nEducation Complex','(11) Leggett\nCommunity'],ids=['01','02','03','04','05','06','07','08','09','10','11'],native=11,total=None,
 x=[688,805,925,1042,1160,1278,1394,1511,1625,1739,1852,1969],header_y=[268,502],row_y=[[1250,1445],[1250,1445],[1250,1445]],header_rule_probe=dict(x_range=[660,2040],y_range=[290,480],dark_threshold=180,minimum_dark_fraction=.45),row_window_status='Broad complete original Senate-band windows, not exact numeric polygons. Machine numeric grid/row detector failed; original eleven physical headers/candidate vectors directly read. Parsed01..11only literal header substrings, not2024/current crosswalk.',values=[
 [627,228,312,631,210,280,385,524,570,553,246],[37,51,54,18,325,8,100,200,228,290,152],[4,8,4,6,13,1,2,9,10,10,3]]),
 3:dict(labels=['(12) Navilla Baptist\nChurch fellowship','(13) Holmesville\nComm.','(14) Calvary Baptist\nChurch','(15) Friendship Bapt.\nChurch','(16) Summit City\nHall','(17) SMCC Work\nForce Training Ctr','(18) Johnston Chapel\nMeth. Church','(19) Pisgah\nMethodist Church','(20) Pike Co. Nat.\nBank','(21) Old Progress\nVolunteer Fire Station','(22) Church of Christ'],ids=['12','13','14','15','16','17','18','19','20','21','22'],native=11,total=None,
 x=[688,805,923,1042,1159,1277,1396,1511,1626,1740,1855,1969],header_y=[268,502],row_y=[[1250,1445],[1250,1445],[1250,1445]],row_window_status='Broad original lower Senate-band windows, not exact polygons. Each named candidate/printed column read independently from whole original, not joined to2024vendor orSEMS observations.',values=[
 [563,288,224,175,427,273,165,226,341,515,525],[615,377,466,546,314,600,848,733,218,410,282],[24,12,12,10,8,18,21,17,9,24,10]]),
 4:dict(labels=['(23) West McComb\nBapt. Church','(24) St. Mary of the\nPines','(25) Osyka City Hall','TOTAL','','','','','','',''],ids=['23','24','25',None,None,None,None,None,None,None,None],native=3,total=4,
 x=[690,809,927,1045,1164,1280,1398,1515,1628,1743,1856,1972],header_y=[268,502],row_y=[[1250,1445],[1250,1445],[1250,1445]],row_window_status='Broad original Senate-band windows. Three final source constituents, TOTALphysical4/sevenunused;25literal historical codes do not establish a cross-year/current identity equivalence.',values=[[276,359,125,9048],[423,522,227,8044],[6,13,3,257]])}
VALUES['sos-2020-county-tippah']={
 2:dict(labels=['Blue Mountain','Brownfield','Chalybeate','Chapman','Clarysville','Cotton Plant','Dry Creek','Dumas','FALKNER','Mitchell','New Hope'],native=11,total=None,
 x=[686,804,923,1042,1161,1280,1398,1518,1636,1754,1872,1990],header_y=[262,494],row_y=[[1231,1292],[1292,1348],[1348,1403]],values=[
 [301,16,97,46,11,102,33,56,119,19,22],[374,116,486,420,131,85,246,469,567,206,257],[21,2,18,6,2,4,1,13,14,1,5]]),
 3:dict(labels=['North Falkner','North Ripley','Palmer','Peoples','Pine Grove','Providence','Ripley','Shady Grove','Southwest Ripley','Spout Springs','Threeforks'],native=11,total=None,
 x=[684,803,922,1040,1159,1278,1396,1516,1633,1752,1870,1987],header_y=[260,492],row_y=[[1230,1291],[1291,1346],[1346,1402]],values=[
 [59,428,71,45,20,47,289,16,343,21,31],[149,777,392,172,224,189,492,128,575,174,245],[5,26,15,8,3,2,13,0,23,5,9]]),
 4:dict(labels=['Tiplersville','Walnut','TOTAL','','','','','','','',''],native=2,total=3,
 x=[684,803,921,1040,1159,1277,1396,1515,1633,1752,1868,1987],header_y=[260,491],row_y=[[1227,1288],[1288,1344],[1344,1398]],row_window_status='Actual24source constituents onthreecomplete original pages, TOTALphysical3/eightunused. No2024/native/current count or name equivalence.',values=[[126,114,2432],[154,366,7394],[7,5,208]])}
VALUES['sos-2020-county-tippah-amended']={
 2:dict(labels=['Blue Mountain','Brownfield','Chalybeate','Chapman','Clarysville','Cotton Plant','Dry Creek','Dumas','FALKNER','Mitchell','New Hope'],native=11,total=None,
 x=[678,796,916,1034,1152,1271,1390,1510,1628,1748,1867,1987],header_y=[270,503],row_y=[[1242,1303],[1303,1358],[1358,1414]],row_window_status='Fresh complete amended original grid directly read independently; equal earlier candidate vectors do not establish chronology or unit identity equivalence.',values=[
 [301,16,97,46,11,102,33,56,119,19,22],[374,116,486,420,131,85,246,469,567,206,257],[21,2,18,6,2,4,1,13,14,1,5]]),
 3:dict(labels=['North Falkner','North Ripley','Palmer','Peoples','Pine Grove','Providence','Ripley','Shady Grove','Southwest Ripley','Spout Springs','Threeforks'],native=11,total=None,
 x=[678,796,915,1034,1152,1270,1389,1508,1628,1746,1864,1986],header_y=[270,502],row_y=[[1240,1302],[1302,1358],[1358,1413]],values=[
 [59,428,71,45,20,47,289,16,343,21,31],[149,777,392,172,224,189,492,128,575,174,245],[5,26,15,8,3,2,13,0,23,5,9]]),
 4:dict(labels=['Tiplersville','Walnut','TOTAL','','','','','','','',''],native=2,total=3,
 x=[676,794,912,1032,1149,1268,1387,1505,1624,1744,1862,1982],header_y=[262,494],row_y=[[1230,1292],[1292,1348],[1348,1403]],values=[[126,114,2432],[154,366,7394],[7,5,208]])}
VALUES['sos-2020-county-warren']={
 2:dict(labels=['Redwood','Bovina','Culkin','Oakland','Cedar Grove','Kings','St Aloysius','Auditorium','Brunswick','3-61','American Legion Post'],native=11,total=None,
 x=[716,833,950,1068,1185,1302,1420,1537,1652,1768,1884,2002],header_y=[282,509],row_y=[[1242,1302],[1302,1356],[1356,1410]],values=[
 [41,530,741,180,938,470,241,714,33,48,925],[221,1140,1491,628,219,303,6,97,230,93,198],[7,28,37,10,11,2,0,6,0,0,17]]),
 3:dict(labels=['Cherry Street','No.7 Fire Station','Jett','Goodrum','Yokena','Elks Lodge','Beechwood','Moose Lodge','Tingleville','Lee Road','Plumbers &\nPipefitters'],native=11,total=None,
 x=[718,836,953,1070,1188,1306,1421,1539,1654,1772,1886,2004],header_y=[299,527],row_y=[[1260,1320],[1320,1374],[1374,1428]],values=[
 [1044,710,763,274,206,707,450,346,465,324,474],[343,179,393,546,339,473,983,731,332,151,529],[19,9,10,7,7,12,15,15,5,7,13]]),
 4:dict(labels=['YMCA','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[714,830,950,1066,1183,1301,1418,1535,1650,1766,1882,2002],header_y=[290,518],row_y=[[1250,1310],[1310,1364],[1364,1418]],values=[[229,10853],[287,9912],[9,246]])}
VALUES['sos-2020-county-warren-amended']={
 2:dict(labels=['Redwood','Bovina','Culkin','Oakland','Cedar Grove','Kings','St Aloysius','Auditorium','Brunswick','3-61','American Legion Post'],native=11,total=None,
 x=[682,798,916,1032,1150,1268,1386,1504,1620,1736,1854,1971],header_y=[270,500],row_y=[[1229,1290],[1290,1344],[1344,1400]],row_window_status='Fresh complete amended original independently read; matching previous candidate vectors do not establish chronology, source-native identity equivalence or current geography.',values=[
 [41,530,741,180,938,470,241,714,33,48,925],[221,1140,1491,628,219,303,6,97,230,93,198],[7,28,37,10,11,2,0,6,0,0,17]]),
 3:dict(labels=['Cherry Street','No.7 Fire Station','Jett','Goodrum','Yokena','Elks Lodge','Beechwood','Moose Lodge','Tingleville','Lee Road','Plumbers &\nPipefitters'],native=11,total=None,
 x=[694,810,928,1046,1162,1280,1398,1516,1632,1749,1865,1984],header_y=[287,520],row_y=[[1248,1309],[1309,1364],[1364,1418]],row_window_status='Eleven physical original table columns; extra machine1984..2120 is outer-page fax margin, excluded, not an unprinted reporting unit.',values=[
 [1044,710,763,274,206,707,450,346,465,324,474],[343,179,393,546,339,473,983,731,332,151,529],[19,9,10,7,7,12,15,15,5,7,13]]),
 4:dict(labels=['YMCA','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[682,800,916,1034,1151,1268,1386,1504,1620,1738,1854,1972],header_y=[268,501],row_y=[[1228,1290],[1290,1344],[1344,1400]],values=[[229,10853],[287,9912],[9,246]])}
VALUES['sos-2020-county-wayne']={
 2:dict(labels=['Beat Four','Big Rock','Buckatunna','Chapparral/Diamond','Chicora','Clara','Corinth','Denham','Eucutta','Hiwannee','Matherville/Coyt'],native=11,total=None,
 x=[722,840,960,1078,1196,1316,1436,1554,1671,1789,1906,2024],header_y=[262,494],row_y=[[1234,1296],[1296,1350],[1350,1406]],values=[
 [93,81,272,253,67,80,15,100,62,209,33],[537,93,229,74,222,1188,255,337,162,79,107],[14,3,6,1,6,23,3,6,4,4,3]]),
 3:dict(labels=['Mozingo','Pleasant Grove','State Line','Strengthford','Waynesboro City 1','Waynesboro City 2','Waynesboro City 3','Waynesboro City 4','Waynesboro City 5','Winchester','Yellow Creek'],native=11,total=None,
 x=[720,839,958,1076,1195,1314,1434,1552,1670,1788,1904,2022],header_y=[264,498],row_y=[[1236,1298],[1298,1352],[1352,1408]],values=[
 [72,123,272,13,513,472,207,257,220,352,188],[258,272,332,173,16,362,555,99,104,217,313],[5,7,14,4,3,12,9,4,1,4,8]]),
 4:dict(labels=['TOTAL','','','','','','','','','',''],native=0,total=1,
 x=[723,843,961,1080,1198,1317,1436,1556,1673,1791,1907,2026],header_y=[259,492],row_y=[[1230,1292],[1292,1348],[1348,1404]],row_window_status='Twenty-two native columns on prior pages and TOTAL-only final page physical1, ten unused. Missing internal machine rule restored from actual full-page header/table geometry, not numeric residual fitting.',values=[[3954],[5984],[144]])}
VALUES['sos-2020-county-lamar']={
 2:dict(labels=['Lamar Park','Okahola','Richburg','Northeast Lamar','Lumberton','South Purvis','Yawn','Wesley Manor','Westover','Pine Grove','Baxterville'],native=11,total=None,
 x=[658,777,896,1014,1134,1252,1372,1492,1611,1730,1848,1968],header_y=[288,519],row_y=[[1260,1322],[1322,1378],[1378,1433]],values=[
 [753,163,662,667,592,192,20,643,317,41,30],[569,361,1109,543,542,1414,243,355,104,473,368],[26,22,51,25,25,41,9,26,7,11,13]]),
 3:dict(labels=['Greenville','Purvis','Arnold Line','Mill Creek','Midway','Oak Grove','Lake Serene','Kingsmill','Breland','Oloh','Rocky Branch'],native=11,total=None,
 x=[660,779,898,1016,1135,1254,1373,1492,1612,1732,1850,1970],header_y=[286,519],row_y=[[1260,1321],[1321,1378],[1378,1434]],values=[
 [59,380,484,109,241,479,597,234,896,73,153],[759,1393,546,398,1214,1164,1944,1130,1588,590,458],[17,53,25,17,38,48,58,25,50,14,10]]),
 4:dict(labels=['Sumrall','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[660,779,897,1016,1134,1254,1373,1492,1612,1731,1850,1969],header_y=[283,514],row_y=[[1256,1318],[1318,1374],[1374,1430]],row_window_status='Actual full original has Sumrall then TOTALphysical2 and nine unused columns; machine merged first two headers. Header physical rules independently restored, not from candidate residuals.',values=[[372,8157],[2323,19588],[82,693]])}
VALUES['sos-2020-county-lincoln']={
 2:dict(labels=['Alexander','Arlington','Big Springs','Bogue Chitto','Brignal / Rogers\nCircle','Caseyville','City Hall','East Lincoln','Enterprise','Fair River','Forestry'],native=11,total=None,
 x=[694,813,932,1051,1170,1289,1408,1528,1645,1763,1880,1998],header_y=[269,498],row_y=[[1234,1295],[1295,1350],[1350,1405]],row_window_status='Broad complete original Senate-band windows, not exact candidate polygons. Literal Forestry here is source-specific; no spelling normalization or join to2024 Forrestry.',values=[
 [469,135,41,160,507,96,105,14,95,12,211],[11,500,152,180,190,391,169,275,951,214,329],[0,7,8,4,6,8,6,2,22,1,9]]),
 3:dict(labels=['Governmental\nComplex','Halbert Heights','Heucks Retreat','High School','Johnson','Johnson Grove','Lipsey','Little Bahala','Loyd Star','Montgomery','New Sight'],native=11,total=None,
 x=[692,810,929,1048,1167,1286,1406,1524,1644,1760,1878,1997],header_y=[273,503],row_y=[[1238,1299],[1299,1354],[1354,1408]],row_window_status='Eleven printed physical columns; extra machine1997..2123 is outer page beyond table, excluded.',values=[
 [445,300,124,393,91,105,292,78,193,143,307],[20,1020,482,24,432,484,336,139,812,200,656],[4,10,7,3,3,2,4,2,6,5,9]]),
 4:dict(labels=['Norfield','Old Brook','Old Red Star','PEARLHAVEN','Ruth','Vaughn','West Lincoln','Zetus','TOTAL','',''],native=8,total=9,
 x=[693,812,930,1048,1168,1287,1406,1526,1644,1762,1879,1998],header_y=[262,491],row_y=[[1226,1286],[1286,1342],[1342,1396]],values=[
 [50,162,77,378,25,101,63,84,5256],[176,678,431,62,535,293,732,504,11378],[2,13,4,3,5,1,10,2,168]])}
VALUES['sos-2020-county-lauderdale']={
 2:dict(labels=['101 - One','105 - Five','126 - Gracepointe\nFellowship','127 - Bailey','146 - New\nLauderdale','175 - West Dalewood','202 - Two','206 - Six','214 - Fourteen','235 - Daleville','237 - East\nLauderdale'],ids=['101','105','126','127','146','175','202','206','214','235','237'],native=11,total=None,
 x=[678,796,916,1034,1154,1274,1391,1510,1628,1746,1863,1980],header_y=[264,496],row_y=[[1234,1296],[1296,1351],[1351,1406]],values=[
 [700,578,300,371,282,25,93,1143,739,207,439],[892,853,762,885,987,101,111,133,88,65,654],[28,20,27,19,22,5,6,4,10,4,12]]),
 3:dict(labels=['238 - Marion','240 - Kewanee','254 - Russell','262 - Toomsuba','303 - Three','313 - Thirteen','329 - Center Hill','331 - Collinsville','343 - Martin','361 - Suqualena','407 - Seven'],ids=['238','240','254','262','303','313','329','331','343','361','407'],native=11,total=None,
 x=[688,808,927,1047,1165,1284,1403,1523,1640,1758,1874,1992],header_y=[280,510],row_y=[[1248,1310],[1310,1364],[1364,1420]],row_window_status='Physical first Marion column and merged internal headers recovered by complete original eleven-column review; no machine-ordinal matching or numeric residual allocation.',values=[
 [385,129,306,189,785,846,193,323,50,372,583],[340,100,486,167,141,577,1015,1225,810,1092,98],[19,5,13,8,9,19,24,32,11,34,9]]),
 4:dict(labels=['408 - Eight','409 - Nine','410 - Ten','411 - Eleven','412 - Twelve','450 - Pickard','517 - Seventeen','528 - Causeyville','530 - Clarkdale','544 - Meehan','549 - Odom'],ids=['408','409','410','411','412','450','517','528','530','544','549'],native=11,total=None,
 x=[684,804,922,1042,1160,1280,1399,1518,1635,1753,1870,1988],header_y=[268,498],row_y=[[1238,1299],[1299,1354],[1354,1409]],values=[
 [552,661,218,666,650,168,225,45,123,94,189],[133,43,45,88,38,364,328,321,1079,360,206],[3,2,3,12,4,5,11,3,21,12,9]]),
 5:dict(labels=['560 - South\nNellieburg','564 - Vimville','565 - Whynot','567 - Zero','583 - Mt Gilead','TOTAL','','','','',''],ids=['560','564','565','567','583',None,None,None,None,None,None],native=5,total=6,
 x=[684,804,922,1040,1160,1278,1398,1516,1634,1752,1869,1986],header_y=[268,498],row_y=[[1236,1297],[1297,1352],[1352,1407]],values=[[104,377,84,145,198,13537],[261,731,390,684,429,17082],[7,20,15,21,13,501]])}
VALUES['sos-2020-county-monroe']={
 2:dict(labels=['1 Amory First','1 Bigbee','1 Boyds','1 Hatley','1 Smithville','2 Amory Second','2 Becker','2 Parham','2 Sipsey','2 Williams','3 Aberdeen Third'],native=11,total=None,
 x=[686,804,922,1042,1160,1280,1400,1518,1637,1754,1871,1992],header_y=[261,490],row_y=[[1227,1288],[1288,1342],[1342,1398]],values=[
 [124,17,34,172,128,530,140,23,21,13,321],[551,156,325,1375,760,1210,856,143,213,83,291],[14,8,9,29,27,47,20,3,10,2,11]]),
 3:dict(labels=['3 Athens','3 Bartahatchie','3 Greenwood Springs','3 Hamilton','3 Lackey','4 Darracott','4 Gibson','4 North Aberdeen','4 Prairie','4 South Aberdeen','5 Amory Fifth'],native=11,total=None,
 x=[674,792,910,1030,1150,1268,1388,1508,1626,1743,1862,1982],header_y=[246,474],row_y=[[1210,1272],[1272,1326],[1326,1380]],values=[
 [93,26,9,312,141,36,328,755,460,830,547],[348,230,109,1071,644,111,87,383,53,154,15],[14,7,3,27,12,2,4,17,3,9,2]]),
 4:dict(labels=['5 Central Grove','5 Nettleton','5 Willis','5 Wren','TOTAL','','','','','',''],native=4,total=5,
 x=[671,790,910,1028,1148,1266,1386,1506,1622,1740,1860,1978],header_y=[246,475],row_y=[[1211,1272],[1272,1326],[1326,1382]],row_window_status='Twenty-six source constituents, TOTALphysical5/sixunused. Extra1978..2126machine column is outer page beyond original table. District prefixes are literal, not unique IDs.',values=[[232,374,541,234,6441],[106,426,160,656,10516],[5,12,4,13,314]])}
VALUES['sos-2020-county-neshoba']={
 2:dict(labels=['Arlington','Bogue Chitto','Burnside','Center','County Line','Deemer','Dixon','East Neshoba','Fairview','Forestdale','Fork'],native=11,total=None,
 x=[680,798,918,1038,1158,1278,1398,1517,1636,1754,1872,1993],header_y=[269,494],row_y=[[1220,1281],[1281,1335],[1335,1390]],values=[
 [22,53,235,40,32,36,192,216,71,67,25],[338,27,150,259,325,183,283,90,152,247,231],[10,1,5,8,11,4,11,5,9,2,7]]),
 3:dict(labels=['Fusky','Hays','Herbert','Hope','House','Mcdonald','Neshoba','North Bend','Northeast\nPhiladelphia','Northwest\nPhiladelphia','Pearl River'],native=11,total=None,
 x=[686,806,926,1046,1166,1286,1406,1526,1644,1762,1882,2000],header_y=[268,496],row_y=[[1215,1400],[1215,1400],[1215,1400]],row_window_status='Broad complete Senate-band original reading windows; machine lower row rules missing. All three named rows directly read on complete source page; no exact candidate polygon assertion.',values=[
 [20,52,34,56,40,49,73,30,275,1143,315],[332,241,281,169,432,513,294,399,1162,136,58],[10,4,9,6,10,16,11,12,30,6,8]]),
 4:dict(labels=['SOUTH\nPHILADELPHIA','Southeast\nPhiladelphia','Tucker - District One','Tucker - District\nThree','Zephyrhill','TOTAL','','','','',''],native=5,total=6,
 x=[685,804,924,1043,1163,1284,1403,1522,1640,1759,1878,1997],header_y=[262,489],row_y=[[1211,1272],[1272,1326],[1326,1382]],row_window_status='Actual original has two distinct South/Southeast Philadelphia columns before Tucker1/Tucker3/Zephyrhill and TOTALphysical6. Machine merged first headers; no current or cross-year identity join.',values=[[39,276,64,63,84,3602],[93,750,12,435,205,7797],[2,13,2,16,6,234]])}
VALUES['sos-2020-county-pearl-river']={
 2:dict(labels=['AMACKERTOWN 2','CARRIERE 3','CARRIERE 5','CEASAR 3','CROSSROADS 2','DERBY 1','F Z GOSS 4','GUMPOND/HICKORY\nGROVE 3','HENLEYFIELD 2','MCNEILL 3','MILL CREEK 2'],native=11,total=None,
 x=[677,795,914,1034,1153,1272,1390,1511,1629,1748,1865,1984],header_y=[256,490],row_y=[[1234,1296],[1296,1352],[1352,1409]],values=[
 [26,181,266,15,72,108,246,101,102,96,98],[252,778,1504,167,583,371,1504,761,696,641,527],[6,29,68,5,22,17,67,28,26,24,30]]),
 3:dict(labels=['NICHOLSON 4','PIC/HAWL/NH 5','PICAYUNE 1\nEASTSIDE','PICAYUNE 1\nSOUTHSIDE','PICAYUNE 2','PICAYUNE 4','PINE GROVE 4','POPLARVILLE 1','POPLARVILLE 2','POPLARVILLE 3','PROGRESS 3'],native=11,total=None,
 x=[690,808,928,1046,1166,1286,1405,1525,1644,1762,1880,1999],header_y=[270,504],row_y=[[1250,1313],[1313,1369],[1369,1425]],row_window_status='Eleven printed original columns; machine stopped at boundary before final PROGRESS3 column, recovered by full-page direct review.',values=[
 [138,486,539,1002,267,134,138,211,161,150,30],[501,2252,485,216,1062,631,825,315,810,770,285],[30,74,31,27,62,24,27,18,40,40,10]]),
 4:dict(labels=['SPRINGHILL 2','STEEP HOLLOW 3','SYCAMORE 5','WHITESAND 1','TOTAL','','','','','',''],native=4,total=5,
 x=[673,792,910,1030,1150,1270,1389,1509,1628,1747,1864,1984],header_y=[256,490],row_y=[[1235,1298],[1298,1354],[1354,1410]],row_window_status='Four final constituents/TOTALphysical5/sixunused; extra1984..2130machine rectangle is outside printed table, excluded. District suffixes literal, not unique IDs or cross-year/current join.',values=[[42,105,123,216,5053],[378,744,621,135,17814],[7,31,32,5,780]])}
VALUES['sos-2020-county-pontotoc']={
 2:dict(labels=['Algoma Al','Bankhead Ba','Beckham Bec','Bethel/Endville Be','Buchanan Bu','Cherry Creek Cc','Ecru Ec','Friendship Fr','Hoyle Ho','Hurricane Hu','Judah Ju'],ids=['Al','Ba','Bec','Be','Bu','Cc','Ec','Fr','Ho','Hu','Ju'],native=11,total=None,
 x=[680,799,918,1036,1156,1276,1395,1516,1634,1752,1868,1986],header_y=[257,487],row_y=[[1230,1292],[1292,1347],[1347,1403]],values=[
 [97,311,98,107,53,73,198,47,318,40,28],[472,343,404,461,410,522,570,181,360,432,282],[11,9,19,9,18,18,24,5,12,13,11]]),
 3:dict(labels=['Longview Lo','Oakhill Oh','Pontotoc 1 P1','Pontotoc 2 P2','Pontotoc 3 P3','Pontotoc 4 P4','Pontotoc 5 P5','Randolph','Robbs Ro','Sherman Sh','Springville Sp'],ids=['Lo','Oh','P1','P2','P3','P4','P5',None,'Ro','Sh','Sp'],native=11,total=None,
 x=[688,808,926,1046,1166,1284,1404,1523,1640,1758,1874,1990],header_y=[263,492],row_y=[[1228,1290],[1290,1344],[1344,1398]],values=[
 [129,40,85,134,257,153,298,65,17,66,141],[167,276,299,373,622,366,819,656,48,262,574],[7,4,12,11,11,8,28,21,3,6,20]]),
 4:dict(labels=['Thaxton Th','Toccopola To','Troy Tr','Turnpike Tu','Woodland Wo','Zion Z','TOTAL','','','',''],ids=['Th','To','Tr','Tu','Wo','Z',None,None,None,None,None],native=6,total=7,
 x=[681,801,920,1039,1158,1276,1395,1514,1632,1748,1864,1981],header_y=[259,489],row_y=[[1225,1288],[1288,1342],[1342,1396]],row_window_status='Twenty-eight original native constituents; source-printed short suffixes retained in labels/optional parsed IDs. No source-name/code join across years or to2026.',values=[[86,54,85,40,21,123,3164],[452,178,478,337,127,332,10803],[12,9,14,7,9,6,337]])}
VALUES['sos-2020-county-scott']={
 2:dict(labels=['BEAT 4/BRANCH','Beat 1/Harperville','Beat 1/Hillsboro','Beat 1/North Forest','Beat 2/High Hill','Beat 2/Homewood','Beat 2/Lake','Beat 2/South Forest','Beat 2/Usry','Beat\n3/Cooperville/Springf','Beat 3/Eastwest\nMorton'],native=11,total=None,
 x=[682,802,922,1042,1162,1283,1403,1522,1641,1759,1878,1998],header_y=[272,498],row_y=[[1220,1400],[1220,1400],[1220,1400]],row_window_status='Broad complete Senate-band reading windows, not exact candidate polygons; c10 source label visibly truncated after Springf, no expanded place inferred.',values=[
 [105,402,486,541,176,68,123,536,39,54,402],[424,276,258,94,149,209,151,288,237,505,581],[10,3,4,0,9,3,8,9,2,10,17]]),
 3:dict(labels=['Beat 3/Northwest\nForest','Beat 3/Pulaski','Beat 4/Clifton','Beat 4/Contrell','Beat 4/Forkville','Beat 4/Ludlow','Beat 4/North Morton','Beat 5/Langs Mill','Beat 5/Northeast\nForest','Beat 5/Salem','Beat 5/Sebastopol'],native=11,total=None,
 x=[678,798,916,1036,1158,1277,1398,1516,1634,1753,1872,1991],header_y=[275,501],row_y=[[1224,1286],[1286,1340],[1340,1396]],values=[
 [26,53,21,169,17,159,424,151,88,240,29],[112,234,82,86,214,281,221,375,335,212,397],[2,8,0,4,2,8,16,6,12,4,8]]),
 4:dict(labels=['Beat 5/Steele','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[676,796,917,1036,1156,1278,1398,1516,1636,1754,1873,1992],header_y=[269,495],row_y=[[1218,1279],[1279,1333],[1333,1389]],values=[[340,4649],[212,5933],[6,151]])}
VALUES['sos-2020-county-yazoo']={
 2:dict(labels=['Benton','Center Ridge','Deasonville','East Bentonia','Eden','Free Run','Fugates','Holly Bluff','Jonestown','LITTLE YAZOO','Lake City'],native=11,total=None,
 x=[716,834,951,1070,1188,1307,1425,1544,1662,1782,1897,2016],header_y=[264,496],row_y=[[1238,1300],[1300,1354],[1354,1410]],header_rule_probe=dict(x_range=[680,2050],y_range=[290,470],dark_threshold=200,minimum_dark_fraction=.4),row_window_status='Faint complete original11physical columns directly reviewed; machine omitted first and multiple internal header boundaries. Header-only pixel proposals retained; accepted broad reading rectangles are not exact candidate polygons.',values=[
 [261,88,443,132,66,35,185,63,328,102,37],[474,345,253,178,187,115,189,96,3,594,131],[6,8,7,5,4,0,4,0,0,4,1]]),
 3:dict(labels=['Mechanicsburg','Midway','Mound St. Building','N.O. Taylor Gym','Old Jr. High','Satartia','Teen Center','Valley','Washington St. Fire\nStation','Welfare Office','West Bentonia'],native=11,total=None,
 x=[702,821,939,1058,1177,1295,1414,1532,1650,1769,1887,2006],header_y=[251,482],row_y=[[1226,1287],[1287,1343],[1343,1398]],values=[
 [53,239,316,1259,495,16,846,33,201,238,294],[438,202,2,45,58,38,374,144,178,115,210],[7,6,1,7,0,0,4,3,0,2,7]]),
 4:dict(labels=['Zion','TOTAL','','','','','','','','',''],native=1,total=2,
 x=[710,828,946,1064,1182,1304,1422,1540,1658,1776,1894,2012],header_y=[256,490],row_y=[[1232,1294],[1294,1350],[1350,1406]],row_window_status='Actual23source constituents followed by TOTALphysical2 and nine unused columns. All original candidate glyphs directly read; source faintness and failed machine locators do not create missing zeros or inferred units.',values=[[74,5804],[182,4551],[3,79]])}
def main():
    controls={r['source_id']:r for r in json.loads((OUT/'county-2020-publication-controls.json').read_text())['readings']};views=[];rows=[];counts=Counter();county_fips={r['county'].lower().replace(' ','-'):r['fips'] for r in csv.DictReader((BASE/'data/county-baselines.csv').open())}
    for sid,pv in VALUES.items():
        c=controls[sid];assert sha(original(sid))==c['raw_sha256'];fips=county_fips[c['county_key']];sums=Counter();totals={};pages=[]
        for pg,p in pv.items():
            folder=OUT/'qa/historical-native-originals'/sid;receipt=json.loads((folder/f'p{pg:04d}-render.json').read_text());assert receipt['raw_sha256']==c['raw_sha256'];assert sha((BASE/receipt['full_original_render_path']).read_bytes())==receipt['render_sha256'];w,h=receipt['render_size'];xs=p['x'];assert len(xs)==len(p['labels'])+1 and all(0<=x<=w for x in xs);roles=[p.get('roles_by_column',{}).get(i+1,'source_native_reporting_constituent' if i<p['native'] else 'source_TOTAL' if i+1==p['total'] else 'unused_template_column') for i in range(len(p['labels']))];columns=[];fields=[]
            for i,(l,r,label,role) in enumerate(zip(xs,xs[1:],p['labels'],roles),1):
                assert l<r;columns.append(dict(source_column=i,label_literal=label,role=role,header_bounds=[l,p['header_y'][0],r,p['header_y'][1]],literal_printed_id=p.get('ids',[None]*len(roles))[i-1],unit_type='precinct_as_printed' if role=='source_native_reporting_constituent' else role));counts[role]+=1
            for name,party,vs,ys in zip(NAMES,PARTIES,p['values'],p['row_y']):
                vs=vs+[None]*(len(roles)-len(vs));assert len(vs)==len(roles) and 0<=ys[0]<ys[1]<=h;fields.append(dict(candidate=name,party_literal=party,values=vs,row_bounds=[xs[0],ys[0],xs[-1],ys[1]],basis='Each glyph directly read from complete original raster, not copied from a peer, another publication/year, or fitted to a residual'))
                for col,v in zip(columns,vs):
                    if col['role']=='unused_template_column':assert v is None;counts['unused_null_positions']+=1
                    else:
                        assert isinstance(v,int) and v>=0;counts['candidate_numeric_positions']+=1
                        if col['role'] in ['source_native_reporting_constituent','source_administrative_reporting_column']:sums[name]+=v
                        else:totals[name]=v
                    rows.append(dict(source_key=f'{sid}:p{pg}:c{col["source_column"]}',source_id=sid,county_fips=fips,source_raw_sha256=c['raw_sha256'],publication_label=c['publication_label'],publication_variant=c['publication_variant'],source_page=pg,source_column=col['source_column'],literal_native_label=col['label_literal'],literal_printed_id=col['literal_printed_id'],role=col['role'],candidate=name,party_literal=party,votes=v,header_bounds_pixels=json.dumps(col['header_bounds']),candidate_reading_window_pixels=json.dumps([col['header_bounds'][0],ys[0],col['header_bounds'][2],ys[1]]),full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256'],generic_writein=None,under_over_ballots_registration=None))
            pages.append(dict(page=pg,render_size=receipt['render_size'],render_scale=receipt['render_scale'],rotation_ccw=receipt['rotation_ccw'],deskew_angle_ccw=receipt['deskew_angle_ccw'],full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256'],columns=columns,fields=fields,row_window_status=p.get('row_window_status','Source candidate row reading window, not a geographic boundary'),source_position_qualification='Physical header grid and actualTOTAL column visually reviewed on this complete2020original; not an accepted geographic polygon or current ID. Reading-window qualification is explicit; broad windows are not exact candidate polygons.'))
            if p.get('header_qualification'):pages[-1]['literal_header_qualification']=p['header_qualification']
            for key in ['source_status_literal','printed_footer_page_literal','source_clock_literal','source_clock_qualification']:
                if key in p:pages[-1][key]=p[key]
            if p.get('numeric_correction_history'):
                from PIL import Image
                history=[]
                for correction in p['numeric_correction_history']:
                    q=folder/correction['evidence_crop_name'];Image.open(BASE/receipt['full_original_render_path']).crop(correction['evidence_crop_bounds']).save(q)
                    history.append(dict(**correction,evidence_crop_path=str(q.relative_to(BASE)),evidence_crop_sha256=sha(q.read_bytes()),evidence_crop_bytes=q.stat().st_size))
                pages[-1]['numeric_correction_history']=history
            if p.get('header_reading_evidence'):
                from PIL import Image
                evidence=[]
                for reading in p['header_reading_evidence']:
                    q=folder/reading['name'];Image.open(BASE/receipt['full_original_render_path']).crop(reading['bounds']).rotate(reading.get('rotate_ccw',0),expand=True).save(q)
                    evidence.append(dict(**reading,evidence_path=str(q.relative_to(BASE)),evidence_sha256=sha(q.read_bytes()),evidence_bytes=q.stat().st_size))
                pages[-1]['header_reading_evidence']=evidence
            if p.get('header_rule_probe'):
                import numpy as np
                from PIL import Image
                settings=p['header_rule_probe'];xl,xr=settings['x_range'];yt,yb=settings['y_range'];a=np.asarray(Image.open(BASE/receipt['full_original_render_path']));score=(a[yt:yb,xl:xr]<settings['dark_threshold']).mean(axis=0);hits=np.where(score>settings['minimum_dark_fraction'])[0]+xl;groups=[]
                for hit in hits:
                    if not groups or hit>groups[-1][-1]+1:groups.append([int(hit)])
                    else:groups[-1].append(int(hit))
                q=folder/f'p{pg:04d}-header-rule-proposals.json';save(q,dict(source_id=sid,PDFpage=pg,raw_sha256=c['raw_sha256'],full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256'],settings=settings,dark_column_fraction=score.tolist(),all_unfiltered_rule_or_text_stroke_runs=groups,accepted_physical_rule_x=xs,qualification='Header-only pixel locator aid. Whole original eleven physical columns/headers directly reviewed; text-stroke false rules retained unfiltered. No candidate digits, numeric polygons or geographic/current boundaries inferred.'))
                pages[-1]['header_rule_probe']=dict(path=str(q.relative_to(BASE)),bytes=q.stat().st_size,sha256=sha(q.read_bytes()),settings=settings)
        assert dict(sums)==totals==c['candidate_values'],(sid,sums,totals,c['candidate_values']);views.append(dict(source_id=sid,county_fips=fips,raw_sha256=c['raw_sha256'],publication_label=c['publication_label'],publication_variant=c['publication_variant'],county_key=c['county_key'],parent_source_id=c['parent_source_id'],requested_url=c['requested_url'],final_url=c['final_url'],pages=pages,controls=dict(native_candidate_sums=dict(sums),printed_TOTAL=totals,earlier_county_publication_control=c['candidate_values'],all_three_vectors_close=True),qualification='Only this source publication Senate3candidate native partition. Generic/ballot/registration/method fields not printed on selected SEMS rows are unknown; full PDF retains all other offices. Same-name/count across years or amendments is not an identity equivalence.',metadata_acceptance=dict(actual_TOTAL_PDFpage=c['source_page'],actual_TOTAL_physical_column=next(p['total'] for p in pv.values() if p['total']),earlier_TOTAL_accepted=c['source_column_accepted'],earlier_TOTAL_proposed=c['source_column_proposed'],basis='Fresh complete original native table review, independently counting physical columns beforeTOTAL. Earlier proposal ledger remains unchanged.')))
    counts['source_views']=len(views);save(OUT/'native-2020-additional-readings.json',dict(qualification='Independent original complete source-specific native3candidate readings; neither county totals nor 2024 geography substitute for unreviewed native fields.',sources=views,counts=dict(counts),full2020_native_complete=False));writecsv(OUT/'native-2020-additional-candidate-votes.csv',rows);print('Original2020native additional',dict(counts))
if __name__=='__main__':main()
