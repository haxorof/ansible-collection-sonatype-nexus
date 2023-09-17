#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_security_anonymous
short_description: Set anonymous access setting
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)


def get_anonymous_setting(helper):
    endpoint = "anonymous"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content.pop("fetch_url_retries", None)
    elif info["status"] in [403]:
        helper.module.fail_json(
            msg="The user does not have permission to perform the operation."
        )
    else:
        helper.module.fail_json(
            msg="Failed to fetch anonymous setting., http_status={status}.".format(
                status=info["status"],
            )
        )
    return content


def update_anonymous_setting(helper, current_data):
    changed = True
    data = {
        "enabled": True if helper.module.params["state"] == "enabled" else False,
    }
    if helper.module.params["user_id"]:
        data.update(
            {
                "userId": helper.module.params["user_id"],
            }
        )
    else:
        data.update(
            {
                "userId": current_data["userId"],
            }
        )
    if helper.module.params["realm_name"]:
        data.update(
            {
                "realmName": helper.module.params["realm_name"],
            }
        )
    else:
        data.update(
            {
                "realmName": current_data["realmName"],
            }
        )

    endpoint = "anonymous"
    changed = not helper.is_json_data_equal(data, current_data)
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="PUT",
        data=data,
    )

    if info["status"] in [200]:
        content.pop("fetch_url_retries", None)
        content = data
    elif info["status"] == 403:
        helper.module.fail_json(
            msg="The user does not have permission to perform the operation."
        )
    else:
        helper.module.fail_json(
            msg="Failed to update anonymous setting, http_status={http_status}, error_msg='{error_msg}'.".format(
                error_msg=info["msg"],
                http_status=info["status"],
            )
        )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        realm_name=dict(type="str", required=False, no_log=False),
        state=dict(type="str", choices=["enabled", "disabled"], default="enabled"),
        user_id=dict(type="str", required=True, no_log=False),
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

    content, changed = update_anonymous_setting(helper, get_anonymous_setting(helper))
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
