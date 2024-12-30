"""Test for streaming_url.py."""
from showroompodcast.api.streaming_url import StreamingUrl


class TestStreamingUrl:
    @staticmethod
    def test(mock_requrst_room_1_streaming_url):
        room_id = 1
        url = StreamingUrl.get_url_for_best_quality(room_id)
        assert url == (
            "https://hls-css.live.showroom-live.com/live"
            "/e528adc6d148858dc650976df10e3663205e6327663fc1475368bf0f9667ee41.m3u8"
        )
