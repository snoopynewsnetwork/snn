export function reportingProgress(live, now = Date.now()) {
  const age = now - Date.parse(live?.lastSuccessAt ?? '');
  if (!live || live.status !== 'reporting' || live.coverage === 'partial' || live.members ||
      !(live.totalVotes > 0) || !Number.isFinite(age) || age < -60_000 || age > 15 * 60_000) return '';
  const percent = live.estimatedVotePercent;
  if (typeof percent === 'number' && Number.isFinite(percent) && percent >= 0 && percent <= 100)
    // Round down so an unfinished count never displays as 100%.
    return `${percent > 0 && percent < 1 ? '<1' : Math.floor(percent)}% est. votes counted`;
  const reported = live.reportedPrecincts, total = live.totalPrecincts;
  if (Number.isInteger(reported) && Number.isInteger(total) && reported >= 0 && total > 0 && reported <= total)
    return `${reported.toLocaleString('en-US')} / ${total.toLocaleString('en-US')} precincts reporting`;
  return '';
}

export function signalFor(item, observation) {
  if (observation?.sourceKind && observation.sourceStatus !== 'reporting') return null;
  if (!observation || observation.status === 'awaiting' || item.chamber === 'cue') return null;
  const { margin, winner, gopSeats } = observation;
  if (item.chamber === 'senate') {
    if (typeof margin !== 'number' || winner === 'other') return null;
    const index = item.ranges.findIndex(range =>
      (range.min === null || (range.minExclusive ? margin > range.min : margin >= range.min)) &&
      (range.max === null || (range.maxExclusive ? margin < range.max : margin <= range.max)));
    return index < 0 ? null : ['riptide', 'tide', 'wave', 'tsunami'][index];
  }
  if (item.group) return gopSeats !== null && gopSeats >= item.gopBar ? 'riptide' : null;
  if (winner === 'other' || winner === 'I') return null;
  const lead = winner === 'D' ? 1 : winner === 'R' ? -1 : margin;
  if (lead === null || lead === 0 || item.band === 'late') return null;
  if (item.winBand) {
    if (lead > 0) return item.winBand;
    return margin !== null && margin <= -item.gopBar ? 'riptide' : null;
  }
  if (item.party === 'D' && lead < 0) return 'riptide';
  if (item.band === 'riptide') return null;
  return lead > 0 ? item.band : null;
}

export function easternMinutes(now = new Date()) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
  }).formatToParts(now).map(part => [part.type, part.value]));
  const date = `${parts.year}-${parts.month}-${parts.day}`;
  return (Date.parse(`${date}T00:00:00Z`) - Date.parse('2026-11-03T00:00:00Z')) / 86400000 * 1440 + Number(parts.hour) * 60 + Number(parts.minute);
}

export function closeMinutes(close) {
  const [hour, minute] = close.split(':').map(Number);
  return hour * 60 + minute;
}

export function timeLabel(close) {
  const [hour, minute] = close.split(':').map(Number);
  return `${hour % 12 || 12}${minute ? `:${String(minute).padStart(2, '0')}` : ''}${hour % 24 < 12 ? 'am' : 'pm'}${hour >= 24 ? ' Wed' : ''}`;
}

export function marginLabel(margin, independent = false) {
  if (margin === null || margin === undefined) return 'No margin';
  if (margin === 0) return 'Even';
  return `${margin > 0 ? independent ? 'I' : 'D' : 'R'} +${Math.abs(margin).toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
}
