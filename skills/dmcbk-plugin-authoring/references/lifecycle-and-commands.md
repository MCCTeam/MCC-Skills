# Lifetimes, sessions, and commands

## Lifecycle order

| Hook | Use |
| --- | --- |
| `Configure` | Declare identity, API major, and settings type without side effects |
| `ActivateAsync` | Register behavior for the plugin lifetime |
| `BeforeConnect` | Inspect, redirect, or veto the connection plan |
| `SessionCreated` | Register observers before handshake, login, and configuration |
| `SessionStarted` | Register work for a new play session |
| `SessionEnded` | Remove references to the ended session |
| `ConfigurationReloaded` | Read the supplied new configuration snapshot |
| `BeforeExit` | Finish bounded shutdown work while a session can still exist |
| `DeactivateAsync` | Release resources that the plugin created |

Activation runs once per loaded instance.
Reconnect does not activate that instance again.
Reload creates a replacement instance.

A plugin loaded during play can receive `SessionStarted` for the existing session.
It cannot assume that it received `SessionCreated` for that session.
Use `SessionCreated` when the first handshake or channel packet matters.
Do not request game actions from an unconnected pre-session client.

## Session ownership

`SessionStarted` supplies a fresh `ISessionScope` for each connection.
Use `args.Session` inside the callback.
Do not cache that scope for use after disconnect.

The scope exposes the following resources:

| Member | Purpose |
| --- | --- |
| `State` | Current tracked state |
| `Actions` | Requested effects, including chat, interaction, inventory, and movement |
| `Events` | Scoped event subscriptions |
| `Scheduler` | Scoped work on or outside the session loop |
| `Commands` | Commands that end with this session |
| `Channels` | Plugin-channel registration and messages |
| `Capabilities` | Actions supported by the negotiated protocol |
| `Detached` | Cancellation when the scope ends |

The host releases scoped registrations when the session or plugin ends.
The host also releases plugin-owned commands and bridge registrations on unload.
It does not dispose arbitrary resources that the plugin creates independently.

Examples of independently owned resources include HTTP clients, sockets, file handles, and background tasks.
Dispose these resources during deactivation.
Remove arbitrary subscriptions to external event sources.

`context.Cron` spans reconnects and can run while disconnected.
Check `CurrentSession` before a cron callback requests a game action.
Do not treat a cron schedule as session cancellation.

## Cancellation

Pass `session.Detached` into session work.
This token also cancels when the plugin unloads during another plugin's continuing session.
Check cancellation before requests whose results are no longer useful.

For an independently owned worker:

1. Create a cancellation source for the worker's actual lifetime.
2. Link it to `session.Detached` when the worker uses session state.
3. Retain the worker task so deactivation can await it.
4. Cancel the worker when its lifetime ends.
5. Await the worker with the deactivation deadline.
6. Dispose its resources.

The host limits the wait for `DeactivateAsync`.
It cancels the supplied token when its teardown budget expires.
It can continue unloading after that budget.
Do not depend on an unlimited shutdown wait.

Avoid `async void` event callbacks.
Prefer scoped scheduling for asynchronous event work.
If separate workers are necessary, define ownership and observe their failures.
Do not hold a lock across an `await`.

## Commands

The command API uses a typed command tree.
The host renders help and supplies the internal command prefix.

```csharp
using DMCBK.Core.Commands;
using DMCBK.PluginSdk;
using Umpk.Commands;

public sealed class PingCommand(IPluginLocalization strings) : CommandBase
{
    public override string CmdName => "plugin-ping";
    public override string CmdDesc => strings.Get("ping.description");
    public override string CmdUsage => "plugin-ping";

    public override void Register(CommandBuilder<CommandContext> builder)
        => builder.Literal(CmdName, command => command.Executes(
            call => call.Source.Result.Ok(strings.Get("ping.reply"))));
}
```

Register a persistent command once:

```csharp
context.Commands.Register(new PingCommand(context.Strings));
```

Register a session-only command within `SessionStarted`:

```csharp
context.SessionStarted += (_, args) =>
    args.Session.Commands.Register(new PingCommand(context.Strings));
```

Use only one ownership pattern for a given command.
Do not register a persistent command again on every reconnect.
Do not use permanent host command registration for plugin code.
Permanent registrations can retain the plugin after unload.

`CmdUsage` contains a command grammar, not a help sentence.
`CmdDesc` and command output use translated plugin strings.
`CommandContext.Result.Ok` returns local command output.
It does not send chat to the server.

Add arguments through the command builder.
Check the restored package's documented command types before selecting a specific argument API.
Do not invent Brigadier helper names or add a raw string parser.

## Packets and movement

`ObservePackets` observes raw sent and received frames.
The callback runs on the read loop or sender path.
It does not run on the session loop.
Do not block that callback.
Use `PacketFrame.CopyPayload()` when bytes must outlive the callback.

`TryAcquireMovement(reason)` can return null when another owner holds movement.
Do not steer without acquiring the lease.
Dispose the lease when the operation stops.
Use `MovementOwner` to inspect ownership without briefly acquiring a lease.

Reading state does not modify the server.
Use action APIs for effects.
Check enabled tracking before interpreting absent terrain, entities, or inventory.
Check protocol capabilities before requesting a version-dependent action.

## Cleanup checks

1. Load the plugin while disconnected.
2. Execute each plugin command.
3. Connect and observe one session callback.
4. Disconnect and observe detach cancellation.
5. Reconnect on the same client.
6. Check that each callback runs once.
7. Unload the plugin.
8. Check that commands, tasks, subscriptions, channels, and movement ownership end.

An in-memory test with fresh clients cannot prove step five.
Use a controlled reusable server for the same-client reconnect check.

The preview can announce an existing play session when a plugin activates during play. Make session setup idempotent.
The counter example observes SessionCreated before counting SessionStarted. It ignores replayed starts after a connected reload.
A connection already active before loading the counter is not a new counted connection.
