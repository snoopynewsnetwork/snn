"""Reconstruct a complete acquired HTTP entity, or independently replay accepted full source closure.
Usage: python3 reconstruct.py --receipt maps/source/ID.receipt.json --output /private/tmp/original.pdf
       python3 reconstruct.py --contract
"""
from common import *
from acquire import body
import argparse

def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt');p.add_argument('--output');p.add_argument('--contract',action='store_true');a=p.parse_args()
 if a.contract:
  from replay_contract import run
  run();return
 if not a.receipt or not a.output:p.error('receipt and output are required')
 receipt=load(S/a.receipt);raw=body(receipt)
 if receipt.get('error') or not receipt.get('stored_parts'):raise ValueError('No complete entity acquired for this receipt')
 out=Path(a.output).resolve()
 if out.is_relative_to(S) and not out.is_relative_to(M):raise ValueError('Output must remain in maps or outside the state checkout, never a peer path')
 out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
 print(json.dumps(dict(path=str(out),bytes=len(raw),sha256=sha(raw),method=receipt['method'],status=receipt['status'])))
if __name__=='__main__':main()
