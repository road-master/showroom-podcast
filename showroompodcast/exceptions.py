"""This module implements exceptions for this package."""


class Error(Exception):
    """Base class for exceptions in this module.

    @see
    https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions
    """


class MaxRetriesExceededError(Error):
    """Max retries exceeded."""


class TemporaryNetworkIssuesError(Error):
    """Temporary network issues."""
