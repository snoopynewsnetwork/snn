import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";
import { runInNewContext } from "node:vm";

const script = await readFile(new URL("../public/theme.js", import.meta.url), "utf8");
const localDate = (month, day, hour = 12) => new Date(2026, month - 1, day, hour).getTime();

function target(properties = {}) {
  const listeners = new Map();
  return {
    ...properties,
    addEventListener(type, callback) {
      const callbacks = listeners.get(type) ?? [];
      callbacks.push(callback);
      listeners.set(type, callbacks);
    },
    emit(type, event = {}) {
      for (const callback of listeners.get(type) ?? []) callback(event);
    },
  };
}

// Exercise the actual pre-paint script with a controllable local clock and browser events.
function browser({ date = localDate(10, 17), dark = false, saved, blocked = false } = {}) {
  let now = date;
  let ready = false;
  let timerId = 0;
  const timers = new Map();
  const storage = new Map(saved === undefined ? [] : [["snn-theme", saved]]);
  const root = { dataset: {} };
  const meta = {};
  const automatic = target({ checked: true });
  const announcement = {};
  const buttons = ["light", "dark", "spooky"].map(themeChoice => target({
    dataset: { themeChoice },
    attributes: {},
    setAttribute(key, value) { this.attributes[key] = value; },
  }));
  const system = target({ matches: dark });
  const document = target({
    documentElement: root,
    title: "Snoopy News Network · Senate 2026",
    hidden: false,
    querySelector(selector) {
      if (selector === 'meta[name="theme-color"]') return meta;
      if (!ready) return null;
      if (selector === "#theme-system") return automatic;
      if (selector === "#theme-announcement") return announcement;
    },
    querySelectorAll() { return ready ? buttons : []; },
  });
  const window = target({
    matchMedia: () => system,
    localStorage: {
      getItem(key) { if (blocked) throw new Error("Storage denied"); return storage.get(key) ?? null; },
      setItem(key, value) { if (blocked) throw new Error("Storage denied"); storage.set(key, value); },
      removeItem(key) { if (blocked) throw new Error("Storage denied"); storage.delete(key); },
    },
    setTimeout(callback, delay) { timers.set(++timerId, { callback, at: now + delay }); return timerId; },
    clearTimeout(id) { timers.delete(id); },
  });
  class Clock extends Date {
    constructor(...args) { super(...(args.length ? args : [now])); }
  }
  runInNewContext(script, { window, document, Date: Clock });
  const initialTheme = root.dataset.theme;
  ready = true;
  document.emit("DOMContentLoaded");
  return {
    root, automatic, buttons, meta, storage, initialTheme, announcement,
    choose(theme) { buttons.find(button => button.dataset.themeChoice === theme).emit("click"); },
    followSystem(checked = true) { automatic.checked = checked; automatic.emit("change", { target: automatic }); },
    setSystem(matches) { system.matches = matches; system.emit("change"); },
    nextMidnight() {
      assert.equal(timers.size, 1, "Only one midnight update is scheduled");
      const timer = [...timers.values()][0];
      now = timer.at;
      timer.callback();
    },
    otherTab(value) {
      if (value === null) storage.clear();
      else storage.set("snn-theme", value);
      window.emit("storage", { key: value === null ? null : "snn-theme" });
    },
    resume(date) { now = date; document.emit("visibilitychange"); },
  };
}

test("system defaults apply before first paint and track live device changes", () => {
  const page = browser({ dark: true });
  assert.equal(page.initialTheme, "dark");
  assert.equal(page.automatic.checked, true);
  page.setSystem(false);
  assert.equal(page.root.dataset.theme, "light");
  page.setSystem(true);
  assert.equal(page.root.dataset.theme, "dark");
  assert.equal(page.meta.content, "#151a17");
  assert.equal(page.buttons.find(button => button.dataset.themeChoice === "dark").attributes["aria-pressed"], "true");
});

test("Halloween runs for October 31 only, in the visitor's local calendar", () => {
  for (const dark of [true, false]) {
    const page = browser({ date: localDate(10, 30, 23), dark });
    assert.equal(page.root.dataset.theme, dark ? "dark" : "light");
    page.nextMidnight();
    assert.equal(page.root.dataset.theme, "spooky");
    assert.match(page.announcement.textContent, /automatically for Halloween/);
    page.setSystem(!dark);
    assert.equal(page.root.dataset.theme, "spooky");
    page.nextMidnight();
    assert.equal(page.root.dataset.theme, !dark ? "dark" : "light");
  }
  assert.equal(browser({ date: localDate(12, 31) }).initialTheme, "light");
  assert.equal(browser({ date: localDate(10, 31) }).initialTheme, "spooky");
  assert.equal(browser({ date: localDate(11, 1) }).initialTheme, "light");
});

test("each explicit theme persists and takes precedence over system and Halloween", () => {
  for (const theme of ["light", "dark", "spooky"]) {
    const page = browser({ date: localDate(10, 30) });
    page.choose(theme);
    assert.equal(page.storage.get("snn-theme"), theme);
    assert.equal(page.automatic.checked, false);
    page.nextMidnight();
    page.setSystem(true);
    assert.equal(page.root.dataset.theme, theme);
    assert.equal(browser({ date: localDate(10, 31), saved: theme }).initialTheme, theme);
    page.followSystem();
    assert.equal(page.storage.has("snn-theme"), false);
    assert.equal(page.root.dataset.theme, "spooky");
    page.nextMidnight();
    assert.equal(page.root.dataset.theme, "dark");
  }
});

test("turning off Follow system locks the current theme", () => {
  const page = browser({ dark: true });
  page.followSystem(false);
  page.setSystem(false);
  assert.equal(page.root.dataset.theme, "dark");
  assert.equal(page.storage.get("snn-theme"), "dark");
});

test("preferences synchronize across tabs, including a reset to automatic", () => {
  const page = browser({ dark: true });
  page.otherTab("spooky");
  assert.equal(page.root.dataset.theme, "spooky");
  assert.equal(page.automatic.checked, false);
  page.otherTab(null);
  assert.equal(page.root.dataset.theme, "dark");
  assert.equal(page.automatic.checked, true);
});

test("suspended tabs recalculate the local date on resume", () => {
  const page = browser({ dark: true });
  page.resume(localDate(10, 31));
  assert.equal(page.root.dataset.theme, "spooky");
  page.resume(localDate(11, 1));
  assert.equal(page.root.dataset.theme, "dark");
});

test("invalid or unavailable storage falls back to system without breaking controls", () => {
  assert.equal(browser({ saved: "invalid", dark: true }).initialTheme, "dark");
  const page = browser({ blocked: true });
  page.choose("spooky");
  assert.equal(page.root.dataset.theme, "spooky");
  page.followSystem();
  assert.equal(page.root.dataset.theme, "light");
});
