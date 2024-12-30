"""Raise if."""


def raise_if(*, condition: bool) -> None:
    if condition:
        # Reason: It's caller's responsible to check calling inside an except clause.
        # pylint: disable-next=misplaced-bare-raise
        raise  # noqa: PLE0704
