"""View for Golden Config APIs."""
import json

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..models import GoldenConfigSettings, ConfigRemove, ConfigReplace
from ..utilities.graphql import graph_ql_query
from .serializer import GraphQLSerializer, LineRemoveSerializer, LineReplaceSerializer


class SOTAggDeviceDetailView(APIView):
    """Detail REST API view showing graphql, with a potential "transformer" of data on a specific device."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Get method serialize for a dictionary to json response."""
        device = kwargs["device"]
        global_settings = GoldenConfigSettings.objects.first()
        status_code, data = graph_ql_query(request, device, global_settings.sot_agg_query)
        data = json.loads(json.dumps(data))
        return Response(GraphQLSerializer(data=data).initial_data, status=status_code)


class ConfigRemoveViewSet(ModelViewSet):  # pylint:disable=too-many-ancestors
    """API viewset for interacting with ConfigRemove objects."""

    queryset = ConfigRemove.objects.all()
    serializer_class = LineRemoveSerializer


class ConfigReplaceViewSet(ModelViewSet):  # pylint:disable=too-many-ancestors
    """API viewset for interacting with ConfigReplace objects."""

    queryset = ConfigReplace.objects.all()
    serializer_class = LineReplaceSerializer
