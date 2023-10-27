"""A python api to interact with mantau by EXEC IT Solutions GmbH"""
import requests
from .mantau_dataclasses import Session, PrivateChat, User, GroupSettings, Color
import time


def login(user: str, password: str) -> Session:
    """This function takes login credentials and returns user id and session token."""
    headers = {
        'VID': '11212',
    }

    json_data = {
        'user': user,
        'password': password,
        'cookie': True,
    }

    response = requests.post(
        'https://app.mantau.de/api-mantau/app/login',
        headers=headers,
        json=json_data,
        timeout=5000
    )

    if response.status_code == 200:
        return Session(True, response.cookies.get_dict()['wfauth'], response.json()['userid'])
    else:
        return Session(False)


def private_chats(session: Session) -> list[PrivateChat]:
    """This takes a session returns a list of private chat objects."""
    cookies = {'wfauth': session.wfauth}

    headers = {
        'VID': '11212'
    }

    json_data = {
        'action': 100,
        'ref': 'view.remote_resultsets.remote_load_chats_and_messages.load_chats_and_messages',
        'df': 2,
        'params': {
            'group_id': 0,
            'chat_id': None,
            'is_moderation': False,
            'is_privatechats': True,
            'min_id': None,
            'loaded_chat_ids': '',
            'load_chats': True,
            'load_messages': False,
        },
    }

    response = requests.post(
        'https://app.mantau.de/api-mantau/app/%5Bmantau%5D%20Chats',
        cookies=cookies,
        headers=headers,
        json=json_data,
        timeout=5000
    )

    private_chats_list = response.json()['result'][0]['childs']['load_chats'][0]['childs'] \
        ['privatechats']

    private_chats_list_out = []

    for chat in private_chats_list:
        private_chat = PrivateChat.from_json(chat['fields'])
        private_chats_list_out.append(private_chat)

    return private_chats_list_out


def load_users(session: Session, user_ids: list[int]) -> list[User]:
    """This takes a session and a list of internal ids to return a list of user objects."""
    cookies = {'wfauth': session.wfauth}

    headers = {
        'VID': '11212',
    }

    json_data = {
        'action': 100,
        'ref': 'view.remote_resultsets.remote_load_unknown_users.load_unknown_users',
        'df': 2,
        'params': {
            'count_user_ids': len(user_ids),
            'user_ids': user_ids,
        },
    }

    response = requests.post(
        'https://app.mantau.de/api-mantau/app/%5Bmantau%5D%20Hauptvorgang',
        cookies=cookies,
        headers=headers,
        json=json_data,
    ).json()

    users = response['result'][0]['childs']['users']

    user_list_out = []

    for user in users:
        _user = User.from_json(user['fields'])
        user_list_out.append(_user)

    return user_list_out


def create_free_group(session: Session, group_settings: GroupSettings, parent_id: int | None = None,
                      creator_profile_id: int = 0):
    """This takes a session and a group settings object to create said group with the current session."""

    current_user = load_users(session, [session.userid])[0]

    if parent_id is not None:
        group_settings.parent_id = parent_id

    # Creates the initials of a group if not present
    if group_settings.short_name is None:
        word_array = group_settings.name.split(' ')

        if len(word_array) > 1 and word_array[1] != '':
            initials = word_array[0][0] + word_array[1][0]
        else:
            if len(word_array[0]) > 1:
                initials = word_array[0][0:2]
            else:
                initials = word_array[0]

        group_settings.short_name = initials

    # If a group is a main group, it can't inherit something
    if group_settings.main:
        group_settings.inheritance = False

    # If inheritance isn't activated authors and mods also can't be inherited
    if not group_settings.inheritance:
        group_settings.inherit_authors = False
        group_settings.inherit_mods = False

    if isinstance(group_settings.color, Color):
        group_settings.color = group_settings.color.value

    cookies = {'wfauth': session.wfauth}

    headers = {
        'VID': '11212'
    }

    json_data = {
        "action": 101,
        "ref": "view.schluessel.remote_create_group.groups",
        "rows": [
            {
                "wf_rowstate": 1,
                "max_user_count": 10,
                "group_name": group_settings.name,
                "description": group_settings.description,
                "initials": group_settings.short_name,
                "color": f"#{group_settings.color}",
                "inherit_kz": group_settings.inheritance,  # inherit members
                "inherit_authors": group_settings.inherit_authors,
                "inherit_moderators": group_settings.inherit_mods,
                "content_messages": group_settings.features.messages,
                "content_events": group_settings.features.events,
                "content_files": group_settings.features.files,
                "content_forms": group_settings.features.forms,
                "content_moderation": group_settings.features.requests,
                "sort_by_lastname": False,
                "has_changes": True,
                "selected_group_user": [session.userid] + group_settings.members,
                "has_license": False,
                "chat_id": None,
                "creator_profile_id": str(creator_profile_id) if creator_profile_id != 0 else "",
                "creator_has_a2": None,
                "creator_profile_ids": "",
                "activate": True,
                "wf_child_rs": [
                    {
                        "name": "group_user",
                        "rows": [
                                    {
                                        "wf_rowstate": 1,
                                        "user_id": session.userid,
                                        "profile_id": 1 + ((creator_profile_id - 1) if creator_profile_id != 0 else 0),
                                        "additional_information": "",
                                        "is_sysuser": True,
                                        "sysuser_profile_id": "1",
                                        "not_is_sysuser": False,
                                        "wf_client_rowid": 0
                                    }
                                ] + [
                                    {
                                        "wf_rowstate": 1,
                                        "user_id": user_id,
                                        # THIS IS THE ROLE; 1 = ADMIN, 2 = member, 3 = organiser, 4 = invis member
                                        "profile_id": 2 + ((creator_profile_id - 1) if creator_profile_id != 0 else 0),
                                        "additional_information": "",
                                        "is_sysuser": False,
                                        "sysuser_profile_id": "",
                                        "not_is_sysuser": True,
                                        "wf_client_rowid": 1 + index
                                    } for index, user_id in enumerate(group_settings.members)
                                ]
                    },
                    {
                        "name": "group_group_author",
                        "rows": [
                            {
                                "wf_rowstate": 1,
                                "group_id": -1,
                                "merge_id": "",
                                "wf_client_rowid": 0
                            }
                        ]
                    },
                    {
                        "name": "group_user_moderator",
                        "rows": [
                            {
                                "wf_rowstate": 1,
                                "user_id": session.userid,
                                "wf_client_rowid": 0
                            }  # more here if more moderators
                        ]
                    }
                ],
                "wf_client_rowid": 0
            }
        ],
        "params": {
            "language": "en-EN",
            "current_user_vorname": current_user.firstname,
            "group_parent": group_settings.parent_id if not group_settings.main else 0,
            "current_user_nachname": current_user.lastname,
            "license_id": ""
        }
    }

    child_rs: list = json_data['rows'][0]['wf_child_rs']

    for index, rs in enumerate(child_rs):
        if group_settings.inheritance and rs['name'] == 'group_user':
            child_rs.pop(index)
        if not group_settings.features.requests and rs['name'] == 'group_user_moderator':
            child_rs.pop(index)

    response = requests.put(
        'https://app.mantau.de/api-mantau/app/%5Bmantau%5D%20Gruppe%20anlegen',
        cookies=cookies,
        headers=headers,
        json=json_data,
        timeout=5000
    ).json()

    print(response)

    group_ids = []
    group_id = response['return']['groups'][0]['fields']['id']
    c_profile_id = int(response['return']['groups'][0]['fields']['creator_profile_id'])
    group_ids += [group_id]

    if creator_profile_id != 0:
        c_profile_id = creator_profile_id

    if group_settings.sub_groups is not None:
        time.sleep(10)
        for group in group_settings.sub_groups:
            group_ids += create_free_group(session, group, group_id, c_profile_id)
            time.sleep(10)

    return group_ids
