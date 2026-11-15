#!/usr/bin/env python3
"""Export compact evidence; never copy runner state, auth links, or raw logs."""
import argparse
import hashlib
import json
from pathlib import Path
from equivalence import frozen_hash, validate as validate_equivalence


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def story_hash(story):
    return hashlib.sha256(json.dumps(story, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('batch', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--replay', type=Path, action='append', default=[], help='Chronological fresh replay batches; retain all earlier outcomes')
    parser.add_argument('--equivalence', type=Path, help='Explicit trace-bound primary-agent audit for unchanged instruction inputs across revisions')
    parser.add_argument('--scenario-revisions', type=Path, help='Explicit raw-input clarifications; changed stories require fresh selected runs')
    args = parser.parse_args()
    batch = args.batch.resolve()
    stories = read(batch / 'stories.json')
    reviews = read(batch / 'reviews.json', {})
    oracle_hash = hashlib.sha256(Path(__file__).with_name('suite.py').read_bytes()).hexdigest()
    batches = [batch] + [value.resolve() for value in args.replay]
    target = batches[-1]
    stories = read(target / 'stories.json')
    revisions = read(args.scenario_revisions, {}) if args.scenario_revisions else {}
    skill_hash = (target / 'skill.sha256').read_text().strip()
    equivalence_manifest = read(args.equivalence, {}) if args.equivalence else {}
    for candidate in batches:
        if frozen_hash(candidate / 'skill-snapshot') != (candidate / 'skill.sha256').read_text().strip():
            raise ValueError('Frozen skill snapshot changed: '+str(candidate))
        prior = read(candidate / 'stories.json')
        if [s['id'] for s in prior] != [s['id'] for s in stories]:
            raise ValueError('Replay uses different story IDs: '+str(candidate))
        for old, current in zip(prior, stories):
            if old == current:
                continue
            revision = revisions.get(current['id'], {})
            if not (revision.get('source_story_sha256') == story_hash(old)
                    and revision.get('target_story_sha256') == story_hash(current)
                    and revision.get('reason')
                    and {k:v for k,v in old.items() if k != 'task'} == {k:v for k,v in current.items() if k != 'task'}):
                raise ValueError('Unapproved scenario change: '+str(candidate)+'/'+current['id'])
    rows = []
    for model in ['luna', 'haiku', 'qwen']:
        for story in stories:
            attempts = []
            for candidate in batches:
                attempt = candidate / model / story['id']
                if attempt.exists():
                    v = read(attempt / 'verdict.json', {})
                    review_entry = read(candidate / 'reviews.json', {}).get(model + '/' + story['id'], {})
                    attempt_metrics = read(attempt / 'metrics.json', {})
                    runner_errors = ' '.join(str(value) for value in attempt_metrics.get('errors', []))
                    operator_stop = read(attempt / 'operator-stop.json')
                    classification = 'operator interruption' if operator_stop else 'capacity' if 'session limit' in runner_errors else 'inference infrastructure' if 'Metal backend' in runner_errors else 'workflow'
                    attempt_story = read(attempt / 'story.json')
                    attempts.append({'batch': candidate.name, 'classification': classification, 'same_scenario': attempt_story == story, 'source_story_sha256': story_hash(attempt_story), 'runner_errors': attempt_metrics.get('errors', []), 'completed': (attempt / 'metrics.json').exists(), 'operator_stop': operator_stop, 'technical_pass': v.get('pass', False), 'review_pass': review_entry.get('pass', False), 'errors': v.get('errors', ['Incomplete run']), 'review': review_entry})
            selected = next((candidate for candidate in reversed(batches) if (candidate / model / story['id']).exists()), batch)
            record = selected / model / story['id']
            verdict = read(record / 'verdict.json', {})
            metrics = read(record / 'metrics.json', {})
            config = read(record / 'launch-config.json', {})
            review = read(selected / 'reviews.json', {}).get(model + '/' + story['id'], {})
            source_story = read(record / 'story.json')
            declared_story = next(s for s in read(selected / 'stories.json') if s['id'] == story['id'])
            prompt_path = record / 'prompt.md'
            prompt = prompt_path.read_text() if prompt_path.exists() else ''
            prompt_bound = bool(prompt_path.exists()
                and hashlib.sha256(prompt_path.read_bytes()).hexdigest() == metrics.get('prompt_sha256')
                and config.get('prompt') == prompt
                and prompt.startswith(story['task'] + '\n\n'))
            same_scenario = source_story == declared_story == story and prompt_bound
            same_skill = (record / 'skill.sha256').exists() and (
                record / 'skill.sha256').read_text().strip() == skill_hash
            equivalent_inputs = None if same_skill else validate_equivalence(equivalence_manifest, record, selected, target)
            actual_models = metrics.get('actual_models', [])
            model_matches = (actual_models == ['gpt-6-luna'] and config.get('thinking') == 'high') if model == 'luna' else (bool(actual_models) and all('haiku' in name for name in actual_models)) if model == 'haiku' else actual_models == ['splash/incoai/Qwen3.8-27B-Splash']
            same_oracle = verdict.get('oracle_sha256') == oracle_hash
            source_matches = (record / 'skill.sha256').exists() and (record / 'skill.sha256').read_text() == (selected / 'skill.sha256').read_text()
            passed = bool(verdict.get('pass') and review.get('pass') and same_scenario and (same_skill or equivalent_inputs) and source_matches and metrics.get('frozen_paths_unchanged') is True and model_matches and same_oracle)
            rows.append({
                'model': model, 'story': story['id'], 'title': story['title'],
                'selected_batch': selected.name, 'attempts': attempts,
                'pass': passed, 'technical_pass': verdict.get('pass', False),
                'review': review, 'same_skill': same_skill, 'model_matches': model_matches, 'same_oracle': same_oracle,
                'same_scenario': same_scenario,
                'source_story_sha256': story_hash(source_story), 'target_story_sha256': story_hash(story),
                'source_skill_sha256': (selected / 'skill.sha256').read_text().strip(),
                'equivalent_instruction_inputs': equivalent_inputs,
                'errors': verdict.get('errors', ['Incomplete run']),
                'actual_models': metrics.get('actual_models', []),
                'thinking': config.get('thinking'), 'timeout_seconds': config.get('timeout_seconds'),
                'seconds': metrics.get('seconds'), 'tool_calls': metrics.get('tools'),
                'runner_exit_code': metrics.get('exit_code'),
                'normal_completion': metrics.get('normal_completion',metrics.get('exit_code')==0),
                'system_prompt_sha256': metrics.get('system_prompt_sha256'),
                'system_prompt_mode': metrics.get('system_prompt_mode',
                    'native_with_user_prefix' if config.get('runner')=='codex' else
                    'native_plus_custom' if config.get('native_system_context') else 'custom_replacement'),
                'network_policy': metrics.get('network_policy'),
                'controller_completion': metrics.get('controller_completion'),
                'frozen_paths_unchanged': metrics.get('frozen_paths_unchanged'),
                'response_sha256': hashlib.sha256((record / 'response.md').read_bytes()).hexdigest()
                    if (record / 'response.md').exists() else None,
                'evidence': verdict.get('evidence', {}),
            })
    result = {
        'batch': batch.name, 'target_batch': target.name, 'skill_sha256': skill_hash, 'oracle_sha256': oracle_hash,
        'passed': sum(row['pass'] for row in rows), 'total': len(rows),
        'first_attempt_passed': sum(bool(row['attempts'] and row['attempts'][0]['technical_pass'] and row['attempts'][0]['review_pass']) for row in rows),
        'replayed_cells': sum(len(row['attempts']) > 1 for row in rows),
        'audited_unchanged_input_cells': sum(bool(row['equivalent_instruction_inputs']) for row in rows),
        'first_attempt_infrastructure_failures': sum(bool(row['attempts'] and row['attempts'][0]['classification'] in ['capacity','inference infrastructure']) for row in rows),
        'first_attempt_operator_interruptions': sum(bool(row['attempts'] and row['attempts'][0]['classification'] == 'operator interruption') for row in rows),
        'gate_passed': all(row['pass'] for row in rows), 'results': rows,
        'scenario_revisions': revisions,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = [
        '# Hosted Nowhere acceptance results', '',
        f"Gate: **{result['passed']}/{len(rows)} passed**; "
        + ('eligible to push.' if result['gate_passed'] else 'push remains gated.'), '',
        f'Frozen skill SHA-256: `{skill_hash}`.', '',
        f"First recorded attempt in this final acceptance matrix: {result['first_attempt_passed']}/{len(rows)}. "
        f"Infrastructure/capacity failures on first attempts: {result['first_attempt_infrastructure_failures']}. "
        f"Operator interruptions on first attempts: {result['first_attempt_operator_interruptions']}. "
        f"Replayed cells: {result['replayed_cells']}. Earlier failures remain in results.json; "
        'a replay is a fresh unassisted session. Earlier revision results qualify only '
        'through an explicit audit of all tool inputs proving their loaded instruction '
        'files and content-search outputs are unchanged. Original source hashes and '
        'trace-bound audit records remain in results.json.', '',
        f"Audited unchanged-input cells: {result['audited_unchanged_input_cells']}. "
        'Changed app references are retested freshly on all three runners; '
        'unaffected cases require the recorded instruction-input audit.', '',
        'Each cell is a fresh session. A pass requires deterministic app/CLI/relay '
        'checks and primary-agent review of its final account. Raw traces remain '
        f'outside the repository under `{batch.parent}`; runner state and auth files are not exported.', '',
        '| Story | Luna High | Claude Haiku | SOMP Qwen |',
        '| --- | --- | --- | --- |',
    ]
    indexed = {(row['model'], row['story']): row for row in rows}
    def status(row):
        if row['pass']:
            return 'PASS after replay' if len(row['attempts'])>1 else 'PASS'
        if not row['attempts'] or not row['attempts'][-1]['completed']:
            return 'REPLAY PENDING' if len(row['attempts'])>1 else 'PENDING'
        if not row['same_scenario']:
            return 'RETEST REQUIRED'
        if row['technical_pass'] and not row['review']:
            return 'REVIEW PENDING'
        return 'FAIL'
    for story in stories:
        statuses = [status(indexed[model, story['id']]) for model in ['luna', 'haiku', 'qwen']]
        lines.append('| ' + story['id'] + ' ' + story['title'] + ' | '
                     + ' | '.join(statuses) + ' |')
    lines += ['', 'See [protocol.md](protocol.md) for runner isolation, controlled '
              'service boundaries, and the meaning of a pass. TEST_ONLY invoice '
              'generation is not real payment settlement; relay acceptance is '
              'not a promise of retention or recipient delivery.', '']
    if revisions:
        lines += ['Scenario wording revisions (fresh selected runs required):']
        lines += ['- '+key+': '+value['reason'] for key,value in revisions.items()]
        lines.append('')
    (args.output / 'report.md').write_text('\n'.join(lines))
    print(json.dumps({key: result[key] for key in ['passed', 'total', 'gate_passed']}))
    return 0 if result['gate_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
