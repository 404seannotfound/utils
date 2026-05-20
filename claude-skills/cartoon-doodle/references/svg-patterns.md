# SVG Patterns — hand-jittered linework for living documents

Everything Sean draws as SVG (Gantt charts, hero strips, banners, charm pictographs, marginalia) shares the same set of patterns. This file is the cheat sheet — copy what you need.

## The three roughness filters

These go in `<defs>`. Every meaningful path applies one of them.

```xml
<filter id="rough" x="-2%" y="-2%" width="104%" height="104%">
  <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="11"/>
  <feDisplacementMap in="SourceGraphic" scale="1.6"/>
</filter>
<filter id="roughBig" x="-2%" y="-2%" width="104%" height="104%">
  <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="2" seed="9"/>
  <feDisplacementMap in="SourceGraphic" scale="2.6"/>
</filter>
<filter id="roughTiny" x="-2%" y="-2%" width="104%" height="104%">
  <feTurbulence type="fractalNoise" baseFrequency="0.08" numOctaves="2" seed="3"/>
  <feDisplacementMap in="SourceGraphic" scale="0.8"/>
</filter>
```

- **`#rough`** — default. Use on most strokes/fills.
- **`#roughBig`** — outer frame, page borders, big block strokes. More jitter so the frame feels hand-drawn even at thick weights.
- **`#roughTiny`** — small charms, tiny labels, subtle marginalia. Light touch so charms remain readable at small sizes.

Apply with `filter="url(#rough)"` on the element or a wrapping `<g>`. Vary the `seed` between filters so each filter draws its own jitter — copying the same filter with the same seed makes everything jitter in lockstep, which looks unnatural.

## The cream paper pattern

```xml
<pattern id="paper" width="6" height="6" patternUnits="userSpaceOnUse">
  <rect width="6" height="6" fill="#FBF5E4"/>
  <circle cx="1" cy="3" r="0.35" fill="#C0B27A" opacity="0.35"/>
  <circle cx="4" cy="1.5" r="0.25" fill="#A89456" opacity="0.3"/>
  <circle cx="3" cy="5" r="0.3"  fill="#C0B27A" opacity="0.25"/>
</pattern>
```

Then for the page background:

```xml
<rect width="100%" height="100%" fill="url(#paper)"/>
```

The dots are barely visible up close and give the cream paper a faintly speckled feel at any zoom level. **Do not** skip this — a plain `#FBF5E4` background reads too clean for the style.

## The double frame

Hand-drawn frames are *two* lines, slightly offset, both jittered:

```xml
<rect x="6" y="6" width="{W-12}" height="{H-12}" fill="none"
      stroke="#1A1A1A" stroke-width="2.6" filter="url(#roughBig)"/>
<rect x="11" y="11" width="{W-22}" height="{H-22}" fill="none"
      stroke="#1A1A1A" stroke-width="1" opacity="0.45" filter="url(#rough)"/>
```

The outer line is the "real" frame; the inner is a thin ghost. Both jittered, slightly different opacities — your eye reads it as one hand-drawn pen stroke that didn't go down evenly.

## Labeled `<g>` charm groups — the augmentable pattern

**Every meaningful unit gets its own `<g>` group with a comment header.** This is the entire reason SVGs are the "living document" half of the system.

```xml
<!-- charm: PIN keypad · #73 PIN 2FA -->
<g transform="translate(681, 188)" filter="url(#roughTiny)">
  <rect x="-4" y="-3" width="8" height="6" fill="#FBF5E4" stroke="#1A1A1A" stroke-width="0.8"/>
  <circle cx="-2" cy="-1" r="0.6" fill="#1A1A1A"/>
  <circle cx="0"  cy="-1" r="0.6" fill="#1A1A1A"/>
  <circle cx="2"  cy="-1" r="0.6" fill="#1A1A1A"/>
  <circle cx="-2" cy="1.4" r="0.6" fill="#1A1A1A"/>
  <text x="0" y="9" font-size="6.5" text-anchor="middle" fill="#6C6033">#73 PIN 2FA</text>
</g>
```

Why the comment header matters: when Sean (or you, in a future session) opens this SVG to add a new charm, you scan for `<!-- charm:` lines, find the closest sibling, copy it, and edit. **Nothing gets redrawn.** The chart grows by accretion.

Also note the `transform="translate(x, y)"` pattern — coordinates inside the group are *relative* to the group's translate. Move the whole charm by changing the translate; never touch the inner coordinates unless you're redesigning the charm.

## Gantt time-axis math

For a Gantt chart, pick an origin x and a px-per-day rate, then derive every date's x position from that. Put the math in a comment block at the top so future-you can verify dates without recomputing.

```xml
<!-- Time scale (locked):
     Mar 4 (origin) = x=130, then 9 px / day.
     Key dates:
       Mar 4  =130   Mar 5  =139   Mar 10 =184
       Mar 23 =301   Apr 1  =382   Apr 28 =625
       May 5  =688   May 12 =751 (TODAY)
       May 21 =832 (EVENT)   May 25 =868
       Jun 1  =931
-->
```

For a 90-day timeline at 9 px/day, that's an 820 px plot area. Tune the rate to fit your viewBox width. Always include a "today" line:

```xml
<!-- TODAY vertical line -->
<path d="M {TODAY_X} 80 Q {TODAY_X-2} 200 {TODAY_X+1} 290 Q {TODAY_X-1} 360 {TODAY_X} 460"
      stroke="#C04D3A" stroke-width="2.4" fill="none" filter="url(#rough)"/>
<!-- YOU ARE HERE pennant -->
<g transform="translate({TODAY_X}, 70)" filter="url(#rough)">
  <polygon points="-30,-12 30,-12 30,2 4,2 0,8 -4,2 -30,2"
           fill="#F5C84B" stroke="#1A1A1A" stroke-width="1.6"/>
  <text x="0" y="-2" font-size="9" font-weight="900" fill="#C04D3A" text-anchor="middle">YOU ARE HERE</text>
</g>
```

The pennant is a flag shape with a notch at the bottom — the visual cliché that says "you are here on the map." Position it just above the timeline, with the path of the today-line jittering downward through every row.

## Solid bars vs dashed bars

This is load-bearing visual grammar. **Past events = solid. Future events = dashed.**

```xml
<!-- past: solid bar -->
<rect x="{X}" y="{Y}" width="{W}" height="20" fill="#C04D3A"
      stroke="#1A1A1A" stroke-width="2" filter="url(#rough)"/>

<!-- future: dashed bar, cream fill -->
<rect x="{X}" y="{Y}" width="{W}" height="20" fill="#FBF5E4"
      stroke="#1A1A1A" stroke-width="2" stroke-dasharray="5,4" filter="url(#rough)"/>
```

When a future event happens, the dashes go solid. That's the whole gimmick of a living Gantt.

## The EVENT-stage block (a dashed destination)

For a Gantt that ends at a major event (a launch, a release, a literal festival), render the destination as a *stage* — taller than other rows, with sky + sand gradients, illustrated with charms. Sean did this for SOAK*2026 at Justesen Ranch:

```xml
<linearGradient id="desert" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0"   stop-color="#F5D58A"/>
  <stop offset="0.55" stop-color="#E5B266"/>
  <stop offset="1"   stop-color="#C58341"/>
</linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#B7D6EF"/>
  <stop offset="1" stop-color="#F5E0C0"/>
</linearGradient>

<!-- EVENT stage block: sky band -->
<rect x="{X}" y="{Y}" width="{W}" height="32" fill="url(#sky)"
      stroke="#1A1A1A" stroke-width="2" filter="url(#rough)"/>
<!-- sand band -->
<rect x="{X}" y="{Y+32}" width="{W}" height="36" fill="url(#desert)"
      stroke="#1A1A1A" stroke-width="2" filter="url(#rough)"/>
<!-- dashed RED border indicating "future stage" -->
<rect x="{X-2}" y="{Y-2}" width="{W+4}" height="72" fill="none"
      stroke="#C04D3A" stroke-width="2.4" stroke-dasharray="6,4" filter="url(#roughBig)"/>
<!-- ribbon-banner with event name across the top of the stage -->
```

Then drop tent / campfire / radio-tower charms inside. The whole block reads as the *destination* of the timeline.

## The charm vocabulary

Sean's Gantt charts are dense with small icon-charms. Each charm is a labeled `<g>` group, ~20–40 px wide, with `filter="url(#roughTiny)"` so the linework stays readable at small sizes. Reuse charm patterns wherever they fit.

Here are the recurring ones:

### SQLite cylinder

```xml
<g filter="url(#roughTiny)">
  <ellipse cx="0" cy="-2" rx="5" ry="1.7" fill="#FBF5E4" stroke="#1A1A1A" stroke-width="0.9"/>
  <path d="M -5,-2 L -5,3 Q -5,4.7 0,4.7 Q 5,4.7 5,3 L 5,-2" fill="#FBF5E4" stroke="#1A1A1A" stroke-width="0.9"/>
  <ellipse cx="0" cy="1" rx="5" ry="1.7" fill="none" stroke="#1A1A1A" stroke-width="0.6" opacity="0.6"/>
</g>
```

### Flask flask (the Python framework, drawn as a chemistry flask)

```xml
<g filter="url(#roughTiny)">
  <path d="M -4,-6 L -4,-2 L -8,8 L 8,8 L 4,-2 L 4,-6 Z" fill="#FBF5E4" stroke="#1A1A1A" stroke-width="1.2"/>
  <path d="M -5,0 L 5,0" stroke="#1A1A1A" stroke-width="0.7"/>
  <path d="M -6,3 L 6,3" stroke="#C04D3A" stroke-width="1" opacity="0.6"/>
  <rect x="-2" y="-9" width="4" height="3" fill="#1A1A1A"/>
</g>
```

### PIN keypad (4 dots in a 2x2 grid inside a small rect)

See the labeled-group example above.

### Tier chips (rounded rectangles, layered)

```xml
<g filter="url(#roughTiny)">
  <rect x="-2" y="-2" width="4" height="3" rx="1.5" fill="#F5C84B" stroke="#1A1A1A" stroke-width="0.6"/>
  <rect x="2" y="-1" width="4" height="3" rx="1.5" fill="#C04D3A" stroke="#1A1A1A" stroke-width="0.6"/>
  <rect x="0" y="2" width="4" height="3" rx="1.5" fill="#2D7A45" stroke="#1A1A1A" stroke-width="0.6"/>
</g>
```

### Megaphone (escalation)

```xml
<g filter="url(#roughTiny)">
  <path d="M -4,-2 L 3,-4 L 3,4 L -4,2 Z" fill="#C04D3A" stroke="#1A1A1A" stroke-width="0.8"/>
  <line x1="3" y1="-4" x2="6" y2="-5" stroke="#1A1A1A" stroke-width="0.6"/>
  <line x1="3" y1="0"  x2="6" y2="0"  stroke="#1A1A1A" stroke-width="0.6"/>
  <line x1="3" y1="4"  x2="6" y2="5"  stroke="#1A1A1A" stroke-width="0.6"/>
</g>
```

### Tent (event destination)

```xml
<g filter="url(#rough)">
  <polygon points="0,-6 -6,3 6,3" fill="#C04D3A" stroke="#1A1A1A" stroke-width="1.2"/>
  <line x1="0" y1="-6" x2="0" y2="3" stroke="#1A1A1A" stroke-width="0.8"/>
  <polygon points="-1,3 1,3 0,-3" fill="#1A1A1A" opacity="0.4"/>
</g>
```

### Campfire (event sub-charm)

```xml
<g filter="url(#rough)">
  <ellipse cx="-6" cy="3" rx="3" ry="1.5" fill="#6C6033" stroke="#1A1A1A" stroke-width="0.8"/>
  <ellipse cx="0" cy="4" rx="3" ry="1.5" fill="#6C6033" stroke="#1A1A1A" stroke-width="0.8"/>
  <ellipse cx="6" cy="3" rx="3" ry="1.5" fill="#6C6033" stroke="#1A1A1A" stroke-width="0.8"/>
  <path d="M -3,2 Q -1,-2 0,-6 Q 1,-3 2,-1 Q 4,-4 3,2 Z" fill="#E07A2A" stroke="#1A1A1A" stroke-width="0.8"/>
</g>
```

### Rubber stamp (rotated red outline + bold letters)

```xml
<g transform="rotate(-9)" filter="url(#roughBig)">
  <rect x="-44" y="-14" width="88" height="28" fill="none" stroke="#C04D3A" stroke-width="2.4"/>
  <text x="0" y="6" font-size="18" font-weight="900" fill="#C04D3A" text-anchor="middle" letter-spacing="3">W·A·R</text>
</g>
```

The dot-separators between letters (`W·A·R`, `T·B·D`, `R·I·P`) are a tic that makes rubber stamps feel official.

## The cursive font stack

For all hand-lettered text inside an SVG:

```xml
font-family="'Marker Felt', 'Comic Sans MS', 'Chalkboard SE', cursive"
```

These are present on macOS by default. The fallback chain catches Linux / Windows users. **Don't use serif or sans-serif fonts** — the cursive feel is half the aesthetic.

## When not to use the rough filters

A few cases where smooth strokes are correct:

- **Dashed dividing lines** in the legend or axis — the dash pattern itself is the texture.
- **Gradient regions** (sky, desert) — the filter can introduce posterization on gradients. Apply the filter to the *border* of a gradient region, not the fill.
- **Tiny details under 2 px** — the filter's displacement (1.6+ px) overwhelms small features. Use `#roughTiny` or no filter.

## Putting it all together — a minimal living SVG

See `../assets/living-svg-skeleton.svg` for a starter SVG that has all of the above wired up. Open it, change the viewBox, drop charms.
