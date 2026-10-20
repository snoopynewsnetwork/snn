"""Contracts used on original raw JSON; no geometry adapter."""
def check_params(p):
 banned={'outSR','outCRS','geometryPrecision','quantizationParameters','maxAllowableOffset','datumTransformation','returnCentroid','returnEnvelope'}
 assert not banned.intersection(p)
 assert p['outFields']=='*' and all(p[k]=='true' for k in ['returnGeometry','returnZ','returnM','returnTrueCurves'])
 ids=[int(x) for x in p['objectIds'].split(',')];assert 0<len(ids)<=50 and len(ids)==len(set(ids));return ids

def check_batch(meta,response,expected):
 assert 'error' not in response and not response.get('exceededTransferLimit',False)
 oid=next(f['name'] for f in meta['fields'] if f['type']=='esriFieldTypeOID');features=response['features'];ids=[f['attributes'][oid] for f in features]
 assert len(ids)==len(set(ids)) and set(ids)==set(expected)
 wanted={f['name'] for f in meta['fields'] if f['type']!='esriFieldTypeGeometry'}
 for f in features:assert set(f['attributes'])==wanted
 assert response['spatialReference']['wkid']==meta['extent']['spatialReference']['wkid']
 assert all(k in meta['extent']['spatialReference'] and meta['extent']['spatialReference'][k]==v for k,v in response['spatialReference'].items())
 return ids

def check_snapshot(pre_meta,post_meta,pre_layer,post_layer,pre_count,post_count,pre_ids,post_ids):
 assert pre_meta==post_meta and pre_layer==post_layer
 assert pre_count==post_count==len(pre_ids)==len(post_ids)==len(set(pre_ids))==len(set(post_ids)) and set(pre_ids)==set(post_ids)
