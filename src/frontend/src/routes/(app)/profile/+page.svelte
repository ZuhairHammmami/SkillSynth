<!-- Profile: edit name/email and change password. -->
<script lang="ts">
  import { authStore, updateProfile, changePassword } from '$lib/stores/auth';
  import { apiFetch, ApiError } from '$lib/api/client';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';
  import { name as validateName, email as validateEmail, password as validatePassword } from '$lib/validation';

  let name = $state($authStore.user?.full_name ?? '');
  let email = $state($authStore.user?.email ?? '');
  let savingProfile = $state(false);

  let cur = $state('');
  let next = $state('');
  let confirm = $state('');
  let savingPw = $state(false);

  const nameKey = $derived(name.trim() ? validateName(name) : null);
  const emailKey = $derived(email.trim() ? validateEmail(email) : null);
  const profileValid = $derived(validateName(name) === null && validateEmail(email) === null);

  const curValid = $derived(cur.trim() !== '');
  const newValid = $derived(validatePassword(next) === null);
  const confirmKey = $derived(
    confirm ? (confirm !== next ? 'validation.passwordsNoMatch' : null) : null
  );
  const confirmValid = $derived(next === confirm && confirm !== '');
  const pwValid = $derived(curValid && newValid && confirmValid);

  async function saveProfile() {
    savingProfile = true;
    try {
      await updateProfile({ full_name: name, email });
      success(t('updateProfile.updateSuccess'));
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : t('updateProfile.updateError'));
    } finally {
      savingProfile = false;
    }
  }

  async function savePassword() {
    if (!pwValid) return;
    savingPw = true;
    try {
      await changePassword(cur, next);
      cur = next = confirm = '';
      success(t('updateProfile.updateSuccess'));
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : t('updateProfile.updateError'));
    } finally {
      savingPw = false;
    }
  }
</script>

<h1>{t('profilePage.title')}</h1>
<p class="muted">{t('profilePage.subtitle')}</p>

<Panel>
  <div class="stack">
    <Input label={t('profilePage.name')} bind:value={name} error={nameKey ? t(nameKey) : ''} />
    <Input label={t('profilePage.email')} type="email" bind:value={email} error={emailKey ? t(emailKey) : ''} />
    <Button onclick={saveProfile} disabled={!profileValid || savingProfile}>{t('common.save')}</Button>
  </div>
</Panel>

<Panel>
  <h3>{t('profilePage.changePassword')}</h3>
  <div class="stack">
    <Input label={t('profilePage.currentPassword')} type="password" bind:value={cur} />
    <Input label={t('profilePage.newPassword')} type="password" bind:value={next} hint={t('registerForm.passwordHint')} />
    <Input label={t('profilePage.confirmPassword')} type="password" bind:value={confirm} error={confirmKey ? t(confirmKey) : ''} />
    <Button onclick={savePassword} disabled={!pwValid || savingPw}>{t('common.save')}</Button>
  </div>
</Panel>

<style>
  h1 { margin-bottom: 0.2rem; }
  h3 { margin-top: 0; }
  .stack { display: flex; flex-direction: column; gap: 1rem; }
</style>
