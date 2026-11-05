# Finding the `nvpn` executable

Read this file when `nvpn` is not found by normal command lookup. Resolve one executable path, verify it with `version --json`, and use the absolute path for the rest of the task.

## macOS

Try `PATH`, then the common bundled-app locations:

```bash
if command -v nvpn >/dev/null 2>&1; then
  NVPN=$(command -v nvpn)
else
  for candidate in \
    "/Applications/Nostr VPN.app/Contents/Resources/nvpn" \
    "$HOME/Applications/Nostr VPN.app/Contents/Resources/nvpn" \
    "$HOME/.local/bin/nvpn" \
    "$HOME/.cargo/bin/nvpn" \
    "$HOME/bin/nvpn" \
    "/opt/homebrew/bin/nvpn" \
    "/usr/local/bin/nvpn" \
    "/usr/local/sbin/nvpn"; do
    if [ -x "$candidate" ]; then
      NVPN="$candidate"
      break
    fi
  done
fi
```

If it is still unset, search only application roots for a bundled resource rather than scanning the whole filesystem:

```bash
for root in /Applications "$HOME/Applications"; do
  if [ -d "$root" ]; then
    candidate=$(find "$root" -path '*/Contents/Resources/nvpn' -type f -perm -111 -print -quit 2>/dev/null)
    if [ -n "$candidate" ]; then
      NVPN="$candidate"
      break
    fi
  fi
done
```

The app GUI executable, `*/Contents/MacOS/Nostr VPN`, is not a replacement for `*/Contents/Resources/nvpn`.

## Linux

Try `PATH`, then the usual Cargo, user, and system locations:

```bash
if command -v nvpn >/dev/null 2>&1; then
  NVPN=$(command -v nvpn)
else
  for candidate in \
    "$HOME/.cargo/bin/nvpn" \
    "$HOME/.local/bin/nvpn" \
    "$HOME/bin/nvpn" \
    "/usr/local/bin/nvpn" \
    "/usr/local/sbin/nvpn" \
    "/usr/bin/nvpn" \
    "/usr/sbin/nvpn" \
    "/opt/nostr-vpn/nvpn"; do
    if [ -x "$candidate" ]; then
      NVPN="$candidate"
      break
    fi
  done
fi
```

If the GUI was installed as an AppImage or another desktop package, inspect its documented install directory for a file named `nvpn`; do not search `/` or run an arbitrary executable found in a download directory.

## Windows PowerShell

Try command lookup, then common native-app and user-install locations:

```powershell
$nvpn = (Get-Command nvpn.exe -ErrorAction SilentlyContinue).Source
if (-not $nvpn) { $nvpn = (Get-Command nvpn -ErrorAction SilentlyContinue).Source }

$candidates = @(
  "$env:LOCALAPPDATA\Programs\Nostr VPN\nvpn.exe",
  "$env:LOCALAPPDATA\Programs\Nostr VPN\resources\nvpn.exe",
  "$env:LOCALAPPDATA\Nostr VPN\nvpn.exe",
  "$env:ProgramFiles\Nostr VPN\nvpn.exe",
  "$env:ProgramFiles\Nostr VPN\resources\nvpn.exe",
  "${env:ProgramFiles(x86)}\Nostr VPN\nvpn.exe",
  "${env:ProgramFiles(x86)}\Nostr VPN\resources\nvpn.exe"
)

if (-not $nvpn) {
  $nvpn = $candidates |
    Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } |
    Select-Object -First 1
}
```

If needed, search only `$env:LOCALAPPDATA\Programs`, `$env:ProgramFiles`, and `${env:ProgramFiles(x86)}` for `nvpn.exe`, with `-ErrorAction SilentlyContinue`.

## Verify the result

```bash
test -n "$NVPN" && "$NVPN" version --json
```

PowerShell:

```powershell
if (-not $nvpn) { throw "nvpn executable not found" }
& $nvpn version --json
```

If verification fails, report the path and error. Do not install, copy, symlink, or modify `PATH` unless the user asks for that setup change.
