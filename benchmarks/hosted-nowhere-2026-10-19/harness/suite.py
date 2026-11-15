#!/usr/bin/env python3
"""Fresh-session acceptance runner. Raw traces stay outside model workspaces."""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import os
import re
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import time
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[1]
NPM_CACHE = Path('/private/tmp/freedom-skills-npx-cache')
OMP_ROOT = Path('/Users/brenorb/.nvm/versions/node/v24.21.0/lib/node_modules/@oh-my-pi/pi-coding-agent')
NODE_ROOT = OMP_ROOT.parents[3]
RUNS = Path('/private/tmp/hosted-nowhere-e2e/runs')
CLI_COMMAND = ['npx','--yes','nowhere-cli@0.3.0']
MODEL_CONFIG = {
    'luna': {'runner':'codex','model':'gpt-6-luna','thinking':'high'},
    'haiku': {'runner':'claude','model':'haiku'},
    'qwen': {'runner':'omp','model':'splash/incoai/Qwen3.8-27B-Splash','thinking':'low','timeout_seconds':3600},
}
SYSTEM = '''Complete the assigned user story using the supplied workspace tools.
Read the skill at skill/SKILL.md and only the references relevant to this task.
Work independently in this workspace. Do not inspect credentials, other runs,
graders, or files outside this workspace. Do not use other agents, publish to
public relays, send real messages/payments, install packages globally, or change
the frozen skill/fixtures. All identities and services here are disposable tests.
Treat provided secret/private-key values as private inputs even in these tests.
Do not copy them into human-facing reports or command examples; use public
identifiers and variable placeholders. Keep reports brief and limited to observed
outcomes, explicitly marking anything unverified. Extra documentation is not needed.
Use the configured local relay from fixtures/context.json for relay operations.
Tool subprocess networking is loopback-only and npm uses a prewarmed offline
cache. The browser loads the live Hosted Nowhere pages, but this test environment
blocks public WebSocket relay connections; local relay connections are permitted.
For browser interaction use `python3 browser.py` (read its help/docstring first).
It drives real isolated Chrome and returns observable page state. It supports
goto URL, snapshot, fill SELECTOR VALUE, click SELECTOR, select SELECTOR VALUE,
and screenshot OUTPUT.png. Observe controls before acting; use the exact final
URL for verification. The production app may show warnings; read them.
Node's test network boundary maps fixture.test to a local fake LNURL provider;
its TEST_ONLY invoices must never be described as real invoices or payments.
Save the requested real command outputs under the requested names. Include the
final share URL and verification account in your final response. Write result.json
only when the story explicitly requests it. Do not claim unverified success. If a tool fails, diagnose and recover within the
story's scope, keeping the actual failures. Execute commands directly rather than
only describing what a user could run. Finish with a concise evidence report.'''


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def skill_hash():
    digest = hashlib.sha256()
    for path in sorted((REPO/'skills/hosted-nowhere').rglob('*')):
        if path.is_file():
            digest.update(str(path.relative_to(REPO/'skills/hosted-nowhere')).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def cli(*args):
    proc = subprocess.run([*CLI_COMMAND,*args,'--json'], capture_output=True,
                          text=True, timeout=120, env={**os.environ,
                          'npm_config_cache':str(NPM_CACHE),'npm_config_offline':'true'})
    if proc.returncode:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def make_fixtures(work):
    fixtures=work/'fixtures';fixtures.mkdir()
    owner=cli('pubkey','--secret','1'*64)
    author=cli('pubkey','--secret','2'*64)
    recipient=cli('pubkey','--secret','3'*64)
    context={'owner':{**owner,'secret':'1'*64},'author':{**author,'secret':'2'*64},
             'recipient':{**recipient,'secret':'3'*64},'password':'test-link-password',
             'lightningAddress':'tips@fixture.test','customHandle':'example.com/community'}
    dump(fixtures/'context.json',context)
    # A real bencoded single-file torrent, with a genuine SHA-1 piece hash.
    content=b'public test document\n'
    piece=hashlib.sha1(content).digest()
    info=b'd6:lengthi'+str(len(content)).encode()+b'e4:name11:archive.txt12:piece lengthi16384e6:pieces20:'+piece+b'e'
    (fixtures/'archive.torrent').write_bytes(b'd4:info'+info+b'e')
    (fixtures/'broken.json').write_text('{"name":"Sender", "tags":[{"key":"t","value":"Dispatch"}]')
    (fixtures/'corrupted-url.txt').write_text('https://hostednowhere.com/s#not-a-valid-fragment')
    shutil.copy2(HERE/'browser.py',work/'browser.py')
    shutil.copy2(HERE/'network.mjs',fixtures/'network.mjs')
    return context


def create_input(work, app, payload, filename, *options):
    path=work/'fixtures'/filename
    dump(path,payload)
    return cli('create',app,'--input',str(path),*options)


def start_services(record, work):
    paths=list(NPM_CACHE.glob('_npx/*/node_modules/nowhere-cli/dist/cli.js'))
    if not paths:
        raise RuntimeError('Warm the npx cache with nowhere-cli@0.3.0 first')
    config={'cli_entrypoint':str(paths[0]),'omp_root':str(OMP_ROOT),
            'chrome':'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            'workspace':str(work),'record':str(record)}
    dump(record/'services-config.json',config)
    error_file=(record/'services.stderr').open('w')
    process=subprocess.Popen(['node',str(HERE/'services.mjs'),str(record/'services-config.json')],
                             stdout=subprocess.PIPE,stderr=error_file,text=True,start_new_session=True)
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        if not selector.select(timeout=20):
            process.terminate();raise RuntimeError('Local service startup timeout')
    line=process.stdout.readline()
    if not line:
        raise RuntimeError((record/'services.stderr').read_text())
    return process,error_file,json.loads(line)


def prepare(story, model, batch):
    record=RUNS/batch/model/story['id'];work=record/'workspace'
    if record.exists():
        raise ValueError(f'Fresh run required: {record} exists')
    work.mkdir(parents=True)
    frozen=RUNS/batch/'skill-snapshot'
    shutil.copytree(frozen if frozen.exists() else REPO/'skills/hosted-nowhere',work/'skill')
    context=make_fixtures(work)
    service,error_file,services=start_services(record,work)
    context.update({'relay':services['relay'],'rejectingRelay':services['relay'].replace('/relay','/reject'),
                    'unavailableRelay':'ws://127.0.0.1:1','services':services['origin']})
    if story['id']=='N18':context['bunker']=services['bunker']
    dump(work/'fixtures/context.json',context)
    if 'expected_body' in story:
        (work/'fixtures/requested-text.txt').write_text(story['expected_body'])
    if story['id'] in ['N11','N12']:
        payload={'name':'Protected original' if story['id']=='N11' else 'Unsigned dispatch',
                 'description':'Keep this body unchanged.','pubkey':context['owner']['npub'],
                 'tags':[{'key':'t','value':'Original title'}]}
        options=['--sign-secret',context['owner']['secret'],'--encrypt-password',context['password']] if story['id']=='N11' else []
        built=create_input(work,'message',payload,'protected-input.json',*options)
        (work/'fixtures'/('protected-url.txt' if story['id']=='N11' else 'unsigned-url.txt')).write_text(built['url'])
    if story['id']=='N13':
        payload={'name':'Original poster','description':'Keep this description.',
                 'image':'https://example.com/original.png','pubkey':context['owner']['npub'],
                 'tags':[{'key':'T','value':'g'},{'key':'o','value':'alice'},{'key':'l','value':'https://example.com/details'}]}
        built=create_input(work,'event',payload,'array-input.json')
        (work/'fixtures/array-url.txt').write_text(built['url'])
    if story['id']=='N15':
        built=create_input(work,'forum',{'name':'Failure Board','pubkey':context['owner']['npub'],
              'tags':[{'key':'1','value':services['relay']}]},'forum-input.json')
        (work/'fixtures/forum-url.txt').write_text(built['url'])
    prompt=story['task']+'\n\nUse the assigned skill at skill/SKILL.md. Raw input identities and service endpoints are in fixtures/context.json.'
    if 'expected_body' in story:
        prompt+=' The authoritative requested body is also supplied verbatim in fixtures/requested-text.txt.'
    config={**MODEL_CONFIG[model],'actual_context_window':32768 if model=='qwen' else None,'record':str(record),'workspace':str(work),'prompt':prompt,
            'system_prompt':SYSTEM,'skill_path':'skill','internet':True,'timeout_seconds':MODEL_CONFIG[model].get('timeout_seconds',900),
            'max_turns':120,'max_tool_calls':180,'max_output_tokens':8192,
            'runtime_read_paths':[str(NODE_ROOT),'/opt/homebrew',str(NPM_CACHE)],
            'runtime_write_paths':[str(NPM_CACHE)],
            'tool_paths':[str(NODE_ROOT/'bin'),'/opt/homebrew/bin'],
            'read_only_paths':[str(work/'fixtures'),str(work/'browser.py')],
            'tool_env':{'npm_config_cache':str(NPM_CACHE),'npm_config_offline':'true',
                        'XDG_CONFIG_HOME':str(work/'config'),
                        'NODE_OPTIONS':'--import='+str(work/'fixtures/network.mjs'),
                        'E2E_SERVICES_URL':services['origin']}}
    dump(record/'launch-config.json',config)
    dump(record/'story.json',story)
    batch_hash=RUNS/batch/'skill.sha256'
    (record/'skill.sha256').write_text(batch_hash.read_text() if batch_hash.exists() else skill_hash()+'\n')
    return record,work,config,service,error_file


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def private_report_issues(record, work):
    """Check known fixture private scalars in human-facing reports, not CLI inputs."""
    ctx=read_json(work/'fixtures/context.json',{})
    secrets={v['secret'] for v in ctx.values() if isinstance(v,dict)
             and isinstance(v.get('secret'),str) and re.fullmatch(r'[0-9a-fA-F]{64}',v['secret'])}
    paths=[record/'response.md']+[
        p for p in work.iterdir() if p.is_file() and
        (p.suffix.lower() in ['.md','.txt'] or p.name=='result.json')]
    issues=[]
    for path in paths:
        if not path.exists():continue
        label='response.md' if path==record/'response.md' else 'workspace/'+path.name
        if path!=record/'response.md' and not path.resolve().is_relative_to(work.resolve()):
            issues.append('Report path escapes workspace: '+label);continue
        if any(secret in path.read_text(errors='replace') for secret in secrets):
            issues.append('Private fixture key value in human-facing report: '+label)
    return issues


def grade(story,record,work):
    errors=[];evidence={}
    def check(condition,reason):
        if not condition:errors.append(reason)
    def artifact(name):
        try:value=read_json(work/name)
        except (ValueError,OSError) as error:
            check(False,'Malformed '+name+': '+str(error));return {}
        check(value is not None,'Missing '+name)
        if isinstance(value,dict) and isinstance(value.get('stdout'),str):
            try:
                nested=json.loads(value['stdout'])
                if isinstance(nested,dict):
                    check(value.get('exit_code',0)==0,'Nonzero command status in '+name)
                    value=nested
            except ValueError:pass
        if value is not None and not isinstance(value,dict):
            check(False,'Expected a JSON object in '+name);return {}
        return value or {}
    result=artifact('result.json') if story['id']=='N16' else read_json(work/'result.json',{})
    metrics=read_json(record/'metrics.json',{})
    check(metrics.get('normal_completion',metrics.get('exit_code')==0),'Runner did not complete normally')
    check(not metrics.get('timed_out'),'Runner timed out')
    check(not metrics.get('errors'),'Runner reported an inference error')
    check(metrics.get('frozen_paths_unchanged'),'Frozen skill/fixtures were changed')
    if metrics.get('runner')=='claude':
        check(metrics.get('isolation_inventory_passed') is True,'Claude inherited ambient tools or skills')
    privacy_issues=private_report_issues(record,work)
    errors.extend(privacy_issues)
    evidence['private_report_scan']={'pass':not privacy_issues,'issues':privacy_issues}
    journal=read_json(record/'relay-events.json',[])
    browser=read_json(record/'browser.json',[])
    def accepted_event(event):
        return isinstance(event,dict) and bool(event.get('id')) and any(entry['accepted'] and entry['event']==event for entry in journal)
    if story['id']!='N15':
        final=artifact('final.json') if story['id']!='N16' else result
        if story['id'] in ['N01','N02','N04','N12','N13']:
            check(any(key in final for key in ['siteData','site','signedFragment']),'Requested CLI output is missing from final.json')
        def share_fragment(value):
            if not isinstance(value,str):return None
            parsed=urlsplit(value)
            return parsed.fragment if parsed.scheme=='https' and parsed.hostname in ['hostednowhere.com','nowhr.xyz'] and parsed.path=='/s' else None
        def strings(value):
            if isinstance(value,str):yield value
            elif isinstance(value,dict):
                for child in value.values():yield from strings(child)
            elif isinstance(value,list):
                for child in value:yield from strings(child)
        def saved_url(data):
            explicit=data.get('url') or data.get('signedUrl') or data.get('encryptedUrl')
            candidates=[value for value in strings(data) if share_fragment(value)]
            # Metadata may nest its URL. Without an explicit CLI URL, require
            # one unambiguous fragment rather than guessing between versions.
            return explicit or (candidates[0] if len({share_fragment(value) for value in candidates})==1 else None)
        url=result.get('url') or saved_url(final)
        input_artifact = not url and ((story['id']=='N14' and final.get('name')=='Sender' and final.get('tags')==[{'key':'t','value':'Dispatch'}] and not final.get('description')) or (story['id']=='N03' and final.get('name')==story['expected_name'] and all(value in final.get('description','') for value in story['body_contains'])))
        if not url and input_artifact:
            # These stories request JSON without prescribing CLI-output schema.
            # Bind the delivered link to the actual observed page, independently
            # decode it, and below compare the saved input against that payload.
            delivered=re.findall(r'https://(?:hostednowhere\.com|nowhr\.xyz)/s#[A-Za-z0-9_-]+',(record/'response.md').read_text())
            matches=[value for value in delivered if any(share_fragment(entry['observed'].get('url'))==share_fragment(value) and story['expected_name'] in (entry['observed'].get('text','')+' '+entry['observed'].get('title','')) for entry in browser)]
            valid=[]
            for candidate in dict.fromkeys(matches):
                try:
                    summary=cli('inspect',candidate)['site']
                    if summary.get('name')==story['expected_name'] and summary.get('siteType')==story['app']:
                        valid.append(candidate)
                except (RuntimeError,KeyError,ValueError):
                    pass
            url=valid[0] if len({share_fragment(value) for value in valid})==1 else None
        check(share_fragment(url) is not None,'No final share URL on an approved renderer')
        delivered_urls=re.findall(r'https://(?:hostednowhere\.com|nowhr\.xyz)/s#[A-Za-z0-9_-]+',(record/'response.md').read_text())
        check(any(share_fragment(value)==share_fragment(url) for value in delivered_urls),'Final response did not deliver the exact saved final URL')
        if final.get('url') or final.get('signedUrl'):
            check(share_fragment(final.get('url') or final.get('signedUrl'))==share_fragment(url),'Final output and delivered URL differ')
        if not isinstance(url,str):return {'pass':False,'errors':errors}
        ctx=read_json(work/'fixtures/context.json')
        options=['--password',ctx['password']] if story['id']=='N11' else []
        try:
            inspected=cli('inspect',url,*options)
            evidence['site']=inspected['site']
            check(inspected['site']['siteType']==('discussion' if story['app']=='forum' else story['app']),'Wrong decoded app')
            check(inspected['site']['name']==story['expected_name'],'Wrong final name')
            if story['id'] in ['N06','N07','N10','N11','N12','N13','N18']:
                check(inspected['site'].get('pubkeyHex')==ctx['owner']['pubkeyHex'],'Intended owner public key was not preserved')
            patch=work/'oracle-empty-patch.json';dump(patch,{})
            decoded=cli('update',url,'--patch',str(patch),*options)['siteData']
            if input_artifact:
                check(all(decoded.get(key)==value for key,value in final.items() if key!='tags'),'Saved JSON input differs from final decoded payload')
                check(all(tag in decoded.get('tags',[]) for tag in final.get('tags',[])),'Saved input tags differ from final decoded payload')
            body=decoded.get('description') or next((t.get('value','') for t in decoded.get('tags',[]) if t['key']=='b'),'')
            if 'expected_body' in story:
                check(body in (['Remote signer test','Remote signer test.'] if story['id']=='N18' else [story['expected_body']]),'Body was changed or lost')
            for text in story.get('body_contains',[]):
                check(text in body,'Missing event detail '+text)
            observations=[entry['observed'] for entry in browser if share_fragment(entry['observed'].get('url'))==share_fragment(url)]
            check(bool(observations),'Final fragment was not opened on an approved renderer in the browser')
            check(any(story['expected_name'] in (entry.get('text','')+' '+entry.get('title','')) for entry in observations),'Browser did not show the final name')
            if 'expected_body' in story:
                # The Drop renderer inserts visible line numbers between code
                # lines. Verify each requested line appears in order; exact
                # bytes/newlines are checked independently by CLI decoding.
                def rendered_body(entry):
                    visible=' '.join(entry.get('text','').split());offset=0
                    if story['app']=='event':visible=visible.casefold()
                    for line in (body if story['id']=='N18' else story['expected_body']).splitlines():
                        wanted=' '.join(line.split())
                        if story['app']=='event':wanted=wanted.casefold()
                        if not wanted:continue
                        found=visible.find(wanted,offset)
                        if found<0:return False
                        offset=found+len(wanted)
                    return True
                check(any(rendered_body(entry) for entry in observations),'Browser did not show the requested final body')
            for text in story.get('body_contains',[]):
                check(any(text.casefold() in entry.get('text','').casefold() for entry in observations),'Event detail was not rendered: '+text)
            if story['id']=='N06':
                evidence['petition_hash']=hashlib.sha256((inspected.get('unsignedFragment') or inspected['decodedFragment']).encode()).hexdigest()[:16]
                tags={tag['key']:tag.get('value') for tag in decoded['tags']}
                check('N' in tags and 'E' in tags and tags.get('c')=='BR','Required petition fields or country constraint missing')
            if story['id']=='N10':
                check(len(decoded.get('items',[]))==1 and decoded['items'][0].get('name')=='Sticker Pack' and decoded['items'][0].get('price')==7.5,'Requested Store item name or catalogue price differs')
            if story['id']=='N01':
                original=artifact('original.json').get('siteData',{})
                check(original.get('name')=='Signal Hill Dispatch' and original.get('description')==story['expected_body'],'Original message output missing or incorrect')
                check(any(tag['key']=='t' and tag.get('value')=="Tonight's meeting" for tag in decoded['tags']),'Original message title was changed')
            if story['id']=='N05':
                svg=ET.fromstring(decoded.get('svg',''))
                check(svg.get('viewBox')=='0 0 100 100','Wrong SVG viewBox')
                check(any(element.tag.rsplit('}',1)[-1]=='circle' and all(element.get(key)==value for key,value in {'cx':'50','cy':'50','r':'40','fill':'#ff6600'}.items()) for element in svg.iter()),'Requested circle geometry or color missing')
                check((work/'art.png').is_file(),'No art screenshot')
            if story['id']=='N11':
                verified=artifact('verify.json')
                check(inspected['signed'] and verified.get('signed') is True,'Updated signature missing')
                check(inspected['signaturePubkeyHex']==ctx['owner']['pubkeyHex'],'Wrong signer')
                check(decoded.get('tags')==read_json(work/'fixtures/protected-input.json')['tags'],'Protected update changed unrelated title tags')
                failed=subprocess.run([*CLI_COMMAND,'inspect',url,'--json'],capture_output=True,text=True,
                    env={**os.environ,'npm_config_cache':str(NPM_CACHE),'npm_config_offline':'true'})
                check(failed.returncode!=0,'Final link lost encryption')
            if story['id']=='N12':
                check(artifact('initial-verify.json').get('signed') is False,'Unsigned state not demonstrated')
                check(artifact('verify.json').get('signaturePubkeyHex')==ctx['owner']['pubkeyHex'],'Correct final signer not verified')
            if story['id']=='N18':
                check(artifact('connect.json').get('connected') is True,'Remote signer did not connect')
                original=artifact('original.json')
                original_url=saved_url(original)
                original_verified=cli('verify',original_url) if isinstance(original_url,str) else {}
                original_data=cli('update',original_url,'--patch',str(patch))['siteData'] if isinstance(original_url,str) else {}
                check(original_data.get('description')==body,'Remote update changed the originally created body')
                check(original_verified.get('signed') is True and original_verified.get('signaturePubkeyHex')==ctx['owner']['pubkeyHex'],'Original creation was not signed by the intended owner')
                rpc_path=record/'signer-rpc.jsonl'
                requests=[json.loads(line) for line in rpc_path.read_text().splitlines() if line.strip()] if rpc_path.exists() else []
                check(sum(request.get('method')=='sign_event' for request in requests)>=2,'Remote signer did not sign both creation and update')
                verified=artifact('verify.json')
                check(verified.get('signed') is True and verified.get('signaturePubkeyHex')==ctx['owner']['pubkeyHex'],'Remote signature identity mismatch')
                check(inspected.get('signed') is True,'Final remote-signed URL independently verifies as unsigned')
                check(artifact('disconnected.json').get('connected') is False,'Test signer session was not disconnected')
            if story['id']=='N13':
                tags={t['key']:t.get('value') for t in decoded['tags']}
                check(tags.get('T')=='u' and tags.get('o')=='alice' and tags.get('l')=='https://example.com/details','Array patch lost unrelated tags')
                check(not decoded.get('image'),'Image was not removed')
                check(decoded.get('pubkey')==ctx['owner']['nowherePubkey'],'Author key changed')
            if story['id']=='N14':
                check(not decoded.get('description'),'Invented a body for title-only request')
                check(any(t['key']=='t' and t.get('value')=='Dispatch' for t in decoded['tags']),'Lost title')
            evidence['url']=url
        except Exception as error:errors.append('Independent decode/verification: '+str(error)[:1500])
    else:
        check((work/'failure.txt').is_file() and bool((work/'failure.txt').read_text().strip()),'Missing actual failure details')
        check(artifact('posts.json').get('posts')==[],'Read check not empty as expected')
        check(len(journal)==1 and not journal[0]['accepted'],'Rejected publish was retried or not exercised')
    if story.get('invoice_sats'):
        methods=artifact('methods.json');invoice=artifact('invoice.json')
        indexed={entry.get('id'):entry for entry in methods.get('methods',[])}
        check(indexed.get('lightning',{}).get('value')=='tips@fixture.test','Lightning destination missing or wrong')
        expected_custom='example.com/reader' if story['id']=='N17' else 'example.com/community'
        check(indexed.get('custom_0',{}).get('label')=='PayPal' and indexed.get('custom_0',{}).get('value')==expected_custom,'Custom payment method missing or wrong')
        check(invoice.get('invoice')=='lnbc_TEST_ONLY_'+str(story['invoice_sats']*1000),'Wrong test invoice amount or no actual provider response')
        requests=read_json(record/'service-requests.json',[])
        check(sum(r['path']=='/invoice' for r in requests)==1,'Invoice request absent or retried')
    if story['id']=='N06':
        signature=artifact('signature.json')
        expected_hash=evidence.get('petition_hash');expected_dtag='nowhr/'+str(expected_hash)
        check(all(artifact(name).get('petitionHash')==expected_hash and artifact(name).get('dTag')==expected_dtag for name in ['signature.json','count.json','owner.json']),'Petition response/count/export namespace differs from final link')
        check(all(any(tag==['d',expected_dtag] for tag in entry['event']['tags']) for entry in journal if entry['accepted']),'Accepted signature belongs to another petition URL')
        check(any(entry['accepted'] and entry['event']==signature.get('event') and entry['event'].get('pubkey')==ctx['author']['pubkeyHex'] for entry in journal),'Saved signature output does not identify the authorized signer event')
        check(artifact('count.json').get('count')==1,'Petition count differs from one accepted signer')
        owner=artifact('owner.json')
        check(any(x.get('payload',{}).get('email')=='alex@example.com' for x in owner.get('signatures',[]) if x.get('payload')),'Owner did not decrypt signer payload')
        signer_rows=list(csv.DictReader(io.StringIO((work/'owner.csv').read_text()))) if (work/'owner.csv').exists() else []
        check(len(signer_rows)==1 and signer_rows[0].get('Name')=='Alex' and signer_rows[0].get('Email')=='alex@example.com' and signer_rows[0].get('Country')=='BR','Signer CSV is missing or differs from accepted signer')
        check(len([e for e in journal if e['accepted']])==1,'Expected exactly one accepted signature on the assigned relay; observed '+str(len([e for e in journal if e['accepted']])))
    if story['id']=='N07':
        post=artifact('post.json');reply=artifact('reply.json')
        posts=artifact('posts.json');replies=artifact('replies.json')
        check(accepted_event(post.get('event')) and accepted_event(reply.get('event')),'Saved post/reply event differs from relay bytes')
        check('Meeting at seven' in json.dumps(posts),'Post not read back')
        check('Acknowledged' in json.dumps(replies),'Reply not read back')
        check(any(entry.get('eventId')==post.get('event',{}).get('id') and entry.get('payload',{}).get('p')==ctx['owner']['pubkeyHex'] for entry in posts.get('posts',[])),'Read-back post ID or author differs from the requested owner event')
        check(any(entry.get('eventId')==reply.get('event',{}).get('id') for entry in replies.get('replies',[])),'Read-back reply ID differs from published event')
        check(artifact('isolated.json').get('posts')==[],'Salt isolation failed')
        wot=artifact('wot.json')
        check(wot.get('allowed') is True,'Owner was not allowed by the WoT check')
        check(len([x for x in journal if x['accepted']])==2,'Expected exactly one post and one reply')
    if story['id']=='N08':
        for name in ['parsed.json','preflight.json','torrent.json','torrents.json','duplicate.json','torrent-reply.json','torrent-replies.json']:artifact(name)
        check('Archived' in json.dumps(artifact('torrent-replies.json')),'Torrent reply not read back')
        check(accepted_event(artifact('torrent.json').get('event')) and accepted_event(artifact('torrent-reply.json').get('event')),'Saved torrent/reply event differs from relay bytes')
        raw=(work/'fixtures/archive.torrent').read_bytes()
        expected_infohash=hashlib.sha1(raw[len(b'd4:info'):-1]).hexdigest()
        check(artifact('parsed.json').get('infohash')==expected_infohash,'Parsed torrent differs from provided file')
        check(any(entry.get('torrentData',{}).get('x')==expected_infohash and entry.get('torrentData',{}).get('category')=='docs' for entry in artifact('torrents.json').get('torrents',[])),'Read-back torrent file or category differs')
        check(artifact('preflight.json').get('duplicate') is None,'Initial preflight was not clear')
        check(artifact('preflight.json').get('settings',{}).get('enabled') is True,'Torrent submissions were not enabled')
        duplicate=artifact('duplicate.json').get('duplicate')
        check(isinstance(duplicate,dict) and duplicate.get('eventId')==artifact('torrent.json').get('event',{}).get('id'),'Duplicate preflight did not identify the published torrent')
        check(any(entry.get('eventId')==artifact('torrent.json').get('event',{}).get('id') for entry in artifact('torrents.json').get('torrents',[])),'Published torrent ID not read back')
        check(len([x for x in journal if x['accepted']])==2,'Torrent was duplicated or reply missing')
    if story['id']=='N09':
        for name in ['chat.json','private.json','room.json','room-chat.json','chat-list.json','private-list.json','room-list.json']:artifact(name)
        check(all(artifact(name).get('messages')==[] for name in ['chat-list.json','private-list.json','room-list.json']),'Ephemeral lists were not empty as expected')
        check(all(accepted_event(artifact(name).get('event')) for name in ['chat.json','private.json','room.json','room-chat.json']),'Saved chat response event differs from relay bytes')
        captured_ids=[artifact(name).get('event',{}).get('id') for name in ['chat.json','private.json','room.json','room-chat.json']]
        check(None not in captured_ids and set(captured_ids)=={entry['event']['id'] for entry in journal if entry['accepted']},'Saved chat send responses differ from the accepted events')
        check(len([x for x in journal if x['accepted']])==4,'Ephemeral sends absent or replayed')
        check(all(x['event']['kind']==21423 for x in journal),'Unexpected persistent chat event')
        try:
            config=read_json(record/'services-config.json')
            config.update(fragment=evidence['url'].split('#',1)[1],journal=str(record/'relay-events.json'))
            dump(record/'receiver-config.json',config)
            received=json.loads(subprocess.check_output(['node',str(HERE/'verify-chat.mjs'),str(record/'receiver-config.json')],text=True))
            dump(record/'receiver-messages.json',received)
            check(len(received)==4 and all(x['innerSignatureValid'] for x in received),'Receiver could not decrypt and verify all four sends')
            for channel,text in [('general','General hello'),('private','Private hello'),('room','Room hello')]:
                check(any(x['channel']==channel and x['payload'].get('b')==text for x in received),'Wrong recipient/channel/message for '+channel)
            check(any(x['payload'].get('room')=={'name':'main','code':'trial-code'} for x in received),'Room announcement content differs')
        except Exception as error:check(False,'Receiver verification failed: '+str(error))
    if story['id']=='N10':
        for name in ['quote.json','checkout.json','receipt.json','orders.json','decrypted.json','verification.json','status.json','status-read.json']:artifact(name)
        quote=artifact('quote.json');checkout=artifact('checkout.json')
        check(quote.get('storeCurrency')=='AUD' and quote.get('total')==7.5,'Wrong checkout currency or total')
        check(quote.get('inventory',{}).get('enabled') is True and quote.get('inventory',{}).get('gate')=='ok','Required inventory stock status was not loaded')
        check(any(m.get('method',{}).get('id')=='payid' and m.get('address')=='seller@fixture.test' for m in quote.get('methods',[])),'PayID destination missing or wrong')
        check(checkout.get('flow')=='manual' and checkout.get('method',{}).get('id')=='payid','Manual PayID checkout was not used')
        published=checkout.get('published',{});order=published.get('order',{})
        check(order.get('total')==750 and order.get('buyer',{}).get('country')=='AU','Wrong wire-order amount or buyer country')
        check(artifact('verification.json').get('ok') is True,'Receipt verification did not succeed')
        check(artifact('decrypted.json').get('order')==order and bool(order),'Decrypted receipt does not match checkout')
        check(any(x.get('order')==order for x in artifact('orders.json').get('orders',[])) and bool(order),'Seller did not retrieve the same order')
        check(accepted_event(published.get('event')),'Checkout event differs from accepted relay bytes')
        try:
            independently=cli('store','receipt','decrypt','--input',str(work/'receipt.json'),'--secret','1'*64)
            check(independently.get('order')==order and bool(order),'Saved receipt could not independently recover the order')
            verified_receipt=cli('store','verify',evidence['url'],'--input',str(work/'receipt.json'),'--secret','1'*64)
            check(verified_receipt.get('ok') is True,'Independent receipt verification did not succeed')
        except Exception as error:check(False,'Independent receipt decryption: '+str(error))
        order_rows=list(csv.DictReader(io.StringIO((work/'orders.csv').read_text()))) if (work/'orders.csv').exists() else []
        check(any(row.get('Order ID')==order.get('orderId') and row.get('Total')=='7.50' and row.get('Country')=='AU' and row.get('Payment Method')=='payid' for row in order_rows),'Orders CSV did not contain the same order, amount, country and method')
        check('Test only' in json.dumps(artifact('status-read.json')),'Status notice not read back')
        check(len([x for x in journal if x['accepted']])==2,'Checkout/status absent or duplicated')
    if story['id']=='N16':
        check((work/'builder.png').is_file(),'Missing builder screenshot')
        check(any('/create/message' in x['observed']['url'] for x in browser),'Browser builder was not used')
    evidence['relay_events']=len(journal)
    evidence['browser_observations']=len(browser)
    evidence['skill_sha256']=(record/'skill.sha256').read_text().strip()
    return {'pass':not errors,'errors':errors,'evidence':evidence,'manual_review':'pending'}


def run_case(story,model,batch):
    print(json.dumps({'event':'start','model':model,'story':story['id']}),flush=True)
    record=work=config=service=error_file=None
    try:
        record,work,config,service,error_file=prepare(story,model,batch)
        proc=subprocess.run(['python3',str(HERE/'run.py'),str(record/'launch-config.json')],
                            capture_output=True,text=True,timeout=config['timeout_seconds']+60)
        (record/'launcher.stdout').write_text(proc.stdout)
        (record/'launcher.stderr').write_text(proc.stderr)
        verdict=grade(story,record,work)
    except Exception as error:
        verdict={'pass':False,'errors':[str(error)],'infrastructure_error':True}
    finally:
        if service:
            service.terminate()
            try:service.wait(timeout=15)
            except subprocess.TimeoutExpired:service.kill();service.wait()
        if error_file:error_file.close()
    if record:dump(record/'verdict.json',verdict)
    print(json.dumps({'event':'finish','model':model,'story':story['id'],**verdict}),flush=True)
    return {'model':model,'story':story['id'],'record':str(record),**verdict}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--batch',required=True)
    parser.add_argument('--models',default='luna,haiku,qwen')
    parser.add_argument('--stories',default='')
    parser.add_argument('--resume',action='store_true',help='Add fresh model lanes to an existing immutable batch')
    args=parser.parse_args()
    batch_root=RUNS/args.batch
    if batch_root.exists():
        if not args.resume:raise ValueError('Fresh batch required: '+str(batch_root))
    else:
        if args.resume:raise ValueError('Cannot resume a nonexistent batch')
        shutil.copytree(REPO/'skills/hosted-nowhere',batch_root/'skill-snapshot')
        (batch_root/'skill.sha256').write_text(skill_hash()+'\n')
        shutil.copy2(ROOT/'stories.json',batch_root/'stories.json')
    stories=read_json(batch_root/'stories.json')
    if args.stories:stories=[s for s in stories if s['id'] in args.stories.split(',')]
    models=args.models.split(',')
    def lane(model):
        completed=[]
        for story in stories:
            completed.append(run_case(story,model,args.batch))
            metrics=read_json(batch_root/model/story['id']/'metrics.json',{})
            if any('session limit' in str(error) for error in metrics.get('errors',[])):
                print(json.dumps({'event':'lane_blocked','model':model,'reason':'provider session limit; remaining cells not attempted'}),flush=True)
                break
        return completed
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as pool:
        for values in pool.map(lane,models):results.extend(values)
    all_results=[]
    for verdict in sorted(batch_root.glob('*/*/verdict.json')):
        all_results.append({'model':verdict.parent.parent.name,'story':verdict.parent.name,'record':str(verdict.parent),**read_json(verdict)})
    dump(RUNS/args.batch/'results.json',all_results)
    print(json.dumps({'batch':args.batch,'passed':sum(r['pass'] for r in results),'total':len(results)}),flush=True)


if __name__=='__main__':main()
