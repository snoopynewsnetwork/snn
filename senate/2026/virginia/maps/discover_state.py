"""Resolve full parent inventory to actual linked state originals, not URL templates."""
import json, re
from html.parser import HTMLParser
from urllib.parse import urljoin
from acquire import HERE, entity

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.active=None
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href'): self.active={'href':attrs['href'],'text':''}
    def handle_data(self, data):
        if self.active is not None: self.active['text']+=data
    def handle_endtag(self, tag):
        if tag=='a' and self.active is not None: self.links.append(self.active); self.active=None

def links(key):
    r=json.loads((HERE/'requests'/f'{key}.json').read_bytes()); p=Links();p.feed(entity(r).decode('utf-8',errors='replace'))
    return [{**a,'url':urljoin(r['final_url'],a['href'])} for a in p.links]

def main():
    c=json.loads((HERE.parent/'data/turnout/priority-set.json').read_bytes())
    gis=[a for a in links('elect-gis') if '/media/redistricting/' in a['url'] and a['url'].lower().endswith('.zip')]
    pdf=[a for a in links('elect-maps') if '/media/redistricting/' in a['url'] and a['url'].lower().endswith('.pdf')]
    def label(a):
        # Filename is a published link identifier, used solely to select its
        # county-equivalent parent. No precinct equivalence follows.
        name=a['href'].split('/')[-1].rsplit('.',1)[0]
        return re.sub(r'_(?:COMBINED_)?\d{8}$','',name).replace('_',' ').casefold()
    inventory=[]
    for parent in c['parent_inventory']:
        name=parent['historical_literal_label']; g=[a for a in gis if label(a)==name.casefold()]; p=[a for a in pdf if label(a)==name.casefold()]
        assert len(g)==len(p)==1,(name,g,p)
        inventory.append({'parent_key':parent['historical_parent_key'],'parent_label':name,'fips':parent['fips'],'priority_children':sum(u['key'] in set(c['ordered_priority_keys']) for u in c['ordered_units'] if u['parent_key']==parent['historical_parent_key']), 'gis_link':g[0], 'pdf_link':p[0]})
    assert len(inventory)==133 and sum(p['priority_children']>0 for p in inventory)==108
    (HERE/'state-link-plan.json').write_text(json.dumps({'source_pages':['requests/elect-gis.json','requests/elect-maps.json'],'parents':inventory},indent=2)+'\n')
    print('133 exact parent links; 108 priority parents')

if __name__=='__main__':main()
