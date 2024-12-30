"""API of polling."""

from requests import HTTPError

from showroompodcast.api import ShowroomApi
from showroompodcast.exceptions import TemporaryNetworkIssuesError
from showroompodcast.raise_if import raise_if


class Polling(ShowroomApi):
    """API of polling."""

    @classmethod
    def poll(cls, room_id: int) -> bool:
        """Returns True when on live, otherwise returns False."""
        response = cls._poll(room_id)
        return "live_end" not in response or response["live_end"] != 1

    @classmethod
    def _poll(cls, room_id: int) -> dict[str, int]:
        """Returns True when on live, otherwise returns False."""
        try:
            return cls.request({"room_id": room_id})
        except HTTPError as error:
            # Often returns 502, 503, 504 temporary, retry.
            raise_if(condition=error.response.status_code not in [500, 502, 503, 504])
            raise TemporaryNetworkIssuesError from error
        except ConnectionError as error:
            # To avoid process down due to temporary DNS resolution error.
            list_error_message_retry = [
                "Failed to establish a new connection: [Errno -2] Name or service not known",
                "Failed to establish a new connection: [Errno -3] Temporary failure in name resolution",
            ]
            condition_retry = any(message in str(error) for message in list_error_message_retry)
            raise_if(condition=not condition_retry)
            raise TemporaryNetworkIssuesError from error

    @staticmethod
    def url() -> str:
        return "https://www.showroom-live.com/api/live/polling"
