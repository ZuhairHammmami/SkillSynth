import { g as escape_html } from "../../../../chunks/index.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils2.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/root.js";
import "../../../../chunks/state.svelte.js";
import { B as Button } from "../../../../chunks/Button.js";
import { I as Input } from "../../../../chunks/Input.js";
import { t } from "../../../../chunks/index3.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let fullName = "";
    let email = "";
    let password = "";
    let loading = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<form class="card svelte-ydeots"><h1 class="svelte-ydeots">${escape_html(t("registerPage.title"))}</h1> <p class="muted">${escape_html(t("registerPage.subtitle"))}</p> `);
      Input($$renderer3, {
        label: t("registerForm.name"),
        placeholder: t("registerForm.namePlaceholder"),
        get value() {
          return fullName;
        },
        set value($$value) {
          fullName = $$value;
          $$settled = false;
        }
      });
      $$renderer3.push(`<!----> `);
      Input($$renderer3, {
        label: t("registerForm.email"),
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
      Input($$renderer3, {
        label: t("registerForm.password"),
        type: "password",
        required: true,
        get value() {
          return password;
        },
        set value($$value) {
          password = $$value;
          $$settled = false;
        }
      });
      $$renderer3.push(`<!----> `);
      Button($$renderer3, {
        type: "submit",
        loading,
        disabled: !email || !password,
        children: ($$renderer4) => {
          $$renderer4.push(`<!---->${escape_html(t("registerForm.submit"))}`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!----> <div class="links svelte-ydeots"><a href="/login">${escape_html(t("registerPage.hasAccount"))}</a></div></form>`);
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
