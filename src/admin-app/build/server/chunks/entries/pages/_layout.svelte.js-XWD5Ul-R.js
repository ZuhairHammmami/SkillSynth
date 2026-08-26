import { a4 as ensure_array_like, a5 as store_get, a6 as attr_class, a7 as escape_html, a8 as unsubscribe_stores, a9 as stringify } from '../../chunks/index.js-DKBV1yhz.js';
import { w as writable } from '../../chunks/index2.js-DOfo_N45.js';
import '../../chunks/uneval.js-5Y6J9rDU.js';

const toasts = writable([]);
function Toaster($$renderer) {
  var $$store_subs;
  $$renderer.push(`<div class="toaster svelte-1dnmrtz" aria-live="polite"><!--[-->`);
  const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$toasts", toasts));
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let t = each_array[$$index];
    $$renderer.push(`<div${attr_class(`toast ${stringify(t.type)}`, "svelte-1dnmrtz")}>${escape_html(t.message)}</div>`);
  }
  $$renderer.push(`<!--]--></div>`);
  if ($$store_subs) unsubscribe_stores($$store_subs);
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { children } = $$props;
    children($$renderer2);
    $$renderer2.push(`<!----> `);
    Toaster($$renderer2);
    $$renderer2.push(`<!---->`);
  });
}

export { _layout as default };
//# sourceMappingURL=_layout.svelte.js-XWD5Ul-R.js.map
