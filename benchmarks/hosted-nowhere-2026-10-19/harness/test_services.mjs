// Fixture regression control; no model inference. See usage below.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const here=path.dirname(fileURLToPath(import.meta.url));
const service=path.join(here,'services.mjs');
if(!process.argv[2])throw new Error('Usage: node test_services.mjs SERVICES_CONFIG.json [OUTPUT.json]');
const baseConfig=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const req=createRequire(baseConfig.cli_entrypoint);
const {WebSocket}=req('ws'); const {finalizeEvent}=req('nostr-tools/pure');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'hosted-relay-controls-'));
const config={...baseConfig,record:temp,workspace:temp};
fs.writeFileSync(path.join(temp,'config.json'),JSON.stringify(config));
const child=spawn('node',[service,path.join(temp,'config.json')],{stdio:['ignore','pipe','pipe']});let stderr='';child.stderr.on('data',d=>stderr+=d);
let ws;
try {
 const url=await new Promise((res,rej)=>{child.stdout.once('data',d=>res(JSON.parse(d.toString()).relay));child.once('exit',c=>rej(new Error('service exit '+c+stderr)));});
 ws=new WebSocket(url);await new Promise((res,rej)=>{ws.once('open',res);ws.once('error',rej)});
 const messages=[];ws.on('message',d=>messages.push(JSON.parse(d.toString())));
 const wait=async pred=>{for(let n=0;n<100;n++){const v=messages.find(pred);if(v)return v;await new Promise(r=>setTimeout(r,20));}throw new Error('Missing expected message '+JSON.stringify(messages));};
 const bad=['not-json','{}','null','["REQ","bad",null]','["REQ","bad",{"ids":{}}]','["REQ","bad",{"#t":"wrong"}]'];
 for(let i=0;i<bad.length;i++){ws.send(bad[i]);for(let n=0;n<100&&messages.filter(x=>x[0]==='NOTICE').length<i+1;n++)await new Promise(r=>setTimeout(r,20));assert.equal(messages.filter(x=>x[0]==='NOTICE').length,i+1);assert.equal(child.exitCode,null);}
 ws.send(JSON.stringify(['REQ','live',{kinds:[1,21423]}]));await wait(x=>x[0]==='EOSE'&&x[1]==='live');
 const secret=Buffer.from('2'.repeat(64),'hex');const persistent=finalizeEvent({kind:1,created_at:Math.floor(Date.now()/1000),tags:[],content:'persistent control'},secret);const ephemeral=finalizeEvent({kind:21423,created_at:Math.floor(Date.now()/1000),tags:[],content:'ephemeral control'},secret);
 for(const event of [persistent,ephemeral]){ws.send(JSON.stringify(['EVENT',event]));const ok=await wait(x=>x[0]==='OK'&&x[1]===event.id);assert.equal(ok[2],true);await wait(x=>x[0]==='EVENT'&&x[1]==='live'&&x[2].id===event.id);}
 ws.send(JSON.stringify(['REQ','later',{kinds:[1,21423]}]));await wait(x=>x[0]==='EOSE'&&x[1]==='later');assert.deepEqual(messages.filter(x=>x[0]==='EVENT'&&x[1]==='later').map(x=>x[2].id),[persistent.id]);
 assert.equal(child.exitCode,null);const journal=JSON.parse(fs.readFileSync(path.join(temp,'relay-events.json')));assert.equal(journal.length,2);assert(journal.every(x=>x.accepted));
 const result={service_sha256:createHash('sha256').update(fs.readFileSync(service)).digest('hex'),all_match:true,malformed_frames_rejected_without_crash:bad.length,invalid_filter_not_retained:true,subsequent_signed_persistent_event_accepted:true,subsequent_signed_ephemeral_event_accepted:true,live_subscription_received_both:true,later_history_only_persistent:true,scope:'Isolated actual service fixture; genuine signed events, no model inference or browser required.'};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{ws?.terminate();child.kill('SIGTERM');}
