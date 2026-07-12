# Sovereign Mesh landing page

A dependency-free static landing page for Freedom Skills. The visual system treats the library as a living decentralized network: tools form the outer topology, portable skills route usable knowledge, and human agency remains the center of authority.

## Preview

From the repository root:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/site/`. Serving the repository root keeps the relative links to individual skills working.

## Structure

- `index.html` — semantic content, inline network graphic, and all 15 skill routes
- `styles.css` — responsive cyan/amber-on-ink system, motion, and reduced-motion handling
- `script.js` — navigation, copy feedback, skill filters, network inspection, and viewport reveals

There are no external fonts, runtime libraries, or remote assets. Links to repository skills use paths relative to `site/`; serve from the repository structure or update those paths for a standalone deployment.

## Accessibility

The page includes a skip link, semantic landmarks, keyboard-operable controls, focus states, live status regions, mobile navigation, and a `prefers-reduced-motion` mode. The animated network is supplementary; the same capabilities are described in the skill directory below it.
