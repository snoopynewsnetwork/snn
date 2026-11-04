import { cnnAdapter } from "./northeast-cnn.ts";

// Pinned from CNN's November 4, 2026 production Senate response. These are
// supplier first-choice returns; ranked-choice tabulation can change the outcome.
export const alaskaAdapter = cnnAdapter("west-ak-cnn", [{
  target: { id: "senate-ak", state: "AK", name: "Alaska U.S. Senate", chamber: "senate" },
  key: "2026-SG-AK",
  candidates: ["Mary Peltola", "Dan S. Sullivan", "Gerald Heikes", "Daniel J. Sullivan"],
  why: "Alaska tracking uses CNN's attributed public results feed",
  note: "First-choice returns only. Alaska's ranked-choice tabulation may change the outcome; these totals are not a race call.",
}]);
