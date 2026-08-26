import { a7 as escape_html } from '../../../../chunks/index.js-DKBV1yhz.js';
import { I as Illustration } from '../../../../chunks/Illustration.js-BHiol4RS.js';
import '../../../../chunks/uneval.js-5Y6J9rDU.js';

function Panel($$renderer, $$props) {
  let { title, subtitle, children, footer } = $$props;
  $$renderer.push(`<section class="panel svelte-1q2ixex">`);
  if (title || subtitle) {
    $$renderer.push("<!--[0-->");
    $$renderer.push(`<header class="panel-head svelte-1q2ixex">`);
    if (title) {
      $$renderer.push("<!--[0-->");
      $$renderer.push(`<h3 class="svelte-1q2ixex">${escape_html(title)}</h3>`);
    } else {
      $$renderer.push("<!--[-1-->");
    }
    $$renderer.push(`<!--]--> `);
    if (subtitle) {
      $$renderer.push("<!--[0-->");
      $$renderer.push(`<p class="muted svelte-1q2ixex">${escape_html(subtitle)}</p>`);
    } else {
      $$renderer.push("<!--[-1-->");
    }
    $$renderer.push(`<!--]--></header>`);
  } else {
    $$renderer.push("<!--[-1-->");
  }
  $$renderer.push(`<!--]--> <div class="panel-body">`);
  children($$renderer);
  $$renderer.push(`<!----></div> `);
  if (footer) {
    $$renderer.push("<!--[0-->");
    $$renderer.push(`<footer class="panel-foot svelte-1q2ixex">`);
    footer($$renderer);
    $$renderer.push(`<!----></footer>`);
  } else {
    $$renderer.push("<!--[-1-->");
  }
  $$renderer.push(`<!--]--></section>`);
}
function _page($$renderer) {
  $$renderer.push(`<h1>Dashboard</h1> <div class="grid svelte-1tyszyy">`);
  Panel($$renderer, {
    title: "Platform overview",
    children: ($$renderer2) => {
      Illustration($$renderer2, { name: "path", width: 160 });
    }
  });
  $$renderer.push(`<!----> `);
  Panel($$renderer, {
    title: "Recent activity",
    children: ($$renderer2) => {
      $$renderer2.push(`<p class="muted">Loading console…</p>`);
    }
  });
  $$renderer.push(`<!----></div>`);
}

export { _page as default };
//# sourceMappingURL=_page.svelte.js-DvfZcip7.js.map
