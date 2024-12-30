"""Configuration."""

from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class SlackConfig(DataClassJsonMixin):
    """This class implements configuration for Slack."""

    bot_token: str
    channel: str


@dataclass
class Config(YamlDataClassConfig):
    """Configuration."""

    # Reason: To use auto complete
    number_process: int = None  # type:ignore[assignment]
    stop_if_file_exists: bool = None  # type:ignore[assignment]
    list_room_id: list[int] = field(default_factory=list)
    slack: SlackConfig = field(  # type:ignore[assignment]
        default=None,
        metadata={"dataclasses_json": {"mm_field": SlackConfig}},
    )
