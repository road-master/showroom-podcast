"""Tests for polling.py."""

import pytest
from requests.models import HTTPError

from showroompodcast.api.polling import Polling
from showroompodcast.exceptions import TemporaryNetworkIssuesError


class TestPolling:
    """Tests for Polling."""

    @pytest.mark.parametrize(
        ("mock_request", "expected"),
        [("mock_request_room_1_not_on_live", False), ("mock_request_room_1_on_live", True)],
    )
    def test(self, request: pytest.FixtureRequest, mock_request: str, *, expected: bool) -> None:
        """Tests for poll."""
        request.getfixturevalue(mock_request)
        room_id = 1
        is_on_live = Polling.poll(room_id)
        assert is_on_live is expected

    @pytest.mark.usefixtures("mock_request_room_1_503")
    def test_503(self) -> None:
        """The function: poll() should raise TemporaryNetworkIssuesError when the status code is 503."""
        room_id = 1
        status_code = 503
        with pytest.raises(TemporaryNetworkIssuesError) as excinfo:
            Polling.poll(room_id)
        exception = excinfo.value.__cause__
        assert isinstance(exception, HTTPError)
        assert exception.response.status_code == status_code
