---
name: beacon-scripting
description: Write, explain, debug, and check Beacon .bcn automation in MCC or DMCBK hosts. Use for Beacon handlers, timers, game APIs, state, capabilities, or integrations.
license: MIT
compatibility: Targets Beacon source version 1 and standard library version 2 in MCC or DMCBK hosts. CLI checks require installed MCC.
---

# Beacon scripting

Produce complete `.bcn` files for Minecraft Console Client (MCC) or a DMCBK host.
Beacon is an interpreted automation language. MCC includes its interpreter.
DMCBK hosts supply their own configuration, observations, and supported actions.
This skill contains its own language documentation. A source checkout is unnecessary.
The language references apply to both hosts. The public CLI procedures use installed MCC.

## Choose the reference

Read only the references needed for the task.

| Task | Read |
| --- | --- |
| Syntax, values, blocks, functions | [Language](references/language.md) |
| Text, lists, maps, numbers, time | [Standard library](references/standard-library.md) |
| Events, snapshots, game actions | [Events and game APIs](references/events-and-game.md) |
| Settings, storage, imports, exports, plugins | [State and integrations](references/state-and-integrations.md) |
| Installation, CLI commands, validation | [Operations and testing](references/operations-and-testing.md) |
| Capabilities, execution limits, safe design | [Capabilities and practices](references/capabilities-and-practices.md) |
| Complete starting files | [Examples](assets/examples/README.md) |
| Inventory, trade, files, web, and dialog examples | [Cookbook](references/cookbook.md) |

## Establish the required behavior

1. Identify the trigger, input, output, and stop condition.
2. Identify the required game observations and actions.
3. Identify any plugin or running-script provider.
4. Check the selected MCC data directory from available configuration.
5. Preserve existing script IDs when saved progress matters.

Use the available task context before requesting missing information.
Document an assumption when it cannot change the requested behavior.

An observation is data MCC received from the server. It can be missing or outdated.
A capability is a declared permission name. It does not create game data or grant server authority.
A provider is a plugin or running script that supplies an integration.

## Write the script

1. Start the file with `# beacon 1`.
2. Place capability declarations and settings before the first code statement.
3. Declare required operations in `# needs:`.
4. Declare optional capabilities in `# wants:`.
5. Give every optional provider a useful failure response.
6. Place imports and extern declarations before executable blocks.
7. Use `set name to value` for assignment.
8. Use explicit yes/no comparisons in conditions.
9. Close each block with its matching `end` label.
10. Keep game actions inside session events or explicit commands.

Source version `1` and library version `2` are different values.
Do not change the header to `# beacon 2` for a newer library.
Use `beacon.lib` when library compatibility matters.

```beacon
# beacon 1
# needs: chat.send
# setting prefix = "Hello" ; Greeting text
on chat as e when trim(lower(e.message)) is "!hello"
  whisper e.player "{settings.prefix}, {e.player}!"
end on
```

MCC discovers scripts beside its configuration directory.
For `/data/configurations`, store discovered source in `/data/scripts`.
The filename `welcome.bcn` gives the script ID `welcome`.

## Apply runtime boundaries

1. Check optional values with `is set` before reading nested fields.
2. Convert command arguments before numeric calculations.
3. Limit loops, retries, searches, and task creation.
4. Use `wait` to yield scheduled work.
5. Read session data again after a wait.
6. Capture task IDs before cancellation or waiting.
7. Use `lock shared` when reading and writing one shared value.
8. Keep network and file calls outside shared locks.
9. Catch unavailable targets, closed windows, and missing providers.
10. Check a later server observation after each important game action.

`show` writes local output. `say` and `whisper` request Minecraft chat.
`server "/home"` sends a server command. `mcc "help"` invokes MCC's internal dispatcher.
Script commands register inside MCC. They do not create server commands.

Named cooldowns apply before event filters.
An unrelated event can consume the cooldown window.
Use explicit state-based throttling when only matching events should consume the window.
`time.stamp` discards fractional seconds. Use a conservative comparison when a minimum delay matters.

Gameplay configuration belongs in the existing `[Gameplay]` table in `client.toml`.
World writes require `Terrain` and `Physics`.
Navigation also depends on `Pathfinding`.
Inventory and entity operations need their corresponding tracking features.
Reconnect after changing composed session features.

## Check in stages

1. Run lint against the exact files you will deliver.
2. Review every error and provider warning.
3. Run offline calculations with a fixed seed.
4. Advance virtual time when testing timer bodies.
5. Compare output with the expected result.
6. Run formatting checks.
7. Test events and game effects in a controlled live session when available.
8. Test stop, reload, cancellation, and reconnect behavior when relevant.

Use the executable from the MCC distribution:

```sh
./Mcc.Cli lint /full/path/calculations.bcn --target-lib 2 --strict
./Mcc.Cli run /full/path/calculations.bcn --seed 42 --format json
./Mcc.Cli run /full/path/timers-tasks.bcn --seed 42 --tick 10
./Mcc.Cli format /full/path/calculations.bcn --check
```

Use `dotnet /full/path/Mcc.Cli.dll` for a framework-dependent distribution.
Use `.\Mcc.Cli.exe` in Windows PowerShell.
Run terminal commands from the application directory.
Use full source paths so imports resolve consistently.

Inside a running MCC client:

```text
/scripts lint welcome
/scripts run welcome --trace
/scripts list
/scripts stop welcome
```

Offline `run` uses an inert host and virtual time.
It does not inject Minecraft events or prove server effects.
Passing lint does not prove handler execution.
Successful loading registers future work.

## Deliver the result

Provide the script files, imported libraries, and required provider files.
State the installation paths and provider load order.
State the required capabilities and gameplay settings.
Report the commands executed and their results.
Identify live behavior that remains unverified.
Include the command that stops the automation.

Keep instructions short and literal.
Define necessary terms before using them.
Explain the reason for a rule when that reason prevents a likely mistake.
