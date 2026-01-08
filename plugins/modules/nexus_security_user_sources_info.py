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
module: nexus_security_user_sources_info
short_description: Retrieve a list of available user sources
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def list_user_sources(helper):
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["user-sources"]).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content = content["json"]
    elif info["status"] in [403]:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg=f"Failed to fetch user sources., http_status={info['status']}."
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

    content = list_user_sources(helper)
    result = NexusHelper.generate_result_struct(False, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
