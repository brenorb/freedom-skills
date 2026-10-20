#!/usr/bin/env python3
"""Apply one current deterministic oracle to completed cells, retaining originals."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import suite


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('batch', type=Path)
    args = parser.parse_args()
    batch = args.batch.resolve()
    stories = suite.read_json(batch / 'stories.json')
    oracle_hash = hashlib.sha256(Path(suite.__file__).read_bytes()).hexdigest()
    results = []
    for model in ['luna', 'haiku', 'qwen']:
        for story in stories:
            record = batch / model / story['id']
            if not (record / 'metrics.json').exists():
                continue
            original = record / 'verdict.json'
            if original.exists() and not (record / 'verdict-first.json').exists():
                shutil.copy2(original, record / 'verdict-first.json')
            previous = suite.read_json(original, {})
            try:
                verdict = suite.grade(story, record, record / 'workspace')
            except Exception as error:
                verdict = {'pass': False, 'errors': [str(error)], 'infrastructure_error': True}
            verdict['oracle_sha256'] = oracle_hash
            suite.dump(original, verdict)
            results.append({'model': model, 'story': story['id'], **verdict})
            if not verdict['pass'] or previous.get('pass') != verdict['pass']:
                print(json.dumps({'model': model, 'story': story['id'],
                                  'pass': verdict['pass'], 'errors': verdict['errors']}), flush=True)
    suite.dump(batch / 'regraded-results.json', results)
    print(json.dumps({'complete': len(results), 'passed': sum(r['pass'] for r in results),
                      'oracle_sha256': oracle_hash}))


if __name__ == '__main__':
    main()
