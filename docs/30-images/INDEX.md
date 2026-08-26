# SS-EDS: Images

## Purpose
Document the image and icon strategy for SkillSynth. The surface is intentionally minimal: one SVG favicon per app, initials-based avatar fallbacks, and no raster asset pipeline.

## Responsibilities
- Serve src/frontend/public/favicon.svg (referenced in src/frontend/src/app/layout.tsx via `icons: { icon: '/favicon.svg' }`)
- Serve src/admin-app/public/favicon.ico for the admin origin
- Render avatar fallbacks as initials when no image URL exists
- Keep zero external image CDN dependencies

## Inputs
- favicon.svg (student app, inline SVG file)
- favicon.ico (admin app)
- User full_name (initials source for fallback rendering)

## Outputs
- Static files under each app's public/ directory
- Initials avatar markup rendered by shared UI components

## Dependencies
- 20-ui-system (component styling around images/avatars)
- 21-accessibility (alt text rules)
- 32-user-profile (full_name feeding the initials fallback)

## Asset Inventory
| App | File | Referenced by |
|-----|------|---------------|
| Student :3000 | src/frontend/public/favicon.svg | app/layout.tsx metadata.icons |
| Admin :3001 | src/admin-app/public/favicon.ico | Next.js default icon convention |

There is no custom icon component set; UI icons come from the installed component library (lucide-style strokes) used directly in components.

## Sequence: Favicon Resolution
```
Browser GET /favicon.svg → Next.js static handler → public/favicon.svg (cached)
Admin browser GET /favicon.ico → src/admin-app/public/favicon.ico
```

## Rules
1. Favicons are the only shipped image assets — no hero images, illustrations, or sprite sheets
2. Any future raster image must use next/image with explicit width/height
3. Alt text is mandatory for every informative image; decorative marks use aria-hidden
4. Avatars never store uploads — there is no avatar_url column on users
5. No external image domains are allowlisted in next.config

## Examples
- Avatar block: colored circle + first letters of full_name, deterministic color from user id
- Favicon swap: replace public/favicon.svg, no build change needed

## Edge Cases
- User with empty full_name → fallback shows a single neutral glyph, not an empty circle
- Browser requests /favicon.ico on :3000 → 404 is harmless (svg declared in metadata)

## Failure Cases
- favicon.svg deleted → browsers show default icon; layout.tsx still points to the path
- Broken remote image URL (none today — no remote images are rendered)

## Recovery Procedures
1. Restore favicon from git history: `git checkout HEAD -- src/frontend/public/favicon.svg`
2. Verify: `curl -I localhost:3000/favicon.svg` returns 200

## Refactoring Strategy
- If brand assets grow, introduce a single icons/ module with typed exports before adding files
- Revisit only when a real requirement appears; keep the asset surface flat
