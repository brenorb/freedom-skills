// Independent receiver-side decryption of the actual relay journal.
import fs from 'node:fs';
import { createHmac } from 'node:crypto';
import { createRequire } from 'node:module';

const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const require=createRequire(config.cli_entrypoint);
const { nip44 }=require('nostr-tools');
const { getEventHash, verifyEvent }=require('nostr-tools/pure');
const forumSecret=createHmac('sha256','nowhere-forum').update(config.fragment).digest();
const roomSecret=createHmac('sha256','nowhere-chat-room')
  .update(Buffer.concat([forumSecret,Buffer.from('main'),Buffer.from([0]),Buffer.from('trial-code')])).digest();
const keys={general:forumSecret,private:Buffer.from('3'.repeat(64),'hex'),room:roomSecret};
const messages=[];
for(const entry of JSON.parse(fs.readFileSync(config.journal,'utf8'))) {
  if(!entry.accepted || entry.event.kind!==21423)continue;
  const event=entry.event;
  for(const [channel,secret] of Object.entries(keys)) {
    try {
      const payload=JSON.parse(nip44.decrypt(event.content,nip44.getConversationKey(secret,event.pubkey)));
      const inner={kind:21423,created_at:payload.ts,tags:[],content:payload.w,pubkey:payload.p,sig:payload.sig};
      inner.id=getEventHash(inner);
      messages.push({eventId:event.id,channel,payload,innerSignatureValid:verifyEvent(inner)});
      break;
    }catch{}
  }
}
process.stdout.write(JSON.stringify(messages));
