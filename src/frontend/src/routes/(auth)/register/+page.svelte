<!-- Register page. Creates an account, then routes to login. -->
<script lang="ts">
  import { register } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { error as toastError, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { ApiError } from '$lib/api/client';

  let fullName = $state('');
  let email = $state('');
  let password = $state('');
  let loading = $state(false);

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
  <Input label={t('registerForm.name')} bind:value={fullName} placeholder={t('registerForm.namePlaceholder')} />
  <Input label={t('registerForm.email')} type="email" bind:value={email} required />
  <Input label={t('registerForm.password')} type="password" bind:value={password} required />
  <Button type="submit" {loading} disabled={loading || !email || !password}>{t('registerForm.submit')}</Button>
  <div class="links"><a href="/login">{t('registerPage.hasAccount')}</a></div>
</form>

<style>
  .card { width: min(380px, 92vw); display: flex; flex-direction: column; gap: 0.9rem; }
  h1 { font-size: 1.8rem; margin: 0; }
  .links { font-size: 0.85rem; }
</style>
