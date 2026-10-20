// Prediction-market prices for races with reviewed market mappings.
import mapping from "./markets.json" with { type: "json" };

interface CandidateMarkets {
  name: string;
  party: string;
  // Gamma market slug whose "Yes" outcome is this candidate or party winning.
  polymarket: string;
  // Kalshi market ticker for the same outcome.
  kalshi: string;
}

interface RaceMarkets {
  polymarketEvent: string;
  kalshiSeries: string;
  kalshiEvent: string;
  // How the markets settle, when it differs from the default below.
  settlement?: string;
  candidates: CandidateMarkets[];
}

// markets.json pairs each race's outcomes by party; run
// `npm run check:markets` to verify it against the exchanges. Ticker
// conventions are not reliable: Kalshi lists Kentucky's 2026 race under the
// SENATELA series and Louisiana's under KXSENATELA.
export const raceMarkets: Record<string, RaceMarkets> = mapping;
const defaultSettlement =
  "Both markets settle on which party’s nominee wins the seat.";

type Range = "7d" | "30d";
type Point = [time: number, price: number];

interface Feed {
  latest: number | null;
  history: Point[];
}

export interface MarketOdds {
  updatedAt: string;
  settlement: string;
  sources: { id: string; name: string; url: string; available: boolean }[];
  // Sample times in epoch milliseconds. The last entry is the fetch time.
  times: Record<Range, number[]>;
  candidates: {
    name: string;
    party: string;
    latest: { polymarket: number | null; kalshi: number | null };
    history: Record<
      Range,
      { polymarket: (number | null)[]; kalshi: (number | null)[] }
    >;
  }[];
}

const GAMMA = "https://gamma-api.polymarket.com";
const CLOB = "https://clob.polymarket.com";
const KALSHI = "https://api.elections.kalshi.com/trade-api/v2";
const HOUR = 3_600_000;
const DAY = 24 * HOUR;
const CACHE_TTL = 5 * 60_000;
// Retry sooner when one exchange failed, for example when rate limited.
const PARTIAL_TTL = 60_000;
const cache = new Map<string, { expires: number; value: MarketOdds }>();
const easternClock = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  hourCycle: "h23",
  year: "numeric",
  month: "numeric",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
});

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
      "User-Agent":
        "SnoopyNewsNetwork/0.1 (+https://github.com/snoopynewsnetwork/snn)",
    },
    signal: AbortSignal.timeout(8000),
  });
  if (!response.ok)
    throw new Error(`${new URL(url).host} returned ${response.status}`);
  return response.json() as Promise<T>;
}

function price(value: unknown) {
  const number = Number(value);
  return value !== null && value !== "" && number >= 0 && number <= 1
    ? Math.round(number * 1000) / 1000
    : null;
}

// Eastern wall-clock time, expressed as if it were UTC.
function easternWallClock(time: number) {
  const parts = Object.fromEntries(
    easternClock
      .formatToParts(time)
      .map((part) => [part.type, Number(part.value)]),
  );
  return Date.UTC(
    parts.year,
    parts.month - 1,
    parts.day,
    parts.hour,
    parts.minute,
    parts.second,
  );
}

// Midnight at the start of the Eastern day containing `time`. Eastern time is
// four or five hours behind UTC, and its clocks never change at midnight.
export function easternMidnight(time: number) {
  const wall = easternWallClock(time);
  const date = wall - (wall % DAY);
  return [4, 5]
    .map((hours) => date + hours * HOUR)
    .find((candidate) => easternWallClock(candidate) === date)!;
}

// Hourly samples for the last week and end-of-day (midnight ET) samples for
// the last 30 days. Both end with the fetch time, which carries live prices.
export function sampleTimes(now: number): Record<Range, number[]> {
  const lastHour = now - (now % HOUR);
  const hourly = Array.from(
    { length: 168 },
    (_, i) => lastHour - (167 - i) * HOUR,
  );
  const today = easternMidnight(now);
  // Step from noon so daylight-saving changes cannot skip or repeat a day.
  const daily = Array.from({ length: 30 }, (_, i) =>
    easternMidnight(today - (29 - i) * DAY + 12 * HOUR),
  );
  return {
    "7d": [...hourly.filter((time) => time < now), now],
    "30d": [...daily.filter((time) => time < now), now],
  };
}

// The price at each time is the most recent observation at or before it.
export function sample(feed: Feed, times: number[]) {
  const values: (number | null)[] = [];
  let next = 0;
  let current: number | null = null;
  for (const time of times) {
    while (next < feed.history.length && feed.history[next][0] <= time)
      current = feed.history[next++][1];
    values.push(current);
  }
  if (values.length) values[values.length - 1] = feed.latest ?? current;
  return values;
}

async function loadPolymarket(race: RaceMarkets, start: number) {
  const query = race.candidates
    .map((candidate) => `slug=${encodeURIComponent(candidate.polymarket)}`)
    .join("&");
  const markets = await getJson<
    {
      slug: string;
      outcomes: string;
      outcomePrices: string;
      clobTokenIds: string;
    }[]
  >(`${GAMMA}/markets?${query}`);
  return Promise.all(
    race.candidates.map(async (candidate): Promise<Feed> => {
      const market = markets.find((item) => item.slug === candidate.polymarket);
      if (!market)
        throw new Error(`Polymarket market ${candidate.polymarket} not found`);
      const outcomes: string[] = JSON.parse(market.outcomes);
      const prices: string[] = JSON.parse(market.outcomePrices);
      const tokens: string[] = JSON.parse(market.clobTokenIds);
      if (outcomes[0] !== "Yes")
        throw new Error(`Unexpected outcomes for ${candidate.polymarket}`);
      const { history } = await getJson<{ history: { t: number; p: number }[] }>(
        `${CLOB}/prices-history?market=${tokens[0]}&startTs=${Math.floor(start / 1000)}&fidelity=60`,
      );
      return {
        latest: price(prices[0]),
        history: history.flatMap(({ t, p }): Point[] => {
          const value = price(p);
          return value === null ? [] : [[t * 1000, value]];
        }),
      };
    }),
  );
}

async function loadKalshi(race: RaceMarkets, start: number, now: number) {
  const tickers = race.candidates.map((candidate) => candidate.kalshi).join(",");
  const [{ markets }, candles] = await Promise.all([
    getJson<{ markets: { ticker: string; last_price_dollars: string }[] }>(
      `${KALSHI}/markets?tickers=${tickers}`,
    ),
    getJson<{
      markets: {
        market_ticker: string;
        candlesticks: {
          end_period_ts: number;
          price: { close_dollars?: string; previous_dollars?: string };
        }[];
      }[];
    }>(
      `${KALSHI}/markets/candlesticks?market_tickers=${tickers}&start_ts=${Math.floor(start / 1000)}&end_ts=${Math.floor(now / 1000)}&period_interval=60`,
    ),
  ]);
  return race.candidates.map((candidate): Feed => {
    const market = markets.find((item) => item.ticker === candidate.kalshi);
    const history = candles.markets.find(
      (item) => item.market_ticker === candidate.kalshi,
    )?.candlesticks;
    if (!market || !history)
      throw new Error(`Kalshi market ${candidate.kalshi} not found`);
    return {
      latest: price(market.last_price_dollars),
      // Hours without trades carry the previous traded price.
      history: history.flatMap((candle): Point[] => {
        const value = price(
          candle.price.close_dollars ?? candle.price.previous_dollars,
        );
        return value === null ? [] : [[candle.end_period_ts * 1000, value]];
      }),
    };
  });
}

export async function loadMarketOdds(
  race: RaceMarkets,
  now: number,
): Promise<MarketOdds> {
  const start = now - 31 * DAY;
  const [polymarket, kalshi] = await Promise.allSettled([
    loadPolymarket(race, start),
    loadKalshi(race, start, now),
  ]);
  for (const result of [polymarket, kalshi])
    if (result.status === "rejected")
      console.error("Market feed failed", result.reason);
  if (polymarket.status === "rejected" && kalshi.status === "rejected")
    throw new Error("All market feeds failed");
  const feeds = {
    polymarket: polymarket.status === "fulfilled" ? polymarket.value : null,
    kalshi: kalshi.status === "fulfilled" ? kalshi.value : null,
  };
  const times = sampleTimes(now);
  const series = (feed: Feed | undefined, range: Range) =>
    feed ? sample(feed, times[range]) : times[range].map(() => null);
  return {
    updatedAt: new Date(now).toISOString(),
    settlement: race.settlement ?? defaultSettlement,
    sources: [
      {
        id: "polymarket",
        name: "Polymarket",
        url: `https://polymarket.com/event/${race.polymarketEvent}`,
        available: !!feeds.polymarket,
      },
      {
        id: "kalshi",
        name: "Kalshi",
        url: `https://kalshi.com/markets/${race.kalshiSeries.toLowerCase()}/senate-race/${race.kalshiEvent.toLowerCase()}`,
        available: !!feeds.kalshi,
      },
    ],
    times,
    candidates: race.candidates.map((candidate, i) => {
      const pm = feeds.polymarket?.[i];
      const kalshi = feeds.kalshi?.[i];
      return {
        name: candidate.name,
        party: candidate.party,
        latest: {
          polymarket: pm?.latest ?? null,
          kalshi: kalshi?.latest ?? null,
        },
        history: {
          "7d": { polymarket: series(pm, "7d"), kalshi: series(kalshi, "7d") },
          "30d": {
            polymarket: series(pm, "30d"),
            kalshi: series(kalshi, "30d"),
          },
        },
      };
    }),
  };
}

export function hasMarkets(slug: string) {
  return Object.hasOwn(raceMarkets, slug);
}

// Prices are cached per isolate. If a refresh fails, the last good copy is
// served instead.
export async function getMarketOdds(slug: string, now = Date.now()) {
  if (!hasMarkets(slug)) return null;
  const cached = cache.get(slug);
  if (cached && now < cached.expires) return cached.value;
  try {
    const value = await loadMarketOdds(raceMarkets[slug], now);
    const complete = value.sources.every((source) => source.available);
    cache.set(slug, {
      expires: now + (complete ? CACHE_TTL : PARTIAL_TTL),
      value,
    });
    return value;
  } catch (error) {
    if (cached) return cached.value;
    throw error;
  }
}
