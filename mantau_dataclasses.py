from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Self


@dataclass(slots=True)
class Session:
    success: bool
    wfauth: str = ''
    userid: int = -1


@dataclass(slots=True)
class PrivateChat:
    last_message_date: int
    last_message_deleted: bool
    last_message_transferred_to_all: bool
    last_message_read_by_all: bool
    creation_date: int
    last_message_creator: int
    partner_id: int
    last_message_file_count: int
    creator_id: int
    count_all_messages: int
    id: int
    count_unread_messages: int
    privatechat_id: int

    last_message: str = ''
    delete_date: int = 0

    @staticmethod
    def from_json(json: dict[str, str | int | bool]) -> PrivateChat:
        return PrivateChat(
            json["last_message_date"],
            json["last_message_deleted"] == 1,
            json["last_message_transferred_to_all"] == 1,
            json["last_message_read_by_all"] == 1,
            json["creation_date"],
            json["last_message_creator"],
            json['partner_id'],
            json["last_message_file_count"],
            json["creator_id"],
            json["count_all_messages"],
            json["id"],
            json["count_all_messages"],
            json["privatechat_id"],
            json["last_message"] if "last_message" in json.keys() else '',
            json["delete_date"] if "delete_date" in json.keys() else -1
        )


@dataclass(slots=True)
class User:
    firstname: str
    avatar_id: int
    loaded_avatar_id: int
    common_group_ids: list[int]
    number_of_groups: int
    id: int
    favorite: bool
    mantau_id: str
    lastname: str
    avatar: str = field(repr=False)
    deleted: bool

    @staticmethod
    def from_json(json: dict[str, str | int | bool]) -> User:
        return User(
            json["firstname"],
            json["avatar_id"] if "avatar_id" in json.keys() else -1,
            json["loaded_avatar_id"] if "loaded_avatar_id" in json.keys() else -1,
            [int(i) for i in json["common_group_ids"].split(',')] if "common_group_ids" in json.keys() else [],
            json["number_of_groups"],
            json["id"],
            json["favorite"] == 1,
            json["mantau_id"],
            json["lastname"],
            json["avatar"] if "avatar" in json.keys() else '',
            json["deleted"] == 1 if "deleted" in json.keys() else False
        )


@dataclass(slots=True)
class GroupFeatures:
    messages: bool = field(default=True)
    events: bool = field(default=True)
    files: bool = field(default=True)
    forms: bool = field(default=False)
    requests: bool = field(default=False)


class RepeatPattern(Enum):
    NONE: str = "none"
    NUMBER: str = "number"
    LIST: str = "list"


class Promise(Enum):
    PARENT_ID: str = "promise"


class Color(Enum):
    YELLOW = "FFDD52"
    ORANGE = "E07700"
    RED = "9F0800"
    PINK = "FF77E3"
    PURPLE = "6D00C2"
    BLUE = "003AFF"
    LIGHT_BLUE = "007ACC"
    GREEN = "006100"
    BLACK = "000000"
    GRAY = "828282"


@dataclass(slots=True)
class GroupSettings:
    main: bool
    name: str
    parent_id: int | Promise.PARENT_ID = field(default=Promise.PARENT_ID)
    features: GroupFeatures = field(default_factory=GroupFeatures)
    short_name: str | None = field(default=None)
    description: str = field(default="")
    # image: str | None = field(default=None, repr=False)
    color: str | Color = field(default="a4dce2")
    inheritance: bool = field(default=False)
    inherit_authors: bool = field(default=False)
    inherit_mods: bool = field(default=False)
    members: list[int] = field(default_factory=list)
    sub_groups: list[GroupSettings] | None = field(default=None)
