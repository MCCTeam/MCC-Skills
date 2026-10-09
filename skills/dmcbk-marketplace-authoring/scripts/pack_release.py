#!/usr/bin/env python3
"""Pack prepared schema-2 folders or check generated assets. Python 3.11+, stdlib only."""

import argparse
import hashlib
import io
import json
import re
import stat
import sys
import tomllib
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

TARGETS = {
    "any", "win-x86", "win-x64", "win-arm64", "linux-x64", "linux-arm64",
    "linux-arm", "linux-musl-x64", "linux-musl-arm64", "linux-musl-arm",
    "osx-x64", "osx-arm64",
}
SHARED_PREFIXES = ("dmcbk.", "umpk.", "system.")
SHARED_NAMES = {"netstandard.dll", "mscorlib.dll", "microsoft.csharp.dll"}
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"} | {f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)}
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?\Z")
IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
DEFAULT_STAMP = (1980, 1, 1, 0, 0, 0)


def quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def package_path(value: str) -> bool:
    return bool(value) and not any(c in value for c in "\\:\0<>\"|?*") and all(
        part not in ("", ".", "..") and not part.endswith((".", " "))
        and part.split(".")[0].upper() not in RESERVED_NAMES for part in value.split("/"))


def check_manifest(manifest: dict) -> None:
    if manifest.get("schema-version") != 2:
        raise ValueError("Set schema-version to 2.")
    if not IDENTITY.fullmatch(manifest.get("id", "")):
        raise ValueError("Use a safe plugin ID.")
    if not VERSION.fullmatch(manifest.get("version", "")):
        raise ValueError("Use a complete SemVer version.")
    kind = manifest.get("kind")
    if kind not in ("source", "compiled") or manifest.get("target") not in TARGETS:
        raise ValueError("Declare a supported kind and target.")
    entry = manifest.get("entry", "")
    if not package_path(entry) or not entry.lower().endswith(".cs" if kind == "source" else ".dll"):
        raise ValueError("Match the entry extension to the package kind.")
    if manifest.get("framework") != "net10.0":
        raise ValueError("Set framework to net10.0.")
    for key in ("api-version", "dmcbk", "umpk"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError(f"Declare {key} explicitly.")
    for dependency in manifest.get("deps", []):
        if not package_path(dependency) or not dependency.lower().endswith(".dll"):
            raise ValueError(f"Invalid private assembly path: {dependency}")
    for dependency in manifest.get("exports", {}).get("assemblies", []):
        if dependency != "entry" and not package_path(dependency):
            raise ValueError(f"Invalid export path: {dependency}")


def collect(folder: Path, manifest: dict) -> dict[str, bytes]:
    if folder.is_symlink():
        raise ValueError("Use a regular package folder.")
    files: dict[str, bytes] = {}
    names: set[str] = set()

    def add(path: Path) -> None:
        relative = path.relative_to(folder).as_posix()
        if not package_path(relative) or any(part.startswith(".") for part in relative.split("/")):
            raise ValueError(f"Invalid package path: {relative}")
        current = path
        while current != folder:
            if current.is_symlink():
                raise ValueError(f"Remove the link: {relative}")
            current = current.parent
        if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise ValueError(f"Use a regular file: {relative}")
        if relative.casefold() in names:
            raise ValueError(f"Duplicate package path: {relative}")
        if path.suffix.lower() == ".dll":
            name = path.name.casefold()
            if name.startswith(SHARED_PREFIXES) or name in SHARED_NAMES:
                raise ValueError(f"Do not package a host contract: {relative}")
        names.add(relative.casefold())
        files[relative] = path.read_bytes()

    required = ["plugin.toml", manifest["entry"], *manifest.get("deps", [])]
    required += [name for name in manifest.get("exports", {}).get("assemblies", []) if name != "entry"]
    for relative in dict.fromkeys(required):
        add(folder / relative)
    for resource in ("lang", "man", "defaults"):
        root = folder / resource
        if root.is_symlink():
            raise ValueError(f"Remove the resource link: {resource}")
        if root.exists():
            for path in sorted(root.rglob("*")):
                if path.is_symlink():
                    raise ValueError(f"Remove the link: {path.relative_to(folder)}")
                if path.is_file():
                    add(path)
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "THIRD-PARTY-NOTICES.md", "THIRD-PARTY-NOTICES.txt"):
        if (folder / name).exists():
            add(folder / name)
    if (folder / "settings.toml").exists():
        raise ValueError("Move package defaults to defaults/settings.toml before packaging.")
    if manifest["kind"] == "compiled":
        for path in sorted(folder.rglob("*")):
            relative = path.relative_to(folder).as_posix()
            if path.is_symlink():
                raise ValueError(f"Remove the link: {relative}")
            if path.is_file() and relative not in files and (
                path.name.endswith((".deps.json", ".runtimeconfig.json", ".so", ".dylib"))
                or relative.startswith("runtimes/") and path.suffix.lower() == ".dll"
            ):
                add(path)
    if len(files) > 10000 or sum(map(len, files.values())) > 512 * 1024 * 1024:
        raise ValueError("Package exceeds the default installer limits.")
    return files


def archive_bytes(files: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, content in sorted(files.items()):
            item = zipfile.ZipInfo(name, DEFAULT_STAMP)
            item.create_system = 3
            item.external_attr = (stat.S_IFREG | 0o644) << 16
            item.compress_type = zipfile.ZIP_STORED
            archive.writestr(item, content)
    payload = output.getvalue()
    if len(payload) > 128 * 1024 * 1024:
        raise ValueError("Archive exceeds the default download limit.")
    return payload


def catalogue_text(manifest: dict, url: str, digest: str) -> str:
    lines = ["schema-version = 2", f"id = {quote(manifest['id'])}", "", "[[releases]]"]
    for key in ("version", "api-version", "dmcbk", "umpk", "framework"):
        lines.append(f"{key} = {quote(manifest[key])}")
    lines += [f"needs = {json.dumps(manifest.get('needs', []), ensure_ascii=False)}", "yanked = false", "assets = ["]
    lines.append("  { " + ", ".join(f"{key} = {quote(value)}" for key, value in (
        ("kind", manifest["kind"]), ("target", manifest["target"]), ("url", url), ("sha256", digest))) + " },")
    lines.append("]")
    for table in ("requires", "optional", "hosts"):
        values = manifest.get(table, {})
        if values:
            lines += ["", f"[releases.{table}]"]
            lines += [f"{quote(key)} = {quote(value)}" for key, value in sorted(values.items())]
    return "\n".join(lines) + "\n"


def write_immutable(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"Existing release differs: {path.name}. Use a new version or a new output folder.")
        return
    with path.open("xb") as stream:
        stream.write(content)


def pack(args: argparse.Namespace) -> None:
    folder = args.folder.absolute()
    manifest = tomllib.loads((folder / "plugin.toml").read_text(encoding="utf-8"))
    check_manifest(manifest)
    base = urlparse(args.base_url)
    if base.scheme not in ("http", "https") or not base.netloc or not args.base_url.endswith("/") or base.query or base.fragment:
        raise ValueError("Use an absolute HTTP(S) base URL ending in /, without a query or fragment.")
    name = f"{manifest['id']}-{manifest['version']}-{manifest['kind']}-{manifest['target']}.zip"
    payload = archive_bytes(collect(folder, manifest))
    digest = hashlib.sha256(payload).hexdigest()
    catalogue = catalogue_text(manifest, urljoin(args.base_url, name), digest).encode("utf-8")
    # Check every existing output before writing any new output.
    outputs = {
        args.output / name: payload,
        args.output / (name + ".sha256"): f"{digest}  {name}\n".encode("ascii"),
        args.output / (name + ".catalogue.toml"): catalogue,
    }
    for path, content in outputs.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"Existing release differs: {path.name}. Use a new version or output folder.")
    args.output.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        write_immutable(path, content)
    print(f"{digest}  {args.output / name}")


def verify(args: argparse.Namespace) -> None:
    archives = sorted(args.output.glob("*.zip"))
    if not archives:
        raise ValueError("No ZIP archives exist in the output folder.")
    for path in archives:
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        sidecar = path.with_name(path.name + ".sha256").read_text(encoding="ascii")
        if sidecar != f"{digest}  {path.name}\n":
            raise ValueError(f"Digest sidecar differs: {path.name}")
        catalogue = tomllib.loads(path.with_name(path.name + ".catalogue.toml").read_text(encoding="utf-8"))
        assets = catalogue["releases"][0]["assets"]
        if len(assets) != 1 or assets[0]["sha256"] != digest:
            raise ValueError(f"Catalogue digest differs: {path.name}")
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if "plugin.toml" not in names or len(set(name.casefold() for name in names)) != len(names):
                raise ValueError(f"Invalid manifest location or duplicate archive path: {path.name}")
            for item in archive.infolist():
                if not package_path(item.filename) or stat.S_IFMT(item.external_attr >> 16) != stat.S_IFREG:
                    raise ValueError(f"Invalid archive entry: {item.filename}")
            if archive.testzip() is not None:
                raise ValueError(f"Archive CRC check failed: {path.name}")
            manifest = tomllib.loads(archive.read("plugin.toml").decode("utf-8"))
            check_manifest(manifest)
            expected = catalogue_text(manifest, assets[0]["url"], digest)
            actual = path.with_name(path.name + ".catalogue.toml").read_text(encoding="utf-8")
            if expected != actual:
                raise ValueError(f"Catalogue and manifest differ: {path.name}")
        print(f"OK {digest}  {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    packing = commands.add_parser("pack", help="Pack one prepared package folder.")
    packing.add_argument("folder", type=Path)
    packing.add_argument("--output", required=True, type=Path)
    packing.add_argument("--base-url", required=True)
    packing.set_defaults(run=pack)
    checking = commands.add_parser("verify", help="Check all generated archives and digest sidecars.")
    checking.add_argument("output", type=Path)
    checking.set_defaults(run=verify)
    args = parser.parse_args()
    try:
        args.run(args)
    except (OSError, ValueError, KeyError, TypeError, tomllib.TOMLDecodeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
