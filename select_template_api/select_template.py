"""
Selects template structure/alignments for a given protein sequence
"""

import logging
import os
import subprocess
import tempfile

#from Bio import SearchIO

from cathpy.align import Align, Sequence

from .errors import NoStructureDomainsError

LOG = logging.getLogger(__name__)

BLASTP_EXE = 'blastp'
MAKEBLASTDB_EXE = 'makeblastdb'
FORMATDB_EXE = 'formatdb'

DEFAULT_MAFFT_EXE = 'mafft'

DEFAULT_BLAST_MAX_EVALUE = 0.001


def seqs_to_fasta_nogaps(seqs):
    """
    Returns a string containing ungapped FASTA sequences
    """
    return ''.join(['>' + seq.uid + '\n' + seq.seq_no_gaps + '\n' for seq in seqs])


class BlastHit(object):
    """
    Stores information on a Blast Hit
    """

    def __init__(self, *, query, subject, identity, alignment_length,
                 mismatches, gap_opens, query_start, query_end, match_start,
                 match_end, evalue, bit_score, subject_sequence=None):
        self.query = query
        self.subject = subject
        self.identity = identity
        self.alignment_length = alignment_length
        self.mismatches = mismatches
        self.gap_opens = gap_opens
        self.query_start = query_start
        self.query_end = query_end
        self.match_start = match_start
        self.match_end = match_end
        self.evalue = evalue
        self.bit_score = bit_score
        self.subject_sequence = subject_sequence

    @classmethod
    def from_outfmt_7(cls, hit_line):
        """
        Creates a new instance from a BLAST format 7 results string
        """

        # query acc.ver, subject acc.ver, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
        (query, subject, identity, alignment_length, mismatches, gap_opens, query_start,
         query_end, match_start, match_end, evalue, bit_score) = hit_line.split()

        return cls(
            query=query,
            subject=subject,
            identity=float(identity),
            alignment_length=int(alignment_length),
            mismatches=int(mismatches),
            gap_opens=int(gap_opens),
            query_start=int(query_start),
            query_end=int(query_end),
            match_start=int(match_start),
            match_end=int(match_end),
            evalue=float(evalue),
            bit_score=float(bit_score),
        )

    def __str__(self):
        return "query={} subject={} query={}-{} match={}-{} identity={} evalue={} bitscore={}".format(
            self.query,
            self.subject,
            self.query_start, self.query_end,
            self.match_start, self.match_end,
            self.identity, self.evalue, self.bit_score,
        )


class SelectBlastRep(object):
    """
    Selects the closest member of an alignment to query sequence (best BLAST)  
    """

    def __init__(self, *, align: Align, ref_seq: Sequence,
                 max_evalue=DEFAULT_BLAST_MAX_EVALUE):

        self.align = align
        self.ref_seq = ref_seq
        self.max_evalue = max_evalue
        self._blast_hits = []

    def run(self):
        """
        Returns a :class:`cathpy.Sequence` corresponding to the 'best' alignment rep
        """

        workdir = tempfile.TemporaryDirectory(prefix='selectblastrep')
        original_dir = os.getcwd()
        os.chdir(workdir.name)

        blast_hits = []

        try:
            queryfile = tempfile.NamedTemporaryFile(
                suffix='.query.fa', mode='wt', delete=False)
            dbfile = tempfile.NamedTemporaryFile(
                suffix='.db.fa', mode='wt', delete=False)
            outfile = tempfile.NamedTemporaryFile(
                suffix='.out', delete=False)

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
            #       though weirdly the 'blast-tab' doesn't work either - might be me...
            with open(outfile.name, 'rt') as blasttab:
                for line in blasttab:
                    # query acc.ver, subject acc.ver, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                    if line.startswith('#'):
                        continue

                    blast_hit = BlastHit.from_outfmt_7(line)

                    subject_seq = self.align.find_seq_by_id(blast_hit.subject)

                    if not subject_seq:
                        raise Exception("failed to find BLAST subject '{}' in original alignment".format(
                            blast_hit.subject))

                    blast_hit.subject_sequence = subject_seq

                    blast_hits.extend([blast_hit])

            queryfile.close()
        except:
            LOG.error("encountered an error when running BLAST")
            raise
        finally:
            os.chdir(original_dir)
            workdir.cleanup()

        self._blast_hits = blast_hits

    @property
    def blast_hits(self):
        if not self._blast_hits:
            self.run()
        return self._blast_hits

    def get_best_blast_hit(self, *, sort_by=None, only_cath_domains=True, reverse=True):
        """
        Returns the 'best' blast hit

        Args:
            sort_by (function): function to use for sorting (default: `lambda h: h.bit_score`)
            only_cath_domains (bool): only consider CATH domains (default: True)
            reverse (bool): reverse the order of the sort hits

        Returns:
            blast_hit (:class:`BlastHit`): best blast hit
        """

        def sort_by_bitscore(hit):
            return hit.bit_score

        def is_seq_valid_cath_domain(seq_id):
            hdr_info = Sequence.split_hdr(seq_id)
            return bool(hdr_info['id_type'] == 'domain')

        if not sort_by:
            sort_by = sort_by_bitscore

        sorted_hits = sorted(self.blast_hits,
                             key=sort_by, reverse=reverse)

        if only_cath_domains:
            sorted_hits = [
                h for h in sorted_hits if is_seq_valid_cath_domain(h.subject)]
            if not sorted_hits:
                raise NoStructureDomainsError(
                    'failed to find any members of the alignment with CATH domain ids')

        best_hit = sorted_hits[0]
        return best_hit

    def get_best_blast_sequence(self, *, only_cath_domains=True):
        """
        Returns the best blast sequence
        """
        best_hit = self.get_best_blast_hit(only_cath_domains=only_cath_domains)
        return best_hit.subject_sequence


class MafftAddSequence(object):
    """
    Uses MAFFT to add a sequence to an existing alignment
    """

    def __init__(self, *, align, sequence, mafft_exe=DEFAULT_MAFFT_EXE):
        self.align = align
        self.sequence = sequence
        self.mafft_exe = mafft_exe

    def run(self):

        seqfile = tempfile.NamedTemporaryFile(
            suffix='.seqs.fa', mode='wt', delete=False)
        alnfile = tempfile.NamedTemporaryFile(
            suffix='.aln.fa', mode='wt', delete=False)
        outfile = tempfile.NamedTemporaryFile(
            suffix='.merged.fa', mode='wt', delete=False)

        # write ungapped sequence(s) to file
        seqfile.write(self.sequence.to_fasta())
        seqfile.close()

        # write existing alignment to file
        self.align.write_fasta(alnfile.name)

        # use mafft to add sequences to alignment
        mafft_cmds = (self.mafft_exe, '--add', seqfile.name, alnfile.name)
        LOG.info("Running MAFFT: %s", " ".join(mafft_cmds))
        subprocess.run(mafft_cmds, check=True,
                       stdout=outfile, stderr=subprocess.PIPE)
        outfile.close()

        # transfer meta data from original alignment
        merged_aln = Align.from_fasta(outfile.name)

        new_aln = self.align.copy()

        # set the length of the alignment (avoids complaints when adding sequences)
        new_seq = merged_aln.find_seq_by_id(self.sequence.uid)
        new_aln.aln_positions = len(new_seq)

        # add reference sequence to the start of the alignment
        new_aln.add_sequence(new_seq, offset=0)

        # update the newly aligned sequences for the rest of the entries
        for seq in new_aln.sequences:
            try:
                merged_seq = merged_aln.find_seq_by_id(seq.uid)
            except:
                raise Exception("failed to find sequence id {} in merged alignment".format(
                    seq.uid))

            LOG.debug("Sub merged sequence from:%s: %s",
                      seq.uid, seq.seq)
            LOG.debug("                      to:%s: %s",
                      merged_seq.uid, merged_seq.seq)
            seq.set_sequence(merged_seq.seq)

        return new_aln
