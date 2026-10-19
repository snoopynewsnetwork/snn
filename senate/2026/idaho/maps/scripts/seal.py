#!/usr/bin/env python3
"""Create a complete owned-membership seal only after passing preseal research QA."""
import hashlib,json
from evidence import MAPS,ROOT,sha
from validate import manifest_paths

def main():
 qa=json.loads((MAPS/'qa/validation.json').read_text());assert qa['status']=='pass_preseal_research_validation'
 owned=[]
 for path,p in sorted(manifest_paths().items()):
  b=p.read_bytes();assert len(b)<40000000;owned.append(dict(path=path,bytes=len(b),sha256=sha(b)))
 result=dict(schema='ID-maps-complete-owned-seal-v1',status='sealed_historical_research_for_independent_coordinator_review',authority='Coordinator alone reviews/accepts/publishes; this seal is integrity, not selfacceptance',acceptance_path='data/coordinator-priority-acceptance.json',owned_scope=['precinct-maps.md','maps/**'],owned=owned,excluded_owned_files=['maps/manifest.json'],frozen_references_path='maps/frozen-references.json',frozen_references_sha256=sha((MAPS/'frozen-references.json').read_bytes()),source_duplication_policy='Individual full originals once by content hash or immutable exact reference; separate preview derivatives',strict_exclusive_bytes_limit=40000000,current_geography_approved=False,result_polygon_join=None)
 b=(json.dumps(result,indent=2)+'\n').encode();assert len(b)<40000000;(MAPS/'manifest.json').write_bytes(b)
 print(json.dumps(dict(status=result['status'],owned_entries=len(owned),manifest_bytes=len(b),manifest_sha256=sha(b))))
if __name__=='__main__':main()
