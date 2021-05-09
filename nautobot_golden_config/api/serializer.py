"""REST API serializer capabilities for graphql plugin."""

from rest_framework import serializers

from nautobot_golden_config.models import ConfigRemove, ConfigReplace


class GraphQLSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Serializer for a GraphQL object."""

    data = serializers.JSONField()


class LineRemoveSerializer(serializers.ModelSerializer):
    """Serializer for Line Removal object."""

    class Meta:
        """Set Meta Data for Line Removal, will serialize all fields."""

        model = ConfigRemove
        fields = "__all__"


class LineReplaceSerializer(serializers.ModelSerializer):
    """Serializer for Line Replacement object."""

    class Meta:
        """Set Meta Data for Line Replacements, will serialize all fields."""

        model = ConfigReplace
        fields = "__all__"
