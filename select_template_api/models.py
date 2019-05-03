"""CATH API Models"""

import logging
import uuid

from django.db import models
#from django.contrib.auth.models import User

from cathpy.funfhmmer import Client

LOG = logging.getLogger(__name__)

# constants
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_ERROR = "error"
STATUS_SUCCESS = "success"
STATUS_UNKNOWN = "unknown"
STATUS_CHOICES = ((st, st) for st in (
    STATUS_UNKNOWN, STATUS_QUEUED, STATUS_RUNNING, STATUS_ERROR, STATUS_SUCCESS))

# Create your models here.


class SelectTemplateTask(models.Model):
    """This class represents the tasklist model."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    query_id = models.CharField(max_length=50, blank=False, unique=False)
    query_sequence = models.CharField(
        max_length=2000, blank=False, unique=False)

    #user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    message = models.CharField(max_length=150)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    results_json = models.CharField(max_length=100000, blank=True)

    client_ip = models.GenericIPAddressField(default="0.0.0.0")

    remote_task_id = models.CharField(max_length=50, blank=True)

    api_client = Client()

    def __str__(self):
        """Return a human readable representation of this instance."""
        return "[{}] uuid: {}, status: {}, remote_task_id: {}, started: {}, last_updated: {}, client_ip: {}".format(
            self.pk, self.uuid, self.status, self.remote_task_id, self.date_created, self.date_modified, self.client_ip)

    @property
    def query_fasta(self):
        """Retrieves the query sequence in FASTA format"""

        return ">{}\n{}\n".format(self.query_id, self.query_sequence)

    def submit_remote_task(self):
        """Submits the task to the remote server"""

        LOG.info("submit_remote_task: %s", self.query_id)
        submit_response = self.api_client.submit(self.query_fasta)
        remote_task_id = submit_response.task_id
        LOG.info("submit_remote_task.response: (%s) %s %s", type(
            submit_response), str(submit_response.__dict__), remote_task_id)
        self.remote_task_id = remote_task_id
        self.save()
        return remote_task_id

    def update_remote_task(self):
        """Updates the task by performing a status request on the remote server"""

        LOG.info("update_remote_task: %s '%s'",
                 self.query_id, self.remote_task_id)

        if not self.remote_task_id:
            LOG.info("update_remote_task: %s no_remote_task_id", self)
            return

        if self.status in [STATUS_SUCCESS, STATUS_ERROR]:
            LOG.info("update_remote_task: %s task_already_complete", self.status)
            return

        try:
            check_response = self.api_client.check(self.remote_task_id)
        except Exception as e:
            LOG.error(
                "encountered error when checking remote task: (%s) %s", type(e), e)
            raise
        msg = check_response.message

        # make these checks explicit so we can add extra hooks to each stage
        if msg == 'done':
            results_response = self.api_client.results(self.remote_task_id)

            try:
                self.results_json = results_response.as_json()
            except Exception as e:
                LOG.error(
                    "encountered an error when outputting results as JSON: [%s] %s", type(e), e)
                raise

            self.status = STATUS_SUCCESS

        elif msg == 'queued':
            self.status = STATUS_QUEUED
        elif msg == 'running':
            self.status = STATUS_RUNNING
        elif msg == 'error':
            self.status = STATUS_ERROR
        else:
            self.status = STATUS_ERROR
            self.message = "CheckResponse returned unexpected message '{}'".format(
                msg)

        self.save()
