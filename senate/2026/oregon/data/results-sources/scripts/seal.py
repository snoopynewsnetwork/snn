"""Authorized owned-only packaging: validation, finalseal, self-only manifest LAST."""
from pathlib import Path
from replay_inputs import R,S,sha
from packaging import owned,MANIFEST
from audit import preseal
import json

def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def ref(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
def main():
 write(R/'validation.json',preseal())
 paths=[S/'official-results.md',S/'data/official-results-sources.csv',R/'validation.json',R/'coverage-validation.json',R/'input-replay.json',R/'original-replay.json',R/'fixtures.json',R/'SCHEMA.md',R/'acquisition-index.json',R/'current-observations.json']+sorted((R/'scripts').glob('*.py'))+sorted((R/'references').glob('*.gz'))
 write(R/'finalseal.json',{'schema':'OR-official-results-acyclic-finalseal-v1','external_acceptance_authority':'data/coordinator-source-research-acceptance.json','status':'bounded_worker_research_complete_pending_coordinator_review','fixed_inputs':[ref(p) for p in paths],'whole_source_counts':{'roots':23,'companions':1994,'recursive_containers':495672,'frozen_current_file_pins':5029,'historical_bodies':5261,'parents':36,'known_contexts':510,'unavailable_parent_cases':31},'canonical_native_priority':None,'coordinator_acceptance':False,'current_approvals':False,'digest_cycle':False})
 files=owned();rows=[ref(files[p]) for p in sorted(files) if p!=MANIFEST]
 write(R/'asset-manifest.json',{'schema':'OR-official-results-self-only-manifest-v1','excluded':[MANIFEST],'file_count':len(rows),'files':rows})
 print('sealed',len(rows),'manifest targets; next and final operation must be read-only audit')
if __name__=='__main__':main()
