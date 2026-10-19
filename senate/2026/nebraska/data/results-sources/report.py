#!/usr/bin/env python3
"""Render the owned report from its prose template and measured parent inventory."""
import sys
sys.dont_write_bytecode=True
from acquire import D,readj
def main():
    s=readj(D/'build-summary.json');t=(D/'report-template.md').read_text();summary=f"The measured inventory contains **{s['own_receipts']} own request receipts**, **{s['PDFs']} complete PDF text inspections**, and **{s['original_graph_frozen_inputs']} verified frozen input pins**. All 58 priority parents have individual fresh authority-chain requests and current state native-schema responses, covering {s['current_native_rows']:,} candidate rows / {s['current_nonadmin_contexts']:,} nonadministrative current contexts plus their separate administrative contexts. These setup contexts are a different universe from historical dispatch observations."
    rows=['| Priority parent | Historical children / selected | Current nonadmin state contexts | Actual local landing status and publication evidence |','| --- | --- | --- | --- |']
    for p in readj(D/'parent-index.json'):
        if not p['priority_parent']:continue
        j=readj(D/p['path']);local=j['local_publication_chain'];landing=next(x for x in local if x['stage']=='directory-landing');docs=[x for x in local if x['stage']in ['linked-publication','deep-publication','deep-historical']];url=landing['final_url']or landing['requested_url'];note=f"[authority]({url}) HTTP {landing['status']}"
        if docs:
            d=next((x for x in docs if 'result'in x['requested_url'].lower()),docs[0]);note+=f"; [linked publication]({d['requested_url']}) HTTP {d['status']}"
        elif j['directory_complete_fields']['county_portal_row']:
            note+='; individual portal row retained'
        if j['additional_notes']:note+='; '+j['additional_notes'][0].split('.')[0]
        rows.append(f"| [{p['county']}](data/results-sources/{p['path']}) | {p['historical_children']} / {p['priority_children']} | {p['current_native_nonadmin']} | {note.replace('|','/')} |")
    t=t.replace('{{SUMMARY}}',summary).replace('{{PRIORITY_TABLE}}','\n'.join(rows));assert '{{'not in t
    (D.parent.parent/'official-results.md').write_text(t);print('Report written; priority parent table rows',len(rows)-2)
if __name__=='__main__':main()
