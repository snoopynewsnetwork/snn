import { adapters as southeast } from "./adapters/southeast.ts";
import { adapters as northeast } from "./adapters/northeast.ts";
import { adapters as west } from "./adapters/west.ts";
import type { ElectionAdapter } from "./adapters/types";

export const electionAdapters: ElectionAdapter[] = [...southeast, ...northeast, ...west];

export function electionAdapter(id: string): ElectionAdapter {
  const adapter = electionAdapters.find(adapter => adapter.id === id);
  if (!adapter) throw new Error(`Unknown election adapter: ${id}`);
  return adapter;
}
