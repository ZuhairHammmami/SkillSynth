import { j as attributes, h as stringify } from "./index.js";
function Button($$renderer, $$props) {
  let {
    variant = "primary",
    size = "md",
    type = "button",
    disabled = false,
    loading = false,
    onclick,
    children,
    $$slots,
    $$events,
    ...rest
  } = $$props;
  $$renderer.push(`<button${attributes(
    {
      class: `btn ${stringify(variant)} ${stringify(size)}`,
      type,
      disabled,
      ...rest
    },
    "svelte-1xko78n"
  )}>`);
  if (loading) {
    $$renderer.push("<!--[0-->");
    $$renderer.push(`<span class="spinner svelte-1xko78n" aria-hidden="true"></span>`);
  } else {
    $$renderer.push("<!--[-1-->");
  }
  $$renderer.push(`<!--]--> `);
  children($$renderer);
  $$renderer.push(`<!----></button>`);
}
export {
  Button as B
};
