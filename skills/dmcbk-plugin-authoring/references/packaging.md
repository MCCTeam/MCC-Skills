# Packaging and platform assets

## Source and compiled staging

Create a clean staging directory outside build output.
Stage only the files required by that asset.

| File | Source asset | Compiled asset |
| --- | --- | --- |
| `plugin.toml` | Required | Required |
| Entry `.cs` | Required | Exclude |
| Entry `.dll` | Exclude | Required |
| Entry `.deps.json` | Only when a packaged helper needs it | Include when dependency resolution requires it |
| Private helper DLLs | Explicit `deps` | Explicit private dependencies |
| Native libraries | Test and package matching targets | Test and package matching targets |
| `lang`, `man`, `defaults` | Include as used | Include as used |
| Host contract DLLs | Exclude | Exclude |
| Author project, `bin`, `obj` | Exclude | Exclude |

Do not copy `bin` wholesale.
It can contain DMCBK, UMPK, framework, compiler, and unrelated build assemblies.
The package's loader shares designated contracts with the host.
Private copies can break type identity or cause rejection.

The compiled Session Journal template has no private helper library.
Its package needs the entry DLL and resource files.
Its generated dependency file can accompany the DLL.
The package script does not include transitive host assemblies.

## Archive the package

The supplied `scripts/package_plugin.py` creates a ZIP from an explicitly staged package.
It checks manifest paths and source versus compiled entry extensions.
It rejects common accidental build and user-data directories.
It rejects packaged DMCBK and UMPK assemblies.
It is a staging check, not a replacement for runtime validation.

Run it after copying the asset to an independent author directory:

```sh
python3 /absolute/path/to/skill/scripts/package_plugin.py \
  /absolute/path/to/staged-package \
  /absolute/path/to/releases/session-journal-1.0.0-any.zip
```

The output archive contains `plugin.toml` at its root.
The script prints the SHA-256 digest and writes a `.sha256` companion file.
Keep both files when distributing an asset.
Recheck the checksum after an upload.

The digest identifies the payload.
It does not prove that the plugin's behavior is trustworthy.

## Runtime targets

| Execution environment | Supported target values |
| --- | --- |
| Portable managed code | `any` |
| Windows | `win-x86`, `win-x64`, `win-arm64` |
| Linux with glibc | `linux-x64`, `linux-arm64`, `linux-arm` |
| Linux with musl | `linux-musl-x64`, `linux-musl-arm64`, `linux-musl-arm` |
| macOS | `osx-x64`, `osx-arm64` |

The target follows the host process, not only the machine's processor.
An x86 process on Windows x64 requires `win-x86` native code.
Linux x86 and macOS 32-bit are not supported plugin targets.

Use one `any` archive for portable managed code when possible.
Do not use `any` for an architecture-specific native library.

## Native dependencies

The runtime uses `AssemblyDependencyResolver` for managed and native dependencies.
Its metadata and paths must match the packaged files.

1. Choose each supported runtime identifier, such as `win-x64` or `linux-arm64`.
2. Build or publish the author project for that identifier.
3. Include the entry assembly's `.deps.json` file.
4. Include the target's native library and required private managed helpers.
5. Preserve the paths that the dependency metadata expects.
6. Exclude shared host and framework assemblies.
7. Set the asset manifest's matching `target`.
8. Load and execute the native operation on that actual target.

Example author build commands:

```sh
dotnet publish NativePlugin.csproj --configuration Release \
  --runtime win-x64 --self-contained false --output staging-build/win-x64
dotnet publish NativePlugin.csproj --configuration Release \
  --runtime linux-arm64 --self-contained false --output staging-build/linux-arm64
```

These commands produce candidate build files.
They do not produce a final plugin package automatically.
They do not prove execution on Windows x64 or Linux arm64.
Stage selected files into separate package directories before archiving.
Check native exports, dynamic dependencies, and actual host loading on each target.

Collectible assembly contexts permit unloading.
Retained objects, active tasks, and native handles can delay release.
Do not depend on overwriting a loaded DLL.
Reload from a new immutable payload or a safe development copy.

## Marketplace release

The authoring outputs are package assets.
Publishing a marketplace also requires its catalogue and release records.
Use the host's marketplace tools and current schema documentation for those records.
Do not invent catalogue fields from the plugin manifest.

Release sequence:

1. Assign a new plugin SemVer version.
2. Build and test each declared asset.
3. Create archives and checksums.
4. Upload immutable assets.
5. Check the uploaded payloads and digests.
6. Publish the catalogue entry after the assets become available.

A release can offer source assets, compiled assets, or both.
Selection prefers an exact compiled target and then compiled `any`.
Source-only releases compile automatically.
Mixed releases need explicit source fallback permission when compiled assets do not match.

Give a changed payload or compatibility declaration a new release version.
Yank a broken release instead of removing its history.
Keep prior immutable assets available for locks and rollback.

## Release notes

State these items:

- Plugin version and changed behavior.
- Tested DMCBK, UMPK, API, and host versions.
- Supported process targets.
- Required and optional plugin ranges.
- Settings or data migrations.
- Required manual steps and downgrade limits.
- Checks that remain untested.

Marketplace development imports reject symlink ancestors.
Use physical paths when a platform supplies an alias path.
Use a separate runtime directory for MCC configuration and test data.
