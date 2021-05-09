"""Unit tests for nautobot_golden_config models."""

from django.test import TestCase
from django.core.exceptions import ValidationError

from nautobot.dcim.models import Platform

from nautobot_golden_config.models import (
    GoldenConfigSettings,
    ConfigRemove,
    ConfigReplace,
)


class ConfigComplianceModelTestCase(TestCase):
    """Test ConfigCompliance Model."""


class GoldenConfigurationTestCase(TestCase):
    """Test GoldenConfiguration Model."""


class ComplianceRuleTestCase(TestCase):
    """Test ComplianceRule Model."""


class GoldenConfigSettingsModelTestCase(TestCase):
    """Test GoldenConfigSettings Model."""

    def setUp(self):
        """Get the golden config settings with the only allowed id."""
        self.global_settings = GoldenConfigSettings.objects.first()

    def test_bad_graphql_query(self):
        """Invalid graphql query."""
        self.global_settings.sot_agg_query = 'devices(name:"ams-edge-01")'
        with self.assertRaises(ValidationError):
            self.global_settings.clean()

    def test_good_graphql_query_invalid_starts_with(self):
        """Valid graphql query, however invalid in the usage with golden config plugin."""
        self.global_settings.sot_agg_query = '{devices(name:"ams-edge-01"){id}}'
        with self.assertRaises(ValidationError) as error:
            self.global_settings.clean()
        self.assertEqual(error.exception.message, "The GraphQL query must start with exactly `query ($device_id: ID!)`")

    def test_good_graphql_query_validate_starts_with(self):
        """Ensure clean() method returns None when valid query is sent through."""
        self.global_settings.sot_agg_query = "query ($device_id: ID!) {device(id: $device_id) {id}}"
        self.assertEqual(self.global_settings.clean(), None)


class ConfigRemoveModelTestCase(TestCase):
    """Test ConfigRemove Model."""

    def setUp(self):
        """Setup Object."""
        self.platform = Platform.objects.create(slug="cisco_ios")
        self.line_removal = ConfigRemove.objects.create(
            name="foo", platform=self.platform, description="foo bar", regex_line="^Back.*"
        )

    def test_add_line_removal_entry(self):
        """Test Add Object."""
        self.assertEqual(self.line_removal.name, "foo")
        self.assertEqual(self.line_removal.description, "foo bar")
        self.assertEqual(self.line_removal.regex_line, "^Back.*")

    def test_edit_line_removal_entry(self):
        """Test Edit Object."""
        new_name = "Line Remove"
        new_desc = "Testing Remove Running Config Line"
        new_regex = "^Running.*"
        self.line_removal.name = new_name
        self.line_removal.description = new_desc
        self.line_removal.regex_line = new_regex
        self.line_removal.save()

        self.assertEqual(self.line_removal.name, new_name)
        self.assertEqual(self.line_removal.description, new_desc)
        self.assertEqual(self.line_removal.regex_line, new_regex)


class ConfigReplaceModelTestCase(TestCase):
    """Test ConfigReplace Model."""

    def setUp(self):
        """Setup Object."""
        self.platform = Platform.objects.create(slug="cisco_ios")
        self.line_replace = ConfigReplace.objects.create(
            name="foo",
            platform=self.platform,
            description="foo bar",
            substitute_text=r"username(\S+)",
            replaced_text="<redacted>",
        )

    def test_add_line_replace_entry(self):
        """Test Add Object."""
        self.assertEqual(self.line_replace.name, "foo")
        self.assertEqual(self.line_replace.description, "foo bar")
        self.assertEqual(self.line_replace.substitute_text, r"username(\S+)")
        self.assertEqual(self.line_replace.replaced_text, "<redacted>")

    def test_edit_line_replace_entry(self):
        """Test Edit Object."""
        new_name = "Line Replacement"
        new_desc = "Testing Replacing Config Line"
        new_regex = r"password(\S+)"
        self.line_replace.name = new_name
        self.line_replace.description = new_desc
        self.line_replace.substitute_text = new_regex
        self.line_replace.save()

        self.assertEqual(self.line_replace.name, new_name)
        self.assertEqual(self.line_replace.description, new_desc)
        self.assertEqual(self.line_replace.substitute_text, new_regex)
        self.assertEqual(self.line_replace.replaced_text, "<redacted>")
