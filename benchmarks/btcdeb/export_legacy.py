#!/usr/bin/env python3
"""Export compact historical facts, never run models, regrade, or open final inputs.

Legacy files stay authoritative. Outputs must be new; regenerate into another
directory and review differences rather than overwriting a published study.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

TOKEN_KEYS = ('input_tokens', 'cached_input_tokens', 'cache_write_tokens', 'output_tokens',
              'reasoning_tokens', 'total_tokens', 'uncached_input_plus_output')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(values):
    observed = [x for x in values if type(x) in (int, float) and math.isfinite(x)]
    return {'n_observed': len(observed), 'n_missing': len(values) - len(observed),
            'sum_observed': sum(observed) if observed else None,
            'median_observed': statistics.median(observed) if observed else None}


def groups(rows, fields):
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[tuple(row[field] for field in fields)].append(row)
    output = []
    for key, items in sorted(grouped.items()):
        evaluable = [x for x in items if x['admitted'] and x['infrastructure_error'] is not True]
        reviewed = [x for x in evaluable if type(x['completed']) is bool]
        successful = [x for x in reviewed if x['completed']]
        output.append({**dict(zip(fields, key)), 'records': len(items),
            'admitted_evaluable': len(evaluable), 'reviewed': len(reviewed),
            'completed': len(successful),
            'seconds_all': measure([x['seconds'] for x in evaluable]),
            'seconds_successful': measure([x['seconds'] for x in successful]),
            'usage_lower_bound_records': sum(x['usage_is_lower_bound'] is True for x in evaluable),
            'usage': {k: measure([x['usage'].get(k) for x in evaluable]) for k in TOKEN_KEYS}})
    return output


def source_json(root, name, sources):
    path = root / name
    sources[name] = sha(path)
    return json.loads(path.read_text())


def baseline(root):
    sources = {}; rows = []
    phases = ['v1-development', 'h2-v1-development', 'h2-v1-holdout',
              'h2-v1-repeat-development', 'h2-v2-development', 'h2-v2-holdout']
    for phase in phases:
        data = source_json(root, phase + '-summary.json', sources)
        for value in data['rows']:
            rows.append({'id': value['record'], 'phase': phase,
                'model': value['model_label'], 'model_id': value['model'], 'runner': value['runner'],
                'case': value['case'], 'condition': value['arm'], 'repetition': value['repetition'],
                'admitted': phase.startswith('h2-'), 'completed': value['manual_completed'],
                'machine_passed': value['machine_passed'], 'infrastructure_error': value['infrastructure_error'],
                'seconds': value['seconds'], 'usage': {k: value.get(k) for k in TOKEN_KEYS},
                'usage_is_lower_bound': value.get('usage_is_lower_bound'),
                'budget_exhausted': value.get('budget_exhausted'), 'tool_calls': value.get('tool_calls'),
                'quality_issues': value.get('quality_issues'), 'source_summary': phase + '-summary.json'})
    if len(rows) != 258 or sum(x['admitted'] for x in rows) != 222:
        raise ValueError('Expected the complete258-row historical inventory (222H2,36H1 diagnostics)')
    return rows, groups(rows, ('phase', 'model', 'condition')), sources


def gepa(root):
    sources = {}; rows = []
    accounting = source_json(root, 'oracle/study-accounting-completed.json', sources)
    diagnostics = source_json(root, 'oracle/search-diagnostics.json', sources)
    admitted = {x['record']: x for x in diagnostics['records']}
    for value in accounting['records']:
        relative = Path(*Path(value['path']).parts[-4:])
        if relative.parts != (value['model'], value['candidate'], value['case'], value['uuid']):
            raise ValueError('Historical record identity does not match its path')
        if any(not part or part in ('.', '..') or '/' in part for part in relative.parts):
            raise ValueError('Unsafe historical record identity')
        record = root / 'runs' / relative
        diagnostic = admitted.get(value['path'])
        metric = value['metrics'] or {}
        score = value['stored_completion']
        rows.append({'id': value['uuid'], 'phase': 'valid_search' if diagnostic else 'not_admitted',
            'model': value['model'], 'model_id': 'haiku' if value['model'] == 'haiku' else 'splash/incoai/Qwen3.8-27B-Splash',
            'runner': 'claude' if value['model'] == 'haiku' else 'omp',
            'condition': 'seed-offline' if value['candidate'] == '596e1a22fad99939' else 'candidate-offline',
            'repetition': 1 if diagnostic else None,
            'candidate': value['candidate'], 'case': value['case'],
            'split': diagnostic['split'] if diagnostic else None,
            'rounds': diagnostic['rounds'] if diagnostic else [], 'admitted': diagnostic is not None,
            'completed': bool(score) if type(score) in (int, float) and score in (0, 1) else None,
            'infrastructure_error': value['stored_infrastructure_error'],
            'seconds': metric.get('seconds'), 'usage': metric.get('usage') or {},
            'usage_is_lower_bound': metric.get('usage_is_lower_bound'),
            'timed_out': metric.get('timed_out'), 'tool_calls': metric.get('tools'),
            'legacy_record': 'runs/' + relative.as_posix(),
            'evidence_hashes': {n: sha(record / n) if (record / n).is_file() else None for n in
                                ['metrics.json', 'evaluation.json', 'review.json', 'sealed.sha256.json']}})
    if len(rows) != 92 or sum(x['admitted'] for x in rows) != 72:
        raise ValueError('Expected all92 retained metrics and72 admitted unique observations')
    benchmark = groups([dict(x, condition=x['candidate'], split=x['split'] or 'diagnostic') for x in rows],
                       ('split', 'model', 'condition'))
    return rows, benchmark, sources


def publish(root, output, mode):
    root, output = root.resolve(), output.resolve()
    rows, summary, sources = baseline(root) if mode == 'baseline' else gepa(root)
    if len({x['id'] for x in rows}) != len(rows):
        raise ValueError('Duplicate historical record identity')
    files = ['results.json', 'results.csv', 'benchmark.json', 'report.md', 'source-manifest.json']
    if any((output / name).exists() for name in files):
        raise ValueError('Refusing to rewrite a previous export')
    output.mkdir(parents=True, exist_ok=True)
    sources['report.md'] = sha(root / 'report.md')
    if mode == 'gepa':
        sources['oracle/failure-analysis.md'] = sha(root / 'oracle/failure-analysis.md')
    source_manifest = {'legacy_path': 'benchmarks/' + root.name, 'files': sources,
        'policy': 'All listed source snapshots inspected. No inference, regrading, or final-input reads.'}
    (output / 'source-manifest.json').write_text(json.dumps(source_manifest, indent=2) + '\n')
    (output / 'results.json').write_text(json.dumps({'schema_version': 1, 'records': rows}, indent=2) + '\n')
    (output / 'benchmark.json').write_text(json.dumps({'schema_version': 1, 'groups': summary,
        'metric_policy': 'Original completion retained; machine checks separate. Unknown usage stays null. No token-category summation or comparison of different task subsets.'}, indent=2) + '\n')
    columns = ['id', 'phase', 'model', 'model_id', 'runner', 'case', 'split', 'condition', 'candidate', 'repetition', 'admitted', 'completed', 'infrastructure_error', 'seconds', 'usage_is_lower_bound', *TOKEN_KEYS]
    with (output / 'results.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n'); writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in columns if k not in TOKEN_KEYS} | {k: row['usage'].get(k) for k in TOKEN_KEYS})
    label = 'Baseline and manual revision' if mode == 'baseline' else 'GEPA search (negative result)'
    lines = ['# ' + label, '',
        'Historical export, not a new benchmark or a regrade. See [every record and metric](results.csv), [structured rows](results.json), [aggregates](benchmark.json), and [source hashes](source-manifest.json).', '',
        '| Configuration / model | Complete / reviewed | Admitted evaluable | Median seconds all / successful | Median uncached input + output | Lower-bound records |',
        '|---|---:|---:|---:|---:|---:|']
    def fmt(x): return 'unavailable' if x is None else f'{x:,.1f}'
    ordered = sorted(summary, key=lambda x: ({'search-validation': 0, 'training': 1, 'diagnostic': 2}.get(x.get('split'), 0), x.get('condition', ''), x.get('model', ''))) if mode == 'gepa' else summary
    for group in ordered:
        key = ' / '.join(str(group[k]) for k in (('phase', 'condition', 'model') if mode == 'baseline' else ('split', 'condition', 'model')))
        lines.append(f"| {key} | {group['completed']}/{group['reviewed']} | {group['admitted_evaluable']} | "
                     f"{fmt(group['seconds_all']['median_observed'])} / {fmt(group['seconds_successful']['median_observed'])} | "
                     f"{fmt(group['usage']['uncached_input_plus_output']['median_observed'])} | {group['usage_lower_bound_records']} |")
    lines += ['', 'Missing measurements are unavailable, not zero. Failed attempts remain in all-run medians; successful-only subsets can differ. Reasoning is already included in output; cached input is already part of input. These are student observations, not complete experiment cost. Reviewers were model-assisted, unblinded and not human-calibrated.', '']
    if mode == 'baseline':
        lines += ['All six summary snapshots are exported: 222 H2 observations and 36 earlier H1 diagnostics. H1 diagnostics remain visible with admitted=false and are excluded from performance summaries. Original manual completion and machine checks remain distinct. Historical holdouts are now exposed public cases; they are not a fresh sealed test.', '']
    else:
        lines += ['Seed validation: Haiku 3/4, Qwen 3/4. Four valid proposals: Haiku 3/4, 3/4, 2/4, 3/4; Qwen 1/4 for each. No candidate improved both; no promotion or final unsealing. Initial 28 plus extension 16 logical pairs reuse original seed observations, yielding 72 unique admitted records. All 92 retained student metrics, including 20 not admitted to valid search, are in results.json. Do not treat diagnostic stored scores as eligible performance.', '',
                  'Observed failures included useful tool work followed by missing requested delivery, unnecessary probes and output-budget exhaustion. The helper guide lacks a compact JSON-shape example; one Qwen run assumed a list where the actual result was a dictionary. Haiku runner mechanics improved but the required aggregate passed field was absent or renamed all_passed. A helper-path-prefix ambiguity also remained. Secondary factual defects were recorded separately from central completion. No measured candidate was silently repaired after evaluation.', '',
                  'The all-attempt ledger reports Haiku 8,459,945 total /1,450,964 uncached-plus-output tokens and 3042.92 seconds; Qwen 2,281,891 /734,307 tokens and 9513.98 seconds. 53/92 usage records are lower bounds. Seven retained reflection requests include excluded trajectories; reflection/reviewer/orchestrator provider tokens are unavailable. A separate Haiku preflight probe (5.47 seconds, 7199 tokens) is outside student rows. Final cases remain sealed.', '']
    lines += ['Full raw evidence is retained in place and in filtered local archives. [Archive checksum and access status](artifacts.json) explicitly identifies local-only availability; a fresh clone has compact records, not raw traces. No hosted archive was published. Archives exclude named auth/cache/executable and sealed-final boundaries; they are not a transcript secret scanner.', '']
    (output / 'report.md').write_text('\n'.join(lines))
    return {'records': len(rows), 'admitted': sum(x['admitted'] for x in rows), 'output': str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['baseline', 'gepa']); parser.add_argument('legacy', type=Path); parser.add_argument('output', type=Path)
    args = parser.parse_args(); print(json.dumps(publish(args.legacy, args.output, args.mode)))


if __name__ == '__main__': main()
