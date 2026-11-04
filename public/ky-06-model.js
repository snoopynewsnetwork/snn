// Certified 2024 House comparisons, conditional scenarios, and the separate
// experimental countyForecast fitted to live returns below. Manual scenarios
// keep the historical turnout mix fixed and do not control that forecast.
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

// Uncalibrated extrapolation. Fit a common share shift to matched county
// returns, then apply it only to modeled additional votes. Published votes
// are fixed; supplier expected-vote percentages are assumptions, not finality.
export function countyForecast(counties, result, now = Date.now()) {
  const unavailable = reason => ({ status: 'unavailable', reason });
  const age = now - Date.parse(result?.lastSuccessAt);
  if (result?.status !== 'reporting' || !Number.isFinite(age) || age < -60_000 || age > 15 * 60_000)
    return unavailable('Waiting for fresh, verified county returns. Saved counts remain available below.');
  const coverage = countyCoverage(counties, result);
  if (!coverage || result.coverage !== 'complete') return unavailable('A complete, reconciled set of 16 county portions is required.');
  const valid = value => Number.isSafeInteger(value) && value >= 0;
  if (counties.some(c => !valid(c.r) || !valid(c.d) || countyTotal(c) <= 0) ||
      coverage.rows.some(c => !valid(c.liveR) || !valid(c.liveD) || !valid(c.liveOther)))
    return unavailable('County baseline or reported counts failed validation.');
  const countedR = coverage.rows.reduce((sum, c) => sum + c.liveR, 0);
  const countedD = coverage.rows.reduce((sum, c) => sum + c.liveD, 0);
  const counted = countedR + countedD;
  const countedOther = coverage.rows.reduce((sum, c) => sum + c.liveOther, 0);
  if (counted + countedOther !== result.totalVotes || ['DEM', 'REP'].some(party => {
    const rows = result.candidates?.filter(c => c.party === party);
    return rows?.length !== 1 || rows[0].votes !== (party === 'DEM' ? countedD : countedR);
  })) return unavailable('County and district candidate totals must reconcile within the county source.');
  const reporting = coverage.rows.filter(c => c.liveR + c.liveD > 0);
  const baselineTotal = counties.reduce((sum, c) => sum + countyTotal(c), 0);
  const reportingWeight = reporting.reduce((sum, c) => sum + countyTotal(c), 0) / baselineTotal * 100;
  // Readiness guardrails, not a statistical confidence claim.
  if (counted < 5000 || reporting.length < 3 || reportingWeight < 20)
    return unavailable('Need at least 5,000 two-party votes in three counties covering 20% of the historical district vote.');
  const completion = result.estimatedVotePercent;
  if (!Number.isFinite(completion) || completion <= 0 || completion > 100)
    return unavailable('The county source has no usable district expected-vote estimate.');
  const turnoutScale = counted / (completion / 100) / baselineTotal;
  const shift = reporting.reduce((sum, c) => sum + c.liveD - (c.liveR + c.liveD) * c.d / countyTotal(c), 0) / counted;
  const bounded = share => Math.max(0, Math.min(1, share));
  const rows = coverage.rows.map(c => {
    const live = result.counties.find(row => row.name === c.name);
    const published = c.liveR + c.liveD;
    const estimate = live.estimatedVotePercent;
    // A known positive county uses its own CNN estimate. Missing counties use
    // 2024 House weights scaled to CNN's district two-party turnout estimate.
    const hasEstimate = Number.isFinite(estimate) && estimate > 0 && estimate <= 100;
    const expected = published && hasEstimate ? published / (estimate / 100) : countyTotal(c) * turnoutScale;
    return { name: c.name, countedR: c.liveR, countedD: c.liveD, countedOther: c.liveOther,
      remaining: Math.max(0, Math.round(expected) - published),
      share: bounded(c.d / countyTotal(c) + shift), volumeSource: published && hasEstimate ? 'supplier' : 'historical-weight' };
  });
  const project = (volumeScale = 1, shareShift = 0) => {
    const projected = rows.map(c => {
      const remaining = Math.round(c.remaining * volumeScale);
      const additionalD = Math.round(remaining * bounded(c.share + shareShift));
      return { ...c, remaining, r: c.countedR + remaining - additionalD, d: c.countedD + additionalD };
    });
    const r = projected.reduce((sum, c) => sum + c.r, 0), d = projected.reduce((sum, c) => sum + c.d, 0);
    return { r, d, total: r + d, margin: 100 * (d - r) / (r + d), counties: projected };
  };
  const central = project();
  const sensitivity = [central.margin];
  for (const volume of [.8, 1, 1.2]) for (const share of [-.05, .05]) sensitivity.push(project(volume, share).margin);
  return { status: 'estimate', ...central, countedR, countedD, countedOther, shift: shift * 100, reportingCount: reporting.length,
    reportingWeight, turnoutScale, remaining: central.total - counted,
    low: Math.min(...sensitivity), high: Math.max(...sensitivity), verifiedAt: result.lastSuccessAt };
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
