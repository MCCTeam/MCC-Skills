# Complete Beacon examples

Copy the needed files into the selected MCC data directory's `scripts` folder.
Preserve the `lib` directory beside `calculations.bcn`.
Lint every copied file before loading.
The files use source version `1` and library version `2`.

| File | Purpose | Prerequisites |
| --- | --- | --- |
| `calculations.bcn` | Assert functions, loops, conversion, and JSON behavior. | Include `lib/math.bcn`. |
| `lib/math.bcn` | Imported calculation helper. | Import it from the caller. |
| `greet-counter.bcn` | Exact chat greeting with saved count and per-player delay. | `chat.send`, live parsed chat. |
| `timers-tasks.bcn` | One-shot/recurring timers and bounded task commands. | No game operations. |
| `shared-counter.bcn` | Atomic shared RAM counter. | One shared runtime for repeated loads. |
| `game-report.bcn` | Local inventory, terrain, and entity reports. | `inventory.read`, `world.search`, `entity.read`, corresponding tracking. |
| `movement-helper.bcn` | Explicit local movement and cancellation commands. | `movement`, terrain, physics, pathfinding, connected session. |
| `shop-provider.bcn` | Running function and value exports. | Load before calling its exports. |
| `shop-caller.bcn` | Numeric command input and recoverable provider call. | Running `shop-provider`. |
| `dialog-summary.bcn` | Dialog keys and button counts without private values. | `dialog.read`, supported dialog. |

## Offline checks

Run these from the MCC application directory:

```sh
./Mcc.Cli lint /full/path/scripts/calculations.bcn --target-lib 2 --strict
./Mcc.Cli run /full/path/scripts/calculations.bcn --seed 42
./Mcc.Cli run /full/path/scripts/timers-tasks.bcn --tick 10
./Mcc.Cli run /full/path/scripts/shared-counter.bcn
```

Calculations output includes `Total: 15` and `Calculation checks passed`.
The timer run outputs one `Recurring report` and one `One reminder`.
Advancing ten seconds once does not replay every intermediate tick.
The shared counter outputs `Shared count: 1` in a fresh offline runtime.
Separate offline processes do not share RAM or prove durable saved state.

## Live commands

| Script | Check | Stop |
| --- | --- | --- |
| `greet-counter` | Another player sends `!hello`. Run `/greeting-stats`. | `/scripts stop greet-counter` |
| `timers-tasks` | Run `/task-start`, then `/task-wait <id>` or `/task-cancel <id>`. | `/scripts stop timers-tasks` |
| `game-report` | Run `/game-report` after tracking receives data. | `/scripts stop game-report` |
| `movement-helper` | Run `/travel <x> <y> <z>` on loaded controlled terrain. | `/travel-stop`, then `/scripts stop movement-helper` |
| `shop-provider`, `shop-caller` | Load the provider first. Run `/shop-total 3 4`. | Stop both scripts. |
| `dialog-summary` | Receive a supported dialog. Run `/dialog-summary`. | `/scripts stop dialog-summary` |

Test a greeting with different case and surrounding whitespace.
Test an unrelated message and a repeated matching message within the configured gap.
Reload the greeting script to check the saved count.
Test invalid numeric input before movement or provider calls.
Stop the provider and check the caller's unavailable response.
Do not claim live success from offline registration alone.

The greeting example uses whole-second timestamps. Its conservative guard enforces the minimum gap and can add up to one second.

## Additional complete recipes

Read the [cookbook](../../references/cookbook.md) for configuration, commands, expected output, and host checks.
Each additional recipe is a complete standalone `.bcn` file.
Automatic offhand and dialog actions start disabled.

| File | Purpose | Prerequisites |
| --- | --- | --- |
| [inventory-inspector.bcn](inventory-inspector.bcn) | Inspect selectors, slots, armor, containers, and recipes. | `inventory.read`, inventory tracking. |
| [offhand-guard.bcn](offhand-guard.bcn) | Check a totem slot before requesting an offhand move. | Inventory read/write, supported actions, explicit opt-in for health reactions. |
| [merchant-helper.bcn](merchant-helper.bcn) | Open a nearby villager, read offers, and purchase explicit units. | Entity and inventory read/write, tracked reachable villager, merchant window. |
| [enchanting-helper.bcn](enchanting-helper.bcn) | Open a table, check synced costs, and choose explicitly. | World write, inventory read/write, terrain, physics, table resources. |
| [regex-json-ledger.bcn](regex-json-ledger.bcn) | Parse typed regex captures and check JSON round trips. | No capability for pure calculations or local output. |
| [file-snapshot.bcn](file-snapshot.bcn) | Write and read an explicit persistent JSON snapshot. | `fs.read`, `fs.write`, configured restricted data directory. |
| [https-status.bcn](https-status.bcn) | Check pure response data and fetch a configured HTTPS status. | `net.fetch`, HTTPS endpoint, configured host allowlist. |
| [session-observer.bcn](session-observer.bcn) | Inspect lifecycle, health, container, and player events. | Inventory/entity reads and tracking. |
| [dialog-input.bcn](dialog-input.bcn) | Submit an opted-in stable dialog key without printing its value. | Dialog read/write, supported active dialog, configured key and button. |

Pure checks:

```sh
./Mcc.Cli run /full/path/scripts/regex-json-ledger.bcn --seed 42
./Mcc.Cli run /full/path/scripts/https-status.bcn --seed 42
```

Expected output is `Regex and JSON checks passed` and `Status response checks passed`, respectively.
The status helper does not fetch an endpoint during loading.
Stop any added recipe through `/scripts stop <id>`.

All nine additions passed strict lint, offline loading, and formatting checks.
The file snapshot write and read commands passed in a disconnected MCC runtime. A restarted process read the unchanged retained file.
Live game effects and HTTPS transactions remain unexecuted.
