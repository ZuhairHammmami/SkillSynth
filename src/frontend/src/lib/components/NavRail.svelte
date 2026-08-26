<!-- Warm "contents rail" sidebar. Replaces the icon-rail SaaS nav with a
     crafted list + tiny plant markers and active-state underline. -->
<script lang="ts">
  import { page } from '$app/stores';
  import { authStore, logout } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Icon from '$lib/icons/Icon.svelte';
  import Logo from '$lib/components/Logo.svelte';
  import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
  import { getInitials } from '$lib/util';

  const items = [
    { href: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { href: '/learn', label: 'My Paths', icon: 'learn' },
    { href: '/analytics', label: 'Analytics', icon: 'analytics' },
    { href: '/profile', label: 'Profile', icon: 'profile' },
    { href: '/settings', label: 'Settings', icon: 'settings' }
  ];

  function isActive(href: string): boolean {
    const p = $page.url.pathname;
    if (href === '/dashboard') return p === '/dashboard';
    return p === href || p.startsWith(href + '/');
  }
  async function doLogout() {
    logout();
    await goto('/login');
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
        <small class="muted">{$authStore.user?.email}</small>
      </span>
    </div>
    <div class="actions">
      <LocaleSwitcher />
      <button class="logout" onclick={doLogout} aria-label="Sign out"><Icon name="logout" size={18} /></button>
    </div>
  </div>
</aside>

<style>
  .rail {
    width: var(--rail-w); flex-shrink: 0; height: 100vh; position: sticky; top: 0;
    background: var(--paper-2); border-inline-end: 1px solid var(--line);
    display: flex; flex-direction: column; padding: 1.2rem 0.9rem;
  }
  .brand { padding: 0.3rem 0.5rem 1.2rem; }
  .nav { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; }
  .nav-item {
    display: flex; align-items: center; gap: 0.65rem; padding: 0.6rem 0.7rem;
    color: var(--ink-soft); border-radius: var(--radius); font-weight: 600; position: relative;
  }
  .nav-item:hover { background: rgba(181, 134, 46, 0.08); text-decoration: none; color: var(--ink); }
  .marker { width: 6px; height: 6px; border-radius: 50%; background: var(--line-strong); transition: background 0.15s; }
  .nav-item.active { color: var(--ochre-deep); background: rgba(181, 134, 46, 0.12); }
  .nav-item.active .marker { background: var(--ochre); }
  .foot { border-top: 1px dashed var(--line-strong); padding-top: 0.9rem; display: flex; flex-direction: column; gap: 0.7rem; }
  .who { display: flex; align-items: center; gap: 0.6rem; }
  .avatar { width: 34px; height: 34px; border-radius: 50%; background: var(--sage); color: #f3f6ee; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; }
  .meta { display: flex; flex-direction: column; line-height: 1.2; overflow: hidden; }
  .meta small { font-size: 0.72rem; }
  .actions { display: flex; align-items: center; justify-content: space-between; }
  .logout { background: transparent; border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 0.35rem; cursor: pointer; color: var(--muted); display: inline-flex; }
  .logout:hover { color: var(--danger); border-color: var(--danger); }
</style>
