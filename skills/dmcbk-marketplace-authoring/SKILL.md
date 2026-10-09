---
name: dmcbk-marketplace-authoring
description: Create, check, package, publish, or repair DMCBK schema-2 plugin marketplaces for MCC or another DMCBK host. Use whenever the user mentions mcc-marketplace.toml, release catalogues, plugin assets, platform targets, source fallback, checksums, dependency resolution, yanking, pins, or marketplace release procedures. Produces consistent manifests, immutable ZIP assets, real SHA-256 digests, and release metadata without requiring MCC, DMCBK, or UMPK source checkouts.
license: MIT
compatibility: Python 3.11+ for the bundled packager. A compatible MCC distribution for validation and installation. .NET 10 SDK and pinned NuGet packages for compiled authoring.
---

# DMCBK marketplace authoring

Create schema-2 metadata and installable plugin archives. Treat published release bytes and compatibility declarations as immutable.

## Read the relevant reference

| Task | Read |
| --- | --- |
| Define or repair metadata | [Schema and compatibility](references/schema-and-compatibility.md) |
| Choose assets or explain resolution | [Resolution and installation](references/resolution-and-installation.md) |
| Package, test, or publish releases | [Release procedure](references/release-procedure.md) |
| Execute a complete local example | [Local marketplace](examples/local-marketplace/README.md) |

The references contain the schema contract. They require no source checkout.

## Collect the release inputs

Use supplied values where available. Ask only for missing values that change the release contract.

1. Identify the marketplace and plugin IDs.
2. Select the exact plugin version.
3. Obtain the required API minor and tested library ranges.
4. Obtain allowed host identities and their version ranges.
5. Obtain required host capabilities.
6. Record required and optional plugin providers.
7. Identify source, compiled, or mixed publication.
8. Record tested operating systems, process architectures, and Linux libc variants.
9. Obtain the final immutable asset URLs.
10. Identify the previous published catalogue, if present.

Do not infer library compatibility from the MCC application version. Do not claim execution tests from a cross-build.

## Define the metadata

Keep these files distinct:

- `mcc-marketplace.toml` lists plugin identities and relative catalogue paths.
- Each release catalogue lists the complete history for one plugin ID.
- Each archive contains its own root `plugin.toml`.
- The installer writes `plugins.lock.toml` for the local active graph and user policy.

Use `schema-version = 2` in each applicable file. Match index IDs to catalogue IDs.
Match every manifest compatibility field to its selected release. Match manifest kind and target to its selected asset.

Use `[requires]` for required plugin providers. Use `[optional]` for providers that the plugin can operate without.
Use `deps` for private assembly paths. Use `[exports]` for assemblies that required consumers may share.

Keep enabled state, pins, and update policy outside package manifests. Keep user data outside immutable packages.

## Select assets deliberately

1. Prefer an exact compiled process target.
2. Otherwise, select compiled `any`.
3. Select suitable source automatically for source-only releases.
4. Require explicit source fallback for mixed releases without a suitable compiled asset.

`--source` requires a suitable source asset. `--source-fallback` permits source only after compiled selection fails.
`--prerelease` changes version selection. It does not bypass compatibility checks.

Select one archive per changed plugin in the required graph. Do not download every target or historical version.

## Package and check

Build compiled plugins against pinned NuGet packages. Keep author projects independent of host source projects.
Use a source entry containing one C# file. Runtime source compilation does not build projects or restore NuGet packages.

The bundled helper packages an already prepared package folder:

```sh
python scripts/pack_release.py pack examples/local-marketplace/plugins/marketplace-demo --output examples/local-marketplace/release-assets --base-url http://127.0.0.1:8765/release-assets/
python scripts/pack_release.py verify examples/local-marketplace/release-assets
```

The helper writes a deterministic ZIP, a digest sidecar, and a catalogue fragment.
It rejects different bytes at the same output identity. It does not upload files or replace MCC validation.
Its stored ZIP entries avoid compression-library differences. See the release reference for its packaging limits.

Run the distributed MCC executable. The following shell commands assume `Mcc.Cli` is available on `PATH`:

```sh
Mcc.Cli --validate-plugin examples/local-marketplace/plugins/marketplace-demo
Mcc.Cli --validate-marketplace examples/local-marketplace/marketplace
```

For a framework-dependent distribution, replace `Mcc.Cli` with `dotnet /absolute/path/Mcc.Cli.dll`.
Use extracted archive folders for additional `--validate-plugin` checks. Metadata validation does not execute plugin code.

## Compose and publish

1. Compose all unpublished assets for the version.
2. Check shared compatibility and dependency declarations.
3. Retain all previous release entries.
4. Upload each immutable archive and digest sidecar.
5. Download each archive through its final URL.
6. Check its digest against the catalogue.
7. Publish the completed catalogue.
8. Publish the index change, if needed.
9. Test installation with a disposable configuration folder.
10. Check version, kind, target, digest, dependency order, and activation.

Use HTTPS for real public release assets. The loopback HTTP example serves only local test files.
Label illustrative external URLs explicitly. Do not present placeholder digests as installable fixtures.

Increase the plugin version for changed payloads, compatibility fields, dependencies, URLs, or asset lists.
Set `yanked = true` to stop ordinary new selection. Preserve release history and original archive bytes.

## Explain operational effects

Read the resolution reference before proposing dependency, pin, uninstall, rollback, or recovery changes.

Show the complete immutable plan before a consequential graph change. Apply within the user's authorized scope.
Recreate a stale plan. Do not change the active lock by hand.

Preserve `userdata`, transaction history, the lock, and immutable versions when diagnosing failures.
Rollback restores package selections. It cannot reverse server commands or arbitrary plugin data migrations.

## Deliver

Report these items:

- Created files and exact plugin versions.
- Generated archive names and SHA-256 digests.
- Required host, library, capability, and platform constraints.
- Validator results and actual installation results.
- Targets that built and targets that executed.
- Final asset URLs or explicitly unresolved publication inputs.
- Release-history changes and any yanked versions.

Do not claim that validators prove plugin behavior. State the separate activation or server test that supports that claim.
