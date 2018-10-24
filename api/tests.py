"""CATH API Tests"""

import logging

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .models import SelectTemplateTask

LOG = logging.getLogger(__name__)
logging.basicConfig()

# Create your tests here.

class ModelTestCase(TestCase):
    """This class defines the test suite for the select template model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.query_id = "test_query_id"
        self.query_seq = "APKGAPKGAPKGAPKGAPKGAKPGAKGKPAKGPAKGPAKGAGPKAGPKAGPKAPGKAAGPK"
        self.template_task = SelectTemplateTask(
            query_id=self.query_id, query_sequence=self.query_seq)

    def test_model_can_create_a_task(self):
        """Test the tasklist model can create a task."""
        old_count = SelectTemplateTask.objects.count()
        self.template_task.save()
        new_count = SelectTemplateTask.objects.count()
        self.assertNotEqual(old_count, new_count)

class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.client = APIClient()
        self.template_task_data = {
            'query_id': "test_query_id",
            'query_sequence': "GPKASPGAPKAPKAPKGPKAGPAKGPKAPSKGPSAKPGKASPKGPAASPGK",
        }

    def test_api_can_create_a_task(self):
        """Test the api has task creation capability (after login)"""
        response = self.client.post(
            reverse('create_selecttemplate'),
            self.template_task_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_can_get_a_task(self):
        """Test the api can get a given tasklist."""
        task = SelectTemplateTask.objects.get()
        LOG.info("task: %s id:%s", task, task.id)
        response = self.client.get(
            reverse('details_selecttemplate',
                    kwargs={'pk': task.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, task.id)

    def test_api_can_delete_task(self):
        """Test the api can delete a task."""
        task = SelectTemplateTask.objects.get()
        response = self.client.delete(
            reverse('details_selecttemplate', kwargs={'pk': task.id}),
            format='json',
            follow=True)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
