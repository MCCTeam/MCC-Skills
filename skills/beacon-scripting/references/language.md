# Beacon language reference

This reference describes source version `1`. The current standard library is version `2`.

## Header and comments

Use a UTF-8 `.bcn` file. Make `# beacon 1` the first line.
A blank line or ordinary comment before the version header fails validation.
The major version contains digits only. `# beacon 1.0` is invalid.

```beacon
# beacon 1
# needs: chat.send world.read
# wants: shop.calculate
# setting prefix = "Hello" ; Greeting text
# setting interval = 30 ; Report interval in seconds
# setting enabled = yes ; Enable reports
# desc: Report an observed count.
# example: /count-report
```

Use `;` before an optional setting description.
Capability names use spaces between names. Do not separate them with commas.
Place `# needs:`, `# wants:`, and settings before the first code statement.
Later declarations become ordinary comments and produce a warning.
Settings support text, numbers, and yes/no values. Settings do not support lists or maps.

Ordinary comments use `#` or `//`. Block comments use `/* ... */`.
Prefer `#` for portable explanations and header declarations.
Use lowercase keywords and documented names consistently.

## Values

| Kind | Source | Meaning |
| --- | --- | --- |
| Text | `"Alice"` | A string of characters. |
| Number | `12`, `12.5`, `-3` | A numeric value. |
| Yes/no | `yes`, `no` | A boolean value used by conditions. |
| List | `[3, 5, 7]` | An ordered collection. Positions start at zero. |
| Map | `{bread: 3, "item name": "bread"}` | A collection addressed by keys. |
| None | `none` | An absent value. |

Text supports interpolation: `"Total: {price * count}"`.
Literal braces use `{{` and `}}`.
Quoted text supports escapes such as `\"`, `\\`, and `\n`.
Triple-quoted text supports multiline strings.

Read a map with `prices.bread` or `prices["bread"]`.
Use bracket access for keys with spaces or punctuation.
Read a list with `names[0]`.
Check bounds before reading a list position that might be absent.
Check optional fields before reading deeper fields.

## Assignment and scope

```beacon
set total to 3
set prices.bread to 4
set names[0] to "Alice"
```

`=` does not assign a runtime variable.
`set total = 3` and `total = 3` are invalid.
Each script owns its globals.
Function parameters and local assignments belong to that function call.
Event aliases belong to their handler.
Bare event fields take precedence over globals inside an event handler.

Avoid variable names that hide built-in namespaces, such as `server`, `world`, `inv`, or `time`.
Do not assign to read-only snapshot maps.
Use action functions when changing game state.

## Operators

| Operation | Syntax | Result |
| --- | --- | --- |
| Arithmetic | `+`, `-`, `*`, `/`, `%` | Number. Addition also accepts two text values. |
| Unary number | `-value` | Number. |
| Equality | `is`, `is not`, `==`, `!=` | Yes/no. Equality compares nested values. |
| Numeric comparison | `<`, `<=`, `>`, `>=` | Yes/no. Both operands need numbers. |
| Logic | `not`, `and`, `or` | Logical result or fallback value. |
| Presence | `is set`, `is not set` | Yes/no. Only `none` is absent. |
| Emptiness | `is empty`, `is not empty` | Yes/no for supported empty values. |
| Membership | `contains` | Text substring or list membership. |
| Text boundary | `starts with`, `ends with` | Yes/no. Both operands need text. |
| Pattern | `matches /pattern/` | Yes/no. A regular expression describes a text pattern. |

`or` supplies the right value only when the left value is `no` or `none`.
Zero, empty text, and empty collections do not select the fallback.
`saved("count") or 0` is a common default expression.

Conditions require yes/no values. `if me.food then` is invalid.
Use `if me.food < 6 then` after checking presence.
Convert external text with `number(...)` before numeric comparisons.
Text plus a number fails. Use interpolation or `text(number)` instead.
Division by zero raises an error.

Precedence, from low to high, is `or`, `and`, `not`, comparison, addition, multiplication, unary number, and access/calls.
Use parentheses when several operators make the meaning unclear.

## Branches and loops

```beacon
if count < 0 then
  show "Negative count"
else if count is 0 then
  show "Empty count"
else
  show "Positive count"
end if

while count < 5
  set count to count + 1
end while

repeat 3 times
  show "One iteration"
end repeat

for each item in ["bread", "apple"]
  show item
end for
```

`repeat` counts iterations. Do not use a time unit after its count.
`for each` visits list values.
Use `keys(map)` or `values(map)` when iterating map data.
`stop` exits the current loop. `skip` continues its next iteration.
The aliases `break` and `continue` also parse.
Prefer `stop` and `skip` for consistent source.
Limit all loops because each iteration spends execution fuel.

## Functions

```beacon
function subtotal(price, count)
  return price * count
end function
set result to subtotal(3, 4)
```

Call functions with parentheses. Match their declared parameter count.
`return value` ends a function call. A bare `return` produces `none`.
Functions can return any Beacon value kind.
Limit recursion to protect the call-depth budget.
Keep calculation helpers separate from game actions for simpler offline tests.

## Events, timers, and commands

Place event, timer, function, command, and export declarations at the top level.
Do not create an event or timer block inside another block.
Place imports and extern declarations before executable declarations.

| Block | Opening | Ending |
| --- | --- | --- |
| Event | `on chat as e when e.message is "!help"` | `end on` |
| Named cooldown | `on tps cooldown 300 seconds named "warn" when tps is set` | `end on` |
| Recurring timer | `every 60 seconds` | `end every` |
| One-shot timer | `in 5 seconds do` | `end in` |
| Script command | `command "/price <item>"` | `end command` |
| Shared lock | `lock shared` | `end lock` |

The event clause order is event name, optional alias, optional cooldown, then optional `when` filter.
A one-shot opening requires `do`.
Use matching endings even when another accepted shorthand appears to work.
Use `arg("item")` inside a command to read its text argument.

`stop event` ends the handler immediately.
Some chat hooks also support local presentation suppression.
Read the event reference before relying on suppression.

## Tasks and time units

| Statement | Meaning |
| --- | --- |
| `start worker()` | Start separate scheduled work. |
| `wait 200 milliseconds` | Yield the current task. |
| `await task_id` | Wait for one task to finish. |
| `cancel task task_id` | Request cancellation of one task. |

`start` is a statement. It does not directly assign a task ID.
Read `tasks()` to identify the created task.
Task records contain `id`, `name`, `status`, and `result`.
The list can include completed or cancelled records.
Select by ID or status instead of assuming every row runs now.

| Construct | Accepted units |
| --- | --- |
| `wait` | Millisecond, second, minute. |
| `every`, `in`, `cooldown` | Second, minute, hour. |

Singular and plural forms parse. `s`, `sec`, and `min` are aliases.
Prefer full unit names.
The minimum wait is 100 milliseconds.
The minimum recurring interval is one second.

## Errors

```beacon
try
  assert(no, "Example failure")
catch err
  show "Code {err.code}, line {err.line}: {err.message}"
finally
  show "Attempt finished"
end try
```

`try` requires `catch` and an error variable.
`finally` is optional and runs after either outcome.
Caught errors provide `message`, `code`, and `line`.
Catch an expected operational failure near the action that can fail.
Execution budget failures need bounded code, not an endless catch-and-retry loop.

## Common invalid forms

| Invalid form | Use |
| --- | --- |
| `# beacon 2` | `# beacon 1` and the correct library target. |
| `set count = 1` | `set count to 1` |
| `if count then` | `if count > 0 then` |
| `while true` | A bounded yes/no condition. |
| `repeat 5 seconds` | `repeat 5 times` or a timer block. |
| `in 5 seconds` | `in 5 seconds do` |
| `call "shop.total"` | `call "shop.total"(arguments)` |
| `say "/home"` | `server "/home"` |
| Mismatched `end` | The opening block's matching label. |
