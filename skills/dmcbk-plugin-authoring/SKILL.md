---
name: dmcbk-plugin-authoring
description: Create, repair, test, and package DMCBK plugins for Minecraft Console Client (MCC). Use for IPlugin entries, plugin.toml, source or compiled packages, reconnect behavior, commands, settings, storage, translations, manuals, and Beacon extensions. Also use for plugin services, messages, exported contracts, private or native dependencies, and release assets. Use this skill when a user requests an MCC plugin, even when the user does not name DMCBK. Produce standalone .NET 10 projects that use NuGet packages. Do not require an MCC, DMCBK, or UMPK source checkout.
license: MIT
compatibility: .NET 10 SDK. Python 3.11 or newer for the optional archive script. MCC or another DMCBK host for live tests.
---

# DMCBK plugin authoring

Create a plugin package and an author project that the user can build independently.
Use the bundled references as the SDK documentation for this preview.
Use public SDK contracts.

## Terms

- **DMCBK** supplies the client facade, modules, and plugin runtime.
- **UMPK** supplies the Minecraft protocol engine and session APIs.
- **Host** means MCC or another application that composes DMCBK modules.
- **Plugin lifetime** starts at activation and ends at unload, disable, or reload.
- **Session** means one server connection, including its negotiated protocol state.
- **Scope** owns registrations and removes them when that scope ends.
- **Manifest** means the package's `plugin.toml` file.
- **Contract assembly** contains public types that plugins share at runtime.
- **Process target** identifies the operating system and architecture of the running host.

## Select the output

| User need | Starting asset | Read first |
| --- | --- | --- |
| Small plugin with host APIs | `assets/source-example/` | `references/setup-and-formats.md` |
| Several source files or private libraries | `assets/compiled-template/` | `references/packaging.md` |
| Session callbacks or reconnect repair | Either author project | `references/lifecycle-and-commands.md` |
| Settings, durable data, translated output | Either author project | `references/settings-and-text.md` |
| Beacon functions, variables, or events | Session Journal example | `references/beacon.md` |
| Plugin communication or dependencies | User's projects | `references/dependencies.md` |
| Verification or release | `assets/verify-plugin/` | `references/testing.md` |
| Exact public signatures | Bundled API reference | `references/public-api.md` |

Copy the selected asset to the user's output directory before editing it.
Keep generated binaries and test results outside this skill's assets.

## Establish compatibility

Use this verified authoring baseline:

- Target framework: `net10.0`.
- DMCBK packages: `0.1.0-preview.3`.
- UMPK packages: `0.9.0-beta.4`.
- Manifest schema: `2`.
- Plugin API contract: `1.0`.

Keep the plugin release version independent from the SDK, engine, and host versions.
Read existing manifests before changing compatibility ranges.
Declare only the host capabilities that the plugin requires.
Do not broaden a range solely to remove a loader error.

An author project restores NuGet packages.
A source package compiles one entry file at load time.
Runtime source loading does not restore NuGet packages or build a project.
Include every required namespace in a source entry.

## Implement the plugin

1. Declare a stable plugin ID and settings type in `Configure`.
2. Keep `Configure` free of file access, network access, and game actions.
3. Register plugin commands and cross-session behavior in `ActivateAsync`.
4. Subscribe to `SessionStarted` for each play session.
5. Use `SessionCreated` for subscriptions before handshake or login.
6. Obtain each session from the event arguments.
7. Pass `session.Detached` to session-bound asynchronous work.
8. Release plugin-created resources in `DeactivateAsync(CancellationToken)`.

`ActivateAsync` can run while disconnected.
`CurrentSession` can be null.
`Session` throws when no session exists.
Do not retain a session across reconnects.

Register persistent commands through `context.Commands`.
Register session commands through `session.Commands`.
Use the command tree for arguments and completion.
Do not parse raw command strings as a replacement command system.

Use scoped session events, schedulers, channels, packet observers, and movement leases.
Dispose a movement lease when your operation ends.
Keep packet callbacks short.
Copy a packet payload before retaining its bytes.

Remove arbitrary event subscriptions that your plugin creates.
Cancel and await plugin-created workers during deactivation.
Honor the deactivation token, which limits the host's teardown wait.
Avoid `async void` callbacks and blocking waits.

## Store data and display text

Declare settings with `descriptor.WithSettings<T>()`.
Implement `IValidatablePluginSettings` to normalize loaded settings.
Read settings through `context.Settings.Load<T>()`.
Validate editor values before saving them.

Use `context.Storage` for persistent data.
Call `Storage.Save()` after key/value changes that must survive restart.
Keep user files outside immutable packages and compilation caches.

Put plugin messages in `lang/en.toml`.
Read messages through `context.Strings.Get` or `context.Strings.Format`.
Use `context.Translations` only for Minecraft translation keys.
Put manual pages under `man/en/` and declare their topic IDs in `man`.
Keep command names, resource keys, and protocol identifiers literal.

Use ASCII letters, digits, and underscores in client variable names.
Plugin IDs can use dashes, but variable names cannot.

## Add optional integrations

For Beacon, read `references/beacon.md` before implementation.
Declare the host capability `beacon` when the plugin requires Beacon.
Declare a separate script capability for each extension contract.
Initialize the lazy Beacon engine before pre-session plugin tests.
Convert extension results to supported scalar, list, or map values.
Pass the provided cancellation token into asynchronous calls.

For other plugins, read `references/dependencies.md`.
Use `[requires]` for mandatory plugins and `[optional]` for optional plugins.
Use `Services.TryGet<T>` when a service can be absent.
Re-resolve optional services when an operation starts.
Export shared types through a provider's `[exports]` assembly list.
Do not package a second private copy of an exported contract in a consumer.

For private or native libraries, read `references/packaging.md`.
Package private helpers explicitly.
Exclude host contracts and framework assemblies.
Test native libraries on each declared process target.

## Check the result

1. Restore the standalone author project from NuGet.
2. Build the author project in Release mode.
3. Stage the actual source or compiled package.
4. Load that package with `DMCBK.Testing`.
5. Check both the operation result and the individual plugin's loaded state.
6. Check commands, settings, storage, reload, and unload.
7. Check outgoing frames when the plugin requests game actions.
8. Test reconnect with one client against a controlled reusable server.
9. Test native execution on each supported target, when applicable.
10. Create the archive and calculate its SHA-256 checksum.

Use `assets/verify-plugin/` to check Session Journal source and compiled packages.
Its in-memory sessions use real protocol frames without a socket or Minecraft account.
It creates a fresh harness client for each session.
This checks restart persistence, but it does not prove same-client reconnect.

Report checks precisely:

- **Author build:** compiler and NuGet reference checks.
- **In-memory test:** runtime loading and scripted protocol checks.
- **Live test:** actual host and controlled Minecraft server behavior.
- **Target test:** native execution on the named operating system and architecture.

Do not describe an in-memory test as a live server test.
Do not describe a build as runtime verification.

## Deliver

Return the author project, package manifest, resources, and verification project.
Include exact build, test, and package commands.
List the checks that passed and the checks that remain untested.
State the tested versions and compatibility ranges.
State the final archive path and checksum when you create an archive.
Keep published instructions independent from source checkouts.
