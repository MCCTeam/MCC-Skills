# Standalone source example

Copy this directory to your author workspace.
The project uses NuGet packages and does not need host source.
Install the .NET 10 SDK before building.

```sh
dotnet restore author/SessionJournal.csproj
dotnet build author/SessionJournal.csproj --configuration Release --no-restore
```

The build compiles the same entry file that the source package ships.
The runtime package is `package/`.
The author project stays outside that package.

Copy the skill's `assets/verify-plugin/` directory beside this example.
Run the verifier against the real package folder:

```sh
dotnet run --project ../verify-plugin/VerifyPlugin.csproj \
  --configuration Release -- ./package
dotnet run --project ../verify-plugin/VerifyPlugin.csproj \
  --configuration Release -- ./package 150
```

The verifier checks defaults and normalization.
It checks actual source compilation, commands, Beacon, persistence, reload, and unload.
Its sessions run in memory with fresh clients.
It does not prove same-client reconnect or live server compatibility.

Archive only `package/` with the skill's `scripts/package_plugin.py`.
Its output directory must remain outside the package folder.

Enter `/plugins validate /absolute/path/to/package` in MCC.
Enter `/plugins load /absolute/path/to/package` to load the development folder.
Enter `/journal-count` to display the count.
Enter `/plugins unload session-journal` to unload it.

Reload after changing code, settings, or resources.
Keep MCC runtime configuration and user data in a separate directory.

The preview can announce an existing play session when a plugin activates during play. Make session setup idempotent.
The counter example observes SessionCreated before counting SessionStarted. It ignores replayed starts after a connected reload.
A connection already active before loading the counter is not a new counted connection.
