"""Tests for showroom_archiver.py."""

import asyncio
from collections.abc import AsyncGenerator
from logging import getLogger
from threading import Lock

import pytest
from asyncffmpeg import FFmpegCoroutine
from asyncffmpeg.exceptions import FFmpegProcessError
from asyncffmpeg.ffmpeg_coroutine_factory import FFmpegCoroutineFactory
from ffmpeg.nodes import InputNode
from ffmpeg.nodes import OutputNode
from ffmpeg.nodes import OutputStream

from showroompodcast.exceptions import MaxRetriesExceededError
from showroompodcast.showroom_archiver import ArchiveAttempter
from showroompodcast.showroom_archiver import ShowroomArchiver
from showroompodcast.showroom_archiver import async_retry
from showroompodcast.showroom_datetime import ShowroomDatetime
from tests.conftest import MockFFmpegCoroutine


class TestShowroomArchiver:
    """Test for ShowroomArchiver."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("mock_request_room_1_streaming_url")
    # Reason: pytest fixture. pylint: disable=unused-argument
    async def test(self, mock_ffmpeg_coroutine: MockFFmpegCoroutine) -> None:
        """Following specifications should be ensured:

        - Locked lock should be unlocked.
        - MaxRetriesEceededError should be raised.
        """
        lock = Lock()
        # Reason: Releasing lock will be executed in function call. pylint: disable=consider-using-with
        lock.acquire()
        task = asyncio.create_task(ShowroomArchiver().archive(1, lock))
        assert lock.locked()
        await task
        assert not lock.locked()
        args, _ = mock_ffmpeg_coroutine.execute.call_args
        async_function_crate = args[0]
        stream_spec = await async_function_crate()
        assert isinstance(stream_spec, OutputStream)
        output_node = stream_spec.node
        assert isinstance(output_node, OutputNode)
        self.assert_output_node(output_node)

    def assert_output_node(self, output_node: OutputNode) -> None:
        assert output_node.args == []
        now = ShowroomDatetime.now_jst()
        now_string = ShowroomDatetime.encode(now)
        assert output_node.kwargs == {"c": "copy", "filename": f"./output/1-{now_string}.mp4", "format": "mp4"}
        self.assert_incoming_edge(output_node.incoming_edge_map[0])

    def assert_incoming_edge(self, incoming_edge: tuple[InputNode, None, None]) -> None:
        """Asserts incoming edge."""
        expected_length_incoming_edge = 3
        assert len(incoming_edge) == expected_length_incoming_edge
        assert incoming_edge[1] is None
        assert incoming_edge[2] is None
        input_node = incoming_edge[0]
        assert isinstance(input_node, InputNode)
        self.assert_input_node(input_node)

    def assert_input_node(self, input_node: InputNode) -> None:
        """Asserts input node."""
        assert input_node.args == []
        assert input_node.kwargs == {
            "copytb": "1",
            "filename": (
                "https://hls-css.live.showroom-live.com/live/"
                "e528adc6d148858dc650976df10e3663205e6327663fc1475368bf0f9667ee41.m3u8"
            ),
        }
        assert input_node.incoming_edge_map == {}


async def shorter_loop_asynchronous_generator() -> AsyncGenerator[None, None]:
    for _ in range(3):
        yield


async def infinity_loop_asynchronous_generator() -> AsyncGenerator[None, None]:
    while True:
        yield


@pytest.mark.asyncio
async def test_async_retry() -> None:
    await run_async_retry(shorter_loop_asynchronous_generator())


@pytest.mark.asyncio
async def test_async_retry_max_retry_exceeded() -> None:
    with pytest.raises(MaxRetriesExceededError):
        await run_async_retry(infinity_loop_asynchronous_generator())


async def run_async_retry(async_generator: AsyncGenerator[None, None]) -> None:
    logger = getLogger()
    async for _ in async_retry(async_generator, 5):
        logger.debug(_)


class TestArchiveAttempter:
    """Test for ArchiveAttempter."""

    @pytest.mark.asyncio
    async def test(self, mock_ffmpeg_coroutine_ffmpeg_empty_future: FFmpegCoroutine) -> None:
        room_id = 1
        archive_attempter = ArchiveAttempter(mock_ffmpeg_coroutine_ffmpeg_empty_future, room_id)
        assert await self.count_iteration(archive_attempter) == 0

    @staticmethod
    async def count_iteration(archive_attempter: ArchiveAttempter) -> int:
        count = 0
        async for _ in archive_attempter:
            count = count + 1
        return count

    # Reason: pytest fixture. pylint: disable=unused-argument
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_request_room_1_streaming_url",
        "existing_file_2021_08_07_21_00_00",
        "mock_now_2021_08_07_21_00_00",
    )
    async def test_file_exists_error_not_stop() -> None:
        """File exists error should not stop iteration."""
        archive_attempter = ArchiveAttempter(FFmpegCoroutineFactory.create(), room_id=1)
        await archive_attempter.__anext__()

    @staticmethod
    @pytest.mark.asyncio
    async def test_ffmpeg_process_error(mock_ffmpeg_coroutine_ffmpeg_process_error: FFmpegCoroutine) -> None:
        room_id = 1
        archive_attempter = ArchiveAttempter(mock_ffmpeg_coroutine_ffmpeg_process_error, room_id)
        with pytest.raises(FFmpegProcessError):
            await archive_attempter.__anext__()
