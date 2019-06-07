"""CATH API Views"""

import logging

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (SelectTemplateQuerySerializer,
                          SelectTemplateStatusSerializer,
                          SelectTemplateResultSerializer,
                          SelectTemplateHitSerializer,
                          SelectTemplateAlignmentSerializer)

from .models import SelectTemplateTask, SelectTemplateHit, SelectTemplateAlignment
from .models import STATUS_ERROR

from .tasks import process_select_template_task

LOG = logging.getLogger(__name__)


class SelectTemplateAlignmentsView(generics.ListAPIView):
    """Generic view for non-resolved hits from template scan."""

    serializer_class = SelectTemplateAlignmentSerializer

    def get_queryset(self):
        hit_uuid = self.kwargs['hit_uuid']
        qs = SelectTemplateAlignment.objects.filter(
            hit_uuid=hit_uuid)
        return qs


class SelectTemplateHitsView(generics.ListAPIView):
    """Generic view for non-resolved hits from template scan."""

    serializer_class = SelectTemplateHitSerializer

    def get_queryset(self):
        task_uuid = self.kwargs['task_uuid']
        qs = SelectTemplateHit.objects.filter(
            is_resolved_hit=False, task_uuid=task_uuid)
        return qs

    def hits(self, request):
        """Returns serialized hits"""
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = SelectTemplateHitSerializer(queryset, many=True)
        return Response(serializer.data)


class SelectTemplateResolvedHitsView(generics.ListAPIView):
    """Generic view for resolved hits from template scan."""

    serializer_class = SelectTemplateHitSerializer

    def get_queryset(self):
        task_uuid = self.kwargs['task_uuid']
        qs = SelectTemplateHit.objects.filter(
            is_resolved_hit=True, task_uuid=task_uuid)
        return qs

    def hits(self, request):
        """Returns serialized hits"""

        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = SelectTemplateHitSerializer(queryset, many=True)
        return Response(serializer.data)


class TemplateTasksView(object):
    """Generic view for TemplateTask."""

    queryset = SelectTemplateTask.objects.all()
    serializer_class = SelectTemplateQuerySerializer
    lookup_field = 'uuid'


class SelectTemplateTasksCreateView(TemplateTasksView, generics.CreateAPIView):
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
            task = serializer.save(client_ip=client_ip)
            LOG.info(
                "Submitting remote task to FunFHMMER server... task[%s]: %s", type(task), task)
            remote_task_id = task.submit_remote_task()
            LOG.info("    ... done (remote_task_id=%s)", remote_task_id)
            task.remote_task_id = remote_task_id
            LOG.info("about to save task: %s",
                     SelectTemplateTask.objects.get(uuid=task.uuid))
            task.save()
            LOG.info("saved task: %s",
                     SelectTemplateTask.objects.get(uuid=task.uuid))
            LOG.info("Processing with delayed task")
            process_select_template_task.delay(task.uuid)
            LOG.info(" ... task running")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as err:
            LOG.error("Caught error when submitting sequence (id:'%s', seq:'%s') to FunFHMMER: [%s] %s",
                      query_id, query_sequence, type(err), err)
            serializer.save(client_ip=client_ip, status=STATUS_ERROR,
                            message="Encountered an error when submitting sequence: {}".format(err))
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SelectTemplateTasksResultView(TemplateTasksView, generics.RetrieveAPIView):
    """This class handles the http GET requests."""

    serializer_class = SelectTemplateResultSerializer


class SelectTemplateTasksStatusView(TemplateTasksView, generics.RetrieveDestroyAPIView):
    """This class handles the http GET and DELETE requests."""

    serializer_class = SelectTemplateStatusSerializer
