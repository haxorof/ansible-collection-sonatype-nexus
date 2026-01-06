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
module: nexus_security_user_token
short_description: Enable/Disable the user token capability or invalidate all user tokens.
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def get_user_token_info(helper):
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["user-tokens"]).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.generic_failure_msg("Failed to get user token information", info)
    return content


def invalidate_user_tokens(helper):
    changed = True
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["user-tokens"]).format(
            url=helper.module.params["url"],
        ),
        method="DELETE",
    )

    if info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.generic_failure_msg("Failed to invalidate user tokens", info)

    return content, changed


def update_user_token(helper):
    changed = True
    data = {
        "enabled": helper.module.params["enabled"],
        "protectContent": helper.module.params["protect_content"],
        "expirationEnabled": helper.module.params.get("expiration_enabled", False),
        "expirationDays": helper.module.params.get("expiration_days", 30),
    }
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["user-tokens"]).format(
            url=helper.module.params["url"],
        ),
        method="PUT",
        data=data,
    )

    if info["status"] in [200]:
        content = data
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg=f"Failed to update user token configuration, http_status={info['status']}, error_msg='{info['msg']}'."
        )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "enabled": {"type": "bool", "default": True},
            "protect_content": {"type": "bool", "default": False},
            "invalidate_tokens": {"type": "bool", "default": False},
            "expiration_enabled": {"type": "bool", "default": False},
            "expiration_days": {"type": "int", "default": 30},
        }
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content = {}
    changed = True
    existing_config = get_user_token_info(helper)
    if (
        existing_config
        and existing_config["protectContent"] == helper.module.params["protect_content"]  # type: ignore
        and existing_config["enabled"] == helper.module.params["enabled"]  # type: ignore
        and existing_config["expirationEnabled"] == helper.module.params["expiration_enabled"]  # type: ignore
    ):
        changed = False
    else:
        content, changed = update_user_token(helper)
    if module.params["invalidate_tokens"]:  # type: ignore
        content, changed = invalidate_user_tokens(helper)
    result = NexusHelper.generate_result_struct(changed, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
