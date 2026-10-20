#!/usr/bin/env python3
"""Retained newsroom evidence is never an arithmetic input."""
import xml.etree.ElementTree as ET
from extract_originals import D,BY,body,save
r=BY['news12-senate-general-data'];root=ET.fromstring(body(r));fields=[{'path':'/'+root.tag+'/'+a.tag,'text':a.text} for a in root.findall('./RACE_DATA/*')]
candidates=[{a.tag:a.text for a in c} for c in root.findall('./RACE_CANDIDATES/RACE_CANDIDATE')]
save(D/'quarantine.json',{'source_id':'news12-senate-general-data','source_receipt':r['receipt'],'raw_sha256':r['raw_sha256'],'body_reference':r['body_reference'],'admitted':False,'arithmetic_input':False,'source_metadata':fields,'literal_candidates':candidates,'actual_election_date_field':None,'test_mode_field':None,'count_supplier_verified':False,'complete_native_method_universe_verified':False,'reason':'Positive/winner-flagged October15 future-tagged Senate setup sample reached from primary metadata. Date/test/supplier/coverage unverified; published names/percent/winner flag do not make current counts. Original preserved, never added to historical/live examples.'})
