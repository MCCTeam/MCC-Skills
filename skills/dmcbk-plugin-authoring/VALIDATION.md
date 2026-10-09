# Draft validation

Baseline: .NET SDK `10.0.401`, DMCBK `0.1.0-preview.3`, UMPK `0.9.0-beta.4`.
All projects restored from published NuGet packages with no host or engine project references.
Validation copies and generated output remained outside assets.
The temporary build and release directories were removed after these checks.

| Check | Result |
| --- | --- |
| Source author Release build | Exit 0, zero warnings, zero errors |
| Compiled author Release build | Exit 0, zero warnings, zero errors |
| Verifier Release build | Exit 0, zero warnings, zero errors |
| Source package, default settings | Exit 0, PASS |
| Source package, `Increment = 150` | Exit 0, PASS, normalized increment 100 |
| Compiled package, default settings | Exit 0, PASS |
| Compiled package, `Increment = 150` | Exit 0, PASS, normalized increment 100 |
| Archive creation, both package forms | Exit 0, manifest at archive root, SHA-256 companion produced |
| Archive helper smoke checks | Exit 0, root layout, stable bytes, unsafe paths, shared DLL rejection |
| Skill creator `quick_validate.py` | Exit 0, `Skill is valid!` |
| STE structural scan | Zero hard violations across skill and references |

The verifier's final line was:

```text
PASS: load, pre-session Beacon, two fresh clients, storage, reload, and command cleanup.
```

Each runtime run loaded the actual package through `DMCBK.Testing`.
Each run created two fresh harness clients with shared temporary user data.
The checks prove runtime loading, callbacks, restart persistence, reload, and command withdrawal.
They do not prove reconnect on one continuing client, live server behavior, authentication, or native execution.

The first verifier build found a missing `using DMCBK.Core` import for the public `Client.Scripts` extension property.
The final verifier includes that import and built without warnings or errors.
Public namespace checks used the installed package XML.

The STE scan disabled synonym rotation because public identifiers such as `Validate` have fixed API names.
The prose uses short instructions and consistent terms.
The scan does not claim compliance with ASD's unpublished dictionary.

## Commands checked

```sh
dotnet restore source-example/author/SessionJournal.csproj
dotnet build source-example/author/SessionJournal.csproj --configuration Release --no-restore
dotnet restore compiled-template/SessionJournal.csproj
dotnet build compiled-template/SessionJournal.csproj --configuration Release --no-restore
dotnet restore verify-plugin/VerifyPlugin.csproj
dotnet build verify-plugin/VerifyPlugin.csproj --configuration Release --no-restore
dotnet verify-plugin/bin/Release/net10.0/VerifyPlugin.dll source-example/package
dotnet verify-plugin/bin/Release/net10.0/VerifyPlugin.dll source-example/package 150
dotnet verify-plugin/bin/Release/net10.0/VerifyPlugin.dll compiled-package
dotnet verify-plugin/bin/Release/net10.0/VerifyPlugin.dll compiled-package 150
python3 scripts/package_plugin.py source-example/package releases/source.zip
python3 scripts/package_plugin.py compiled-package releases/compiled.zip
```

The validation selected the SDK and package cache explicitly.
Consumer instructions use ordinary `dotnet` and `python3` commands.

## Proposed evaluation criteria

The three prompts in `evals/evals.json` initially contain no assertions.
Use these criteria when the paired evaluation runs start:

1. Restore and build without MCC, DMCBK, or UMPK source checkouts.
2. Use the exact package baseline and a valid schema-2 manifest.
3. Load the real source package through runtime compilation.
4. Load a compiled staging package without bundled host assemblies.
5. Register plugin commands once and withdraw them on unload.
6. Handle each new session through its supplied scope and cancellation token.
7. Persist storage and normalize user settings.
8. Resolve plugin text and manuals from bundled resources.
9. Initialize lazy Beacon before pre-session calls and declare both capability boundaries.
10. Share exported contracts through the provider and handle optional service absence.
11. Keep private and native dependency packaging consistent with process targets.
12. Distinguish author builds, in-memory tests, same-client reconnect, and native execution.

Compile and runtime checks are objective evidence.
Review explanations and coverage for clarity separately.

The final example also checks connected reload without recount. Run the repository example runner for current validation.
