/** Cookie helpers shared across the student app. */
export function getCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]+)'));
  return m ? decodeURIComponent(m[1]) : undefined;
}

export function setCookie(name: string, value: string, days = 1): void {
  if (typeof document === 'undefined') return;
  const d = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${d}; path=/; SameSite=Lax`;
}

export function deleteCookie(name: string): void {
  if (typeof document === 'undefined') return;
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

/** Format an ISO date for display in the current locale. */
export function formatDate(iso: string | undefined, locale = 'en'): string {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString(locale === 'ar' ? 'ar' : 'en-US', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  } catch {
    return iso;
  }
}

/** Initials from a name or email, for avatars. */
export function getInitials(name: string | null | undefined, email?: string): string {
  const src = (name || email || '?').trim();
  const parts = src.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return src.slice(0, 2).toUpperCase();
}
