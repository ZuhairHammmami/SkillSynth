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
    let email = "";
    let password = "";
    let loading = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<form class="card svelte-8k30lk"><h1 class="svelte-8k30lk">${escape_html(t("loginPage.title"))}</h1> <p class="muted">${escape_html(t("loginPage.subtitle"))}</p> `);
      {
        $$renderer3.push("<!--[-1-->");
      }
      $$renderer3.push(`<!--]--> `);
      Input($$renderer3, {
        label: t("loginForm.email"),
        type: "email",
        placeholder: "you@example.com",
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
        label: t("loginForm.password"),
        type: "password",
        placeholder: "••••••••",
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
          $$renderer4.push(`<!---->${escape_html(t("loginForm.submit"))}`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!----> <div class="links svelte-8k30lk"><a href="/forgot-password">${escape_html(t("loginPage.forgot"))}</a> <a href="/register">${escape_html(t("loginPage.noAccount"))}</a></div></form>`);
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
