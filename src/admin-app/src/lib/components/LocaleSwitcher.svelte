<!-- Locale switcher (AR/EN). Toggles the LOCALE cookie and updates the store. -->
<script lang="ts">
  import { localeStore, setLocale, type Locale } from '$lib/stores/locale';
  import { t } from '$lib/i18n';
  function toggle() {
    const next: Locale = $localeStore.locale === 'ar' ? 'en' : 'ar';
    setLocale(next);
  }
</script>

<button class="switch" onclick={toggle} aria-label={t('admin.common.switchLanguage')}>
  <span class="dot" class:on={$localeStore.locale === 'ar'}>ع</span>
  <span class="bar"></span>
  <span class="dot" class:on={$localeStore.locale === 'en'}>EN</span>
</button>

<style>
  .switch { display: inline-flex; align-items: center; gap: 0.4rem; background: var(--paper-2); border: 1px solid var(--line-strong); border-radius: 999px; padding: 0.25rem 0.55rem; cursor: pointer; font-size: 0.8rem; font-weight: 600; }
  .dot { color: var(--muted); }
  .dot.on { color: var(--accent-deep); }
  .bar { width: 1px; height: 14px; background: var(--line-strong); }
</style>
