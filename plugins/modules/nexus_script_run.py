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
module: nexus_script_run
short_description: Run a script in Nexus
"""
EXAMPLES = r"""
"""
RETURN = r"""
"""


def run_script(helper):
    endpoint = "script"
    headers = {"Content-Type": "application/json"}
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}/run").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="POST",
        headers=headers,
        data=helper.module.params["body"],
    )
    changed = False
    if info["status"] in [200, 204]:
        changed = True
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg=f"Failed to run script {helper.module.params['name']}, \
                http_status={info['status']}, error_msg='{info['msg']}'."
        )
    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True, "no_log": False},
        body={"type": "str", "required": False, "no_log": False},
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content, changed = run_script(helper)

    result = NexusHelper.generate_result_struct(changed, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
