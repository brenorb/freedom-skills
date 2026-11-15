---
name: napplet-ui
description: Use whenever you write or change napplet markup, CSS, or layout - the applet visual contract. Napplets are software applets framed by a runtime, not web pages - no title header or tagline, compact tool-like density by default, a layout that stays good at ANY size from a tiny widget tile to a full-screen pane (resized live), an explicit minimum-size notice only when the UI genuinely breaks below a size, and NAP-THEME applied to the whole surface. Load before napplet-build touches index.html or styles.
compatibility: CLI workflows assume `@napplet/cli` 0.13.0; package versions are independent, so verify installed SDK types.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-ui"
---

# Napplet UI Contract

A napplet is an **applet** — a piece of software the runtime frames — not a website. The runtime already draws the napplet's name, icon, and window chrome around the iframe. Everything inside the frame is working surface. Apply this skill before touching `index.html`, `src/styles.css`, or any component markup, and re-check it before `napplet-test`.

Three failures show up in almost every unreviewed napplet. Treat them as bugs:

1. A title header (`<h1>` with the napplet name, an eyebrow, a tagline).
2. A website layout: a centered column with a max width, page padding, cards inside cards, dead margins at large sizes, overflow or clipped controls at small sizes.
3. Ignoring size: the napplet was checked at one desktop width only.

## Rule 1 — No title header

Do not render the napplet's own name, subtitle, tagline, "eyebrow", hero, masthead, logo lockup, footer, or credits. The runtime shows the name. The first pixels of the frame belong to the primary control or content.

- Delete the boilerplate's `<header class="masthead">`, `.eyebrow`, and `<h1 id="app-title">` when you replace the starter demo. Keep the `#status` output if the product uses it, but move it into a compact toolbar or status line.
- Content titles are not chrome: a note's subject, a profile's display name, a playlist's title are data — render them. A section label inside a toolbar ("Drafts", "Inbox") is fine when it disambiguates; keep it at body size, not display size.
- Keep the `<title>` element in `index.html`; it is metadata, not UI.
- Do not print the protocol ("NIP-5D napplet"), the framework, or the package versions anywhere in the UI.

## Rule 2 — Compact by default

Default to tool density: think editor panel, chat client, media widget — not landing page.

| Token | Default | Why |
| --- | --- | --- |
| Base font | `13px`–`14px` (`clamp(12px, 0.8rem + 0.2vw, 15px)`) | Applet text, not article text |
| Spacing scale | `4 / 8 / 12 / 16px` | Padding above 16px is almost always waste inside a frame |
| Frame padding | `8px` (`0`–`12px`) | The runtime frame already separates the napplet from its neighbours |
| Control height | `28px`–`32px` | Touch-friendly enough, still dense |
| Corner radius | `4px`–`8px` | Subtle; large radii read as marketing |
| Max content width | none | Fill the frame; wrap into columns instead of capping width |

- The root fills the frame: `html, body, #app { height: 100%; margin: 0; }`. Scroll inside regions (`overflow: auto` on the list/editor), not the whole document, unless the napplet is a single long document.
- One surface level. Panels sit directly on the background; avoid card-inside-card nesting and drop shadows for structure. Use hairline borders or spacing.
- Prefer inline, single-line status over banners; prefer icon buttons with `aria-label` and a `title` over labelled buttons once space is tight.
- Loading, empty, error, and signed-out states are compact and inline (one line of text plus the action that fixes it). No full-frame splash, no illustration.
- Keep the boilerplate's `user-select: none` default; opt real content back in with `data-napplet-select="text"` (the template already provides the rule). Applets should feel like software when dragged or double-clicked.
- Density can be raised or lowered for a product (a reader napplet may want 16px type), but the *default* is dense, and the change must be a deliberate line in the design spec.

## Rule 3 — Responsive-maximalist: good at every size

A runtime may place a napplet anywhere: a widget tile (`~160×120`), a sidebar (`~280` wide), a split pane, a phone-width column, a full-screen tab, a 4K wall — and the user resizes it live. The iframe's viewport **is** the napplet's viewport, so `@media` queries, `vw`/`vh`/`dvh`, and container queries all measure the napplet, not the host page.

Design for the extremes first, then the middle:

| Tier | Inline size | What changes |
| --- | --- | --- |
| tiny | `< 240px` | One primary thing only. Icon-only controls, single column, hide secondary info, no labels beside inputs. |
| compact | `240–480px` | Single column, short labels, toolbar collapses into a row of icons or an overflow menu. |
| regular | `480–900px` | Full labels, two-pane layouts where the product has a list + detail. |
| wide | `> 900px` | Use the space: more columns, more rows visible, wider editors, side-by-side detail. Never a narrow centered column with empty margins. |

Implementation defaults:

- Put `container-type: inline-size` on the app root and write `@container (min-width: …)` rules for components; use `@media` for the tier switches that concern the whole frame. Both work inside the sandboxed iframe.
- Fluid units everywhere: `%`, `fr`, `minmax()`, `clamp()`, `auto-fit` grids (`grid-template-columns: repeat(auto-fit, minmax(160px, 1fr))`). No fixed pixel widths on layout containers; no `min-width` on `body` (delete the boilerplate's `min-width: 320px`).
- Vertical space matters as much as horizontal: a 1000×160 strip and a 300×1200 column are both valid frames. Use `@media (max-height: …)` to collapse toolbars and shrink editors when the frame is short.
- Text truncates (`text-overflow: ellipsis`) or wraps; controls never overflow the frame. At every tier the primary action stays reachable without horizontal scrolling.
- Nothing is position-locked by pixel: no absolute-positioned panels sized for one viewport, no assumptions about the frame's aspect ratio.
- Large sizes are a feature, not a leftover: at `wide`, show more data density (more list rows, more columns, an always-visible detail pane), larger hit targets, richer previews. If the napplet looks identical at 600px and 2400px, it is not done.

## Rule 4 — Minimum size notice (only when the UI genuinely breaks)

Prefer degrading (Rule 3) over refusing. Some napplets do have a hard floor — a game board, a chart that needs axes, a grid editor. For those:

- State the floor in the design spec as exact numbers (`minWidth: 320px`, `minHeight: 240px`) and the reason.
- Below the floor, render a short notice instead of a broken layout: what the napplet needs and what to do (`Needs at least 320×240 — enlarge or open this napplet in a larger pane.`). No headline, no icon required; readable at the smallest size the notice can appear (so it must itself wrap and never overflow).
- Toggle it with CSS, not JS, when possible so it is instant and cannot race the resize:

```css
.too-small { display: none; }
@media (max-width: 319px), (max-height: 239px) {
  .app-body { display: none; }
  .too-small { display: grid; place-items: center; padding: 8px; font-size: 12px; text-align: center; }
}
```

- Keep working state alive while the notice shows (do not unmount editors or drop subscriptions); the user is usually mid-resize.
- Never set a minimum only to avoid doing the compact tier. A feed, composer, list, chat, or settings napplet has no floor.

## Rule 5 — NAP-THEME covers the whole surface

If `theme` is available, the napplet must look native to the host at every size and in dark and light themes. `Theme.colors` carries `background`, `text`, and `primary` (see the installed `@napplet/sdk` types); derive surface, border, and muted tokens from those in one function.

- Apply `background` to `:root`, `html`, `body`, and the app root; apply `text` as the body color; apply `primary` to accents. Never leave a browser-white canvas behind a dark UI or a dark card on a white page.
- Subscribe with `themeOnChanged` and repaint every token, including empty, loading, and error states.
- With no `theme` domain, use an explicit local fallback palette that also sets the page background.
- Optional `theme.fonts` may be applied to body/title text; keep a system-font fallback stack.

Skeleton:

```css
:root {
  --bg: #12111a; --fg: #ece9f6; --primary: #a78bfa;                 /* fallback; runtime theme overrides */
  --surface: color-mix(in srgb, var(--bg) 92%, var(--fg));
  --border: color-mix(in srgb, var(--fg) 14%, transparent);
  --muted: color-mix(in srgb, var(--fg) 60%, var(--bg));
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --control-h: 30px; --radius: 6px;
  font: 13px/1.4 system-ui, sans-serif;
  color-scheme: dark light;
}
html, body, #app { height: 100%; margin: 0; background: var(--bg); color: var(--fg); }
#app { container-type: inline-size; display: grid; grid-template-rows: auto 1fr; gap: var(--space-2); padding: var(--space-2); }
.toolbar { display: flex; gap: var(--space-1); align-items: center; min-height: var(--control-h); }
.toolbar .label { display: none; }
@container (min-width: 480px) { .toolbar .label { display: inline; } }
@container (min-width: 900px) { #app { grid-template-columns: minmax(220px, 1fr) 2fr; } }
```

```ts
import { themeGet, themeOnChanged, type Theme } from '@napplet/sdk';

function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  root.style.setProperty('--bg', theme.colors.background);
  root.style.setProperty('--fg', theme.colors.text);
  root.style.setProperty('--primary', theme.colors.primary);
}
if (window.napplet?.theme) { themeGet().then(applyTheme); themeOnChanged(applyTheme); }
```

## Verification checklist

Run through this at **four** frames before calling the UI done: `200×160`, `320×560`, `900×600`, and the largest the runtime offers (or `2400×1200` in the browser devtools device toolbar while served through Paja). At each:

- No napplet name / tagline / eyebrow / masthead / footer rendered.
- No horizontal scrollbar; no clipped control; primary action visible.
- Frame is filled: no centered column with dead side margins at wide; no empty vertical band at short heights.
- Type and control sizes stay in the compact ranges unless the spec raised them.
- Dark and light runtime themes both paint `html`/`body`/root and all states.
- If a minimum is declared: the notice appears exactly below it, is readable, and the app resumes intact above it.

Record the four frame sizes and the theme pair you checked in the completion report.

## Anti-patterns → replacements

| Seen in agent output | Do instead |
| --- | --- |
| `<h1>My Napplet</h1>` + `<p class="eyebrow">NIP-5D napplet</p>` | Delete; start with the toolbar or content |
| `.workspace { width: min(1040px, 100%); margin: 0 auto; padding: 2rem }` | `#app { height: 100%; padding: 8px }` + container-query tiers |
| `body { min-width: 320px }` | Remove; add a `tiny` tier or a declared minimum with a notice |
| Cards with shadows inside a card | One surface level, hairline borders |
| 16–18px body text, 48px buttons | 13–14px text, 28–32px controls |
| Full-frame "Loading…" splash | Inline status line while content area renders |
| Testing only at the dev browser width | Four-frame check above, both themes |
| `@media (min-width: 768px)` breakpoints copied from web CSS | Tiers keyed on the napplet frame (`240 / 480 / 900`) via container queries |
