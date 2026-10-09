# Public API reference

This is a focused authoring reference for DMCBK `0.1.0-preview.3`.
UMPK members use engine `0.9.0-beta.4`.
Declarations below describe public members used by this skill.
They omit implementations and unrelated members.
Do not treat these fragments as replacement SDK source files.

## Plugin entry

Namespace: `DMCBK.PluginSdk`.

```csharp
public interface IPlugin
{
    void Configure(PluginDescriptor descriptor);
    Task ActivateAsync(PluginContext context);
    Task DeactivateAsync(CancellationToken ct) => Task.CompletedTask;
}

public interface IValidatablePluginSettings
{
    void Validate();
}
```

`DeactivateAsync` has a default no-op implementation.
Declare a matching public method when the plugin owns resources.
The host discovers the implementing plugin type and creates an instance.
Keep the entry class public and instantiable.

`PluginDescriptor` exposes:

```csharp
string Id { get; set; }
string Version { get; set; }
int ApiVersion { get; set; }
Type? SettingsType { get; set; }
PluginDescriptor WithSettings<TSettings>() where TSettings : class, new();
```

Manifest identity and version values take precedence when present.
Keep the descriptor and manifest values consistent.

`PluginApiVersion.Major` is `1`.
`PluginApiVersion.Minor` is `0`.
`PluginApiVersion.Current` returns `"1.0"`.

## Plugin context

`PluginContext` provides these public properties:

```csharp
HostInfo Host { get; }
DMCBK.Core.Client Client { get; }
DMCBK.Core.GameApi Game { get; }
IPluginCommandScope Commands { get; }
ISessionScope Session { get; }
ISessionScope? CurrentSession { get; }
bool InSession { get; }
PluginSettings Settings { get; }
IPluginStorage Storage { get; }
Microsoft.Extensions.Logging.ILogger Logger { get; }
Umpk.Text.ITranslationSource Translations { get; }
IPluginLocalization Strings { get; }
IChatClassifier Chat { get; }
Umpk.Hosting.ICronScheduler Cron { get; }
IPluginMessenger Messenger { get; }
IPluginServices Services { get; }
DMCBK.Core.Commands.VariableStore Variables { get; }
IBeaconHost Beacon { get; }
```

Session lifecycle events:

```csharp
event EventHandler<SessionCreatedEventArgs>? SessionCreated;
event EventHandler<SessionScopeEventArgs>? SessionStarted;
event EventHandler<EventArgs>? SessionEnded;
```

`SessionScopeEventArgs.Session` returns `ISessionScope`.
`SessionCreatedEventArgs.Session` returns `IPreSessionScope`.
`SessionCreatedEventArgs.Client` returns an unconnected `Umpk.Client.UmpkClient`.

`BeforeConnect`, `ConfigurationReloaded`, and `BeforeExit` are additional context events.
Use the new configuration snapshot supplied by `ConfigurationReloaded`.
Use bounded shutdown deferral from `BeforeExit` for asynchronous final work.
Check the corresponding restored package documentation before authoring those specialized handlers.

## Session scope

Namespace: `DMCBK.PluginSdk`.

```csharp
public interface ISessionScope
{
    Umpk.Client.UmpkClient Client { get; }
    Umpk.Client.ClientState State { get; }
    Umpk.Client.ClientEvents Events { get; }
    Umpk.Client.ClientActions Actions { get; }
    Umpk.Client.Plugins.PluginScheduler Scheduler { get; }
    IPluginCommandScope Commands { get; }
    CancellationToken Detached { get; }
    Umpk.Client.Movement.IMovementLease? TryAcquireMovement(string reason);
    string? MovementOwner { get; }
    ISessionChannels Channels { get; }
    Umpk.Client.ClientActionCapabilities Capabilities { get; }
    Umpk.Client.Plugins.PluginChannelRegistration RegisterPluginChannel(
        Umpk.Identifier channel, Action<ReadOnlyMemory<byte>> onMessage);
    ValueTask SendPluginMessageAsync(
        Umpk.Identifier channel, ReadOnlyMemory<byte> data,
        CancellationToken ct = default);
    IDisposable ObservePackets(Umpk.Protocol.Java.PacketFrameHandler handler);
}
```

The `Events`, `Actions`, and related types above use their public namespaces from the engine packages.
Use IDE completion or the installed package XML when selecting individual engine methods.
Do not infer game-action signatures from legacy MCC `ChatBot` APIs.

## Commands

```csharp
public interface IPluginCommandScope
{
    IDisposable Register(DMCBK.Core.Commands.CommandBase command);
}
```

`DMCBK.Core.Commands.CommandBase` requires:

```csharp
public abstract string CmdName { get; }
public abstract string CmdDesc { get; }
public abstract string CmdUsage { get; }
public abstract void Register(
    Umpk.Commands.CommandBuilder<DMCBK.Core.Commands.CommandContext> builder);
```

The bundled author projects compile a complete literal command example.
Use that implementation before extending the argument tree.

## Settings, storage, and localization

`PluginSettings` exposes:

```csharp
string FilePath { get; }
bool Exists { get; }
T Load<T>() where T : class, new();
void Save<T>(T settings) where T : class;
```

```csharp
public interface IPluginStorage
{
    string DataDirectory { get; }
    string GetPath(string relativeName);
    bool TryGet(string key, out string? value);
    void Set(string key, string value);
    bool Remove(string key);
    void Save();
}

public interface IPluginLocalization
{
    string Get(string key);
    string Format(string key, params object?[] args);
    IReadOnlyList<string> Languages { get; }
}
```

`IPluginLocalization` also supplies a coverage report.
The snippets omit that reporting member because the examples do not need it.

## Services and messages

```csharp
public interface IPluginServices
{
    IDisposable Register<T>(T instance) where T : class;
    bool TryGet<T>(out T? instance) where T : class;
}

public interface IPluginMessenger
{
    IDisposable Subscribe<T>(Action<T> handler);
    void Publish<T>(T message);
    IDisposable RegisterResponder<TRequest, TResponse>(
        Func<TRequest, TResponse> responder);
    bool TryRequest<TRequest, TResponse>(TRequest request, out TResponse? response);
}
```

`TryGet` marks its output non-null on success.
An incompatible private contract can raise `PluginContractMismatchException`.
That failure differs from an absent optional service.

## Beacon bridge

```csharp
public sealed record BeaconFunction(
    string Name,
    string Capability,
    string Description,
    IReadOnlyList<string> Parameters,
    IReadOnlyList<Type>? ParameterTypes,
    Type? ReturnType,
    Func<BeaconCallContext, Task<object?>> Invoke);

public sealed record BeaconVariable(
    string Name, string Capability, string Description,
    Func<CancellationToken, object?> Snapshot);
```

`BeaconCallContext` exposes these public members:

```csharp
string Function { get; }
string CallerScriptId { get; }
CancellationToken Cancellation { get; }
int Count { get; }
string RequireText(int index);
double RequireNumber(int index);
bool RequireYesNo(int index);
```

The call also exposes the source span and evaluated Beacon arguments.
Use the typed argument helpers for the common scalar boundary.

```csharp
public interface IBeaconHost
{
    IBeaconFunctionRegistry Functions { get; }
    IBeaconVariableRegistry Variables { get; }
    IDisposable RegisterEvent(
        string name, IReadOnlyList<string> fields, string description,
        bool suppressible = false, string? capability = null);
    Task<DMCBK.Core.Beacon.BeaconFireResult> FireEventAsync(
        string name, IReadOnlyDictionary<string, object?> fields,
        CancellationToken detached = default);
    Task<object?> CallFunctionAsync(
        string scriptId, string function, IReadOnlyList<object?> args,
        CancellationToken ct = default);
}
```

`Functions.Register(BeaconFunction)` and `Variables.Register(BeaconVariable)` return `IDisposable` handles.

## Test harness

Namespace: `DMCBK.Testing`.

```csharp
PluginTestHost.Create(PluginTestHostOptions? options = null);
string AddPluginFolder(string folder, bool enable = true);
Task<PluginActionResult> LoadAsync(CancellationToken ct = default);
Task RunSessionAsync(Func<PluginTestSession, Task> body,
    CancellationToken ct = default);
Task<bool> WaitForAsync(Func<bool> condition, CancellationToken ct = default);
string DataFile(string id, string relative);
```

`PluginActionResult` belongs to `DMCBK.Core.Plugins`.
The harness provides `Client`, `Plugins`, and a bounded `Token`.
Dispose the harness with `await using`.

`PluginTestSession` supports:

```csharp
Task AnnounceChannelsAsync(params Umpk.Identifier[] channels);
Task SendPluginMessageAsync(Umpk.Identifier channel, byte[] data,
    CancellationToken ct = default);
Task<(int WireId, byte[] Payload)> NextFrameAsync(CancellationToken ct = default);
```

See `references/testing.md` for what these tests prove.
