# Security Policy — sdl2-game-engine-starter

## Scope

This repository is a **developer starter kit**. It ships build orchestration
tooling, a project generator, and a C++/SDL2 engine skeleton. It is not a
networked service. It does not ship a server binary.

The attack surface that matters here:

- The project generator writes files into a target directory. Path traversal
  and symlink escape are in scope.
- The asset pipeline reads arbitrary user-provided asset files. Malformed
  image/audio parsing in the C++ layer is in scope.
- The build orchestrator shells out to `cmake`, `ninja`, and the system
  compiler. Command injection through user-supplied config is in scope.

## Reporting

Open a private security advisory on GitHub. Do not file a public issue for a
memory-safety bug in the C++ layer — those get coordinated disclosure.

Include: affected file, commit SHA, minimal reproducer, and the platform you
reproduced on (Windows 10/11, Linux distro, macOS version).

## Supported versions

Only the `main` branch is supported. Tagged releases get fixes backported for
one minor version.

## Known non-issues

- The starter engine has no sandbox. Games built on it run with the user's
  privileges. That is by design.
- The generator will happily write into a directory you own. Do not run it as
  Administrator against a system path. That is on you, not on us.