"""Test for showroom_podcast.py."""

import logging
from pathlib import Path

from click.testing import CliRunner
import pytest

from showroompodcast.cli import showroom_podcast


class TestShowroomPodcast:
    """Test for ShowroomPodcast."""

    @staticmethod
    @pytest.mark.usefixtures(
        "mock_request_room_1_to_5_on_live",
        "mock_slack_web_client_type_error",
        "mock_process_task_pool_executor",
    )
    # Reason: pytest fixture. pylint: disable=unused-argument
    def test(resource_path_root: Path, caplog: pytest.LogCaptureFixture) -> None:
        """Smoke test."""
        caplog.set_level(logging.CRITICAL)
        runner = CliRunner()
        result = runner.invoke(
            showroom_podcast,
            ["--file", str(resource_path_root / "config_valid_slack_configuration.yml")],
        )
        assert result.exit_code == 1
