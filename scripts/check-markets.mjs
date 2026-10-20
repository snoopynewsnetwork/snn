import { readFile } from "node:fs/promises";

// Check src/markets.json against the live exchanges: every market must be
// open, belong to the mapped event, and name the race's state along with the
// candidate's party or the candidate.
const races = JSON.parse(
  await readFile(new URL("../src/markets.json", import.meta.url), "utf8"),
);
const kalshi = "https://api.elections.kalshi.com/trade-api/v2";
const partyWords = {
  Democratic: /Democrat/,
  Republican: /Republican/,
  Independent: /independent/i,
};

async function get(url) {
  const response = await fetch(url, { signal: AbortSignal.timeout(15000) });
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.json();
}

let failures = 0;
for (const [slug, race] of Object.entries(races)) {
  const state = slug
    .split("-")
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ");
  const problems = [];
  try {
    const [event] = await get(
      `https://gamma-api.polymarket.com/events?slug=${race.polymarketEvent}`,
    );
    if (!event || event.closed)
      problems.push(`Polymarket event ${race.polymarketEvent} is closed`);
    const { event: kalshiEvent, markets } = await get(
      `${kalshi}/events/${race.kalshiEvent}`,
    );
    if (kalshiEvent.series_ticker !== race.kalshiSeries)
      problems.push(
        `Kalshi ${race.kalshiEvent} is in ${kalshiEvent.series_ticker}, not ${race.kalshiSeries}`,
      );
    for (const candidate of race.candidates) {
      const surname = candidate.name.split(" ").at(-1);
      const matches = (text) =>
        text.includes(state) &&
        (partyWords[candidate.party].test(text) || text.includes(surname));
      const poly = event?.markets.find(
        (market) => market.slug === candidate.polymarket,
      );
      if (!poly?.active || poly.closed)
        problems.push(`Polymarket ${candidate.polymarket} is not open`);
      else if (JSON.parse(poly.outcomes)[0] !== "Yes" || !matches(poly.question))
        problems.push(`${candidate.name}: Polymarket asks "${poly.question}"`);
      const market = markets.find((item) => item.ticker === candidate.kalshi);
      if (market?.status !== "active")
        problems.push(`Kalshi ${candidate.kalshi} is not open`);
      else if (!matches(market.rules_primary))
        problems.push(`${candidate.name}: Kalshi rules "${market.rules_primary}"`);
    }
  } catch (error) {
    problems.push(error.message);
  }
  failures += problems.length;
  console.log(
    problems.length
      ? `✗ ${slug}\n  ${problems.join("\n  ")}`
      : `✓ ${slug} (${race.candidates.map((candidate) => candidate.name).join(", ")})`,
  );
}
if (failures) {
  console.error(`${failures} market problem(s) found.`);
  process.exitCode = 1;
} else console.log(`All ${Object.keys(races).length} races match.`);
