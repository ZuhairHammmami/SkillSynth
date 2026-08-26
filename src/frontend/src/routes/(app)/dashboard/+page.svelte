<!-- Dashboard placeholder (Task 7 builds the full version). -->
<script lang="ts">
  import Illustration from '$lib/components/Illustration.svelte';
  import Panel from '$lib/components/ui/Panel.svelte';
</script>

<h1>Dashboard</h1>
<div class="grid">
  <Panel title="Your progress"><Illustration name="path" width={160} /></Panel>
  <Panel title="Recent activity"><p class="muted">Coming together…</p></Panel>
</div>

<style>
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top: 1rem; }
</style>
