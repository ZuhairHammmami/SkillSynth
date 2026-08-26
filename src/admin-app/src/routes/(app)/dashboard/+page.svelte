<!-- Admin dashboard placeholder (Task 13 builds the full version). -->
<script lang="ts">
  import Panel from '$lib/components/ui/Panel.svelte';
  import Illustration from '$lib/components/Illustration.svelte';
</script>

<h1>Dashboard</h1>
<div class="grid">
  <Panel title="Platform overview"><Illustration name="path" width={160} /></Panel>
  <Panel title="Recent activity"><p class="muted">Loading console…</p></Panel>
</div>

<style>
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top: 1rem; }
</style>
