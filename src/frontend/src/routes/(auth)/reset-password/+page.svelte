<!-- Reset password. Reads ?token=, submits the new password. -->
<script lang="ts">
  import { page } from '$app/stores';
  import { resetPassword } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { ApiError } from '$lib/api/client';

  const token = $derived($page.url.searchParams.get('token') || '');

  let password = $state('');
  let loading = $state(false);
  let bad = $state(false);

  async function submit(e: Event) {
    e.preventDefault();
    if (!token) { bad = true; return; }
    loading = true;
    try {
      await resetPassword(token, password);
      success(t('resetPasswordPage.success'));
      await goto('/login');
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Reset failed');
    } finally {
      loading = false;
    }
  }
</script>

<form class="card" onsubmit={submit}>
  <h1>{t('resetPasswordPage.title')}</h1>
  <p class="muted">{t('resetPasswordPage.subtitle')}</p>
  {#if bad}<p class="form-err">{t('resetPasswordPage.badToken')}</p>{/if}
  <Input label={t('resetPasswordForm.password')} type="password" bind:value={password} required />
  <Button type="submit" {loading} disabled={loading || !password}>{t('resetPasswordForm.submit')}</Button>
</form>

<style>
  .card { width: min(380px, 92vw); display: flex; flex-direction: column; gap: 0.9rem; }
  h1 { font-size: 1.8rem; margin: 0; }
  .form-err { color: var(--danger); font-size: 0.85rem; margin: 0; }
</style>
