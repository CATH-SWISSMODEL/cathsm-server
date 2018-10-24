"""CATH API Views"""

import logging

from django.shortcuts import render

from rest_framework import generics

from .serializers import SelectTemplateQuerySerializer, SelectTemplateResultsSerializer
from .models import SelectTemplateTask

LOG = logging.getLogger(__name__)

class SelectTemplateTaskCreateView(generics.CreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateQuerySerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new task."""

        LOG.info("%s.perform_create: %s", str(self), str(serializer))
        serializer.save()

class SelectTemplateTaskDetailsView(generics.RetrieveDestroyAPIView):
    """This class handles the http GET and DELETE requests."""

    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateResultsSerializer
