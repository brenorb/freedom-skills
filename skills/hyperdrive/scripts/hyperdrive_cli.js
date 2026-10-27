#!/usr/bin/env node

const fs = require('fs')
const fsp = require('fs/promises')
const path = require('path')
const process = require('process')

const Corestore = require('corestore')
const Hyperdrive = require('hyperdrive')
const Hyperswarm = require('hyperswarm')
const Id = require('hypercore-id-encoding')

function usage() {
  console.error(`Usage:
  node hyperdrive_cli.js create --store <dir> [--json]
  node hyperdrive_cli.js put --store <dir> --source <file-or-dir> [--path </remote/path>] [--json]
  node hyperdrive_cli.js list --store <dir> [--key <hex-or-z32>] [--prefix </path>] [--json]
  node hyperdrive_cli.js get --store <dir> [--key <hex-or-z32>] --path </remote/path> [--output <file>] [--json]
  node hyperdrive_cli.js mirror --store <dir> [--key <hex-or-z32>] --dest <dir> [--prefix </path>] [--strip-prefix] [--json]
  node hyperdrive_cli.js seed --store <dir> [--json]

Options:
  --store        Corestore directory for this local drive or cache
  --key          Remote drive key as hex or z32 id for read-only client operations
  --prefix       Prefix to list or mirror from, default "/"
  --strip-prefix Mirror listed paths relative to --prefix instead of preserving the full drive path
  --timeout-ms   Remote wait timeout in milliseconds, default 15000
  --json         Emit machine-readable JSON
`)
}

function parseArgs(argv) {
  const args = { _: [] }
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]
    if (!arg.startsWith('--')) {
      args._.push(arg)
      continue
    }
    const key = arg.slice(2)
    const next = argv[i + 1]
    if (!next || next.startsWith('--')) {
      args[key] = true
      continue
    }
    args[key] = next
    i++
  }
  return args
}

function assertArg(args, key, message) {
  if (!args[key]) throw new Error(message)
}

function normalizeDrivePath(p) {
  if (!p) return '/'
  if (p === '/') return '/'
  const normalized = p.startsWith('/') ? p : `/${p}`
  return normalized.replace(/\/+/g, '/')
}

function decodeKey(key) {
  if (!key) return null
  return Id.decode(key)
}

function toDriveSegments(relativePath) {
  return relativePath.split(path.sep).filter(Boolean)
}

function joinDrivePath(basePath, relativePath) {
  const base = normalizeDrivePath(basePath)
  const segments = toDriveSegments(relativePath)
  if (base === '/') return normalizeDrivePath(`/${segments.join('/')}`)
  return normalizeDrivePath(`${base}/${segments.join('/')}`)
}

function ensureInsideDest(destDir, relativePath) {
  const resolved = path.resolve(destDir, relativePath)
  const relative = path.relative(destDir, resolved)
  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error(`Refusing to write outside destination: ${relativePath}`)
  }
  return resolved
}

function mirrorRelativePath(entryPath, prefix, stripPrefix) {
  if (!stripPrefix || prefix === '/') return entryPath.replace(/^\/+/, '')
  const relative = path.posix.relative(prefix, entryPath)
  if (!relative) return path.posix.basename(entryPath)
  return relative
}

function driveInfo(drive, storeDir) {
  return {
    store: storeDir,
    key_hex: drive.key.toString('hex'),
    drive_id: drive.id,
    discovery_key_hex: drive.discoveryKey.toString('hex'),
    version: drive.version,
    writable: drive.writable
  }
}

function printResult(result, json) {
  if (json) {
    process.stdout.write(JSON.stringify(result, null, 2) + '\n')
    return
  }
  process.stdout.write(result.message + '\n')
}

function withTimeout(promise, timeoutMs, label) {
  if (!timeoutMs || timeoutMs <= 0) return promise
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      const timer = setTimeout(() => reject(new Error(label)), timeoutMs)
      promise.finally(() => clearTimeout(timer))
    })
  ])
}

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms))
}

async function openDrive(storeDir, key) {
  const store = new Corestore(storeDir)
  const drive = new Hyperdrive(store, key || undefined)
  await drive.ready()
  return { store, drive }
}

async function connectClient(drive, store, timeoutMs) {
  const swarm = new Hyperswarm()
  let connectionCount = 0
  swarm.on('connection', (conn) => store.replicate(conn))
  swarm.on('connection', () => {
    connectionCount++
  })
  const session = swarm.join(drive.discoveryKey, { server: false, client: true })
  const initialVersion = drive.version
  const initialLength = drive.db.core.length
  await session.flushed()
  await swarm.flush()
  const settleDeadline = Date.now() + Math.min(timeoutMs, 2000)

  while (Date.now() < settleDeadline) {
    if (drive.version > initialVersion || drive.db.core.length > initialLength) break
    if (connectionCount > 0) await drive.update()
    await sleep(100)
  }

  if (connectionCount === 0) {
    await withTimeout(
      drive.update({ wait: true }),
      timeoutMs,
      `Timed out waiting for peers for drive ${drive.id}`
    )
  }

  if (drive.db.core.length > 0) {
    await withTimeout(
      drive.db.core.download({ start: 0, end: drive.db.core.length }).done(),
      timeoutMs,
      `Timed out downloading metadata for drive ${drive.id}`
    )
  }

  return swarm
}

async function commandCreate(args) {
  assertArg(args, 'store', '--store is required')
  const { store, drive } = await openDrive(args.store)
  try {
    const info = driveInfo(drive, args.store)
    return {
      ...info,
      message: `Created Hyperdrive ${info.drive_id} at ${args.store}`
    }
  } finally {
    await drive.close()
    await store.close()
  }
}

async function commandPut(args) {
  assertArg(args, 'store', '--store is required')
  assertArg(args, 'source', '--source is required')

  const sourcePath = path.resolve(args.source)
  const sourceStat = await fsp.lstat(sourcePath)
  const remotePath = normalizeDrivePath(args.path || `/${path.basename(sourcePath)}`)

  const { store, drive } = await openDrive(args.store)
  try {
    const written = []

    if (sourceStat.isDirectory()) {
      const queue = [sourcePath]

      while (queue.length > 0) {
        const current = queue.shift()
        const entries = await fsp.readdir(current, { withFileTypes: true })

        for (const entry of entries) {
          const entryPath = path.join(current, entry.name)
          const relativePath = path.relative(sourcePath, entryPath)
          const drivePath = joinDrivePath(remotePath, relativePath)

          if (entry.isDirectory()) {
            queue.push(entryPath)
            continue
          }

          if (entry.isSymbolicLink()) {
            const linkname = await fsp.readlink(entryPath)
            await drive.symlink(drivePath, linkname)
            written.push({
              path: drivePath,
              type: 'symlink',
              source: entryPath,
              linkname
            })
            continue
          }

          if (!entry.isFile()) continue

          const data = await fsp.readFile(entryPath)
          await drive.put(drivePath, data)
          written.push({
            path: drivePath,
            type: 'file',
            source: entryPath,
            byte_length: data.byteLength
          })
        }
      }
    } else {
      const data = await fsp.readFile(sourcePath)
      await drive.put(remotePath, data)
      written.push({
        path: remotePath,
        type: 'file',
        source: sourcePath,
        byte_length: data.byteLength
      })
    }

    const info = driveInfo(drive, args.store)
    return {
      ...info,
      remote_path: remotePath,
      source: sourcePath,
      written,
      byte_length: written.length === 1 && written[0].type === 'file' ? written[0].byte_length : null,
      message: `Stored ${written.length} entr${written.length === 1 ? 'y' : 'ies'} from ${sourcePath} at ${remotePath} in Hyperdrive ${info.drive_id}`
    }
  } finally {
    await drive.close()
    await store.close()
  }
}

async function commandList(args) {
  assertArg(args, 'store', '--store is required')
  const prefix = normalizeDrivePath(args.prefix || '/')
  const timeoutMs = Number(args['timeout-ms'] || 15000)

  const { store, drive } = await openDrive(args.store, decodeKey(args.key))
  let swarm = null
  try {
    if (args.key) swarm = await connectClient(drive, store, timeoutMs)

    const entries = []
    for await (const entry of drive.list(prefix, { recursive: true, wait: true })) {
      entries.push({
        path: entry.key,
        type: entry.value.linkname ? 'symlink' : 'file',
        byte_length: entry.value.blob ? entry.value.blob.byteLength : null,
        executable: !!entry.value.executable,
        linkname: entry.value.linkname || null
      })
    }

    const info = driveInfo(drive, args.store)
    return {
      ...info,
      prefix,
      entries,
      message: `Listed ${entries.length} entr${entries.length === 1 ? 'y' : 'ies'} from ${prefix}`
    }
  } finally {
    if (swarm) await swarm.destroy()
    await drive.close()
    await store.close()
  }
}

async function commandGet(args) {
  assertArg(args, 'store', '--store is required')
  assertArg(args, 'path', '--path is required')
  const timeoutMs = Number(args['timeout-ms'] || 15000)

  const remotePath = normalizeDrivePath(args.path)
  const outputPath = path.resolve(args.output || path.basename(remotePath))

  const { store, drive } = await openDrive(args.store, decodeKey(args.key))
  let swarm = null
  try {
    if (args.key) swarm = await connectClient(drive, store, timeoutMs)

    const data = await drive.get(remotePath, { wait: true, timeout: timeoutMs })
    if (!data) throw new Error(`No blob found at ${remotePath}`)

    await fsp.mkdir(path.dirname(outputPath), { recursive: true })
    await fsp.writeFile(outputPath, data)

    const info = driveInfo(drive, args.store)
    return {
      ...info,
      remote_path: remotePath,
      output: outputPath,
      byte_length: data.byteLength,
      message: `Downloaded ${remotePath} to ${outputPath}`
    }
  } finally {
    if (swarm) await swarm.destroy()
    await drive.close()
    await store.close()
  }
}

async function ensureParentDir(filePath) {
  await fsp.mkdir(path.dirname(filePath), { recursive: true })
}

async function commandMirror(args) {
  assertArg(args, 'store', '--store is required')
  assertArg(args, 'dest', '--dest is required')
  const prefix = normalizeDrivePath(args.prefix || '/')
  const stripPrefix = !!args['strip-prefix']
  const timeoutMs = Number(args['timeout-ms'] || 15000)
  const destDir = path.resolve(args.dest)

  const { store, drive } = await openDrive(args.store, decodeKey(args.key))
  let swarm = null
  try {
    if (args.key) swarm = await connectClient(drive, store, timeoutMs)

    const written = []
    for await (const entry of drive.list(prefix, { recursive: true, wait: true })) {
      const relative = mirrorRelativePath(entry.key, prefix, stripPrefix)
      const destPath = ensureInsideDest(destDir, relative)

      if (entry.value.linkname) {
        await ensureParentDir(destPath)
        try {
          await fsp.symlink(entry.value.linkname, destPath)
        } catch (err) {
          if (err.code !== 'EEXIST') throw err
        }
        written.push({ path: entry.key, type: 'symlink', output: destPath })
        continue
      }

      const data = await drive.get(entry.key, { wait: true, timeout: timeoutMs })
      if (!data) continue
      await ensureParentDir(destPath)
      await fsp.writeFile(destPath, data)
      written.push({
        path: entry.key,
        type: 'file',
        output: destPath,
        byte_length: data.byteLength
      })
    }

    const info = driveInfo(drive, args.store)
    return {
      ...info,
      prefix,
      strip_prefix: stripPrefix,
      dest: destDir,
      written,
      message: `Mirrored ${written.length} entr${written.length === 1 ? 'y' : 'ies'} into ${destDir}`
    }
  } finally {
    if (swarm) await swarm.destroy()
    await drive.close()
    await store.close()
  }
}

async function commandSeed(args) {
  assertArg(args, 'store', '--store is required')
  const { store, drive } = await openDrive(args.store)
  const swarm = new Hyperswarm()
  swarm.on('connection', (conn) => store.replicate(conn))

  const session = swarm.join(drive.discoveryKey, { server: true, client: false })
  await session.flushed()

  const info = driveInfo(drive, args.store)
  const payload = {
    ...info,
    message: `Seeding Hyperdrive ${info.drive_id} from ${args.store}`
  }

  if (args.json) {
    process.stdout.write(JSON.stringify(payload) + '\n')
  } else {
    process.stdout.write(payload.message + '\n')
    process.stdout.write(`Share key: ${payload.key_hex}\n`)
  }

  const shutdown = async () => {
    await swarm.destroy().catch(() => {})
    await drive.close().catch(() => {})
    await store.close().catch(() => {})
    process.exit(0)
  }

  process.once('SIGINT', shutdown)
  process.once('SIGTERM', shutdown)
  await new Promise(() => {})
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const command = args._[0]

  if (!command || args.help || args.h) {
    usage()
    process.exit(command ? 0 : 1)
  }

  try {
    let result
    switch (command) {
      case 'create':
        result = await commandCreate(args)
        break
      case 'put':
        result = await commandPut(args)
        break
      case 'list':
        result = await commandList(args)
        break
      case 'get':
        result = await commandGet(args)
        break
      case 'mirror':
        result = await commandMirror(args)
        break
      case 'seed':
        await commandSeed(args)
        return
      default:
        usage()
        throw new Error(`Unknown command: ${command}`)
    }

    printResult(result, !!args.json)
  } catch (err) {
    console.error(err.message)
    process.exit(1)
  }
}

main()
