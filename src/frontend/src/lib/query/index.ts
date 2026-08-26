/** Minimal query cache replacing TanStack Query. Caches by key string with a
 *  staleTime, and supports prefix-based invalidation (used by the SSE bus to
 *  mirror the backend's invalidation signals). */

type Entry = { data: any; ts: number; promise?: Promise<any> };

const cache = new Map<string, Entry>();

export function keyStr(key: string[] | string): string {
  return Array.isArray(key) ? key.join('::') : key;
}

/** Fetch (and cache) a resource. Returns cached data while fresh. */
export async function query<T>(
  key: string[] | string,
  fetcher: () => Promise<T>,
  opts: { staleTime?: number } = {}
): Promise<T> {
  const k = keyStr(key);
  const stale = opts.staleTime ?? 30000;
  const ex = cache.get(k);
  if (ex?.promise) return ex.promise as Promise<T>;
  if (ex && Date.now() - ex.ts < stale) return ex.data as T;
  const p = fetcher()
    .then((d) => {
      cache.set(k, { data: d, ts: Date.now() });
      return d;
    })
    .catch((e) => {
      cache.delete(k);
      throw e;
    });
  cache.set(k, { data: ex?.data, ts: ex?.ts ?? 0, promise: p });
  return p;
}

/** Drop every cached entry whose key starts with the given prefix. */
export function invalidate(prefix: string[] | string): void {
  const p = keyStr(prefix);
  for (const k of [...cache.keys()]) {
    if (k === p || k.startsWith(p + '::')) cache.delete(k);
  }
}
