"""SHOWROOM poller."""
from logging import getLogger
from threading import Lock

from asynccpu import ProcessTaskPoolExecutor
from requests.exceptions import HTTPError

from showroompodcast.api.polling import Polling
from showroompodcast.raise_if import raise_if
from showroompodcast.showroom_archiver import ShowroomArchiver


class ShowroomPoller:
    """SHOWROOM poller."""

    def __init__(self, showroom_archiver: ShowroomArchiver, executor: ProcessTaskPoolExecutor) -> None:
        self.showroom_archiver = showroom_archiver
        self.executor = executor
        self.logger = getLogger(__name__)

    def poll(self, room_id: int, lock_archive_task: Lock):
        """Polls."""
        try:
            is_on_live = Polling.poll(room_id)
        except HTTPError as error:
            # Often returns 503, 504 temporary, retry.
            raise_if(error.response.status_code not in [503, 504])
            self.logger.debug(str(error), exc_info=error)
            return
        if is_on_live and lock_archive_task.acquire(blocking=False):
            self.executor.create_process_task(self.showroom_archiver.archive, room_id, lock_archive_task)
