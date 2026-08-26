<!-- Authenticated app shell: route guard + contents rail + SSE connection. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { onMount } from 'svelte';
  import { authStore, loadUser, getAuthToken } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { connectSSE } from '$lib/stores/sse';
  import NavRail from '$lib/components/NavRail.svelte';

  let { children }: any = $props();

  onMount(async () => {
    if (!getAuthToken()) {
      await goto('/login');
      return;
    }
    if (!$authStore.user) await loadUser();
    if (!$authStore.user) {
      await goto('/login');
      return;
    }
    connectSSE();
  });
</script>

{#if $authStore.user}
  <div class="shell">
    <NavRail />
    <main class="content">
      <div class="container pad">{@render children()}</div>
    </main>
  </div>
{/if}

<style>
  .shell { display: flex; min-height: 100vh; }
  .content { flex: 1; padding-block: 2rem; }
  .pad { padding-block: 0; }
</style>
