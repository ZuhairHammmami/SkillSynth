import { a7 as escape_html, a5 as store_get, a8 as unsubscribe_stores } from '../../chunks/index.js-DKBV1yhz.js';
import { p as page } from '../../chunks/stores.js-o9FwENuq.js';
import { I as Illustration } from '../../chunks/Illustration.js-BHiol4RS.js';
import { B as Button } from '../../chunks/Button.js-BZHPFJtc.js';
import '../../chunks/uneval.js-5Y6J9rDU.js';
import '../../chunks/exports.js-8HOoaa4e.js';
import '../../chunks/utils2.js-BQzn9ikS.js';
import '../../chunks/utils.js-DwNP_mEr.js';
import '../../chunks/root.js-Br7Q0GCE.js';
import '../../chunks/state.svelte.js-DHLV7VlX.js';

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

export { _error as default };
//# sourceMappingURL=_error.svelte.js-BjZSgynm.js.map
