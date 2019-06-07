"""CATH API Serializers"""

import logging

from rest_framework import serializers

from .models import SelectTemplateTask, SelectTemplateHit, SelectTemplateAlignment

LOG = logging.getLogger(__name__)


class SelectTemplateQuerySerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('uuid', 'status', 'message', 'query_id',
                  'query_sequence', 'date_created', 'date_modified', )
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


class SelectTemplateResultSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('uuid', 'status', 'message', 'date_created',
                  'date_modified', 'results_json',)
        read_only_fields = ('status', 'message', 'date_created',
                            'date_modified', 'results_json',)


class SelectTemplateHitSerializer(serializers.ModelSerializer):
    """Serializer to map the `SelectTemplateHit` model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateHit
        fields = ('uuid', 'task_uuid', 'date_created', 'query_range', 'query_range_sequence',
                  'ff_id', 'ff_name', 'is_resolved_hit',
                  'ff_cath_domain_count', 'ff_uniq_ec_count', 'ff_uniq_go_count',
                  'ff_seq_count', 'ff_dops_score',
                  'evalue', 'bitscore', )
        read_only_fields = fields


class SelectTemplateAlignmentSerializer(serializers.ModelSerializer):
    """Serializer to map the `SelectTemplateAlignment` model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateAlignment
        fields = ('uuid', 'hit_uuid', 'date_created', 'align_method', 'pdb_id',
                  'auth_asym_id', 'target_sequence', 'template_sequence', 'template_seqres_offset')
        read_only_fields = fields
