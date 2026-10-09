# MCC Skills

This repository publishes agent skills through `npx skills`. It uses the MIT license.

## Layout

- Each installable skill lives under `skills/<name>/`.
- `SKILL.md` contains YAML metadata and concise agent instructions.
- `references/` contains detailed documentation.
- `assets/` contains complete examples and templates.
- `scripts/` contains deterministic helpers.
- `evals/evals.json` contains realistic test prompts.

## Authoring rules

1. Keep each skill independent of MCC and DMCBK source checkouts.
2. Use published NuGet packages or installed CLI binaries for examples.
3. Bundle the documentation needed to complete the skill's task.
4. Use ASD-STE100 structural rules for instructions.
5. Keep each instruction at 20 words or fewer when possible.
6. Keep each description at 25 words or fewer when possible.
7. Define technical terms before their first procedural use.
8. Preserve language syntax and public API names.
9. Check examples against the stated package and schema versions.
10. Separate offline checks, simulated tests, and real server tests.
11. Record missing prerequisites as unexecuted checks.

Do not link new skills to application source code. Use bundled references.
Do not claim certified ASD dictionary compliance. Do not redistribute its dictionary.
Preserve copied skill licenses and attribution. Keep new skill code and prose MIT.
Keep caches, generated build output, credentials, and evaluation outputs outside Git.
Keep only documented, deterministic fixture archives in Git.
Use concise imperative commit messages. Publish only within the user's authorized scope.

## Checks

Run `python3 scripts/validate_skills.py` from this repository.
Run `npx skills add . --list` to check installer discovery.
Test installation from a fresh temporary directory before publication.
Compile plugin examples through NuGet. Lint complete Beacon examples.
Check marketplace examples with the public MCC validator.
