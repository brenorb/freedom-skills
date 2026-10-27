# btcdeb evidence

- [Baseline and manual revision](studies/2026-10-18-baseline/report.md): all six source summaries, 258 rows including 222 admitted H2 observations and 36 H1 diagnostics. Luna with the original skill completed 20/20; the revised skill completed 12/12 tested cases. This is historical output quality, not automatic skill discovery.
- [GEPA evolution](studies/2026-10-19-gepa/report.md): 92 retained student metrics, 72 admitted unique observations, no candidate improved both models. No GEPA package was promoted; final cases remain sealed.

The runtime skill is [skills/btcdeb](../../skills/btcdeb/). Its 20 public eval cases
were already exposed in the original study. `historical_split` records old cohort
labels; those cases are no longer a fresh holdout. Trigger queries are unexecuted.

Both studies retain compact per-record JSON/CSV, per-configuration metrics and
source checksums. Full traces/code snapshots remain in their untouched legacy
directories and filtered local archives. Archive checksums and access gaps are
explicit in each study's `artifacts.json`; raw evidence is not hosted by this PR.

`export_legacy.py` reads only named historical summaries/accounting records and
hashes associated record metadata. It neither reads final inputs nor launches
models, evaluates outputs or alters sources. To independently regenerate exports
from available legacy evidence, choose a new empty output directory:

```sh
python3 benchmarks/btcdeb/export_legacy.py baseline /path/to/btcdeb-2026-10-18 /tmp/baseline-export
python3 benchmarks/btcdeb/export_legacy.py gepa /path/to/btcdeb-gepa-2026-10-19 /tmp/gepa-export
```

The archive access and path reconstruction requirements in the [repository guide](../README.md)
apply. Reports preserve the original completion definition; they do not silently
replace agent-assisted reviews with machine-only checks.
