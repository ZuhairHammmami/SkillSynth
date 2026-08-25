# SS-EDS: Images

## Purpose
Document the image handling strategy for SkillSynth, including icon SVGs, avatar management, image optimization with Next.js, and WebP conversion.

## Responsibilities
- Maintain custom icon SVG set (25 synth-themed icons)
- Manage user avatar display and defaults
- Configure Next.js image optimization
- Ensure all images meet performance and accessibility standards

## Inputs
- UI design specifications
- Icon requirements (25 custom icons from DESIGN_SYSTEM.md)
- Avatar requirements

## Outputs
- SVG icon components
- Avatar components
- Image optimization configuration

## Dependencies
- 20-ui-system (icon catalog, design specs)
- 08-frontend (next.config.js, Image component)
- 21-accessibility (alt text, aria labels)

## Icon Catalog (25 Custom Icons)
All icons: 24×24px viewBox, 2px stroke width, round linecap/join, fill="none", color inherits from currentColor.
| Icon | Name | Purpose |
|------|------|---------|
| 1 | jack-in | Audio plug entering port |
| 2 | jack-out | Audio plug exiting port |
| 3 | knob | Rotary knob top-view |
| 4-6 | wave-* | Sine/square/saw waves |
| 7 | patch-cable | Patching cable |
| 8 | module | Eurorack faceplate |
| 9 | rack | 3U equipment rack |
| 10-11 | led-* | LED states |
| 12-24 | Various | Spectrum, oscilloscope, filter, etc. |
| 25 | attenuator | Level adjust |

## Logo SVG (36×36)
```
<svg viewBox="0 0 36 36">
  <path d="M2 26 C 2 10, 9 10, 9 10 C 9 10, 14 10, 18 18 C 22 26, 27 26, 27 26"
        fill="none" stroke="#D4A843" stroke-width="2" stroke-linecap="round"/>
  <circle cx="27" cy="26" r="4" fill="#0B0B0D" stroke="#D4A843" stroke-width="1.5"/>
</svg>
```

## ERD References
- profiles: avatar URL (stored as string, not BLOB)

## Rules
1. All icons are inline SVGs (no external sprite sheets)
2. Images use next/Image for optimization
3. WebP format preferred, AVIF as future option
4. All images must have alt text
5. Avatar defaults to initials on missing image
6. No external image CDN dependency

## Examples
- Avatar component: shows image or initials in 32px circle
- Icon component: `<JackInIcon className="w-6 h-6" />`

## Edge Cases
- Avatar URL broken → show initials fallback
- SVG doesn't render in old browser → static PNG fallback
- Image optimization fails during build → skip optimization

## Failure Cases
- Large unoptimized images slow down page load
- Missing alt text → accessibility violation
- SVG stroke-width doesn't scale → use vector-effect="non-scaling-stroke"

## Recovery Procedures
1. Verify next.config.js image domains configuration
2. Check image optimization settings for production build
3. Replace raster images with SVG where possible

## Refactoring Strategy
- Create a single `icons/` directory with all 25 SVGs as React components
- Add image compression pipeline for user uploads
- Implement lazy loading for off-screen images
