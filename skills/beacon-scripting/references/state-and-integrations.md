# State and integrations

Choose storage by the value's required lifetime.

## Storage choices

| Storage | Lifetime | Use |
| --- | --- | --- |
| Function local | One function call. | Temporary calculation. |
| Script global | One loaded script. | Current working state. |
| `settings` | Declared default plus user overlay. | User choices. |
| `saved` | Script ID and configuration root. | Progress that survives restart. |
| `shared` | One Beacon runtime in RAM. | Coordination between scripts. |
| `vars.beacon` | MCC's string variable store. | Integration with MCC commands. |

Reload resets globals, tasks, and registrations.
Saved values and setting overrides remain.
Stopping a script does not remove saved files.
Renaming a discovered file changes its script ID.
Keep the ID stable when progress must remain available.

## Settings

```beacon
# beacon 1
# setting prefix = "Hello" ; Greeting text
# setting interval = 30 ; Interval in seconds
# setting enabled = yes ; Enable reporting
show "{settings.prefix}, interval {settings.interval}"
```

Declare settings before code.
Use scalar defaults: text, number, or yes/no.
The optional description follows the `;` separator.
The host reads overrides from `configurations/beacon/<id>.settings.toml`.
Omitted keys retain declared defaults.
Incorrect value kinds produce diagnostics.

Inside MCC:

```text
/scripts config welcome
/scripts config welcome prefix "Welcome back"
/scripts config welcome enabled yes
/scripts reload welcome
```

Quote a text value containing spaces.
Use `yes` or `no` for a declared yes/no setting.
Use settings for choices, not counters the script updates.

## Saved state

```beacon
# beacon 1
set runs to saved("runs") or 0
set runs to runs + 1
save "runs" to runs
show "Run {runs}"
```

`saved(key)` returns `none` when the key is absent.
`save key to value` stores the value under a text key.
Normal MCC stores data in `configurations/beacon/<id>.toml`.
An offline run does not prove durable state across separate processes.
Test persistence through reload and restart in normal MCC.
Do not remove a state file during routine source replacement.

## Shared values

```beacon
# beacon 1
lock shared
  set count to shared["report.count"] or 0
  set shared["report.count"] to count + 1
end lock
show "Reports: {shared["report.count"]}"
```

Use namespaced keys because all scripts share this RAM map.
`lock shared` serializes an update that reads a value and writes its replacement.
Without the lock, concurrent tasks can overwrite each other's updates.
Keep the lock body short.
Avoid `wait`, HTTP, file access, and game actions inside the lock.
Shared values do not survive a new runtime.

## MCC variables

```beacon
# beacon 1
set vars.beacon.coins to 5
show vars.beacon.coins
```

This creates the MCC command variable `%beacon_coins%`.
Bridge reads return text.
Convert with `number(...)` before calculating.
Check whether that conversion returned `none`.
This bridge differs from saved and shared state.
The offline runner does not supply MCC's variable store.

## Imported libraries

Create `scripts/lib/math.bcn`:

```beacon
# beacon 1
function subtotal(price, count)
  return price * count
end function
```

Create `scripts/order.bcn`:

```beacon
# beacon 1
import "lib/math.bcn" as math
show math.subtotal(3, 4)
```

Imports resolve relative to the importing file.
Include imported files when distributing the script.
Place imports before executable blocks.
Libraries contribute functions and top-level constants.
Their event and command blocks do not register in the caller.
Circular imports fail validation.
Lint includes imported capability requirements.
The combined lint file closure caps at 32 files.

## Running script exports

Provider file `shop-provider.bcn`:

```beacon
# beacon 1
export function subtotal(price, count)
  return price * count
end function
export set prices to {bread: 3, apple: 5}
```

Caller expression:

```beacon
set total to call "shop-provider.subtotal"(3, 4)
set prices to call "shop-provider.prices"()
```

Load the provider before a caller executes a cross-script call.
The target must run and export the requested name.
Call arguments and return values use the six Beacon kinds.
Calls spend the caller's execution fuel.
Missing targets, missing exports, and wrong argument counts raise catchable errors.
Stopping or reloading the provider can temporarily remove exports.

Use imports for reusable calculations and constants.
Use running exports when several scripts need one provider's live state.

## Plugin functions

A plugin provider has an exact plugin ID and a documented capability.
Do not invent either name.
Declare an extern function before executable blocks:

```beacon
# beacon 1
# wants: shop.calculate
extern subtotal from "shop-tools"
try
  show subtotal(3, 4)
catch err
  show "Pricing unavailable: {err.message}"
end try
```

This example needs a provider that exports `subtotal` from `shop-tools`.
It is not a built-in pricing service.
Use `# needs:` when the task cannot function without the provider.
Use `# wants:` only when an absent provider has a useful fallback.
The optional declaration does not make an absent function succeed.
Offline lint can warn because it cannot resolve the installed provider.
Strict lint escalates those unresolved-provider warnings.
Preserve a valid declaration instead of removing it to silence warnings.

## Plugin variables and events

A plugin can publish a read-only variable namespace.
Every read obtains a snapshot.
Use the provider's documented namespace, fields, and capability.
Scripts cannot change the plugin's internal object graph.
Use a documented plugin function for an action.

A plugin can publish a named event.
Use `on EVENT_NAME as e` with the documented fields.
Offline lint may warn when the provider is absent.
Test provider reload and disappearance when the integration must recover.

Only text, number, yes/no, list, map, and none cross the script bridge.
C# services, session objects, and arbitrary CLR objects do not cross directly.
A capability declaration does not isolate arbitrary C# plugin code.

## Restricted files

File helpers use the shared `scripts/data` directory.
Pass a relative path, such as `reports/latest.json`.
Declare `fs.read` or `fs.write` as required.
Use a feature directory or filename prefix to prevent collisions.
The runtime rejects absolute paths, parent traversal, and symbolic-link escapes.
Each file caps at 1 MiB.
Missing reads raise catchable errors.
Saved state remains separate from this shared file area.
The offline runner does not configure this persistent directory.

## Network configuration

Declare `net.fetch`.
Add bare destination host names to `configurations/beacon.toml`:

```toml
[Net]
AllowedHosts = ["api.example.org"]
```

Use an HTTPS URL in the script:

```beacon
set body to http_get("https://api.example.org/status")
set payload to json_parse(body)
```

The allowlist contains host names, not URLs.
The runtime refuses plain HTTP.
The per-request timeout is five seconds.
Response bodies cap at 1 MiB.
`http_post` sends its body as plain text.
Do not assume a custom JSON content type or header API exists.
Check response structure before using its fields.
Use bounded delayed retries for temporary failures.
Do not store passwords or tokens in shared state or script output.
The offline runner does not supply a network allowlist.
