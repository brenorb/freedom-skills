import test from 'node:test';
import assert from 'node:assert/strict';
import {finalizedUsage,installRuntimeModel} from '../../benchmarks/harness/telemetry.mjs';

test('finalized requests deduplicate by identity and retain real zero measurements',()=>{
 const usage={input:0,output:2,cacheRead:3,cacheWrite:0,totalTokens:5,reasoningTokens:1};
 const value=finalizedUsage([{message_id:'a',usage},{message_id:'a',usage}]);
 assert.equal(value.finalized_requests,1);assert.equal(value.known.input,0);
 assert.equal(value.known.totalTokens,5);assert.equal(value.known.reasoningTokens,1);
});
test('missing output measurements stay unavailable instead of being zero-filled',()=>{
 const value=finalizedUsage([{usage:{input:2}},{stop_reason:'aborted',usage:{input:0,output:0}}]);
 assert.equal(value.known.output,null);assert.equal(value.missing_usage_requests,1);
 assert.equal(value.known.input,2);assert.equal(finalizedUsage([]).known.totalTokens,null);
});
test('runtime registry and recovery lookup share explicit local limits',()=>{
 let model;const registry={registerProvider(_name,provider){model=provider.models[0];assert.equal(provider.authHeader,false);},find(){return model;}};
 const selected=installRuntimeModel(registry,{provider:'splash',baseUrl:'http://127.0.0.1:8000/v1',id:'synthetic',maxTokens:8192},{actual_context_window:32768,max_output_tokens:4096});
 assert.equal(selected.contextWindow,32768);assert.equal(selected.maxTokens,4096);
});
test('remote providers and mismatched recovery registries are rejected',()=>{
 assert.throws(()=>installRuntimeModel({}, {provider:'splash',baseUrl:'https://example.com',maxTokens:8192},{}));
 assert.throws(()=>installRuntimeModel({registerProvider(){},find(){return {contextWindow:999,maxTokens:1};}}, {provider:'splash',baseUrl:'http://localhost:8000',maxTokens:8192},{}));
});
