# Release procedure

## Prepare independent author projects

Use a standalone plugin repository with source, manifests, tests, resources, and catalogue history.
Keep binary archives outside Git history. Host them as immutable release assets.
Authoring does not require MCC, DMCBK, or UMPK source checkouts.

Use pinned package versions for compiled authoring and any shared-model packaging tool.
The current example contract targets `DMCBK.PluginSdk` `0.1.0-preview.3` and UMPK `0.9.0-beta.4`.
These pins identify a tested preview contract. Obtain and test newer pins before changing them.
Use a private feed explicitly for unpublished packages.
Use an isolated NuGet cache when replacing development packages at the same preview version.

Do not include host contracts in a plugin archive.
Keep native dependencies at the paths that the compiled dependency resolver expects.
Check private dependency licensing and include relevant notices.

## Source, compiled, or mixed

| Publication | Inputs | Typical target |
| --- | --- | --- |
| Source-only | One entry C# file and declared private assemblies | `any` |
| Compiled managed | Entry DLL, private assemblies, resources | `any` |
| Compiled native | Managed entry and platform-specific native payload | Exact tested target |
| Mixed | Separate source and compiled archives for one release | Each archive's own target |

A mixed release shares version, API, library ranges, framework, capabilities, providers, and host restrictions across all asset manifests.
Its manifests differ in kind, target, entry, and package-specific private dependencies.
Compose the complete asset list before first publication.
Adding an asset to a published version changes its immutable release identity.

Runtime source compilation does not process project files or perform NuGet restores.
A multi-file author project needs a compiled asset or a deliberate single-file source alternative.

## Bundled deterministic helper

Run `scripts/pack_release.py` with Python 3.11 or later.
The script uses the standard library only.

```sh
python scripts/pack_release.py pack examples/local-marketplace/plugins/marketplace-demo --output examples/local-marketplace/release-assets --base-url http://127.0.0.1:8765/release-assets/
python scripts/pack_release.py verify examples/local-marketplace/release-assets
```

For an installed skill, substitute its absolute script and input paths.

The helper accepts an already prepared package folder with its final root manifest.
It does not build source, change manifest kind, or upload files.
For a compiled asset, prepare a separate folder with a compiled manifest and payload.

It produces:

```text
<id>-<version>-<kind>-<target>.zip
<id>-<version>-<kind>-<target>.zip.sha256
<id>-<version>-<kind>-<target>.zip.catalogue.toml
```

Packaging uses these deterministic rules:

- Sort archive entries by their forward-slash paths.
- Store each entry without compression.
- Fix every timestamp at `1980-01-01 00:00:00`.
- Mark each entry as a regular Unix file with mode `0644`.
- Copy original file bytes without newline conversion.
- Reject an existing output whose bytes differ.

Stored entries avoid differences between compression-library versions.
Input line endings still affect bytes. Use consistent line endings in the author repository.
Changing the asset base URL changes the catalogue fragment.
The helper rejects that change in an existing output folder.
Select final public URLs before creating production metadata.

The helper includes:

- Root `plugin.toml`.
- Entry source or compiled DLL.
- Declared `deps` files.
- Declared export files other than the `entry` token.
- `lang`, `man`, and `defaults` resources.
- License and third-party notice files.
- Compiled `.deps.json`, `.runtimeconfig.json`, `.so`, and `.dylib` files.
- Compiled native DLL files below `runtimes/`.

Declare other managed private DLLs in `deps`.
Move root author settings to `defaults/settings.toml` before using this helper.
The shared DMCBK packager can convert root author settings automatically.
This helper deliberately requires the final package layout.

The helper rejects links, duplicate case-insensitive paths, and unsafe package paths.
It rejects obvious DMCBK, UMPK, and framework DLL names.
Filename checks cannot establish full assembly identity.
Use host validation and runtime loading checks for final acceptance.

The helper checks basic manifest structure. MCC checks the complete manifest and shared range syntax.
The helper does not compose multiple assets or append production catalogue history automatically.

## Archive acceptance rules

The installer processes ZIP archives with root manifests.
It checks SHA-256 before extraction and manifest agreement before activation.
It rejects unsafe paths, case-insensitive duplicates, and links or unsupported archive entry types.

Use portable paths. Avoid reserved Windows device names and names with trailing spaces or dots.
Do not include traversal paths, symlinks, or absolute file names.

Default limits are:

| Limit | Default |
| --- | --- |
| Downloaded archive | 128 MiB |
| Total expanded entries | 512 MiB |
| Archive entries | 10,000 |
| Marketplace metadata document | 4 MiB |

Hosts can configure limits. Stay below these defaults for broadly usable assets.
A valid hexadecimal digest is insufficient if the downloaded archive has different bytes.

## Shared packaging APIs

A .NET packaging tool can use pinned `DMCBK.Marketplace` packages.
The shared APIs check schema models directly:

- `PluginPackageBuilder.Pack` creates an archive, digest sidecar, and catalogue fragment.
- `ReleaseCatalogueBuilder.Compose` combines compatible unpublished asset fragments.
- `ReleaseCatalogueBuilder.Publish` appends new versions to existing history.

The shared packager excludes host assemblies through their assembly identities.
It copies resource directories and converts author settings into packaged defaults.
Prepare compiled payloads outside `bin` and `obj` directories inside the selected payload root.
The packager excludes these build directories.

`Compose` requires matching release metadata across asset fragments.
`Publish` preserves previous releases. Only the yank flag can change for an existing version.
Do not add duplicate `(kind, target)` assets with different URLs or hashes.

## Check each stage

1. Check plugin behavior with author tests.
2. Build every compiled target that the release declares.
3. Check each prepared package folder with MCC.
4. Pack every asset.
5. Extract each generated archive into a disposable folder.
6. Check each extracted folder with MCC.
7. Compose the complete release catalogue.
8. Check the index and all release catalogues with MCC.
9. Test actual installation and activation in a disposable runtime.
10. Check the generated lock and user data.

These commands assume the distributed `Mcc.Cli` executable is available:

```sh
Mcc.Cli --validate-plugin /absolute/path/prepared-package
Mcc.Cli --validate-marketplace /absolute/path/marketplace
Mcc.Cli MarketplaceDemo - --configurations /absolute/path/test-runtime/configurations --connection.auto-connect=false
```

For a framework-dependent distribution, use `dotnet /absolute/path/Mcc.Cli.dll ...`.
These commands do not require a source project.
Keep each installation's configuration folder below its own runtime parent.

Validation does not prove source compilation, native loading, activation, or gameplay behavior.
Record build success and execution success separately for each target.
Use a controlled server for plugins that require a Minecraft session.

## Publish in order

1. Obtain the previous public catalogue.
2. Increase the plugin version for changed release content.
3. Build and execute the available target checks.
4. Produce every asset and digest.
5. Compose the complete release.
6. Check compatibility and dependency declarations.
7. Upload immutable archives and digest sidecars.
8. Download each asset through its final URL.
9. Check the downloaded digest.
10. Append the new release to the historical catalogue.
11. Publish the catalogue and any index changes.
12. Test installation from the published metadata.

Do not publish a catalogue entry before its archive exists.
Retain older entries and archives. Use yanking for a bad release.
Do not rewrite a published digest to describe replacement bytes.

A changed payload, compatibility range, dependency, target list, asset URL, or export contract needs a new release version.
The manifest and archive remain immutable for the old version.
Keep build provenance, tested runtimes, and final digests in the release report.

## Negative fixtures and recovery checks

Create negative metadata under a disposable test publisher.
Keep it separate from the public catalogue.

Check these relevant cases:

- A bad digest fails before activation.
- A missing target explains its unavailable asset.
- A mixed release requires source fallback when compiled selection fails.
- Explicit source selection fails when source is absent.
- Required version conflicts fail before package changes.
- A pinned provider blocks an incompatible update.
- A missing optional provider does not prevent the consumer's supported behavior.
- A source compiler error preserves the previous active graph.
- An activation failure restores the prior package graph.

Do not claim these results unless the test executed.
The bundled source fixture checks local activation. It does not establish native or live-server behavior.
