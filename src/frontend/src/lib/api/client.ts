/** Thin fetch client for the SkillSynth API. Replaces axios.
 *  Injects the authToken cookie as a Bearer header and normalizes
 *  FastAPI error `detail` payloads into a thrown ApiError. */

const BASE = (import.meta.env.PUBLIC_API_BASE_URL as string) || 'http://127.0.0.1:8000/api';

export class ApiError extends Error {
  status: number;
  detail: any;
  dependents?: Record<string, number> | null;
  constructor(status: number, detail: any, dependents?: Record<string, number> | null) {
    super(typeof detail === 'string' ? detail : 'Request failed');
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
    this.dependents = dependents;
  }
}

function readCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]+)'));
  return m ? decodeURIComponent(m[1]) : undefined;
}

export function getToken(): string | undefined {
  return readCookie('authToken');
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

export async function apiFetch(path: string, opts: RequestOpts = {}): Promise<any> {
  const url = new URL(path, BASE);
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
  let res: Response;
  try {
    res = await fetch(url.toString(), {
      method: opts.method ?? 'GET',
      headers,
      body: opts.body instanceof FormData ? opts.body : isForm ? opts.body.toString() : opts.body !== undefined ? JSON.stringify(opts.body) : undefined
    });
  } catch {
    throw new ApiError(0, 'Network error — is the backend running?');
  }
  if (res.status === 204) return null;
  const text = await res.text();
  let data: any = null;
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }
  if (!res.ok) {
    const dependents = data?.detail?.dependents ?? data?.dependents ?? null;
    throw new ApiError(res.status, normalizeDetail(data), dependents);
  }
  return data;
}
