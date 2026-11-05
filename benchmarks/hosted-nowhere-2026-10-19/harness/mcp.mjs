#!/usr/bin/env bun
// Minimal stdio MCP transport; the same runtime backs Qwen's SDK tools.
import fs from 'node:fs';
import readline from 'node:readline';
import { makeToolRuntime, TOOL_SCHEMAS } from './tools.mjs';
const config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const runtime = makeToolRuntime(config, config.record);
const input = readline.createInterface({ input: process.stdin });
for await (const line of input) {
  let request;
  try {
    request = JSON.parse(line);
    if (!Object.hasOwn(request, 'id')) continue;
    let result;
    switch (request.method) {
      case 'initialize': result = { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'hosted-nowhere-e2e', version: '1.0' } }; break;
      case 'ping': result = {}; break;
      case 'tools/list': result = { tools: TOOL_SCHEMAS }; break;
      case 'resources/list': result = { resources: [] }; break;
      case 'resources/templates/list': result = { resourceTemplates: [] }; break;
      case 'prompts/list': result = { prompts: [] }; break;
      case 'tools/call': {
        const value = await runtime.invoke(request.params.name, request.params.arguments || {});
        result = { content: [{ type: 'text', text: JSON.stringify(value) }], isError: !!value.error || !!value.exit_code }; break;
      }
      default: throw Error('Unsupported MCP method.');
    }
    process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: request.id, result }) + '\n');
  } catch (error) {
    process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: request?.id ?? null, error: { code: -32603, message: error.message } }) + '\n');
  }
}
