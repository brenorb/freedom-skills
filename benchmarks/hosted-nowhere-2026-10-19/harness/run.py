#!/usr/bin/env python3
"""Launch fresh Codex Luna / Claude Haiku / SOMP Qwen runs with common tools.

Usage: python3 run.py CONFIG.json
The config must supply record, workspace, runner, model, prompt and optionally
internet, skill_path, thinking, timeout_seconds, max_turns, max_tool_calls.
No scored inference is performed merely by importing this module.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import shlex
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SYSTEM_PROMPT = ('Complete the user task using the supplied workspace tools. '
                 'Work independently. Verify results by executing the available tools. '
                 'Save requested artifacts in your workspace and report concrete evidence. '
                 'Do not read outside your workspace, use other agents, or inspect credentials. '
                 'If required information is absent, state the limitation precisely.')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshots(root):
    if not root or not Path(root).exists():
        return {}
    return {str(p.relative_to(root)): digest(p) for p in sorted(Path(root).rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts}


def events(path):
    values = []
    for line in path.read_text().split('\n') if path.exists() else []:
        try:
            values.append(json.loads(line))
        except ValueError:
            pass
    return values


def post_final_compaction(trace):
    """Recognize native final-stop output followed only by host maintenance."""
    final = None
    maintenance = False
    reply_index = -1
    for event_index, event in enumerate(trace):
        message = event.get('message', {})
        if event.get('type') == 'message_end' and message.get('role') == 'assistant':
            reply_index += 1
            content = message.get('content', [])
            tools = any(part.get('type') == 'toolCall' for part in content)
            text = '\n'.join(part.get('text', '') for part in content if part.get('type') == 'text')
            if tools:
                final = None
                maintenance = False
            elif message.get('stopReason') == 'stop' and text.strip():
                final = {'kind': 'post_final_compaction', 'reply_index': reply_index,
                         'event_index': event_index,
                         'text_sha256': hashlib.sha256(text.encode()).hexdigest()}
                maintenance = False
        elif event.get('type') == 'auto_compaction_start' and final:
            maintenance = True
    return final if maintenance else None


def stop_runner(proc, sig=signal.SIGTERM):
    """Stop this agent group while preserving any shared Splash daemon."""
    rows = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,pgid=,command='], text=True)
    processes = {}
    for row in rows.splitlines():
        fields = row.strip().split(None, 3)
        if len(fields) == 4:
            processes[int(fields[0])] = (int(fields[1]), int(fields[2]), fields[3])
    def is_splash(command):
        words = command.split()
        executable = Path(words[0]).name.lower() if words else ''
        if executable == 'splash':
            return len(words)>1 and words[1] in ['serve','serve-native']
        return executable.startswith('python') and any(
            '/libexec/server/server.py' in word or
            (Path(word).name=='splash' and index+1<len(words) and words[index+1]=='serve')
            for index,word in enumerate(words[:4]))
    protected = {pid for pid, (_, _, command) in processes.items() if is_splash(command)}
    changed = True
    while changed:
        changed = False
        for pid, (parent, _, _) in processes.items():
            if parent in protected and pid not in protected:
                protected.add(pid)
                changed = True
    targets = {pid for pid, (_, group, _) in processes.items() if group == proc.pid}
    for pid in sorted(targets - protected, reverse=True):
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass


def prepare(config):
    config = dict(config)
    record = Path(config['record']).resolve()
    workspace = Path(config['workspace']).resolve()
    record.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)
    if record == workspace:
        raise ValueError('Record directory and workspace must differ.')
    if workspace.is_relative_to(record):
        # The record may contain workspace/, but metadata/logs must remain OUTSIDE
        # the model-visible workspace, never the reverse.
        pass
    elif record.is_relative_to(workspace):
        raise ValueError('The record directory must be outside the model workspace.')
    if (record/'invocation.json').exists():
        raise ValueError('Existing run record; use a fresh record for every attempt.')
    config.update(record=str(record), workspace=str(workspace))
    config.setdefault('system_prompt', SYSTEM_PROMPT)
    config.setdefault('timeout_seconds', 180)
    config.setdefault('max_turns', 12)
    config.setdefault('max_tool_calls', 48)
    config.setdefault('max_output_tokens', 4096)
    config.setdefault('runtime_read_paths', [])
    config.setdefault('read_only_paths', [])
    config['harness_version']='hosted-nowhere-e2e-v1'
    config.setdefault('output_serialized_byte_limit',config.get('output_char_limit',24000))
    if config.get('skill_path'):
        skill_path = (workspace/config['skill_path']).resolve()
        if not skill_path.is_relative_to(workspace):
            raise ValueError('Skill snapshot must be inside the run workspace.')
        config['read_only_paths'] = list(set(config['read_only_paths'] + [str(skill_path)]))
    config['network_policy'] = 'tool-network-loopback-only'
    config['initial_snapshot'] = snapshots(workspace)
    config['harness_hashes'] = snapshots(HERE)
    (record/'run-config.json').write_text(json.dumps(config, indent=2)+'\n')
    (record/'prompt.md').write_text(config['prompt'])
    (record/'system-prompt.txt').write_text(config['system_prompt'])
    (record/'tools.jsonl').touch()
    return config, record, workspace


def adapter(config, record, workspace):
    runner = config['runner']
    system_flag = '--append-system-prompt' if config.get('native_system_context') else '--system-prompt'
    bun = config.get('bun', '/opt/homebrew/bin/bun')
    mcp = {'command': bun, 'args': [str(HERE/'mcp.mjs'), str(record/'run-config.json')]}
    env = os.environ.copy()
    if runner == 'omp':
        env['HOSTED_NOWHERE_RUN_CONFIG'] = str(record/'run-config.json')
        # Keep the user's SOMP launcher while giving this fresh run truthful
        # context/output limits. Never edit the user's global model settings.
        state = record/'omp-state'
        state.mkdir()
        env['PI_CODING_AGENT_DIR'] = str(state)
        (state/'models.yml').write_text("""providers:
  splash:
    baseUrl: http://127.0.0.1:8000/v1
    auth: none
    api: openai-completions
    models:
      - id: incoai/Qwen3.8-27B-Splash
        name: Qwen3.8 27B (Splash)
        contextWindow: 32768
        maxTokens: 4096
        reasoning: true
        thinking:
          mode: effort
          efforts: [low, medium, xhigh]
          defaultLevel: low
        compat:
          supportsReasoningEffort: true
          reasoningEffortMap: {low: low, medium: medium, xhigh: xhigh}
          thinkingFormat: qwen
          qwenTemplateReasoningEffort: true
        input: [text]
        compactionModel: splash/incoai/Qwen3.8-27B-Splash
""")
        (state/'config.yml').write_text("compaction:\n  enabled: true\n  methodOrder: [soft]\n  asyncEnabled: false\n  thresholdTokens: 22000\n  reserveTokens: 6000\n  keepRecentTokens: 6000\n")
        args = ['somp', '--thinking', config.get('thinking','low'), '--no-tools',
                '--no-skills', '--no-rules', '--no-extensions', '--no-lsp',
                '--no-title', '--no-session', '--mode', 'json', '--auto-approve',
                system_flag, config['system_prompt'],
                '-e', str(HERE/'somp-tools.ts'), '--max-time', str(config['timeout_seconds']),
                '-p', config['prompt']]
        return ['zsh','-lic',shlex.join(args)], env
    if runner == 'codex':
        state = record/'codex-state'
        state.mkdir()
        auth = Path.home()/'.codex/auth.json'
        if auth.exists():
            (state/'auth.json').symlink_to(auth)
        model = config.get('model', 'gpt-6-luna')
        disabled = sorted(str(p) for root in [Path.home()/'.agents/skills', Path.home()/'.codex/skills']
                          for p in root.glob('*/SKILL.md'))
        text = f'''model = {json.dumps(model)}
model_reasoning_effort = {json.dumps(config.get('thinking','high'))}
approval_policy = "never"
web_search = "disabled"
project_doc_max_bytes = 0
[features]
shell_tool = false
unified_exec = false
multi_agent = false
apps = false
plugins = false
hooks = false
browser_use = false
browser_use_external = false
computer_use = false
image_generation = false
in_app_browser = false
view_image = false
goals = false
memories = false
skill_search = false
skip_host_skill_discovery = true
code_mode_host = true
sleep_tool = false
[mcp_servers.benchmark]
command = {json.dumps(bun)}
args = {json.dumps(mcp['args'])}
required = true
enabled_tools = ["read", "write", "bash"]
startup_timeout_sec = 20
tool_timeout_sec = 200
[mcp_servers.benchmark.tools.read]
approval_mode = "approve"
[mcp_servers.benchmark.tools.write]
approval_mode = "approve"
[mcp_servers.benchmark.tools.bash]
approval_mode = "approve"
[skills]
max_context_tokens = 1
config = [{','.join('{path='+json.dumps(p)+',enabled=false}' for p in disabled)}]
'''
        (state/'config.toml').write_text(text)
        # The auth symlink is transport state. It is outside all exposed tools.
        env['CODEX_HOME'] = str(state)
        command = [config.get('executable', 'codex'), 'exec', '--json', '--ignore-rules',
                   '--skip-git-repo-check', '--color', 'never', '-s', 'workspace-write',
                   '-m', model, '-c', 'model_reasoning_effort='+json.dumps(config.get('thinking','high')),
                   '-C', str(workspace), '-o', str(record/'response.md'), '-']
        return command, env
    if runner == 'claude':
        mcp_path = record/'mcp-config.json'
        mcp_path.write_text(json.dumps({'mcpServers': {'benchmark': mcp}}, indent=2)+'\n')
        env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] = '1'
        env['CLAUDE_CODE_DISABLE_CLAUDE_MDS'] = '1'
        env['CLAUDE_CODE_DISABLE_BUNDLED_SKILLS'] = '1'
        env['CLAUDE_CODE_DISABLE_ORG_MEMORY'] = '1'
        env['CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC'] = '1'
        # --safe-mode also suppresses explicit MCP servers, so combine the
        # narrower no-CLAUDE.md/no-skills switches with restricted settings.
        command = [config.get('executable','claude'), '-p', '--model', config.get('model','haiku'),
                   '--output-format','stream-json','--verbose', '--no-session-persistence',
                   '--restricted','--setting-sources','', '--disable-slash-commands',
                   '--settings',json.dumps({'disableAllHooks':True,'disableBundledSkills':True,'enabledPlugins':{}}),
                   '--strict-mcp-config','--mcp-config',str(mcp_path), '--tools','',
                   '--allowedTools','mcp__benchmark__read,mcp__benchmark__write,mcp__benchmark__bash',
                   system_flag,config['system_prompt'], '--max-turns',str(config['max_turns'])]
        if config.get('thinking'):
            command += ['--effort',config['thinking']]
        return command, env
    raise ValueError('runner must be codex, claude or omp')


def collect(config, record, code, seconds, timed_out, tool_limit):
    trace = events(record/'stdout.jsonl')
    result = dict(runner=config['runner'], model=config['model'], thinking=config.get('thinking'),
                  harness_version=config.get('harness_version'),actual_context_window=config.get('actual_context_window'),
                  output_serialized_byte_limit=config.get('output_serialized_byte_limit'),
                  seconds=seconds, exit_code=code, normal_completion=code==0 and not timed_out,
                  timed_out=timed_out, tool_limit_reached=tool_limit,
                  prompt_sha256=digest(record/'prompt.md'), system_prompt_sha256=digest(record/'system-prompt.txt'),
                  system_prompt_mode=('native_with_user_prefix' if config['runner']=='codex' else
                      'native_plus_custom' if config.get('native_system_context') else 'custom_replacement'),
                  network_policy=config['network_policy'], tools=len(events(record/'tools.jsonl')),
                  usage=None, errors=[], artifact_hashes=snapshots(config['workspace']))
    if config['runner']=='codex':
        completed=[e.get('usage') for e in trace if e.get('type')=='turn.completed']
        errors=[e for e in trace if e.get('type') in ['error','turn.failed']]
        result.update(completed_turn_usage=completed,errors=errors,
                      usage_is_lower_bound=not completed or bool(errors) or timed_out)
        if completed:
            sums={k:sum(u[k] for u in completed) if all(u.get(k) is not None for u in completed) else None
                  for k in ['input_tokens','cached_input_tokens','output_tokens']}
            reasoning=[u.get('reasoning_output_tokens') for u in completed]
            sums['reasoning_tokens']=sum(reasoning) if all(x is not None for x in reasoning) else None
            sums['total_tokens']=sums['input_tokens']+sums['output_tokens'] if all(sums[k] is not None for k in ['input_tokens','output_tokens']) else None
            sums['uncached_input_plus_output']=sums['total_tokens']-sums['cached_input_tokens'] if sums['total_tokens'] is not None and sums['cached_input_tokens'] is not None else None
            if any(sums[k] is None for k in ['input_tokens','cached_input_tokens','output_tokens']):
                result['usage_is_lower_bound']=True
            result['usage']=sums
        steps=[];seen=set();context=[]
        for rollout in (record/'codex-state/sessions').rglob('*.jsonl'):
            for entry in events(rollout):
                payload=entry.get('payload',{})
                if entry.get('type')=='event_msg' and payload.get('type')=='token_count':
                    info=payload.get('info') or {};total=info.get('total_token_usage')
                    key=json.dumps(total,sort_keys=True)
                    if total and key not in seen:
                        seen.add(key);steps.append({'at':entry.get('timestamp'),'last_token_usage':info.get('last_token_usage'),'cumulative_token_usage':total})
                if entry.get('type')=='response_item' and payload.get('type')=='message' and payload.get('role') in ['developer','user']:
                    text='\n'.join(c.get('text','') for c in payload.get('content',[]))
                    context.append({'role':payload['role'],'text':text})
        actual_models=set()
        for rollout in (record/'codex-state/sessions').rglob('*.jsonl'):
            for entry in events(rollout):
                if entry.get('type')=='turn_context' and entry.get('payload',{}).get('model'):
                    actual_models.add(entry['payload']['model'])
        result['actual_models']=sorted(actual_models)
        result['provider_step_usage']=steps
        (record/'context-audit.json').write_text(json.dumps(context,indent=2)+'\n')
        result['no_context']={'ambient_skill_catalog_entries':0 if any('### Available skills\n</skills_instructions>' in c['text'] for c in context) else None,
                              'parent_history_inherited':False,'fresh_state_directory':True,
                              'generic_cli_system_instructions_retained':True,'shared_prompt_placement':'initial user message prefix'}
    elif config['runner']=='claude':
        terminal=next((e for e in reversed(trace) if e.get('type')=='result'),None)
        initial=next((e for e in trace if e.get('type')=='system' and e.get('subtype')=='init'),None)
        result['initial_tool_inventory']=initial.get('tools') if initial else None
        result['isolation_inventory_passed']=bool(initial) and set(initial.get('tools',[]))=={
            'mcp__benchmark__read','mcp__benchmark__write','mcp__benchmark__bash'} and not initial.get('skills')
        if terminal:
            result['actual_models']=sorted(terminal.get('modelUsage',{}))
            usage=terminal.get('usage')
            result.update(provider_result=terminal,usage_is_lower_bound=bool(terminal.get('is_error')) or timed_out)
            if usage:
                uncached=usage.get('input_tokens',0); cached=usage.get('cache_read_input_tokens',0)
                written=usage.get('cache_creation_input_tokens',0); output=usage.get('output_tokens',0)
                result['usage']={'input_tokens':uncached+cached+written,'uncached_input_tokens':uncached,
                    'cached_input_tokens':cached,'cache_write_tokens':written,'output_tokens':output,
                    'reasoning_tokens':usage.get('output_tokens_details',{}).get('thinking_tokens'),
                    'total_tokens':uncached+cached+written+output,'uncached_input_plus_output':uncached+written+output}
            (record/'response.md').write_text(terminal.get('result','')+'\n')
            if terminal.get('is_error'):
                result['errors'].append(terminal.get('result'))
    else:
        replies=[e['message'] for e in trace if e.get('type')=='message_end' and e.get('message',{}).get('role')=='assistant']
        marker_path=record/'controller-completion.json'
        marker=json.loads(marker_path.read_text()) if marker_path.exists() else None
        detected=post_final_compaction(trace)
        if marker and detected and all(marker.get(key)==value for key,value in detected.items()):
            result['controller_completion']=marker
            result['normal_completion']=not timed_out and not tool_limit
            result['post_completion_errors']=[m.get('errorMessage') or m.get('stopReason')
                for m in replies[detected['reply_index']+1:] if m.get('stopReason') in ['error','aborted']]
            replies=replies[:detected['reply_index']+1]
        result['actual_models']=sorted(set(m.get('provider','')+'/'+m.get('model','') for m in replies))
        result['errors']=[m.get('errorMessage') or m.get('stopReason') for m in replies if m.get('stopReason') in ['error','aborted']]
        result['usage']={key:sum((m.get('usage') or {}).get(key,0) for m in replies) for key in ['input','output','cacheRead','cacheWrite','totalTokens']}
        result['usage_is_lower_bound']=bool(result['errors']) or timed_out or bool(result.get('controller_completion'))
        final=replies[-1] if replies else {}
        (record/'response.md').write_text('\n'.join(c.get('text','') for c in final.get('content',[]) if c.get('type')=='text')+'\n')
    result['frozen_paths_unchanged'] = all(
        digest(Path(config['workspace'])/p)==h for p,h in config['initial_snapshot'].items()
        if any((Path(config['workspace'])/p).is_relative_to((Path(config['workspace'])/r).resolve())
               for r in config.get('read_only_paths',[])))
    result['collector_sha256']=digest(__file__)
    (record/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    config, record, workspace = prepare(json.loads(Path(sys.argv[1]).read_text()))
    command, env = adapter(config,record,workspace)
    (record/'invocation.json').write_text(json.dumps(command,indent=2)+'\n')
    prompt = config['prompt']
    if config['runner']=='codex':
        prompt=config['system_prompt']+'\n\n'+prompt
    start=time.monotonic(); timed_out=False; tool_limit=False; next_terminal_poll=0
    with (record/'stdout.jsonl').open('w') as output,(record/'stderr.txt').open('w') as errors:
        proc=subprocess.Popen(command,cwd=workspace,env=env,stdin=subprocess.PIPE,
                              stdout=output,stderr=errors,start_new_session=True)
        (record/'pid').write_text(str(proc.pid)+'\n')
        if config['runner']!='omp':
            proc.stdin.write(prompt.encode())
        proc.stdin.close()
        while proc.poll() is None:
            if config['runner']=='omp' and time.monotonic()>=next_terminal_poll:
                next_terminal_poll=time.monotonic()+1
                completed=post_final_compaction(events(record/'stdout.jsonl'))
                if completed:
                    completed['observed_at_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
                    (record/'controller-completion.json').write_text(json.dumps(completed,indent=2)+'\n')
                    stop_runner(proc)
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        stop_runner(proc,signal.SIGKILL);proc.wait()
                    break
            if time.monotonic()-start>config['timeout_seconds']+10:
                timed_out=True
            tool_limit=len(events(record/'tools.jsonl'))>=config['max_tool_calls']
            if timed_out or tool_limit:
                stop_runner(proc)
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    stop_runner(proc,signal.SIGKILL);proc.wait()
                break
            time.sleep(.2)
    result=collect(config,record,proc.returncode,time.monotonic()-start,timed_out,tool_limit)
    print(json.dumps({k:result[k] for k in ['runner','model','seconds','exit_code','timed_out','tool_limit_reached','usage','errors']}))


if __name__=='__main__':
    main()
