# Settings, durable data, and resources

## Typed settings

Declare the settings type in `Configure`:

```csharp
public sealed class JournalSettings : IValidatablePluginSettings
{
    public int Increment { get; set; } = 1;
    public void Validate() => Increment = Math.Clamp(Increment, 1, 100);
}

descriptor.WithSettings<JournalSettings>();
```

The type needs a public parameterless constructor.
`Load<T>()` reads package defaults, applies user values, and validates the result.
Package defaults can live in `defaults/settings.toml`.
User values take precedence.
Updates do not replace user settings with new package defaults.

Use settings for user choices.
Use storage for counters, results, and other changing state.
Do not serialize connection objects or services into settings.

`Save<T>(settings)` writes the supplied object.
It does not validate editor input automatically.
Call `Validate()` before saving values from a command, UI, or external service.

Reload a cached settings object only at a documented hook.
Editing a file does not mutate that cached object.
`ConfigurationReloaded` supplies the new host snapshot.
`Client.Configuration` remains the original immutable snapshot.

Malformed user TOML produces a warning and validated defaults.
Successful activation does not prove that the user file parsed correctly.
Test the warning path as well as the resulting values.

## Persistent storage

| API | Result |
| --- | --- |
| `DataDirectory` | Assigned persistent data directory |
| `GetPath(relativeName)` | Path within that directory, with parent directories created |
| `TryGet(key, out value)` | Stored text from the in-memory table |
| `Set(key, value)` | Updated text in the in-memory table |
| `Remove(key)` | Removal from the in-memory table |
| `Save()` | Durable table write |

The table persists as `data/storage.toml`.
`Set` alone does not persist a value.
Use invariant formats for machine-readable values.
Use the selected language for displayed values.

Serialize concurrent read-modify-write operations in the plugin.
The storage implementation serializes concurrent saves from the same instance.
This does not make a separate counter increment atomic.

Each save writes a temporary file and replaces the prior storage file.
Custom readers on Windows must permit replacement with `FileShare.Delete`.
Batch frequent updates to avoid excessive disk writes.

## Paths

```text
plugins/
  versions/<id>/<version>/<target>/<sha256>/  immutable packages
  userdata/<id>/settings.toml               user choices
  userdata/<id>/data/storage.toml           durable table
  userdata/<id>/data/report.json            plugin-owned file
  cache/                                   compilation and download caches
  transactions/                            installer work
  plugins.lock.toml                        selected installations
```

MCC normally places the plugin root beside its configurations directory.
`MCC_PLUGINS` can select an explicit absolute root.
Use `Storage.GetPath` instead of reconstructing these host paths in plugin code.
Do not write into an installed package or a source cache.
Do not edit the installation lock while MCC runs.

## Localization

Put user-facing messages in the package's `lang/en.toml`:

```toml
[journal]
command_help = "Show the saved session count."
function_help = "Read the saved session count."
count = "Sessions: {0}"
```

Read these messages with `context.Strings`:

```csharp
string help = context.Strings.Get("journal.command_help");
string result = context.Strings.Format("journal.count", count);
```

Nested TOML tables become dotted lookup keys.
Lookup checks the selected culture, its parents, and English.
A missing message returns its key.
A partial translation can fall back for each message separately.
Reload the plugin after changing its language files.

`context.Translations` resolves Minecraft translation keys in server text.
It is a different resource source from the plugin's `context.Strings`.

Use stable dot-delimited keys for logs, descriptions, warnings, and output.
Command names, capabilities, protocol identifiers, and grammar remain literal identifiers.
Preserve all parameter placeholders in translated text.

Tomlet comments can use `$journal.increment_help$` placeholders.
The settings writer resolves those placeholders through the plugin's language table.
Keep settings property names stable to preserve existing user values.

## Manuals

Create `man/en/session-journal.md`.
Declare `man = ["session-journal"]` in the manifest.
The host registers the topic for the plugin lifetime.
Unload removes that contribution.

Explain the following items:

1. Purpose and observable behavior.
2. Commands and whether they send server chat.
3. Settings and accepted ranges.
4. Stored data and restart behavior.
5. Dependencies and script capabilities.
6. Limits and required manual steps.

Add translated topics under matching language directories.
The English-only form `man/<topic>.md` also works.

## Settings migration

A renamed property can make an old user value ineffective.
Explain property changes in release notes.
Document whether stored data permits downgrade.
Test absent files, partial files, invalid TOML, and out-of-range values.

Settings are ordinary files, not a secret vault.
Do not include credentials in release archives or diagnostics.
Use the host's secure-storage process when it provides one.
