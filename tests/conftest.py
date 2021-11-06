"""Configuration of pytest"""
import asyncio
import json
import os
from datetime import datetime
from typing import List

import pytest
import requests_mock
from asynccpu.process_task_pool_executor import ProcessTaskPoolExecutor
from asyncffmpeg.exceptions import FFmpegProcessError
from asyncffmpeg.ffmpeg_coroutine_factory import FFmpegCoroutineFactory
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse

import showroompodcast.slack.slack_client


class MockSlackWebClient:
    """Mock Slack web client."""

    BOT_TOKEN_FOR_TEST = "slack_bot_token"
    SLACK_CHANNEL = "slack_channel"

    def __init__(self, mocker, responses) -> None:
        self.constructor = self.mock_constructor(mocker)
        self.chat_post_message = self.mock_chat_post_message(mocker, responses)
        self.responses = responses

    @classmethod
    def mock_constructor(cls, mocker):
        mock_constructor = mocker.MagicMock(return_value=WebClient(token=cls.BOT_TOKEN_FOR_TEST))
        mocker.patch.object(showroompodcast.slack.slack_client, "WebClient", mock_constructor)
        return mock_constructor

    @staticmethod
    def mock_chat_post_message(mocker, responses):
        mock_chat_post_message = mocker.MagicMock(side_effect=responses)
        mocker.patch.object(WebClient, "chat_postMessage", mock_chat_post_message)
        return mock_chat_post_message


@pytest.fixture
def mock_slack_web_client_broken_process_pool(resource_path_root, mocker):
    response = json.loads(
        (resource_path_root / "successful_response_chat_post_message_broken_process_pool.json").read_text()
    )
    yield MockSlackWebClient(mocker, [response])


@pytest.fixture
def mock_slack_web_client_type_error(resource_path_root, mocker):
    response = json.loads((resource_path_root / "successful_response_chat_post_message_type_error.json").read_text())
    yield MockSlackWebClient(mocker, [response, response])


@pytest.fixture
def mock_slack_web_client_raise_slack_api_error(mocker):
    """Mocks Slack web client to raise SlackApiError."""
    slack_response = SlackResponse(
        client=None,
        http_verb="POST",
        api_url="https://slack.com/api/chat.postMessage",
        req_args={
            "token": MockSlackWebClient.BOT_TOKEN_FOR_TEST,
            "channel": MockSlackWebClient.SLACK_CHANNEL,
            "text": "",
        },
        data={"ok": False, "error": "invalid_auth"},
        headers={
            "date": "Thu, 05 Aug 2021 13:27:22 GMT",
            "server": "Apache",
            "access-control-expose-headers": "x-slack-req-id, retry-after",
            "access-control-allow-headers": (
                "slack-route, x-slack-version-ts, x-b3-traceid, "
                "x-b3-spanid, x-b3-parentspanid, x-b3-sampled, x-b3-flags"
            ),
            "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
            "access-control-allow-origin": "*",
            "x-slack-backend": "r",
            "x-xss-protection": "0",
            "x-slack-req-id": "3a7ca5929fe904442e5630c641cbcd59",
            "vary": "Accept-Encoding",
            "x-content-type-options": "nosniff",
            "referrer-policy": "no-referrer",
            "content-type": "application/json; charset=utf-8",
            "x-envoy-upstream-service-time": "14",
            "x-backend": (
                "main_normal main_bedrock_normal_with_overflow main_canary_with_overflow "
                "main_bedrock_canary_with_overflow main_control_with_overflow main_bedrock_control_with_overflow"
            ),
            "x-server": "slack-www-hhvm-canary-main-iad-373l",
            "x-via": "envoy-www-iad-op6f, haproxy-edge-nrt-ih4z",
            "x-slack-shared-secret-outcome": "shared-secret",
            "via": "envoy-www-iad-op6f",
            "connection": "close",
            "transfer-encoding": "chunked",
        },
        status_code=200,
    )
    slack_api_error = SlackApiError("The request to the Slack API failed.", slack_response,)
    yield MockSlackWebClient(mocker, [slack_api_error])


class MockPolling:
    """Mock polling."""

    URL = "https://www.showroom-live.com/api/live/polling"
    QUERY = "?room_id="

    @classmethod
    def not_on_live(cls, list_room_id: List[int]):
        with requests_mock.Mocker() as mock_request:
            response_text = '{"live_end":1,"invalid":1}'
            for room_id in list_room_id:
                mock_request.get(cls.URL + cls.QUERY + str(room_id), complete_qs=True, text=response_text)
            yield

    @classmethod
    def on_live(cls, list_room_id: List[int]):
        with requests_mock.Mocker() as mock_request:
            response_text = '{"is_login":true,"online_user_num":411,"live_watch_incentive":{}}'
            for room_id in list_room_id:
                mock_request.get(cls.URL + cls.QUERY + str(room_id), complete_qs=True, text=response_text)
            yield

    @classmethod
    def status_503(cls, list_room_id: List[int]):
        status_code = 503
        with requests_mock.Mocker() as mock_request:
            for room_id in list_room_id:
                mock_request.get(cls.URL + cls.QUERY + str(room_id), complete_qs=True, status_code=status_code)
            yield


@pytest.fixture
def mock_requrst_room_1_not_on_live():
    yield from MockPolling.not_on_live([1])


@pytest.fixture
def mock_requrst_room_1_on_live():
    yield from MockPolling.on_live([1])


@pytest.fixture
def mock_requrst_room_1_503():
    yield from MockPolling.status_503([1])


@pytest.fixture
def mock_requrst_room_1_to_5_on_live():
    yield from MockPolling.on_live(list(range(1, 6)))


class MockStreamingUrl:
    """Mock of SHOWROOM streaming URL API."""

    URL = "https://www.showroom-live.com/api/live/streaming_url"

    @classmethod
    def mock_requrst_streaming_url(cls, room_id, response_text):
        query = "?room_id="
        with requests_mock.Mocker() as mock_request:
            mock_request.get(cls.URL + query + str(room_id), complete_qs=True, text=response_text)
            yield


@pytest.fixture
def mock_requrst_room_1_streaming_url(resource_path_root):
    # Specifies encoding to prevent following error in Windows:
    # UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 663: character maps to <undefined>
    response_text = (resource_path_root / "response_streaming_url.json").read_text(encoding="utf-8")
    yield from MockStreamingUrl.mock_requrst_streaming_url(1, response_text)


@pytest.fixture
def existing_file_2021_08_07_21_00_00():
    path_to_file_example = create_path_to_file_2021_08_07_21_00_00()
    with open(path_to_file_example, "x", encoding="utf-8") as file:
        yield file
    os.remove(path_to_file_example)


def create_path_to_file_2021_08_07_21_00_00():
    room_id = 1
    now_string = "2021_08_07-21_00_00"
    return f"./output/{room_id}-{now_string}.mp4"


@pytest.fixture
def mock_now_2021_08_07_21_00_00(mocker):
    mock_datetime = mocker.MagicMock(wrap=datetime)
    mock_datetime.now.return_value = datetime(2021, 8, 7, 21, 0, 0)
    mocker.patch("showroompodcast.showroom_datetime.datetime", mock_datetime)


@pytest.fixture
def mock_ffmpeg_croutine_ffmpeg_empty_future(mocker):
    future = asyncio.Future()
    future.set_result(None)
    yield mock_ffmpeg_croutine(mocker, [future])


@pytest.fixture
def mock_ffmpeg_croutine_ffmpeg_process_error(mocker):
    ffmpeg_process_error = FFmpegProcessError(
        "File '/tmp/pytest-of-root/pytest-1/test_excecption0/2021_08_07-22_30_00.mp4' already exists. Exiting.", 1
    )
    yield mock_ffmpeg_croutine(mocker, [ffmpeg_process_error])


def mock_ffmpeg_croutine(mocker, result):
    ffmpeg_croutine = FFmpegCoroutineFactory.create()
    mock_execute = mocker.MagicMock(side_effect=result)
    ffmpeg_croutine.execute = mock_execute
    return ffmpeg_croutine


@pytest.fixture
def mock_process_task_pool_executor(mocker):
    process_task_executor = ProcessTaskPoolExecutor()
    mock_method = mocker.MagicMock(side_effect=[None, None, None, None, FFmpegProcessError("", 127)])
    process_task_executor.create_process_task = mock_method
    mock_constructor = mocker.MagicMock(return_value=process_task_executor)
    mocker.patch("showroompodcast.showroom_podcast.ProcessTaskPoolExecutor", mock_constructor)
