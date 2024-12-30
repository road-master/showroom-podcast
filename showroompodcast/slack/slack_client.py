"""Slack client."""

import logging
import traceback

from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse
from slack_sdk import WebClient


class SlackNotification:
    """Slack notification."""

    def __init__(self, bot_token: str, channel: str) -> None:
        self.client = SlackClient(bot_token, channel)

    def post_error(self, exception: Exception) -> None:
        type_exception = exception.__class__.__name__
        error_message = str(exception)
        response = self.client.post_message(f"{type_exception}: {error_message}")
        joined_traceback = "\n".join(traceback.format_tb(exception.__traceback__))
        response = self.client.post_reply(f"```{joined_traceback}```", response["message"]["ts"])


class SlackClient:
    """Slack client."""

    def __init__(self, bot_token: str, channel: str) -> None:
        self.client = WebClient(token=bot_token)
        self.channel = channel
        self.logger = logging.getLogger(__name__)

    def post_message(self, message: str) -> SlackResponse:
        try:
            return self.client.chat_postMessage(channel=self.channel, text=message)
        except SlackApiError as error:
            self.log_slack_api_error(error)
            raise

    def post_reply(self, message: str, thread_timestamp: str) -> SlackResponse:
        try:
            return self.client.chat_postMessage(channel=self.channel, text=message, thread_ts=thread_timestamp)
        except SlackApiError as error:
            self.log_slack_api_error(error)
            raise

    def log_slack_api_error(self, error: SlackApiError) -> None:
        """Logs Slack API error."""
        # You will get a SlackApiError if "ok" is False
        if error.response["ok"] is not False:
            self.logger.error('Ok is not False. error.response["ok"] = %s', error.response["ok"])
        if not error.response["error"]:  # str like 'invalid_auth', 'channel_not_found'
            self.logger.error('Error is empty. error.response["error"] = %s', error.response["error"])
        self.logger.error(error.response["error"])
        self.logger.exception(error)
