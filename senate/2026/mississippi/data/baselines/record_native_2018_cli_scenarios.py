"""Meaningful offline CLI examples: impossible, literalXunknown and no-positive-pool."""
import contextlib,io,json
from native_2018_calculator import load_inputs,selected_cli
from sources import OUT,save

def main():
 _,_,units,admins=load_inputs();chosen=[units[0],next(u for u in units if u['pair_votes'] is None),admins[0]];outputs=[]
 for u in chosen:
  s=io.StringIO()
  with contextlib.redirect_stdout(s):selected_cli(u['source_key'],0,0)
  outputs.append(json.loads(s.getvalue()))
 assert [d['status'] for d in outputs]==['impossible','unknown_source_mark','no_positive_pool'] and all(d['state_counties']==82 for d in outputs)
 save(OUT/'native-2018-selected-cli-scenarios.json',dict(qualification='Offline exactstage selected-unit demonstration, other known units fixed at observed source preferences; unknown marks/source residual retained. Arithmetic not probability/2026projection.',scenarios=outputs))
 print('PASS2018selected CLI impossible/unknown/no-positive-pool')
if __name__=='__main__':main()
