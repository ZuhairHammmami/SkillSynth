<!-- Accessible native select. Explicit label association, error via
     aria-describedby + role="alert", 44px target, focus ring.
     Numeric FK values are normalized to strings for the DOM (<select> only
     round-trips strings) and round-tripped back to their original type on
     change, so number/string mismatches no longer break preselection. -->
<script lang="ts">
  let { label, value = $bindable(), options = [], placeholder = '', error = '', id, ...rest }: any = $props();
  const uid = `sel-${Math.random().toString(36).slice(2, 9)}`;
  const fieldId = $derived(id || uid);
  const errId = $derived(`${fieldId}-err`);

  // Keep the original (possibly numeric) value alongside its string form so we
  // can preserve the bound type and match by string for preselection.
  const norm = $derived(
    (options || []).map((o: any) => {
      const raw = o?.value;
      return { ...o, _raw: raw, _str: raw == null ? '' : String(raw) };
    })
  );
  const strValue = $derived(value == null ? '' : String(value));

  function handle(e: Event) {
    const picked = (e.currentTarget as HTMLSelectElement).value;
    const match = norm.find((o: any) => o._str === picked);
    value = match ? match._raw : picked;
  }
</script>

<div class="field">
  {#if label}<label class="lbl" for={fieldId}>{label}</label>{/if}
  <select
    class="sel"
    id={fieldId}
    value={strValue}
    onchange={handle}
    aria-invalid={error ? 'true' : undefined}
    aria-describedby={error ? errId : undefined}
    {...rest}
  >
    {#if placeholder}<option value="">{placeholder}</option>{/if}
    {#each norm as opt}
      <option value={opt._str}>{opt.label}</option>
    {/each}
  </select>
  {#if error}<span class="err" id={errId} role="alert">{error}</span>{/if}
</div>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.82rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.3rem; }
  .sel {
    width: 100%;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--ink);
    background: var(--paper);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.6rem 0.7rem;
    min-height: 44px;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .sel:focus-visible {
    outline: none;
    border-color: var(--ring);
    box-shadow: 0 0 0 3px var(--focus-glow);
  }
  .sel[aria-invalid='true'] { border-color: var(--danger); }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.25rem; }
</style>
