# Events and game APIs

An event is a notification from MCC's host.
Its fields describe that notification.
Later game reads can describe a newer observation.

## Event grammar

```beacon
# beacon 1
# needs: chat.send
on chat as e when trim(lower(e.message)) is "!help"
  whisper e.player "Commands: !help and !rules."
end on
```

The default alias is `event` when `as e` is absent.
Fields also work as bare names inside their handler.
Use an explicit alias to distinguish event fields from globals.
Use exact filters when accepting command words.
`contains "!help"` also accepts longer messages.

The clause order is `on EVENT [as ALIAS] [cooldown COUNT UNIT named "NAME"] [when CONDITION]`.
Named cooldowns belong to one script and name.
Handlers sharing a cooldown name share its window.
The dispatcher acquires the cooldown before evaluating `when`.
An unrelated notification can consume that window.

## Built-in events and fields

Missing optional fields appear as `none`.
Check their presence before calculations or nested access.

| Event | Fields |
| --- | --- |
| `chat` | `player`, `message`, `raw`, `is_private` |
| `whisper` | `player`, `message`, `raw` |
| `server_message` | `text`, `translation_key` |
| `raw_chat` | `raw`, `category`, `sender`, `sender_id`, `chat_type`, `target`, `body`, `translation_key`, `verified` |
| `join`, `leave` | `player` |
| `death` | `player`, `cause` |
| `respawn` | `player` |
| `health` | `health`, `max_health`, `change` |
| `hunger` | `food`, `saturation`, `change` |
| `inventory` | `slots_changed`, a list of numeric slot IDs |
| `start`, `login`, `logout`, `reconnect` | No built-in payload fields. |
| `disconnect`, `kick` | `reason` |
| `tps` | `tps`, `mspt` |
| `player_list` | `players`, `count`, `header`, `footer` |
| `container_open` | `window`, `title`, `kind` |
| `container_close` | `window` |
| `entity_add`, `entity_remove` | `id`, `uuid`, `type`, `name`, `custom_name`, `is_player`, `x`, `y`, `z`, `distance`, `yaw`, `pitch`, `pose`, `on_ground` |
| `dialog` | `title`, `body`, `inputs`, `buttons`, `input_keys`, `registry_id` |

`join` and `leave` follow the server tab list.
They do not describe every entity entering or leaving render distance.
The first entity poll establishes a baseline.
It does not emit additions for every existing tracked entity.
An entity removal contains its last known row.
That row does not make the entity available for actions.

`start` follows successful script loading.
`login` means the session reached play and can repeat after reconnect.
`reconnect` accompanies a new session after a drop.
Use session events for work that needs a live connection.

Plugins can publish named events.
Use only the provider's documented fields and capability.
An unknown offline event warning can reflect an absent plugin.

## Local suppression

`stop event` ends the current handler.
For `chat`, `whisper`, and `server_message`, it can suppress MCC's local presentation.
It does not cancel a message already delivered to the server.
`raw_chat` remains observable and cannot be suppressed.
Other hooks do not cancel the underlying game action.

## Output and command paths

| Statement | Capability | Effect |
| --- | --- | --- |
| `show value` | None | Write local output. |
| `log value` | None | Alias for local output. Prefer `show`. |
| `say "text"` | `chat.send` | Request public chat without a leading slash. |
| `whisper "Alice" "text"` | `chat.send` | Request a private message. |
| `server "/home"` | `server.send` | Send a server command with its leading slash. |
| `mcc "help"` | `mcc.run` | Invoke MCC's internal dispatcher. |
| `set result to mcc "help"` | `mcc.run` | Capture internal command output as text. |
| `disconnect "Finished"` | `server.disconnect` | Leave the server and stop automatic reconnect. |

Use `show` for multiline internal command output.
All scripts share eight chat messages per ten seconds.
Excess requests queue and produce warnings.
Inspect `chat_bucket()` when diagnosing output delays.

## Gameplay configuration

Edit the existing table in `configurations/client.toml`:

```toml
[Gameplay]
Terrain = true
Inventory = true
Entity = true
Physics = true
Pathfinding = true
```

Enable only the features the task requires.
Physics depends on terrain. Pathfinding depends on physics.
Reconnect or restart after changing composed session features.
Reloading a script does not add missing session modules.
Capabilities do not enable these features.

## World reads and actions

| Function | Capability | Result |
| --- | --- | --- |
| `world.block_at(x, y, z)` | `world.read` | Map containing `name` and `id`. An unknown loaded block raises an error. |
| `world.light_at(x, y, z)` | `world.read` | Light number or `none`. |
| `world.biome_at(x, y, z)` | `world.read` | Biome text or `none`. |
| `world.sign_text(x, y, z)` | `world.read` | Sign text or `none`. |
| `world.find_blocks(type, radius, maximum)` | `world.search` | Position rows containing `x`, `y`, `z`. |
| `world.find_signs(text, radius, maximum)` | `world.search` | Rows containing `x`, `y`, `z`, `text`. |
| `world.dig(x, y, z[, face])` | `world.write` | Map containing `broken` and `detail`. |
| `world.place(x, y, z[, face])` | `world.write` | Whether the host sent the placement request. |
| `world.use(x, y, z)` | `world.write` | Requested container observation or `none`. |
| `world.looking_at([range])` | `world.write` | Hit row containing `x`, `y`, `z`, `name`, `distance`, or `none`. |

Coordinates for block operations need whole finite numbers.
The horizontal bounds are ±30,000,000. The vertical envelope is -64 through 320.
Version-specific world data can have narrower usable limits.
Face names are `up`, `down`, `north`, `south`, `east`, and `west`.
The default dig/place face is `up`.

World writes and targeting reads require `Terrain` and `Physics`.
Dig, place, and use share eight mutations per ten seconds per script.
Refusals report a retry delay.
Search radius caps at 32 blocks. Results cap at 64.
Searches use tracked terrain, not the whole server.
An empty result can mean missing tracked data.

## Inventory and containers

| Function | Capability | Result or effect |
| --- | --- | --- |
| `inv.list()` | `inventory.read` | Observed slot rows. |
| `inv.count(selector)` | `inventory.read` | Matching item count. |
| `inv.has(selector[, count])` | `inventory.read` | Whether enough matching items exist. |
| `inv.find(selector)` | `inventory.read` | Matching slot number or `none`. |
| `inv.find_all(selector)` | `inventory.read` | Matching slot numbers. |
| `inv.selected()` | `inventory.read` | Selected hotbar slot. |
| `inv.armor()` | `inventory.read` | Armor slot observations. |
| `inv.container()` | `inventory.read` | Current container map or `none`. |
| `inv.select(slot)` | `inventory.write` | Select hotbar slot zero through eight. |
| `inv.drop()`, `inv.drop_stack()` | `inventory.write` | Drop the selected item or stack. |
| `inv.move(from, to)` | `inventory.write` | Move between slot numbers or a supported named target such as `"offhand"`. |
| `inv.click(slot[, mode])` | `inventory.write` | Request a container click. Default mode is `"left"`. |
| `inv.take(slot[, count])` | `inventory.write` | Take items from an open container. |
| `inv.put(slot)` | `inventory.write` | Put an inventory slot into the open container. |
| `craft_list()` | `inventory.read` | Observed recipe identifiers. |
| `craft_one(recipe)` | `inventory.write` | Request one craft and return yes/no. |
| `eat()` | No inferred capability | Request the best available food. Runtime prerequisites still apply. |
| `use_in_hand()` | No inferred capability | Request held-item use. Runtime prerequisites still apply. |

Slot rows contain `slot`, `type`, `name`, `count`, and optional `lore`.
`inv.find` returns a slot number, not a slot map.
A container map contains `window`, `title`, `kind`, and `slots`.
Use the observed window's slot numbering for container actions.
Do not assume all inventory windows share one layout.

A selector can be item text or a criteria map.
Basic text matching ignores case and accepts an optional `minecraft:` prefix.
Basic matching treats spaces, hyphens, and underscores alike.
Map criteria include `type`, `name`, `name_contains`, `name_matches`, `lore_contains`, `lore_matches`, `min_count`, and `named`.
Use stable type identifiers when translated display names would be ambiguous.

Inventory actions require tracking and negotiated protocol support.
Open a container before reading its transaction data.
Wait for `container_open` before deciding that opening succeeded.
Read a later observation after an action that changes the next decision.

## Trading and enchanting

| Function | Capability | Behavior |
| --- | --- | --- |
| `trade.list()` | `inventory.read` | Read offers from the open merchant window. |
| `trade.select(index)` | `inventory.write` | Select an offer. |
| `trade.buy(index[, count])` | `inventory.write` | Buy units and return the completed count. Count must be one through 64. |
| `enchant.options()` | `inventory.read` | Read choices from the open enchanting window. |
| `enchant.choose(choice)` | `inventory.write` | Select a choice, such as `"top"`. |

Offer rows contain `index`, `first`, `second`, `result`, `uses`, `max_uses`, `sold_out`, and `xp`.
Offer item maps contain `type`, `name`, and `count`.
The second item can be `none`.
Enchanting rows contain `slot` and optional `level`.
Catch failures when the window closes or the merchant becomes unavailable.

## Entities and movement

| Function | Capability | Behavior |
| --- | --- | --- |
| `entities.near([radius[, maximum]])` | `entity.read` | Nearby tracked rows, nearest first. |
| `entities.of_type(type[, radius[, maximum]])` | `entity.read` | Nearby rows of one type. |
| `entities.by_id(id)` | `entity.read` | Current tracked row or `none`. |
| `entities.nearest([type[, radius]])` | `entity.read` | Nearest matching row or `none`. |
| `entities.count([type[, radius]])` | `entity.read` | Matching tracked count. |
| `attack(target)`, `interact(target)` | `entity.write` | Request an action by tracked ID, row, or supported name. |
| `move_goto(x, y, z[, options])` | `movement` | Move until arrival or failure. |
| `move_goto(position[, options])` | `movement` | Move to a map containing `x`, `y`, `z`. |
| `move_follow(target)` | `movement` | Follow a player name, tracked entity ID, or row until cancellation. |
| `stop_moving()` | No inferred capability | Cancel steering. |
| `look_at(x, y, z)` | No inferred capability | Request orientation toward coordinates. |
| `look_at(entity_row)` | No inferred capability | Request orientation toward the row's position. |

Entity rows use the same fields as `entity_add` and `entity_remove`.
The default radius is 64 blocks. The maximum radius is 128.
Results cap at 64 rows.
IDs last for one session. Obtain a new row after reconnect.
Catch failures when a target disappears.

Movement options include `tolerance`, `sneak`, and `sprint`.
The latest movement request replaces the earlier request.
The earlier request receives a superseded error.
Movement functions await arrival or cancellation.
`move_goto` returns an arrival map with `reached` and `detail`. It does not return a task ID.
Use `start` for a worker function, then select its running ID from `tasks()` when cancellation needs that ID.
Use `start` when a handler must continue separately.

## Server dialogs

| Function | Capability | Behavior |
| --- | --- | --- |
| `dialog.show()` | `dialog.read` | Read the active dialog or `none`. |
| `dialog.set(key, value)` | `dialog.write` | Set one input value. |
| `dialog.click(button)` | `dialog.write` | Click a one-based button number. |
| `dialog.answer(values[, button])` | `dialog.write` | Submit input values and click a button. |
| `dialog.close()` | `dialog.write` | Close the active dialog. |

Dialog input rows contain `key`, `label`, `kind`, and `value`.
Button rows contain `index` and `label`.
Match stable input keys instead of translated titles.
Keep private form values out of chat and local output.
Catch failures if the dialog disappears before submission.
