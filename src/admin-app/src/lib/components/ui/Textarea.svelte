<!-- Accessible textarea. Explicit label association, error via aria-describedby +
     role="alert", 44px-min target, focus ring. -->
<script lang="ts">
  let { label, value = $bindable(), placeholder = '', error = '', rows = 4, id, ...rest }: any = $props();
  const uid = `ta-${Math.random().toString(36).slice(2, 9)}`;
  const fieldId = $derived(id || uid);
  const errId = $derived(`${fieldId}-err`);
</script>

<div class="field">
  {#if label}<label class="lbl" for={fieldId}>{label}</label>{/if}
  <textarea
    class="ta"
    id={fieldId}
    {rows}
    {placeholder}
    bind:value
    aria-invalid={error ? 'true' : undefined}
    aria-describedby={error ? errId : undefined}
    {...rest}
  ></textarea>
  {#if error}<span class="err" id={errId} role="alert">{error}</span>{/if}
</div>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.82rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.3rem; }
  .ta {
    width: 100%;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--ink);
    background: var(--card);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.6rem 0.7rem;
    resize: vertical;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .ta::placeholder { color: var(--clay); }
  .ta:focus-visible {
    outline: none;
    border-color: var(--ring);
    box-shadow: 0 0 0 3px var(--focus-glow);
  }
  .ta[aria-invalid='true'] { border-color: var(--danger); }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.25rem; }
</style>
