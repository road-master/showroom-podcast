"""Test for showroom_podcast.py."""
import logging

from click.testing import CliRunner

from showroompodcast.cli import showroom_podcast


class TestShowroomPodcast:
    """Test for ShowroomPodcast."""

    @staticmethod
    # Reason: pytest fixture. pylint: disable=unused-argument
    def test(
        mock_requrst_room_1_to_5_on_live,
        mock_slack_web_client_type_error,
        mock_process_task_pool_executor,
        resource_path_root,
        caplog,
    ):
        """Smoke test."""
        caplog.set_level(logging.CRITICAL)
        runner = CliRunner()
        result = runner.invoke(
            showroom_podcast, ["--file", resource_path_root / "config_valid_slack_configuration.yml"]
        )
        assert result.exit_code == 1
        # assert result.output == 'Hello Peter!\n'
