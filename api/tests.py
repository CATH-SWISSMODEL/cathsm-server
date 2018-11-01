"""CATH API Tests"""

import logging
import time

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework import status

from .models import SelectTemplateTask

from .models import STATUS_UNKNOWN, STATUS_QUEUED, STATUS_RUNNING, STATUS_ERROR, STATUS_SUCCESS

LOG = logging.getLogger(__name__)
#logging.basicConfig()

# Create your tests here.

DEFAULT_QUERY_ID = "test_query_id"
DEFAULT_QUERY_SEQ = "MNDFHRDTWAEVDLDAIYDNVANLRRLLPDDTHIMAVVKANAYGDVQVARTALEAGASRLAVAFLDEALALREKGIEAPILVLGASRPADAALAAQQRIALTVFRSDWLEEASALYSGPFPIHFHLKMDTGMGRLGVKDEEETKRIVALIERHPHFVLEGVYTHFATADEVNTDYFSYQYTRFLHMLEWLPSRPPLVHCANSAASLRFPDRTFNMVRFGIAMYGLAPSPGIKPLLPYPLKEAFSLHSRLVHVKKLQPGEKVSYGATYTAQTEEWIGTIPIGYADGWLRRLQH"

class ModelTestCase(TestCase):
    """This class defines the test suite for the select template model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.query_id = DEFAULT_QUERY_ID
        self.query_seq = DEFAULT_QUERY_SEQ
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

        # test user
        self.testuser_auth = {
            'username': 'testuser',
            'password': '12345',
        }

        # example task data
        self.template_task_data = {
            'query_id': DEFAULT_QUERY_ID,
            'query_sequence': DEFAULT_QUERY_SEQ,
        }

        # create user
        self.testuser = User.objects.create_user(**self.testuser_auth)
        self.assertEqual(self.testuser.get_username(), 'testuser')

        # create task object
        self.template_task = SelectTemplateTask(**self.template_task_data)

    def submit_default_task_with_auth(self):
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token '+token)
        response = self.client.post(
            reverse('api:create_selecttemplate'),
            self.template_task_data,
            format="json")
        
        return response

    def check_task(self, task_uuid):

        self.assertTrue(task_uuid)

        response = self.client.get(
            reverse('api:status_selecttemplate', kwargs={'uuid': task_uuid}),
            format="json")

        return response

    def get_task_results_csv(self, task_uuid):

        self.assertTrue(task_uuid)

        response = self.client.get(
            reverse('api:results_selecttemplate', kwargs={'uuid': task_uuid}),
            format="json")

        results_data = response.json()
        # LOG.info("results_data: %s", results_data)

        return results_data['results_csv']


    def test_api_create_task_requires_auth(self):
        """Test the api cannot create tasks without authentication"""

        self.assertEqual(reverse('api:create_selecttemplate'), '/api/select-template/')

        response = self.client.post(
            reverse('api:create_selecttemplate'),
            self.template_task_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def get_auth_token(self):

        token_response = self.client.post(
            reverse('api:auth_token'),
            self.testuser_auth,
            format="json"
        )

        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        token = token_response.json()['token']

        LOG.debug("token_response.token: (%d) %s", len(token), token)
        self.assertRegex(token, r'^[0-9a-f]{40}$')

        return token

    def test_api_create_task_with_auth(self):
        """Test the api can create a task after auth"""
        
        tasks_before = SelectTemplateTask.objects.count()

        create_response = self.submit_default_task_with_auth()

        LOG.info("create.response.json: %s", create_response.json())

        json_data = create_response.json()
        self.assertIn('uuid', json_data)
        task_uuid = json_data['uuid']

        tasks_after = SelectTemplateTask.objects.count()

        self.assertEqual(tasks_after, tasks_before + 1)

        task_from_db = SelectTemplateTask.objects.get(uuid=task_uuid)

        self.assertEqual(task_from_db.query_sequence, self.template_task_data['query_sequence'])

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

    def test_api_can_get_a_task(self):
        """Test the api can get an existing task."""

        # add test task to database
        task = self.template_task
        task.save()

        task_from_db = SelectTemplateTask.objects.get(uuid=task.uuid)
        self.assertEqual(task_from_db.uuid, task.uuid)

        # get task via API
        response = self.check_task(task.uuid)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        LOG.info("get.response.json: %s", response.json())

        self.assertContains(response, task.id)

        # remove test task from database
        task.delete()


    def test_api_can_delete_task(self):
        """Test the api can delete a task."""

        task = self.template_task
        task.save()

        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token '+token)

        response = self.client.delete(
            reverse('api:status_selecttemplate', kwargs={'uuid': task.uuid}),
            format='json',
            follow=True)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_api_can_complete_task(self):
        """Test the api can create a task then retrieve results."""

        res_create = self.submit_default_task_with_auth()

        task_uuid = res_create.json()['uuid']

        check_counter = 0
        max_checks = 100
        while True:
            check_counter += 1
            if check_counter >= max_checks:
                raise Exception("Exceeded maximum number of loops ({}) while waiting for task to complete".format(max_checks))

            res_check = self.check_task(task_uuid)
            res_check_data = res_check.json()

            if 'status' not in res_check_data:
                raise Exception("check response does not have 'status' field: %s", res_check_data)

            task_status = res_check_data['status']
            if task_status in [STATUS_QUEUED, STATUS_RUNNING]:
                pass
            elif task_status == STATUS_ERROR:
                raise Exception("check response has reported error state {}".format(res_check))
            elif task_status == STATUS_SUCCESS:
                break
            else:
                raise Exception("check response reported unknown status '{}'".format(task_status))

            time.sleep(1)

        res_results = self.get_task_results_csv(task_uuid)
        self.assertTrue(res_results)


    def tearDown(self):
        """Remove testing data, users, etc"""

        self.testuser.delete()

