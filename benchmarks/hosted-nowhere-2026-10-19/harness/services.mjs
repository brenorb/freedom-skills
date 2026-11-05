// Isolated Nostr relay, fake LNURL provider, and generic headless browser.
// Persistent and ephemeral relay events are deliberately treated differently.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';

const config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const require = createRequire(config.cli_entrypoint);
const { WebSocketServer } = require('ws');
const { nip44 } = require('nostr-tools');
const { finalizeEvent, getPublicKey, verifyEvent } = require('nostr-tools/pure');
const signerSecret = Buffer.from('1'.repeat(64), 'hex');
const signerPubkey = getPublicKey(signerSecret);
const browserRequire = createRequire(path.join(config.omp_root, 'package.json'));
const puppeteer = browserRequire('puppeteer-core');
const history = [], stored = new Map(), requests = [], browserLog = [];
let browser, page, origin, sequence = 0;

function matches(event, filter) {
  if (filter.ids && !filter.ids.some(id => event.id.startsWith(id))) return false;
  if (filter.authors && !filter.authors.some(id => event.pubkey.startsWith(id))) return false;
  if (filter.kinds && !filter.kinds.includes(event.kind)) return false;
  if (filter.since !== undefined && event.created_at < filter.since) return false;
  if (filter.until !== undefined && event.created_at > filter.until) return false;
  return Object.entries(filter).every(([key, values]) => !key.startsWith('#') ||
    event.tags.some(tag => tag[0] === key.slice(1) && values.includes(tag[1])));
}

async function snapshot() {
  return page.evaluate(() => {
    const inputs = [...document.querySelectorAll('input,textarea,select')].map((el, i) => {
      el.setAttribute('data-e2e-input', String(i));
      return {selector: `[data-e2e-input="${i}"]`, type: el.type, value: el.value,
        label: el.labels?.[0]?.innerText, placeholder: el.placeholder,
        options: el.options ? [...el.options].map(x => ({text:x.text, value:x.value})) : undefined};
    });
    const buttons = [...document.querySelectorAll('button,a,[role="button"]')].map((el, i) => {
      el.setAttribute('data-e2e-button', String(i));
      return {selector: `[data-e2e-button="${i}"]`, text: el.innerText, href: el.href, disabled:el.disabled};
    });
    return {url:location.href,title:document.title,text:document.body.innerText,inputs,buttons,
      svg:[...document.querySelectorAll('main svg')].map(el => el.outerHTML).slice(0,4)};
  });
}

async function browserAction(body) {
  if (!browser) {
    browser = await puppeteer.launch({executablePath:config.chrome,headless:true,
      userDataDir:path.join(config.record,'chrome-profile'),
      args:['--no-first-run','--disable-background-networking','--no-default-browser-check']});
    page = await browser.newPage();
    await page.setViewport({width:1280,height:1000});
    const cdp = await page.createCDPSession();
    await cdp.send('Network.enable');
    await cdp.send('Network.setBlockedURLs', {urls:['wss://*']});
    page.on('console', msg => fs.appendFileSync(path.join(config.record,'browser-console.jsonl'), JSON.stringify({text:msg.text()})+'\n'));
  }
  const [first,second] = body.args || [];
  if (body.action === 'goto') {
    const target = new URL(first);
    if (!['hostednowhere.com','www.hostednowhere.com','nowhr.xyz','127.0.0.1'].includes(target.hostname))
      throw Error('Browser navigation restricted to the app and loopback fixtures');
    await page.goto(first,{waitUntil:'networkidle2',timeout:60000});
  } else if (body.action === 'fill') {
    await page.$eval(first,(el,value) => { el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true})); },second);
  } else if (body.action === 'click') {
    await page.click(first);
    await new Promise(resolve => setTimeout(resolve,300));
  } else if (body.action === 'select') {
    await page.select(first,second);
  } else if (body.action === 'screenshot') {
    const destination = path.resolve(config.workspace,first);
    if (!destination.startsWith(config.workspace+path.sep)) throw Error('Screenshot must be inside workspace');
    fs.mkdirSync(path.dirname(destination),{recursive:true});
    await page.screenshot({path:destination,fullPage:true});
  } else if (body.action !== 'snapshot') throw Error('Unknown browser action');
  const observed = await snapshot();
  browserLog.push({sequence:++sequence,action:body.action,args:body.args,observed});
  fs.writeFileSync(path.join(config.record,'browser.json'),JSON.stringify(browserLog,null,2));
  return observed;
}

const server = http.createServer(async (request,response) => {
  const url = new URL(request.url,'http://localhost');
  try {
    if (url.pathname === '/browser') {
      let raw='';for await (const chunk of request) raw+=chunk;
      const result = await browserAction(JSON.parse(raw));
      response.writeHead(200,{'Content-Type':'application/json'}).end(JSON.stringify(result));return;
    }
    requests.push({path:url.pathname,query:Object.fromEntries(url.searchParams)});
    fs.writeFileSync(path.join(config.record,'service-requests.json'),JSON.stringify(requests,null,2));
    let data;
    if (url.pathname === '/events') data=history;
    else if (url.pathname.startsWith('/.well-known/lnurlp/'))
      data={tag:'payRequest',callback:origin+'/invoice',minSendable:1000,maxSendable:1000000000,metadata:'[["text/plain","Test-only invoice"]]'};
    else if (url.pathname === '/invoice') data={pr:'lnbc_TEST_ONLY_'+url.searchParams.get('amount'),routes:[]};
    else if (url.pathname === '/health') data={ok:true};
    else { response.writeHead(404).end();return; }
    response.writeHead(200,{'Content-Type':'application/json'}).end(JSON.stringify(data));
  } catch(error) { response.writeHead(400,{'Content-Type':'application/json'}).end(JSON.stringify({error:error.message})); }
});
const sockets = new WebSocketServer({server});
function broadcast(event) {
  for(const client of sockets.clients) for(const [sub,queries] of client.subscriptions || [])
    if(queries.some(q=>matches(event,q))) client.send(JSON.stringify(['EVENT',sub,event]));
}
function bunkerReply(event) {
  if(event.kind!==24133 || !event.tags.some(tag=>tag[0]==='p' && tag[1]===signerPubkey))return;
  const key=nip44.getConversationKey(signerSecret,event.pubkey);
  const request=JSON.parse(nip44.decrypt(event.content,key));
  fs.appendFileSync(path.join(config.record,'signer-rpc.jsonl'),JSON.stringify({method:request.method,id:request.id,eventId:event.id})+'\n');
  let result;
  if(request.method==='connect')result='ack';
  else if(request.method==='get_public_key')result=signerPubkey;
  else if(request.method==='sign_event')result=JSON.stringify(finalizeEvent(JSON.parse(request.params[0]),signerSecret));
  else if(request.method==='nip44_encrypt')result=nip44.encrypt(request.params[1],nip44.getConversationKey(signerSecret,request.params[0]));
  else if(request.method==='nip44_decrypt')result=nip44.decrypt(request.params[1],nip44.getConversationKey(signerSecret,request.params[0]));
  const response=finalizeEvent({kind:24133,created_at:Math.floor(Date.now()/1000),tags:[['p',event.pubkey]],
    content:nip44.encrypt(JSON.stringify({id:request.id,result}),key)},signerSecret);
  broadcast(response);
}
sockets.on('connection',(socket,request) => {
  const subscriptions = new Map();socket.subscriptions=subscriptions;
  socket.on('message',raw => {
    try {
      const frame=JSON.parse(raw.toString());
      if(!Array.isArray(frame))throw new Error('Expected a relay request array');
      const [kind,id,...filters]=frame;
      if (kind==='EVENT') {
        const event=id, accepted=request.url!=='/reject' && verifyEvent(event);
        history.push({event,accepted,relayPath:request.url});
        fs.writeFileSync(path.join(config.record,'relay-events.json'),JSON.stringify(history,null,2));
        if(accepted) {
          if(event.kind<20000 || event.kind>=30000) {
            if(event.kind>=30000 && event.kind<40000) {
              const d=event.tags.find(t=>t[0]==='d')?.[1];
              for(const [oldId,old] of stored) if(old.kind===event.kind && old.pubkey===event.pubkey && old.tags.find(t=>t[0]==='d')?.[1]===d) stored.delete(oldId);
            }
            stored.set(event.id,event);
          }
          broadcast(event);
          setTimeout(()=> {try{bunkerReply(event);}catch(error){fs.appendFileSync(path.join(config.record,'signer-errors.log'),error.message+'\n');}},10);
        }
        if(request.url!=='/dropack') socket.send(JSON.stringify(['OK',event.id,accepted,accepted?'':'blocked: test rejection']));
      } else if(kind==='REQ' || kind==='COUNT') {
        if(typeof id!=='string' || !filters.length || filters.some(filter =>
          !filter || typeof filter!=='object' || Array.isArray(filter) ||
          Object.entries(filter).some(([key,value]) =>
            (['ids','authors','kinds'].includes(key) || key.startsWith('#')) && !Array.isArray(value)))) {
          throw new Error('Invalid subscription filter');
        }
        subscriptions.set(id,filters);
        const result=[...stored.values()].filter(e=>filters.some(f=>matches(e,f)))
          .sort((a,b)=>b.created_at-a.created_at);
        if(kind==='COUNT')socket.send(JSON.stringify(['COUNT',id,{count:result.length}]));
        else {
          const limit=Math.max(...filters.map(f=>f.limit || result.length));
          for(const event of result.slice(0,limit))socket.send(JSON.stringify(['EVENT',id,event]));
          socket.send(JSON.stringify(['EOSE',id]));
        }
      } else if(kind==='CLOSE')subscriptions.delete(id);
    } catch(error) {
      // Diagnostic/malformed clients must not terminate the shared fixture.
      fs.appendFileSync(path.join(config.record,'relay-protocol-errors.jsonl'),
        JSON.stringify({error:error.message})+'\n');
      socket.send(JSON.stringify(['NOTICE','invalid: malformed relay request']));
    }
  });
});
server.listen(0,'127.0.0.1',() => {
  origin=`http://127.0.0.1:${server.address().port}`;
  const relay=origin.replace('http:','ws:')+'/relay';
  process.stdout.write(JSON.stringify({origin,relay,bunker:`bunker://${signerPubkey}?relay=${encodeURIComponent(relay)}`})+'\n');
});
process.on('SIGTERM',async () => { if(browser)await browser.close();for(const socket of sockets.clients)socket.terminate();server.close(()=>process.exit(0)); });
