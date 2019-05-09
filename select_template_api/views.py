"""CATH API Views"""

import logging

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (SelectTemplateQuerySerializer, SelectTemplateStatusSerializer,
                          SelectTemplateResultsSerializer, SelectTemplateHitSerializer)

from .models import SelectTemplateTask, SelectTemplateHit
from .models import STATUS_ERROR

LOG = logging.getLogger(__name__)


class TemplateTaskView(object):
    """Generic view for TemplateTask."""

    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateQuerySerializer
    lookup_field = 'uuid'


class SelectTemplateTaskHitsView(generics.RetrieveAPIView):
    """Generic view for TemplateTask."""

    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateHitSerializer
    lookup_field = 'uuid'

    def hits(self, request):

        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = SelectTemplateHitSerializer(queryset, many=True)
        return Response(serializer.data)


class SelectTemplateTaskCreateView(TemplateTaskView, generics.CreateAPIView):
    """This class defines the create behavior of our rest api."""

    # https://stackoverflow.com/a/4581997/821642
    def get_client_ip(self):
        """Returns the client IP"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0]
        else:
            client_ip = self.request.META.get('REMOTE_ADDR')
        return client_ip

    def perform_create(self, serializer):
        """Save the post data when creating a new task."""

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        object_data = serializer.validated_data

        query_id = object_data['query_id']
        query_sequence = object_data['query_sequence']
        client_ip = self.get_client_ip()
        LOG.debug("%s.perform_create: %s", str(self), str(serializer))

        try:
            obj = serializer.save(client_ip=client_ip)
            task_id = obj.submit_remote_task()
            serializer.save(remote_task_id=task_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as err:
            LOG.error("Caught error when submitting sequence (id:'%s', seq:'%s') to FunFHMMER: [%s] %s",
                      query_id, query_sequence, type(err), err)
            serializer.save(client_ip=client_ip, status=STATUS_ERROR,
                            message="Encountered an error when submitting sequence: {}".format(err))
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SelectTemplateTaskResultsView(TemplateTaskView, generics.RetrieveAPIView):
    """This class handles the http GET requests."""

    serializer_class = SelectTemplateResultsSerializer


class SelectTemplateTaskStatusView(TemplateTaskView, generics.RetrieveDestroyAPIView):
    """This class handles the http GET and DELETE requests."""

    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateStatusSerializer

    # overriding this so we can update the remote task whenever we
    # check the status of this task
    def get_object(self):
        queryset = self.get_queryset()
        filt = {}
        for field in [self.lookup_field]:
            filt[field] = self.kwargs[field]

        obj = get_object_or_404(queryset, **filt)
        self.check_object_permissions(self.request, obj)

        obj.update_remote_task()
        return obj
