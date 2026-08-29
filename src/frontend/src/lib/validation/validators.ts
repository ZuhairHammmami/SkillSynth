/**
 * Hand-rolled validators for the learner app — no deps, mirrors backend rules
 * (Spec §6; src/backend/dto/auth.py PasswordValidator). Every validator
 * returns an i18n KEY (`validation.*`) or null when valid; never display text.
 * Callers resolve keys with `t()` and pass the same params ({min}/{max}) they
 * gave the validator. Password decision: ONE `policyRequirements` key ({min})
 * for every unmet-policy failure (per-rule keys were rejected — the negotiated
 * i18n slot list is fixed); hard bounds 6..32 use `minLength`/`maxLength` and
 * whitespace uses `whitespace`. Learner mirrors the backend DEFAULT policy;
 * backend stays the authority (R-5).
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
const NAME_FORBIDDEN = /[<>"'\\]/;
const HEX_COLOR_RE = /^#[0-9a-fA-F]{6}$/;
const WHITESPACE = /\s/;
const SPECIAL_CHARS = '!@#$%^&*(),.?":{}|<>_-\\[]~`';

export type Validator = (value: any, ...args: any[]) => string | null;

/** Return `validation.required` when the trimmed value is empty, else null. */
export function required(value: string): string | null {
  return value.trim() === '' ? 'validation.required' : null;
}

/** Return a key when the email is empty, over 200 chars, or not simply addressed; else null. */
export function email(value: string): string | null {
  const v = value.trim();
  if (!v) return 'validation.required';
  return v.length > EMAIL_MAX || !EMAIL_RE.test(v) ? 'validation.emailInvalid' : null;
}

/** Return a key when the name is empty, holds < > " ' \, or exceeds 100 chars; else null. */
export function name(value: string): string | null {
  const v = value.trim();
  if (!v) return 'validation.required';
  if (NAME_FORBIDDEN.test(v)) return 'validation.nameChars';
  return v.length > 100 ? 'validation.nameTooLong' : null;
}

/** Return a key when the value violates the password policy (hard bounds, then single `policyRequirements` {min}, whitespace last); else null. */
export function password(
  value: string,
  policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY,
): string | null {
  if (!value) return 'validation.required';
  if (value.length > 32) return 'validation.maxLength';
  if (value.length < 6) return 'validation.minLength';
  if (value.length < policy.min_length) return 'validation.policyRequirements';
  if (policy.require_uppercase && !/[A-Z]/.test(value)) return 'validation.policyRequirements';
  if (policy.require_lowercase && !/[a-z]/.test(value)) return 'validation.policyRequirements';
  if (policy.require_digit && !/\d/.test(value)) return 'validation.policyRequirements';
  if (policy.require_special_char && !hasSpecial(value)) return 'validation.policyRequirements';
  return WHITESPACE.test(value) ? 'validation.whitespace' : null;
}

/** Helper that reports whether the value holds a backend special char; caller is password(). */
function hasSpecial(value: string): boolean {
  return value.split('').some((c) => SPECIAL_CHARS.includes(c));
}

/** Return `validation.maxLength` {max} when the value exceeds max chars, else null. */
export function maxLength(value: string, max: number): string | null {
  return value.length > max ? 'validation.maxLength' : null;
}

/** Return `validation.range` {min}/{max} when the value isn't a number in [min,max]; blank passed as null. */
export function range(value: string, min: number, max: number): string | null {
  const v = value.trim();
  if (v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) && n >= min && n <= max ? null : 'validation.range';
}

/** Return `validation.weeklyHoursRange` {min}/{max} when weekly hours fall outside the bound; blank passed as null. */
export function weeklyHours(value: string, min = 1, max = 80): string | null {
  const v = value.trim();
  if (v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) && n >= min && n <= max ? null : 'validation.weeklyHoursRange';
}

/** Return `validation.urlInvalid` unless the value (or blank) parses as an http(s) URL, else null. */
export function url(value: string): string | null {
  const v = value.trim();
  if (v === '') return null;
  try {
    const parsed = new URL(v);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:' ? null : 'validation.urlInvalid';
  } catch {
    return 'validation.urlInvalid';
  }
}

/** Return `validation.hexColorInvalid` unless the value (or blank) is `#` + 6 hex digits, else null. */
export function hexColor(value: string): string | null {
  const v = value.trim();
  return v === '' || HEX_COLOR_RE.test(v) ? null : 'validation.hexColorInvalid';
}

/** Return `validation.minOptions` {min} (default 2) when the array holds fewer than min options, else null. */
export function options(value: unknown[] | null | undefined, min = 2): string | null {
  return value && value.length >= min ? null : 'validation.minOptions';
}

/** Map `{field: [value, validator]}` to `{field: errorKey|null}`; parametrized validators must be wrapped (`(v) => maxLength(v, 200)`). */
export function validateForm(
  schema: Record<string, [unknown, Validator]>,
): Record<string, string | null> {
  const errors: Record<string, string | null> = {};
  for (const [field, [value, validate]] of Object.entries(schema)) {
    errors[field] = validate(value);
  }
  return errors;
}