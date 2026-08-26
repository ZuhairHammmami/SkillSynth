import { g as escape_html } from "../../chunks/index.js";
import { I as Illustration } from "../../chunks/Illustration.js";
import { B as Button } from "../../chunks/Button.js";
import { t } from "../../chunks/index3.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<header class="top container between svelte-1uha8ag"><a class="brand svelte-1uha8ag" href="/">Skill<em class="svelte-1uha8ag">Synth</em></a> <nav class="row"><a href="/login">Sign in</a> `);
    Button($$renderer2, {
      onclick: () => location.href = "/register",
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->Get started`);
      },
      $$slots: { default: true }
    });
    $$renderer2.push(`<!----></nav></header> <main class="hero container svelte-1uha8ag"><div class="copy"><span class="kicker svelte-1uha8ag">Adaptive Learning OS</span> <h1 class="svelte-1uha8ag">Grow skills that<br/><span class="accent svelte-1uha8ag">actually stick.</span></h1> <p class="lede svelte-1uha8ag">${escape_html(t("landing.subtitle"))}</p> <div class="row">`);
    Button($$renderer2, {
      onclick: () => location.href = "/register",
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->Start your path`);
      },
      $$slots: { default: true }
    });
    $$renderer2.push(`<!----> `);
    Button($$renderer2, {
      variant: "ghost",
      onclick: () => location.href = "/login",
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->I already have an account`);
      },
      $$slots: { default: true }
    });
    $$renderer2.push(`<!----></div></div> <div class="art svelte-1uha8ag">`);
    Illustration($$renderer2, { name: "hero", width: 380 });
    $$renderer2.push(`<!----></div></main>`);
  });
}
export {
  _page as default
};
