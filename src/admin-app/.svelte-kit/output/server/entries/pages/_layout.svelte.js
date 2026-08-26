import { e as ensure_array_like, s as store_get, c as attr_class, h as stringify, d as escape_html, u as unsubscribe_stores } from "../../chunks/index.js";
import { w as writable } from "../../chunks/index2.js";
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
export {
  _layout as default
};
