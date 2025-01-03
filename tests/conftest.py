"""Configuration of pytest."""

import asyncio
from collections.abc import Awaitable, Callable, Generator
from datetime import datetime, timezone
from io import TextIOWrapper
import json
from pathlib import Path
from typing import Any, Union
from unittest.mock import MagicMock

from asynccpu.process_task_pool_executor import ProcessTaskPoolExecutor
from asyncffmpeg.exceptions import FFmpegProcessError
from asyncffmpeg.ffmpeg_coroutine_factory import FFmpegCoroutineFactory
from asyncffmpeg import FFmpegCoroutine, StreamSpec
import pytest
from pytest_mock import MockerFixture
import requests_mock
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse
from slack_sdk import WebClient

import showroompodcast.slack.slack_client


# Reason: Mock pylint: disable-next=too-few-public-methods
class MockFFmpegCoroutine:
    """Mock FFmpeg coroutine."""

    def __init__(
        self,
        mocker: MockerFixture,
        side_effect: Callable[[Callable[[], Awaitable[StreamSpec]]], Awaitable[StreamSpec]],
    ) -> None:
        self.execute = mocker.AsyncMock(side_effect=side_effect)


class MockSlackWebClient:
    """Mock Slack web client."""

    # Reason: This is not password.
    BOT_TOKEN_FOR_TEST = "slack_bot_token"  # noqa: S105  # nosec: B105
    SLACK_CHANNEL = "slack_channel"

    def __init__(self, mocker: MockerFixture, responses: list[Union[SlackResponse, SlackApiError]]) -> None:
        self.constructor = self.mock_constructor(mocker)
        self.chat_post_message = self.mock_chat_post_message(mocker, responses)
        self.responses = responses

    @classmethod
    def mock_constructor(cls, mocker: MockerFixture) -> MagicMock:
        mock_constructor = mocker.MagicMock(return_value=WebClient(token=cls.BOT_TOKEN_FOR_TEST))
        mocker.patch.object(showroompodcast.slack.slack_client, "WebClient", mock_constructor)
        # Reason: Certainly returns MagicMock.
        return mock_constructor  # type: ignore[no-any-return]

    @staticmethod
    def mock_chat_post_message(
        mocker: MockerFixture,
        responses: list[Union[SlackResponse, SlackApiError]],
    ) -> MagicMock:
        """Mocks chat_postMessage."""
        mock_chat_post_message = mocker.MagicMock(side_effect=responses)
        mocker.patch.object(WebClient, "chat_postMessage", mock_chat_post_message)
        # Reason: Certainly returns MagicMock.
        return mock_chat_post_message  # type: ignore[no-any-return]


async def sleep_one_second(_: Callable[[], Awaitable[StreamSpec]]) -> None:
    await asyncio.sleep(1)


@pytest.fixture
def mock_ffmpeg_coroutine(mocker: MockerFixture) -> MockFFmpegCoroutine:
    # Program sleeps for 1 second when call mock_execute.
    this = MockFFmpegCoroutine(mocker, sleep_one_second)
    mock_create = mocker.MagicMock(return_value=this)
    mocker.patch.object(FFmpegCoroutineFactory, "create", mock_create)
    return this


@pytest.fixture
def mock_slack_web_client_broken_process_pool(resource_path_root: Path, mocker: MockerFixture) -> MockSlackWebClient:
    response = json.loads(
        (resource_path_root / "successful_response_chat_post_message_broken_process_pool.json").read_text(),
    )
    return MockSlackWebClient(mocker, [response])


@pytest.fixture
def mock_slack_web_client_type_error(resource_path_root: Path, mocker: MockerFixture) -> MockSlackWebClient:
    response = json.loads((resource_path_root / "successful_response_chat_post_message_type_error.json").read_text())
    return MockSlackWebClient(mocker, [response, response])


@pytest.fixture
def mock_slack_web_client_raise_slack_api_error(mocker: MockerFixture) -> MockSlackWebClient:
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
    # Reason: Slack API's issue.
    slack_api_error = SlackApiError(  # type: ignore[no-untyped-call]
        "The request to the Slack API failed.",
        slack_response,
    )
    return MockSlackWebClient(mocker, [slack_api_error])


class MockPolling:
    """Mock polling."""

    URL = "https://www.showroom-live.com/api/live/polling"
    QUERY = "?room_id="

    @classmethod
    def not_on_live(cls, list_room_id: list[int]) -> Generator[None, None, None]:
        with requests_mock.Mocker() as mock_request:
            response_text = '{"live_end":1,"invalid":1}'
            for room_id in list_room_id:
                mock_request.get(cls.URL + cls.QUERY + str(room_id), complete_qs=True, text=response_text)
            yield

    @classmethod
    def on_live(cls, list_room_id: list[int]) -> Generator[None, None, None]:
        with requests_mock.Mocker() as mock_request:
            response_text = '{"is_login":true,"online_user_num":411,"live_watch_incentive":{}}'
            for room_id in list_room_id:
                mock_request.get(cls.URL + cls.QUERY + str(room_id), complete_qs=True, text=response_text)
            yield

    @classmethod
    def status_503(cls, list_room_id: list[int]) -> Generator[None, None, None]:
        status_code = 503
        with requests_mock.Mocker() as mock_request:
            for room_id in list_room_id:
                mock_request.get(cls.URL + cls.QUERY + str(room_id), complete_qs=True, status_code=status_code)
            yield


@pytest.fixture
def mock_request_room_1_not_on_live() -> Generator[None, None, None]:
    yield from MockPolling.not_on_live([1])


@pytest.fixture
def mock_request_room_1_on_live() -> Generator[None, None, None]:
    yield from MockPolling.on_live([1])


@pytest.fixture
def mock_request_room_1_503() -> Generator[None, None, None]:
    yield from MockPolling.status_503([1])


@pytest.fixture
def mock_request_room_1_to_5_on_live() -> Generator[None, None, None]:
    yield from MockPolling.on_live(list(range(1, 6)))


class MockStreamingUrl:
    """Mock of SHOWROOM streaming URL API."""

    URL = "https://www.showroom-live.com/api/live/streaming_url"

    @classmethod
    def mock_request_streaming_url(cls, room_id: int, response_text: str) -> Generator[None, None, None]:
        query = "?room_id="
        with requests_mock.Mocker() as mock_request:
            mock_request.get(cls.URL + query + str(room_id), complete_qs=True, text=response_text)
            yield


@pytest.fixture
def mock_request_room_1_streaming_url(resource_path_root: Path) -> Generator[None, None, None]:
    # Specifies encoding to prevent following error in Windows:
    # UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 663: character maps to <undefined>
    response_text = (resource_path_root / "response_streaming_url.json").read_text(encoding="utf-8")
    yield from MockStreamingUrl.mock_request_streaming_url(1, response_text)


@pytest.fixture
def existing_file_2021_08_07_21_00_00() -> Generator[TextIOWrapper, None, None]:
    path_to_file_example = create_path_to_file_2021_08_07_21_00_00()
    with path_to_file_example.open("x", encoding="utf-8") as file:
        yield file
    path_to_file_example.unlink()


def create_path_to_file_2021_08_07_21_00_00() -> Path:
    room_id = 1
    now_string = "2021_08_07-21_00_00"
    return Path(f"./output/{room_id}-{now_string}.mp4")


@pytest.fixture
def mock_now_2021_08_07_21_00_00(mocker: MockerFixture) -> None:
    mock_datetime = mocker.MagicMock(wrap=datetime)
    mock_datetime.now.return_value = datetime(2021, 8, 7, 21, 0, 0, tzinfo=timezone.utc)
    mocker.patch("showroompodcast.showroom_datetime.datetime", mock_datetime)


@pytest.fixture
def mock_ffmpeg_coroutine_ffmpeg_empty_future(mocker: MockerFixture) -> FFmpegCoroutine:
    future: asyncio.Future[None] = asyncio.Future()
    future.set_result(None)
    return create_mock_ffmpeg_coroutine(mocker, [future])


@pytest.fixture
def mock_ffmpeg_coroutine_ffmpeg_process_error(mocker: MockerFixture) -> FFmpegCoroutine:
    ffmpeg_process_error = FFmpegProcessError(
        "File '/tmp/pytest-of-root/pytest-1/test_excecption0/2021_08_07-22_30_00.mp4' already exists. Exiting.",
        1,
    )
    return create_mock_ffmpeg_coroutine(mocker, [ffmpeg_process_error])


def create_mock_ffmpeg_coroutine(mocker: MockerFixture, side_effect: Any) -> FFmpegCoroutine:
    ffmpeg_coroutine = FFmpegCoroutineFactory.create()
    mock_execute = mocker.MagicMock(side_effect=side_effect)
    # Reason: Creating Mock.
    ffmpeg_coroutine.execute = mock_execute  # type: ignore[method-assign]
    return ffmpeg_coroutine


@pytest.fixture
def mock_process_task_pool_executor(mocker: MockerFixture) -> None:
    """Mocks ProcessTaskPoolExecutor."""
    process_task_executor = ProcessTaskPoolExecutor()
    mock_method = mocker.MagicMock(side_effect=[None, None, None, None, FFmpegProcessError("", 127)])
    # Reason: Creating Mock.
    process_task_executor.create_process_task = mock_method  # type: ignore[method-assign]
    mock_constructor = mocker.MagicMock(return_value=process_task_executor)
    mocker.patch("showroompodcast.showroom_podcast.ProcessTaskPoolExecutor", mock_constructor)
