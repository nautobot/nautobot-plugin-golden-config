"""Nornir job for generating the compliance data."""
# pylint: disable=relative-beyond-top-level
import difflib
import logging
import os

from datetime import datetime

from netutils.config.compliance import parser_map, section_config, _open_file_config
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.task import Result, Task

from nornir_nautobot.utils.logger import NornirLogger
from nornir_nautobot.exceptions import NornirNautobotException

from nautobot_plugin_nornir.plugins.inventory.nautobot_orm import NautobotORMInventory
from nautobot_plugin_nornir.constants import NORNIR_SETTINGS

from nautobot_golden_config.models import ComplianceRule, ConfigCompliance, GoldenConfigSettings, GoldenConfiguration
from nautobot_golden_config.utilities.helper import (
    get_job_filter,
    verify_global_settings,
    check_jinja_template,
)
from .processor import ProcessGoldenConfig


InventoryPluginRegister.register("nautobot-inventory", NautobotORMInventory)
LOGGER = logging.getLogger(__name__)


def get_features():
    """A serializer of sorts to return feature mappings as a dictionary."""
    # TODO: Review if creating a proper serializer is the way to go.
    features = {}
    for obj in ComplianceRule.objects.all():
        platform = str(obj.platform.slug)
        if not features.get(platform):
            features[platform] = []
        features[platform].append({"ordered": obj.config_ordered, "obj": obj, "section": obj.match_config.splitlines()})
    return features


def diff_files(backup_file, intended_file):
    """Utility function to provide `Unix Diff` between two files."""
    bkup = open(backup_file).readlines()
    intended = open(intended_file).readlines()

    for line in difflib.unified_diff(bkup, intended, lineterm=""):
        yield line


def run_compliance(  # pylint: disable=too-many-arguments,too-many-locals
    task: Task,
    logger,
    global_settings,
    backup_root_path,
    intended_root_folder,
    features,
) -> Result:
    """Prepare data for compliance task.

    Args:
        task (Task): Nornir task individual object

    Returns:
        result (Result): Result from Nornir task
    """
    obj = task.host.data["obj"]

    compliance_obj = GoldenConfiguration.objects.filter(device=obj).first()
    if not compliance_obj:
        compliance_obj = GoldenConfiguration.objects.create(device=obj)
    compliance_obj.compliance_last_attempt_date = task.host.defaults.data["now"]
    compliance_obj.save()

    intended_path_template_obj = check_jinja_template(obj, logger, global_settings.intended_path_template)

    intended_file = os.path.join(intended_root_folder, intended_path_template_obj)

    backup_template = check_jinja_template(obj, logger, global_settings.backup_path_template)
    backup_file = os.path.join(backup_root_path, backup_template)

    platform = obj.platform.slug
    if not features.get(platform):
        logger.log_failure(obj, f"There is no `user` defined feature mapping for platform slug {platform}.")
        raise NornirNautobotException()

    if platform not in parser_map.keys():
        logger.log_failure(obj, f"There is currently no parser support for platform slug {platform}.")
        raise NornirNautobotException()

    backup_cfg = _open_file_config(backup_file)
    intended_cfg = _open_file_config(intended_file)

    # TODO: Make this atomic with compliance_obj step.
    for feature in features[obj.platform.slug]:
        # using update_or_create() method to conveniently update actual obj or create new one.
        ConfigCompliance.objects.update_or_create(
            device=obj,
            rule=feature["obj"],
            actual=section_config(feature, backup_cfg, platform),
            intended=section_config(feature, intended_cfg, platform),
        )

    compliance_obj.compliance_last_success_date = task.host.defaults.data["now"]
    compliance_obj.compliance_config = "\n".join(diff_files(backup_file, intended_file))
    compliance_obj.save()
    logger.log_success(obj, "Successfully tested compliance.")

    return Result(host=task.host)


def config_compliance(job_result, data, backup_root_path, intended_root_folder):
    """Nornir play to generate configurations."""
    now = datetime.now()
    features = get_features()
    logger = NornirLogger(__name__, job_result, data.get("debug"))
    global_settings = GoldenConfigSettings.objects.first()
    verify_global_settings(logger, global_settings, ["backup_path_template", "intended_path_template"])
    nornir_obj = InitNornir(
        runner=NORNIR_SETTINGS.get("runner"),
        logging={"enabled": False},
        inventory={
            "plugin": "nautobot-inventory",
            "options": {
                "credentials_class": NORNIR_SETTINGS.get("credentials"),
                "params": NORNIR_SETTINGS.get("inventory_params"),
                "queryset": get_job_filter(data),
                "defaults": {"now": now},
            },
        },
    )

    nr_with_processors = nornir_obj.with_processors([ProcessGoldenConfig(logger)])
    nr_with_processors.run(
        task=run_compliance,
        name="RENDER COMPLIANCE TASK GROUP",
        logger=logger,
        global_settings=global_settings,
        backup_root_path=backup_root_path,
        intended_root_folder=intended_root_folder,
        features=features,
    )

    logger.log_debug("Completed Compliance for devices.")
