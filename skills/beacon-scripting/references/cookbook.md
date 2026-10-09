# Beacon cookbook

These complete `.bcn` examples use source version `1` and library version `2`.
They need no source checkout or unshipped helper file.
The surrounding skill uses the MIT license.
Read the matching recipe before enabling an action.

## Install and check

1. Copy a recipe into the selected data directory's `scripts` folder.
2. Preserve its filename when its script ID must remain stable.
3. Check the copied file with installed MCC.
4. Load the file through `/scripts run <id>`.
5. Stop the file through `/scripts stop <id>` after its work.

```sh
./Mcc.Cli lint /full/path/scripts/inventory-inspector.bcn --target-lib 2 --strict
./Mcc.Cli run /full/path/scripts/regex-json-ledger.bcn --seed 42
./Mcc.Cli format /full/path/scripts/inventory-inspector.bcn --check
```

Windows PowerShell uses `.\Mcc.Cli.exe`.
A framework-dependent distribution uses `dotnet /full/path/Mcc.Cli.dll`.
Enter `/scripts` and recipe commands inside MCC.
Do not enter them as operating-system commands.

## Inventory inspection

Source: [inventory-inspector.bcn](../assets/examples/inventory-inspector.bcn).

The recipe inspects slot rows, selectors, armor, containers, and recipe observations.
It requests no inventory changes.
`inv.find_all` returns slot IDs. `inv.list` returns slot maps.

1. Enable `[Gameplay] Inventory` in `client.toml`.
2. Reconnect after changing that feature.
3. Load `inventory-inspector`.
4. Run `/inventory-snapshot`.
5. Compare the reported items with the next inventory observation.

Optional selector setting:

```text
/scripts config inventory-inspector item "torch"
/scripts reload inventory-inspector
```

An empty offline inventory does not prove that a connected player carries no items.

## Guarded offhand movement

Source: [offhand-guard.bcn](../assets/examples/offhand-guard.bcn).

The recipe checks for a totem slot before requesting an offhand move.
Its automatic health reaction starts disabled.
It avoids starting another automatic worker while its named worker runs.
An accepted move request does not prove the next server inventory state.

1. Enable inventory tracking and supported inventory actions.
2. Load `offhand-guard` on a controlled server.
3. Run `/equip-totem` to check the explicit action.
4. Check the next inventory observation.
5. Enable automatic reactions only after that check.

```text
/scripts config offhand-guard enabled yes
/scripts config offhand-guard threshold 6
/scripts reload offhand-guard
```

The `health` event starts the worker when observed health reaches the threshold.
Stopping the script cancels its pending scheduled work.
Test missing totems and session loss separately.

## Merchant offers and purchases

Source: [merchant-helper.bcn](../assets/examples/merchant-helper.bcn).

The recipe uses explicit local commands for interaction and purchase.
It checks distance before interacting with a tracked villager.
It checks offer availability, sold-out state, and whole unit counts.
The default purchase limit is four units. The runtime maximum remains 64.

1. Enable entity and inventory tracking.
2. Stand within reach of a tracked villager.
3. Load `merchant-helper`.
4. Run `/merchant-open`.
5. Wait for a container observation.
6. Run `/trade-offers`.
7. Read the current costs and result before selecting an offer.
8. Keep the cursor empty before purchasing.
9. Run `/trade-purchase 0 1` only for the intended offer.
10. Check the completed count and next inventory observation.

Trade purchases need enough input items and empty destination slots.
Do not combine raw result-slot clicks with this purchase command.
Closing the window can produce a catchable failure.
The recipe reports completed units instead of assuming the requested count succeeded.

## Enchanting choices

Source: [enchanting-helper.bcn](../assets/examples/enchanting-helper.bcn).

The recipe opens a block, reports synced choice costs, and requests one explicit choice.
It guards unavailable costs and the player's experience level.
It leaves item and lapis placement to the operator's inventory controls.
It does not assume a particular container slot layout.

1. Enable terrain, physics, and inventory tracking.
2. Stand within reach of an enchanting table.
3. Load `enchanting-helper`.
4. Run `/enchant-open <x> <y> <z>` for that table.
5. Check the observed open window.
6. Place the intended item and lapis with MCC's inventory controls.
7. Run `/enchant-costs` after the server supplies costs.
8. Run `/enchant-choice top`, `middle`, or `bottom` for the intended choice.
9. Check the next item observation.

An unsynced `level` is `none`.
Do not compare that value with the player's numeric level.
The host can refuse a choice despite a sufficient observed experience level.
Item, lapis, window state, and server rules still matter.

## Regex and JSON data

Source: [regex-json-ledger.bcn](../assets/examples/regex-json-ledger.bcn).

A regular expression describes a text pattern.
This recipe uses named capture groups for count, item, and price.
It converts captures into numeric data before encoding JSON.
It rejects unrelated lines and malformed prices.

```sh
./Mcc.Cli run /full/path/scripts/regex-json-ledger.bcn --seed 42
```

Expected output: `Regex and JSON checks passed`.
The pure assertions check valid input, rejected input, multiple matches, and a JSON round trip.

Inside MCC:

```text
/scripts run regex-json-ledger
/parse-deal "bought 2x bread for $12.50"
```

The recipe also observes matching `server_message` lines.
It prints parsed data locally and requests no game action.
A live server-message test remains separate from its pure checks.

## Persistent file snapshots

Source: [file-snapshot.bcn](../assets/examples/file-snapshot.bcn).

The recipe explicitly writes and reads one small JSON file.
Its default relative path is `example/snapshot.json` inside the host's `scripts/data` directory.
It creates the file on an explicit write command.
A failed read never resets or overwrites an existing file.

1. Load `file-snapshot` in normal MCC.
2. Set a non-secret note if needed.
3. Run `/snapshot-write`.
4. Run `/snapshot-read`.
5. Restart MCC with the same data directory.
6. Load the same script ID.
7. Run `/snapshot-read` again.

```text
/scripts config file-snapshot note "Storage check complete"
/scripts reload file-snapshot
```

Absolute paths, parent traversal, and symbolic-link escapes remain refused.
Each file caps at 1 MiB.
The shared file area differs from per-script saved state.
The offline runner supplies no persistent file directory.
Offline loading therefore does not check these write or read commands.

## Configured HTTPS status

Source: [https-status.bcn](../assets/examples/https-status.bcn).

The recipe starts with an empty endpoint.
No request occurs merely because the script loads.
Its pure helper checks a decoded response with `ok` and `players` fields.
Accepted player counts are whole numbers from zero through one million.

Expected JSON shape:

```json
{"ok": true, "players": 12}
```

1. Choose an HTTPS endpoint with that response shape.
2. Add its bare host to `configurations/beacon.toml`.
3. Set the recipe's full endpoint URL.
4. Reload the recipe.
5. Run `/web-status`.
6. Check the response against the actual endpoint.

Illustrative configuration:

```toml
[Net]
AllowedHosts = ["api.example.org"]
```

```text
/scripts config https-status endpoint "https://api.example.org/status"
/scripts reload https-status
```

Replace the illustrative host and URL with the endpoint you control.
Allowlist entries contain host names, not URLs.
HTTPS requests have a five-second timeout and a 1 MiB response limit.

```sh
./Mcc.Cli run /full/path/scripts/https-status.bcn --seed 42
```

Expected output: `Status response checks passed`.
That output checks the helper's supplied data, not an HTTP transaction.

## Session and container events

Source: [session-observer.bcn](../assets/examples/session-observer.bcn).

The recipe reports lifecycle, health, player-list, container, and player-entity events locally.
It requests no game mutations.

1. Enable inventory and entity tracking.
2. Load `session-observer`.
3. Check its local loaded message.
4. Produce a container-open and container-close event.
5. Produce a controlled disconnect and reconnect.
6. Compare the event sequence with the session behavior.

Tab-list events and entity events describe different observations.
Entity IDs from an earlier session are stale after reconnect.
The first entity poll establishes a baseline without additions for every existing entity.
Offline loading checks only the `start` handler here.

## Dialog input

Source: [dialog-input.bcn](../assets/examples/dialog-input.bcn).

The recipe starts disabled and matches a stable configured input key.
It checks the active dialog again before submission.
It checks a one-based button number against the current button list.
It uses `dialog.answer` to submit fields and click in one call.
It never prints the submitted value.

1. Receive a supported dialog on a controlled server.
2. Inspect its real input keys with the read-only dialog summary recipe.
3. Set the input key, non-secret value, and intended button.
4. Enable submission.
5. Reload the recipe.
6. Receive a fresh matching dialog or run `/dialog-submit`.
7. Check the server's next response.

```text
/scripts config dialog-input key "team_choice"
/scripts config dialog-input value "blue"
/scripts config dialog-input button 1
/scripts config dialog-input enabled yes
/scripts reload dialog-input
```

Do not infer successful team selection from a locally accepted request.
An unrelated dialog remains untouched.
Stop the script when automatic submission is no longer wanted.

## Recorded checks

All nine added files passed strict lint for library version `2`.
All nine passed offline loading with seed `42`.
Their formatting checks passed.
Regex/JSON and status-helper assertions produced their expected output.

Live inventory, trading, enchanting, lifecycle, and dialog checks remain unexecuted.
Persistent file commands remain unexecuted in a configured host.
HTTPS transactions remain unexecuted. The task supplies no endpoint.
Successful offline loading does not prove any of those effects.

The file snapshot write/read commands passed in a disconnected MCC runtime. Restart read the retained file without changing it.
No live game effects or HTTPS transactions ran during that check.
