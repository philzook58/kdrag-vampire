import hashlib
import os
import subprocess
import sys
import sysconfig
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from setuptools import Distribution, setup
from setuptools.command.bdist_wheel import bdist_wheel as _bdist_wheel
from setuptools.command.build_py import build_py as _build_py

VAMPIRE_REF = "v5.1.0"
VAMPIRE_EXECUTABLE = "vampire.exe" if sys.platform == "win32" else "vampire"
VAMPIRE_WINDOWS_SHA256 = "b98d0c6b4a42e11c25243ca31b3cbabd1673b437c994263166804b92b715de33"
VAMPIRE_WINDOWS_DLLS = [
    (
        "libiconv/libiconv2/libiconv2-1.17-1.tar.xz",
        "695679eac95451bdbffb01309aba58104f10734e5998e8a4619e457505d58c00",
        "cygiconv-2.dll",
    ),
    (
        "gettext/libintl8/libintl8-0.22.5-1.tar.xz",
        "aa981c2583e187c5c07c75132d714fe3b8a4a81f585e9b5de64f0bf8c8dd211f",
        "cygintl-8.dll",
    ),
]


def download_verified(url, target, digest):
    if not target.exists():
        urllib.request.urlretrieve(url, target)
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"Archive checksum mismatch: {target.name}")
    return target


def get_vampire_binary():
    if binary := os.environ.get("VAMPIRE_BINARY"):
        return Path(binary)
    if sys.platform == "win32":
        if sysconfig.get_platform() != "win-amd64":
            raise RuntimeError("Windows wheels currently require x86-64 Python.")
        source = Path("build/vampire-windows").resolve()
        source.mkdir(parents=True, exist_ok=True)
        archive = download_verified(
            f"https://github.com/vprover/vampire/releases/download/{VAMPIRE_REF}/vampire-Windows-X64.zip",
            source / "vampire.zip", VAMPIRE_WINDOWS_SHA256,
        )
        with zipfile.ZipFile(archive) as files:
            for name in ("vampire.exe", "cygwin1.dll"):
                (source / name).write_bytes(files.read(name))
        for package, digest, name in VAMPIRE_WINDOWS_DLLS:
            archive = download_verified(
                f"https://mirrors.kernel.org/sourceware/cygwin/x86_64/release/{package}",
                source / Path(package).name, digest,
            )
            with tarfile.open(archive) as files:
                (source / name).write_bytes(files.extractfile(f"usr/bin/{name}").read())
        return source / "vampire.exe"

    source = Path("build/vampire-source").resolve()
    if not source.exists():
        subprocess.run(
            [
                "git",
                "clone",
                "--depth=1",
                f"--branch={VAMPIRE_REF}",
                "https://github.com/vprover/vampire.git",
                str(source),
            ],
            check=True,
        )
    subprocess.run(
        ["git", "submodule", "update", "--init", "--depth=1", "cadical", "viras", "z3"],
        cwd=source,
        check=True,
    )
    # Statically link Z3 so the wheel needs no separate Z3 installation.
    subprocess.run(
        [
            "cmake", "-S", str(source / "z3"), "-B", str(source / "z3/build"),
            "-DCMAKE_BUILD_TYPE=Release",
            "-DZ3_BUILD_EXECUTABLE=OFF",
            "-DZ3_BUILD_TEST_EXECUTABLES=OFF",
            "-DZ3_BUILD_LIBZ3_SHARED=OFF",
        ],
        check=True,
    )
    subprocess.run(["cmake", "--build", str(source / "z3/build"), "--parallel", "4"], check=True)
    subprocess.run(
        [
            "cmake", "-S", str(source), "-B", str(source / "build"),
            "-DCMAKE_BUILD_TYPE=Release", "-DCCACHE_PROGRAM=OFF",
        ],
        check=True,
    )
    subprocess.run(
        ["cmake", "--build", str(source / "build"), "--target", "vampire", "--parallel", "4"],
        check=True,
    )
    binary = source / "build/vampire"
    subprocess.run(["strip", str(binary)], check=True)
    return binary


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


class build_py(_build_py):
    def run(self):
        super().run()
        binary = get_vampire_binary()
        files = [(binary, VAMPIRE_EXECUTABLE), (Path("COPYING"), "COPYING")]
        if sys.platform == "win32":
            files.extend((dll, dll.name) for dll in binary.parent.glob("*.dll"))
        for source, name in files:
            target = Path(self.build_lib, "vampire", name)
            self.mkpath(str(target.parent))
            self.copy_file(str(source), str(target))
        Path(self.build_lib, "vampire", VAMPIRE_EXECUTABLE).chmod(0o755)


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        self.root_is_pure = False

    def get_tag(self):
        platform = os.environ.get("VAMPIRE_WHEEL_TAG")
        platform = platform or sysconfig.get_platform().replace("-", "_").replace(".", "_")
        return "py3", "none", platform


setup(
    distclass=BinaryDistribution,
    cmdclass={"build_py": build_py, "bdist_wheel": bdist_wheel},
)
