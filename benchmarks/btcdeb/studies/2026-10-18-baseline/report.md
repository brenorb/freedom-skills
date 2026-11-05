# Baseline and manual revision

Historical export, not a new benchmark or a regrade. See [every record and metric](results.csv), [structured rows](results.json), [aggregates](benchmark.json), and [source hashes](source-manifest.json).

| Configuration / model | Complete / reviewed | Admitted evaluable | Median seconds all / successful | Median uncached input + output | Lower-bound records |
|---|---:|---:|---:|---:|---:|
| h2-v1-development / offline-no-skill / haiku | 0/12 | 12 | 64.5 / unavailable | 31,554.5 | 12 |
| h2-v1-development / skill-offline / haiku | 10/12 | 12 | 88.2 / 88.2 | 36,927.5 | 7 |
| h2-v1-development / web-no-skill / haiku | 0/12 | 12 | 65.0 / unavailable | 33,942.0 | 12 |
| h2-v1-development / offline-no-skill / luna | 7/12 | 12 | 56.9 / 47.8 | 22,449.5 | 0 |
| h2-v1-development / skill-offline / luna | 12/12 | 12 | 28.1 / 28.1 | 12,553.5 | 0 |
| h2-v1-development / web-no-skill / luna | 8/12 | 12 | 58.7 / 55.6 | 25,447.5 | 0 |
| h2-v1-development / offline-no-skill / qwen | 0/12 | 12 | 240.6 / unavailable | 18,763.0 | 12 |
| h2-v1-development / skill-offline / qwen | 3/12 | 12 | 240.6 / 200.1 | 18,606.0 | 9 |
| h2-v1-development / web-no-skill / qwen | 0/12 | 12 | 240.7 / unavailable | 19,372.0 | 12 |
| h2-v1-holdout / offline-no-skill / haiku | 1/8 | 8 | 114.0 / 100.9 | 47,404.5 | 8 |
| h2-v1-holdout / skill-offline / haiku | 3/8 | 8 | 80.4 / 97.9 | 36,119.0 | 4 |
| h2-v1-holdout / web-no-skill / haiku | 0/8 | 8 | 133.6 / unavailable | 48,177.0 | 8 |
| h2-v1-holdout / offline-no-skill / luna | 2/8 | 8 | 67.1 / 59.6 | 39,774.0 | 0 |
| h2-v1-holdout / skill-offline / luna | 8/8 | 8 | 34.1 / 34.1 | 24,049.5 | 0 |
| h2-v1-holdout / web-no-skill / luna | 7/8 | 8 | 68.9 / 74.8 | 37,663.0 | 0 |
| h2-v1-holdout / offline-no-skill / qwen | 0/8 | 8 | 240.7 / unavailable | 16,413.0 | 8 |
| h2-v1-holdout / skill-offline / qwen | 1/8 | 8 | 240.7 / 163.2 | 17,043.5 | 7 |
| h2-v1-holdout / web-no-skill / qwen | 0/8 | 8 | 240.7 / unavailable | 18,406.0 | 7 |
| h2-v1-repeat-development / skill-offline / haiku | 1/2 | 2 | 56.0 / 39.2 | 26,618.5 | 1 |
| h2-v1-repeat-development / skill-offline / luna | 2/2 | 2 | 28.9 / 28.9 | 13,947.5 | 0 |
| h2-v1-repeat-development / skill-offline / qwen | 0/2 | 2 | 240.8 / unavailable | 14,044.5 | 2 |
| h2-v2-development / skill-offline / haiku | 3/4 | 4 | 54.0 / 63.5 | 27,890.5 | 1 |
| h2-v2-development / skill-offline / luna | 4/4 | 4 | 33.3 / 33.3 | 14,355.5 | 0 |
| h2-v2-development / skill-offline / qwen | 2/4 | 4 | 208.1 / 155.5 | 15,858.0 | 2 |
| h2-v2-holdout / skill-offline / haiku | 3/8 | 8 | 74.5 / 77.6 | 37,846.5 | 5 |
| h2-v2-holdout / skill-offline / luna | 8/8 | 8 | 39.0 / 39.0 | 19,571.0 | 0 |
| h2-v2-holdout / skill-offline / qwen | 0/8 | 8 | 240.7 / unavailable | 17,966.0 | 7 |
| v1-development / offline-no-skill / luna | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| v1-development / skill-offline / luna | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| v1-development / web-no-skill / luna | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| v1-development / offline-no-skill / qwen | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| v1-development / skill-offline / qwen | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |
| v1-development / web-no-skill / qwen | 0/0 | 0 | unavailable / unavailable | unavailable | 0 |

Missing measurements are unavailable, not zero. Failed attempts remain in all-run medians; successful-only subsets can differ. Reasoning is already included in output; cached input is already part of input. These are student observations, not complete experiment cost. Reviewers were model-assisted, unblinded and not human-calibrated.

All six summary snapshots are exported: 222 H2 observations and 36 earlier H1 diagnostics. H1 diagnostics remain visible with admitted=false and are excluded from performance summaries. Original manual completion and machine checks remain distinct. Historical holdouts are now exposed public cases; they are not a fresh sealed test.

Full raw evidence is retained in place and in filtered local archives. [Archive checksum and access status](artifacts.json) explicitly identifies local-only availability; a fresh clone has compact records, not raw traces. No hosted archive was published. Archives exclude named auth/cache/executable and sealed-final boundaries; they are not a transcript secret scanner.
