#!/usr/bin/env python3
"""Trusted subprocess runner, executed INSIDE the per-tool macOS sandbox."""
import errno
import base64
import json
import os
import pty
import select
import signal
import subprocess
import sys
import time


def output_fields(stdout, stderr, spec):
    fields={}
    for name,value in [('stdout',stdout),('stderr',stderr)]:
        try:
            text=value.decode('utf-8',errors='strict')
            binary=b'\x00' in value
        except UnicodeDecodeError:
            text=value.decode('utf-8',errors='replace');binary=True
        fields[name]=text
        fields[name+'_binary']=binary
        fields[name+'_bytes']=len(value)
        if spec.get('capture_base64'):
            fields[name+'_base64']=base64.b64encode(value).decode('ascii')
    return fields


def run(spec):
    argv = spec.get('argv') or ['/bin/bash', '--noprofile', '--norc', '-c', spec['command']]
    started = time.monotonic()
    timeout = min(180, max(1, spec.get('timeout_seconds', 30)))
    if not spec.get('tty'):
        proc = subprocess.Popen(argv, cwd=spec['cwd'], env=spec['env'], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(spec.get('stdin', '').encode(), timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            timed_out = True
        return dict(**output_fields(stdout,stderr,spec),
                    exit_code=124 if timed_out else proc.returncode, timed_out=timed_out,
                    seconds=time.monotonic() - started, tty=False)
    pid, master = pty.fork()
    if pid == 0:
        os.chdir(spec['cwd'])
        os.execvpe(argv[0], argv, spec['env'])
    output = bytearray()
    pending = spec.get('stdin', '').encode()
    # A PTY keeps isatty(0) true. Two EOTs terminate both a pending canonical
    # line and the following empty read; callers can opt out when sending exit.
    if spec.get('close_stdin', True):
        pending += b'\x04\x04'
    timed_out, status = False, None
    try:
        while True:
            if time.monotonic() - started > timeout:
                timed_out = True
                try:
                    os.killpg(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            readable, writable, _ = select.select([master], [master] if pending else [], [], .05)
            if writable:
                pending = pending[os.write(master, pending):]
            if readable:
                try:
                    chunk = os.read(master, 65536)
                    if not chunk:
                        break
                    output.extend(chunk)
                except OSError as error:
                    if error.errno == errno.EIO:
                        break
                    raise
            done, candidate = os.waitpid(pid, os.WNOHANG)
            if done:
                status = candidate
                # Drain the final output already buffered by the terminal.
                while select.select([master], [], [], .05)[0]:
                    try:
                        chunk = os.read(master, 65536)
                        if not chunk:
                            break
                        output.extend(chunk)
                    except OSError:
                        break
                break
        if status is None:
            _, status = os.waitpid(pid, 0)
    finally:
        os.close(master)
    return dict(**output_fields(bytes(output),b'',spec),
                exit_code=124 if timed_out else os.waitstatus_to_exitcode(status), timed_out=timed_out,
                seconds=time.monotonic() - started, tty=True, stderr_merged=True)


if __name__ == '__main__':
    try:
        print(json.dumps(run(json.load(sys.stdin))))
    except Exception as error:
        print(json.dumps(dict(stdout='', stderr=str(error), exit_code=126, runner_error=True)))
