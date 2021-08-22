"""Tests for showroom_archiver.py."""
import asyncio
from threading import Lock

import pytest
from asyncffmpeg.exceptions import FFmpegProcessError
from asyncffmpeg.ffmpeg_coroutine_factory import FFmpegCoroutineFactory

from showroompodcast.exceptions import MaxRetriesExceededError
from showroompodcast.showroom_archiver import ArchiveAttempter, ShowroomArchiver, async_retry


class TestShowroomArchiver:
    """Test for ShowroomArchiver."""

    @staticmethod
    @pytest.mark.asyncio
    # Reason: pytest fixture. pylint: disable=unused-argument
    async def test(mock_requrst_room_1_streaming_url):
        """
        - Locked lock should be unlocked.
        - MaxRetriesEceededError should be raised.
        """
        lock = Lock()
        # Reason: Releasing lock will be executed in function call. pylint: disable=consider-using-with
        lock.acquire()
        task = asyncio.create_task(ShowroomArchiver().archive(1, lock))
        assert lock.locked()
        with pytest.raises(MaxRetriesExceededError):
            await task
        assert not lock.locked()


async def shorter_loop_asynchronous_generator():
    for _ in range(3):
        yield


async def infinity_loop_asynchronous_generator():
    while True:
        yield


@pytest.mark.asyncio
async def test_async_retry():
    async for _ in async_retry(shorter_loop_asynchronous_generator(), 5):
        print(_)


async def test_async_retry_max_retry_exceeded():
    with pytest.raises(MaxRetriesExceededError):
        async for _ in async_retry(infinity_loop_asynchronous_generator(), 5):
            print(_)


class TestArchiveAttempter:
    """Test for ArchiveAttempter."""

    @pytest.mark.asyncio
    async def test(self, mock_ffmpeg_croutine_ffmpeg_empty_future):
        room_id = 1
        archive_attempter = ArchiveAttempter(mock_ffmpeg_croutine_ffmpeg_empty_future, room_id)
        assert await self.count_iteration(archive_attempter) == 0

    @staticmethod
    async def count_iteration(archive_attempter):
        count = 0
        async for _ in archive_attempter:
            count = count + 1
        return count

    @pytest.mark.asyncio
    # Reason: pytest fixture. pylint: disable=unused-argument
    async def test_file_exists_error_not_stop(
        self, mock_requrst_room_1_streaming_url, existing_file_2021_08_07_21_00_00, mock_now_2021_08_07_21_00_00
    ):
        archive_attempter = ArchiveAttempter(FFmpegCoroutineFactory.create(), room_id=1)
        await archive_attempter.__anext__()

    @pytest.mark.asyncio
    async def test_ffmpeg_process_error(self, mock_ffmpeg_croutine_ffmpeg_process_error):
        room_id = 1
        archive_attempter = ArchiveAttempter(mock_ffmpeg_croutine_ffmpeg_process_error, room_id)
        with pytest.raises(FFmpegProcessError):
            await archive_attempter.__anext__()
