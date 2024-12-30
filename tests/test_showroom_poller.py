"""Test for showroom_poller.py."""

from threading import Lock

import pytest

from showroompodcast.showroom_poller import ShowroomPoller


class TestShowroomPoller:
    """Test for ShowroomPoller."""

    @staticmethod
    @pytest.mark.usefixtures("mock_request_room_1_503")
    # Reason: pytest fixture. pylint: disable=unused-argument
    def test() -> None:
        # Reason: This test doesn't require arguments.
        ShowroomPoller(None, None).poll(1, Lock())  # type: ignore[arg-type]
