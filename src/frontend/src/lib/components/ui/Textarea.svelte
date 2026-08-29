<!-- Textarea. Hand-styled. -->
<script module lang="ts">
  let _counter = 0;
</script>

<script lang="ts">
  let {
    label = '',
    value = $bindable(),
    placeholder = '',
    error = '',
    hint = '',
    rows = 4,
    id = '',
    ...rest
  }: any = $props();

  const uid = 'ta-' + ++_counter;
  const taId = $derived(id || uid);
  const errId = $derived(taId + '-err');
  const hintId = $derived(taId + '-hint');
</script>

<label class="field">
  {#if label}<span class="lbl">{label}</span>{/if}
  <textarea
    class="ta"
    class:invalid={!!error}
    {rows}
    {placeholder}
    bind:value
    id={taId}
    aria-invalid={error ? 'true' : undefined}
    aria-describedby={error ? errId : hint ? hintId : undefined}
    {...rest}
  ></textarea>
  {#if hint && !error}<span class="hint" id={hintId}>{hint}</span>{/if}
  {#if error}<span class="err" id={errId} role="alert">{error}</span>{/if}
</label>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.35rem; }
  .ta {
    width: 100%;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--ink);
    background: var(--paper);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.7rem 0.8rem;
    resize: vertical;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .ta:focus { outline: none; border-color: var(--ring); box-shadow: 0 0 0 3px var(--focus-glow); }
  .ta.invalid { border-color: var(--danger); }
  .ta.invalid:focus { box-shadow: 0 0 0 3px var(--danger-soft); }
  .hint { display: block; color: var(--muted); font-size: 0.78rem; margin-top: 0.3rem; }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.3rem; }
</style>
