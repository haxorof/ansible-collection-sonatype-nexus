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
module: nexus_license_info
short_description: Get Nexus license Information
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def get_license(helper):
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["license"].format(
            url=helper.module.params["url"]
        ),
        method="GET",
    )

    if info["status"] in [200]:
        content = content  # pylint: disable=self-assigning-variable
    elif info["status"] in [402]:
        content = {}
    elif info["status"] == 403:
        helper.module.fail_json(msg="Insufficient permissions to get license.")
    else:
        helper.module.fail_json(
            msg=f"Failed to get license, http_status={info['status']}, error_msg='{info['msg']}'."
        )
    return content


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )
    helper = NexusHelper(module)
    result = NexusHelper.generate_result_struct(False, get_license(helper))

    module.exit_json(**result)


if __name__ == "__main__":
    main()
