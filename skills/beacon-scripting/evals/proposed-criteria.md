# Proposed measurable criteria

These criteria describe later evaluation checks.
The initial `evals.json` intentionally contains no assertions.

## Greeting and saved state

1. The complete source starts with `# beacon 1`.
2. Lint reports no errors for the delivered file.
3. The header declares `chat.send` before code.
4. The handler accepts the exact normalized `!hello` word.
5. An unrelated message does not consume the matching request delay.
6. The same player cannot trigger another greeting within five seconds.
7. A different player can trigger a greeting during that window.
8. The prefix is a declared editable setting.
9. The count uses saved state and a stable script ID.
10. The statistics command reads that count locally.
11. The report separates offline checks from chat delivery and durable persistence.

## Provider and input conversion

1. Both complete files start with the correct version header.
2. The provider explicitly exports the called function.
3. The caller uses `call "shop-provider.subtotal"(price, count)`.
4. Invalid numeric conversion cannot reach arithmetic or the provider call.
5. A missing provider produces a useful local response.
6. Pure checks produce the expected total of twelve for three times four.
7. Installation includes every required file and the provider load order.
8. Procedures use installed MCC without source-checkout dependencies.

## Movement and read-only reports

1. Source declares `movement`, `world.search`, and `entity.read` for their used operations.
2. Coordinate conversion checks `none` before movement starts.
3. The movement task has an identified cancellation path.
4. Searches stay inside documented radius and result limits.
5. The report uses local output and read-only APIs.
6. Instructions identify terrain, physics, pathfinding, and entity tracking requirements.
7. The script handles superseded movement and session changes.
8. Offline lint or loading is not presented as proof of arrival.
9. The report states unavailable live-server validation explicitly.
