"""SHOWROOM archiver."""

import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
from logging import getLogger
import os
from threading import Lock
from typing import TypeVar

from asyncffmpeg.exceptions import FFmpegProcessError
from asyncffmpeg.ffmpeg_coroutine import FFmpegCoroutine
from asyncffmpeg import FFmpegCoroutineFactory

from showroompodcast.exceptions import MaxRetriesExceededError
from showroompodcast.raise_if import raise_if
from showroompodcast.showroom_stream_spec_factory import ShowroomStreamSpecFactory

TIME_TO_FORCE_TERMINATION = 8


class ShowroomArchiver:
    """SHOWROOM archiver."""

    RETRY = 5

    def __init__(self, *, time_to_force_termination: int = TIME_TO_FORCE_TERMINATION) -> None:
        self.ffmpeg_coroutine = FFmpegCoroutineFactory.create(time_to_force_termination=time_to_force_termination)
        self.logger = getLogger(__name__)

    async def archive(self, room_id: int, lock: Lock) -> None:
        """Archives SHOWROOM program."""
        self.logger.debug("Start archive")
        self.logger.debug("room_id: %d", room_id)
        archive_attempter = ArchiveAttempter(self.ffmpeg_coroutine, room_id)
        try:
            async for _ in async_retry(archive_attempter, self.RETRY):
                pass
        finally:
            lock.release()


T = TypeVar("T")


async def async_retry(asynchronous_generator: AsyncIterator[T], count: int) -> AsyncGenerator[T, None]:
    for _ in range(count):
        try:
            yield await asynchronous_generator.__anext__()
        except StopAsyncIteration:
            return
    raise MaxRetriesExceededError


class ArchiveAttempter:
    """Archive attmpter."""

    def __init__(self, ffmpeg_coroutine: FFmpegCoroutine, room_id: int) -> None:
        self.ffmpeg_coroutine = ffmpeg_coroutine
        self.room_id = room_id
        self.logger = getLogger(__name__)

    def __aiter__(self) -> "ArchiveAttempter":
        return self

    async def __anext__(self) -> None:
        try:
            await self.ffmpeg_coroutine.execute(ShowroomStreamSpecFactory(self.room_id).create)
        except FFmpegProcessError as error:
            raise_if(condition="404 Not Found" not in str(error))
        except (KeyboardInterrupt, asyncio.CancelledError):
            self.logger.debug("SIGINT for PID=%d", os.getpid())
            self.logger.debug("FFmpeg run cancelled.")
            raise
        except FileExistsError as error:
            self.logger.debug(str(error), exc_info=error)
        else:
            raise StopAsyncIteration
        await asyncio.sleep(1)
