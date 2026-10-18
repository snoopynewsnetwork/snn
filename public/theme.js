// Run before the stylesheet so the saved theme is present on the first paint.
(() => {
  const storageKey = "snn-theme";
  const choices = ["light", "dark", "spooky"];
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  const root = document.documentElement;
  const colors = { light: "#f6f4ed", dark: "#151a17", spooky: "#160e20" };
  let midnight;

  function readPreference() {
    try {
      const saved = window.localStorage.getItem(storageKey);
      return choices.includes(saved) ? saved : "system";
    } catch {
      return "system";
    }
  }

  let preference = readPreference();

  function applyTheme() {
    const now = new Date();
    const halloween = now.getMonth() === 9 && now.getDate() === 31;
    const theme = choices.includes(preference)
      ? preference
      : halloween
        ? "spooky"
        : system.matches ? "dark" : "light";
    const changed = root.dataset.theme !== theme;
    root.dataset.theme = theme;
    root.dataset.themePreference = preference;
    document.querySelector('meta[name="theme-color"]').content = colors[theme];
    document.title = document.title.replace(
      /(?:Snoopy|Spoopy) News Network/,
      theme === "spooky" ? "Spoopy News Network" : "Snoopy News Network",
    );

    for (const button of document.querySelectorAll("[data-theme-choice]")) {
      button.setAttribute("aria-pressed", String(button.dataset.themeChoice === theme));
    }
    const automatic = document.querySelector("#theme-system");
    if (automatic) automatic.checked = preference === "system";
    const announcement = document.querySelector("#theme-announcement");
    if (announcement && changed) {
      announcement.textContent = `${theme[0].toUpperCase() + theme.slice(1)} theme enabled${preference === "system" ? halloween ? " automatically for Halloween" : ", following your system" : ""}.`;
    }

    // Use the visitor's local calendar, including DST, and update an open tab at midnight.
    window.clearTimeout(midnight);
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    midnight = window.setTimeout(applyTheme, tomorrow.getTime() - now.getTime() + 100);
  }

  function chooseTheme(value) {
    preference = value;
    try {
      if (value === "system") window.localStorage.removeItem(storageKey);
      else window.localStorage.setItem(storageKey, value);
    } catch {
      // The controls still work for this page when browser storage is unavailable.
    }
    applyTheme();
  }

  applyTheme();
  document.addEventListener("DOMContentLoaded", () => {
    for (const button of document.querySelectorAll("[data-theme-choice]")) {
      button.addEventListener("click", () => chooseTheme(button.dataset.themeChoice));
    }
    document.querySelector("#theme-system").addEventListener("change", (event) => {
      chooseTheme(event.target.checked ? "system" : root.dataset.theme);
    });
    applyTheme();
  }, { once: true });
  system.addEventListener("change", applyTheme);
  window.addEventListener("storage", (event) => {
    if (event.key === storageKey || event.key === null) {
      preference = readPreference();
      applyTheme();
    }
  });
  window.addEventListener("pageshow", applyTheme);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) applyTheme();
  });
})();
