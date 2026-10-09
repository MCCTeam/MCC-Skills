# Plugin tests and evidence

## Three distinct checks

| Check | Evidence |
| --- | --- |
| Author build | C# syntax and restored build references |
| In-memory runtime test | Actual loading, protocol callbacks, registration ownership, and scripted frames |
| Live server test | Actual host, networking, negotiated game behavior, and reconnect |

Add a fourth check for native code: actual execution on every declared process target.
A cross-build only proves compilation for that target.

## Use the provided verifier

Copy `assets/verify-plugin/` to the author output directory.
Its console project uses only published NuGet packages.
It throws when an expectation fails.
A failed run returns a nonzero exit status.

```sh
dotnet restore verify-plugin/VerifyPlugin.csproj
dotnet run --project verify-plugin/VerifyPlugin.csproj \
  --configuration Release -- /absolute/path/to/session-journal-package
dotnet run --project verify-plugin/VerifyPlugin.csproj \
  --configuration Release -- /absolute/path/to/session-journal-package 150
```

The second run checks normalization from 150 to 100.
Run both commands against the source package and the compiled staging directory.
Each run creates isolated user data and removes it after completion.

The checks cover:

1. Manifest parsing and actual source compilation or assembly loading.
2. Individual loaded state after activation.
3. Command dispatch while disconnected.
4. Beacon extension use before connection.
5. A session callback on each fresh harness client.
6. Durable storage shared across those fresh clients.
7. Reload and restored count.
8. Beacon extension use after reload.
9. Command withdrawal after unload.

`PluginTestHost` uses in-memory pipes and real protocol frames.
It opens no socket and requires no Minecraft account.
Its transport closes after a session.
Repeating `RunSessionAsync` on that same harness cannot prove reconnect.
The example creates a new harness client for each session.
Report that result as restart persistence and fresh-session callbacks.

## Await observable conditions

Use `WaitForAsync` for work on the event thread:

```csharp
bool observed = await host.WaitForAsync(
    () => host.Client.Variables.Get("session_journal_sessions") == "1",
    host.Token);
```

A fixed sleep can inspect state before the callback completes.
Keep the harness budget finite.
Increase the budget when CI compilation is slow, but retain a limit.
Pass `host.Token` to asynchronous operations.

Check both the aggregate load result and `Plugins.List()`.
An aggregate success does not prove individual activation.

## Check requested effects

`PluginTestSession.NextFrameAsync` returns a wire ID and copied serverbound payload.
Check the intended packet and its payload.
An unrelated keep-alive or background frame is not evidence of the intended action.

`SendPluginMessageAsync` injects a clientbound channel message.
`AnnounceChannelsAsync` advertises available channels.
`SendAsync<TPacket>` encodes a clientbound packet for the negotiated version.
Use these APIs to test the actual event boundary.

## Expand tests to match behavior

| Behavior | Test |
| --- | --- |
| Settings | Missing, partial, malformed, and out-of-range TOML |
| Persistent data | Save, restart, migration, and downgrade policy |
| Commands | Availability, output, completion, session end, and unload |
| Optional dependency | Absence, incompatible version, provider unload, and new operation |
| Required dependency | Missing provider, range conflict, and cycle diagnostics |
| Exported contract | Shared CLR type identity and typed calls |
| Session worker | Cancellation, observed failure, and bounded teardown |
| Packet observer | Copied payload and short callback |
| Native library | Actual load and operation on each declared target |

Test meaningful behavior, not a copy of the implementation.
The supplied verifier does not claim every row in this table.

## Same-client reconnect

Use MCC or a reusable DMCBK host against a controlled local server.
Use isolated configuration and plugin data directories.
Do not reuse mutable server sessions concurrently across a version matrix.

1. Load the plugin before connecting.
2. Connect and record the session result.
3. Trigger a controlled disconnect.
4. Check that session work cancels.
5. Reconnect on the same client process.
6. Check one callback and one registration per new session.
7. Unload during a live session.
8. Check command removal and worker termination.

For game actions, check the server's resulting state.
For native operations, name the actual process target in the report.

## Report format

Use precise evidence in a short report:

```text
Author build: PASS, .NET SDK <version>, DMCBK 0.1.0-preview.3.
Source runtime: PASS, actual package through DMCBK.Testing.
Compiled runtime: PASS, staged DLL package through DMCBK.Testing.
Settings: PASS, default and normalization case.
Reconnect: UNTESTED, no reusable live server used.
Native targets: UNTESTED, portable managed example only.
Archive: <absolute path>, SHA-256 <digest>.
```

Record the exact commands, exit codes, warnings, and limitations in validation logs.
Keep validation outputs outside assets.
Do not turn an untested compatibility range into a verified support claim.
