"""
Custom errors
"""


class NoStructureDomainsError(Exception):
    """
    No structural domains in alignment
    """
    pass


class DiscontinuousDomainError(Exception):
    """
    Not able to process discontinuous domains
    """
    pass
