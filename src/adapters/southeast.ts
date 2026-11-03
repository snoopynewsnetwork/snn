import type { ElectionAdapter } from "./types";
import { florida } from "./southeast-fl.ts";
import { georgia, virginia } from "./southeast-ga-va.ts";
import { indiana } from "./southeast-in.ts";
import { kentucky } from "./southeast-ky.ts";
import { northCarolina } from "./southeast-nc.ts";
import { southCarolina } from "./southeast-sc.ts";

// Southeast region: FL GA SC NC VA KY IN. One adapter per state publisher so a
// blocked or changed feed in one state cannot affect another state's targets.
export const adapters: ElectionAdapter[] = [florida, georgia, southCarolina, northCarolina, virginia, kentucky, indiana];
