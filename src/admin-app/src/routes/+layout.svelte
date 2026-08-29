<!-- Admin root layout: global CSS + toast viewport. -->
<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import Toaster from '$lib/components/ui/Toaster.svelte';
  import { initLocale } from '$lib/stores/locale';

  let { children } = $props();
  onMount(() => {
    initLocale();
  });
</script>

{@render children()}
<Toaster />
