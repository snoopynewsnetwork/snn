"""Meaningful arithmetic stress scenarios, never calibrated probabilities."""
from source_io import ROOT,dump
from calculator import live,bounded_shift,selected_only
def main():
    cases=[]
    def add(name,counted,remaining,**kw):cases.append(dict(id=name,A='A',B='B',counted=counted,remaining=remaining,**kw))
    def pool(n,q=.5,rho=1,unit='u',**kw):return dict(unit=unit,votes=n,pair_participation=rho,A_pair_share=q,**kw)
    add('unknown-remainder',{'A':40,'B':50,'C':10},[pool(None)])
    add('negative-remainder',{'A':40,'B':50,'C':10},[pool(-1)])
    add('no-pool-secured-pair',{'A':60,'B':40,'C':0},[pool(0,None,None)])
    add('no-pool-pair-tie',{'A':40,'B':40,'C':10},[])
    add('no-pool-impossible-pair',{'A':30,'B':50,'C':10},[pool(0)])
    add('positive-pool-impossible',{'A':0,'B':100,'C':0},[pool(20,1)])
    add('positive-pool-secured',{'A':100,'B':0,'C':0},[pool(20,0)])
    add('pair-win-other-candidate-wins',{'A':40,'B':35,'C':200},[pool(20,1)])
    add('clipping-high-share',{'A':40,'B':50,'C':10},[pool(100,1.3)])
    add('clipping-low-share',{'A':40,'B':50,'C':10},[pool(100,-.2)])
    add('unknown-preference',{'A':40,'B':50,'C':10},[pool(100,None)])
    add('unknown-pair-participation',{'A':40,'B':50,'C':10},[pool(100,.5,None)])
    add('unknown-other-allocation',{'A':40,'B':50,'C':10},[pool(100,.5,.8)])
    add('mixed-final-denominator',{'A':40,'B':60,'C':10},[pool(100,.7,.8,other_shares={'C':1})],selected_unit='u')
    add('all-other-remainder',{'A':40,'B':50,'C':10},[pool(100,None,0,other_shares={'C':1})])
    add('strict-plurality-tie',{'A':40,'B':60,'C':0},[pool(100,.6)])
    add('selected-small-pool-impossible',{'A':0,'B':100,'C':0},[pool(10,.8,unit='selected'),pool(10,.4,unit='other')],selected_unit='selected')
    add('selected-only-feasible',{'A':40,'B':60,'C':10},[pool(70,.6,unit='selected'),pool(30,.4,unit='other')],selected_unit='selected')
    add('corrected-count-snapshot',{'A':35,'B':60,'C':10},[pool(100,.7,.8,other_shares={'C':1})])
    add('invalid-negative-counts',{'A':-1,'B':40,'C':10},[pool(20)])
    dump(ROOT/'live-synthetic-inputs.json',cases)
    dump(ROOT/'live-synthetic-results.json',[dict(id=c['id'],result=live(c))for c in cases])
    bounded=[]
    for name,units,target in [('clipped-tie',[{'volume':90,'share':.9},{'volume':10,'share':.05}],0),('clipped-Aplus1',[{'volume':10,'share':.99},{'volume':90,'share':.2}],.01),('impossible-margin',[{'volume':100,'share':.5}],1.1),('no-positive-pool',[{'volume':0,'share':None}],0),('unknown-positive-preference',[{'volume':10,'share':None}],0),('negative-volume',[{'volume':-1,'share':.5}],0),('already-winning-negative-shift',[{'volume':100,'share':.65}],0)]:
        bounded.append(dict(id=name,units=units,target_margin=target,result=bounded_shift(units,target)))
    dump(ROOT/'bounded-synthetic-results.json',bounded)
if __name__=='__main__':main()
