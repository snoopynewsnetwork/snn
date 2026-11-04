import { alaskaAdapter } from "./adapters/alaska.ts";
import { adapters as southeast } from "./adapters/southeast.ts";
import { adapters as northeast } from "./adapters/northeast.ts";
import { adapters as west } from "./adapters/west.ts";
import type { ElectionAdapter } from "./adapters/types";
import { completionAdapter } from './completion.ts';
import { ky06CountyAdapter } from "./adapters/ky06-counties.ts";
import { miCountyAdapter } from './adapters/mi-counties.ts';

export const electionAdapters: ElectionAdapter[] = [...southeast, ...northeast, ...west, alaskaAdapter, ky06CountyAdapter, miCountyAdapter];
export const monitorAdapters: ElectionAdapter[] = [...electionAdapters, completionAdapter];

export function electionAdapter(id: string): ElectionAdapter {
  const adapter = monitorAdapters.find(adapter => adapter.id === id);
  if (!adapter) throw new Error(`Unknown election adapter: ${id}`);
  return adapter;
}
