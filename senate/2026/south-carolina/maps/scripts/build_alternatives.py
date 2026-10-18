#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
from build_geometry import *
from acquire_alternatives import SOURCES
import pyproj

def run():
 out=[]
 for n,url,parent in SOURCES:
  layer=js(n+'-layer');oid=layer.get('objectIdField',next(x['name'] for x in layer['fields'] if x['type']=='esriFieldTypeOID'));entries=[];pages=[]
  for p in sorted((ROOT/'raw').glob(n+'-page-*.request.json')):
   d,ee=slices(p.name.removesuffix('.request.json'));entries+=ee;pages.append({'capture':p.name.removesuffix('.request.json'),'count':len(ee),'spatialReference':d.get('spatialReference'),'exceededTransferLimit':d.get('exceededTransferLimit'),'transform':d.get('transform')});assert not d.get('exceededTransferLimit') and not d.get('transform')
  ids=[f['attributes'][oid] for f,_,_ in entries];expected=js(n+'-pre-ids')['objectIds'];assert len(ids)==len(set(ids))==js(n+'-pre-count')['count'];assert set(ids)==set(expected)==set(js(n+'-post-ids')['objectIds']);assert js(n+'-pre-count')==js(n+'-post-count')
  sr=pages[0]['spatialReference'];crs=pyproj.CRS.from_epsg(sr.get('latestWkid',sr.get('wkid')));units=crs.axis_info[0].unit_name;features=[];gg=[]
  for f,loc,raw in entries:
   g,d=geometry(f)
   d={k.replace('sq_international_feet','square_CRS_units').replace('international_feet','CRS_units'):v for k,v in d.items()};features.append({'attributes':f['attributes'],'original_locator':loc,'geometry_diagnostics':d});gg.append(g)
  overlaps=[];skips=[]
  for i,a in enumerate(gg):
   for j in range(i+1,len(gg)):
    b=gg[j]
    if a is None or b is None or not a.is_valid or not b.is_valid:skips.append([ids[i],ids[j]]);continue
    if not a.envelope.intersects(b.envelope):continue
    ar=a.intersection(b).area
    if ar>0:overlaps.append({'a_id':ids[i],'b_id':ids[j],'area_square_CRS_units':ar})
  out.append({'source_id':n,'url':url,'parent':parent,'schema':'raw/'+n+'-layer.body.gz','geometry_count':len(ids),'pre_post_count_equal':True,'pre_post_all_ID_sets_equal':True,'all_ids':sorted(ids),'pages':pages,'crs':sr,'CRS_name':crs.name,'coordinate_units':units,'unit_meters':crs.axis_info[0].unit_conversion_factor,'hasZ':layer.get('hasZ'),'hasM':layer.get('hasM'),'true_curves_returned':sum(x['geometry_diagnostics']['curves'] for x in features),'features':features,'positive_area_overlaps':overlaps,'skipped_pairs':skips,'interpretation':'Separate county publication; no equivalence to statewide geometry, historic result IDs, 2024 election snapshot or legally approved November reporting roster established.'})
 dump('alternative-native-audit.json.gz',out);print([(x['source_id'],x['geometry_count'],x['CRS_name'],len(x['positive_area_overlaps'])) for x in out])
if __name__=='__main__':run()
