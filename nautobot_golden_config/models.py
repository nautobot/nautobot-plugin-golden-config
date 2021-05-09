"""Django Models for tracking the configuration compliance per feature and device."""

import logging

from django.db import models
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import reverse
from graphene_django.settings import graphene_settings
from graphql import get_default_backend
from graphql.error import GraphQLSyntaxError

from nautobot.dcim.models import Device
from nautobot.extras.models import ObjectChange
from nautobot.extras.utils import extras_features
from nautobot.utilities.utils import get_filterset_for_model, serialize_object
from nautobot.core.models.generics import PrimaryModel
from netutils.config.compliance import feature_compliance

from nautobot_golden_config.choices import ComplianceRuleTypeChoice


LOGGER = logging.getLogger(__name__)
GRAPHQL_STR_START = "query ($device_id: ID!)"


def null_to_empty(val):
    """Convert to empty string if the value is currently null."""
    if not val:
        return ""
    return val


@extras_features(
    "custom_fields",
    "custom_validators",
    "export_templates",
    "relationships",
    "graphql",
    "webhooks",
)
class ComplianceFeature(PrimaryModel):
    """Compliance feature details."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        """Meta information for ComplianceRule model."""

        ordering = ("slug",)

    def __str__(self):
        """Return a sane string representation of the instance."""
        return self.slug

    def get_absolute_url(self):  # pylint: disable=no-self-use
        """Absolute url for the ComplianceRule instance."""
        return reverse("plugins:nautobot_golden_config:compliancefeature_list")


@extras_features(
    "custom_fields",
    "custom_validators",
    "export_templates",
    "relationships",
    "graphql",
    "webhooks",
)
class ComplianceRule(PrimaryModel):
    """Configuration compliance details."""

    feature = models.ForeignKey(to="ComplianceFeature", on_delete=models.CASCADE, blank=False, related_name="feature")

    platform = models.ForeignKey(
        to="dcim.Platform",
        on_delete=models.CASCADE,
        related_name="compliance_rules",
        null=False,
        blank=False,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    config_ordered = models.BooleanField(
        null=False,
        blank=False,
        verbose_name="Configured Ordered",
        help_text="Whether or not the configuration order matters, such as in ACLs.",
    )
    match_config = models.TextField(
        null=True,
        blank=False,
        verbose_name="Config to Match",
        help_text="The config to match that is matched based on the parent most configuration. e.g. `router bgp` or `ntp`.",
    )
    config_type = models.CharField(
        max_length=20,
        default=ComplianceRuleTypeChoice.TYPE_CLI,
        choices=ComplianceRuleTypeChoice,
        help_text="Whether the config is in cli or json/structured format.",
    )

    class Meta:
        """Meta information for ComplianceRule model."""

        ordering = ("platform", "feature__name")
        unique_together = (
            "feature",
            "platform",
        )

    def __str__(self):
        """Return a sane string representation of the instance."""
        return f"{self.platform} - {self.feature.name}"

    def get_absolute_url(self):  # pylint: disable=no-self-use
        """Absolute url for the ComplianceRule instance."""
        return reverse("plugins:nautobot_golden_config:compliancerule_list")

    def clean(self):
        """Verify that if cli, then match_config is set."""
        if self.config_type == ComplianceRuleTypeChoice.TYPE_CLI and not self.match_config:
            raise ValidationError("CLI configuration set, but no configuration set to match.")
        if self.config_type == ComplianceRuleTypeChoice.TYPE_JSON:
            raise ValidationError("JSON currently not supported.")


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class ConfigCompliance(PrimaryModel):
    """Configuration compliance details."""

    device = models.ForeignKey(to="dcim.Device", on_delete=models.CASCADE, help_text="The device", blank=False)
    rule = models.ForeignKey(to="ComplianceRule", on_delete=models.CASCADE, blank=False, related_name="rule")
    compliance = models.BooleanField(null=True, blank=True)
    actual = models.TextField(blank=True, help_text="Actual Configuration for feature")
    intended = models.TextField(blank=True, help_text="Intended Configuration for feature")
    missing = models.TextField(blank=True, help_text="Configuration that should be on the device.")
    extra = models.TextField(blank=True, help_text="Configuration that should not be on the device.")
    ordered = models.BooleanField(default=True)
    compliance_int = models.IntegerField(null=True, blank=True)

    csv_headers = ["Device Name", "Feature", "Compliance"]

    def get_absolute_url(self):
        """Return absolute URL for instance."""
        return reverse("plugins:nautobot_golden_config:configcompliance", args=[self.pk])

    def to_csv(self):
        """Indicates model fields to return as csv."""
        return (self.device.name, self.rule.feature.name, self.compliance)

    def to_objectchange(self, action):
        """Remove actual and intended configuration from changelog."""
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            object_data=serialize_object(self, exclude=["actual", "intended"]),
        )

    class Meta:
        """Set unique together fields for model."""

        ordering = ["device"]
        unique_together = ("device", "rule")

    def __str__(self):
        """String representation of a the compliance."""
        return f"{self.device} -> {self.rule} -> {self.compliance}"

    def save(self, *args, **kwargs):
        """Perform that actual compliance check."""
        feature = {
            "ordered": self.rule.config_ordered,
            "name": self.rule.feature.name,
            "section": self.rule.match_config.splitlines(),
        }
        value = feature_compliance(feature, self.actual, self.intended, self.device.platform.slug)
        self.compliance = value["compliant"]
        if self.compliance:
            self.compliance_int = 1
        else:
            self.compliance_int = 0
        self.ordered: value["ordered_compliant"]
        self.missing = null_to_empty(value["missing"])
        self.extra = null_to_empty(value["extra"])
        super().save(*args, **kwargs)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class GoldenConfiguration(PrimaryModel):
    """Configuration Management Model."""

    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        help_text="device",
        blank=False,
    )
    backup_config = models.TextField(blank=True, help_text="Full backup config for device.")
    backup_last_attempt_date = models.DateTimeField(null=True)
    backup_last_success_date = models.DateTimeField(null=True)

    intended_config = models.TextField(blank=True, help_text="Intended config for the device.")
    intended_last_attempt_date = models.DateTimeField(null=True)
    intended_last_success_date = models.DateTimeField(null=True)

    compliance_config = models.TextField(blank=True, help_text="Full config diff for device.")
    compliance_last_attempt_date = models.DateTimeField(null=True)
    compliance_last_success_date = models.DateTimeField(null=True)

    csv_headers = [
        "Device Name",
        "backup attempt",
        "backup successful",
        "intended attempt",
        "intended successful",
        "compliance attempt",
        "compliance successful",
    ]

    def to_csv(self):
        """Indicates model fields to return as csv."""
        return (
            self.device,
            self.backup_last_attempt_date,
            self.backup_last_success_date,
            self.intended_last_attempt_date,
            self.intended_last_success_date,
            self.compliance_last_attempt_date,
            self.compliance_last_success_date,
        )

    def to_objectchange(self, action):
        """Remove actual and intended configuration from changelog."""
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            object_data=serialize_object(self, exclude=["backup_config", "intended_config", "compliance_config"]),
        )

    class Meta:
        """Set unique together fields for model."""

        ordering = ["device"]

    def __str__(self):
        """String representation of a the compliance."""
        return f"{self.device}"


class GoldenConfigSettings(PrimaryModel):
    """GoldenConfigSettings Model defintion. This provides global configs instead of via configs.py."""

    # TODO: Need to limit to the correct content_identifier or is it _token?
    backup_repository = models.ForeignKey(
        to="extras.GitRepository", on_delete=models.CASCADE, null=True, blank=True, related_name="backup_repository"
    )
    backup_path_template = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        verbose_name="Backup Path in Jinja Template Form",
        help_text="The Jinja path representation of where the backup file will be found. The variable `obj` is available as the device instance object of a given device, as is the case for all Jinja templates. e.g. `{{obj.site.slug}}/{{obj.name}}.cfg`",
    )
    intended_repository = models.ForeignKey(
        to="extras.GitRepository", on_delete=models.CASCADE, null=True, blank=True, related_name="intended_repository"
    )
    intended_path_template = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        verbose_name="Intended Path in Jinja Template Form",
        help_text="The Jinja path representation of where the generated file will be places. e.g. `{{obj.site.slug}}/{{obj.name}}.cfg`",
    )
    jinja_repository = models.ForeignKey(
        to="extras.GitRepository", on_delete=models.CASCADE, null=True, blank=True, related_name="jinja_template"
    )
    jinja_path_template = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        verbose_name="Template Path in Jinja Template Form",
        help_text="The Jinja path representation of where the Jinja template can be found. e.g. `{{obj.platform.slug}}.j2`",
    )
    backup_test_connectivity = models.BooleanField(
        null=False,
        default=True,
        verbose_name="Backup Test",
        help_text="Whether or not to pretest the connectivity of the device by verifying there is a resolvable IP that can connect to port 22.",
    )
    scope = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        null=True,
        help_text="Queryset filter matching the list of devices for the scope of devices to be considered.",
    )
    sot_agg_query = models.TextField(
        null=False,
        blank=True,
        verbose_name="GraphQL Query",
        help_text=f"A query that is evaluated and used to render the config. The query must start with `{GRAPHQL_STR_START}`.",
    )

    def get_absolute_url(self):  # pylint: disable=no-self-use
        """Return absolute URL for instance."""
        return reverse("plugins:nautobot_golden_config:goldenconfigsettings")

    def __str__(self):
        """Return a simple string if model is called."""
        return "Golden Config Settings"

    def delete(self, *args, **kwargs):
        """Enforce the singleton pattern, there is no way to delete the configurations."""

    @classmethod
    def load(cls):
        """Enforce the singleton pattern, fail it somehow more than one instance."""
        if len(cls.objects.all()) != 1:
            raise ValidationError("There was an error where more than one instance existed for a setting.")
        return cls.objects.first()

    def clean(self):
        """Validate there is only one model and if there is a GraphQL query, that it is valid."""
        super().clean()

        if self.sot_agg_query:
            try:
                LOGGER.debug("GraphQL - test query: `%s`", str(self.sot_agg_query))
                backend = get_default_backend()
                schema = graphene_settings.SCHEMA
                backend.document_from_string(schema, str(self.sot_agg_query))
            except GraphQLSyntaxError as error:
                raise ValidationError(str(error))  # pylint: disable=raise-missing-from

            LOGGER.debug("GraphQL - test  query start with: `%s`", GRAPHQL_STR_START)
            if not str(self.sot_agg_query).startswith(GRAPHQL_STR_START):
                raise ValidationError(f"The GraphQL query must start with exactly `{GRAPHQL_STR_START}`")

        if self.scope:
            filterset_class = get_filterset_for_model(Device)
            filterset = filterset_class(self.scope, Device.objects.all())

            if filterset.errors:
                for key in filterset.errors:
                    error_message = ", ".join(filterset.errors[key])
                    raise ValidationError({"scope": f"{key}: {error_message}"})

            filterset_params = set(filterset.get_filters().keys())
            for key in self.scope.keys():
                if key not in filterset_params:
                    raise ValidationError({"scope": f"'{key}' is not a valid filter parameter for Device object"})

    def get_queryset(self):
        """Generate a Device QuerySet from the filter."""
        if not self.scope:
            return Device.objects.all()

        filterset_class = get_filterset_for_model(Device)
        filterset = filterset_class(self.scope, Device.objects.all())

        return filterset.qs

    def device_count(self):
        """Return the number of devices in the group."""
        return self.get_queryset().count()

    def get_filter_as_string(self):
        """Get filter as string."""
        if not self.scope:
            return None

        result = ""

        for key, value in self.scope.items():
            if isinstance(value, list):
                for item in value:
                    if result != "":
                        result += "&"
                    result += f"{key}={item}"
            else:
                result += "&"
                result += f"{key}={value}"

        return result

    def get_url_to_filtered_device_list(self):
        """Get url to all devices that are matching the filter."""
        base_url = reverse("dcim:device_list")
        filter_str = self.get_filter_as_string()

        if filter_str:
            return f"{base_url}?{filter_str}"

        return base_url


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class ConfigRemove(PrimaryModel):
    """GoldenConfigSettings for Regex Line Removals from Backup Configuration Model defintion."""

    name = models.CharField(max_length=255, null=False, blank=False)
    platform = models.ForeignKey(
        to="dcim.Platform",
        on_delete=models.CASCADE,
        related_name="backup_line_remove",
        null=False,
        blank=False,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    regex_line = models.CharField(
        max_length=200,
        verbose_name="Regex Pattern",
        help_text="Regex pattern used to remove a line from the backup configuration.",
    )
    csv_headers = ["name", "platform", "description", "regex_line"]

    class Meta:
        """Meta information for ComplianceRule model."""

        ordering = ("platform", "name")
        unique_together = ("name", "platform")

    def __str__(self):
        """Return a simple string if model is called."""
        return self.name

    def get_absolute_url(self):  # pylint: disable=no-self-use
        """Return absolute URL for instance."""
        # TODO: Update to create detailed view, as shown in next line
        # return reverse("plugins:nautobot_golden_config:configremove", args=[self.pk])
        return reverse(
            "plugins:nautobot_golden_config:configremove_list",
        )


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class ConfigReplace(PrimaryModel):
    """GoldenConfigSettings for Regex Line Replacements from Backup Configuration Model defintion."""

    name = models.CharField(max_length=255, null=False, blank=False)
    platform = models.ForeignKey(
        to="dcim.Platform",
        on_delete=models.CASCADE,
        related_name="backup_line_replace",
        null=False,
        blank=False,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    substitute_text = models.CharField(
        max_length=200,
        verbose_name="Regex Pattern to Substitute",
        help_text="Regex pattern that will be found and replaced with 'replaced text'.",
    )
    replaced_text = models.CharField(
        max_length=200,
        verbose_name="Replaced Text",
        help_text="Text that will be inserted in place of Regex pattern match.",
    )

    csv_headers = ["name", "platform", "description", "substitute_text", "replaced_text"]

    class Meta:
        """Meta information for ComplianceRule model."""

        ordering = ("platform", "name")
        unique_together = ("name", "platform")

    def get_absolute_url(self):  # pylint: disable=no-self-use
        """Return absolute URL for instance."""
        # TODO: Update to create detailed view, as shown in next line
        # return reverse("plugins:nautobot_golden_config:configreplace", args=[self.pk])
        return reverse(
            "plugins:nautobot_golden_config:configreplace_list",
        )

    def __str__(self):
        """Return a simple string if model is called."""
        return self.name
