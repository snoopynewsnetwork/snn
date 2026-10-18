#!/usr/bin/env python3
"""Replay recorded actual requests into a new evidence directory, never overwrite originals."""
import argparse,json,pathlib
import acquire
p=argparse.ArgumentParser();p.add_argument('--out',required=True,help='New or partially replayed evidence directory');a=p.parse_args();plan=json.loads((acquire.ROOT/'source/acquisition-plan.json').read_text());acquire.ROOT=pathlib.Path(a.out).resolve();(acquire.ROOT/'source').mkdir(parents=True,exist_ok=True);(acquire.ROOT/'derived').mkdir(exist_ok=True)
for r in plan:acquire.fetch(r['id'],r['url'],r['parent'],r['note'],r['kind'])
