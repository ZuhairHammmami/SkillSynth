import '../../chunks/exports.js-8HOoaa4e.js';
import '../../chunks/utils2.js-BQzn9ikS.js';
import '../../chunks/utils.js-DwNP_mEr.js';
import '../../chunks/root.js-Br7Q0GCE.js';
import '../../chunks/state.svelte.js-DHLV7VlX.js';
import { B as Button } from '../../chunks/Button.js-BZHPFJtc.js';
import { a7 as escape_html, ae as attributes, ad as bind_props } from '../../chunks/index.js-DKBV1yhz.js';
import { I as Illustration } from '../../chunks/Illustration.js-BHiol4RS.js';
import '../../chunks/uneval.js-5Y6J9rDU.js';

function Input($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      label,
      value = "",
      type = "text",
      placeholder = "",
      error = "",
      $$slots,
      $$events,
      ...rest
    } = $$props;
    $$renderer2.push(`<label class="field svelte-138axrz">`);
    if (label) {
      $$renderer2.push("<!--[0-->");
      $$renderer2.push(`<span class="lbl svelte-138axrz">${escape_html(label)}</span>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--> <input${attributes({ class: "input", type, placeholder, value, error, ...rest }, "svelte-138axrz", void 0, void 0, 4)}/> `);
    if (error) {
      $$renderer2.push("<!--[0-->");
      $$renderer2.push(`<span class="err svelte-138axrz">${escape_html(error)}</span>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></label>`);
    bind_props($$props, { value });
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let email = "";
    let password = "";
    let loading = false;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="wrap svelte-1uha8ag"><div class="side svelte-1uha8ag">`);
      Illustration($$renderer3, { name: "hero", width: 320 });
      $$renderer3.push(`<!----> <h1 class="svelte-1uha8ag">SkillSynth Admin</h1> <p class="muted">Operational console for the Adaptive Learning OS.</p></div> <form class="card svelte-1uha8ag"><h2 class="svelte-1uha8ag">Sign in</h2> `);
      {
        $$renderer3.push("<!--[-1-->");
      }
      $$renderer3.push(`<!--]--> `);
      Input($$renderer3, {
        label: "Email",
        type: "email",
        placeholder: "admin@skillsynth.io",
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
        label: "Password",
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
          $$renderer4.push(`<!---->Sign in`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!----></form></div>`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
  });
}

export { _page as default };
//# sourceMappingURL=_page.svelte.js-Dbgwlgcw.js.map
