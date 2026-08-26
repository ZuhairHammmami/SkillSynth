<!-- Admin login page (root route). Uses the admin auth store. -->
<script lang="ts">
  import { login, authStore } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { ApiError } from '$lib/api/client';
  import Illustration from '$lib/components/Illustration.svelte';

  let email = $state('');
  let password = $state('');
  let loading = $state(false);
  let err = $state('');

  $effect(() => {
    if ($authStore.user && $page.url.pathname === '/') goto('/dashboard');
  });

  async function submit(e: Event) {
    e.preventDefault();
    err = '';
    loading = true;
    try {
      await login(email, password);
      success('Welcome back');
      await goto('/dashboard');
    } catch (e) {
      const msg = e instanceof ApiError ? e.detail : e instanceof Error ? e.message : 'Login failed';
      err = msg;
      toastError(msg);
    } finally {
      loading = false;
    }
  }
</script>

<div class="wrap">
  <div class="side">
    <Illustration name="hero" width={320} />
    <h1>SkillSynth Admin</h1>
    <p class="muted">Operational console for the Adaptive Learning OS.</p>
  </div>
  <form class="card" onsubmit={submit}>
    <h2>Sign in</h2>
    {#if err}<p class="form-err">{err}</p>{/if}
    <Input label="Email" type="email" bind:value={email} placeholder="admin@skillsynth.io" required />
    <Input label="Password" type="password" bind:value={password} placeholder="••••••••" required />
    <Button type="submit" {loading} disabled={loading || !email || !password}>Sign in</Button>
  </form>
</div>

<style>
  .wrap { min-height: 100vh; display: grid; grid-template-columns: 1fr 1fr; }
  .side { background: var(--paper-2); border-inline-end: 1px solid var(--line); display: flex; flex-direction: column; justify-content: center; gap: 0.6rem; padding: 3rem; }
  .side h1 { font-size: 2rem; margin: 0; }
  .card { display: flex; flex-direction: column; gap: 0.9rem; align-self: center; width: min(380px, 92vw); }
  .card h2 { font-size: 1.6rem; margin: 0; }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0; }
  @media (max-width: 800px) { .wrap { grid-template-columns: 1fr; } .side { display: none; } }
</style>
