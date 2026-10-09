# Standalone compiled template

Copy this directory to your author workspace.
It uses NuGet packages and does not need host source.
Install the .NET 10 SDK before building.

```sh
dotnet restore SessionJournal.csproj
dotnet build SessionJournal.csproj --configuration Release --no-restore
mkdir -p ../session-journal-compiled
cp plugin.toml ../session-journal-compiled/
cp bin/Release/net10.0/SessionJournal.dll ../session-journal-compiled/
cp bin/Release/net10.0/SessionJournal.deps.json ../session-journal-compiled/
cp -R lang man defaults ../session-journal-compiled/
```

Use a clean staging directory for each release.
Do not copy build output wholesale.
This portable example needs no private helper DLLs or native files.
Do not package DMCBK, UMPK, or framework DLLs from `bin`.

Copy the skill's `assets/verify-plugin/` directory beside this template.
Run both test cases against the staged runtime package:

```sh
dotnet run --project ../verify-plugin/VerifyPlugin.csproj \
  --configuration Release -- ../session-journal-compiled
dotnet run --project ../verify-plugin/VerifyPlugin.csproj \
  --configuration Release -- ../session-journal-compiled 150
```

Archive the staging directory with the skill's `scripts/package_plugin.py`.
The verifier checks assembly loading, commands, Beacon, persistence, reload, and unload.
The in-memory verifier does not prove same-client reconnect or live server behavior.

For a different plugin, rename the ID, assembly, entry class, commands, capabilities, and manual topic consistently.
Keep the release version consistent between the descriptor and manifest.
Keep compatible library bounds distinct from the plugin release version.

For private or native dependencies, read the skill's packaging reference before staging.
An architecture-specific native library requires a matching process target and an actual execution test.

The preview can announce an existing play session when a plugin activates during play. Make session setup idempotent.
The counter example observes SessionCreated before counting SessionStarted. It ignores replayed starts after a connected reload.
A connection already active before loading the counter is not a new counted connection.
