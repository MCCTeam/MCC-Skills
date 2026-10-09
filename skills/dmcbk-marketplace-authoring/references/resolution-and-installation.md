# Resolution and installation

## Process targets

Asset detection uses the operating system, process architecture, and Linux libc.
The operating system's architecture alone is insufficient.
A 32-bit MCC process on Windows x64 selects `win-x86`.

| Runtime | Supported targets |
| --- | --- |
| Windows | `win-x86`, `win-x64`, `win-arm64` |
| Linux glibc | `linux-x64`, `linux-arm64`, `linux-arm` |
| Linux musl | `linux-musl-x64`, `linux-musl-arm64`, `linux-musl-arm` |
| macOS | `osx-x64`, `osx-arm64` |
| Portable managed payload | `any` |

`any` describes a portable payload. It is not the process's detected target.
Native dependencies require a suitable target-specific asset.
Do not label a glibc native dependency as `linux-musl-x64` or portable `any`.
Do not declare a platform that the author did not build.

## Select exactly one asset

| Release and request | Result |
| --- | --- |
| Compiled exact target exists | Select that compiled archive |
| Compiled exact target absent, compiled `any` exists | Select compiled `any` |
| Source-only release | Select suitable source automatically |
| Mixed release, no suitable compiled asset | Fail unless the request permits source fallback |
| `--source` | Require suitable source, even when compiled exists |
| `--source-fallback` | Select source only after compiled selection fails |
| Requested source absent | Fail, rather than silently selecting compiled |
| No suitable asset | Explain the unavailable target |

For each kind, exact source or compiled target takes precedence over `any`.
`AssetPolicy(PreferSource: true)` corresponds to `--source`.
`AssetPolicy(AllowSourceFallback: true)` corresponds to `--source-fallback`.

A mixed release with `win-x64`, `linux-x64`, and source `any` does not automatically support macOS or musl installation.
The source request must explicitly authorize selection on those runtimes.
All gates still apply after source selection.

The installer downloads one selected archive per changed plugin in the required graph.
It reuses unchanged installed selections. Required providers can add downloads.
Asset count does not determine download count.

## Resolve the whole graph

The resolver chooses one active version for each plugin ID.
It checks the requested plugin, required providers, and existing installed consumers together.
It respects publisher bindings, compatibility gates, installed assets, pins, and dependent ranges.

An install can retain an installed version that satisfies the request.
An update prefers newer compatible releases for the requested identity.
Exact requests never substitute another version.

Required dependencies install transitively. Missing providers and required cycles fail before installation changes.
Optional dependencies do not trigger installation.
A missing or incompatible optional provider remains unavailable.
Compatible optional providers can affect activation order without introducing a cycle.

Suppose two consumers require `shared-tools = "^2.0.0"` and `shared-tools = "^3.0.0"`.
No single provider version satisfies both ranges. Resolution fails before downloading or unloading plugins.
Separate immutable package directories do not permit two active versions under one ID.
Select compatible consumer releases or deliberately remove a conflicting consumer.

## Bind publishers explicitly

The user registry binds each publisher identity to one explicit index source.
A source can be an index HTTP(S) URL, index file, or local folder containing `mcc-marketplace.toml`.

This registry fragment is illustrative. The external URL does not provide a fixture:

```toml
schema-version = 2

[[marketplaces]]
id = "community"
source = "https://publisher.example/marketplace/mcc-marketplace.toml"
auto-update = "off"
```

Use `<plugin>@<marketplace>` to choose the publisher deliberately.
An unbound plugin with multiple candidate publishers requires an explicit choice.

New required providers default to the consumer's publisher.
An already-installed provider retains its explicit existing publisher binding.
Cross-market dependencies therefore need an established provider binding, not merely an added unrelated marketplace.
Do not silently search other publishers when the selected source lacks a required provider.

For a trusted cross-market provider, install `shared-tools@tools-publisher` first.
Then resolve the consumer from its own publisher.
Check both publishers and provider ranges before changing an existing source binding.

Direct folder, ZIP, URL, and Git imports use the same package checks and immutable layout.
They record the explicit source and archive digest or Git commit.
They do not automatically bind required providers to arbitrary marketplaces.
A direct consumer requires existing provider bindings when its dependencies come from marketplaces.

## Pins, yanking, and policy

Pins hold plugin versions. They can prevent dependent updates.
Inspect `/plugins deps <id>` before removing a pin.
Do not silently unpin a provider to satisfy a new request.

Yanking excludes a release from ordinary new selection.
The resolver can retain a compatible installed yanked selection.
Yanking does not force an uninstall or bypass a pin.
Do not use an exact request as a claimed way to install a newly selected yanked release.

| Policy layer | Values |
| --- | --- |
| Marketplace `auto-update` | `off`, `check`, `apply` |
| Plugin update policy in lock/API | `inherit`, `off`, `manual`, `automatic` |

An inherited plugin policy follows the publisher binding.
Marketplace `check` reports compatible changes. Marketplace `apply` permits automatic application after disconnection.
Automatic checks honor offline state and a 24-hour metadata cache.
Startup checks use a short randomized delay.
Manual refresh explicitly obtains current metadata.

The CLI exposes marketplace policy and pins.
Do not invent a per-plugin policy command that the CLI does not implement.
Direct installer application does not itself defer for a live session.
The host chooses the appropriate time for direct application.

## Installation layout

```text
runtime/
├── configurations/
│   └── marketplaces.toml
└── plugins/
    ├── versions/<id>/<version>/<target>/<sha256>/
    ├── userdata/<id>/settings.toml
    ├── userdata/<id>/data/
    ├── cache/downloads/
    ├── cache/source/<id>/
    ├── transactions/
    └── plugins.lock.toml
```

In MCC, select `runtime/configurations` with `--configurations`.
The plugin root is the sibling `runtime/plugins` folder.
Use separate runtime parents for isolated installation tests.

The lock records schema, revision, exact release and asset, publisher, enabled state, pin, update policy, and direct source information.
It represents the active graph in dependency-first order.
Do not edit the lock while MCC operates.
The runtime does not overwrite loaded DLLs.

Package defaults form an overlay beneath user values.
Updates preserve user settings and data.
Uninstall preserves userdata unless the user explicitly selects purge.

## Plans and transactions

`PlanInstallAsync`, `PlanUpdateAsync`, `PlanUninstallAsync`, `PlanPolicyAsync`, and `PlanRollbackAsync` return immutable plans.
The plan records exact versions, kinds, targets, digests, and affected dependent changes.
Display the complete plan before applying a consequential graph change.

`ApplyAsync` checks the plan against the current lock under the installation-root lock.
A stale plan requires a new plan and review.
Convenience service operations use a confirmation callback. Its default response is refusal.
`ApplyAsync` performs application without requesting another confirmation.

Installation uses this sequence:

1. Stage the selected downloads.
2. Check digests and extraction rules.
3. Check each manifest against its selected release.
4. Check the staged graph.
5. Compile source entries.
6. Stop affected plugins in reverse dependency order.
7. Commit immutable package directories and the new lock.
8. Activate enabled plugins in dependency order.
9. Restore the prior graph if activation fails.

Source compilation occurs before commitment.
Cancellation before commitment preserves the previous active selection.
Startup recovers interrupted transactions before loading plugins.

## Recovery and rollback

Preserve the lock, transaction history, userdata, and immutable packages together.
Copying only entry DLLs loses the graph and rollback history.
Do not correct a failed package by overwriting installed immutable files.

Use `/plugins rollback <transaction>` with a retained transaction ID.
Rollback restores cached package selections and dependencies.
It cannot reverse arbitrary plugin data migrations, chat, server commands, or network side effects.
Plugin authors must design durable storage migrations separately.

| Failure | Action |
| --- | --- |
| Digest mismatch | Obtain the original immutable asset or publish a corrected new release |
| Asset missing | Upload the declared original asset or publish corrected new metadata under a new version |
| Manifest disagreement | Correct authoring and publish a new immutable version |
| No matching target | Select a supported release or explicitly permit suitable source |
| Required capability absent | Use a host that composes the capability or select another release |
| Required version conflict | Select compatible consumers and inspect provider pins |
| Stale plan | Recreate the plan against the current lock |
| Source compiler failure | Correct entry code and declared references before publication |
| Activation failure | Inspect plugin status, logs, and transaction outcome |
| Interrupted operation | Start MCC and inspect recovery before further changes |

Do not disable path, digest, or manifest checks to accept a bad archive.
