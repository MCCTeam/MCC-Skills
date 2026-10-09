#!/usr/bin/env python3
"""Archive an explicitly staged DMCBK plugin and write its SHA-256 digest."""

import argparse
import hashlib
import tomllib
import zipfile
from pathlib import Path, PurePosixPath


EXCLUDED_PARTS = {"bin", "obj", ".git", "userdata", "cache", "transactions"}
SHARED_PREFIXES = ("dmcbk.", "umpk.", "system.")
SHARED_NAMES = {
    "brigadier.net.dll", "microsoft.extensions.logging.abstractions.dll",
    "tomlet.dll", "system.dll", "netstandard.dll", "mscorlib.dll", "microsoft.csharp.dll",
}


def package_path(root: Path, value: str) -> Path:
    """Return an existing file named by a package-relative path."""
    parts = value.split("/")
    if (
        not value
        or PurePosixPath(value).is_absolute()
        or any(part in {"", ".", ".."} for part in parts)
        or any(character in value for character in ("\\", ":", "\0"))
    ):
        raise ValueError(f"Invalid package path: {value!r}")
    path = root.joinpath(*parts)
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError(f"Package path leaves the staging directory: {value!r}")
    if not path.is_file():
        raise ValueError(f"Required package file is absent: {value}")
    return path


def create_archive(root: Path, output: Path) -> str:
    """Check staged payloads and create a stable ZIP with its manifest at root."""
    manifest_path = package_path(root, "plugin.toml")
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    required = {
        "schema-version", "id", "version", "kind", "target", "entry",
        "framework", "api-version", "dmcbk", "umpk", "needs",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise ValueError(f"Manifest fields are absent: {', '.join(missing)}")
    if manifest["schema-version"] != 2 or manifest["framework"] != "net10.0":
        raise ValueError("The archive requires schema 2 and framework net10.0.")
    kind = manifest["kind"]
    expected_suffix = {"source": ".cs", "compiled": ".dll"}.get(kind)
    if expected_suffix is None:
        raise ValueError("The manifest kind must be source or compiled.")
    entry = package_path(root, manifest["entry"])
    if entry.suffix.lower() != expected_suffix:
        raise ValueError("The entry extension does not match the manifest kind.")
    for dependency in manifest.get("deps", []):
        package_path(root, dependency)
    for exported in manifest.get("exports", {}).get("assemblies", []):
        if exported != "entry":
            package_path(root, exported)

    if output.is_relative_to(root):
        raise ValueError("Write release archives outside the staged package.")
    files = sorted(path for path in root.rglob("*") if path.is_file() or path.is_symlink())
    for path in files:
        relative = path.relative_to(root)
        if path.is_symlink() or any(part in EXCLUDED_PARTS for part in relative.parts):
            raise ValueError(f"Unexpected staging path: {relative.as_posix()}")
        if path.suffix.lower() == ".dll" and (
            path.name.lower().startswith(SHARED_PREFIXES) or path.name.lower() in SHARED_NAMES
        ):
            raise ValueError(f"Shared host or framework assembly in package: {path.name}")
        if path.suffix.lower() in {".csproj", ".sln", ".slnx", ".pdb"}:
            raise ValueError(f"Author build file in package: {relative.as_posix()}")
        if kind == "compiled" and path.suffix.lower() == ".cs":
            raise ValueError(f"Author source file in compiled package: {relative.as_posix()}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())

    with output.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Clean staged package directory")
    parser.add_argument("output", type=Path, help="ZIP path outside the package directory")
    arguments = parser.parse_args()
    try:
        digest = create_archive(arguments.package.resolve(), arguments.output.resolve())
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        parser.exit(1, f"Package error: {error}\n")
    print(f"Archive: {arguments.output.resolve()}")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
