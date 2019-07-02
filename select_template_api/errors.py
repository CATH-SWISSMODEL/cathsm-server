"""
Custom errors
"""


class NoDomainsError(Exception):
    """
    No valid domains in alignment
    """
    pass


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


class NoRemoteTaskIdError(Exception):
    """
    Task needs to have `remote_task_id` set for this process
    """
    pass


class ParseDataError(Exception):
    """
    Failed to parse scan data
    """


class NoResultsDataError(Exception):
    """
    Task requires results data for this process
    """
    pass


class TaskInErrorStateError(Exception):
    """
    Task is in an error state and cannot be processed further
    """
    pass
