// Descriptive matched-county comparisons plus an explicit turnout scenario.
// The remaining-vote allocation is not a calibrated forecast or a race call.
export const twoPartyMargin = (d, r) => d + r > 0 ? 100 * (d - r) / (d + r) : null;
export function miCountyModel(baseline, result, { turnout = 80, volume = 'supplier', swing = true } = {}, now = Date.now()) {
  if (!Number.isFinite(turnout) || turnout < 10 || turnout > 150 || !['supplier', 'historical'].includes(volume)) throw new Error('Use turnout from 10% to 150% of 2024.');
  if (!result?.counties || result.counties.length !== baseline.counties.length || result.coverage !== 'complete') return null;
  const byFips = new Map(result.counties.map(c => [c.fips, c]));
  if (byFips.size !== baseline.counties.length) return null;
  const rows = baseline.counties.map(b => {
    const live = byFips.get(b.fips);
    if (!live) return null;
    const d = live.candidates.filter(c => c.party === 'DEM'), r = live.candidates.filter(c => c.party === 'REP');
    if (d.length !== 1 || r.length !== 1 || live.candidates.some(c => !Number.isSafeInteger(c.votes) || c.votes < 0) ||
        live.candidates.reduce((sum, c) => sum + c.votes, 0) !== live.totalVotes) return null;
    const counted = d[0].votes + r[0].votes, baselineTotal = b.d + b.r;
    const margin24 = twoPartyMargin(b.d, b.r), margin26 = twoPartyMargin(d[0].votes, r[0].votes);
    return { ...b, baselineTotal, margin24, margin26, d26: d[0].votes, r26: r[0].votes, other26: live.totalVotes - counted,
      counted, published: live.totalVotes, observedPct24: 100 * counted / baselineTotal,
      swing: margin26 === null ? null : margin26 - margin24,
      netChange: counted ? d[0].votes - r[0].votes - counted * margin24 / 100 : 0,
      supplierPercent: live.estimatedVotePercent };
  });
  if (rows.some(c => !c)) return null;
  const sum = key => rows.reduce((s, c) => s + c[key], 0);
  const d = sum('d26'), r = sum('r26'), other = sum('other26'), counted = d + r;
  if (counted + other !== result.totalVotes || ['DEM', 'REP'].some(p => {
    const cs = result.candidates?.filter(c => c.party === p);
    return cs?.length !== 1 || cs[0].votes !== (p === 'DEM' ? d : r);
  })) return null;
  const age = now - Date.parse(result.lastSuccessAt);
  const fresh = ['setup', 'reporting'].includes(result.status) && Number.isFinite(age) && age >= -60000 && age <= 900000;
  const matchedSwing = counted ? sum('netChange') / counted * 100 : null;
  const baselineTotal = sum('baselineTotal');
  // A pooled comparison reweights 2024 shares by each county's published 2026
  // volume. It controls county mix, not the within-county method/precinct mix.
  const shareShift = swing && matchedSwing !== null ? matchedSwing / 200 : 0;
  for (const c of rows) {
    const supplier = volume === 'supplier' && c.counted > 0 && Number.isFinite(c.supplierPercent) && c.supplierPercent > 0 && c.supplierPercent <= 100;
    c.volumeSource = supplier ? 'CNN county estimate' : '2024 × turnout assumption';
    c.assumedTotal = Math.round(supplier ? c.counted / (c.supplierPercent / 100) : c.baselineTotal * turnout / 100);
    c.headroom = c.assumedTotal - c.counted;
    c.exceeded = c.headroom < 0;
    c.remaining = fresh ? Math.max(0, c.headroom) : null;
    const share = Math.max(0, Math.min(1, c.d / c.baselineTotal + shareShift));
    c.remainingD = fresh ? Math.round(c.remaining * share) : null;
    c.remainingR = fresh ? c.remaining - c.remainingD : null;
    c.remainingNet = fresh ? c.remainingD - c.remainingR : null;
    c.finalD = fresh ? c.d26 + c.remainingD : null;
    c.finalR = fresh ? c.r26 + c.remainingR : null;
  }
  const remaining = fresh ? sum('remaining') : null;
  const finalD = fresh ? sum('finalD') : null, finalR = fresh ? sum('finalR') : null;
  return { rows, fresh, d, r, other, counted, baselineTotal, margin: twoPartyMargin(d, r), matchedSwing,
    missing: rows.filter(c => !c.published), remaining, finalD, finalR,
    finalMargin: fresh ? twoPartyMargin(finalD, finalR) : null,
    impliedTurnout: fresh ? 100 * (finalD + finalR) / baselineTotal : null,
    requiredDToTie: remaining > 0 && (remaining + r - d) / (2 * remaining) >= 0 && (remaining + r - d) / (2 * remaining) <= 1
      ? 100 * (remaining + r - d) / (2 * remaining) : null };
}
