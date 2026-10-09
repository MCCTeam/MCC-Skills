using System.Globalization;
using DMCBK.Core;
using DMCBK.Testing;

if (args.Length is < 1 or > 2)
    throw new ArgumentException("Supply a package folder and an optional Increment value.");

string package = Path.GetFullPath(args[0]);
int requested = args.Length == 2 ? int.Parse(args[1], CultureInfo.InvariantCulture) : 1;
int increment = Math.Clamp(requested, 1, 100);
string root = Path.Combine(Path.GetTempPath(), "session-journal-test-" + Guid.NewGuid().ToString("N"));

try
{
    if (args.Length == 2)
    {
        string user = Path.Combine(root, "userdata", "session-journal");
        Directory.CreateDirectory(user);
        File.WriteAllText(Path.Combine(user, "settings.toml"),
            $"Increment = {requested.ToString(CultureInfo.InvariantCulture)}\n");
    }

    for (int iteration = 0; iteration < 2; iteration++)
    {
        await using PluginTestHost host = PluginTestHost.Create(new()
        {
            PluginsRoot = root,
            Budget = TimeSpan.FromSeconds(60)
        });
        // The preview creates the Beacon engine lazily. Initialize before activation.
        host.Client.Scripts.SetMuted(false);
        host.AddPluginFolder(package);
        var loaded = await host.LoadAsync(host.Token);
        if (!loaded.Success || !host.Plugins.List().Single().Loaded)
            throw new InvalidOperationException("Activation failed: " + loaded.Message);

        int previous = iteration * increment;
        await CheckCountAsync(host, previous);
        await CheckBeaconAsync(host, previous);

        int expected = previous + increment;
        await host.RunSessionAsync(async _ =>
        {
            string value = expected.ToString(CultureInfo.InvariantCulture);
            bool changed = await host.WaitForAsync(
                () => host.Client.Variables.Get("session_journal_sessions") == value,
                host.Token);
            if (!changed)
                throw new InvalidOperationException("The session callback did not update the count.");
            await CheckCountAsync(host, expected);
            var liveReload = await host.Plugins.ReloadAsync("session-journal", host.Token);
            if (!liveReload.Success || !host.Plugins.List().Single().Loaded)
                throw new InvalidOperationException("Connected reload failed: " + liveReload.Message);
            await CheckCountAsync(host, expected);
            await CheckBeaconAsync(host, expected);
        }, host.Token);

        if (!File.Exists(host.DataFile("session-journal", "storage.toml")))
            throw new InvalidOperationException("The storage table was not saved.");

        var reloaded = await host.Plugins.ReloadAsync("session-journal", host.Token);
        if (!reloaded.Success || !host.Plugins.List().Single().Loaded)
            throw new InvalidOperationException("Reload failed: " + reloaded.Message);
        await CheckCountAsync(host, expected);
        await CheckBeaconAsync(host, expected);

        var unloaded = await host.Plugins.UnloadAsync("session-journal", host.Token);
        if (!unloaded.Success)
            throw new InvalidOperationException("Unload failed: " + unloaded.Message);
        var missing = await host.Client.Commands.DispatchAsync("journal-count", host.Token);
        if (missing.IsSuccess)
            throw new InvalidOperationException("The command remained available after unload.");
    }

    Console.WriteLine("PASS: load, pre-session Beacon, two fresh clients, storage, connected reload without recount, and command cleanup.");
}
finally
{
    if (Directory.Exists(root))
        Directory.Delete(root, recursive: true);
}

static async Task CheckCountAsync(PluginTestHost host, int expected)
{
    var result = await host.Client.Commands.DispatchAsync("journal-count", host.Token);
    string message = "Sessions: " + expected.ToString(CultureInfo.InvariantCulture);
    if (!result.IsSuccess || result.Message != message)
        throw new InvalidOperationException($"Expected '{message}', received '{result.Message}'.");
}

static async Task CheckBeaconAsync(PluginTestHost host, int expected)
{
    string script = """
        # beacon 1
        # needs: journal.read
        extern journal_count from "session-journal"
        assert(journal_count() is EXPECTED, "saved count")
        show journal_count()
        """.Replace("EXPECTED", expected.ToString(CultureInfo.InvariantCulture), StringComparison.Ordinal);
    try
    {
        var run = await host.Client.Scripts.RunAsync("read-count", script, ct: host.Token);
        if (!run.Success || !run.LocalOutput.Contains(expected.ToString(CultureInfo.InvariantCulture)))
            throw new InvalidOperationException("The Beacon bridge did not return the saved count.");
    }
    finally
    {
        host.Client.Scripts.Stop("read-count");
    }
}
