"""Test for showroom_poller.py."""
from threading import Lock

from showroompodcast.showroom_poller import ShowroomPoller


class TestShowroomPoller:
    """Test for ShowroomPoller."""

    @staticmethod
    # Reason: pytest fixture. pylint: disable=unused-argument
    def test(mock_requrst_room_1_503):
        ShowroomPoller(None, None).poll(1, Lock())
