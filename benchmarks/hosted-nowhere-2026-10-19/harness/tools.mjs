import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const helper = fileURLToPath(new URL('./command_runner.py', import.meta.url));
const inside = (root, candidate) => candidate === root || candidate.startsWith(root + path.sep);
const sbquote = value => JSON.stringify(value);
export const HARNESS_VERSION='h2';

export function serializedBytes(value) { return Buffer.byteLength(JSON.stringify(value),'utf8'); }

// Cap the complete serialized response, including JSON escapes and both output
// streams, rather than counting only unescaped stdout characters.
export function boundResult(value, budget=24000) {
  const result=structuredClone(value);
  const cap=Math.max(1024,budget);
  let loops=0;
  while(serializedBytes(result)>cap && loops++<100) {
    const candidates=Object.keys(result).filter(k=>typeof result[k]==='string' && result[k].length>80)
      .sort((a,b)=>Buffer.byteLength(result[b])-Buffer.byteLength(result[a]));
    const key=candidates[0];
    if(key) {
      result[key]=result[key].slice(0,Math.max(0,Math.floor(result[key].length*.65)))+'…[truncated]';
      result[key+'_truncated']=true;
    } else if(Array.isArray(result.entries) && result.entries.length) {
      result.entries=result.entries.slice(0,Math.floor(result.entries.length/2));result.entries_truncated=true;
    } else return {error:'Response exceeds the serialized output budget; full response retained in benchmark logs.',exit_code:126,response_truncated:true};
  }
  if(serializedBytes(result)>cap)throw Error('Failed to bound tool response.');
  return result;
}

export const TOOL_SCHEMAS = [
  {name:'read', description:'Read a UTF-8 text workspace file with numbered lines, or list a directory. Binary files are rejected. Large responses are bounded; use offset/limit for more text. Paths are relative to the workspace.', inputSchema:{type:'object',properties:{path:{type:'string'},offset:{type:'integer'},limit:{type:'integer'}},required:['path'],additionalProperties:false}},
  {name:'write', description:'Create or overwrite a UTF-8 file within your workspace; parent directories are created automatically.',inputSchema:{type:'object',properties:{path:{type:'string'},content:{type:'string'}},required:['path','content'],additionalProperties:false}},
  {name:'bash',description:'Run a shell command or argv array within your workspace. Supply exactly one of command or argv. stdin supplies piped input. tty=true uses an interactive terminal; stdin is then terminal input. close_stdin defaults true (sends EOF); set false if stdin already contains exit. timeout_seconds is 1..180. Writes inside the workspace and localhost connections are permitted; non-loopback network access is blocked. Binary output is omitted; large stdout/stderr are bounded. Full outputs are retained in benchmark logs. Outside files are inaccessible except system runtime paths.',inputSchema:{type:'object',properties:{command:{type:'string'},argv:{type:'array',items:{type:'string'}},cwd:{type:'string'},stdin:{type:'string'},tty:{type:'boolean'},close_stdin:{type:'boolean'},timeout_seconds:{type:'integer',minimum:1,maximum:180}},additionalProperties:false}},
];

// Resolve every existing ancestor, so symlinks cannot escape before creation.
export function canonical(candidate) {
  const full = path.resolve(candidate);
  if (fs.existsSync(full)) return fs.realpathSync(full);
  return path.join(canonical(path.dirname(full)), path.basename(full));
}

export function makeToolRuntime(config, record) {
  const workspace = fs.realpathSync(config.workspace);
  const protectedRoots = (config.read_only_paths || []).map(p => canonical(path.resolve(workspace, p)));
  fs.mkdirSync(path.join(workspace, 'tmp'), { recursive: true });
  const check = (value, write = false) => {
    const resolved = canonical(path.resolve(workspace, value));
    if (!inside(workspace, resolved)) throw Error('Only the assigned workspace is accessible.');
    if (write && protectedRoots.some(root => inside(root, resolved) || inside(resolved, root)))
      throw Error('Frozen skill and fixtures are read-only.');
    return resolved;
  };
  const readonly = ['/System', '/usr', '/bin', '/sbin', '/Library/Apple',
    '/Library/Developer/CommandLineTools', '/private/etc', '/private/var/db',
    ...(config.runtime_read_paths || [])].filter(p => fs.existsSync(p));
  // macOS aborts signed binaries under an unfiltered blanket file-read denial.
  // Deny every non-runtime root explicitly instead; metadata stays readable so
  // realpath/dyld can traverse ancestors to specifically allowed descendants.
  const runtimeRoots = new Set(['System','usr','bin','sbin','dev','private','var','tmp','Library']);
  const denied = fs.readdirSync('/').filter(name=>!runtimeRoots.has(name)).map(name=>'/'+name);
  denied.push('/private/tmp','/tmp');
  for (const name of fs.readdirSync('/private/var')) if (!['db','run','empty'].includes(name)) denied.push('/private/var/'+name);
  for (const name of fs.readdirSync('/Library')) if (!['Apple','Developer'].includes(name)) denied.push('/Library/'+name);
  const profile = ['(version 1)', '(allow default)', '(deny file-write*)',
    ...denied.map(p=>`(deny file-read* (subpath ${sbquote(p)}))`), '(allow file-read-metadata)',
    ...readonly.map(p => `(allow file-read* (subpath ${sbquote(p)}))`),
    `(allow file-read* (literal ${sbquote(helper)}))`,
    '(allow file-read* file-write* (subpath "/dev"))',
    `(allow file-read* file-write* (subpath ${sbquote(workspace)}))`,
    ...protectedRoots.map(p => `(deny file-write* (subpath ${sbquote(p)}))`),
    ...(config.runtime_write_paths || []).map(p => `(allow file-write* (subpath ${sbquote(p)}))`),
    '(deny network*)',
    '(allow network-outbound (remote ip "localhost:*"))',
    '(allow network-inbound (local ip "localhost:*"))',
  ].join('\n') + '\n';
  const profilePath = path.join(record, 'tool-sandbox.sb');
  fs.writeFileSync(profilePath, profile);
  const log = entry => fs.appendFileSync(path.join(record, 'tools.jsonl'), JSON.stringify({ utc: new Date().toISOString(), ...entry }) + '\n');
  fs.mkdirSync(path.join(record,'raw-output'),{recursive:true});
  let invocation=0;
  async function invoke(name, input, signal) {
    const sequence=++invocation;
    const start = performance.now();
    let result;
    try {
      if (name === 'read') {
        const target = check(input.path);
        if (fs.statSync(target).isDirectory()) {
          result = { entries: fs.readdirSync(target, { withFileTypes: true }).map(d => ({ name: d.name, directory: d.isDirectory() })) };
        } else {
          const bytes=fs.readFileSync(target);
          fs.writeFileSync(path.join(record,'raw-output',`${sequence}.read.bin`),bytes);
          if(bytes.includes(0))throw Error('read supports UTF-8 text only; binary/NUL data is unavailable.');
          let text;
          try {text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);}
          catch {throw Error('read supports UTF-8 text only; invalid UTF-8 binary data is unavailable.');}
          const lines = text.split('\n');
          const offset = Math.max(1, input.offset || 1), limit = Math.min(1000, input.limit || 250);
          result = { path: input.path, text: lines.slice(offset - 1, offset - 1 + limit).map((s, i) => `${offset + i}: ${s}`).join('\n'), total_lines: lines.length };
        }
      } else if (name === 'write') {
        const target = check(input.path, true);
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.writeFileSync(target, input.content);
        result = { path: input.path, bytes: Buffer.byteLength(input.content) };
      } else if (name === 'bash') {
        if (Boolean(input.command) === Boolean(input.argv?.length)) throw Error('Supply exactly one of command or nonempty argv.');
        const cwd = check(input.cwd || '.');
        const spec = { ...input, cwd, capture_base64:true, env: { PATH: (config.tool_paths || [path.join(workspace,'bin')]).join(':') + ':/usr/bin:/bin:/usr/sbin:/sbin',
          TMPDIR: path.join(workspace, 'tmp'), LANG: 'en_US.UTF-8', LC_ALL: 'en_US.UTF-8', ...(config.tool_env || {}) } };
        result = await new Promise((resolve, reject) => {
          const python = fs.existsSync('/Library/Developer/CommandLineTools/usr/bin/python3') ? '/Library/Developer/CommandLineTools/usr/bin/python3' : '/usr/bin/python3';
          const proc = spawn('/usr/bin/sandbox-exec', ['-f', profilePath, python, helper], {
            cwd, env: spec.env, stdio: ['pipe', 'pipe', 'pipe'], detached: true,
          });
          let stdout = '', stderr = '', killed = false;
          const kill = () => { killed = true; try { process.kill(-proc.pid, 'SIGKILL'); } catch {} };
          const timer = setTimeout(kill, (Math.min(180, Math.max(1, input.timeout_seconds || 30)) + 10) * 1000);
          signal?.addEventListener('abort', kill, { once: true });
          proc.stdout.on('data', chunk => { stdout += chunk; });
          proc.stderr.on('data', chunk => { stderr += chunk; });
          proc.on('error', reject);
          proc.on('close', code => {
            clearTimeout(timer); signal?.removeEventListener('abort', kill);
            try { const payload = JSON.parse(stdout); resolve({ ...payload, sandbox_stderr: stderr }); }
            catch { resolve({ stdout, stderr, exit_code: killed ? 124 : code, sandbox_error: true }); }
          });
          proc.stdin.end(JSON.stringify(spec));
        });
        for(const stream of ['stdout','stderr']) {
          if(result[stream+'_base64']!==undefined) {
            fs.writeFileSync(path.join(record,'raw-output',`${sequence}.${stream}.bin`),Buffer.from(result[stream+'_base64'],'base64'));
            delete result[stream+'_base64'];
          }
        }
        fs.appendFileSync(path.join(record, 'commands.jsonl'), JSON.stringify({ sequence, input, result }) + '\n');
        for(const stream of ['stdout','stderr']) if(result[stream+'_binary']) {
          result={...result,[stream]:`[Binary ${stream} omitted; ${result[stream+'_bytes']} raw bytes retained in benchmark logs.]`};
        }
      } else throw Error('Unknown tool.');
    } catch (error) { result = { error: error.message, blocked: true, exit_code: 126 }; }
    fs.writeFileSync(path.join(record,'raw-output',`${sequence}.result.json`),JSON.stringify(result)+'\n');
    result=boundResult(result,config.output_serialized_byte_limit || config.output_char_limit || 24000);
    log({ name, input, result, serialized_response_bytes:serializedBytes(result), seconds: (performance.now() - start) / 1000 });
    return result;
  }
  return { invoke, profile, check };
}

export function makeTools(z, runtime) {
  const specs = [
    ['read', 'Read a UTF-8 workspace file with numbered lines, or list a directory. Paths are relative to the workspace.', z.object({ path: z.string(), offset: z.number().int().optional(), limit: z.number().int().optional() })],
    ['write', 'Create or overwrite a UTF-8 file within your workspace; parent directories are created automatically.', z.object({ path: z.string(), content: z.string() })],
    ['bash', 'Run a shell command or an argv array within your workspace. Set stdin for piped input. Set tty=true for interactive terminal commands; stdin is then sent as terminal input. close_stdin defaults true (sends EOF); set false when stdin already contains an exit command. timeout_seconds is 1..180. Files outside your workspace and system runtime paths are inaccessible.', z.object({
      command: z.string().optional(), argv: z.array(z.string()).optional(), cwd: z.string().optional(), stdin: z.string().optional(),
      tty: z.boolean().optional(), close_stdin: z.boolean().optional(), timeout_seconds: z.number().int().min(1).max(180).optional(),
    }).refine(v => Boolean(v.command) !== Boolean(v.argv?.length), 'Supply exactly one of command or nonempty argv.')],
  ];
  return specs.map(([name, _description, parameters]) => ({ name, label: name, description: TOOL_SCHEMAS.find(t=>t.name===name).description, parameters, loadMode: 'essential',
    async execute(_id, input, _update, _ctx, signal) {
      const result = await runtime.invoke(name, input, signal);
      return { content: [{ type: 'text', text: JSON.stringify(result) }], details: result,
        isError: !!result.error || (typeof result.exit_code === 'number' && result.exit_code !== 0) };
    },
  }));
}
