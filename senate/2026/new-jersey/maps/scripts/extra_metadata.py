from acquire import *
from concurrent.futures import ThreadPoolExecutor
# Item IDs are literal serviceItemId values, never guessed. ArcGIS REST documented
# item constructor: /sharing/rest/content/items/{itemID}; metadata resource appended.
S=[('state-service-item','https://www.arcgis.com/sharing/rest/content/items/764362ac87254d77b976a080f926a6fe','literal serviceItemId; documented ArcGIS item constructor',None,{'f':'json'}),('state-service-xml','https://www.arcgis.com/sharing/rest/content/items/764362ac87254d77b976a080f926a6fe/info/metadata/metadata.xml','literal serviceItemId; ArcGIS item metadata resource'),('burlington-service-item','https://www.arcgis.com/sharing/rest/content/items/96aaa5321bb6462e95efdb2764033488','literal serviceItemId; documented ArcGIS item constructor',None,{'f':'json'}),('arcgis-item-constructor','https://developers.arcgis.com/rest/users-groups-and-items/item/','constructor documentation')]
with ThreadPoolExecutor(max_workers=4) as e:list(e.map(lambda j:fetch(*j),S))
