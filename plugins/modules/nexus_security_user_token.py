#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_security_user_token
short_description: Enable/Disable the user token capability or invalidate all user tokens.
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)


def get_user_token_info(helper):
    endpoint = "user-tokens"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
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
    endpoint = "user-tokens"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
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
    }
    endpoint = "user-tokens"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
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
            msg="Failed to update user token configuration, http_status={http_status}, error_msg='{error_msg}'.".format(
                error_msg=info["msg"],
                http_status=info["status"],
            )
        )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        enabled=dict(type="bool", default=True),
        protect_content=dict(type="bool", default=False),
        invalidate_tokens=dict(type="bool", default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = dict(
        changed=False,
        messages=[],
        json={},
    )

    content = {}
    changed = True
    existing_config = get_user_token_info(helper)
    if (
        existing_config
        and existing_config["protectContent"] == helper.module.params["protect_content"]
        and existing_config["enabled"] == helper.module.params["enabled"]
    ):
        changed = False
    else:
        content, changed = update_user_token(helper)
    if module.params["invalidate_tokens"] == True:
        content, changed = invalidate_user_tokens(helper)
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
