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
module: nexus_script_info
short_description: List Nexus scripts
"""

EXAMPLES = r"""
"""
RETURN = r"""
"""


def list_scripts(helper):
    endpoint = "script"
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(
            url=helper.module.params["url"]
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content = content["json"]
    elif info["status"] == 403:
        helper.module.fail_json(msg="Insufficient permissions to read scripts.")
    else:
        helper.module.fail_json(
            msg=f"Failed to read scripts, http_status={info['status']}."
        )
    return content


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        method={"type": "str", "choices": ["GET"], "required": True},
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content = {}
    if module.params["method"] == "GET":  # type: ignore
        content = list_scripts(helper)
    else:
        helper.module.fail_json(msg=f"Unsupported method: {module.params['method']}")  # type: ignore

    result = NexusHelper.generate_result_struct(False, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
