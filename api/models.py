"""CATH API Models"""

import hashlib
import logging

from django.db import models

LOG = logging.getLogger(__name__)

# constants
STATUS_INITIALISED = "initialised"
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

    query_id = models.CharField(max_length=50, blank=False, unique=False)
    query_sequence = models.CharField(max_length=2000, blank=False, unique=False)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_INITIALISED)
    message = models.CharField(max_length=150)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    results = models.CharField(max_length=5000, blank=True)

    ip = models.GenericIPAddressField(default="0.0.0.0")

    @property
    def task_id(self):
        """returns unique key from input fields"""
        md5 = hashlib.md5()
        md5.update(str(self.query_id).encode('utf-8'))
        md5.update(str(self.query_sequence).encode('utf-8'))
        task_id = md5.hexdigest()
        return task_id

    def __str__(self):
        """Return a human readable representation of this instance."""
        return "[{}] status:{}, started:{}, last_updated:{}".format(
            self.task_id, self.status, self.date_created, self.date_modified)
