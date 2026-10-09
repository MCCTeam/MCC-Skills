# Complete local marketplace example

This fixture contains one source-only release with a real deterministic ZIP and digest.
The plugin writes an activation marker without connecting to Minecraft.
It requires no source checkout, NuGet restore, account credential, or Minecraft server.

Use Python 3.11 or later and a compatible MCC distribution.
The manifest targets plugin API `1.0`, DMCBK `>=0.1.0-preview.3 <0.2.0`, UMPK `>=0.9.0-beta.4 <0.10.0`, and MCC `>=2.0.0 <3.0.0`.

## Files

```text
local-marketplace/
├── plugins/marketplace-demo/
│   ├── plugin.toml
│   ├── MarketplaceDemo.cs
│   ├── defaults/settings.toml
│   ├── lang/en.toml
│   ├── man/en/marketplace-demo.md
│   └── LICENSE
├── marketplace/
│   ├── mcc-marketplace.toml
│   └── catalog/marketplace-demo.toml
└── release-assets/
    ├── marketplace-demo-1.0.0-source-any.zip
    ├── marketplace-demo-1.0.0-source-any.zip.sha256
    └── marketplace-demo-1.0.0-source-any.zip.catalogue.toml
```

Archive SHA-256:

```text
e418bd5bc249d19907571417651de817eb0b0eb3506c152fa36c0e5f2d672c57
```

The catalogue's loopback URL serves this exact archive.
It is usable while the local server below runs.
It is not a public publication URL.

## Prepare the commands

Execute shell commands from the skill folder containing `SKILL.md`.
The commands assume `Mcc.Cli` is available on `PATH`.
For a framework-dependent distribution, replace `Mcc.Cli` with `dotnet /absolute/path/Mcc.Cli.dll`.

Lines starting with `/plugins` are MCC prompt commands.
Enter those lines inside MCC, without a shell prefix.

## Regenerate and check

1. Execute the packaging command.
2. Execute the checksum check.
3. Check the author package with MCC.
4. Check the marketplace metadata with MCC.

```sh
python scripts/pack_release.py pack examples/local-marketplace/plugins/marketplace-demo --output examples/local-marketplace/release-assets --base-url http://127.0.0.1:8765/release-assets/
python scripts/pack_release.py verify examples/local-marketplace/release-assets
Mcc.Cli --validate-plugin examples/local-marketplace/plugins/marketplace-demo
Mcc.Cli --validate-marketplace examples/local-marketplace/marketplace
```

Regeneration reproduces the bundled archive digest exactly.
The helper refuses different bytes under the same archive name.
MCC metadata validation does not download the archive or activate the plugin.

If you change fixture code, assign a new plugin version before packaging into existing outputs.
Generate a fresh catalogue from the new fragment. Do not replace the original published release.

## Install through a file path

Start MCC with a disposable runtime:

```sh
Mcc.Cli MarketplaceDemo - --configurations ./local-test/direct/configurations --connection.auto-connect=false
```

The offline username prevents account prompts. The configuration override prevents server connection.

Enter these commands in the MCC prompt:

```text
/plugins install ./examples/local-marketplace/release-assets/marketplace-demo-1.0.0-source-any.zip yes
/plugins info marketplace-demo
/plugins deps marketplace-demo
/exit
```

`yes` accepts installation in this disposable fixture test.
The expected plugin state is `loaded`, with source kind and version `1.0.0`.
The recorded publisher for a direct file import is `development`.
The import records its exact source path and archive digest.

Check the activation marker after MCC exits:

```sh
cat local-test/direct/plugins/userdata/marketplace-demo/data/storage.toml
cat local-test/direct/plugins/userdata/marketplace-demo/settings.toml
```

The storage file contains `activation = "Marketplace demo activated."`.
The settings file contains `WriteMarker = true`.
This proves that the source compiled and its activation callback executed.
It does not prove live Minecraft behavior.

A local folder import also works in a separate disposable runtime:

```text
/plugins install ./examples/local-marketplace/plugins/marketplace-demo yes
```

Folder import repackages the author folder with the shared host packager.
Its resulting archive digest can differ from the bundled Python-produced ZIP.
Both imports record their actual immutable digest.

## Install through the marketplace

Start this loopback server in a separate terminal from the same skill folder:

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory examples/local-marketplace
```

Use another fresh runtime parent for the catalogue install:

```sh
Mcc.Cli MarketplaceDemo - --configurations ./local-test/market/configurations --connection.auto-connect=false
```

Enter these MCC commands:

```text
/plugins marketplace add ./examples/local-marketplace/marketplace as local-demo
/plugins search marketplace-demo in local-demo
/plugins install marketplace-demo@local-demo 1.0.0 yes
/plugins pin marketplace-demo
/plugins info marketplace-demo
/plugins marketplace auto-update local-demo off
/exit
```

Check these results:

- The publisher is `local-demo`.
- The selected version is `1.0.0`.
- The selected asset kind is `source`.
- The selected target is `any`.
- The selected digest matches the digest above.
- MCC loads the plugin and records its pin.
- The server receives one ZIP request.
- The activation marker exists under the marketplace test runtime.

The installed lock is `local-test/market/plugins/plugins.lock.toml`.
Read it for inspection. Do not change it while MCC operates.
Stop the loopback server with Ctrl+C after the test.

If port `8765` is unavailable, use a disposable copy of this fixture.
Generate outputs into a fresh directory with a new matching loopback base URL.
Copy its generated fragment to the disposable marketplace catalogue.
Do not change an existing release fragment in the original output directory.

## Check user settings preservation

1. Stop MCC.
2. Set `WriteMarker = false` in the test runtime's user settings.
3. Start MCC with that same configuration folder.
4. Inspect the plugin state and user settings.
5. Stop MCC.

The plugin still loads. The user setting remains `false`.
The old marker remains because the plugin does not remove stored data.
Immutable package defaults remain `true`.

Uninstall without `purge` preserves settings and data.
Use `purge` only for an explicit data-removal test in a disposable runtime.
Do not expect rollback to reverse arbitrary plugin data changes.

## Limits of this fixture

This fixture checks source packaging, schema validation, compilation, activation, direct import, catalogue download, and pinning.
It contains no compiled asset, required provider, native dependency, or Minecraft callback.
Use the references for those release variants.
Test their actual payloads before claiming support.
