# Session Journal

Session Journal counts successful play sessions.
It saves the count after each session starts.
Reload and restart preserve the count.

## Command

Enter `/journal-count` at the MCC prompt.
The command displays the saved count locally.
It does not send server chat.
The command also works while disconnected.

## Setting

`Increment` controls the amount added for each session.
The default is one.
Values below one become one.
Values above 100 become 100.
Reload the plugin after editing its user settings.

## Beacon

The host must provide Commands and Beacon.
A script must declare `journal.read` before importing `journal_count` from `session-journal`.
The function returns the saved count as a number.

## Data and limits

The persistent key `sessions` lives in the assigned storage table.
The variable `session_journal_sessions` updates when a session starts.
The plugin does not perform game actions.
It writes one small storage record per session start.
The count uses a signed 32-bit integer.
An overflow raises a callback failure instead of wrapping the count.
