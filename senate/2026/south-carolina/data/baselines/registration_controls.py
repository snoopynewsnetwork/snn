"""Independent original native registration/ballot control reconciliation."""
from legacy_extract import *
def main():
    out=[]
    for lab in LABELS:
        year=lab[:4];cf=json.loads((SRC/'county-fips-crosswalk.json').read_text())['counties']
        for county in cf:
            if year=='2022' and county=='Clarendon':continue
            sid='legacy'+year+'-county-'+county.lower();root,_=xml(sid);v=root.find('VoterTurnout');rs=list(v.find('Precincts'))
            reg=sum(int(r.get('totalVoters'))for r in rs);ballots=sum(int(r.get('ballotsCast'))for r in rs);R=int(v.get('totalVoters'));B=int(v.get('ballotsCast'))
            out.append(dict(contest_label=lab,source_id=sid,county=county,source_clock=root.findtext('Timestamp'),county_registered=R,native_registered_sum=reg,registered_difference=R-reg,county_ballots=B,native_ballots_sum=ballots,ballots_difference=B-ballots,source_native_turnout_rows=len(rs),source_pointer='/ElectionResult/VoterTurnout',note='source registration universes retained; no reallocation/normalization'))
    dump(BASE/'legacy-registration-reconciliation.json',dict(contexts=len(out),registration_disagreements=sum(r['registered_difference']!=0 for r in out),ballots_disagreements=sum(r['ballots_difference']!=0 for r in out),rows=out,Clarendon2022='XML disabled; pinned TXT/JSON registration controls zero, later current JSON registration nonzero; no source-vintage substitution'))
    print(compact(dict(contexts=len(out),registration_disagreements=sum(r['registered_difference']!=0 for r in out),ballots_disagreements=sum(r['ballots_difference']!=0 for r in out))))
if __name__=='__main__':main()
