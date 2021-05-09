"""Golden Configuration Plugin GraphQL Testing."""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory

from graphql import get_default_backend
from graphene_django.settings import graphene_settings

from nautobot.dcim.models import Platform, Site, Device, Manufacturer, DeviceRole, DeviceType

from nautobot_golden_config.models import (
    ConfigCompliance,
    GoldenConfiguration,
    ComplianceRule,
    GoldenConfigSettings,
    ConfigRemove,
    ConfigReplace,
)

# Use the proper swappable User model
User = get_user_model()


class TestGraphQLQuery(TestCase):  # pylint: disable=too-many-instance-attributes
    """Test GraphQL Queries for Golden Config Plugin."""

    def setUp(self):
        """Setup request and create test data to validate GraphQL."""
        super().setUp()
        self.user = User.objects.create(username="Super User", is_active=True, is_superuser=True)

        # Initialize fake request that will be required to execute GraphQL query
        self.request = RequestFactory().request(SERVER_NAME="WebRequestContext")
        self.request.id = uuid.uuid4()
        self.request.user = self.user

        self.backend = get_default_backend()
        self.schema = graphene_settings.SCHEMA

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        self.devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model="Device Type 1", slug="device-type-1"
        )
        self.devicerole1 = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        self.site1 = Site.objects.create(name="Site-1", slug="site-1", asn=65000)
        self.platform1 = Platform.objects.create(
            name="Platform1",
            slug="platform1",
        )

        self.device1 = Device.objects.create(
            name="Device 1",
            device_type=self.devicetype,
            device_role=self.devicerole1,
            site=self.site1,
            comments="First Device",
        )

        GoldenConfigSettings.objects.update(
            backup_path_template="test/backup",
            intended_path_template="test/intended",
            jinja_path_template="{{jinja_path}}",
            backup_test_connectivity=True,
            shorten_sot_query=True,
            sot_agg_query="{test_model}",
        )

        ComplianceRule.objects.create(
            name="aaa",
            platform=self.platform1,
            description="Test Desc",
            config_ordered=True,
            match_config="aaa ",
        )

        ConfigCompliance.objects.create(
            device=self.device1,
            name="aaa",
            compliance=True,
            actual="aaa test",
            intended="aaa test",
            missing="",
            extra="",
            ordered=False,
        )

        GoldenConfiguration.objects.create(
            device=self.device1,
            backup_config="interface Eth1/1\ndescription test",
            intended_config="interface Ethernet1/1\ndescription test",
            compliance_config="interface Ethernet1/1\ndescription test",
        )

        ConfigRemove.objects.create(
            name="Test Removal", platform=self.platform1, description="Test Desc", regex_line="^.Test.*"
        )

        ConfigReplace.objects.create(
            name="Test Replace",
            platform=self.platform1,
            description="Test Desc",
            substitute_text="username\\s+(\\S+)",
            replaced_text="<redacted>",
        )

    def execute_query(self, query, variables=None):
        """Function to execute a GraphQL query."""
        document = self.backend.document_from_string(self.schema, query)
        if variables:
            return document.execute(context_value=self.request, variable_values=variables)
        return document.execute(context_value=self.request)

    def test_query_config_compliance(self):
        """Test GraphQL Config Compliance Model."""
        query = """
            query {
                config_compliances {
                    device {
                        name
                    }
                    name
                    compliance
                    actual
                    intended
                    missing
                    extra
                    ordered
                    }
                }
        """
        response_data = {
            "config_compliances": [
                {
                    "actual": "aaa test",
                    "compliance": True,
                    "device": {"name": "Device 1"},
                    "extra": "",
                    "name": "aaa",
                    "intended": "aaa test",
                    "missing": "",
                    "ordered": False,
                }
            ]
        }
        result = self.execute_query(query)
        self.assertEqual(result.data, response_data)
        self.assertEqual(len(result.data["config_compliances"]), 1)

    def test_query_golden_config(self):
        """Test Configuration management Model."""
        query = """
            query {
                golden_configurations {
                    device {
                        name
                    }
                    backup_config
                    intended_config
                    compliance_config
                    }
                }
        """
        # Need to figure out how to execute a mock Job.
        response_data = {
            "golden_configurations": [
                {
                    "device": {"name": "Device 1"},
                    "backup_config": "interface Eth1/1\ndescription test",
                    "intended_config": "interface Ethernet1/1\ndescription test",
                    "compliance_config": "interface Ethernet1/1\ndescription test",
                }
            ]
        }
        result = self.execute_query(query)
        self.assertEqual(result.data, response_data)
        self.assertEqual(len(result.data["golden_configurations"]), 1)

    def test_query_compliance_rule(self):
        """Test Configuration Compliance Details Model."""
        query = """
            query {
                compliance_rules {
                    name
                    platform {
                        name
                    }
                    description
                    config_ordered
                    match_config
                }
            }
        """
        response_data = {
            "compliance_rules": [
                {
                    "name": "test",
                    "platform": {"name": "Platform1"},
                    "description": "Test Desc",
                    "config_ordered": True,
                    "match_config": "test",
                }
            ]
        }
        result = self.execute_query(query)
        self.assertEqual(result.data, response_data)
        self.assertEqual(len(result.data["compliance_rules"]), 1)

    def test_query_golden_config_settings(self):
        """Test GraphQL Golden Config Settings Model."""
        query = """
            query {
                golden_config_settingss {
                    backup_path_template
                    intended_path_template
                    jinja_path_template
                    backup_test_connectivity
                    shorten_sot_query
                    sot_agg_query
                }
            }
        """
        response_data = {
            "golden_config_settingss": [
                {
                    "backup_path_template": "test/backup",
                    "intended_path_template": "test/intended",
                    "jinja_path_template": "{{jinja_path}}",
                    "backup_test_connectivity": True,
                    "shorten_sot_query": True,
                    "sot_agg_query": "{test_model}",
                }
            ]
        }
        result = self.execute_query(query)
        self.assertEqual(result.data, response_data)
        self.assertEqual(len(result.data["golden_config_settingss"]), 1)

    def test_query_line_removal(self):
        """Test Regex Line Removal."""
        query = """
            query {
                backup_config_line_removes {
                    name
                    platform {
                        name
                    }
                    description
                    regex_line
                }
            }
        """

        response_data = {
            "backup_config_line_removes": [
                {
                    "name": "Test Removal",
                    "platform": {"name": "Platform1"},
                    "description": "Test Desc",
                    "regex_line": "^.Test.*",
                }
            ]
        }
        result = self.execute_query(query)
        self.assertEqual(len(result.data["backup_config_line_removes"]), 1)
        self.assertEqual(result.data, response_data)

    def test_query_line_replace(self):
        """Test Line Replacement Model."""
        query = """
            query {
                backup_config_line_replaces {
                    name
                    platform {
                        name
                    }
                    description
                    substitute_text
                    replaced_text
                }
            }
        """

        response_data = {
            "backup_config_line_replaces": [
                {
                    "name": "Test Replace",
                    "platform": {"name": "Platform1"},
                    "description": "Test Desc",
                    "substitute_text": "username\\s+(\\S+)",
                    "replaced_text": "<redacted>",
                }
            ]
        }
        result = self.execute_query(query)
        self.assertEqual(len(result.data["backup_config_line_replaces"]), 1)
        self.assertEqual(result.data, response_data)
