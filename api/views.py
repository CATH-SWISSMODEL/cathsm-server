from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from .serializers import SelectTemplateQuerySerializer, SelectTemplateResultsSerializer
from .models import SelectTemplateTask

class SelectTemplateTaskCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateQuerySerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new task."""
        serializer.save()

class SelectTemplateTaskDetailsView(generics.RetrieveDestroyAPIView):
    """This class handles the http GET and DELETE requests."""

    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateResultsSerializer
