"""
Run tasks in the background with Celery
"""
from __future__ import absolute_import, unicode_literals
import time

import logging
import celery

from celery import shared_task
from celery.utils.log import get_task_logger

LOG = get_task_logger(__name__)

CHECK_REMOTE_SLEEP = 5


@celery.signals.after_setup_logger.connect
def on_after_setup_logger(**kwargs):
    logger = logging.getLogger('celery')
    logger.propagate = True
    logger = logging.getLogger('celery.app.trace')
    logger.propagate = True


@shared_task
def process_select_template_task(task_uuid):

    from select_template_api import models
    from select_template_api import errors as err

    select_template_task = models.SelectTemplateTask.objects.get(
        uuid=task_uuid)

    LOG.info("START %s [status=%s]",
             select_template_task.uuid, select_template_task.status)

    # keep going until remote task is complete
    is_remote_task_complete = False
    while not is_remote_task_complete:
        is_remote_task_complete = select_template_task.update_remote_task()
        time.sleep(CHECK_REMOTE_SLEEP)

    LOG.info("REMOTE_IS_COMPLETE %s [status=%s]",
             select_template_task.uuid, select_template_task.status)

    if select_template_task.status == models.STATUS_ERROR:
        raise err.TaskInErrorStateError(
            'An error has occurred when processing this task: cannot continue')

    LOG.info("CREATE_RESOLVED_HITS %s [status=%s]",
             select_template_task.uuid, select_template_task.status)

    try:
        select_template_task.create_resolved_hits()
    except err.NoResultsDataError:
        msg = 'found no results when searching query sequence'
        LOG.warning(msg)
    except Exception as e:
        msg = 'encountered {} when trying to create resolved hits: {}'.format(
            type(e), str(e)[:250])
        LOG.error(msg)
        select_template_task.status = models.STATUS_ERROR
        select_template_task.message = msg
        select_template_task.save()
        raise

    hits = models.SelectTemplateHit.objects.filter(
        task_uuid=select_template_task.uuid)

    LOG.info("HITS %s (%d)",
             select_template_task.uuid, len(hits))

    select_template_task.status = models.STATUS_SUCCESS
    select_template_task.message = 'Created {} hits'.format(len(hits))
    select_template_task.save()

    LOG.info("DONE %s", select_template_task.uuid)
