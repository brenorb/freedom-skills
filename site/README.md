# Freedom Skills civic terminal landing page

A dependency-free static landing page for Freedom Skills. The design combines public-service wayfinding, a service manifest, and a command terminal. It uses only HTML, CSS, and vanilla JavaScript; fonts are local system fallbacks and there are no third-party requests.

## Preview locally

From the repository root:

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000/site/>. Serving from the repository root keeps links from the service directory to `skills/` working.

## Controls

- Select a category or type into the service search to filter the manifest.
- Press `/` outside a text field to focus service search.
- Press `Escape` in service search to clear the query and category.
- Press <kbd>Command</kbd>+<kbd>K</kbd> on macOS or <kbd>Ctrl</kbd>+<kbd>K</kbd> elsewhere to open the route command palette.
- Use arrow keys and <kbd>Enter</kbd> to navigate the palette.

All primary content and links remain available without JavaScript. The stylesheet includes responsive layouts, visible focus states, reduced-motion behavior, and print styles.

## Files

- `index.html` — semantic information architecture and complete skill manifest
- `styles.css` — civic-terminal visual system and responsive states
- `script.js` — search, filters, UTC clock, and command palette
