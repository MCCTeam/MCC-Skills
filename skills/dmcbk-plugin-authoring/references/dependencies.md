# Plugin dependencies and communication

## Select the mechanism

| Requirement | Mechanism |
| --- | --- |
| Build reference | Author project's NuGet `PackageReference` |
| Another plugin must run | Manifest `[requires]` |
| Another plugin adds optional behavior | Manifest `[optional]` and absence handling |
| Private helper DLL | Package `deps` list |
| Shared typed data | Provider's exported contract assembly |
| Required host module | Manifest `needs` |
| Direct typed operations | `context.Services` |
| Notifications or typed requests | `context.Messenger` |

A NuGet reference does not install another plugin.
A manifest dependency does not restore a NuGet package.

## Required and optional plugins

```toml
[requires]
price-provider = ">=1.0.0 <2.0.0"

[optional]
alerts = ">=3.0.0 <4.0.0"
```

Required dependencies must be installed and loaded at compatible versions.
Resolution includes transitive requirements before installation changes begin.
Missing providers, conflicting required ranges, and required cycles reject the plan.

Optional dependencies do not install automatically.
The runtime orders a compatible installed optional provider before its consumer.
Absence or incompatibility must not break the consumer's essential behavior.
Treat the optional service as unavailable.

Only one active version exists for each plugin ID.
Required version ranges must intersect across consumers.
Use ranges supported by the runtime's SemVer parser.
Examples include `1.2.3`, `^2.1.0`, and `>=2.1.0 <2.4.0`.
Keep explicit preview bounds when testing preview releases.

Pins restrict version changes.
Yanked releases remain in history.
New selection excludes yanked releases, but a compatible installed version can remain selected.

## Export a contract

A contract assembly contains public interfaces and immutable message records.
Keep implementation types and private library dependencies outside that assembly.

```csharp
namespace Pricing.Contracts;

public interface IPriceService
{
    double Subtotal(double unitPrice, double count);
}

public sealed record QuoteRequest(double UnitPrice, double Count);
public sealed record QuoteReply(double Total);
public sealed record OrderPriced(double Total);
```

The provider's package includes `Pricing.Contracts.dll` and declares:

```toml
[exports]
assemblies = ["Pricing.Contracts.dll"]
```

The consumer builds against the matching contract definition.
The consumer declares the provider under `[requires]`.
At runtime, its assembly reference resolves through the provider's load context.
Do not ship another private copy in the consumer package.

Two same-named interfaces loaded from different contexts are different CLR types.
This is a type-identity failure, not a missing method.
The SDK can diagnose mismatched private contracts.
Provider exports take precedence in this preview. A redundant consumer copy can remain unused when the export declaration is correct.
A missing export declaration permits separate private identities and breaks typed communication. Exclude the duplicate instead of relying on resolution precedence.

The token `"entry"` exports a provider's entry assembly.
It can support a single-file source provider.
A small separate contract assembly usually gives a more stable public surface.

## Publish and consume services

Provider activation can register a typed service:

```csharp
context.Services.Register<IPriceService>(new PriceService());
```

The provider retains its implementation privately.
Consumers request the public contract:

```csharp
if (context.Services.TryGet<IPriceService>(out var pricing))
{
    double total = pricing.Subtotal(3, 4);
}
```

`Register<T>` accepts class or interface types.
It returns a disposable registration handle.
The host also withdraws owned registrations on unload.

Re-resolve optional services when each operation starts.
Do not keep a provider's service after that provider unloads.
Retained references can prevent its load context from unloading.

## Notifications and requests

```csharp
context.Messenger.Subscribe<OrderPriced>(message =>
    context.Variables.Set("latest_order_total",
        message.Total.ToString(CultureInfo.InvariantCulture)));

context.Messenger.RegisterResponder<QuoteRequest, QuoteReply>(request =>
    new QuoteReply(request.UnitPrice * request.Count));

context.Messenger.Publish(new OrderPriced(12.0));

bool replied = context.Messenger.TryRequest<QuoteRequest, QuoteReply>(
    new QuoteRequest(3, 4), out var reply);
```

Callbacks use the shared contract types.
These responder and notification callbacks are synchronous.
Do not block them with network work.
Check the boolean result and nullable reply when a responder can be absent.
Dispose returned handles for early withdrawal.

## Private managed dependencies

```toml
deps = ["lib/PrivateHelper.dll"]
```

Package each required private helper under the declared path.
Different plugins can use different private library versions.
Their private libraries belong to separate collectible load contexts.

DMCBK, UMPK, and designated framework contracts remain shared with the host.
Do not package duplicate host contract DLLs.
The runtime rejects these copies.

The load context controls assembly resolution.
It does not restrict file or network access.
Plugins run inside the host process with the host's permissions.
Compatibility checks are not a security sandbox.

## Diagnose loading failures

1. Check the plugin ID and installed provider version.
2. Check the consumer's required version range.
3. Check the provider's individual loaded state.
4. Check exported assembly names and paths.
5. Check the consumer for duplicate exported contracts.
6. Check the package for duplicate host assemblies.
7. Check private helper paths and dependency metadata.

Test the dependency graph and typed runtime calls together.
A successful consumer build does not prove shared runtime identity.
