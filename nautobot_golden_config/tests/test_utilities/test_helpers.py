"""Unit tests for nautobot_golden_config utilities helpers."""

import unittest
from unittest.mock import patch, Mock
from django.conf import settings
from nornir_nautobot.exceptions import NornirNautobotException
from jinja2.exceptions import TemplateError
from nautobot_golden_config.utilities.helper import (
    get_job_filter,
    null_to_empty,
    verify_global_settings,
    check_jinja_template,
)

# pylint: disable=no-self-use


class HelpersTest(unittest.TestCase):
    """Test Helper Functions."""

    def setUp(self):
        """Setup default settings for each test."""
        settings.PLUGINS_CONFIG["nautobot_golden_config"]["allowed_os"] = ["all"]

    @patch("nautobot_golden_config.utilities.helper.Platform")
    def test_get_job_filter_data_null_os_all(self, mock_platform):
        """Test Platform called when os is "all"."""
        get_job_filter(data=None)
        mock_platform.objects.values_list.assert_called_once()

    @patch("nautobot_golden_config.utilities.helper.Platform")
    def test_get_job_filter_data_null_os_not_all(self, mock_platform, mock_allowed):
        """Test Platform called when os is NOT "all"."""
        mock_allowed.return_value = ["cisco_ios"]
        get_job_filter(data=None)
        mock_platform.objects.values_list.assert_not_called()

    @patch("nautobot_golden_config.utilities.helper.Device")
    @patch("nautobot_golden_config.utilities.helper.DeviceFilterSet")
    def test_get_job_filter_data_null_return(self, mock_return, mock_device):
        """Test Return value when no data provided."""
        get_job_filter(data=None)
        mock_return.assert_called_once()
        mock_device.objects.filter.assert_called_once()

    @patch("nautobot_golden_config.utilities.helper.Device")
    @patch("nautobot_golden_config.utilities.helper.DeviceFilterSet")
    def test_get_job_filter_with_data_return(self, mock_return, mock_device):
        """Test Return value when data is provided."""
        get_job_filter(data={"test-key": "test"})
        mock_return.assert_called_once()
        mock_device.objects.filter.assert_called_once()

    @patch("nautobot_golden_config.utilities.helper.getattr")
    def test_verify_global_settings_exception(self, mock_getattr):
        """Validate exception if not getattr()."""
        log_mock = Mock()
        with self.assertRaises(NornirNautobotException):
            mock_getattr.return_value = None
            verify_global_settings(log_mock, Mock(), "test-attr")

    def test_null_to_empty_null(self):
        """Ensure None returns with empty string."""
        result = null_to_empty(None)
        self.assertEqual(result, "")

    def test_null_to_empty_val(self):
        """Ensure if not None input is returned."""
        result = null_to_empty("test")
        self.assertEqual(result, "test")

    def test_check_jinja_template_success(self):
        """Simple success test to return template."""
        worker = check_jinja_template("obj", "logger", "fake-template-name")
        self.assertEqual(worker, "fake-template-name")

    def test_check_jinja_template_exceptions_undefined(self):
        """Use fake obj key to cause UndefinedError from Jinja2 Template."""
        log_mock = Mock()
        with self.assertRaises(NornirNautobotException):
            check_jinja_template("test-obj", log_mock, "{{ obj.fake }}")

    def test_check_jinja_template_exceptions_syntaxerror(self):
        """Use invalid templating to cause TemplateSyntaxError from Jinja2 Template."""
        log_mock = Mock()
        with self.assertRaises(NornirNautobotException):
            check_jinja_template("test-obj", log_mock, "{{ obj.fake }")

    @patch("nautobot_golden_config.utilities.helper.Template")
    def test_check_jinja_template_exceptions_templateerror(self, template_mock):
        """Cause issue to cause TemplateError form Jinja2 Template."""
        log_mock = Mock()
        with self.assertRaises(NornirNautobotException):
            template_mock.side_effect = TemplateError
            template_render = check_jinja_template("test-obj", log_mock, "template")
            self.assertEqual(template_render, TemplateError)
            template_mock.assert_called_once()
