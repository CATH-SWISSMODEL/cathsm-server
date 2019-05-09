"""CATH API Models"""

import logging
import json
import uuid

from django.db import models
#from django.contrib.auth.models import User

import requests

from cathpy.funfhmmer import Client
from cathpy.models import Scan, ScanHit, Segment
from cathpy.align import Align, Sequence

from .errors import NoStructureDomainsError

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


class SelectTemplateHit(models.Model):
    """This class represents a particular hit from a given task."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    task_uuid = models.UUIDField(editable=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)

    query_id = models.CharField(max_length=50, blank=False, unique=False)
    query_sequence = models.CharField(
        max_length=2000, blank=False, unique=False)
    query_range = models.CharField(max_length=100, blank=False, unique=False)

    funfam_id = models.CharField(max_length=100, blank=False, unique=False)
    funfam_name = models.CharField(max_length=500, blank=False, unique=False)

    pdb_id = models.CharField(max_length=4, blank=False, unique=False)
    auth_asym_id = models.CharField(max_length=4, blank=False, unique=False)
    template_sequence = models.CharField(
        max_length=2000, blank=False, unique=False)
    template_seqres_offset = models.IntegerField(
        default=0, unique=False)

    @classmethod
    def get_funfam_alignment(cls, *, funfam_id, cath_version):
        """
        Retrieves the FunFam alignment

        TODO: 
            move this functionality to :class:`cathpy`
        """

        # http://www.cathdb.info/version/v4_2_0/superfamily/1.10.8.10/funfam/10980/files/stockholm?task_id=&max_sequences=200&onlyseq=1

        # TODO: move to cathpy
        sfam_id, _, ff_num = funfam_id.split('-')
        ff_url = '{base_url}/version/{version}/superfamily/{sfam_id}/funfam/{ff_num}/files/stockholm'.format(
            base_url='http://www.cathdb.info',
            version=cath_version,
            sfam_id=sfam_id,
            ff_num=ff_num,
        )
        res = requests.get(ff_url)
        res.raise_for_status()
        aln = Align.new_from_stockholm(res.content)
        return aln

    @classmethod
    def create_from_scan_hit(cls, *, scan_hit, cath_version, task_uuid, task_query_id, task_query_sequence):

        assert isinstance(scan_hit, ScanHit)

        task_seq = Sequence(task_query_id, task_query_sequence)

        query_segs = [Segment(hsp.query_start, hsp.query_end)
                      for hsp in scan_hit.hsps]

        hit_seq = task_seq.apply_segments(query_segs)

        query_id = hit_seq.id
        query_sequence = hit_seq.seq
        funfam_id = scan_hit.match_name
        funfam_name = scan_hit.match_description

        ff_aln = cls.get_funfam_alignment(
            funfam_id=funfam_id, cath_version=cath_version)

        dom_seqs = [seq for seq in ff_aln.sequences if seq.is_cath_domain]

        if not dom_seqs:
            raise NoStructureDomainsError(
                "no CATH domains found in FunFam alignment: {}".format(funfam_id))

        best_domain_seq = SelectBlastRep(align=ff_aln, ref_seq=hit_seq).run()

        pdb_id = '1XXX'
        auth_asym_id = 'A'
        template_sequence = 'CHANGEME'
        template_seqres_offset = 24

        hit = SelectTemplateHit(
            task_uuid=self.uuid,
            query_id=query_id,
            query_sequence=query_sequence,
            funfam_id=funfam_id,
            funfam_name=funfam_name,
            pdb_id=pdb_id,
            auth_asym_id=auth_asym_id,
            template_sequence=template_sequence,
            template_seqres_offset=template_seqres_offset,
        )

        return hit


class SelectTemplateTask(models.Model):
    """This class represents the task model."""

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

    def get_resolved_hits(self):

        results_data = json.loads(self.results_json)
        cath_version = results_data['cath_version']
        scan_data = results_data['funfam_resolved_scan']
        scan = Scan(**scan_data)

        if len(scan.results) != 1:
            raise Exception("expected exactly 1 result in scan, got {} (scan:{})".format(
                len(scan.results), scan))
        result = scan.results[0]
        for scan_hit in result.hits:
            hit = SelectTemplateHit.create_from_scan_hit(scan_hit)
