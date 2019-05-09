"""CATH API Serializers"""

import logging

from rest_framework import serializers

from .models import SelectTemplateTask, SelectTemplateHit

LOG = logging.getLogger(__name__)


class SelectTemplateQuerySerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('uuid', 'status', 'message', 'query_id',
                  'query_sequence', 'date_created', 'date_modified')
        read_only_fields = ('status', 'message',
                            'date_created', 'date_modified',)

    def create(self, validated_data):
        """
        Create and return a new `SelectTemplateTask` instance, given the validated data.
        """
        LOG.info("%s.create(%s)", __name__, str(validated_data))
        return SelectTemplateTask.objects.create(**validated_data)


class SelectTemplateStatusSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('uuid', 'status', 'message',
                  'date_created', 'date_modified',)
        read_only_fields = ('status', 'message',
                            'date_created', 'date_modified',)


class SelectTemplateResultsSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('uuid', 'status', 'message', 'date_created',
                  'date_modified', 'results_json',)
        read_only_fields = ('status', 'message', 'date_created',
                            'date_modified', 'results_json',)


class SelectTemplateHitSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateHit
        fields = ('uuid', 'task_uuid', 'date_created', 'funfam_id', 'funfam_name', 'pdb_id',
                  'auth_asym_id', 'template_sequence', 'template_seqres_offset')
        read_only_fields = fields
