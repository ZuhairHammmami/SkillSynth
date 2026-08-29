<!-- Admin contents rail. Bilingual (AR/EN); 15 sections. -->
<script lang="ts">
  import { page } from '$app/stores';
  import { authStore, logout } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Icon from '$lib/icons/Icon.svelte';
  import Logo from '$lib/components/Logo.svelte';
  import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
  import { t } from '$lib/i18n';
  import { getInitials } from '$lib/util';

  const items = $derived([
    { href: '/dashboard', label: t('admin.nav.dashboard'), icon: 'dashboard' },
    { href: '/users', label: t('admin.nav.users'), icon: 'users' },
    { href: '/categories', label: t('admin.nav.categories'), icon: 'category' },
    { href: '/skills', label: t('admin.nav.skills'), icon: 'learn' },
    { href: '/resources', label: t('admin.nav.resources'), icon: 'resource' },
    { href: '/job-roles', label: t('admin.nav.jobRoles'), icon: 'role' },
    { href: '/assessments', label: t('admin.nav.assessments'), icon: 'quiz' },
    { href: '/paths', label: t('admin.nav.paths'), icon: 'path' },
    { href: '/reports', label: t('admin.nav.reports'), icon: 'analytics' },
    { href: '/health', label: t('admin.nav.systemHealth'), icon: 'shield' },
    { href: '/settings', label: t('admin.nav.settings'), icon: 'settings' },
    { href: '/audit-logs', label: t('admin.nav.auditLogs'), icon: 'activity' },
    { href: '/backups', label: t('admin.nav.backups'), icon: 'database' },
    { href: '/db-inspector', label: t('admin.nav.dbInspector'), icon: 'layers' },
    { href: '/feature-flags', label: t('admin.nav.featureFlags'), icon: 'flag' }
  ]);

  function isActive(href: string): boolean {
    const p = $page.url.pathname;
    return p === href || p.startsWith(href + '/');
  }
  async function doLogout() {
    logout();
    await goto('/');
  }
</script>

<aside class="rail">
  <div class="brand"><Logo /></div>
  <nav class="nav">
    {#each items as it}
      <a class="nav-item" class:active={isActive(it.href)} href={it.href} aria-current={isActive(it.href) ? 'page' : undefined}>
        <span class="marker"></span>
        <Icon name={it.icon} size={18} />
        <span>{it.label}</span>
      </a>
    {/each}
  </nav>
  <div class="foot">
    <div class="who">
      <span class="avatar">{getInitials($authStore.user?.full_name, $authStore.user?.email)}</span>
      <span class="meta">
        <strong>{$authStore.user?.full_name || $authStore.user?.email}</strong>
        <small class="muted">{t('admin.common.administrator')}</small>
      </span>
    </div>
    <div class="foot-actions">
      <LocaleSwitcher />
      <button class="logout" onclick={doLogout} aria-label={t('nav.logout')}><Icon name="logout" size={18} /></button>
    </div>
  </div>
</aside>

<style>
  .rail {
    width: var(--rail-w); flex-shrink: 0; height: 100vh; position: sticky; top: 0;
    background: var(--paper-2); border-inline-end: 1px solid var(--line);
    display: flex; flex-direction: column; padding: 1.2rem 0.9rem;
  }
  .brand { padding: 0.3rem 0.5rem 1rem; }
  .nav { display: flex; flex-direction: column; gap: 0.15rem; flex: 1; overflow-y: auto; }
  .nav-item {
    display: flex; align-items: center; gap: 0.65rem; padding: 0.6rem 0.7rem; min-height: 44px;
    color: var(--ink-soft); border-radius: var(--radius); font-weight: 600; font-size: 0.92rem; position: relative;
  }
  .nav-item:hover { background: var(--ochre-soft); text-decoration: none; color: var(--ink); }
  .marker { width: 6px; height: 6px; border-radius: 50%; background: var(--line-strong); transition: background 0.15s; }
  .nav-item.active { color: var(--ochre-deep); background: var(--ochre-soft); }
  .nav-item.active .marker { background: var(--ochre); }
  .nav-item:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }
  .foot { border-top: 1px dashed var(--line-strong); padding-top: 0.8rem; display: flex; align-items: center; justify-content: space-between; }
  .who { display: flex; align-items: center; gap: 0.6rem; overflow: hidden; }
  .foot-actions { display: flex; align-items: center; gap: 0.5rem; }
  .avatar { width: 34px; height: 34px; border-radius: 50%; background: var(--ochre-soft); color: var(--ochre-deep); display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; flex-shrink: 0; }
  .meta { display: flex; flex-direction: column; line-height: 1.2; overflow: hidden; }
  .meta small { font-size: 0.7rem; }
  .logout { background: transparent; border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 0.35rem; cursor: pointer; color: var(--clay); display: inline-flex; }
  .logout:hover { color: var(--danger); border-color: var(--danger); }
</style>
