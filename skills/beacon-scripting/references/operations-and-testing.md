# Operations and testing

These procedures use an installed MCC distribution.
They do not require an MCC or DMCBK source checkout.
Other DMCBK hosts supply their own loading and testing procedures.

## Data directory

`--configurations /data/configurations` selects MCC's configuration root.
Discovered Beacon files then belong in `/data/scripts`.

```text
mcc-data/
  configurations/
    client.toml
    accounts.toml
    servers.toml
    console.toml
    beacon.toml
    beacon/
      welcome.settings.toml
      welcome.toml
  scripts/
    welcome.bcn
    lib/
      math.bcn
    data/
      reports/
```

| Path | Purpose |
| --- | --- |
| `scripts/*.bcn` | Top-level discovered source. Discovery does not start it. |
| `scripts/lib/*.bcn` | Imported libraries distributed with their callers. |
| `scripts/data/` | Shared restricted file area. |
| `configurations/beacon.toml` | Network allowlist. |
| `configurations/beacon/<id>.settings.toml` | User setting overrides. |
| `configurations/beacon/<id>.toml` | Saved runtime values. |

Use a stable filename for a stable script ID.
Keep account credentials in MCC's authentication configuration.
Do not place credentials in Beacon source or general state.

## Terminal commands

Run these from the MCC application directory.
Use full script paths.
`./Mcc.Cli` is the executable from a Linux or macOS distribution.
Windows PowerShell uses `.\Mcc.Cli.exe`.
A framework-dependent distribution uses `dotnet /full/path/Mcc.Cli.dll`.
An installed `mcc` launcher can substitute for the executable.

```text
Mcc.Cli lint <file...> [--format text|json] [--target-lib N] [--strict] [--fix]
Mcc.Cli run <file...> [--seed N] [--tick S] [--format text|json]
Mcc.Cli format <file...> [--check]
```

All three commands accept `--stdin` and `--stdin-name name.bcn`.
One-shot commands run before normal configuration loading.
They do not create a login session or configuration directory.

| Option | Command | Meaning |
| --- | --- | --- |
| `--format text` | lint, run | Readable report. Default format. |
| `--format json` | lint, run | Structured diagnostics and results. |
| `--target-lib 2` | lint | Check standard-library compatibility. The source header remains version `1`. |
| `--strict` | lint | Escalate unresolved providers and unverifiable integration calls. |
| `--fix` | lint | Apply supported source corrections. Review the diff. |
| `--seed 42` | run | Use repeatable random choices. Default seed is `1234`. |
| `--tick 10` | run | Advance virtual time once after loading. Default is zero seconds. |
| `--check` | format | Report formatting changes without writing files. |
| `--stdin` | all | Read source from standard input. |
| `--stdin-name file.bcn` | all | Set the reported source name. |

```sh
./Mcc.Cli lint /full/path/calculations.bcn --target-lib 2 --strict --format json
./Mcc.Cli run /full/path/calculations.bcn --seed 42 --format json
./Mcc.Cli run /full/path/timers-tasks.bcn --seed 42 --tick 10
./Mcc.Cli format /full/path/calculations.bcn --check
```

Normal `format` rewrites source.
`format --stdin` returns formatted source on standard output.
Use an explicit file path when imports are present.

| Exit code | Meaning |
| --- | --- |
| `0` | Success. Normal lint warnings do not fail the command. |
| `1` | Script failure, lint error, or formatting change under `--check`. |
| `2` | Invalid arguments or file access failure. |

Read both the exit code and diagnostics.
Do not treat an empty output list as proof that handlers ran.

## Commands inside MCC

Enter these at MCC's input prompt.
They are internal commands, not operating-system commands.
Examples assume the default internal command prefix `/`.

| Command | Effect |
| --- | --- |
| `/scripts`, `/scripts list` | List running script IDs and mute state. |
| `/scripts run <id|file> [--trace]` | Load source and register handlers. |
| `/scripts stop <id|all>` | Stop one script or every script. |
| `/scripts reload [id]` | Reload one script or all running scripts. |
| `/scripts lint <file...> [options]` | Use the shared lint engine. |
| `/scripts new <template> <id>` | Create a template without overwriting a file. |
| `/scripts mute [on|off]` | Inspect or change script chat suppression. |
| `/scripts repl [--seed N] [line]` | Evaluate a line against the current host. |
| `/scripts watch [on|off]` | Inspect or change automatic source reload. |
| `/scripts config <id> [key value]` | Inspect or edit declared settings. |
| `/scripts format <file> [--check]` | Format a file or report changes. |
| `/scripts ui` | Open the TUI script manager. |
| `/help scripts` | Show command help. |

Bare IDs resolve under the configured scripts directory.
An existing explicit file path takes priority.
In-client JSON lint returns a command message even when its report contains errors.
Inspect `summary` and diagnostics inside that report.

Template names are `empty`, `welcome`, `guard`, and `shop`.
Template creation writes `<id>.bcn`.
Use letters, numbers, hyphens, and underscores for IDs.
The shop template starts with an empty saved price map.

## Script lifecycle

Stopping removes handlers, timers, commands, and exports.
Stopping preserves saved state and settings.
Reload creates new globals and registrations.
Inspect diagnostics after every reload.
Watching is opt-in and can repeat top-level side effects after edits.
Use manual reload until those effects are understood.

Mute suppresses script chat while logic continues.
Mute does not stop movement, inventory actions, file writes, or HTTP calls.
Use `/scripts stop <id>` to stop automation.

A REPL is an interactive evaluator.
Its local variables persist between REPL lines.
The live REPL can perform real game actions.
Use one-shot `run` for isolated offline checks.

## Scheduler and cancellation

A scheduler controls tasks, waits, and timer execution.
Scheduled waiting yields execution instead of blocking the connection loop.
Keep task IDs when later cancellation matters.
Use `tasks()` and inspect each record's status.
Settled records can remain in that list.
`await id` waits for completion and can report task failure or cancellation.
`cancel task id` requests cancellation and interrupts a pending wait.

Disconnect invalidates session observations and cancels pending waits.
Reconnect cancels old running tasks and pending one-shot timers.
Login and reconnect handlers can start fresh session work.
Recurring timers resume with at most one catch-up firing per timer.
They do not replay every missed interval.
Reload cancels pending tasks and recreates registrations.
Shared RAM and saved state have different lifetimes from task state.

## Validation levels

| Level | Method | Evidence |
| --- | --- | --- |
| Static | Public CLI `lint`. | Syntax, declarations, and known API compatibility. |
| Offline logic | Public CLI `run`. | Executed top-level calculations and due timer bodies. |
| Simulated event | A configured DMCBK testing host. | A chosen event requests the expected action. |
| Live session | MCC connected to a controlled server. | Host integration and observed server effects. |

Offline `run` uses empty game observations, virtual time, and seeded randomness.
It can register handlers but does not deliver Minecraft events.
It does not prove chat delivery, inventory transactions, movement, or persistent file configuration.
A successful simulated request does not prove server acceptance.

## Repeatable check sequence

1. Read every file in the deliverable.
2. Run lint with explicit paths.
3. Review required and optional provider diagnostics.
4. Run calculation assertions with a fixed seed.
5. Advance virtual time for timer tests.
6. Compare output with the expected values.
7. Run formatting checks.
8. Start MCC with the selected configuration root.
9. Load providers before dependent callers.
10. Load the target script with tracing.
11. Produce a matching live trigger.
12. Produce an unrelated trigger.
13. Check the resulting server observation.
14. Check stop, reload, and reconnect behavior when relevant.
15. Report each validation level separately.

```sh
./Mcc.Cli --configurations /full/path/mcc-data/configurations
```

```text
/scripts lint greet-counter
/scripts run greet-counter --trace
/scripts list
/greeting-stats
/scripts stop greet-counter
```

A greeting event needs another player to send the matching message.
Loading the greeting script alone does not test that event.

## Diagnose failures

| Symptom | First check |
| --- | --- |
| File missing | Configuration root, scripts directory, filename, and extension. |
| Header error | First line of the actual file. |
| Unknown function | Exact name, import path, and provider availability. |
| Capability refusal | Header declarations and provider capability. |
| Game action unavailable | Tracking settings, live session, and protocol support. |
| Handler silent | Running ID, exact filter, event arrival, and cooldown state. |
| World read missing | Loaded tracked terrain near the requested coordinates. |
| Saved count lost | Stable script ID and original configuration root. |
| Network refused | HTTPS URL and bare host allowlist entry. |
| Formatting check fails | Reported diff, then normal formatting if appropriate. |

Fix the first diagnostic before investigating later failures.
Preserve provider declarations when offline resolution is the only limitation.
