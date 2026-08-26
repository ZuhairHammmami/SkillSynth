<!-- Admin root layout: global CSS + toast viewport. -->
<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import Toaster from '$lib/components/ui/Toaster.svelte';

  let { children } = $props();
  onMount(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.lang = 'en';
      document.documentElement.dir = 'ltr';
    }
  });
</script>

{@render children()}
<Toaster />
