<!-- Register page. Creates an account, then routes to login. -->
<script lang="ts">
  import { register } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { ApiError } from '$lib/api/client';
  import { name as validateName, email as validateEmail, password as validatePassword } from '$lib/validation';

  let fullName = $state('');
  let email = $state('');
  let password = $state('');
  let loading = $state(false);

  const nameKey = $derived(fullName.trim() ? validateName(fullName) : null);
  const emailKey = $derived(email.trim() ? validateEmail(email) : null);
  const pwKey = $derived(password ? validatePassword(password) : null);
  const nameValid = $derived(validateName(fullName) === null);
  const emailValid = $derived(validateEmail(email) === null);
  const pwValid = $derived(validatePassword(password) === null);
  const valid = $derived(nameValid && emailValid && pwValid);

  async function submit(e: Event) {
    e.preventDefault();
    loading = true;
    try {
      await register(email, password, fullName);
      success(t('registerPage.success'));
      await goto('/login');
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Registration failed');
    } finally {
      loading = false;
    }
  }
</script>

<form class="card" onsubmit={submit}>
  <h1>{t('registerPage.title')}</h1>
  <p class="muted">{t('registerPage.subtitle')}</p>
  <Input label={t('registerForm.nameLabel')} bind:value={fullName} placeholder={t('registerForm.namePlaceholder')} error={nameKey ? t(nameKey) : ''} />
  <Input label={t('registerForm.emailLabel')} type="email" bind:value={email} required error={emailKey ? t(emailKey) : ''} />
  <Input label={t('registerForm.passwordLabel')} type="password" bind:value={password} required hint={t('registerForm.passwordHint')} error={pwKey ? t(pwKey) : ''} />
  <Button type="submit" {loading} disabled={loading || !valid}>{t('registerForm.createButton')}</Button>
  <div class="links"><a href="/login">{t('registerPage.hasAccount')}</a></div>
</form>

<style>
  .card { width: min(380px, 92vw); display: flex; flex-direction: column; gap: 0.9rem; }
  h1 { font-size: 1.8rem; margin: 0; }
  .links { font-size: 0.85rem; }
</style>
