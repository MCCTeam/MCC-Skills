# Setup and package formats

This reference targets DMCBK `0.1.0-preview.3` and UMPK `0.9.0-beta.4`.
These are preview versions.
Keep all DMCBK package versions equal within an author project.
Keep all UMPK package versions equal within that project.

## Tools and packages

Install the [.NET 10 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/10.0).
Check `dotnet --list-sdks` before building.
A repository's `global.json` can select a different SDK.
Create an independent output directory when that file selects an unavailable SDK.

Use these package roles:

| Package | Role |
| --- | --- |
| `DMCBK.PluginSdk` | Public author contracts and plugin context |
| `DMCBK.Core` | Client facade, game facade, command context, and configuration types |
| `DMCBK.Commands` | Command module for a composed host |
| `DMCBK.Plugins` | Package loading, compilation, activation, and cleanup |
| `DMCBK.Beacon` | Beacon module for a composed host |
| `DMCBK.Testing` | In-memory plugin runtime and protocol sessions |
| `Umpk.Client` | Session state, actions, events, schedulers, and movement ownership |

The SDK supplies its required DMCBK and UMPK dependencies transitively.
The assets explicitly pin `Umpk.Client` to make the engine baseline visible.
Do not use `ProjectReference` entries to host or engine source projects.
A reference between projects in the author's own solution remains valid.

Published package pages:

- [DMCBK.PluginSdk 0.1.0-preview.3](https://www.nuget.org/packages/DMCBK.PluginSdk/0.1.0-preview.3)
- [DMCBK.Testing 0.1.0-preview.3](https://www.nuget.org/packages/DMCBK.Testing/0.1.0-preview.3)
- [Umpk.Client 0.9.0-beta.4](https://www.nuget.org/packages/Umpk.Client/0.9.0-beta.4)

## Author project

An author project exists for development builds.
It does not become a runtime source package automatically.

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
    <ManagePackageVersionsCentrally>false</ManagePackageVersionsCentrally>
    <GenerateDependencyFile>true</GenerateDependencyFile>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="DMCBK.PluginSdk" Version="0.1.0-preview.3" />
    <PackageReference Include="Umpk.Client" Version="0.9.0-beta.4" />
  </ItemGroup>
</Project>
```

For projects inside a centrally managed solution, follow that solution's package policy.
The standalone assets disable central management because they contain their own version pins.

Run these commands from the author project directory:

```sh
dotnet restore
dotnet build --configuration Release --no-restore
```

## Source package

```text
session-journal/
  plugin.toml
  SessionJournal.cs
  defaults/settings.toml
  lang/en.toml
  man/en/session-journal.md
```

The manifest uses these fields:

```toml
schema-version = 2
id = "session-journal"
version = "1.0.0"
kind = "source"
target = "any"
entry = "SessionJournal.cs"
framework = "net10.0"
api-version = "1.0"
dmcbk = ">=0.1.0-preview.3 <0.2.0"
umpk = ">=0.9.0-beta.4 <0.10.0"
needs = ["commands", "beacon"]
man = ["session-journal"]
```

The archive root contains the manifest.
Do not put the package under another directory inside the archive.
Use forward slashes in package-relative paths.
Paths cannot contain `..`, empty components, backslashes, drive separators, or absolute paths.

Runtime compilation reads the entry `.cs` file and supported assembly references.
It does not build the `.csproj` or restore packages.
Use explicit `using` directives in the entry file.
Prebuilt private helper DLLs can accompany the source entry through `deps`.

## Compiled package

Build the entry project first.
Copy its entry DLL into a separate staging directory.
Use a manifest with these changes:

```toml
kind = "compiled"
entry = "SessionJournal.dll"
```

The project, source files, `bin`, and `obj` do not belong in this runtime package.
The compiled template contains source files for the author.
Its package script selects the compiled runtime payload.

## Compatibility fields

| Field | Meaning |
| --- | --- |
| `schema-version` | Manifest format, currently `2` |
| `version` | Plugin release version in canonical SemVer form |
| `api-version` | Required plugin API major and minor |
| `dmcbk` | Allowed DMCBK library versions |
| `umpk` | Allowed protocol engine versions |
| `framework` | Required managed framework, currently `net10.0` |
| `target` | Operating system and process architecture, or `any` |
| `needs` | Required host capabilities |
| `[hosts]` | Optional application ID and application version restrictions |

The API major must match.
The host's API minor must meet the plugin's required minor.
API `1.0` is separate from package version `0.1.0-preview.3`.

Use `context.Host` to inspect actual compatibility information.
Its capability set reports what the composed host provides.
Manifest `needs` enforces requirements before activation.
`[meta].uses` describes behavior but does not enforce access restrictions.

## Load in MCC

Enter these commands at the MCC prompt:

```text
/plugins validate /absolute/path/to/session-journal
/plugins load /absolute/path/to/session-journal
/plugins list
/journal-count
/plugins unload session-journal
```

The examples use the default internal command prefix `/`.
Use the configured prefix if the user changed it.
Unprefixed input can become server chat.

Use a development folder while editing code and resources.
Use `/plugins install /absolute/path/to/package.zip` for a persistent installation.
Installation copies the package into immutable storage.
Editing the author folder does not edit that installed copy.

Check the individual loaded state after each load or reload.
An aggregate operation can succeed while one plugin remains unloaded.
Keep the first load disconnected until configuration checks pass.
