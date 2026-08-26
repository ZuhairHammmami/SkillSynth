<!-- Forgot password. Requests a reset token; in dev the backend returns the
     token so we surface a direct reset link. -->
<script lang="ts">
  import { forgotPassword } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { ApiError } from '$lib/api/client';

  let email = $state('');
  let loading = $state(false);
  let devLink = $state('');

  async function submit(e: Event) {
    e.preventDefault();
    loading = true;
    try {
      const res = await forgotPassword(email);
      success(t('forgotPasswordPage.success'));
      if (res?.reset_token) devLink = `/reset-password?token=${res.reset_token}`;
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Request failed');
    } finally {
      loading = false;
    }
  }
</script>

<form class="card" onsubmit={submit}>
  <h1>{t('forgotPasswordPage.title')}</h1>
  <p class="muted">{t('forgotPasswordPage.subtitle')}</p>
  <Input label={t('forgotPasswordForm.email')} type="email" bind:value={email} required />
  <Button type="submit" {loading} disabled={loading || !email}>{t('forgotPasswordForm.submit')}</Button>
  {#if devLink}
    <p class="dev"><a href={devLink}>{t('forgotPasswordPage.devLink')}</a></p>
  {/if}
  <div class="links"><a href="/login">{t('forgotPasswordPage.back')}</a></div>
</form>

<style>
  .card { width: min(380px, 92vw); display: flex; flex-direction: column; gap: 0.9rem; }
  h1 { font-size: 1.8rem; margin: 0; }
  .dev { font-size: 0.85rem; }
  .links { font-size: 0.85rem; }
</style>
