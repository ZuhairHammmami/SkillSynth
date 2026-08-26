import { a5 as store_get, a8 as unsubscribe_stores, a4 as ensure_array_like, a6 as attr_class, ac as attr, a7 as escape_html, ab as fallback, ad as bind_props } from '../../../chunks/index.js-DKBV1yhz.js';
import { w as writable } from '../../../chunks/index2.js-DOfo_N45.js';
import '../../../chunks/exports.js-8HOoaa4e.js';
import '../../../chunks/utils2.js-BQzn9ikS.js';
import '../../../chunks/utils.js-DwNP_mEr.js';
import '../../../chunks/root.js-Br7Q0GCE.js';
import '../../../chunks/state.svelte.js-DHLV7VlX.js';
import { p as page } from '../../../chunks/stores.js-o9FwENuq.js';
import '../../../chunks/uneval.js-5Y6J9rDU.js';

function getInitials(name, email) {
  const src = (name || email || "?").trim();
  const parts = src.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return src.slice(0, 2).toUpperCase();
}
const authStore = writable({
  user: null,
  loading: false,
  initialized: false
});
function Icon($$renderer, $$props) {
  let name = $$props["name"];
  let size = fallback($$props["size"], 20);
  let stroke = fallback($$props["stroke"], 1.6);
  const paths = {
    dashboard: "M3 3h7v8H3zM14 3h7v5h-7zM14 11h7v10h-7zM3 13h7v8H3z",
    learn: "M4 5.5A2 2 0 0 1 6 4h9a2 2 0 0 1 2 2v11a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2zM6 4v14",
    analytics: "M4 20V10M10 20V4M16 20v-7M22 20H2",
    profile: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
    settings: "M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM4 12l1.5-1 1 2-1.5 1M20 12l-1.5-1-1 2 1.5 1M12 4l-1 1.5 2 1 1-1.5M12 20l-1-1.5 2-1 1 1.5",
    plus: "M12 5v14M5 12h14",
    trash: "M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13",
    edit: "M4 20l4-1 11-11-3-3L5 16zM14 6l3 3",
    check: "M5 12l5 5L20 6",
    chevron: "M9 6l6 6-6 6",
    globe: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18",
    logout: "M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4M10 12H3M6 8l-4 4 4 4",
    sparkles: "M12 4l1.6 4.4L18 10l-4.4 1.6L12 16l-1.6-4.4L6 10l4.4-1.6zM18 15l.8 2.2L21 18l-2.2.8L18 21l-.8-2.2L15 18l2.2-.8z",
    search: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4",
    menu: "M4 7h16M4 12h16M4 17h16",
    x: "M6 6l12 12M18 6L6 18",
    download: "M12 4v10M8 11l4 3 4-3M5 20h14",
    alert: "M12 4l9 16H3zM12 10v5M12 17.5v.5",
    key: "M14 7a4 4 0 1 0-3.5 6.9L5 20v-3l1-1 2 2 1-1-2-2h3l3.5-3.5A4 4 0 0 0 14 7z",
    shield: "M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z",
    database: "M12 3c4 0 7 1 7 3s-3 3-7 3-7-1-7-3 3-3 7-3zM5 6v6c0 2 3 3 7 3s7-1 7-3V6M5 12v6c0 2 3 3 7 3s7-1 7-3v-6",
    activity: "M3 12h4l3-8 4 16 3-8h4",
    refresh: "M20 11a8 8 0 0 0-14-4M4 5v3h3M4 13a8 8 0 0 0 14 4M20 19v-3h-3",
    layers: "M12 3l9 5-9 5-9-5zM3 13l9 5 9-5",
    flag: "M5 21V4h12l-2 4 2 4H5",
    calendar: "M4 7a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM4 10h16M8 4v4M16 4v4",
    arrow: "M5 12h14M13 6l6 6-6 6",
    users: "M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM3 20a6 6 0 0 1 12 0M16 11a3 3 0 0 0 0-6M15 14a6 6 0 0 1 6 6",
    category: "M4 5h7v7H4zM13 5h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z",
    resource: "M4 5h16v14H4zM8 9h8M8 13h8M8 17h5",
    role: "M12 3v4M8 7h8M6 21v-7a6 6 0 0 1 12 0v7",
    quiz: "M9 9a3 3 0 1 1 4 2.8L9 16M9 16h.01M14 14h.01",
    brain: "M9 4a3 3 0 0 0-3 3 3 3 0 0 0-1 5 3 3 0 0 0 2 4 3 3 0 0 0 5 1V4a3 3 0 0 0-3 0zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 1 5 3 3 0 0 1-2 4 3 3 0 0 1-5 1",
    book: "M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 0-3 3zM5 4v16",
    trending: "M3 17l6-6 4 4 8-8M21 7h-5M21 7v5",
    clock: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l4 2",
    mail: "M3 6h18v12H3zM3 7l9 6 9-6",
    home: "M4 11l8-7 8 7M6 10v9h12v-9"
  };
  $$renderer.push(`<svg xmlns="http://www.w3.org/2000/svg"${attr("width", size)}${attr("height", size)} viewBox="0 0 24 24" fill="none" stroke="currentColor"${attr("stroke-width", stroke)} stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path${attr("d", paths[name] ?? paths.arrow)}></path></svg>`);
  bind_props($$props, { name, size, stroke });
}
function Logo($$renderer, $$props) {
  let compact = fallback($$props["compact"], false);
  $$renderer.push(`<a class="logo svelte-1l8nvlt" href="/" aria-label="SkillSynth home"><svg width="30" height="30" viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M16 28C9 28 5 23 5 16c0-5 4-9 11-9s11 4 11 9c0 7-4 12-11 12z" stroke="var(--ochre)" stroke-width="1.8"></path><path d="M16 27V13M16 18c-3-1-5-3-5-6M16 18c3-1 5-3 5-6" stroke="var(--sage-deep)" stroke-width="1.8" stroke-linecap="round"></path><circle cx="16" cy="9" r="2.2" fill="var(--ochre)"></circle></svg> `);
  if (!compact) {
    $$renderer.push("<!--[0-->");
    $$renderer.push(`<span class="word svelte-1l8nvlt">Skill<em class="svelte-1l8nvlt">Synth</em></span>`);
  } else {
    $$renderer.push("<!--[-1-->");
  }
  $$renderer.push(`<!--]--></a>`);
  bind_props($$props, { compact });
}
function NavRail($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const items = [
      { href: "/dashboard", label: "Dashboard", icon: "dashboard" },
      { href: "/users", label: "Users", icon: "users" },
      { href: "/categories", label: "Categories", icon: "category" },
      { href: "/skills", label: "Skills", icon: "learn" },
      { href: "/resources", label: "Resources", icon: "resource" },
      { href: "/job-roles", label: "Job Roles", icon: "role" },
      { href: "/assessments", label: "Assessments", icon: "quiz" },
      { href: "/paths", label: "Paths", icon: "path" },
      { href: "/reports", label: "Reports", icon: "analytics" },
      { href: "/health", label: "System Health", icon: "shield" },
      { href: "/settings", label: "Settings", icon: "settings" },
      { href: "/audit-logs", label: "Audit Logs", icon: "activity" },
      { href: "/backups", label: "Backups", icon: "database" },
      { href: "/db-inspector", label: "DB Inspector", icon: "layers" },
      { href: "/feature-flags", label: "Feature Flags", icon: "flag" }
    ];
    function isActive(href) {
      const p = store_get($$store_subs ??= {}, "$page", page).url.pathname;
      return p === href || p.startsWith(href + "/");
    }
    $$renderer2.push(`<aside class="rail svelte-6uojg9"><div class="brand svelte-6uojg9">`);
    Logo($$renderer2, {});
    $$renderer2.push(`<!----></div> <nav class="nav svelte-6uojg9"><!--[-->`);
    const each_array = ensure_array_like(items);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let it = each_array[$$index];
      $$renderer2.push(`<a${attr_class("nav-item svelte-6uojg9", void 0, { "active": isActive(it.href) })}${attr("href", it.href)}><span class="marker svelte-6uojg9"></span> `);
      Icon($$renderer2, { name: it.icon, size: 18 });
      $$renderer2.push(`<!----> <span>${escape_html(it.label)}</span></a>`);
    }
    $$renderer2.push(`<!--]--></nav> <div class="foot svelte-6uojg9"><div class="who svelte-6uojg9"><span class="avatar svelte-6uojg9">${escape_html(getInitials(store_get($$store_subs ??= {}, "$authStore", authStore).user?.full_name, store_get($$store_subs ??= {}, "$authStore", authStore).user?.email))}</span> <span class="meta svelte-6uojg9"><strong>${escape_html(store_get($$store_subs ??= {}, "$authStore", authStore).user?.full_name || store_get($$store_subs ??= {}, "$authStore", authStore).user?.email)}</strong> <small class="muted svelte-6uojg9">Administrator</small></span></div> <button class="logout svelte-6uojg9" aria-label="Sign out">`);
    Icon($$renderer2, { name: "logout", size: 18 });
    $$renderer2.push(`<!----></button></div></aside>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { children } = $$props;
    if (store_get($$store_subs ??= {}, "$authStore", authStore).user) {
      $$renderer2.push("<!--[0-->");
      $$renderer2.push(`<div class="shell svelte-1v2axqk">`);
      NavRail($$renderer2);
      $$renderer2.push(`<!----> <main class="content svelte-1v2axqk"><div class="container pad svelte-1v2axqk">`);
      children($$renderer2);
      $$renderer2.push(`<!----></div></main></div>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}

export { _layout as default };
//# sourceMappingURL=_layout.svelte.js-zJ9ugdWa.js.map
