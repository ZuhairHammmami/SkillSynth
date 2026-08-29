<!-- Text input. Hand-styled, no UI-kit. -->
<script module lang="ts">
  let _counter = 0;
</script>

<script lang="ts">
  let {
    label = '',
    value = $bindable(),
    type = 'text',
    placeholder = '',
    error = '',
    hint = '',
    id = '',
    ...rest
  }: any = $props();

  const uid = 'in-' + ++_counter;
  const inputId = $derived(id || uid);
  const errId = $derived(inputId + '-err');
  const hintId = $derived(inputId + '-hint');
</script>

<label class="field">
  {#if label}<span class="lbl" id={inputId + '-lbl'}>{label}</span>{/if}
  <input
    class="input"
    class:invalid={!!error}
    {type}
    {placeholder}
    bind:value
    id={inputId}
    aria-invalid={error ? 'true' : undefined}
    aria-describedby={error ? errId : hint ? hintId : undefined}
    {...rest}
  />
  {#if hint && !error}<span class="hint" id={hintId}>{hint}</span>{/if}
  {#if error}<span class="err" id={errId} role="alert">{error}</span>{/if}
</label>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.35rem; }
  .input {
    width: 100%;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--ink);
    background: var(--paper);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.7rem 0.8rem;
    min-height: 44px;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .input:focus { outline: none; border-color: var(--ring); box-shadow: 0 0 0 3px var(--focus-glow); }
  .input.invalid { border-color: var(--danger); }
  .input.invalid:focus { box-shadow: 0 0 0 3px var(--danger-soft); }
  .hint { display: block; color: var(--muted); font-size: 0.78rem; margin-top: 0.3rem; }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.3rem; }
</style>
