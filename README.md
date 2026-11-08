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

Wheels support x86-64 and ARM64 Linux and macOS. On Windows, use WSL.

## Release

Configure a PyPI trusted publisher for repository `kdrag-vampire`, workflow
`wheels.yml`, and environment `pypi`. Push a `v*` tag to publish.

Build locally with:

```sh
uv build
```

Building requires Git, CMake, and a C++20 compiler. The build fetches the pinned
upstream release and its dependencies. Set `VAMPIRE_BINARY` to package an existing
binary instead, or `VAMPIRE_WHEEL_TAG` to override the platform tag.

Vampire is [BSD-3-Clause](https://github.com/vprover/vampire/blob/v5.1.0/LICENCE).
The executable also includes MIT-licensed MiniSat, CaDiCaL, and Z3, and mini-gmp
under GPL-2.0-or-later. See [COPYING](COPYING) for notices and license texts.
The corresponding source is the linked upstream tag, including its pinned
submodules.
