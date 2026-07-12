# Freedom Skills field manual landing page

A dependency-free static landing page for Freedom Skills, designed as an expedition handbook and annotated technical dossier.

## Preview

From the repository root:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/site/>. Serving from the repository root keeps links from capability cards to `skills/` working.

## Structure

- `index.html` — semantic page content and the complete 15-skill capability inventory
- `styles.css` — responsive field-manual layout, paper texture, accessible focus states, and reduced-motion treatment
- `script.js` — mobile navigation, skill-category filtering, and progressive reveal enhancement

There are no external fonts, build steps, runtime packages, or remote visual assets. If JavaScript is unavailable, the complete inventory and navigation remain visible.

## Validation

Run these from the repository root:

```bash
node --check site/script.js
git diff --check
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

root = Path.cwd()
page = root / "site/index.html"

class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        for key in ("href", "src"):
            if values.get(key):
                self.refs.append(values[key])

audit = Audit()
audit.feed(page.read_text())
missing = []
for ref in audit.refs:
    parsed = urlparse(ref)
    if parsed.scheme in {"http", "https"}:
        continue
    if ref.startswith("#"):
        if ref[1:] not in audit.ids:
            missing.append(ref)
        continue
    target = (page.parent / parsed.path).resolve()
    if not target.exists():
        missing.append(ref)
assert not missing, f"Missing local references: {missing}"
print(f"OK: {len(audit.ids)} IDs and {len(audit.refs)} references audited")
PY
```
