# kdrag-vampire

[Vampire 5.1.0](https://github.com/vprover/vampire/tree/v5.1.0) with higher-order
logic and statically linked Z3 support, packaged in Python wheels.

```sh
uv add kdrag-vampire
```

```python
import subprocess
from vampire import vampire_path

subprocess.run([vampire_path, "--version"], check=True)
```

Wheels support x86-64 and ARM64 Linux and macOS, and x86-64 Windows.
Windows wheels bundle the Cygwin runtime; no separate Cygwin installation is needed.

## Release

Configure a PyPI trusted publisher for repository `kdrag-vampire`, workflow
`wheels.yml`, and environment `pypi`. Push a `v*` tag to publish.

Build locally with:

```sh
uv build
```

Linux and macOS builds require Git, CMake, and a C++20 compiler, and fetch the
pinned upstream source and its dependencies. Windows builds fetch the official
release binary and verify its SHA-256 checksum. Set `VAMPIRE_BINARY` to package
an existing binary instead, or `VAMPIRE_WHEEL_TAG` to override the platform tag.
For a custom Windows build, place `cygwin1.dll` beside `vampire.exe`.

Vampire is [BSD-3-Clause](https://github.com/vprover/vampire/blob/v5.1.0/LICENCE).
The executable also includes MIT-licensed MiniSat, CaDiCaL, and Z3, and mini-gmp
under GPL-2.0-or-later. Windows wheels additionally include the
[Cygwin runtime](https://cygwin.com/licensing.html) under LGPL-3.0-or-later.
See [COPYING](COPYING) for notices and license texts.
The corresponding source is the linked upstream tag, including its pinned
submodules.
