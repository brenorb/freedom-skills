# Freedom Skills — Autonomy Atlas

A dependency-free landing page concept for Freedom Skills, designed as a luminous cartographic atlas rather than a conventional software catalogue.

## Preview

From the repository root:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/site/`. Serving from the repository root preserves the landing page's relative links to each skill directory.

## Design direction

- Warm parchment, ultramarine ink, vermilion wayfinding, engraved linework, and map legends
- Six routes collecting all 15 skills into a journey through communication, money, privacy, preservation, research, and product design
- Editorial, asymmetric layouts and an original inline SVG compass with no image or font downloads
- Route filtering with arrow-key navigation, URL persistence, live result announcements, Escape-to-reset, and journey progress
- Responsive, print-friendly, reduced-motion, and no-JavaScript states

## Files

- `index.html` — page structure, project copy, inline atlas artwork, and all skill landmarks
- `styles.css` — visual system, responsive layouts, animation, print, and accessibility states
- `script.js` — progressive route filtering, keyboard behavior, section awareness, and scroll progress

There are no package installs, build steps, external fonts, trackers, or runtime dependencies.
