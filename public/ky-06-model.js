// Conditional two-party scenarios, anchored to certified 2024 House votes.
// County turnout mix stays fixed. A common Democratic share shift is solved
// with shares bounded to [0, 1]; this is not a fitted election forecast.
export const countyTotal = county => county.r + county.d;
export const countyMargin = county => 100 * (county.d - county.r) / countyTotal(county);

export function countyCoverage(counties, result) {
  if (!result?.counties || result.counties.length !== counties.length) return null;
  const rows = counties.map(baseline => {
    const live = result.counties.find(c => c.name === baseline.name);
    if (!live) return null;
    const r = live.candidates.filter(c => c.party === 'REP'), d = live.candidates.filter(c => c.party === 'DEM');
    if (r.length !== 1 || d.length !== 1) return null;
    return { ...baseline, liveR: r[0].votes, liveD: d[0].votes, liveOther: live.totalVotes - r[0].votes - d[0].votes, published: live.totalVotes };
  });
  if (rows.some(c => c === null)) return null;
  const missing = rows.filter(c => c.published === 0);
  return { rows, missing, missingWeight: missing.reduce((sum, c) => sum + countyTotal(c), 0) / counties.reduce((sum, c) => sum + countyTotal(c), 0) * 100 };
}

export function scenarioRemaining(scenario, coverage) {
  if (!coverage) return null;
  const rows = scenario.counties.map(c => {
    const live = coverage.rows.find(row => row.name === c.name);
    return { name: c.name, r: c.r - live.liveR, d: c.d - live.liveD };
  });
  const r = rows.reduce((sum, row) => sum + row.r, 0), d = rows.reduce((sum, row) => sum + row.d, 0);
  return { rows, r, d, total: r + d, feasible: rows.every(row => row.r >= 0 && row.d >= 0),
    districtFeasible: r >= 0 && d >= 0, requiredDShare: r >= 0 && d >= 0 && r + d > 0 ? 100 * d / (r + d) : null };
}

function apportion(values, total) {
  const counts = values.map(Math.floor);
  const order = values.map((value, index) => ({ index, remainder: value - counts[index] }))
    .sort((a, b) => b.remainder - a.remainder || a.index - b.index);
  const remaining = total - counts.reduce((sum, value) => sum + value, 0);
  for (let n = 0; n < remaining; n++) counts[order[n].index]++;
  return counts;
}

export function countyScenario(counties, { margin, turnout = 100 }) {
  if (!Number.isFinite(margin) || margin < -100 || margin > 100 ||
      !Number.isFinite(turnout) || turnout < 10 || turnout > 150)
    throw new Error('Use a D-minus-R margin from −100 to 100 and turnout from 10% to 150% of 2024.');
  if (!counties.length || counties.some(c => !Number.isSafeInteger(c.r) || c.r < 0 || !Number.isSafeInteger(c.d) || c.d < 0 || countyTotal(c) <= 0))
    throw new Error('A complete positive county baseline is required.');
  const baselineTotal = counties.reduce((sum, county) => sum + countyTotal(county), 0);
  const total = Math.round(baselineTotal * turnout / 100);
  const volumes = apportion(counties.map(c => countyTotal(c) * turnout / 100), total);
  const targetD = Math.round(total * (1 + margin / 100) / 2);
  const share = (c, shift) => Math.max(0, Math.min(1, c.d / countyTotal(c) + shift));
  let low = -1, high = 1;
  for (let iteration = 0; iteration < 64; iteration++) {
    const shift = (low + high) / 2;
    const d = counties.reduce((sum, c, i) => sum + volumes[i] * share(c, shift), 0);
    if (d < targetD) low = shift;
    else high = shift;
  }
  const shift = (low + high) / 2;
  const dVotes = apportion(counties.map((c, i) => volumes[i] * share(c, shift)), targetD);
  return {
    total, d: targetD, r: total - targetD, margin: 100 * (2 * targetD - total) / total,
    shareShift: Math.abs(shift) < 1e-12 ? 0 : shift * 100,
    counties: counties.map((c, i) => ({ ...c, baselineR: c.r, baselineD: c.d, r: volumes[i] - dVotes[i], d: dVotes[i] })),
  };
}
