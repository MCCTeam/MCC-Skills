# Check the skills

Run checks from the MCC Skills repository directory unless a step specifies another directory.

## Metadata and references

```bash
python3 scripts/validate_skills.py
npx skills add . --list
```

The validator checks each skill's name, metadata, bundled links, and portable reference paths. It does not execute example code.

The installer should list seven skills. Listing does not install them into your agent directories.

## Published package checks

Install the .NET SDK selected by `global.json`. Run the consumer checks:

```bash
python3 tests/check_examples.py
```

This project restores DMCBK through NuGet. It does not reference MCC, DMCBK, or UMPK source projects.

The checks lint bundled Beacon files and parse manifests and catalogues. Provider-dependent extern examples use ordinary offline lint, then execute with their plugin loaded. They test exact chat filtering, saved state, command and export calls, cleanup, and mixed-release fallback.

The runner also builds source and compiled plugin examples. It executes four simulated loading, persistence, settings, Beacon, reload, and unload tests. It then checks packaging and reproduces the marketplace fixture digest.

Build the plugin author projects included under `skills/dmcbk-plugin-authoring`. Follow their bundled README for source and compiled packaging.

Use the installed MCC CLI for additional checks:

```bash
Mcc.Cli lint /absolute/path/to/example.bcn
Mcc.Cli --validate-plugin /absolute/path/to/plugin-folder
Mcc.Cli --validate-marketplace /absolute/path/to/mcc-marketplace.toml
```

Use `dotnet /absolute/path/Mcc.Cli.dll` when your distribution has no native executable. Use `Mcc.Cli.exe` on Windows.

These commands require binaries and package feeds. They do not require application source code.

## Check installation in isolation

1. Create a temporary project directory.
2. Run the installer from that directory.
3. Select one skill and an agent.
4. Check the installed skill and its bundled references.
5. Remove the temporary directory after the check.

Example for Codex:

```bash
npx skills add /absolute/path/to/MCC-Skills --skill beacon-scripting --agent codex --copy --yes
```

Run this example from the temporary directory. Do not add `--global` during an isolated installation check.

After publication, repeat with `MCCTeam/MCC-Skills` instead of the local path. This checks remote discovery and installation.

## Evaluate agent output

Each new authoring skill contains three prompts in `evals/evals.json`.

Run each prompt once with the skill and once without it. Keep both runs isolated. Check generated files with the compiler or interpreter.

Record the prompt, output, checks, and observed failures. Use the skill-creator review viewer to compare the results.

Keep evaluation output outside the repository. Do not invent timing, token counts, or successful checks.

## Report the test boundary

Use these terms in validation reports:

| Check | What it establishes |
| --- | --- |
| Metadata check | The installer can identify the skill. |
| Lint | The script parses and satisfies static checks. |
| Compilation | The example uses APIs available in the selected packages. |
| Simulated session | The runtime handles controlled events and test transport. |
| Live server | The selected server observes the requested action. |
| Platform execution | The asset runs on the stated operating system and architecture. |

An unexecuted check is not a pass. A cross-build does not prove native execution.
