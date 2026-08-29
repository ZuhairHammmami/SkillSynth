<!-- Admin settings page: client-side preferences (locale) and account info.
     No dedicated backend endpoint, so this page is read/adjust-only. -->
<script lang="ts">
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { t } from '$lib/i18n';
  import { localeStore, setLocale, type Locale } from '$lib/stores/locale';
  import { authStore } from '$lib/stores/auth';

  const langs: { code: Locale; label: string }[] = [
    { code: 'en', label: 'English' },
    { code: 'ar', label: 'العربية' }
  ];

  function pick(code: Locale) { setLocale(code); }
</script>

<h1>{t('admin.settings.title')}</h1>

<Panel title={t('admin.settings.language')}>
  <div class="langs">
    {#each langs as l}
      <Button
        variant={$localeStore.locale === l.code ? 'primary' : 'ghost'}
        onclick={() => pick(l.code)}
        aria-pressed={$localeStore.locale === l.code}
      >{l.label}</Button>
    {/each}
  </div>
</Panel>

<Panel title={t('admin.settings.account')}>
  <dl class="info">
    <div><dt>{t('admin.common.name')}</dt><dd>{$authStore.user?.full_name || '—'}</dd></div>
    <div><dt>{t('admin.common.email')}</dt><dd>{$authStore.user?.email || '—'}</dd></div>
    <div><dt>{t('admin.common.admin')}</dt><dd>{$authStore.user?.is_admin ? t('admin.common.yes') : t('admin.common.no')}</dd></div>
  </dl>
</Panel>

<style>
  .langs { display: flex; gap: 0.6rem; flex-wrap: wrap; }
  .info { display: grid; gap: 0.6rem; margin: 0; }
  .info > div { display: flex; justify-content: space-between; gap: 1rem; border-bottom: 1px solid var(--line); padding-bottom: 0.5rem; }
  .info dt { color: var(--clay); font-size: 0.85rem; }
  .info dd { margin: 0; font-weight: 600; }
</style>
