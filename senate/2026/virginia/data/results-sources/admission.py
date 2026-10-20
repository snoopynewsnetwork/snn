"""Pure source-research admission guards. No ingestion, forecast or collector."""
from replay import strict,semantic
def full_context(observed,expected):
    if semantic(observed)!=semantic(expected):raise ValueError('complete source context differs')
def vote_admission(election,contest,evidence):
    issues=[]
    if election.get('electionDate')!='2026-11-03':issues.append('wrong election')
    if election.get('isPrimary') is not False:issues.append('primary or missing stage')
    if election.get('isProduction') is not True:issues.append('staging/test or missing production context')
    if contest.get('id')!=evidence.get('observed_contest_id'):issues.append('wrong contest ID')
    names=[x.get('text') for x in contest.get('name',[]) if x.get('languageId')=='en']
    if names!=['Member, United States Senate']:issues.append('wrong contest')
    if evidence.get('complete_body_verified') is not True:issues.append('truncated or unverified entity')
    if evidence.get('authority_chain_verified') is not True:issues.append('unproved authority')
    if evidence.get('genuine_release_verified') is not True:issues.append('genuineness unproved')
    if evidence.get('date_of_genuine_release','')<'2026-11-03':issues.append('pre-election/setup')
    if not isinstance(contest.get('voteTotal'),int) or isinstance(contest.get('voteTotal'),bool) or contest['voteTotal']<=0:issues.append('no genuine positive candidate vote universe established')
    return {'admitted':not issues,'issues':issues}
def partition(scopes):
    if not scopes:raise ValueError('missing partition')
    levels={s['level'] for s in scopes}
    if len(levels)!=1:raise ValueError('overlapping state/local/native levels')
    keys=[(s['election_id'],s['contest_id'],s['parent_id'],s['native_id'],s['method_id']) for s in scopes]
    if len(set(keys))!=len(keys):raise ValueError('duplicate observation keys')
    if len({s['snapshot'] for s in scopes})!=1:raise ValueError('mixed snapshots; cumulative overlap')
    return True
