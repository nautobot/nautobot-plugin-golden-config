"""Unit tests for nautobot_golden_config utilities graphql."""

from unittest.mock import patch

from nautobot.utilities.testing import TestCase
from nautobot.dcim.models import Device
from nautobot_golden_config.utilities.graphql import graph_ql_query

# pylint: disable=no-self-use


class GraphQLTest(TestCase):
    """Test for the GraphQL Queries."""

    @patch("nautobot_golden_config.utilities.graphql.graph_ql_query")
    def test_graph_ql_query(self, mock):
        """Make sure graph_ql_query is called correctly."""
        mock("request", Device.objects.get(name="ams-edge-01"), '{devices(name:"ams-edge-01"){id}}')
        mock.assert_called_with("request", Device.objects.get(name="ams-edge-01"), '{devices(name:"ams-edge-01"){id}}')

    def test_bad_graph_ql_query_syntax(self):
        """Ensure invalid GraphQL query results with Error."""
        result = graph_ql_query("request", Device.objects.get(name="ams-edge-01"), "not valid query")
        self.assertEqual(result[0], 400)
        self.assertTrue(result[1]["error"])
        self.assertRegex(result[1].get("error"), r"Syntax Error GraphQL.*")
