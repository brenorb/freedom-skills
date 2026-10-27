// Pure H2 helpers: finalized request accounting survives SDK history compaction.
export function finalizedUsage(turns) {
  const deduplicated=[];const seen=new Set();
  for(const turn of turns) {
    if(turn.message_id && seen.has(turn.message_id))continue;
    if(turn.message_id)seen.add(turn.message_id);
    deduplicated.push(turn);
  }
  const fields=['input','output','cacheRead','cacheWrite','totalTokens'];
  const usable=deduplicated.filter(t=>t.usage && !(['error','aborted'].includes(t.stop_reason) && fields.every(k=>!t.usage[k])));
  const sum=field=>usable.length && usable.every(t=>typeof t.usage[field]==='number') ? usable.reduce((n,t)=>n+t.usage[field],0) : null;
  const known={...Object.fromEntries(fields.map(k=>[k,sum(k)])),reasoningTokens:sum('reasoningTokens')};
  return {known,finalized_requests:deduplicated.length,known_usage_requests:usable.length,
    missing_usage_requests:deduplicated.length-usable.length,
    known_reasoning_tokens_lower_bound:usable.reduce((n,t)=>n+(t.usage.reasoningTokens || 0),0)};
}

export function installRuntimeModel(registry, registered, config) {
  const endpoint=new URL(registered.baseUrl);
  if(registered.provider!=='splash' || !['127.0.0.1','localhost','[::1]'].includes(endpoint.hostname))
    throw Error('H2 runtime overlay is restricted to the local Splash benchmark server.');
  const desired={...registered,...(config.model_overrides || {}),
    contextWindow:config.actual_context_window || 32768,
    maxTokens:Math.min(registered.maxTokens,config.max_output_tokens || 4096)};
  // Runtime registration affects the per-process registry too, so retries and
  // compaction resolve this same actual window instead of the global catalog.
  // The local benchmark server was launched without API-key auth. Registration
  // requires a key declaration, so use a public dummy and suppress auth headers.
  registry.registerProvider(registered.provider,{baseUrl:registered.baseUrl,api:registered.api,
    apiKey:'unused-local-benchmark',authHeader:false,
    compat:registered.compat,models:[desired]},'btcdeb-benchmark-h2');
  const resolved=registry.find(registered.provider,registered.id);
  if(!resolved || resolved.contextWindow!==desired.contextWindow || resolved.maxTokens!==desired.maxTokens)
    throw Error('Runtime model limits were not installed in the recovery registry.');
  return resolved;
}
