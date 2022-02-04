"""Raise if."""


def raise_if(condition):
    if condition:
        # Reason: It's caller's responsible to check calling inside an except clause.
        # pylint: disable=misplaced-bare-raise
        raise
