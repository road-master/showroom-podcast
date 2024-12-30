"""API of Streaming URL."""

from collections.abc import Callable

from showroompodcast.api import ShowroomApi


def itemgetter(key: str) -> Callable[[dict[str, int]], int]:
    """The key `quality` sometimes does not exist in latest specification in SHOWROOM."""

    def function(item: dict[str, int]) -> int:
        """The key `quality` sometimes does not exist in latest specification in SHOWROOM."""
        return item.get(key, 0)

    return function


class StreamingUrl(ShowroomApi):
    """API of Streaming URL."""

    @classmethod
    def get_url_for_best_quality(cls, room_id: int) -> str:
        response = cls.request({"room_id": room_id})
        # The key `quality` sometimes does not exist in latest specification in SHOWROOM.
        # Reason: Certainly returns str. pylint: disable-next=line-too-long
        return sorted(response["streaming_url_list"], key=itemgetter("quality"), reverse=True)[0]["url"]  # type: ignore[no-any-return]  # noqa: E501,RUF100

    @staticmethod
    def url() -> str:
        return "https://www.showroom-live.com/api/live/streaming_url"
