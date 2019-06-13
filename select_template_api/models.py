"""
CATH API Models

::
    SelectTemplateTask [query_sequence]
        -> SelectTemplateHit [query_region -> match_funfam]
            -> SelectTemplateAlignment [match_funfam -> structural_rep]

"""

import logging
import io
import json
import re
import uuid

from django.db import models
#from django.contrib.auth.models import User

import requests

from cathpy.funfhmmer import Client
from cathpy.models import Scan, ScanHit, Segment
from cathpy.align import Align, Sequence

import cathpy.error

from . import errors as err
from .select_template import SelectBlastRep, MafftAddSequence

LOG = logging.getLogger(__name__)

# constants
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_ERROR = "error"
STATUS_SUCCESS = "success"
STATUS_UNKNOWN = "unknown"
STATUS_CHOICES = ((st, st) for st in (
    STATUS_UNKNOWN, STATUS_QUEUED, STATUS_RUNNING, STATUS_ERROR, STATUS_SUCCESS))

STATUS_TYPES_COMPLETED = [STATUS_SUCCESS, STATUS_ERROR]

ALIGN_METHOD_MAFFT = "mafft"
ALIGN_METHOD_HHSEARCH = "hhsearch"
ALIGN_METHOD_CHOICES = ((st, st) for st in (
    ALIGN_METHOD_MAFFT, ))

# Create your models here.


class SelectTemplateAlignment(models.Model):
    """
    Represents a query-template alignment from a `SelectTemplate` task
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    hit_uuid = models.UUIDField(editable=False, blank=False)

    date_created = models.DateTimeField(auto_now_add=True)
    align_method = models.CharField(
        max_length=20, choices=ALIGN_METHOD_CHOICES, default=ALIGN_METHOD_MAFFT)

    pdb_id = models.CharField(max_length=4, blank=False, unique=False)
    auth_asym_id = models.CharField(max_length=4, blank=False, unique=False)
    target_sequence = models.CharField(
        max_length=2000, blank=False, unique=False)
    template_sequence = models.CharField(
        max_length=2000, blank=False, unique=False)
    template_seqres_offset = models.IntegerField(
        default=0, unique=False)


class SelectTemplateHit(models.Model):
    """
    Represents a scan hit from a `SelectTemplate` task.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    task_uuid = models.UUIDField(editable=False, blank=False)
    query_range = models.CharField(max_length=100, blank=False, unique=False)
    query_range_sequence = models.CharField(
        max_length=5000, blank=False, unique=False)
    ff_id = models.CharField(max_length=100, blank=False, unique=False)
    ff_name = models.CharField(max_length=500, blank=False, unique=False)
    is_resolved_hit = models.BooleanField(blank=False, default=False)

    ff_cath_domain_count = models.IntegerField(null=True)
    ff_uniq_ec_count = models.IntegerField(null=True)
    ff_uniq_go_count = models.IntegerField(null=True)
    ff_seq_count = models.IntegerField(null=True)
    ff_dops_score = models.IntegerField(null=True)

    evalue = models.FloatField(null=True)
    bitscore = models.FloatField(null=True)

    @classmethod
    def get_funfam_alignment(cls, *, funfam_id, cath_version):
        """
        Retrieves the FunFam alignment

        TODO:
            move this functionality to :class:`cathpy`
        """

        # http://www.cathdb.info/version/v4_2_0/superfamily/1.10.8.10/funfam/10980/files/stockholm?task_id=&max_sequences=200&onlyseq=1

        # TODO: move to cathpy
        try:
            sfam_id, _, ff_num = re.split(r'[\-/]', funfam_id)
        except ValueError as e:
            LOG.error('failed to parse funfam id "%s": %s', funfam_id, e)
            raise

        ff_url = '{base_url}/version/{version}/superfamily/{sfam_id}/funfam/{ff_num}/files/stockholm'.format(
            base_url='http://www.cathdb.info',
            version=cath_version,
            sfam_id=sfam_id,
            ff_num=ff_num,
        )
        res = requests.get(ff_url)
        res.raise_for_status()
        sto_io = io.StringIO(res.content.decode('utf-8'))
        aln = Align.new_from_stockholm(sto_io)
        return aln

    @classmethod
    def create_from_scan_hit(cls, *, scan_hit, cath_version, task_uuid, is_resolved_hit):
        """
        Creates a new :class:`SelectTemplateHit` from a :class:`cathpy.model.ScanHit`

        This will fetch the matching FunFam alignment, align the matching
        region of query sequence to this alignment (`MAFFT`). Then it will 
        use `BLAST` to find the closest structural sequence within the FunFam,
        isolate the pairwise alignment of the 'best' BLAST hit and save it as
        :class:`SelectTemplateAlignment`.

        Args:
            scan_hit (:class:`cathpy.model.ScanHit`): hit from sequence scan
            cath_version (str): CATH version
            task_uuid (str): unique id of parent task

        Returns:
            hit (:class:`SelectTemplateHit`): select template hit model
        """

        assert isinstance(scan_hit, ScanHit)

        funfam_id = scan_hit.match_name
        funfam_name = scan_hit.match_description

        if len(scan_hit.hsps) > 1:
            raise err.DiscontinuousDomainError("""
                Hit '{}' has more than one ({}) HSPs, which means it is probably a 
                discontinuous domain (this pipeline is not currently able to process 
                discontinuous domains).
                """.format(scan_hit.match_name, len(scan_hit.hsps)))

        scan_hsp = scan_hit.hsps[0]
        hit_evalue = scan_hsp.evalue
        hit_bitscore = scan_hsp.score

        task = SelectTemplateTask.objects.get(uuid=task_uuid)
        if not task:
            raise Exception(
                'failed to find task with task_uuid="{}"'.format(task_uuid))

        task_seq = Sequence(task.query_id, task.query_sequence)

        query_segs = [Segment(hsp.query_start, hsp.query_end)
                      for hsp in scan_hit.hsps]

        query_range_sequence = task_seq.apply_segments(query_segs)

        ff_aln = cls.get_funfam_alignment(
            funfam_id=funfam_id, cath_version=cath_version)

        ff_aln_meta = ff_aln.get_meta_summary()

        ff_uniq_ec_count = len(
            ff_aln_meta.ec_term_counts) if ff_aln_meta.ec_term_counts else 0
        ff_uniq_go_count = len(
            ff_aln_meta.go_term_counts) if ff_aln_meta.go_term_counts else 0
        ff_cath_domain_count = ff_aln_meta.cath_domain_count
        ff_seq_count = ff_aln_meta.seq_count
        ff_dops_score = ff_aln_meta.dops_score

        # cathpy.seq.is_cath_domain needs fixing...
        is_cath_domain = re.compile('^[0-9][a-zA-Z0-9]{3}[A-Z][0-9]{2}\b')
        dom_seqs = [seq for seq in ff_aln.sequences if is_cath_domain.match(seq.uid)]

        LOG.info('Creating entry in SelectTemplateHit')
        hit_args = {
            'task_uuid': task_uuid,
            'query_range': query_range_sequence.seginfo,
            'query_range_sequence': query_range_sequence.seq,
            'ff_id': funfam_id,
            'ff_name': funfam_name,
            'is_resolved_hit': is_resolved_hit,
            'ff_cath_domain_count': ff_cath_domain_count,
            'ff_seq_count': ff_seq_count,
            'ff_uniq_ec_count': ff_uniq_ec_count,
            'ff_uniq_go_count': ff_uniq_go_count,
            'ff_dops_score': ff_dops_score,
            'evalue': hit_evalue,
            'bitscore': hit_bitscore,
        }
        LOG.info("saving hit: %s", hit_args)
        select_template_hit = SelectTemplateHit(**hit_args)
        select_template_hit.save()

        if not dom_seqs:
            LOG.warning('No CATH domains found in FunFam alignment: {}'.format(funfam_id))
            return select_template_hit

        LOG.info('Found %s CATH domains in alignments', len(dom_seqs))

        select_rep = SelectBlastRep(align=ff_aln, ref_seq=query_range_sequence)
        best_hit = select_rep.get_best_blast_hit(only_cath_domains=True)

        add_sequence = MafftAddSequence(
            align=ff_aln, sequence=query_range_sequence)

        aln_with_query = add_sequence.run()

        id1 = query_range_sequence.uid
        id2 = best_hit.subject
        LOG.info(
            "extracting sequences with ids ['%s', '%s'] from alignment", id1, id2)
        aln_with_query = aln_with_query.subset(
            [id1, id2]).remove_alignment_gaps()

        target_sequence = aln_with_query.find_seq_by_id(id1)
        template_sequence = aln_with_query.find_seq_by_id(id2)
        template_seqres_offset = template_sequence.segs[0].start - 1

        domain_id = best_hit.subject
        pdb_id = domain_id[:4]
        auth_asym_id = domain_id[4:5]

        LOG.info('Creating entry in SelectTemplateAlignment')
        aln_args = {
            'hit_uuid': select_template_hit.uuid,
            'target_sequence': target_sequence.seq,
            'template_sequence': template_sequence.seq,
            'template_seqres_offset': template_seqres_offset,
            'pdb_id': pdb_id,
            'auth_asym_id': auth_asym_id,
        }
        LOG.info("saving aln: %s", aln_args)
        template_alignment = SelectTemplateAlignment(**aln_args)
        template_alignment.save()

        return select_template_hit


class SelectTemplateTask(models.Model):

    """This class represents an overall select template task."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    query_id = models.CharField(max_length=50, blank=False, unique=False)
    query_sequence = models.CharField(
        max_length=2000, blank=False, unique=False)

    #user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    message = models.CharField(max_length=1000)
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

    def is_complete(self):
        """
        Returns whether or not the task has finished (ie SUCCESS or ERROR)
        """
        return self.status in STATUS_TYPES_COMPLETED

    def update_remote_task(self):
        """
        Updates the task by performing a status request on the remote server

        Returns:
            is_remote_complete (bool): whether the remote task has completed

        """

        is_remote_complete = False
        LOG.info("update_remote_task: %s '%s'",
                 self.query_id, self.remote_task_id)

        if not self.remote_task_id:
            raise err.NoRemoteTaskIdError(
                'failed to update remote task: remote_task_id not set')

        if self.status in STATUS_TYPES_COMPLETED:
            LOG.info("update_remote_task: %s task_already_complete", self.status)
            return self.status

        try:
            check_response = self.api_client.check(self.remote_task_id)
        except Exception as e:
            msg = "encountered {} when checking remote task: {} (possibly recoverable)".format(
                type(e), e)
            self.message = msg
            self.save()
            LOG.error(msg)
            raise
        msg = check_response.message

        # make these checks explicit so we can add extra hooks to each stage
        if msg == 'done':
            is_remote_complete = True
            
            try:
                results_response = self.api_client.results(self.remote_task_id)
                self.results_json = results_response.as_json()
                self.message = 'remote job finished; processing results'
            except cathpy.error.NoMatchesError:
                self.message = 'remote job finished (no FunFam matches found)'

        elif msg == 'queued':
            self.message = 'remote job still in queue'
            self.status = STATUS_QUEUED
        elif msg == 'running':
            self.message = 'remote job running'
            self.status = STATUS_RUNNING
        elif msg == 'error':
            is_remote_complete = True
            self.message = 'remote job in error state'
            self.status = STATUS_ERROR
        else:
            self.status = STATUS_ERROR
            self.message = "CheckResponse returned unexpected message '{}'".format(
                msg)

        self.save()
        return is_remote_complete

    def create_resolved_hits(self):
        """
        Creates :class:`SelectTemplateHit` entries for the resolved funfam scan
        """

        if not self.results_json:
            raise err.NoResultsDataError('No data in field "results_json"')

        try:
            results_data = json.loads(self.results_json)
            cath_version = results_data['cath_version']
            scan_data = results_data['funfam_resolved_scan']
            scan = Scan(**scan_data)
        except:
            raise err.ParseDataError("Failed to parse 'results_json' (scan: {}): {}".format(
                scan, self.results_json[:100] + '...'
            ))

        if len(scan.results) != 1:
            raise Exception("expected exactly 1 result in scan, got {} (scan:{})".format(
                len(scan.results), scan))

        result = scan.results[0]
        hits = []
        LOG.info("Found %s regions in the query sequence that match CATH FunFams", len(
            result.hits))
        for scan_hit in result.hits:
            query_range = ','.join(
                ['{}-{}'.format(hsp.query_start, hsp.query_end) for hsp in scan_hit.hsps])
            LOG.info("Adding SelectTemplateHit for best structural match in region %s: funfam=%s",
                     query_range, scan_hit.match_name)
            hit = SelectTemplateHit.create_from_scan_hit(
                scan_hit=scan_hit,
                cath_version=cath_version,
                task_uuid=self.uuid,
                is_resolved_hit=True)
            hit.save()
            hits.extend([hit])

        self.message = "Created {} hits".format(len(hits))
        self.save()

        return hits
