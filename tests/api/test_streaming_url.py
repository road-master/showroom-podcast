"""Test for streaming_url.py."""
from showroompodcast.api.streaming_url import StreamingUrl


class TestStreamingUrl:
    @staticmethod
    def test(mock_requrst_room_1_streaming_url):
        room_id = 1
        url = StreamingUrl.get_url_for_best_quality(room_id)
        assert url == (
            "https://hls-origin246.showroom-cdn.com/liveedge"
            "/8c8aa496884af085d8f1bf853f03cfc71e7e1f83bbf3f44497e64063caffe28d_source/chunklist.m3u8"
        )
