<!-- Native select, warm-styled. Replaces Radix Select (unused even in the old admin). -->
<script lang="ts">
  let { label, value = $bindable(''), options = [], placeholder = '', error = '', ...rest }: any = $props();
</script>

<label class="field">
  {#if label}<span class="lbl">{label}</span>{/if}
  <select class="sel" bind:value {...rest}>
    {#if placeholder}<option value="" disabled>{placeholder}</option>{/if}
    {#each options as opt}
      <option value={opt.value}>{opt.label}</option>
    {/each}
  </select>
  {#if error}<span class="err">{error}</span>{/if}
</label>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.82rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.3rem; }
  .sel {
    width: 100%;
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--ink);
    background: var(--paper);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.6rem 0.7rem;
  }
  .sel:focus { outline: none; border-color: var(--ochre); box-shadow: 0 0 0 2px rgba(181, 134, 46, 0.25); }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.25rem; }
</style>
