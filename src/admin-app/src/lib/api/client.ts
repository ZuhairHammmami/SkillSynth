/** Thin fetch client for the SkillSynth API. Replaces axios.
 *  Injects the authToken cookie as a Bearer header and normalizes
 *  FastAPI error `detail` payloads into a thrown ApiError. */

const BASE = (import.meta.env.PUBLIC_API_BASE_URL as string) || 'http://127.0.0.1:8000/api';

const DEFAULT_TIMEOUT_MS = 30_000;

export class ApiError extends Error {
  status: number;
  detail: any;
  rawDetail: any;
  dependents?: Record<string, number> | null;
  constructor(status: number, detail: any, dependents?: Record<string, number> | null, rawDetail: any = null) {
    super(typeof detail === 'string' ? detail : 'Request failed');
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
    this.rawDetail = rawDetail;
    this.dependents = dependents;
  }
}

function readCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]+)'));
  return m ? decodeURIComponent(m[1]) : undefined;
}

export function getToken(): string | undefined {
  return readCookie('adminToken');
}

export interface RequestOpts {
  method?: string;
  body?: any;
  token?: string | null;
  query?: Record<string, string | number | undefined>;
  headers?: Record<string, string>;
}

function normalizeDetail(data: any): string {
  const d = data?.detail;
  if (!d) return 'Request failed';
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) return d.map((x: any) => x?.msg ?? JSON.stringify(x)).join('; ');
  if (typeof d === 'object') return d.message ?? JSON.stringify(d);
  return String(d);
}

/** Map a backend validation `detail` payload to a per-field error map for
 *  inline form display. Handles FastAPI 422 arrays (loc = [..., field]) and
 *  flat {field: message} objects. Returns {} when there is nothing to map. */
export function fieldErrorsFrom(detail: any): Record<string, string> {
  const out: Record<string, string> = {};
  if (!detail) return out;
  if (Array.isArray(detail)) {
    for (const item of detail) {
      const loc = (item as any)?.loc;
      const field = Array.isArray(loc) ? String(loc[loc.length - 1]) : undefined;
      const msg = (item as any)?.msg;
      if (field && msg) out[field] = msg;
    }
    return out;
  }
  if (typeof detail === 'object') {
    for (const [k, v] of Object.entries(detail)) {
      if (k === 'message' || k === 'dependents') continue;
      out[k] = typeof v === 'string' ? v : JSON.stringify(v);
    }
  }
  return out;
}

/** Thin fetch wrapper that calls the API with auth and normalized errors.
 *  Applies a DEFAULT_TIMEOUT_MS AbortController so a hung response (e.g. a
 *  streaming endpoint hit via GET) aborts and throws ApiError instead of
 *  freezing the UI; aborts map to a timeout message, other failures to a
 *  network message. Callers: every $lib/api/* module and Svelte page fetch. */
export async function apiFetch(path: string, opts: RequestOpts = {}): Promise<any> {
  const clean = path.startsWith('/') ? path.slice(1) : path;
  const base = BASE.endsWith('/') ? BASE : BASE + '/';
  const url = new URL(clean, base);
  if (opts.query) {
    for (const [k, v] of Object.entries(opts.query)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }
  const headers: Record<string, string> = { ...(opts.headers || {}) };
  const token = opts.token === undefined ? getToken() : opts.token || undefined;
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const isForm = opts.body instanceof URLSearchParams || opts.body instanceof FormData;
  if (opts.body !== undefined && !isForm && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  let res: Response;
  try {
    res = await fetch(url.toString(), {
      method: opts.method ?? 'GET',
      headers,
      signal: controller.signal,
      body: opts.body instanceof FormData ? opts.body : isForm ? opts.body.toString() : opts.body !== undefined ? JSON.stringify(opts.body) : undefined
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === 'AbortError') throw new ApiError(0, 'Request timed out — the server took too long to respond.');
    throw new ApiError(0, 'Network error — is the backend running?');
  } finally {
    clearTimeout(timer);
  }
  if (res.status === 204) return null;
  const text = await res.text();
  let data: any = null;
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }
  if (!res.ok) {
    const dependents = data?.detail?.dependents ?? data?.dependents ?? null;
    throw new ApiError(res.status, normalizeDetail(data), dependents, data?.detail ?? null);
  }
  return data;
}
