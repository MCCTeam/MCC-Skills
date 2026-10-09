using DMCBK.Core.Beacon;
using DMCBK.Marketplace;
using DMCBK.PluginSdk;
using DMCBK.Testing;

string root = Path.GetFullPath(args.Length > 0 ? args[0] : ".");
string skills = Path.Combine(root, "skills");
int count = 0;
foreach (string path in Directory.EnumerateFiles(skills, "*.bcn", SearchOption.AllDirectories))
{
    BeaconLintReport report = BeaconLint.LintSource(path, await File.ReadAllTextAsync(path), new BeaconLintOptions(Strict: path.Contains("beacon-scripting"), TargetLib: 2));
    if (!report.Ok)
        throw new InvalidOperationException($"Invalid Beacon example: {path}\n{string.Join("\n", report.Diagnostics)}");
    count++;
}
foreach (string path in Directory.EnumerateFiles(skills, "plugin.toml", SearchOption.AllDirectories))
{
    if (!PluginManifest.TryParse(await File.ReadAllTextAsync(path), out _, out string? error))
        throw new InvalidOperationException($"Invalid plugin manifest: {path}: {error}");
    count++;
}

if (count < 13) throw new InvalidOperationException("Bundled examples are missing");

foreach (string path in Directory.EnumerateFiles(skills, "mcc-marketplace.toml", SearchOption.AllDirectories))
    MarketplaceIndex.Parse(await File.ReadAllTextAsync(path));
foreach (string path in Directory.EnumerateFiles(skills, "*.toml", SearchOption.AllDirectories)
    .Where(p => p.Contains($"{Path.DirectorySeparatorChar}catalog{Path.DirectorySeparatorChar}") || p.EndsWith(".catalogue.toml")))
    ReleaseCatalogue.Parse(await File.ReadAllTextAsync(path));

string examples = Path.Combine(skills, "beacon-scripting", "assets", "examples");
string temporary = Path.Combine(Path.GetTempPath(), "mcc-skills-check-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(temporary);
var host = new ScriptTestHost();
var clock = new VirtualClock(DateTimeOffset.UnixEpoch.AddMilliseconds(100900));
var engine = new BeaconEngine(host, clock);
try
{
    string source = await File.ReadAllTextAsync(Path.Combine(examples, "greet-counter.bcn"));
    Check((await engine.RunScriptAsync("greet-counter", source, configFolder: temporary)).Success, "Greeting example load");
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Alice", "unrelated"));
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Alice", " !HELLO "));
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Alice", "!hello"));
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Bob", "!hello later"));
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Bob", "!hello"));
    Check(host.Whispers.SequenceEqual(new[] { ("Alice", "Hello, Alice!"), ("Bob", "Hello, Bob!") }), "Exact match and per-player delay");
    BeaconRunResult stats = await engine.InvokeScriptCommandAsync("greeting-stats", new Dictionary<string, string>());
    Check(stats.Success && stats.LocalOutput.Contains("Greetings: 2"), "Greeting count command");
    clock.Advance(TimeSpan.FromMilliseconds(4100));
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Alice", "!hello"));
    Check(host.Whispers.Count == 2, "Minimum delay at a fractional-second boundary");
    clock.Advance(TimeSpan.FromSeconds(1));
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Alice", "!hello"));
    Check(host.Whispers.Count == 3, "Greeting resumes after the minimum gap");
    engine.RemoveScript("greet-counter");
    await engine.FireEventAsync("chat", BeaconEventFields.Chat("Carol", "!hello"));
    Check(host.Whispers.Count == 3, "Greeting handler cleanup");
    var restarted = new BeaconEngine(host);
    try
    {
        Check((await restarted.RunScriptAsync("greet-counter", source, configFolder: temporary)).Success, "Greeting reload");
        stats = await restarted.InvokeScriptCommandAsync("greeting-stats", new Dictionary<string, string>());
        Check(stats.Success && stats.LocalOutput.Contains("Greetings: 3"), "Durable saved count");
    }
    finally { restarted.RemoveScript("greet-counter"); }

    Check((await engine.RunScriptAsync("shop-provider", await File.ReadAllTextAsync(Path.Combine(examples, "shop-provider.bcn")))).Success, "Provider load");
    Check((await engine.RunScriptAsync("shop-caller", await File.ReadAllTextAsync(Path.Combine(examples, "shop-caller.bcn")))).Success, "Caller load");
    var argsMap = new Dictionary<string, string> { ["price"] = "3", ["count"] = "4" };
    BeaconRunResult total = await engine.InvokeScriptCommandAsync("shop-total", argsMap);
    Check(total.Success && total.LocalOutput.Contains("Order total: 12"), "Provider call");
    argsMap["price"] = "invalid";
    total = await engine.InvokeScriptCommandAsync("shop-total", argsMap);
    Check(total.Success && total.LocalOutput.Contains("Enter a numeric price and count."), "Numeric conversion guard");
    engine.RemoveScript("shop-provider");
    argsMap["price"] = "3";
    total = await engine.InvokeScriptCommandAsync("shop-total", argsMap);
    Check(total.Success && total.LocalOutput.Any(p => p.StartsWith("Provider unavailable:")), "Provider disappearance recovery");
}
finally
{
    engine.RemoveScript("greet-counter");
    engine.RemoveScript("shop-provider");
    engine.RemoveScript("shop-caller");
    Directory.Delete(temporary, true);
}

var release = new PluginRelease
{
    Version = "1.0.0",
    Assets = [new() { Kind = "compiled", Target = "win-x64" }, new() { Kind = "source", Target = "any" }],
};
if (AssetSelector.Select(release, "win-x64").Kind != "compiled")
    throw new InvalidOperationException("Exact platform selection failed");
try
{
    AssetSelector.Select(release, "linux-x64");
    throw new InvalidOperationException("Mixed source fallback occurred without permission");
}
catch (MarketplaceException) { }
if (AssetSelector.Select(release, "linux-x64", new AssetPolicy(AllowSourceFallback: true)).Kind != "source")
    throw new InvalidOperationException("Explicit source fallback failed");
Console.WriteLine($"PASS: {count} bundled files, Beacon filtering, saved state, commands, exports, cleanup, and asset policy.");

static void Check(bool condition, string name)
{
    if (!condition) throw new InvalidOperationException(name + " failed");
}
