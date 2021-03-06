import pytest
from requests.models import HTTPError

from showroompodcast.api.polling import Polling


class TestPolling:
    @pytest.mark.parametrize(
        "mock_request, expected", [("mock_requrst_room_1_not_on_live", False), ("mock_requrst_room_1_on_live", True)],
    )
    def test(self, request, mock_request, expected):
        request.getfixturevalue(mock_request)
        room_id = 1
        is_on_live = Polling.poll(room_id)
        assert is_on_live is expected

    def test_503(self, mock_requrst_room_1_503):
        room_id = 1
        status_code = 503
        with pytest.raises(HTTPError) as error:
            Polling.poll(room_id)
            assert error.response.status_code == status_code
