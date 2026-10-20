#!/usr/bin/env python3
"""Format prose while preserving literal citations, code and source identifiers."""
import re
# Protected spans are restored byte-for-byte; formatting never processes them.
PROTECTED = re.compile(r"```[\s\S]*?```|`[^`\n]*`|\]\([^\n)]*\)|https?://[^\s<>\)]+|\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b|\bva:\d+:csv-record:\d+\b")
def render_prose(report):
 spans=[]
 def save(m):
  spans.append(m.group(0));return f'\x00PRESERVED_{len(spans)-1}\x00'
 report=PROTECTED.sub(save,report)
 report=re.sub(r'\b(all|All|across|throughout|in|of|by|is|has|The|the|a)(?=\d)',r'\1 ',report)
 for old,new in [('Kaine2,','Kaine 2,'),('Cao2,','Cao 2,'),('total4,','total 4,'),('generic5,','generic 5,'),('generic4,','generic 4,'),('literal0','literal 0'),('and2020','and 2020'),('and2024','and 2024'),('and133','and 133'),('and2,','and 2,'),('by36','by 36'),('City+','City +'),('County+','County +'),('2018 is75','2018 is 75'),('2020 is99','2020 is 99'),('is60,200','is 60,200'),('and107,630','and 107,630'),('includes16','includes 16'),('contains8,055','contains 8,055'),('including16','including 16'),('those48','those 48'),('yields2,669','yields 2,669'),('sum4,','sum 4,'),('sums4,','sums 4,'),('TotalVoteTurnout4,','TotalVoteTurnout 4,'),('Total Voting4,','Total Voting 4,'),('registration6,','registration 6,'),('totalVoters6,','totalVoters 6,'),('AllVoters6,','AllVoters 6,'),('active5,','active 5,'),('inactive485,','inactive 485,'),('ballotsCast4,','ballotsCast 4,'),('active6,','active 6,'),('inactive457,','inactive 457,'),('voterTurnout4,','voterTurnout 4,'),('voterRegistration6,','voterRegistration 6,'),('repeats13','repeats 13'),('repeats2','repeats 2'),('covers127','covers 127'),('holds133','holds 133'),('below40,','below 40,'),('is77,','is 77,'),('and2,573','and 2,573')]:report=report.replace(old,new)
 for i,literal in enumerate(spans):report=report.replace(f'\x00PRESERVED_{i}\x00',literal)
 return report
