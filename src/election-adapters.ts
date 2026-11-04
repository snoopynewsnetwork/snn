import { adapters as southeast } from "./adapters/southeast.ts";
import { adapters as northeast } from "./adapters/northeast.ts";
import { adapters as west } from "./adapters/west.ts";
import type { ElectionAdapter } from "./adapters/types";
import { completionAdapter } from './completion.ts';

export const electionAdapters: ElectionAdapter[] = [...southeast, ...northeast, ...west];
export const monitorAdapters: ElectionAdapter[] = [...electionAdapters, completionAdapter];

export function electionAdapter(id: string): ElectionAdapter {
  const adapter = monitorAdapters.find(adapter => adapter.id === id);
  if (!adapter) throw new Error(`Unknown election adapter: ${id}`);
  return adapter;
}
