import { g as escape_html, s as store_get, u as unsubscribe_stores } from "../../chunks/index.js";
import { p as page } from "../../chunks/stores.js";
import { I as Illustration } from "../../chunks/Illustration.js";
import { B as Button } from "../../chunks/Button.js";
function _error($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    $$renderer2.push(`<div class="wrap svelte-1j96wlh">`);
    Illustration($$renderer2, { name: "sprout", width: 140 });
    $$renderer2.push(`<!----> <h1 class="svelte-1j96wlh">${escape_html(store_get($$store_subs ??= {}, "$page", page).status)}</h1> <p class="muted">${escape_html(store_get($$store_subs ??= {}, "$page", page).error?.message || "Something went off the path.")}</p> `);
    Button($$renderer2, {
      onclick: () => history.back(),
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->Go back`);
      },
      $$slots: { default: true }
    });
    $$renderer2.push(`<!----></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _error as default
};
