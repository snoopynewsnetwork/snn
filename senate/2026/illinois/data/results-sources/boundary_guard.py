"""Source admission and navigation guards; this is offline QA, never a collector."""
from urllib.parse import urlsplit
import math
BLOCK_HOSTS=('facebook.com','twitter.com','instagram.com','reddit.com','plus.google.com','linkedin.com','t.co')
def allowed_public_url(url):
 p=urlsplit(url);h=(p.hostname or '').lower();parts=[v.lower() for v in p.path.split('/')]
 return p.scheme in ('http','https') and not any(h==b or h.endswith('.'+b) for b in BLOCK_HOSTS) and not any(x in parts for x in ['admin','security','myaccount','login','signin','profilecreate','antiforgery'])
def admission(x):
 reasons=[]
 if x.get('election_date')!='2026-11-03':reasons.append('wrong_or_unknown_election')
 if x.get('contest')!='U.S. Senate':reasons.append('wrong_or_unknown_contest')
 for key in ['navigation_verified','contest_keys_verified','choice_keys_verified','unit_keys_verified','all_source_fields_preserved','eligible_scope_verified','genuine_november_returns','coordinator_approval']:
  if x.get(key) is not True:reasons.append(key+'_required')
 if x.get('stage') in ['setup','test','primary','historical','shell','blocked','empty']:reasons.append('non_return_stage')
 count=x.get('votes')
 if isinstance(count,bool) or not isinstance(count,int) or count<0:reasons.append('invalid_or_missing_vote_count')
 return dict(admitted=not reasons,reasons=reasons)
def exact_remainder(x):
 if x.get('eligible') is True and x.get('unprocessed') is True and x.get('explicit_official_status') is True:
  v=x.get('count')
  if isinstance(v,int) and not isinstance(v,bool) and v>=0:return v
 return None
