import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('legacy_export', ROOT / 'benchmarks/btcdeb/export_legacy.py')
export = importlib.util.module_from_spec(spec); spec.loader.exec_module(export)


class HistoricalContracts(unittest.TestCase):
    def test_full_baseline_coverage_keeps_diagnostic_cohort(self):
        folder = ROOT / 'benchmarks/btcdeb/studies/2026-10-18-baseline'
        rows = json.loads((folder / 'results.json').read_text())['records']
        self.assertEqual(len(rows), 258)
        self.assertEqual(sum(x['admitted'] for x in rows), 222)
        self.assertEqual(sum(not x['admitted'] for x in rows), 36)
        self.assertEqual(len({x['id'] for x in rows}), len(rows))
        sources = json.loads((folder / 'source-manifest.json').read_text())['files']
        self.assertEqual(sum(name.endswith('-summary.json') for name in sources), 6)
        # Original review corrected a mechanical miss; do not silently regrade it.
        row = next(x for x in rows if x['phase'] == 'h2-v2-holdout' and x['model'] == 'haiku' and x['case'] == 'B07')
        self.assertIs(row['completed'], True); self.assertIs(row['machine_passed'], False)

    def test_gepa_dedup_admission_and_missing_measurements(self):
        folder = ROOT / 'benchmarks/btcdeb/studies/2026-10-19-gepa'
        rows = json.loads((folder / 'results.json').read_text())['records']
        self.assertEqual(len(rows), 92); self.assertEqual(len({x['id'] for x in rows}), 92)
        self.assertEqual(sum(x['admitted'] for x in rows), 72)
        self.assertEqual(sum(x['usage_is_lower_bound'] is True for x in rows), 53)
        self.assertTrue(any(x['completed'] is None for x in rows))
        validation = [x for x in rows if x['admitted'] and x['split'] == 'search-validation']
        self.assertEqual(len(validation), 40)
        for candidate in {x['candidate'] for x in validation}:
            for model in ('haiku', 'qwen'):
                selected = [x for x in validation if x['candidate'] == candidate and x['model'] == model]
                self.assertEqual(len(selected), 4)
        self.assertEqual(export.measure([None])['sum_observed'], None)
        self.assertEqual(export.measure([0, None])['sum_observed'], 0)
        self.assertEqual(export.measure([True, float('nan')])['n_observed'], 0)

    def test_every_catalogued_study_and_source_hash_is_resolvable(self):
        base = ROOT / 'benchmarks'; index = json.loads((base / 'index.json').read_text())
        for study in index['studies']:
            self.assertTrue((base / study['path'] / 'report.md').is_file())
            if study['raw_access'] == 'local_only':
                artifact = json.loads((base / study['path'] / 'artifacts.json').read_text())
                self.assertEqual(artifact['availability'], 'local_only')
                self.assertEqual(len(artifact['archive_sha256']), 64)
                self.assertTrue(artifact['originals_retained'])
                self.assertFalse(Path(artifact['local_path']).is_absolute())
                config = json.loads((base / study['path'] / 'study.json').read_text())
                actual = hashlib.sha256((base / study['path'] / 'protocol.md').read_bytes()).hexdigest()
                self.assertEqual(actual, config['protocol_source_sha256'])


if __name__ == '__main__': unittest.main()
