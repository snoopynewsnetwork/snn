from common import *
expected={
 'turnout.md':'c9f89b6334d961d0d0daa32f583a74ef11078ffa38d452f55688e2ba63d2fafa',
 'data/turnout/asset-manifest.json':'591cb2c893a377c9e56c2480a599dec290dfd68d8ac7baa51319bba70c4e4220',
 'county-partisanship.md':'7951f084f0ac62996df5b09a54a9dd59f64c05506c500b9c14c83d668831bd4b',
 'data/county-baselines.csv':'940c99db5c49586cda8f6a9085d1faea60bfb67fd20e2fc4ca186ff597e5542d',
 'data/baselines/asset-manifest.json':'bd089283cb93d3e74105da216a9d280e4d9f2b4b282054abeff0dcd3a44a0418',
 'data/turnout/priority-set.json':'1f589d2785d985af2eb33de50adad5a398924ab55f9343deaf79ac5c7378d97a'}
r=[]
for p,h in expected.items():
 b=(GA/p).read_bytes();assert sha(b)==h;r.append({'path':p,'bytes':len(b),'sha256':h,'immutable':True})
for p in ['data/coordinator-priority-acceptance.json','data/coordinator-priority-membership-review.json','data/coordinator-native-contract-review.json']:
 b=(GA/p).read_bytes();r.append({'path':p,'bytes':len(b),'sha256':sha(b),'role':'external coordinator acceptance/review; no reverse hash cycle'})
save(ROOT/'frozen-inputs.json',r)
print('6 frozen reports/vectors/manifests + external acceptance3 pinned')
