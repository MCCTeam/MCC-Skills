# Schema 2 and compatibility

## Metadata layers

| Document | Purpose | Author |
| --- | --- | --- |
| `mcc-marketplace.toml` | Publisher identity and plugin catalogue paths | Publisher |
| `catalog/<id>.toml` | Complete release history for one plugin | Publisher |
| Root `plugin.toml` | One archive's contents and loading requirements | Plugin author |
| Configuration `marketplaces.toml` | Explicit publisher bindings and automatic policy | Host or user |
| Installation `plugins.lock.toml` | Exact active graph and user policy | Installer |

The runtime rejects schema 1. A manifest `enabled` field does not control the managed installation.
Do not publish the local registry or lock as catalogue metadata.

## Marketplace index

```toml
schema-version = 2
id = "local-demo"
name = "Local marketplace demonstration"

[[plugins]]
id = "marketplace-demo"
description = "Writes a local activation marker without a Minecraft connection."
tags = ["tutorial", "offline"]
releases = "catalog/marketplace-demo.toml"
```

| Field | Rule |
| --- | --- |
| `schema-version` | Integer `2` |
| `id` | Stable publisher ID |
| `name` | Nonempty display name |
| `plugins[].id` | Unique plugin ID within the publisher |
| `plugins[].releases` | Safe path relative to the index |
| `description`, `tags` | Search metadata |

IDs permit ASCII letters, digits, dots, hyphens, and underscores. IDs cannot start with a dot.
Use lowercase IDs consistently. The runtime treats many identity comparisons as case-insensitive.
Do not use absolute catalogue paths, parent traversal, empty segments, or backslashes.
Each catalogue's `id` must match its index entry.

## Release catalogue

The complete working catalogue lives in `examples/local-marketplace/marketplace/catalog/marketplace-demo.toml`.
The helper generates its digest from the actual bundled ZIP.

Each `[[releases]]` table contains these fields:

| Field | Meaning |
| --- | --- |
| `version` | Exact, complete SemVer string, such as `1.0.0` |
| `api-version` | Required plugin API major and minor |
| `dmcbk` | Supported DMCBK library range |
| `umpk` | Supported UMPK library range |
| `framework` | `net10.0` |
| `needs` | Required host capabilities |
| `yanked` | Exclusion from ordinary new selection |
| `assets` | Nonempty list of archive descriptors |
| `[releases.requires]` | Required plugin IDs and ranges |
| `[releases.optional]` | Optional plugin IDs and ranges |
| `[releases.hosts]` | Allowed application IDs and ranges |

Asset fields are `kind`, `target`, `url`, and `sha256`.
Kinds are `source` and `compiled`. A release cannot repeat the same `(kind, target)` pair.
Asset URLs must be absolute HTTP or HTTPS URLs. Use stable HTTPS URLs for public releases.
The catalogue rejects local file paths and `file:` URLs as asset URLs.
Local archive imports are a separate installation mechanism.

Use a digest with exactly 64 hexadecimal characters. Generate the digest after producing the final archive bytes.
The manifest cannot contain the digest of its own enclosing archive.
Avoid self-dependencies. Required self-dependencies invalidate a release.

## Archive manifest

Every ZIP contains `plugin.toml` directly at its root. Do not wrap the package in another directory.

```toml
schema-version = 2
id = "marketplace-demo"
version = "1.0.0"
kind = "source"
target = "any"
entry = "MarketplaceDemo.cs"
framework = "net10.0"
api-version = "1.0"
dmcbk = ">=0.1.0-preview.3 <0.2.0"
umpk = ">=0.9.0-beta.4 <0.10.0"
needs = []
deps = []
man = ["marketplace-demo"]

[hosts]
mcc = ">=2.0.0 <3.0.0"
```

`dmcbk` and `umpk` must be explicit, nonempty ranges in package manifests.
Use `"*"` only when tests justify unrestricted library compatibility.
An omitted or empty `[hosts]` permits any otherwise compatible application.
A populated `[hosts]` permits only listed application identities within their ranges.

Manifest IDs, versions, API versions, library ranges, framework, capabilities, and dependency tables must agree with the selected release.
Manifest kind and target must agree with the selected asset.
Equivalent-looking range text is insufficient when the installation compares declaration strings.
Keep exact range strings consistent across the release and every asset manifest.

`entry` identifies one `.cs` file for source or one `.dll` for compiled packages.
All `deps` entries identify relative `.dll` paths. All declared entry, dependency, and export files must exist.
Use forward slashes for subdirectories.
Reject rooted paths, `.` or `..` segments, colons, backslashes, NUL characters, and empty path segments.

Optional manifest metadata includes:

```toml
[meta]
description = "Writes a local activation marker."
tags = ["tutorial", "offline"]
uses = ["files"]

[services]
offline = true
```

`meta.uses` discloses behavior. It does not grant or restrict permissions.
`services.offline` describes useful operation without a Minecraft session.
These fields do not replace compatibility gates.

## Three version axes

| Axis | Example | Check |
| --- | --- | --- |
| Plugin API | `api-version = "1.2"` | Host major is `1`, host minor is at least `2` |
| Libraries | `dmcbk`, `umpk` | Actual library versions satisfy their independent ranges |
| Application | `[hosts] mcc = ">=2.0.0 <3.0.0"` | Application ID and version satisfy the declared host table |

API `"1"` means API `1.0`. API compatibility does not use caret SemVer ranges.
An API `1.1` host cannot load a plugin requiring API `1.2`.
An API `2.0` host cannot load a plugin requiring API `1.0`.

Application versions do not determine DMCBK or UMPK library versions.
Library and application gates evaluate actual preview versions with prerelease comparison enabled.
Plugin release selection has a separate prerelease admission policy.

`needs` checks composed host capabilities, such as `commands`, `beacon`, or `aspnetcore`.
Importing a namespace or adding a NuGet reference does not compose a host capability.

## Supported version ranges

The shared parser supports these forms:

| Range | Meaning |
| --- | --- |
| `1.2.3` or `=1.2.3` | Exactly `1.2.3` |
| `>=1.2.3 <2.0.0` | Both comparator conditions |
| `1.2` or `1.2.x` | `>=1.2.0 <1.3.0` |
| `1` or `1.x` | `>=1.0.0 <2.0.0` |
| `^1.2.3` | `>=1.2.3 <2.0.0` |
| `^0.2.3` | `>=0.2.3 <0.3.0` |
| `^0.0.3` | `>=0.0.3 <0.0.4` |
| `~1.2.3` | `>=1.2.3 <1.3.0` |
| `*`, `x`, `X` | Unrestricted range, subject to prerelease policy |
| `^1.2.3 || ^2.0.0` | Either comparator set |

Spaces combine comparators with AND. `||` combines comparator sets with OR.
Attach each comparator operator to its version. Use `>=1.2.3`, not `>= 1.2.3`.
Do not assume the parser supports every npm range extension. For example, do not emit hyphen ranges.
Build metadata does not change SemVer ordering.

Ordinary unrestricted plugin requests exclude prereleases.
An exact prerelease request remains exact.
An explicit prerelease comparator can admit prereleases with the same major, minor, and patch numbers.

For example, `>=0.4.0-beta.2 <0.5.0` can admit `0.4.0-beta.3`.
It does not independently admit `0.4.1-beta.1` under the ordinary prerelease policy.
`--prerelease` enables prerelease candidates without changing comparator precedence or compatibility gates.
Quote MCC ranges that contain spaces:

```text
/plugins install marketplace-demo@local-demo ">=1.0.0 <2.0.0"
```

## Dependencies and exports

This fragment illustrates dependency declarations. It does not declare an available fixture release.

```toml
deps = ["lib/PrivateMath.dll"]

[requires]
shared-tools = "^2.1.0"

[optional]
alerts = "~3.2.0"

[exports]
assemblies = ["Contracts.dll"]
```

`deps` names bundled private assemblies. `[requires]` and `[optional]` name other plugin identities.
The provider declares `[exports]`, not the consumer.
Use `assemblies = ["entry"]` to export the provider's entry assembly, including a source entry's generated assembly.
Use a shipped contract DLL path when the provider exposes a separate contract assembly.

Required provider exports preserve shared type identity across plugin load contexts.
Unexported plugin types remain private. Identical-looking types from separate contexts are different runtime types.
Private dependencies remain in a collectible plugin context.
An optional provider must remain optional in the consumer's behavior and linkage.

Do not bundle DMCBK, UMPK, or host framework assemblies.
Compiled packages can include `.deps.json` and native dependencies for assembly resolution.

## Package resources

```text
plugin.toml
MarketplaceDemo.cs                  # Or the compiled entry DLL
lib/PrivateMath.dll                 # If declared in deps
lang/en.toml
man/en/marketplace-demo.md
defaults/settings.toml
LICENSE
```

Manual topics in `man` identify pages under `man/<language>/<topic>.md`.
The English-only `man/<topic>.md` form is also supported.
Plugin localization uses `lang/<language>.toml` and `context.Strings`.
Packaged defaults live under `defaults/settings.toml`.
User settings belong under `userdata/<id>/settings.toml`.

Runtime source compilation accepts one entry source file and declared assembly references.
It does not build `.csproj` files, restore NuGet packages, or compile every `.cs` file in the folder.
The host must expose usable compilation reference assemblies.
Standard MCC distributions keep managed assemblies accessible.
Single-file or embedded hosts must supply reference assets explicitly.
