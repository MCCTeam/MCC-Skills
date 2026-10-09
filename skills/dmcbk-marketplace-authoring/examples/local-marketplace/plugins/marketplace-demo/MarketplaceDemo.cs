using System.Threading.Tasks;
using DMCBK.PluginSdk;

public sealed class MarketplaceDemo : IPlugin
{
    public void Configure(PluginDescriptor descriptor)
    {
        descriptor.Id = "marketplace-demo";
        descriptor.Version = "1.0.0";
        descriptor.WithSettings<MarketplaceDemoSettings>();
    }

    public Task ActivateAsync(PluginContext context)
    {
        MarketplaceDemoSettings settings = context.Settings.Load<MarketplaceDemoSettings>();
        if (settings.WriteMarker)
        {
            context.Storage.Set("activation", context.Strings.Get("demo.activation"));
            context.Storage.Save();
        }
        return Task.CompletedTask;
    }
}

public sealed class MarketplaceDemoSettings
{
    public bool WriteMarker { get; set; } = true;
}
