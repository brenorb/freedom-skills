# Runtime fallback

Use only after the requested command is unavailable or fails to launch. Preserve a user-provided executable path or launcher. Do not globally install tools or change shell configuration merely to answer a Script question.

With Nix available, a one-shot debugger is:

```sh
printf '%s\n' '[OP_3 OP_DUP OP_ADD]' | nix run nixpkgs#btcdeb
```

For companion executables, use `nix shell nixpkgs#btcdeb -c btcc OP_3 OP_DUP OP_ADD` or `nix shell nixpkgs#btcdeb -c tap -h`. Record the resolved package version/revision for reproducible work rather than assuming an unpinned nixpkgs matches this skill.

For an existing upstream source checkout, local build commands are `./autogen.sh`, `./configure`, and `make`; the resulting `./btcdeb`, `./btcc`, and `./tap` can be used without `sudo make install`. Configure dependency errors guide the next action. Upstream lists libtool, OpenSSL development files, autoconf/automake, and pkg-config. If dependencies or network are unavailable, report the exact blocker and provide a source-backed command without claiming execution.

An existing Docker workflow can build upstream's Dockerfile and run the resulting executables. For batch stdin preserve input with `docker run --rm -i IMAGE btcdeb`; interactive debugging uses `-it`. Avoid inventing a published image or Python/npm package named btcdeb.

Offline tasks must stay offline. Use installed `btcdeb -h`, `tap -h`, interactive `tf -h`, local source/docs, and bundled references. Setup success is not evidence that an example was executed.

Sources: [upstream build/Docker instructions](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/README.md), [Nixpkgs package](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/bt/btcdeb/package.nix).
