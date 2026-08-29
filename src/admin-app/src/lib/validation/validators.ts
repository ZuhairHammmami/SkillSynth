/**
 * Hand-rolled validators for the admin app — no deps; mirrors the learner lib
 * (src/frontend/src/lib/validation/validators.ts) for shared rules and treats
 * the backend (src/backend/dto/auth.py PasswordValidator) as the authority for
 * password policy (R-5). Return contract (Option B, uniform + documented):
 * every validator returns a FULL i18n dot-key that resolves inside the admin
 * `admin.validation` group, or null when valid — never display text. Callers
 * resolve keys with `t(key, params)`; the key name itself states which
 * placeholders apply ({field} always; {min}/{max} for parametrized keys), and
 * every docstring lists its caller's params. {field} must stay first in the
 * templates, identical in en + ar.
 */

export interface PasswordPolicy {
  min_length: number;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_digit: boolean;
  require_special_char: boolean;
}

export const DEFAULT_PASSWORD_POLICY: PasswordPolicy = {
  min_length: 8,
  require_uppercase: true,
  require_lowercase: true,
  require_digit: true,
  require_special_char: true,
};

const EMAIL_MAX = 200;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const NAME_MAX = 100;
const NAME_FORBIDDEN = /[<>"'\\]/;
const HEX_COLOR_RE = /^#[0-9a-fA-F]{6}$/;
const WHITESPACE = /\s/;
const SPECIAL_CHARS = '!@#$%^&*(),.?":{}|<>_-\\[]~`';

export type Validator = (value: any, ...args: any[]) => string | null;

/** Return `admin.validation.required` {field} when the trimmed value is empty; callee of every admin form, called with the raw field value. */
export function required(value: string): string | null {
  return value.trim() === '' ? 'admin.validation.required' : null;
}

/** Return required/invalidEmail {field} when the email is empty, over 200 chars, or not simply addressed; caller resolves with {field}. */
export function email(value: string): string | null {
  const v = value.trim();
  if (!v) return 'admin.validation.required';
  return v.length > EMAIL_MAX || !EMAIL_RE.test(v) ? 'admin.validation.invalidEmail' : null;
}

/** Return required/nameChars/maxLen when the name is empty, holds < > " ' \, or exceeds 100 chars; caller passes {field} (+ {max:100} for maxLen). */
export function name(value: string): string | null {
  const v = value.trim();
  if (!v) return 'admin.validation.required';
  if (NAME_FORBIDDEN.test(v)) return 'admin.validation.nameChars';
  return v.length > NAME_MAX ? 'admin.validation.maxLen' : null;
}

/** Return a password key for hard bounds 6/32 (minLen/maxLen), the policy (policyRequirements {min}), or whitespace; caller passes {field} and the flagged {min}/{max}. */
export function password(
  value: string,
  policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY,
): string | null {
  if (!value) return 'admin.validation.required';
  if (value.length > 32) return 'admin.validation.maxLen';
  if (value.length < 6) return 'admin.validation.minLen';
  if (value.length < policy.min_length) return 'admin.validation.policyRequirements';
  if (policy.require_uppercase && !/[A-Z]/.test(value)) return 'admin.validation.policyRequirements';
  if (policy.require_lowercase && !/[a-z]/.test(value)) return 'admin.validation.policyRequirements';
  if (policy.require_digit && !/\d/.test(value)) return 'admin.validation.policyRequirements';
  if (policy.require_special_char && !hasSpecial(value)) return 'admin.validation.policyRequirements';
  return WHITESPACE.test(value) ? 'admin.validation.whitespace' : null;
}

/** Helper that reports whether the value holds a backend special char; caller is password(). */
function hasSpecial(value: string): boolean {
  return value.split('').some((c) => SPECIAL_CHARS.includes(c));
}

/** Return `admin.validation.maxLen` {field}/{max} when the value exceeds max chars (100/150/200/2000); caller wraps to bind max. */
export function maxLength(value: string, max: number): string | null {
  return value.length > max ? 'admin.validation.maxLen' : null;
}

/** Return `admin.validation.minMax` {field}/{min}/{max} when the value isn't a number in [min,max] (0-5, 1-80, 0-100); blank passes as null. */
export function range(value: string, min: number, max: number): string | null {
  const v = value.trim();
  if (v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) && n >= min && n <= max ? null : 'admin.validation.minMax';
}

/** Return `admin.validation.nonNegative` {field} when the value is a negative or non-numeric number; blank passes as null (duration/hours ≥ 0). */
export function nonNegative(value: string): string | null {
  const v = value.trim();
  if (v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? null : 'admin.validation.nonNegative';
}

/** Return required/positiveInt {field} when a numeric FK id (category_id, skill_id, assessment_id, path_id) is blank or not an integer > 0; else null. */
export function positiveInt(value: number | string): string | null {
  const raw = typeof value === 'string' ? value.trim() : String(value);
  if (raw === '') return 'admin.validation.required';
  const n = Number(raw);
  return Number.isInteger(n) && n > 0 ? null : 'admin.validation.positiveInt';
}

/** Return `admin.validation.url` {field} unless the value (or blank) parses as an http(s) URL; caller resolves with {field}. */
export function url(value: string): string | null {
  const v = value.trim();
  if (v === '') return null;
  try {
    const parsed = new URL(v);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
      ? null
      : 'admin.validation.url';
  } catch {
    return 'admin.validation.url';
  }
}

/** Return `admin.validation.hexColor` {field} unless the value (or blank) is `#` + exactly 6 hex digits (case-insensitive); else null. */
export function hexColor(value: string): string | null {
  const v = value.trim();
  return v === '' || HEX_COLOR_RE.test(v) ? null : 'admin.validation.hexColor';
}

/** Return `admin.validation.minOptions` {min} when an assessment-question options array holds fewer than min (default 2); else null. */
export function options(value: unknown[] | null | undefined, min = 2): string | null {
  return value && value.length >= min ? null : 'admin.validation.minOptions';
}

/** Map `{field: [value, validator]}` to `{field: errorKey|null}`; parametrized validators must be wrapped, e.g. `(v) => maxLength(v, 200)` — kept for T16. */
export function validateForm(
  schema: Record<string, [unknown, Validator]>,
): Record<string, string | null> {
  const errors: Record<string, string | null> = {};
  for (const [field, [value, validate]] of Object.entries(schema)) {
    errors[field] = validate(value);
  }
  return errors;
}