# Runtime verifier

This standalone .NET 10 console application uses published NuGet packages.
Supply the absolute path of a Session Journal source or compiled package.
An optional second argument supplies a user `Increment` setting.

```sh
dotnet restore VerifyPlugin.csproj
dotnet run --project VerifyPlugin.csproj --configuration Release \
  -- /absolute/path/to/package
dotnet run --project VerifyPlugin.csproj --configuration Release \
  -- /absolute/path/to/package 150
```

Each run creates two fresh clients with one shared temporary user-data root.
The setting 150 normalizes to 100.
The verifier checks actual package loading, pre-session Beacon, callbacks, storage, reload, and command cleanup.
The verifier removes its temporary root when it finishes.

The protocol sessions use in-memory transport.
They open no socket and require no Minecraft account.
These tests do not prove same-client reconnect, live game behavior, authentication, or native execution.
Use a controlled reusable server for same-client reconnect.

The verifier reloads the plugin during each play session. The count must remain unchanged during that reload.
