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
module: nexus_security_user_token_info
short_description: Show if the user token capability is enabled or not
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


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "user_id": {"type": "str", "required": False, "no_log": False},
            "source": {"type": "str", "required": False, "no_log": False},
        }
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content = get_user_token_info(helper)
    result = NexusHelper.generate_result_struct(False, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
