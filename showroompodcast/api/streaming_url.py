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
        """Gets streaming URL for best quality."""
        response = cls.request({"room_id": room_id})
        # WebRTC URLs are excluded since FFmpeg does not support the webrtc:// protocol.
        urls = [u for u in response["streaming_url_list"] if not u["url"].startswith("webrtc://")]
        # The key `quality` sometimes does not exist in latest specification in SHOWROOM.
        # Reason: Certainly returns str.
        return sorted(urls, key=itemgetter("quality"), reverse=True)[0]["url"]  # type: ignore[no-any-return]

    @staticmethod
    def url() -> str:
        return "https://www.showroom-live.com/api/live/streaming_url"
