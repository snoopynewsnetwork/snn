"use strict";
function unitVisible(node, query, scope) {
  return (scope === "all" || node.dataset.scope === scope) &&
    node.dataset.search.toLocaleLowerCase().includes(query.toLocaleLowerCase());
}
function updateUnits() {
  const query = document.getElementById("filter").value;
  const scope = document.getElementById("scope").value;
  let count = 0;
  for (const node of document.querySelectorAll("details.source-unit")) {
    node.hidden = !unitVisible(node, query, scope);
    if (!node.hidden) count++;
  }
  document.getElementById("visible-count").textContent = `${count} source records shown`;
}
if (document.getElementById("filter")) {
  document.getElementById("filter").addEventListener("input", updateUnits);
  document.getElementById("scope").addEventListener("change", updateUnits);
  updateUnits();
}
if (document.getElementById("parent-filter")) {
  document.getElementById("parent-filter").addEventListener("input", event => {
    for (const row of document.querySelectorAll("tbody tr"))
      row.hidden = !row.dataset.search.toLocaleLowerCase().includes(event.target.value.toLocaleLowerCase());
  });
}
