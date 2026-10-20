from pathlib import Path
import json,gzip
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def main():
 parents=json.loads(gzip.decompress((P/'county-investigations.json.gz').read_bytes()));s=(P/'report-intro.md').read_text()+'\n| County / FIPS | All / priority / remainder | Fresh parent investigation |\n| --- | ---: | --- |\n'
 for p in parents:
  a=p['authority_directory'];clerk=next(r for r in a['roles'] if 'Clerk' in str(r['role_literal']));url=clerk['links'][0]['resolved_url'] if clerk['links'] else 'https://nj.gov/state/elections/vote-county-election-officials.shtml';finding=p['findings']['observed_parent_chain'];s+=f"| [{p['county']}]({url}) / {p['parent_key']} | {len(p['rank_ordered_children'])} / {len(p['priority_children'])} / {len(p['remainder_children'])} | {finding.replace('|','/')} |\n"
 s+='\n'+(P/'report-tail.md').read_text();(ROOT/'official-results.md').write_text(s)
if __name__=='__main__':main()
