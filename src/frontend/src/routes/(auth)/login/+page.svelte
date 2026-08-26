<!-- Login page. Uses the auth store; redirects to the dashboard on success. -->
<script lang="ts">
  import { login } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { ApiError } from '$lib/api/client';

  let email = $state('');
  let password = $state('');
  let loading = $state(false);
  let err = $state('');

  async function submit(e: Event) {
    e.preventDefault();
    err = '';
    loading = true;
    try {
      await login(email, password);
      success(t('loginPage.success'));
      await goto('/dashboard');
    } catch (e) {
      const msg = e instanceof ApiError ? e.detail : 'Login failed';
      err = msg;
      toastError(msg);
    } finally {
      loading = false;
    }
  }
</script>

<form class="card" onsubmit={submit}>
  <h1>{t('loginPage.title')}</h1>
  <p class="muted">{t('loginPage.subtitle')}</p>
  {#if err}<p class="form-err">{err}</p>{/if}
  <Input label={t('loginForm.email')} type="email" bind:value={email} placeholder="you@example.com" required />
  <Input label={t('loginForm.password')} type="password" bind:value={password} placeholder="••••••••" required />
  <Button type="submit" {loading} disabled={loading || !email || !password}>{t('loginForm.submit')}</Button>
  <div class="links">
    <a href="/forgot-password">{t('loginPage.forgot')}</a>
    <a href="/register">{t('loginPage.noAccount')}</a>
  </div>
</form>

<style>
  .card { width: min(380px, 92vw); display: flex; flex-direction: column; gap: 0.9rem; }
  h1 { font-size: 1.8rem; margin: 0; }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0; }
  .links { display: flex; justify-content: space-between; font-size: 0.85rem; }
</style>
