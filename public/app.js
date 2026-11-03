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

let monitoring;
function monitorTime(value) {
  return value ? new Date(value).toLocaleString() : "Not checked yet";
}
function renderMonitoring() {
  const labels = { pending: "Awaiting first check", waiting: "Watching for publication", setup: "Awaiting first votes", reporting: "Unofficial results", review: "Source review needed", error: "Source check failed" };
  for (const panel of document.querySelectorAll("[data-monitor-race]")) {
    const slug = panel.dataset.monitorRace;
    const race = monitoring?.races.find(item => item.race === slug);
    if (!race) continue;
    const sources = monitoring.sources.filter(source => source.race === slug);
    const stale = !race.lastSuccessAt || Date.now() - Date.parse(race.lastSuccessAt) > 15 * 60_000;
    panel.innerHTML = `<div class="monitor-heading"><h3><a href="#race/${escape(slug)}">${slug === "kansas" ? "Kansas" : "North Carolina"}</a></h3><span class="tag">${escape(labels[race.status] || race.status)}${stale ? " · stale" : ""}</span></div>
      <p>${escape(race.message || "Waiting for the first source check.")}</p>
      ${race.candidates ? `<p><strong>${Number(race.totalVotes).toLocaleString()}</strong> Senate votes published${race.status === "error" ? " · last verified snapshot" : ""}</p><table class="monitor-results"><thead><tr><th>Candidate</th><th>Party</th><th>Votes</th></tr></thead><tbody>${race.candidates.map(candidate => `<tr><td>${escape(candidate.name)}</td><td>${escape(candidate.party)}</td><td>${Number(candidate.votes).toLocaleString()}</td></tr>`).join("")}</tbody></table><p class="muted">${Number(race.reportedPrecincts).toLocaleString()} / ${Number(race.totalPrecincts).toLocaleString()} precincts reported. Precinct reporting is not the share of votes counted.</p>` : ""}
      <dl class="monitor-times"><div><dt>Last check</dt><dd>${escape(monitorTime(race.checkedAt))}</dd></div><div><dt>Last verified</dt><dd>${escape(monitorTime(race.lastSuccessAt))}</dd></div><div><dt>Last result/link change</dt><dd>${escape(monitorTime(race.lastResultChangedAt))}</dd></div></dl>
      ${race.sourceUpdated ? `<p class="muted">Source upload: ${escape(race.sourceUpdated)}. Source submit: ${escape(race.sourceSubmitted)}. Timezone not specified by source.</p>` : ""}
      <details><summary>Official sources and saved evidence</summary><ul class="sources">${sources.map(source => `<li><a href="${escape(source.url)}" target="_blank" rel="noopener noreferrer">${escape(source.name)} ↗</a><p>${source.status === "error" ? escape(source.error) : source.status === "ok" ? "Reachable" : "Pending"} · checked ${escape(monitorTime(source.checkedAt))}${source.nextAttemptAt ? ` · retry ${escape(monitorTime(source.nextAttemptAt))}` : ""}${source.snapshotId ? ` · <a href="/api/monitor/snapshots/${Number(source.snapshotId)}" target="_blank" rel="noopener noreferrer">Saved response</a>` : ""}</p></li>`).join("")}</ul>${race.publications?.length ? `<p>Result links found; November Senate identity requires verification:</p><ul>${race.publications.map(item => `<li><a href="${escape(item.url)}" target="_blank" rel="noopener noreferrer">${escape(item.title)}</a></li>`).join("")}</ul>` : ""}</details>`;
  }
}
async function loadMonitoring() {
  try { monitoring = await api("/api/monitor"); renderMonitoring(); }
  catch { for (const panel of document.querySelectorAll("[data-monitor-race]")) panel.textContent = "Monitoring status is unavailable. Retrying in one minute."; }
}

function renderRace() {
  const race = currentRace;
  document.title = `${race.state} · Senate 2026 · SNN`;
  $("#race-view").innerHTML = `<a href="#" class="back">← All Senate races</a>
    <div class="race-hero"><div><p class="eyebrow">${escape(race.code)} / U.S. SENATE / 2026</p><h1>${escape(race.state)}</h1><p class="muted">General election ${escape(race.electionDate)} · Class ${escape(race.seatClass)}</p></div><span class="tag ${race.election === "Special" ? "special" : ""}">${escape(race.election)} election</span></div>
    <div class="race-layout"><div><section class="panel"><h2>The seat at a glance</h2><dl class="facts">
      <div><dt>Current seat holder</dt><dd>${escape(race.holder)}</dd></div><div><dt>Seat holder’s party</dt><dd>${escape(race.party)}</dd></div>
      <div><dt>Term to be filled</dt><dd>${escape(race.term)}</dd></div><div><dt>Seat details verified</dt><dd>${escape(race.verified)}</dd></div>
    </dl><p class="coverage-note">${escape(race.coverage)}. The seat holder is background information; confirm candidates with the state election office.</p></section>
    ${["kansas", "north-carolina"].includes(race.slug) ? `<section class="panel" data-monitor-race="${escape(race.slug)}"><h2>Official election monitoring</h2><p>Loading source status…</p></section>` : ""}
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
  renderMonitoring();
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
  void loadMonitoring();
  setInterval(() => { if (!document.hidden) void loadMonitoring(); }, 60_000);
  await loadIndex();
  await navigate();
} catch (error) {
  $("#races").innerHTML =
    '<tr><td colspan="5">The race index could not be loaded. Refresh to try again.</td></tr>';
  notify(error.message, true);
}
