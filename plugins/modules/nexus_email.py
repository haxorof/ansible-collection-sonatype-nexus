#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)

DOCUMENTATION = r"""
---
module: nexus_email
short_description: Manage Nexus email settings
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def get_email_setting(helper):
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["email"].format(
            url=helper.module.params["url"]
        ),
        method="GET",
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to get email settings."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to get email settings, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content


def update_email_setting(helper, existing_data):
    data = {
        "enabled": helper.module.params["enabled"],
        "host": helper.module.params["host"],
        "port": helper.module.params["port"],
        "username": helper.module.params["authentication"]["username"],
        "password": helper.module.params["authentication"]["password"],
        "fromAddress": helper.module.params["from_address"],
        "subjectPrefix": helper.module.params["subject_prefix"],
        "startTlsEnabled": helper.module.params["start_tls_enabled"],
        "startTlsRequired": helper.module.params["start_tls_required"],
        "sslOnConnectEnabled": helper.module.params["ssl_on_connect_enabled"],
        "sslServerIdentityCheckEnabled": helper.module.params[
            "ssl_server_identity_check_enabled"
        ],
        "nexusTrustStoreEnabled": helper.module.params["nexus_trust_store_enabled"],
    }

    password = None
    if isinstance(data, dict):
        password = data.get("password")
        if password:
            existing_data["password"] = password

    normalized_data = helper.clean_dict_list(data)
    normalized_current_data = helper.clean_dict_list(existing_data)

    changed = not helper.is_json_data_equal(normalized_data, normalized_current_data)

    if not helper.module.params["enabled"] and not existing_data["enabled"]:
        return existing_data, False

    if not changed and not helper.module.params["authentication"]["password"]:
        return existing_data, False

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["email"].format(
            url=helper.module.params["url"]
        ),
        method="PUT",
        data=data,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(msg="Required parameters missing.")
        elif info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to update email settings."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update email settings, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def delete_email_setting(helper, existing_data):
    changed = True

    if not existing_data["enabled"]:
        return existing_data, False

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["email"].format(
            url=helper.module.params["url"]
        ),
        method="DELETE",
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to delete email settings."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to delete email settings, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
            "enabled": {"type": "bool", "required": False},
            "host": {"type": "str", "required": False},
            "port": {"type": "int", "required": False},
            "authentication": {
                "type": "dict",
                "default": {},
                "options": {
                    "username": {"type": "str", "required": False},
                    "password": {"type": "str", "required": False, "no_log": True},
                },
            },
            "from_address": {"type": "str", "required": False},
            "subject_prefix": {"type": "str", "required": False},
            "start_tls_enabled": {"type": "bool", "required": False, "default": False},
            "start_tls_required": {"type": "bool", "required": False, "default": False},
            "ssl_on_connect_enabled": {
                "type": "bool",
                "required": False,
                "default": False,
            },
            "ssl_server_identity_check_enabled": {
                "type": "bool",
                "required": False,
                "default": False,
            },
            "nexus_trust_store_enabled": {
                "type": "bool",
                "required": False,
                "default": False,
            },
        }
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = {
        "changed": False,
        "state": module.params["state"],  # type: ignore
        "messages": [],
        "json": {},
    }

    content = {}
    changed = True
    existing_config = get_email_setting(helper)

    if module.params["state"] == "present":  # type: ignore
        content, changed = update_email_setting(helper, existing_config)
    else:
        content, changed = delete_email_setting(helper, existing_config)
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
