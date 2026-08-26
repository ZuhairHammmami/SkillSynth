import { e as ensure_array_like, g as escape_html } from "../../../chunks/index.js";
import { t } from "../../../chunks/index3.js";
import { I as Illustration } from "../../../chunks/Illustration.js";
import { L as Logo } from "../../../chunks/Logo.js";
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { children } = $$props;
    const features = [
      "authLayout.feature1",
      "authLayout.feature2",
      "authLayout.feature3",
      "authLayout.feature4"
    ];
    $$renderer2.push(`<div class="split svelte-5bky5h"><div class="panel-side svelte-5bky5h">`);
    Logo($$renderer2, {});
    $$renderer2.push(`<!----> `);
    Illustration($$renderer2, { name: "path", width: 300 });
    $$renderer2.push(`<!----> <ul class="features svelte-5bky5h"><!--[-->`);
    const each_array = ensure_array_like(features);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let f = each_array[$$index];
      $$renderer2.push(`<li class="svelte-5bky5h">${escape_html(t(f))}</li>`);
    }
    $$renderer2.push(`<!--]--></ul></div> <div class="panel-form svelte-5bky5h">`);
    children($$renderer2);
    $$renderer2.push(`<!----></div></div>`);
  });
}
export {
  _layout as default
};
