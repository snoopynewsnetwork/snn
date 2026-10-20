const $ = (selector) => document.querySelector(selector);
const escape = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
const categoryNames = {
  news: "News",
  candidates: "Candidates",
  polling: "Polling",
  finance: "Finance",
  results: "Results",
};
let races = [];
let editorKey = "";
let currentRace = null;
let navigation = 0;

function notify(message, error = false) {
  $("#status").textContent = message;
  $("#status").classList.toggle("error", error);
  $("#status").hidden = !message;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(editorKey ? { Authorization: `Bearer ${editorKey}` } : {}),
      ...options.headers,
    },
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The request failed.");
  return data;
}

function renderIndex() {
  const query = $("#search").value.trim().toLowerCase();
  const shown = races.filter(
    (race) =>
      `${race.state} ${race.code} ${race.holder}`
        .toLowerCase()
        .includes(query) &&
      (!$("#party").value || race.party === $("#party").value) &&
      (!$("#election").value || race.election === $("#election").value),
  );
  $("#races").innerHTML = shown.length
    ? shown
        .map(
          (race) => `<tr>
    <td><a class="state-link" href="#race/${escape(race.slug)}"><span class="state-code">${escape(race.code)}</span>${escape(race.state)}</a></td>
    <td><span class="holder">${escape(race.holder)}<span class="party ${escape(race.party.toLowerCase())}">${escape(race.party)}</span></span></td>
    <td><span class="tag ${race.election === "Special" ? "special" : ""}">${escape(race.election)}</span></td>
    <td>${race.noteCount}</td><td><a class="open-link" href="#race/${escape(race.slug)}" aria-label="Open ${escape(race.state)} race">↗</a></td>
  </tr>`,
        )
        .join("")
    : '<tr><td colspan="5">No races match these filters.</td></tr>';
  $("#showing").textContent = `${shown.length} of ${races.length} races`;
  $("#race-count").textContent = races.length;
  $("#note-count").textContent = races.reduce(
    (sum, race) => sum + race.noteCount,
    0,
  );
}

async function loadIndex() {
  ({ races } = await api("/api/races"));
  renderIndex();
}

function renderNotes(category = "") {
  const race = currentRace;
  const notes = race.notes.filter(
    (note) => !category || note.category === category,
  );
  $("#report-notes").innerHTML = notes.length
    ? notes
        .map(
          (note) => `<article class="report-note">
    <div class="note-meta"><span class="tag">${escape(categoryNames[note.category])}</span><time datetime="${escape(note.date)}">${escape(note.date)}</time></div>
    <h3>${escape(note.title)}</h3><p class="note-body">${escape(note.body)}</p>
    <div class="note-footer"><a href="${escape(note.sourceUrl)}" target="_blank" rel="noopener noreferrer">View source ↗</a><span class="muted">Added ${escape(note.createdAt.slice(0, 10))}</span>${editorKey ? `<button class="remove-note" data-id="${escape(note.id)}">Remove note</button>` : ""}</div>
  </article>`,
        )
        .join("")
    : `<div class="empty-state"><strong>No ${category ? escape(categoryNames[category].toLowerCase()) + " " : ""}notes on file yet.</strong>Add dated research with a source to start this race’s reporting log.</div>`;
  for (const button of document.querySelectorAll(".remove-note"))
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await api(`/api/races/${race.slug}/notes/${button.dataset.id}`, {
          method: "DELETE",
        });
        if (currentRace?.slug === race.slug) {
          currentRace.notes = currentRace.notes.filter(
            (note) => note.id !== button.dataset.id,
          );
          renderNotes($("#note-category-filter").value);
        }
        await loadIndex();
        notify(`Note removed from the ${race.state} reporting log.`);
      } catch (error) {
        notify(error.message, true);
        button.disabled = false;
      }
    });
}

const marketNames = { polymarket: "Polymarket", kalshi: "Kalshi" };
const easternDay = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  month: "short",
  day: "numeric",
});
const easternHour = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  month: "short",
  day: "numeric",
  hour: "numeric",
});
const easternTime = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  hour: "numeric",
  minute: "2-digit",
  timeZoneName: "short",
});
// Market prices for the open race: { slug, requestedAt, odds, range, index }.
// index is the inspected sample, or null to show the latest prices.
let market = null;

function percent(value) {
  if (value == null) return "—";
  if (value < 0.005) return "<1%";
  if (value > 0.995) return ">99%";
  return `${Math.round(value * 100)}%`;
}

function marketX(times, index) {
  const span = times.at(-1) - times[0] || 1;
  return (((times[index] - times[0]) / span) * 1000).toFixed(1);
}

function marketY(value) {
  return (100 - value * 100).toFixed(2);
}

function linePath(values, times) {
  let path = "";
  let drawing = false;
  values.forEach((value, index) => {
    if (value == null) {
      drawing = false;
      return;
    }
    path += `${drawing ? "L" : "M"}${marketX(times, index)} ${marketY(value)}`;
    drawing = true;
  });
  return path;
}

// A zero-length segment with round caps draws a dot that stays circular
// while the SVG stretches to fit its box.
function dotPath(x, value) {
  return `M${x} ${marketY(value)}h0.001`;
}

function sampleLabel(times, index) {
  if (index === times.length - 1)
    return `Latest · ${easternTime.format(times[index])}`;
  // Daily samples fall at midnight ET, so each one closes the previous day.
  return market.range === "30d"
    ? `${easternDay.format(times[index] - 1)} close`
    : easternHour.format(times[index]);
}

function marketShell() {
  return `<section class="market-card" aria-labelledby="market-title">
    <div class="market-head"><div><h2 id="market-title">Market odds over time</h2><p>Each candidate’s chance of winning, as priced by prediction markets</p></div>
    <div class="range-toggle" role="group" aria-label="Time range"><button type="button" data-range="7d">7D</button><button type="button" data-range="30d">30D</button></div></div>
    <div class="market-legend">${Object.entries(marketNames)
      .map(([id, name]) => `<span class="key ${id}">${name}</span>`)
      .join("")}</div>
    <div class="market-columns" aria-hidden="true"><span>Candidate</span><span>Win probability</span><span>Price</span></div>
    <div id="market-rows"><p class="market-message">Loading market prices…</p></div>
    <div class="market-foot"><span>Same 0–100% scale on every chart.</span><span>Hover, tap or use ← → to inspect dates.</span></div>
  </section><div id="market-note" class="market-note"></div>`;
}

function renderMarketCursor() {
  const { odds, range } = market;
  const times = odds.times[range];
  const index = market.index ?? times.length - 1;
  const x = marketX(times, index);
  const label = sampleLabel(times, index);
  for (const plot of document.querySelectorAll(".plot")) {
    const history = odds.candidates[plot.dataset.candidate].history[range];
    const values = Object.keys(marketNames).map((id) => [
      id,
      history[id][index],
    ]);
    plot.querySelector(".cursor").innerHTML =
      (market.index === null
        ? ""
        : `<line class="crosshair" x1="${x}" x2="${x}" y1="0" y2="100"/>`) +
      values
        .filter(([, value]) => value != null)
        .map(
          ([id, value]) =>
            `<path class="marker-halo" d="${dotPath(x, value)}"/><path class="marker ${id}" d="${dotPath(x, value)}"/>`,
        )
        .join("");
    const row = plot.closest(".market-row");
    for (const [id, value] of values)
      row.querySelector(`dd[data-source="${id}"]`).textContent = percent(value);
    row.querySelector(".price-caption").textContent = label;
    plot.setAttribute("aria-valuenow", index);
    plot.setAttribute(
      "aria-valuetext",
      `${label}: ${values.map(([id, value]) => `${marketNames[id]} ${value == null ? "no price" : percent(value)}`).join(", ")}`,
    );
  }
}

function renderMarkets() {
  for (const button of document.querySelectorAll(".range-toggle button"))
    button.setAttribute("aria-pressed", button.dataset.range === market.range);
  const { odds, range } = market;
  if (!odds) return;
  const times = odds.times[range];
  const last = times.length - 1;
  $("#market-rows").innerHTML = odds.candidates
    .map(
      (candidate, i) => `<div class="market-row">
    <div class="market-candidate"><h3>${escape(candidate.name)}</h3><span class="party ${escape(candidate.party.toLowerCase())}">${escape(candidate.party)}</span></div>
    <div class="market-chart">
      <div class="y-axis" aria-hidden="true"><span>100</span><span>50</span><span>0</span></div>
      <div class="plot" tabindex="0" role="slider" data-candidate="${i}" aria-label="${escape(candidate.name)} win probability" aria-valuemin="0" aria-valuemax="${last}">
        <svg viewBox="0 0 1000 100" preserveAspectRatio="none" aria-hidden="true" focusable="false">
          <line class="gridline" x1="0" x2="1000" y1="0" y2="0"/><line class="gridline middle" x1="0" x2="1000" y1="50" y2="50"/><line class="gridline" x1="0" x2="1000" y1="100" y2="100"/>
          ${Object.keys(marketNames)
            .map(
              (id) =>
                `<path class="line ${id}" d="${linePath(candidate.history[range][id], times)}"/>`,
            )
            .join("")}
          <g class="cursor"></g>
        </svg>
      </div>
      <div class="x-axis" aria-hidden="true"><span>${escape(easternDay.format(range === "30d" ? times[0] - 1 : times[0]))}</span><span>${escape(easternDay.format(times[last]))}</span></div>
      <p class="chart-caption">${range === "30d" ? "Prices at midnight ET each day" : "Hourly prices"}</p>
    </div>
    <div class="market-price"><dl>${Object.entries(marketNames)
      .map(
        ([id, name]) =>
          `<div class="${id}"><dt>${name}</dt><dd data-source="${id}"></dd></div>`,
      )
      .join("")}</dl><p class="price-caption"></p></div>
  </div>`,
    )
    .join("");
  const missing = odds.sources.filter((source) => !source.available);
  $("#market-note").innerHTML = `<p><strong>About these prices.</strong> Each contract pays $1 if its outcome happens, so a price of 69¢ is read as a 69% chance. ${escape(odds.settlement)} Prices come from the Polymarket and Kalshi public APIs. They are not SNN forecasts.${missing.length ? ` ${missing.map((source) => escape(source.name)).join(" and ")} prices could not be loaded just now.` : ""}</p>
    <p>Market pages: ${odds.sources.map((source) => `<a href="${escape(source.url)}" target="_blank" rel="noopener noreferrer">${escape(source.name)} ↗</a>`).join(" · ")}</p>`;
  for (const plot of document.querySelectorAll(".plot")) {
    const inspect = (event) => {
      const box = plot.getBoundingClientRect();
      const share = Math.min(
        1,
        Math.max(0, (event.clientX - box.left) / box.width),
      );
      const target = times[0] + share * (times[last] - times[0]);
      let nearest = 0;
      times.forEach((time, index) => {
        if (Math.abs(time - target) < Math.abs(times[nearest] - target))
          nearest = index;
      });
      market.index = nearest;
      renderMarketCursor();
    };
    const reset = () => {
      market.index = null;
      renderMarketCursor();
    };
    plot.addEventListener("pointerdown", inspect);
    plot.addEventListener("pointermove", inspect);
    // A tap leaves its date in view until focus moves elsewhere.
    plot.addEventListener("pointerleave", (event) => {
      if (event.pointerType === "mouse" && document.activeElement !== plot)
        reset();
    });
    plot.addEventListener("blur", reset);
    plot.addEventListener("keydown", (event) => {
      const current = market.index ?? last;
      const next = {
        ArrowLeft: current - 1,
        ArrowDown: current - 1,
        ArrowRight: current + 1,
        ArrowUp: current + 1,
        Home: 0,
        End: last,
      }[event.key];
      if (event.key === "Escape") reset();
      if (next === undefined) return;
      event.preventDefault();
      market.index = Math.min(last, Math.max(0, next));
      renderMarketCursor();
    });
  }
  renderMarketCursor();
}

async function showMarkets(race) {
  for (const button of document.querySelectorAll(".range-toggle button"))
    button.addEventListener("click", () => {
      if (!market) return;
      market.range = button.dataset.range;
      market.index = null;
      renderMarkets();
    });
  // Reuse prices for five minutes, matching the Worker's cache.
  if (market?.slug === race.slug && Date.now() - market.requestedAt < 300000) {
    renderMarkets();
    return;
  }
  const request = {
    slug: race.slug,
    requestedAt: Date.now(),
    odds: null,
    range: market?.slug === race.slug ? market.range : "30d",
    index: null,
  };
  market = request;
  renderMarkets();
  try {
    request.odds = await api(`/api/races/${race.slug}/markets`);
    if (market === request) renderMarkets();
  } catch (error) {
    if (market !== request) return;
    market = null;
    $("#market-rows").innerHTML =
      `<p class="market-message">${escape(error.message)}</p>`;
  }
}

function renderRace() {
  const race = currentRace;
  document.title = `${race.state} · Senate 2026 · SNN`;
  $("#race-view").innerHTML = `<a href="#" class="back">← All Senate races</a>
    <div class="race-hero"><div><p class="eyebrow">${escape(race.code)} / U.S. SENATE / 2026</p><h1>${escape(race.state)}</h1><p class="muted">General election ${escape(race.electionDate)} · Class ${escape(race.seatClass)}</p></div><span class="tag ${race.election === "Special" ? "special" : ""}">${escape(race.election)} election</span></div>
    ${race.hasMarkets ? marketShell() : ""}
    <div class="race-layout"><div><section class="panel"><h2>The seat at a glance</h2><dl class="facts">
      <div><dt>Current seat holder</dt><dd>${escape(race.holder)}</dd></div><div><dt>Seat holder’s party</dt><dd>${escape(race.party)}</dd></div>
      <div><dt>Term to be filled</dt><dd>${escape(race.term)}</dd></div><div><dt>Seat details verified</dt><dd>${escape(race.verified)}</dd></div>
    </dl><p class="coverage-note">${escape(race.coverage)}. The seat holder is background information; confirm candidates with the state election office.</p></section>
    <section class="panel"><div class="note-toolbar"><h2>Reporting log</h2><label><span class="sr-only">Filter reporting notes</span><select id="note-category-filter"><option value="">All notes</option>${Object.entries(
      categoryNames,
    )
      .map(([value, name]) => `<option value="${value}">${name}</option>`)
      .join("")}</select></label></div>
    <button id="add-note-button" class="button">${editorKey ? "+ Add a sourced note" : "Editor access to add notes"}</button>
    <form id="note-form" class="note-form" hidden><h3>Add a reporting note</h3><div class="form-grid">
      <label>Category<select name="category">${Object.entries(categoryNames)
        .map(([value, name]) => `<option value="${value}">${name}</option>`)
        .join("")}</select></label>
      <label>Development date<input type="date" name="date" required value="${new Date().toISOString().slice(0, 10)}"></label>
      <label class="full-width">Headline<input name="title" required maxlength="160" placeholder="What changed?"></label>
      <label class="full-width">Reporting note<textarea name="body" required maxlength="6000" placeholder="Record the facts, context, and what still needs verification."></textarea></label>
      <label class="full-width">Source URL<input name="sourceUrl" type="url" required maxlength="2048" placeholder="https://…"></label>
    </div><p class="form-hint">Saved notes are public. For polls, include field dates, sponsor, sample, population, method, and margin of error. Label results as projected, unofficial, or certified.</p><p id="note-error" role="alert" class="error note-error"></p><div class="form-actions"><button type="button" id="cancel-note" class="button quiet">Cancel</button><button type="submit" class="button">Save note</button></div></form>
    <div id="report-notes"></div></section></div>
    <aside><section class="panel"><h2>Research sources</h2><ul class="sources">${race.sources.map((source) => `<li><a href="${escape(source.url)}" target="_blank" rel="noopener noreferrer">${escape(source.title)} ↗</a><p>${escape(source.description)}</p></li>`).join("")}</ul></section>
    <p class="aside-note">Baseline seat details and source links come from the project’s research files. The reporting log contains notes added through this app; it does not update automatically.</p><a class="aside-note" href="${escape(race.repositoryUrl)}" target="_blank" rel="noopener noreferrer">Read the original tracker ↗</a></aside></div>`;
  renderNotes();
  if (race.hasMarkets) showMarkets(race);
  $("#note-category-filter").addEventListener("change", (event) =>
    renderNotes(event.target.value),
  );
  $("#add-note-button").addEventListener("click", () => {
    if (!editorKey) {
      openEditor();
      return;
    }
    $("#note-form").hidden = false;
    $("#add-note-button").hidden = true;
    $('#note-form [name="title"]').focus();
  });
  $("#cancel-note").addEventListener("click", () => {
    $("#note-form").hidden = true;
    $("#add-note-button").hidden = false;
  });
  $("#note-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector('[type="submit"]');
    button.disabled = true;
    $("#note-error").textContent = "";
    try {
      const note = await api(`/api/races/${race.slug}/notes`, {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      // The user may have navigated to another race while the request was pending.
      if (currentRace?.slug === race.slug) {
        currentRace.notes.unshift(note);
        currentRace.notes.sort(
          (a, b) =>
            b.date.localeCompare(a.date) ||
            b.createdAt.localeCompare(a.createdAt),
        );
        renderRace();
      }
      await loadIndex();
      notify(`Note saved to the ${race.state} reporting log.`);
    } catch (error) {
      if (currentRace?.slug === race.slug)
        $("#note-error").textContent = error.message;
      else notify(error.message, true);
    } finally {
      button.disabled = false;
    }
  });
}

async function navigate() {
  const sequence = ++navigation;
  const match = location.hash.match(/^#race\/([a-z-]+)$/);
  notify("");
  $("#index-view").hidden = !!match;
  $("#race-view").hidden = !match;
  if (!match) {
    currentRace = null;
    document.title = "Snoopy News Network · Senate 2026";
    return;
  }
  $("#race-view").innerHTML =
    '<a href="#" class="back">← All Senate races</a><p>Loading race details…</p>';
  try {
    const race = await api(`/api/races/${match[1]}`);
    if (sequence !== navigation) return;
    currentRace = race;
    renderRace();
    window.scrollTo(0, 0);
  } catch (error) {
    if (sequence === navigation) notify(error.message, true);
  }
}

function openEditor() {
  $("#editor-error").textContent = "";
  $("#editor-dialog").showModal();
}

$("#editor-button").addEventListener("click", () => {
  if (!editorKey) {
    openEditor();
    return;
  }
  editorKey = "";
  $("#editor-button").textContent = "Editor access";
  if (currentRace) renderRace();
  notify("Editing locked.");
});
$("#cancel-editor").addEventListener("click", () =>
  $("#editor-dialog").close(),
);
$("#editor-dialog").addEventListener("close", () => {
  $("#editor-key").value = "";
});
$("#editor-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector('[type="submit"]');
  button.disabled = true;
  try {
    const key = $("#editor-key").value;
    await api("/api/editor", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}` },
    });
    editorKey = key;
    $("#editor-button").textContent = "Lock editing";
    $("#editor-dialog").close();
    if (currentRace) renderRace();
    notify("Editor access unlocked for this page session.");
  } catch (error) {
    $("#editor-error").textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
for (const selector of ["#search", "#party", "#election"])
  $(selector).addEventListener("input", renderIndex);
window.addEventListener("hashchange", navigate);
try {
  await loadIndex();
  await navigate();
} catch (error) {
  $("#races").innerHTML =
    '<tr><td colspan="5">The race index could not be loaded. Refresh to try again.</td></tr>';
  notify(error.message, true);
}
