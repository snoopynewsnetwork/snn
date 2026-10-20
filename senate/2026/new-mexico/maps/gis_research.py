from common import *
import concurrent.futures
jobs=[('rgis-folders','https://rgis.unm.edu/gstore/folders.json','gis-link-57','literal /gstore/folders.json constructor in clearinghouse HTML'),('rgis-js','https://rgis.unm.edu/rgis6/javascript/rgis.js','gis-link-57','literal script src javascript/rgis.js'),('experience-item','https://www.arcgis.com/sharing/rest/content/items/5341868bd5634feebf46f60f94c6e89e?f=pjson','gis-link-58','ArcGIS public item metadata constructor; item ID taken verbatim from SOS-linked app URL'),('experience-data','https://www.arcgis.com/sharing/rest/content/items/5341868bd5634feebf46f60f94c6e89e/data?f=pjson','gis-link-58','ArcGIS public item data constructor; item ID taken verbatim from SOS-linked app URL')]
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for r in pool.map(lambda x:fetch(*x),jobs):print(r['id'],r.get('status'),r.get('error'))
