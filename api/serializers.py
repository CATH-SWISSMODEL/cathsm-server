"""CATH API Serializers"""

import logging

from rest_framework import serializers

from .models import SelectTemplateTask

LOG = logging.getLogger(__name__)

class SelectTemplateQuerySerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('query_id', 'query_sequence', 'task_id')
        read_only_fields = ('status', 'message', 'date_created', 'date_modified', 'results',)

    def create(self, validated_data):
        """
        Create and return a new `SelectTemplateTask` instance, given the validated data.
        """
        LOG.info("%s.create(%s)", __name__, str(validated_data))
        return SelectTemplateTask.objects.create(**validated_data)


class SelectTemplateResultsSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('task_id', 'status', 'message', 'date_created', 'date_modified', 'results',)
        read_only_fields = ('status', 'message', 'date_created', 'date_modified', 'results',)
