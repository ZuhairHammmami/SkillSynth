import { g as escape_html, h as attributes, c as bind_props } from "./index.js";
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
export {
  Input as I
};
