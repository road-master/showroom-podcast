"""Test for slack_client.py."""

import html
from unittest.mock import ANY

import pytest
from slack_sdk.errors import SlackApiError

from showroompodcast.slack.slack_client import SlackClient
from showroompodcast.slack.slack_client import SlackNotification
from tests.conftest import MockSlackWebClient


class TestSlackClient:
    """Test for SlackClient."""

    @staticmethod
    def test_post_message(mock_slack_web_client_broken_process_pool: MockSlackWebClient) -> None:
        """Tests following:

        - Method post_message() should create WebClient with Slack bot token.
        - Method post_message() should call chat_postMessage() with Slack channel and message.
        - Method post_message() should return responce.
        """
        slack_channel = "slack_channel"
        message = "BrokenProcessPool: A child process terminated abruptly, the process pool is not usable anymore"
        actual = SlackClient(MockSlackWebClient.BOT_TOKEN_FOR_TEST, slack_channel).post_message(message)
        assert actual == mock_slack_web_client_broken_process_pool.responses[0]
        assert html.unescape(actual["message"]["text"]) == message, actual["message"]["text"] + message
        mock_slack_web_client_broken_process_pool.constructor.assert_called_once_with(
            token=MockSlackWebClient.BOT_TOKEN_FOR_TEST,
        )
        mock_slack_web_client_broken_process_pool.chat_post_message.assert_called_once_with(
            channel=slack_channel,
            text=message,
        )

    @staticmethod
    @pytest.mark.usefixtures("mock_slack_web_client_raise_slack_api_error")
    # Reason: pytest fixture. pylint: disable=unused-argument
    def test_post_message_slack_api_error() -> None:
        """Method post_message should raise SlackApiError when Slack web client raises SlackApiError."""
        slack_channel = "slack_channel"
        message = "BrokenProcessPool: A child process terminated abruptly, the process pool is not usable anymore"
        with pytest.raises(SlackApiError):
            SlackClient(MockSlackWebClient.BOT_TOKEN_FOR_TEST, slack_channel).post_message(message)

    @staticmethod
    def test_post_reply(mock_slack_web_client_broken_process_pool: MockSlackWebClient) -> None:
        """Tests following:

        - Method post_reply() should create WebClient with Slack bot token.
        - Method post_reply() should call post_message() with Slack channel, message, and timestamp.
        - Method post_reply() should return responce.
        """
        slack_channel = "slack_channel"
        thread_timestamp = "thread_timestamp"
        message = "BrokenProcessPool: A child process terminated abruptly, the process pool is not usable anymore"
        actual = SlackClient(MockSlackWebClient.BOT_TOKEN_FOR_TEST, slack_channel).post_reply(
            message,
            thread_timestamp,
        )
        assert actual == mock_slack_web_client_broken_process_pool.responses[0]
        assert html.unescape(actual["message"]["text"]) == message, actual["message"]["text"] + message
        mock_slack_web_client_broken_process_pool.constructor.assert_called_once_with(
            token=MockSlackWebClient.BOT_TOKEN_FOR_TEST,
        )
        mock_slack_web_client_broken_process_pool.chat_post_message.assert_called_once_with(
            channel=slack_channel,
            text=message,
            thread_ts=thread_timestamp,
        )

    @staticmethod
    @pytest.mark.usefixtures("mock_slack_web_client_raise_slack_api_error")
    # Reason: pytest fixture. pylint: disable=unused-argument
    def test_post_reply_slack_api_error() -> None:
        """Method post_reply should raise SlackApiError when Slack web client raises SlackApiError."""
        slack_channel = "slack_channel"
        thread_timestamp = "thread_timestamp"
        message = "BrokenProcessPool: A child process terminated abruptly, the process pool is not usable anymore"
        with pytest.raises(SlackApiError):
            SlackClient(MockSlackWebClient.BOT_TOKEN_FOR_TEST, slack_channel).post_reply(message, thread_timestamp)

    def test_post_error(self, mock_slack_web_client_type_error: MockSlackWebClient) -> None:
        """Tests following:

        - Method post_error() should create WebClient with Slack bot token.
        - Method post_error() should call post_message() with Slack channel, any text, and any timestamp.
        """
        slack_channel = "slack_channel"
        self.execute_test(MockSlackWebClient.BOT_TOKEN_FOR_TEST, slack_channel)
        mock_slack_web_client_type_error.constructor.assert_called_once_with(
            token=MockSlackWebClient.BOT_TOKEN_FOR_TEST,
        )
        mock_slack_web_client_type_error.chat_post_message.assert_any_call(
            channel=slack_channel,
            text='TypeError: can only concatenate str (not "int") to str',
        )
        mock_slack_web_client_type_error.chat_post_message.assert_called_with(
            channel=slack_channel,
            text=ANY,
            thread_ts=ANY,
        )

    @staticmethod
    def execute_test(slack_bot_token: str, slack_channel: str) -> None:
        try:
            # Reason: To raise TypeError.
            "2" + 2  # type: ignore[operator]  # noqa: B018
        except TypeError as error:
            SlackNotification(slack_bot_token, slack_channel).post_error(error)
