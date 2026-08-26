<!-- Textarea. Hand-styled. -->
<script lang="ts">
  let { label, value = $bindable(''), placeholder = '', error = '', rows = 4, ...rest }: any = $props();
</script>

<label class="field">
  {#if label}<span class="lbl">{label}</span>{/if}
  <textarea class="ta" {rows} {placeholder} bind:value {...rest}></textarea>
  {#if error}<span class="err">{error}</span>{/if}
</label>

<style>
  .field { display: block; }
  .lbl { display: block; font-size: 0.82rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.3rem; }
  .ta {
    width: 100%;
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--ink);
    background: var(--paper);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.6rem 0.7rem;
    resize: vertical;
  }
  .ta:focus { outline: none; border-color: var(--ochre); box-shadow: 0 0 0 2px rgba(181, 134, 46, 0.25); }
  .err { display: block; color: var(--danger); font-size: 0.78rem; margin-top: 0.25rem; }
</style>
