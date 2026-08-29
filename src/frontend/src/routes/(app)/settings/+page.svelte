<!-- Settings: locale + general preferences (kept deliberately small). -->
<script lang="ts">
  import { localeStore, setLocale } from '$lib/stores/locale';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import { success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  function save() {
    setLocale($localeStore.locale);
    success(t('settingsPage.saved'));
  }
</script>

<h1>{t('settingsPage.title')}</h1>
<p class="muted">{t('settingsPage.subtitle')}</p>

<Panel>
  <div class="stack">
    <Select label={t('settingsPage.language')} bind:value={$localeStore.locale} options={[{ value: 'en', label: 'English' }, { value: 'ar', label: 'العربية' }]} />
    <Button onclick={save}>{t('common.save')}</Button>
  </div>
</Panel>

<style>
  h1 { margin-bottom: 0.2rem; }
  .stack { display: flex; flex-direction: column; gap: 1rem; }
</style>
