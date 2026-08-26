<!-- Admin contents rail. English-only; 15 sections; is_admin gate handled by
     the auth store + layout guard. No locale switcher (admin is EN-only). -->
<script lang="ts">
  import { page } from '$app/stores';
  import { authStore, logout } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Icon from '$lib/icons/Icon.svelte';
  import Logo from '$lib/components/Logo.svelte';
  import { getInitials } from '$lib/util';

  const items = [
    { href: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { href: '/users', label: 'Users', icon: 'users' },
    { href: '/categories', label: 'Categories', icon: 'category' },
    { href: '/skills', label: 'Skills', icon: 'learn' },
    { href: '/resources', label: 'Resources', icon: 'resource' },
    { href: '/job-roles', label: 'Job Roles', icon: 'role' },
    { href: '/assessments', label: 'Assessments', icon: 'quiz' },
    { href: '/paths', label: 'Paths', icon: 'path' },
    { href: '/reports', label: 'Reports', icon: 'analytics' },
    { href: '/health', label: 'System Health', icon: 'shield' },
    { href: '/settings', label: 'Settings', icon: 'settings' },
    { href: '/audit-logs', label: 'Audit Logs', icon: 'activity' },
    { href: '/backups', label: 'Backups', icon: 'database' },
    { href: '/db-inspector', label: 'DB Inspector', icon: 'layers' },
    { href: '/feature-flags', label: 'Feature Flags', icon: 'flag' }
  ];

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
      <a class="nav-item" class:active={isActive(it.href)} href={it.href}>
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
        <small class="muted">Administrator</small>
      </span>
    </div>
    <button class="logout" onclick={doLogout} aria-label="Sign out"><Icon name="logout" size={18} /></button>
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
    display: flex; align-items: center; gap: 0.65rem; padding: 0.5rem 0.7rem;
    color: var(--ink-soft); border-radius: var(--radius); font-weight: 600; font-size: 0.92rem; position: relative;
  }
  .nav-item:hover { background: rgba(181, 134, 46, 0.08); text-decoration: none; color: var(--ink); }
  .marker { width: 6px; height: 6px; border-radius: 50%; background: var(--line-strong); transition: background 0.15s; }
  .nav-item.active { color: var(--ochre-deep); background: rgba(181, 134, 46, 0.12); }
  .nav-item.active .marker { background: var(--ochre); }
  .foot { border-top: 1px dashed var(--line-strong); padding-top: 0.8rem; display: flex; align-items: center; justify-content: space-between; }
  .who { display: flex; align-items: center; gap: 0.6rem; overflow: hidden; }
  .avatar { width: 34px; height: 34px; border-radius: 50%; background: var(--sage); color: #f3f6ee; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; flex-shrink: 0; }
  .meta { display: flex; flex-direction: column; line-height: 1.2; overflow: hidden; }
  .meta small { font-size: 0.7rem; }
  .logout { background: transparent; border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 0.35rem; cursor: pointer; color: var(--muted); display: inline-flex; }
  .logout:hover { color: var(--danger); border-color: var(--danger); }
</style>
