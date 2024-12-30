"""API of Streaming URL."""
from showroompodcast.api import ShowroomApi


def itemgetter(key):
    """The key `quality` sometimes does not exist in latest specification in SHOWROOM."""

    def function(item):
        """The key `quality` sometimes does not exist in latest specification in SHOWROOM."""
        return item.get(key, 0)

    return function


class StreamingUrl(ShowroomApi):
    """API of Streaming URL."""

    @classmethod
    def get_url_for_best_quality(cls, room_id: int):
        response = cls.request({"room_id": room_id})
        # The key `quality` sometimes does not exist in latest specification in SHOWROOM.
        return sorted(response["streaming_url_list"], key=itemgetter("quality"), reverse=True)[0]["url"]

    @staticmethod
    def url():
        return "https://www.showroom-live.com/api/live/streaming_url"
