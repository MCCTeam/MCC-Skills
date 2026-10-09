#!/usr/bin/env python3
"""Run standalone skill examples with published NuGet packages."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DOTNET = os.environ.get("SKILLS_DOTNET", "dotnet")
PLUGIN = ROOT / "skills/dmcbk-plugin-authoring"
MARKET = ROOT / "skills/dmcbk-marketplace-authoring"


def run(*args: str) -> None:
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        print(result.stdout, file=sys.stderr)
        raise SystemExit(result.returncode)
    print(result.stdout.strip())


run(DOTNET, "run", "--project", "tests/SkillExamples", "-c", "Release", "--", str(ROOT))
source = PLUGIN / "assets/source-example"
compiled = PLUGIN / "assets/compiled-template"
verifier = PLUGIN / "assets/verify-plugin/VerifyPlugin.csproj"
run(DOTNET, "build", str(source / "author/SessionJournal.csproj"), "-c", "Release", "--nologo")
run(DOTNET, "build", str(compiled / "SessionJournal.csproj"), "-c", "Release", "--nologo")
with tempfile.TemporaryDirectory(prefix="mcc-skills-examples-") as temporary:
    stage = Path(temporary) / "compiled"
    stage.mkdir()
    for name in ("plugin.toml",):
        shutil.copy2(compiled / name, stage / name)
    for name in ("lang", "man", "defaults"):
        shutil.copytree(compiled / name, stage / name)
    for name in ("SessionJournal.dll", "SessionJournal.deps.json"):
        shutil.copy2(compiled / "bin/Release/net10.0" / name, stage / name)
    for package in (source / "package", stage):
        for settings in ((), ("150",)):
            run(DOTNET, "run", "--project", str(verifier), "-c", "Release", "--", str(package), *settings)
        archive = Path(temporary) / (package.name + ".zip")
        run(sys.executable, str(PLUGIN / "scripts/package_plugin.py"), str(package), str(archive))
    release = Path(temporary) / "release"
    run(sys.executable, str(MARKET / "scripts/pack_release.py"), "pack",
        str(MARKET / "examples/local-marketplace/plugins/marketplace-demo"), "--output", str(release),
        "--base-url", "http://127.0.0.1:8765/release-assets/")
    run(sys.executable, str(MARKET / "scripts/pack_release.py"), "verify", str(release))
    name = "marketplace-demo-1.0.0-source-any.zip"
    expected = MARKET / "examples/local-marketplace/release-assets" / name
    if hashlib.sha256((release / name).read_bytes()).digest() != hashlib.sha256(expected.read_bytes()).digest():
        raise SystemExit("Marketplace fixture is not reproducible")
print("PASS: source and compiled plugins, four simulated runtime tests, packaging, and marketplace fixture reproduction.")
