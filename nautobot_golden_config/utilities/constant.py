"""Storage of data that will not change throughout the life cycle of application."""
from django.conf import settings

PLUGIN_CFG = settings.PLUGINS_CONFIG["nautobot_golden_config"]

ENABLE_INTENDED = PLUGIN_CFG["enable_intended"]
ENABLE_COMPLIANCE = PLUGIN_CFG["enable_compliance"]
ENABLE_BACKUP = PLUGIN_CFG["enable_backup"]
ENABLE_SOTAGG = PLUGIN_CFG["enable_sotagg"]

CONFIG_FEATURES = {
    "intended": ENABLE_INTENDED,
    "compliance": ENABLE_COMPLIANCE,
    "backup": ENABLE_BACKUP,
    "sotagg": ENABLE_SOTAGG,
}
