"""Plugin declaration for nautobot_golden_config."""

__version__ = "0.9.0"

from nautobot.extras.plugins import PluginConfig


class GoldenConfiguration(PluginConfig):
    """Plugin configuration for the nautobot_golden_config plugin."""

    name = "nautobot_golden_config"
    verbose_name = "Golden Configuration"
    version = __version__
    author = "Network to Code, LLC"
    author_email = "opensource@networktocode.com"
    description = "A plugin for managing Golden Configurations."
    base_url = "golden-config"
    required_settings = []
    # min_version = "0"
    # max_version = "100"
    default_settings = {
        "enable_backup": True,
        "enable_golden": True,
        "enable_compliance": True,
        "enable_sotagg": True,
        "per_feature_width": 13,
        "per_feature_height": 4,
        "per_feature_bar_width": 0.3,
    }
    caching_config = {}


config = GoldenConfiguration  # pylint:disable=invalid-name
