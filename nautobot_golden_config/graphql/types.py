"""GraphQL implementation for application dictionary plugin."""
import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from taggit.managers import TaggableManager

from nautobot.extras.graphql.types import TagType
from nautobot_golden_config import models
from nautobot_golden_config import filters


@convert_django_field.register(TaggableManager)
def convert_field_to_list_tags(field, registry=None):
    """Convert TaggableManager to List of Tags."""
    return graphene.List(TagType)


class ConfigComplianceType(DjangoObjectType):
    """Graphql Type Object for Config Compliance model."""

    class Meta:
        """Meta object boilerplate for ConfigComplianceType."""

        model = models.ConfigCompliance
        filterset_class = filters.ConfigComplianceFilter


class GoldenConfigurationType(DjangoObjectType):
    """Graphql Type Object for Golden Configuration model."""

    class Meta:
        """Meta object boilerplate for GoldenConfigurationType."""

        model = models.GoldenConfiguration
        filterset_class = filters.GoldenConfigurationFilter


class ComplianceRuleType(DjangoObjectType):
    """Graphql Type Object for Compliance Rule model."""

    class Meta:
        """Meta object boilerplate for GoldenConfigurationType."""

        model = models.ComplianceRule
        filterset_class = filters.ComplianceRuleFilter


class GoldenConfigSettingsType(DjangoObjectType):
    """Graphql Type Object for Golden Config Settings model."""

    class Meta:
        """Meta object boilerplate for GoldenConfigSettingsType."""

        model = models.GoldenConfigSettings


class ConfigRemoveType(DjangoObjectType):
    """Graphql Type Object for Backup Config Line Remove model."""

    class Meta:
        """Meta object boilerplate for ConfigRemoveType."""

        model = models.ConfigRemove


class ConfigReplaceType(DjangoObjectType):
    """Graphql Type Object for Backup Config Line Replace model."""

    class Meta:
        """Meta object boilerplate for ConfigReplaceType."""

        model = models.ConfigReplace


graphql_types = [
    ConfigComplianceType,
    GoldenConfigurationType,
    ComplianceRuleType,
    GoldenConfigSettingsType,
    ConfigRemoveType,
    ConfigReplaceType,
]
