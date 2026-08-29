<!-- Searchable combobox. Replaces the plain native select with rich searchable picking. -->
<script module lang="ts">
  let _counter = 0;
</script>

<script lang="ts">
  import Icon from '$lib/icons/Icon.svelte';
  import { fade } from 'svelte/transition';
  import { onMount } from 'svelte';

  let {
    label = '',
    value = $bindable(),
    items = [],
    placeholder = '',
    hint = '',
    error = '',
    id = '',
    emptyText = '',
    clearLabel = '',
    ...rest
  }: any = $props();

  const uid = 'cb-' + ++_counter;
  const selId = $derived(id || uid);
  const errId = $derived(selId + '-err');
  const hintId = $derived(selId + '-hint');
  const listId = $derived(selId + '-list');

  let query = $state('');
  let open = $state(false);
  let active = $state(0);
  let root: HTMLElement | undefined = $state();
  let inputEl: HTMLInputElement | undefined = $state();
  let focusBeforePointer = false;

  const selectedItem = $derived(items.find((i: any) => i.value === value) ?? null);
  const display = $derived(query !== '' ? query : (selectedItem?.label ?? ''));
  const filtered = $derived(
    (() => {
      const q = query.trim().toLowerCase();
      if (!q) return items;
      return items.filter((i: any) =>
        (i.label + ' ' + (i.keywords ?? '') + ' ' + (i.chips ?? []).join(' '))
          .toLowerCase()
          .includes(q)
      );
    })()
  );
  const safeActive = $derived(filtered.length ? Math.min(active, filtered.length - 1) : 0);
  const activeOptId = $derived(open && filtered.length ? optId(filtered[safeActive]) : undefined);

  function optId(item: any) {
    return listId + '-opt-' + item.value;
  }

  $effect(() => {
    if (active > filtered.length - 1) active = Math.max(0, filtered.length - 1);
  });
  function select(item: any) {
    value = item.value;
    query = '';
    open = false;
    active = 0;
  }

  function onInput(e: Event) {
    query = (e.currentTarget as HTMLInputElement).value;
    open = true;
    active = 0;
  }

  function onFocus() {
    open = true;
    active = 0;
  }

  function onToggle() {
    if (!focusBeforePointer) return;
    if (open) {
      open = false;
      query = '';
    } else {
      open = true;
      active = 0;
    }
  }

  function onClear() {
    value = '';
    query = '';
    inputEl?.focus();
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!open) {
        open = true;
        active = 0;
      } else if (filtered.length) {
        active = (active + 1) % filtered.length;
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (!open) {
        open = true;
        active = filtered.length - 1;
      } else if (filtered.length) {
        active = (active - 1 + filtered.length) % filtered.length;
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (open && filtered.length) select(filtered[safeActive]);
      else if (!open) open = true;
    } else if (e.key === 'Escape') {
      open = false;
      query = '';
    } else if (e.key === 'Tab') {
      open = false;
    }
  }

  onMount(() => {
    function onDocDown(e: PointerEvent) {
      if (root && !root.contains(e.target as Node)) {
        open = false;
        query = '';
      }
    }
    document.addEventListener('pointerdown', onDocDown);
    return () => document.removeEventListener('pointerdown', onDocDown);
  });
</script>

<div class="wrap" bind:this={root}>
  <label class="field">
    {#if label}<span class="lbl">{label}</span>{/if}
    <div class="cbox" class:has-value={!!value}>
      <input class="sel" class:invalid={!!error} type="text" role="combobox"
        autocomplete="off" placeholder={placeholder} id={selId}
        aria-expanded={open} aria-haspopup="listbox" aria-controls={listId}
        aria-activedescendant={open ? activeOptId : undefined}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? errId : hint ? hintId : undefined}
        value={display} bind:this={inputEl} oninput={onInput} onfocus={onFocus}
        onpointerdown={() => { focusBeforePointer = inputEl === document.activeElement; }}
        onclick={onToggle} onkeydown={onKeydown} {...rest}
      />
      {#if value}
        <button class="clear" type="button" aria-label={clearLabel || 'clear selection'}
          onmousedown={(e) => e.preventDefault()} onclick={onClear}>
          <Icon name="x" size={18} />
        </button>
      {/if}
      <span class="chev" class:open={open}><Icon name="chevron" size={18} /></span>
    </div>
    {#if hint && !error}<span class="hint" id={hintId}>{hint}</span>{/if}
    {#if error}<span class="err" id={errId} role="alert">{error}</span>{/if}
  </label>
  {#if open}
    <ul id={listId} role="listbox" aria-expanded={open} class="list" transition:fade={{ duration: 120 }}>
      {#if filtered.length === 0}
        <li class="empty" role="option" aria-selected="false" aria-disabled="true">{emptyText}</li>
      {:else}
        {#each filtered as item, idx}
          <li class="opt" class:active={idx === safeActive} role="option"
            aria-selected={item.value === value} id={optId(item)}
            onmousedown={(e) => e.preventDefault()}
            onclick={(e) => { e.preventDefault(); select(item); }}
            onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(item); } }}
          >
            <div class="opt-top">
              <span class="opt-lbl">{item.label}</span>
              {#if item.badge}<span class="badge">{item.badge}</span>{/if}
            </div>
            {#if item.chips && item.chips.length}
              <span class="chips">
                {#each item.chips as chip}<span class="chip">{chip}</span>{/each}
              </span>
            {/if}
            {#if item.value === value}
              <span class="check"><Icon name="check" size={16} /></span>
            {/if}
          </li>
        {/each}
      {/if}
    </ul>
  {/if}
</div>

<style>
  .field, .wrap { display: block; position: relative; }
  .lbl { display: block; font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); margin-bottom: 0.35rem; }
  .cbox { position: relative; }
  .sel {
    width: 100%;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--ink);
    background: var(--card);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius);
    padding: 0.7rem 0.8rem;
    padding-inline-end: 2.75rem;
    min-height: 44px;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }
  .sel:focus { outline: none; border-color: var(--ring); box-shadow: 0 0 0 3px var(--focus-glow); }
  .sel.invalid { border-color: var(--danger); }
  .sel.invalid:focus { box-shadow: 0 0 0 3px var(--danger-soft); }
  .cbox.has-value .sel { padding-inline-end: 5.4rem; }
  .chev {
    position: absolute;
    inset-inline-end: 0.55rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--ink-soft);
    pointer-events: none;
    transition: transform 0.18s ease;
  }
  .cbox.has-value .chev { inset-inline-end: 3.05rem; }
  .chev.open { transform: translateY(-50%) rotate(180deg); }
  .clear {
    position: absolute;
    inset-inline-end: 0.1rem;
    top: 50%;
    transform: translateY(-50%);
    width: 44px;
    height: 44px;
    display: grid;
    place-items: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    color: var(--ink-soft);
    transition: color 0.18s ease, background 0.18s ease;
  }
  .clear:hover { color: var(--ink); background: var(--ochre-soft); }
  .list {
    position: absolute;
    top: calc(100% + 0.35rem);
    inset-inline: 0;
    margin: 0;
    padding: 0.3rem;
    list-style: none;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    max-height: 320px;
    overflow-y: auto;
    z-index: 60;
  }
  .opt {
    position: relative;
    min-height: 44px;
    padding: 0.45rem 0.7rem;
    padding-inline-end: 2.2rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.15rem;
    cursor: pointer;
    border-radius: var(--radius-sm);
  }
  .opt.active { background: var(--ochre-soft); }
  .opt-top { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
  .opt-lbl { color: var(--ink); font-weight: 600; }
  .badge,
  .chip { font-size: 0.72rem; border-radius: var(--radius-sm); padding: 0.1rem 0.45rem; }
  .badge {
    background: color-mix(in srgb, var(--clay) 14%, transparent);
    color: var(--ink-soft);
    white-space: nowrap;
  }
  .chip { background: var(--sage-soft); color: var(--sage-deep); }
  .chips { display: flex; flex-wrap: wrap; gap: 0.25rem; }
  .check {
    position: absolute;
    inset-inline-end: 0.6rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--ochre-deep);
  }
  .empty { padding: 0.5rem 0.7rem; color: var(--ink-soft); font-size: 0.9rem; }
  .hint,
  .err { display: block; font-size: 0.78rem; margin-top: 0.3rem; }
  .hint { color: var(--clay); }
  .err { color: var(--danger); }
</style>