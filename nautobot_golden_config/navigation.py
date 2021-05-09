"""Add the configuration compliance buttons to the Plugins Navigation."""

from nautobot.extras.plugins import PluginMenuItem, PluginMenuButton
from nautobot.utilities.choices import ButtonColorChoices
from .utilities.constant import ENABLE_COMPLIANCE


plugin_items = [
    PluginMenuItem(
        link="plugins:nautobot_golden_config:goldenconfiguration_list",
        link_text="Home",
        permissions=["nautobot_golden_config.view_goldenconfiguration"],
    )
]

if ENABLE_COMPLIANCE:
    plugin_items.append(
        PluginMenuItem(
            link="plugins:nautobot_golden_config:configcompliance_list",
            link_text="Configuration Compliance",
            permissions=["nautobot_golden_config.view_configcompliance"],
        )
    )
    plugin_items.append(
        PluginMenuItem(
            link="plugins:nautobot_golden_config:compliancerule_list",
            link_text="Compliance Rules",
            permissions=["nautobot_golden_config.view_compliancerule"],
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_golden_config:compliancerule_add",
                    title="Compliance Rules",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_golden_config.add_compliancerule"],
                ),
            ),
        )
    )
    plugin_items.append(
        PluginMenuItem(
            link="plugins:nautobot_golden_config:compliancefeature_list",
            link_text="Compliance Features",
            permissions=["nautobot_golden_config.view_compliancefeature"],
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_golden_config:compliancefeature_add",
                    title="Compliance Features",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_golden_config.add_compliancefeature"],
                ),
            ),
        )
    )
    plugin_items.append(
        PluginMenuItem(
            link="plugins:nautobot_golden_config:configremove_list",
            link_text="Line Removals",
            permissions=["nautobot_golden_config.view_configremove"],
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_golden_config:configremove_add",
                    title="Line Removals",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_golden_config.add_configremove"],
                ),
            ),
        )
    )
    plugin_items.append(
        PluginMenuItem(
            link="plugins:nautobot_golden_config:configreplace_list",
            link_text="Line Replacements",
            permissions=["nautobot_golden_config.view_compliancereplace"],
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_golden_config:configreplace_add",
                    title="Line Replacements",
                    icon_class="mdi mdi-plus-thick",
                    color=ButtonColorChoices.GREEN,
                    permissions=["nautobot_golden_config.add_compliancereplace"],
                ),
            ),
        )
    )
    plugin_items.append(
        PluginMenuItem(
            link="plugins:nautobot_golden_config:goldenconfigsettings",
            link_text="Settings",
            permissions=["nautobot_golden_config.view_compliancereplace"],
            buttons=(
                PluginMenuButton(
                    link="plugins:nautobot_golden_config:goldenconfigsettings_edit",
                    title="Golden Config Settings",
                    icon_class="mdi mdi-pencil",
                    color=ButtonColorChoices.YELLOW,
                    permissions=["nautobot_golden_config.edit_goldenconfigsettings"],
                ),
            ),
        ),
    )

menu_items = tuple(plugin_items)
