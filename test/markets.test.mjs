import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import {
  loadMarketOdds,
  raceMarkets,
  sample,
  sampleTimes,
} from "../src/markets.ts";

const HOUR = 3_600_000;
const easternHour = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  hourCycle: "h23",
  hour: "2-digit",
  minute: "2-digit",
});
const easternDate = new Intl.DateTimeFormat("en-CA", {
  timeZone: "America/New_York",
});
const realFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = realFetch;
});

test("samples the latest observation at or before each time", () => {
  const feed = {
    latest: 0.7,
    history: [
      [20, 0.5],
      [30, 0.55],
      [31, 0.6],
    ],
  };
  assert.deepEqual(sample(feed, [10, 20, 30, 40, 50]), [
    null,
    0.5,
    0.55,
    0.6,
    0.7,
  ]);
  assert.deepEqual(sample({ ...feed, latest: null }, [30, 50]), [0.55, 0.6]);
});

test("daily samples fall on midnight ET across the end of daylight time", () => {
  const now = Date.parse("2026-11-10T17:30:00Z");
  const { "7d": hourly, "30d": daily } = sampleTimes(now);
  assert.equal(hourly.length, 169);
  assert.equal(hourly.at(-1), now);
  assert.equal(hourly[1] - hourly[0], HOUR);
  assert.equal(daily.length, 31);
  assert.equal(daily.at(-1), now);
  const days = daily.slice(0, -1);
  for (const time of days) assert.equal(easternHour.format(time), "00:00");
  const dates = days.map((time) => easternDate.format(time));
  assert.equal(new Set(dates).size, 30);
  assert.equal(dates.at(-1), "2026-11-10");
  assert.ok(dates.includes("2026-11-01") && dates.includes("2026-11-02"));
});

// Fake exchange APIs for Michigan. Polymarket's history is one point 40 hours
// old. Kalshi has two hourly candles ending 2 and 1 hours before the current
// hour; the second had no trades.
function exchanges(now, { kalshiDown = false } = {}) {
  const calls = [];
  const fetch = async (input) => {
    const url = new URL(input);
    calls.push(url);
    if (url.host === "api.elections.kalshi.com") {
      if (kalshiDown) return new Response("busy", { status: 503 });
      const tickers = url.searchParams.get(
        url.pathname.endsWith("/candlesticks") ? "market_tickers" : "tickers",
      );
      if (url.pathname.endsWith("/candlesticks"))
        return Response.json({
          markets: tickers.split(",").map((ticker, i) => ({
            market_ticker: ticker,
            candlesticks: [
              {
                end_period_ts: (now - (now % HOUR) - 2 * HOUR) / 1000,
                price: { close_dollars: i ? "0.3300" : "0.6700" },
              },
              {
                end_period_ts: (now - (now % HOUR) - HOUR) / 1000,
                price: { previous_dollars: i ? "0.3300" : "0.6700" },
              },
            ],
          })),
        });
      return Response.json({
        markets: tickers.split(",").map((ticker, i) => ({
          ticker,
          last_price_dollars: i ? "0.3200" : "0.6800",
        })),
      });
    }
    if (url.pathname === "/markets")
      return Response.json(
        url.searchParams.getAll("slug").map((slug, i) => ({
          slug,
          outcomes: '["Yes", "No"]',
          outcomePrices: i ? '["0.31", "0.69"]' : '["0.69", "0.31"]',
          clobTokenIds: `["token-${i}", "other-${i}"]`,
        })),
      );
    const yes = url.searchParams.get("market") === "token-0" ? 0.66 : 0.34;
    return Response.json({
      history: [{ t: (now - 40 * HOUR) / 1000, p: yes }],
    });
  };
  return { fetch, calls };
}

test("aligns both exchanges on the same sample times", async () => {
  const now = Date.parse("2026-10-18T16:30:00Z");
  const { fetch, calls } = exchanges(now);
  globalThis.fetch = fetch;
  const odds = await loadMarketOdds(raceMarkets.michigan, now);
  assert.equal(
    calls.filter((url) => url.host === "api.elections.kalshi.com").length,
    2,
  );
  assert.equal(
    odds.sources.find((source) => source.id === "kalshi").url,
    "https://kalshi.com/markets/senatemi/senate-race/senatemi-26",
  );
  const [democrat, republican] = odds.candidates;
  assert.deepEqual(democrat.latest, { polymarket: 0.69, kalshi: 0.68 });
  assert.deepEqual(republican.latest, { polymarket: 0.31, kalshi: 0.32 });
  const week = democrat.history["7d"];
  assert.deepEqual(week.kalshi.slice(-5), [null, 0.67, 0.67, 0.67, 0.68]);
  assert.deepEqual(week.polymarket.slice(-3), [0.66, 0.66, 0.69]);
});

test("serves one market when the other fails", async () => {
  const now = Date.parse("2026-10-18T16:30:00Z");
  globalThis.fetch = exchanges(now, { kalshiDown: true }).fetch;
  const errors = [];
  const consoleError = console.error;
  console.error = (...args) => errors.push(args);
  let odds;
  try {
    odds = await loadMarketOdds(raceMarkets.michigan, now);
  } finally {
    console.error = consoleError;
  }
  assert.equal(errors.length, 1);
  assert.deepEqual(
    odds.sources.map((source) => [source.id, source.available]),
    [
      ["polymarket", true],
      ["kalshi", false],
    ],
  );
  const [democrat, republican] = odds.candidates;
  assert.deepEqual(democrat.latest, { polymarket: 0.69, kalshi: null });
  assert.deepEqual(republican.latest, { polymarket: 0.31, kalshi: null });
  const week = democrat.history["7d"];
  assert.equal(week.polymarket.length, odds.times["7d"].length);
  assert.equal(week.polymarket.at(-1), 0.69);
  assert.equal(week.polymarket.at(-2), 0.66);
  assert.equal(week.polymarket[0], null);
  assert.ok(week.kalshi.every((value) => value === null));
});

test("fails when every market is unavailable", async () => {
  globalThis.fetch = async () => new Response("down", { status: 500 });
  const consoleError = console.error;
  console.error = () => {};
  try {
    await assert.rejects(
      loadMarketOdds(raceMarkets.michigan, Date.now()),
      /All market feeds failed/,
    );
  } finally {
    console.error = consoleError;
  }
});
