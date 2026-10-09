# Beacon integration

Beacon is the host's scripting language and scheduler.
The plugin bridge adds functions, variable maps, custom events, and calls into running scripts.

## Two capability boundaries

The plugin manifest declares a required host capability:

```toml
needs = ["commands", "beacon"]
```

An extension function declares its script capability:

```csharp
context.Beacon.Functions.Register(new BeaconFunction(
    Name: "subtotal",
    Capability: "shop.calculate",
    Description: context.Strings.Get("shop.subtotal_help"),
    Parameters: ["price", "count"],
    ParameterTypes: [typeof(double), typeof(double)],
    ReturnType: typeof(double),
    Invoke: call =>
    {
        call.Cancellation.ThrowIfCancellationRequested();
        return Task.FromResult<object?>(
            call.RequireNumber(0) * call.RequireNumber(1));
    }));
```

The script declares that capability and selects the provider:

```beacon
# beacon 1
# needs: shop.calculate
extern subtotal from "shop-tools"
assert(subtotal(3, 4) is 12, "plugin subtotal")
show subtotal(3, 4)
```

The host capability permits integration.
The script capability permits the script's use of the declared extension.
They have different names and purposes.

## Lazy engine initialization

Composing the Beacon module does not create its engine immediately in this preview.
Plugin registrations can remain pending before the first script or session uses Beacon.
Initialize the engine before plugin activation when testing an extension while disconnected.

```csharp
using DMCBK.Core;

host.Client.Scripts.SetMuted(false);
host.AddPluginFolder(packageFolder);
var result = await host.LoadAsync(host.Token);
```

This code uses the supplied `PluginTestHost`.
`SetMuted(false)` initializes the engine and allows script chat.
Use `SetMuted(true)` when the host must hold script chat.
Apply the same initialization before `PluginHost.LoadAllAsync` in a custom host.

Load providers before running scripts that require their capabilities.
Check each provider's loaded state.
An unresolved pre-session `extern` can indicate pending lazy initialization.

## Supported values

| Beacon value | C# boundary value |
| --- | --- |
| Text | `string` |
| Number | Supported numeric scalar, represented as a Beacon number |
| Yes/no | `bool` |
| List | List with supported boundary values as elements |
| Map | String-keyed dictionary with supported boundary values |
| None | `null` |

Declare static list and map signatures with `object` elements or values.
For example, use `IReadOnlyList<object>` or `IReadOnlyDictionary<string, object>`.
Nullable annotations do not change CLR type identity.
Do not return private DTOs, services, or session objects.
Copy internal mutable data into a fresh map or list.

Specify argument names, argument types, and the return type.
Static validation catches unsupported signatures during registration.
Call-time validation still checks the returned object.

Use `RequireNumber`, `RequireText`, and `RequireYesNo` for arguments.
Do not cast internal Beacon value types without checking them.

## Function ownership

Function callbacks run on the Beacon scheduler.
They do not run on the session loop.
Keep synchronous work short.
Pass `call.Cancellation` into asynchronous I/O.
Make callbacks safe for simultaneous calls.
Do not steer directly from an extension callback.
Return data for script-side movement operations.

The registration returns an `IDisposable` handle.
Dispose it to withdraw the function early.
The host also withdraws registrations during unload, disable, and reload.

## Read-only variable maps

```csharp
context.Beacon.Variables.Register(new BeaconVariable(
    Name: "shop",
    Capability: "shop.read",
    Description: context.Strings.Get("shop.snapshot_help"),
    Snapshot: cancellation =>
    {
        cancellation.ThrowIfCancellationRequested();
        return new Dictionary<string, object?>
        {
            ["balance"] = 12.0,
            ["currency"] = "coins"
        };
    }));
```

Scripts can read fields such as `shop.balance`.
The callback runs inline during dispatch.
Do not block or expose a mutable internal object.
Field names form part of the script contract.

## Custom events

Register the event schema before dispatching an event:

```csharp
context.Beacon.RegisterEvent(
    name: "order_priced",
    fields: ["total"],
    description: context.Strings.Get("shop.event_help"),
    capability: "shop.events");

await context.Beacon.FireEventAsync(
    "order_priced",
    new Dictionary<string, object?> { ["total"] = 12.0 },
    session.Detached);
```

Use `session.Detached` when the event belongs to that session.
Use plugin-owned cancellation for work that remains meaningful while disconnected.
A canceled detach token prevents dispatch into an ended session.
Keep event names and field names stable across compatible releases.
Inspect unsuccessful dispatch results without repeating an external effect accidentally.

## Call a script export

```csharp
object? result = await context.Beacon.CallFunctionAsync(
    "shop", "subtotal", [3.0, 4.0], cancellation);
```

The script ID is its file name without an extension.
The script must be running and must declare the function with `export function`.
Missing scripts, exports, and argument mismatches raise `BeaconCallException`.
Use bounded cancellation.

## Diagnostic checks

| Failure | Check |
| --- | --- |
| Provider absent before connection | Engine initialization before activation |
| Function absent | Plugin loaded state and registered function name |
| Capability absent | Script header and function capability |
| Argument failure | Declared types and supplied values |
| Return failure | Unsupported object crossing the boundary |
| Function absent after reload | Replacement plugin's new registration |

The Session Journal verifier checks the engine before connection and checks registration after reload.
It does not perform a live server action.
