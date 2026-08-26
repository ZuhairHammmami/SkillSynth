import { f as fallback, c as bind_props } from "./index.js";
function Logo($$renderer, $$props) {
  let compact = fallback($$props["compact"], false);
  $$renderer.push(`<a class="logo svelte-1l8nvlt" href="/" aria-label="SkillSynth home"><svg width="30" height="30" viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M16 28C9 28 5 23 5 16c0-5 4-9 11-9s11 4 11 9c0 7-4 12-11 12z" stroke="var(--ochre)" stroke-width="1.8"></path><path d="M16 27V13M16 18c-3-1-5-3-5-6M16 18c3-1 5-3 5-6" stroke="var(--sage-deep)" stroke-width="1.8" stroke-linecap="round"></path><circle cx="16" cy="9" r="2.2" fill="var(--ochre)"></circle></svg> `);
  if (!compact) {
    $$renderer.push("<!--[0-->");
    $$renderer.push(`<span class="word svelte-1l8nvlt">Skill<em class="svelte-1l8nvlt">Synth</em></span>`);
  } else {
    $$renderer.push("<!--[-1-->");
  }
  $$renderer.push(`<!--]--></a>`);
  bind_props($$props, { compact });
}
export {
  Logo as L
};
