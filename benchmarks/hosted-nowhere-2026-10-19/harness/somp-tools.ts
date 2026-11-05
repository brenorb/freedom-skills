import fs from 'node:fs';
import { makeToolRuntime, makeTools } from './tools.mjs';

export default function (pi) {
  const config = JSON.parse(fs.readFileSync(process.env.HOSTED_NOWHERE_RUN_CONFIG, 'utf8'));
  const runtime = makeToolRuntime(config, config.record);
  const names = [];
  for (const tool of makeTools(pi.zod, runtime)) {
    const originalName = tool.name;
    tool.name = `work_${tool.name}`;
    tool.execute = async (_id, input, ...rest) => {
      // CLI extensions and SDK custom tools place context/signal differently.
      const signal = rest.find(value => typeof value?.addEventListener === 'function' && 'aborted' in value);
      const result = await runtime.invoke(originalName, input, signal);
      return {content:[{type:'text',text:JSON.stringify(result)}],details:result,
        isError:!!result.error || (typeof result.exit_code==='number' && result.exit_code!==0)};
    };
    names.push(tool.name);
    pi.registerTool(tool);
  }
  pi.on('session_start', async () => { await pi.setActiveTools(names); });
}
