import { g as escape_html } from "../../../../chunks/index.js";
import { B as Button } from "../../../../chunks/Button.js";
import { I as Input } from "../../../../chunks/Input.js";
import { t } from "../../../../chunks/index3.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let email = "";
    let loading = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<form class="card svelte-1xufxwe"><h1 class="svelte-1xufxwe">${escape_html(t("forgotPasswordPage.title"))}</h1> <p class="muted">${escape_html(t("forgotPasswordPage.subtitle"))}</p> `);
      Input($$renderer3, {
        label: t("forgotPasswordForm.email"),
        type: "email",
        required: true,
        get value() {
          return email;
        },
        set value($$value) {
          email = $$value;
          $$settled = false;
        }
      });
      $$renderer3.push(`<!----> `);
      Button($$renderer3, {
        type: "submit",
        loading,
        disabled: !email,
        children: ($$renderer4) => {
          $$renderer4.push(`<!---->${escape_html(t("forgotPasswordForm.submit"))}`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!----> `);
      {
        $$renderer3.push("<!--[-1-->");
      }
      $$renderer3.push(`<!--]--> <div class="links svelte-1xufxwe"><a href="/login">${escape_html(t("forgotPasswordPage.back"))}</a></div></form>`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
  });
}
export {
  _page as default
};
