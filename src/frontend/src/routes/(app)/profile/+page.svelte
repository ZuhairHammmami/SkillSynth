<!-- Profile: edit name/email and change password. -->
<script lang="ts">
  import { authStore, updateProfile, changePassword } from '$lib/stores/auth';
  import { apiFetch, ApiError } from '$lib/api/client';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import { success, error as toastError } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let name = $state($authStore.user?.full_name ?? '');
  let email = $state($authStore.user?.email ?? '');
  let savingProfile = $state(false);

  let cur = $state('');
  let next = $state('');
  let confirm = $state('');
  let savingPw = $state(false);

  async function saveProfile() {
    savingProfile = true;
    try {
      await updateProfile({ full_name: name, email });
      success('Profile saved');
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Save failed');
    } finally {
      savingProfile = false;
    }
  }

  async function savePassword() {
    if (next !== confirm) { toastError('Passwords do not match'); return; }
    savingPw = true;
    try {
      await changePassword(cur, next);
      cur = next = confirm = '';
      success('Password updated');
    } catch (e) {
      toastError(e instanceof ApiError ? e.detail : 'Update failed');
    } finally {
      savingPw = false;
    }
  }
</script>

<h1>{t('profilePage.title')}</h1>
<p class="muted">{t('profilePage.subtitle')}</p>

<Panel>
  <Field label={t('profilePage.name')}>
    <Input bind:value={name} />
  </Field>
  <Field label={t('profilePage.email')}>
    <Input type="email" bind:value={email} />
  </Field>
  <Button onclick={saveProfile} disabled={savingProfile}>{t('common.save')}</Button>
</Panel>

<Panel>
  <h3>{t('profilePage.changePassword')}</h3>
  <Field label={t('profilePage.currentPassword')}>
    <Input type="password" bind:value={cur} />
  </Field>
  <Field label={t('profilePage.newPassword')}>
    <Input type="password" bind:value={next} />
  </Field>
  <Field label={t('profilePage.confirmPassword')}>
    <Input type="password" bind:value={confirm} />
  </Field>
  <Button onclick={savePassword} disabled={savingPw}>{t('common.save')}</Button>
</Panel>

<style>
  h1 { margin-bottom: 0.2rem; }
  h3 { margin-top: 0; }
</style>
