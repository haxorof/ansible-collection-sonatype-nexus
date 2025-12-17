#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_roles_info
short_description: Retrieve Nexus roles configuration
"""
EXAMPLES = r"""
"""
RETURN = r"""
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)

def get_role(helper):
    """Retrieve the Nexus role configuration by name."""
    endpoint = "roles"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        return content
    elif info["status"] in [404]:
        return {}
    elif info["status"] == 403:
        helper.module.fail_json(
            msg=f"Insufficient permissions to read role '{helper.module.params['name']}'."
        )
    else:
        helper.module.fail_json(
            msg=f"Failed to read role '{helper.module.params['name']}', http_status={info['status']}."
        )
    return content

def list_roles(helper):
    endpoint = "roles"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content = content["json"]
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg="Failed to fetch roles, http_status={status}.".format(
                status=info["status"],
            )
        )
    return content

def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False, no_log=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = dict(
        changed=False,
        messages=[],
        json={},
    )

    if module.params["name"]:
        content = get_role(helper)
    else:
        content = list_roles(helper)
        
    result["json"] = content
    result["changed"] = False

    module.exit_json(**result)


if __name__ == "__main__":
    main()