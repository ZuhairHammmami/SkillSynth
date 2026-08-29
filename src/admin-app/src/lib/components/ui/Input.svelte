<!-- Accessible text input. Explicit label association, error linked via
     aria-describedby + role="alert", 44px target, focus ring from tokens. -->
<script lang="ts">
  let { label, value = $bindable(), type = 'text', placeholder = '', error = '', hint = '', id, ...rest }: any = $props();
  const uid = `in-${Math.random().toString(36).slice(2, 9)}`;
  const fieldId = $derived(id || uid);
  const errId = $derived(`${fieldId}-err`);
  const hintId = $derived(`${fieldId}-hint`);
</script>

<div class="field">
  {#if label}<label class="lbl" for={fieldId}>{label}</label>{/if}
  <input
    class="input"
    id={fieldId}
    {type}
    {placeholder}
    bind:value
    aria-invalid={error ? 'true' : undefined}
    aria-describedby={error ? errId : hint ? hintId : undefined}
    {...rest}
  />
  {#if hint && !error}<span class="hint" id={hintId}>{hint}</span>{/if}
  {#if error}<span class="err" id={errId} role="alert">{error}</span>{/if}
</div>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.82rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.3rem; }
  .input {
    width: 100%;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--ink);
    background: var(--card);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.6rem 0.7rem;
    min-height: 44px;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .input::placeholder { color: var(--clay); }
  .input:focus-visible {
    outline: none;
    border-color: var(--ring);
    box-shadow: 0 0 0 3px var(--focus-glow);
  }
  .input[aria-invalid='true'] { border-color: var(--danger); }
  .hint { display: block; color: var(--clay); font-size: 0.78rem; margin-top: 0.25rem; }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.25rem; }
</style>
