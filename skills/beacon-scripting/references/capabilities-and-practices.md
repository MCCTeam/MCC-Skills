# Capabilities and practices

A capability names a permitted operation.
Required capabilities use `# needs:`.
Optional capabilities use `# wants:` and need a useful fallback.
The loader checks all function and handler bodies, including branches that do not run during loading.

## Capability table

| Capability | Operations | Additional requirement |
| --- | --- | --- |
| `chat.send` | `say`, `whisper` | Connected session and chat delivery. |
| `server.send` | `server` statement | Connected session and server permission. |
| `mcc.run` | MCC command expression or statement. | MCC's internal command dispatcher. |
| `server.disconnect` | `disconnect` | An active session to leave. |
| `inventory.read` | `inv` reads, recipes, trade reads, enchant reads. | Inventory tracking. |
| `inventory.write` | `inv` changes, crafting, trade/enchant selection. | Tracking and negotiated action support. |
| `world.read` | Block, light, biome, and sign observations. | Terrain tracking and loaded data. |
| `world.search` | Block and sign searches. | Terrain tracking and bounded search. |
| `world.write` | Dig, place, use, and targeting reads. | Terrain, physics, and supported gameplay actions. |
| `entity.read` | Entity reads and appearance/removal events. | Entity tracking. |
| `entity.write` | Attack and interaction. | Tracked target and action support. |
| `movement` | `move_goto`, `move_follow` | Terrain, physics, navigation data, and action support. |
| `dialog.read` | Dialog reads and events. | Supported dialog observations. |
| `dialog.write` | Dialog input and button actions. | Active supported dialog. |
| `fs.read` | Restricted file reads. | Configured data directory. |
| `fs.write` | Restricted file writes. | Configured data directory. |
| `net.fetch` | HTTP helper calls. | HTTPS and destination allowlist. |
| `econ.read` | Reserved known capability. | Declaring this name does not supply an economy service. |

Plugins can supply additional capability names.
Use the exact names from their installed provider documentation.
Declarations do not enable tracking, create providers, connect MCC, or grant server permissions.

Current inference assigns no capability to `look_at`, `stop_moving`, `eat`, or `use_in_hand`.
Those functions still depend on host support and live prerequisites.
Do not treat absent inference as proof of unrestricted access.

## Limits

| Limit | Value or behavior |
| --- | --- |
| Source syntax version | `1`. |
| Standard-library version | `2`. |
| Execution fuel | 100,000 units per dispatch. |
| Wall-clock budget | Five seconds per dispatch, with scheduler-aware treatment of yielding work. |
| Function depth | 256 nested calls. |
| Chat allowance | Eight messages per ten seconds across scripts in one runtime. Excess requests queue. |
| World mutation allowance | Eight mutations per ten seconds per script. Refusals give a retry delay. |
| Minimum wait | 100 milliseconds. |
| Minimum recurring interval | One second. |
| Restricted file size | 1 MiB. |
| HTTP response size | 1 MiB. |
| HTTP request timeout | Five seconds. |
| Import/call lint closure | 32 files. |
| JSON nesting | 32 levels. |
| Generated padding/repetition | 10,000 characters. |
| Player-name page | Default 50, maximum 100. |
| Chat history | Maximum 200 entries. |
| World search | Radius 32 blocks, maximum 64 results. |
| Entity search | Default radius 64, maximum 128, maximum 64 rows. |
| Trade purchase count | One through 64 units per call. |
| Block horizontal bound | Absolute `x` and `z` at most 30,000,000. |
| Block vertical envelope | `y` from -64 through 320. |

Fuel counts execution work such as calls and loop iterations.
Fuel exhaustion means the code needs smaller or bounded work.
An endless retry cannot repair that design.
Queued chat can outlive the event that requested it.
Limit repeated triggers before they create excessive work.

## File and network boundaries

File helpers address the shared `scripts/data` directory.
The runtime rejects absolute paths, parent traversal, and symbolic-link escapes.
These helpers do not grant general host filesystem access.
HTTPS requests require a configured destination host.
A capability declaration does not bypass that allowlist.

Beacon value checks and capability checks do not isolate arbitrary C# plugin code.
Use trusted scripts and providers.
Check external text and JSON before using them as commands or numeric data.

## Writing practices

1. Define the intended trigger and completion condition.
2. Separate calculations from actions.
3. Use descriptive names that do not hide built-in namespaces.
4. Use exact chat filters for command words.
5. Check absent values before arithmetic or nested reads.
6. Check `number(...)` before using its result.
7. Keep retries bounded and delayed.
8. Re-read session data after waits.
9. Use stable item IDs when display text can vary.
10. Keep session IDs out of durable state.
11. Use shared locks only for short state updates.
12. Preserve stable script IDs for saved progress.

A chat name is input, not proof of administrator authority.
Add an explicit authorization rule before accepting remote management commands.
Prefer local MCC commands for operations intended for the MCC operator.

## Action checks

1. Declare the action's inferred capability.
2. Check the gameplay feature prerequisites.
3. Catch missing targets and closed windows.
4. Limit repeated mutations.
5. Check the later observed server result.
6. Provide a stop command.

A successful local action can still fail at the server.
Test writes separately on a controlled server.
State unverified live behavior plainly in the delivery report.

## Common mistakes

| Mistake | Correction |
| --- | --- |
| Set source header to library version. | Keep `# beacon 1`. Target library version with lint or `beacon.lib`. |
| Treat `0` as false under `or`. | Only `no` and `none` choose the fallback. |
| Treat invalid numeric input as a number. | Check the `none` result from `number(...)`. |
| Cancel the first `tasks()` row unconditionally. | Select the intended ID and inspect its status. |
| Treat mute as a stop switch. | Stop the script to end non-chat actions. |
| Assume matching filters protect named cooldowns. | Account for cooldown acquisition before `when`. |
| Treat empty world search as server absence. | Check whether MCC tracks loaded terrain in that area. |
| Edit an inventory snapshot to move items. | Use the documented action function. |
| Treat lint success as a live test. | Trigger the handler and inspect the server observation. |
| Depend on unshipped files. | Include imports and document provider load order. |
