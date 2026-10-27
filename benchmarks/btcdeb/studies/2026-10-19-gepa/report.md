# GEPA search (negative result)

Historical export, not a new benchmark or a regrade. See [every record and metric](results.csv), [structured rows](results.json), [aggregates](benchmark.json), and [source hashes](source-manifest.json).

| Configuration / model | Complete / reviewed | Admitted evaluable | Median seconds all / successful | Median uncached input + output | Lower-bound records |
|---|---:|---:|---:|---:|---:|
| search-validation / 37e5b2a3cc8977eb / haiku | 3/4 | 4 | 70.2 / 69.4 | 34,851.5 | 2 |
| search-validation / 37e5b2a3cc8977eb / qwen | 1/4 | 4 | 240.6 / 88.5 | 16,078.0 | 3 |
| search-validation / 596e1a22fad99939 / haiku | 3/4 | 4 | 67.9 / 77.5 | 28,469.5 | 3 |
| search-validation / 596e1a22fad99939 / qwen | 3/4 | 4 | 192.5 / 192.1 | 16,460.0 | 1 |
| search-validation / 9c159019b57c4646 / haiku | 3/4 | 4 | 80.1 / 61.3 | 39,119.0 | 2 |
| search-validation / 9c159019b57c4646 / qwen | 1/4 | 4 | 240.9 / 51.9 | 17,319.0 | 3 |
| search-validation / a7079bad62abcbea / haiku | 2/4 | 4 | 68.6 / 49.6 | 29,690.0 | 2 |
| search-validation / a7079bad62abcbea / qwen | 1/4 | 4 | 240.6 / 79.6 | 12,172.0 | 3 |
| search-validation / cf6e2f491eda155a / haiku | 3/4 | 4 | 77.6 / 72.9 | 35,230.0 | 2 |
| search-validation / cf6e2f491eda155a / qwen | 1/4 | 4 | 240.7 / 159.8 | 13,068.0 | 3 |
| training / 37e5b2a3cc8977eb / haiku | 1/2 | 2 | 100.9 / 39.7 | 36,139.0 | 1 |
| training / 37e5b2a3cc8977eb / qwen | 0/2 | 2 | 241.0 / unavailable | 18,565.5 | 2 |
| training / 596e1a22fad99939 / haiku | 2/6 | 6 | 80.7 / 82.0 | 32,668.0 | 4 |
| training / 596e1a22fad99939 / qwen | 0/6 | 6 | 240.7 / unavailable | 14,381.5 | 6 |
| training / 9c159019b57c4646 / haiku | 2/2 | 2 | 45.4 / 45.4 | 25,348.5 | 0 |
| training / 9c159019b57c4646 / qwen | 2/2 | 2 | 173.6 / 173.6 | 18,873.0 | 0 |
| training / a7079bad62abcbea / haiku | 1/2 | 2 | 89.6 / 65.6 | 39,389.5 | 1 |
| training / a7079bad62abcbea / qwen | 0/2 | 2 | 240.8 / unavailable | 14,570.0 | 2 |
| training / cf6e2f491eda155a / haiku | 3/4 | 4 | 44.4 / 39.0 | 28,523.0 | 1 |
| training / cf6e2f491eda155a / qwen | 1/4 | 4 | 240.6 / 104.0 | 17,682.0 | 3 |
| diagnostic / 596e1a22fad99939 / haiku | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| diagnostic / 596e1a22fad99939 / qwen | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| diagnostic / 6d9c569ab919c384 / haiku | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| diagnostic / 6d9c569ab919c384 / qwen | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| diagnostic / 7fc94f7f33c35612 / haiku | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| diagnostic / 7fc94f7f33c35612 / qwen | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| diagnostic / 9ea675f687f539c2 / haiku | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| diagnostic / 9ea675f687f539c2 / qwen | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |

Missing measurements are unavailable, not zero. Failed attempts remain in all-run medians; successful-only subsets can differ. Reasoning is already included in output; cached input is already part of input. These are student observations, not complete experiment cost. Reviewers were model-assisted, unblinded and not human-calibrated.

Seed validation: Haiku 3/4, Qwen 3/4. Four valid proposals: Haiku 3/4, 3/4, 2/4, 3/4; Qwen 1/4 for each. No candidate improved both; no promotion or final unsealing. Initial 28 plus extension 16 logical pairs reuse original seed observations, yielding 72 unique admitted records. All 92 retained student metrics, including 20 not admitted to valid search, are in results.json. Do not treat diagnostic stored scores as eligible performance.

Observed failures included useful tool work followed by missing requested delivery, unnecessary probes and output-budget exhaustion. The helper guide lacks a compact JSON-shape example; one Qwen run assumed a list where the actual result was a dictionary. Haiku runner mechanics improved but the required aggregate passed field was absent or renamed all_passed. A helper-path-prefix ambiguity also remained. Secondary factual defects were recorded separately from central completion. No measured candidate was silently repaired after evaluation.

The all-attempt ledger reports Haiku 8,459,945 total /1,450,964 uncached-plus-output tokens and 3042.92 seconds; Qwen 2,281,891 /734,307 tokens and 9513.98 seconds. 53/92 usage records are lower bounds. Seven retained reflection requests include excluded trajectories; reflection/reviewer/orchestrator provider tokens are unavailable. A separate Haiku preflight probe (5.47 seconds, 7199 tokens) is outside student rows. Final cases remain sealed.

Full raw evidence is retained in place and in filtered local archives. [Archive checksum and access status](artifacts.json) explicitly identifies local-only availability; a fresh clone has compact records, not raw traces. No hosted archive was published. Archives exclude named auth/cache/executable and sealed-final boundaries; they are not a transcript secret scanner.
