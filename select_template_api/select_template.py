import logging
import os
import subprocess
import tempfile

from Bio import SearchIO

from cathpy.align import Align, Sequence
from cathpy.tests import is_valid_domain_id

LOG = logging.getLogger(__name__)

BLASTP_EXE = 'blastp'
MAKEBLASTDB_EXE = 'makeblastdb'
FORMATDB_EXE = 'formatdb'
MAFFT_EXE = 'mafft'

DEFAULT_BLAST_MAX_EVALUE = 0.001


class SelectBlastRep(object):
    def __init__(self, *, align: Align, ref_seq: Sequence,
                 only_cath_domains=True, max_evalue=DEFAULT_BLAST_MAX_EVALUE):

        self.align = align
        self.ref_seq = ref_seq
        self.only_cath_domains = only_cath_domains
        self.max_evalue = max_evalue
        self._rep_seq = None

    def get_seq_rep(self):

        workdir = tempfile.TemporaryDirectory(prefix='selectblastrep')
        original_dir = os.getcwd()
        os.chdir(workdir.name)

        try:
            queryfile = tempfile.NamedTemporaryFile(
                suffix='.query.fa', mode='wt', delete=False)
            dbfile = tempfile.NamedTemporaryFile(
                suffix='.db.fa', mode='wt', delete=False)
            outfile = tempfile.NamedTemporaryFile(
                suffix='.out', delete=False)

            def seqs_to_fasta_nogaps(seqs):
                return ''.join(['>' + seq.id + '\n' + seq.seq_no_gaps + '\n' for seq in seqs])

            queryfile.write(seqs_to_fasta_nogaps([self.ref_seq]))
            queryfile.close()

            dbfile.write(seqs_to_fasta_nogaps(self.align.seqs))
            dbfile.close()

            makeblastdb_cmds = (MAKEBLASTDB_EXE, '-in',
                                dbfile.name, '-dbtype', 'prot')
            LOG.info("Running makeblastdb: %s", " ".join(makeblastdb_cmds))
            subprocess.run(makeblastdb_cmds, check=True)

            blast_cmds = (BLASTP_EXE, '-query', queryfile.name, '-db', dbfile.name,
                          '-evalue', '{:f}'.format(self.max_evalue), '-outfmt', '7', '-out', outfile.name)

            LOG.info("Running blast: %s", " ".join(blast_cmds))
            subprocess.run(blast_cmds, check=True)

            LOG.info("Processing BLAST results... ")

            # HACK: this should use Bio.SearchIO, but it is currently complaining about
            #       deprecated parsers (possibly an incompatibility with blastp v2.9.0+?)
            #       though weirdly the 'blast-tab' doesn't work either - might be me
            with open(outfile.name, 'rt') as blasttab:
                for line in blasttab:
                    # query acc.ver, subject acc.ver, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                    if line.startswith('#'):
                        continue
                    (query, subject, identity, alignment_length, mismatches, gap_opens, query_start,
                     query_end, match_start, match_end, evalue, bit_score) = line.split()

                    subject_seq = align.find_seq_by_id(subject)
                    if only_cath_domains and not subject_seq.is_cath_domain:
                        continue

                    best_seq = subject_seq
                    LOG.info("  ... found best hit: %s [evalue=%s bit=%s] (skipping rest)",
                             best_seq.id, evalue, bit_score)
                    break

            # for qresult in SearchIO.parse(outfile.name, 'blast-xml'):
            #     LOG.info('BLAST Hit: %s %.2e', qresult.id, qresult.evalue)

            queryfile.close()
        except:
            LOG.error("encountered an error when running BLAST")
            raise
        finally:
            os.chdir(original_dir)
            workdir.cleanup()

        self._rep_seq = subject_seq
        return self._rep_seq

    @property
    def rep_seq(self):
        return self._rep_seq
