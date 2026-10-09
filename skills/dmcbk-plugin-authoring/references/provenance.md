# Reference scope and version

This skill targets one tested package baseline:

- DMCBK packages: `0.1.0-preview.3`.
- UMPK packages: `0.9.0-beta.4`.
- Plugin API contract: `1.0`.
- Managed framework: `net10.0`.
- Example plugin release: `1.0.0`.

The author projects use published NuGet packages exclusively.
The runtime verifier loads the actual source and compiled packages.
The validation used .NET SDK `10.0.401`.

## Research inputs

The reference text uses these documentation topics:

- DMCBK plugin setup, lifecycle, commands, settings, resources, Beacon, dependencies, testing, and release guides.
- DMCBK PluginAuthoring examples, including Session Journal and its verifier.
- DMCBK public plugin SDK contracts and package XML documentation.
- MCC plugin management and development documentation.
- UMPK package XML documentation for the public type namespaces.

The bundled API reference contains public declarations and explanatory notes.
The skill does not require a source checkout to read or use those declarations.
The examples are standalone author templates with local resources.
The examples do not contain private host implementation code.

## Limits

The examples use portable managed code.
Validation does not prove native library execution or live server behavior.
Fresh in-memory clients prove restart persistence and new-session callbacks.
They do not prove reconnect on one continuing client.

Manifest ranges describe compatibility constraints.
The tests establish results only for the stated package baseline.
Check SDK differences before migrating to another preview.
Use installed NuGet XML or public SDK documentation when a required member is absent from this focused reference.
