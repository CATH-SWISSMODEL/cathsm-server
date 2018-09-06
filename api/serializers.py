# api/serializers.py

from .models import SelectTemplateTask
from rest_framework import serializers

class SelectTemplateQuerySerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('fasta', 'task_id')
        read_only_fields = ('status', 'message', 'date_created', 'date_modified', 'results')

class SelectTemplateResultsSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format"""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = SelectTemplateTask
        fields = ('task_id', 'status', 'message', 'date_created', 'date_modified', 'results')
        read_only_fields = ('status', 'message', 'date_created', 'date_modified', 'results')

