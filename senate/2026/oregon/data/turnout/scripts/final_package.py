#!/usr/bin/env python3
"""Acyclic complete current package seal; default is a read-only final audit.
Only manifest itself is excluded. No validation/finalseal reverse CURRENT hash.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,json,subprocess,os,re,gzip
from reciprocal import T,S,O,P,sha,enc

def owned():return [S/'turnout.md',S/'data/county-turnout.csv']+sorted(p for p in T.rglob('*')if p.is_file())
def record(p):
 b=p.read_bytes();assert len(b)<40000000
 return dict(path=p.relative_to(S).as_posix(),bytes=len(b),sha256=sha(b))
def run(n,*args):
 r=subprocess.run([sys.executable,'-B',str(T/'scripts'/n),*args],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
 assert r.returncode==0,dict(script=n,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
 return dict(script=n,status='pass',stdout=r.stdout.strip())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seal',action='store_true');a=ap.parse_args()
 if a.seal:
  if not (T/'finalseal.json').exists():(T/'finalseal.json').write_bytes(b'{}\n')
  run('validate.py','--write')
  pinpaths=['turnout.md','data/county-turnout.csv','data/turnout/priority-set.json','data/turnout/validation.json','data/turnout/peer-reconciliation.json','data/turnout/source/reciprocal-full-evidence.json.gz','data/turnout/source/offline-rebuild.json','data/turnout/source/corruption-fixtures.json','data/turnout/source/SCHEMA.md','data/turnout/source/history/pre-reciprocal-v1/inventory.json','data/turnout/source/peer-capture-v1/inventory.json']
  seal=dict(schema='oregon.turnout.finalseal.v2',scheme='acyclic: finalseal pins validation/research bodies; current manifest pins every owned body except itself; no reverse current-manifest digest',pins=[record(S/p)for p in pinpaths],own_original_first_witness_sha256='d2b433035d5671178fda01261f0d35a6d13d95ab9c9a2204192ea138eda291b9',peer_final_manifest_sha256='c725c0069e8409d9667ef0ce674a14bea20456410bdee4e50eb0e44b4e5846b9',peer_agent_id='7c03df8c-f908-40a8-a289-369e4aa26e69',agreement='bounded captured source core with explicit historical extraction differences only',canonical_statewide_native_priority_available=False,coordinator_accepted=False,current_source_accepted=False,current_geometry_accepted=False)
  (T/'finalseal.json').write_bytes(enc(seal))
  mf=dict(schema_version='oregon.turnout.asset-manifest.v2',self_exclusion='data/turnout/asset-manifest.json only; no other owned exclusions',owned_assets=[record(p)for p in sorted(owned())if p!=T/'asset-manifest.json'],shared_assets=O.js('data/turnout/asset-manifest.json')['shared_assets'],original_reconstruction='Complete historical inventories restore every prior body. Original response entities and huge ZIP byteparts remain once by immutable raw/stored hash references; all72members CRC/hash/position checked. See source/SCHEMA.md.',strict_individual_artifact_byte_limit=40000000)
  (T/'asset-manifest.json').write_bytes(enc(mf))
 # Everything below is read-only in the owned tree, including after --seal.
 initial={p.relative_to(S).as_posix():(p.stat().st_size,sha(p.read_bytes()))for p in owned()}
 mf=json.loads((T/'asset-manifest.json').read_bytes());expected=set(initial)-{'data/turnout/asset-manifest.json'};actual=set()
 for r in mf['owned_assets']+mf['shared_assets']:
  p=(S/r['path']).resolve();assert p.is_relative_to(S.resolve());b=p.read_bytes();assert (len(b),sha(b))==(r['bytes'],r['sha256']);assert len(b)<40000000
 for r in mf['owned_assets']:assert r['path']not in actual;actual.add(r['path'])
 assert actual==expected,'exact complete current owned membership'
 assert not list(T.rglob('__pycache__'))
 seal=json.loads((T/'finalseal.json').read_bytes())
 for r in seal['pins']:assert record(S/r['path'])==r
 assert not any('current_manifest'in k or 'manifest_sha'in k and k!='peer_final_manifest_sha256'for k in seal)
 O.verify();P.verify()
 checks=[run('reciprocal.py'),run('corruption_fixtures.py'),run('validate.py')]
 after={p.relative_to(S).as_posix():(p.stat().st_size,sha(p.read_bytes()))for p in owned()};assert initial==after,'final audit must leave every byte/membership frozen'
 print(json.dumps(dict(status='pass',read_only_final_audit=True,owned_files=len(initial),manifest_assets=len(actual),shared_assets=len(mf['shared_assets']),maximum_owned_bytes=max(v[0]for v in initial.values()),manifest_sha256=sha((T/'asset-manifest.json').read_bytes()),finalseal_sha256=sha((T/'finalseal.json').read_bytes()),validation_sha256=sha((T/'validation.json').read_bytes()),priority_contract_sha256=sha((T/'priority-set.json').read_bytes()),county_csv_sha256=sha((S/'data/county-turnout.csv').read_bytes()),checks=checks,coordinator_accepted=False,canonical_statewide_priority_available=False),indent=2))
if __name__=='__main__':main()
