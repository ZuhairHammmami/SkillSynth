<!-- Native select, warm-styled. Replaces Radix Select (unused even in the old admin). -->
<script module lang="ts">
  let _counter = 0;
</script>

<script lang="ts">
  let {
    label = '',
    value = $bindable(),
    options = [],
    placeholder = '',
    error = '',
    hint = '',
    id = '',
    ...rest
  }: any = $props();

  const uid = 'sel-' + ++_counter;
  const selId = $derived(id || uid);
  const errId = $derived(selId + '-err');
  const hintId = $derived(selId + '-hint');
</script>

<label class="field">
  {#if label}<span class="lbl">{label}</span>{/if}
  <select
    class="sel"
    class:invalid={!!error}
    bind:value
    id={selId}
    aria-invalid={error ? 'true' : undefined}
    aria-describedby={error ? errId : hint ? hintId : undefined}
    {...rest}
  >
    {#if placeholder}<option value="" disabled>{placeholder}</option>{/if}
    {#each options as opt}
      <option value={opt.value}>{opt.label}</option>
    {/each}
  </select>
  {#if hint && !error}<span class="hint" id={hintId}>{hint}</span>{/if}
  {#if error}<span class="err" id={errId} role="alert">{error}</span>{/if}
</label>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.35rem; }
  .sel {
    width: 100%;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--ink);
    background: var(--card);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.7rem 0.8rem;
    min-height: 44px;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .sel:focus { outline: none; border-color: var(--ring); box-shadow: 0 0 0 3px var(--focus-glow); }
  .sel.invalid { border-color: var(--danger); }
  .sel.invalid:focus { box-shadow: 0 0 0 3px var(--danger-soft); }
  .hint { display: block; color: var(--clay); font-size: 0.78rem; margin-top: 0.3rem; }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.3rem; }
</style>
