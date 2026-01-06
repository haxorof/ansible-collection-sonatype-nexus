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
module: nexus_status_info
short_description: Status checks
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def check_status(helper):
    check_type = ""
    if helper.module.params["check_type"] == "writable":
        check_type = "/writable"
    elif helper.module.params["check_type"] == "system":
        check_type = "/check"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["status"] + check_type).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [503]:
        helper.module.fail_json(msg="Unavailable to service requests.")
    elif not helper.is_request_status_ok(info):
        helper.generic_failure_msg("Failed to check status", info)
    return content


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "check_type": {
                "type": "str",
                "choices": ["writable", "readable", "system"],
                "default": "writable",
            },
        }
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content = check_status(helper)
    result = NexusHelper.generate_result_struct(False, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
