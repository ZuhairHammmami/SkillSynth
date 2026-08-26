<!-- Root layout: global CSS, locale init, toast viewport. -->
<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { initLocale } from '$lib/stores/locale';
  import Toaster from '$lib/components/ui/Toaster.svelte';

  let { children } = $props();
  onMount(() => initLocale());
</script>

{@render children()}
<Toaster />
