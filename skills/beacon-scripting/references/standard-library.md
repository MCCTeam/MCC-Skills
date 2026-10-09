# Beacon standard library

This reference targets library version `2`.
Call functions with parentheses.
Square brackets in signatures indicate optional arguments. Do not type those signature brackets around an argument.

## Text and conversion

| Function | Behavior |
| --- | --- |
| `text(value)` | Return display text. |
| `number(value)` | Convert numbers, numeric text, or yes/no values. Unconvertible values return `none`. |
| `yesno(value)` | Return `no` for `no` or `none`. Other values return `yes`. |
| `len(value)` | Count text characters, list values, or map entries. |
| `lower(text)`, `upper(text)` | Change case with invariant rules. |
| `trim(text)` | Remove whitespace from both ends. |
| `trim_start(text)`, `trim_end(text)` | Remove whitespace from the selected end. |
| `split(text, separator)` | Return a list of text parts. |
| `join(list, separator)` | Join display values as text. |
| `slice(text_or_list, start[, end])` | Return the selected range. The end is exclusive. Positions start at zero. |
| `replace(text, old, new)` | Replace every exact occurrence. The old text cannot be empty. |
| `replace_first(text, old, new)` | Replace the first exact occurrence. |
| `index_of(text, needle[, start])` | Return a zero-based position or `none`. |
| `pad_start(text, width[, pad])` | Pad the start to the requested width. Default pad is a space. |
| `pad_end(text, width[, pad])` | Pad the end to the requested width. Default pad is a space. |
| `repeat_str(text, count)` | Repeat text a non-negative whole number of times. |
| `escape_regex(text)` | Escape characters for literal use inside a regular expression. |
| `json_parse(text)` | Decode JSON data into the six Beacon value kinds. |
| `json_stringify(value)` | Encode Beacon data as JSON text. Nesting caps at 32 levels. |

Check `number(...)` with `is set` before calculating.
Use `try` when JSON parsing can fail.
Check decoded field kinds before using external data.
JSON encodes data. It does not execute Beacon source.
Padding and repetition cap generated text at 10,000 characters.

## Collections and matching

| Function | Behavior |
| --- | --- |
| `sort(list)` | Return a sorted copy. Items must all be numbers or all be text. |
| `reverse(text_or_list)` | Return a reversed copy. |
| `unique(list)` | Remove repeated values and preserve first-seen order. |
| `keys(map)` | Return text keys in ordinal order. |
| `values(map)` | Return values in their keys' ordinal order. |
| `has_key(map, key)` | Return yes/no for a text key. |
| `match(text, pattern)` | Return the first match map or `none`. |
| `match_all(text, pattern)` | Return a list of match maps. |

A pattern can use `/[0-9]+/` or text containing the regular expression.
Match maps use key `"0"` for the whole match.
Capture groups use keys `"1"`, `"2"`, and their declared names.
Use brackets for numeric text keys: `found["1"]`.
Patterns can fail compilation or exceed their matching timeout.

```beacon
# beacon 1
set found to match("Price 12", /(?<amount>[0-9]+)/)
if found is set then
  assert(number(found.amount) is 12, "Captured price")
end if
```

## Numbers, randomness, and tests

| Function | Behavior |
| --- | --- |
| `min(values...)`, `max(values...)` | Return the smallest or largest number. A numeric list is also accepted. |
| `clamp(value, low, high)` | Bound a number between the limits. |
| `round(value[, digits])` | Round with half values away from zero. |
| `abs(value)` | Return the non-negative magnitude. |
| `log(value[, base])` | Return the natural logarithm or the requested logarithm. |
| `random(max)` | Return an integer from zero through `max - 1`. Require a positive whole maximum. |
| `pick(list)` | Return a random value or `none` for an empty list. |
| `chance(probability)` | Return yes/no with probability from zero through one. |
| `assert(condition[, label])` | Return `yes` or raise an error for `no`. |

Use positive input for logarithms.
An explicit logarithm base must be positive and different from one.
Use `--seed 42` for repeatable offline randomness.
Do not predict a live random result from an offline seed.

## State, commands, and tasks

| Function or value | Behavior |
| --- | --- |
| `saved(key)` | Read a saved value or `none`. |
| `save key to value` | Store one value. This is a statement. |
| `settings.name` | Read a declared setting with its user override. |
| `shared["feature.key"]` | Read shared RAM state across scripts in the same runtime. |
| `arg(name)` | Read a script command's text argument or `none`. |
| `tasks()` | Return task records with `id`, `name`, `status`, and `result`. |
| `chat_bucket()` | Return `burst`, `window_seconds`, `available`, and `muted`. |
| `vars.beacon.name` | Read MCC's string variable `%beacon_name%`. This bridge requires the MCC host. |

`tasks()` can include settled tasks. Filter its records before cancellation.
`result` is available for a completed task with a return value.
The offline host does not supply MCC's command variable store.
Read the state reference before choosing a storage lifetime.

## Time

| Value or function | Behavior |
| --- | --- |
| `time.hour`, `time.minute` | Numeric clock fields. |
| `time.stamp` | Whole Unix seconds. The clock discards fractional seconds. |
| `time.now` | Time as `HH:mm` text. |
| `time.date` | Date as `yyyy-MM-dd` text. |
| `time.today` | Day name. |
| `time.format(stamp, format)` | Format a timestamp. |
| `time.ago(stamp)` | Describe elapsed time. |

Timestamp subtraction has one-second granularity.
For a minimum five-second delay, allow another request only when the whole-second difference exceeds five.
This conservative guard can add up to one second. Use scheduled waits when precise relative delays are necessary.

The offline clock uses a repeatable value.
`--tick` advances that clock once after loading.
It does not repeatedly simulate every intermediate timer tick.

## Chat and server observations

| Function | Behavior |
| --- | --- |
| `online_players([count])` | Return observed names. Default page is 50. Maximum is 100. |
| `chat_history([count])` | Return recent observed chat text. Maximum is 200 entries. |
| `last_from(player)` | Return the last observed text from that player or `none`. |
| `count_matching(text, minutes)` | Count recent observed chat containing text without case sensitivity. |
| `server.scoreboard()` | Return the observed scoreboard snapshot. |
| `server.bossbars()` | Return observed bossbar rows. |
| `server.score(objective[, holder])` | Return one score when you supply a holder. Otherwise return the objective's scores map. Missing data returns `none`. |

The bare `online_players` value also returns an observed list.
These observations describe received data. They do not query complete server history.

## Game API index

The [events and game reference](events-and-game.md) defines arguments, results, and prerequisites.

| Area | Functions |
| --- | --- |
| World reads | `world.block_at`, `world.light_at`, `world.biome_at`, `world.sign_text` |
| World search | `world.find_blocks`, `world.find_signs` |
| World actions | `world.dig`, `world.place`, `world.use`, `world.looking_at` |
| Inventory reads | `inv.list`, `inv.count`, `inv.has`, `inv.find`, `inv.find_all`, `inv.selected`, `inv.armor`, `inv.container` |
| Inventory actions | `inv.select`, `inv.drop`, `inv.drop_stack`, `inv.move`, `inv.click`, `inv.take`, `inv.put` |
| Recipes and item use | `craft_list`, `craft_one`, `eat`, `use_in_hand` |
| Entities | `entities.near`, `entities.of_type`, `entities.by_id`, `entities.nearest`, `entities.count`, `attack`, `interact` |
| Movement | `move_goto`, `move_follow`, `stop_moving`, `look_at` |
| Trading | `trade.list`, `trade.select`, `trade.buy` |
| Enchanting | `enchant.options`, `enchant.choose` |
| Dialogs | `dialog.show`, `dialog.set`, `dialog.click`, `dialog.answer`, `dialog.close` |

## Files and network

| Function | Capability | Behavior |
| --- | --- | --- |
| `file_read(path)` | `fs.read` | Read text inside the restricted `scripts/data` directory. |
| `file_write(path, text)` | `fs.write` | Write text inside that directory and return `yes`. |
| `http_get(url)` | `net.fetch` | Fetch response text from an allowed HTTPS host. |
| `http_post(url, body)` | `net.fetch` | Send plain text and return response text. |

Normal MCC configuration supplies the restricted directory and network allowlist.
The offline runner supplies neither.
Read the state reference before using these functions.

## Read-only namespaces

| Namespace | Fields |
| --- | --- |
| `me` | `name`, `uuid`, `health`, `max_health`, `food`, `saturation`, `air`, `xp_level`, `armor`, `gamemode`, `yaw`, `pitch`, `ping`, `is_sneaking`, `pos`, `effects` |
| `me.pos` | `x`, `y`, `z` |
| `me.effects` rows | `name`, `level`, `seconds_left` |
| `server` | `online_count`, `tps`, `mspt`, `protocol`, `ip`, `port`, `version_name`, `max_players`, `motd`, `day_time`, `day`, `weather`, `difficulty`, `scoreboard`, `bossbars` |
| `game` | `protocol`, `protocols` |
| `time` | `hour`, `minute`, `stamp`, `now`, `date`, `today` |
| `beacon` | `lib` |
| `items`, `effects`, `enchants` | Named game identifiers for the observed protocol. |
| `settings` | Scalar defaults declared by this script with user overrides. |

Optional fields can be `none` before their first observation.
`me.uuid` currently remains `none`.
The identifier tables use fallback data offline.
Do not assume an offline identifier exists on the connected protocol.

Scoreboard maps contain `objectives` and `teams`.
Each objective contains `display` and a `scores` map.
Each team contains `display` and `members`.
Bossbar rows contain `title`, `progress`, and `color`.
