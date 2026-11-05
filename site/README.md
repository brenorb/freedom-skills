# Freedom Press landing page

A dependency-free static concept for Freedom Skills: a joyful community print shop and open-source zine rendered in cobalt, tomato, sunflower, and off-white.

## Preview

From the repository root:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/site/`. Serving from the repository root keeps links from the edition to the real `skills/` directories working.

## Structure

- `index.html` contains the complete semantic page and all repository-backed content.
- `styles.css` creates the responsive risograph system without images, frameworks, or external fonts.
- `script.js` controls the accessible mobile menu and progressive skill-workbench filters.

The page remains readable without JavaScript. It respects `prefers-reduced-motion`, provides keyboard focus styles and a skip link, and uses no trackers or remote runtime assets.
