# MCC Skills

Agent skills for Beacon scripting, DMCBK plugins, plugin marketplaces, C# development, and clear technical writing. Each skill contains instructions and reference material. The authoring skills also include working examples.

These skills do not need an MCC or DMCBK source checkout. Beacon examples use an installed MCC CLI. Plugin examples use published NuGet packages.

## Install

Install [Node.js](https://nodejs.org/en/download) to use `npx`. Run the command from the project where you want the skills.

```bash
npx skills add MCCTeam/MCC-Skills
```

Select the skills and agent in the installer. For one skill and Codex:

```bash
npx skills add MCCTeam/MCC-Skills --skill beacon-scripting --agent codex
```

For Claude Code, replace `codex` with `claude-code`. Add `--global` to make the skill available across projects.

List the available skills:

```bash
npx skills add MCCTeam/MCC-Skills --list
```

Install all skills for one agent without prompts:

```bash
npx skills add MCCTeam/MCC-Skills --skill '*' --agent codex --yes
```

The [Vercel skills CLI](https://github.com/vercel-labs/skills) handles discovery and installation. This repository does not publish a separate npm installer.

## Choose a skill

| Skill | Use it to |
| --- | --- |
| [asd-ste100](skills/asd-ste100/SKILL.md) | Rewrite ambiguous instructions, tool descriptions, errors, and status reports. |
| [beacon-scripting](skills/beacon-scripting/SKILL.md) | Create, check, and test `.bcn` scripts, events, commands, and scheduled tasks. |
| [dmcbk-plugin-authoring](skills/dmcbk-plugin-authoring/SKILL.md) | Create source or compiled plugins with lifecycle, settings, localization, and tests. |
| [dmcbk-marketplace-authoring](skills/dmcbk-marketplace-authoring/SKILL.md) | Create schema-2 catalogues, versioned releases, platform assets, and checksums. |
| [csharp-best-practices](skills/csharp-best-practices/SKILL.md) | Write and review C# code, including async behavior and cancellation. |
| [csharp-solid-principles](skills/csharp-solid-principles/SKILL.md) | Review responsibilities, interfaces, dependencies, and maintainability. |
| [dotnet-performance-profiling-and-optimization](skills/dotnet-performance-profiling-and-optimization/SKILL.md) | Measure and diagnose CPU, memory, latency, and concurrency problems. |
| [dotnet-security-review](skills/dotnet-security-review/SKILL.md) | Review .NET application security and dependency risks. |

Plugin and marketplace authoring are separate skills. Install both when you need to publish your plugin:

```bash
npx skills add MCCTeam/MCC-Skills --skill dmcbk-plugin-authoring dmcbk-marketplace-authoring --agent codex
```

## Use a skill

Ask your agent for the task you need. For example:

- "Create a Beacon script that replies to `!hello` and saves its greeting count."
- "Create a DMCBK plugin that records session starts and exposes a translated command."
- "Create a marketplace release with portable source and separate Windows and Linux compiled assets."

The agent reads the skill's instructions and loads the relevant bundled references. Ask it to state which checks ran. A successful syntax check does not prove server behavior.

The authoring examples target Beacon syntax `1`, plugin API `1.0`, schema `2`, DMCBK `0.1.0-preview.3`, and UMPK `0.9.0-beta.4`. Check compatibility before using another library version.

## Repository layout

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── references/
    ├── assets/
    ├── scripts/
    └── evals/evals.json
```

Some skills do not need every optional directory. `SKILL.md` is the installable entry point. Relative links refer to files inside that skill.

## Maintain the skills

Read [AGENTS.md](AGENTS.md) before editing. Check metadata and local references:

```bash
python3 scripts/validate_skills.py
npx skills add . --list
```

The [validation guide](docs/validation.md) explains example checks, isolated installation tests, and the evaluation prompts.

Instructions follow ASD-STE100 structural principles. This repository does not redistribute the official dictionary or claim certified STE compliance.

## License

MCC Skills uses the [MIT license](LICENSE). Copied .NET skills retain their license files and attribution.
