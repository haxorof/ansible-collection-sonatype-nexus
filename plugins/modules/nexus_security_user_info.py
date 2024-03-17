#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_security_user_info
short_description: List user(s)
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)


def list_users(helper):
    endpoint = "users"
    info, content = helper.request(
        api_url=(
            helper.NEXUS_API_ENDPOINTS[endpoint]
            + helper.generate_url_query(
                {
                    "source": "source",
                    "userId": "user_id",
                }
            )
        ).format(
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
            msg="Failed to fetch users, http_status={status}.".format(
                status=info["status"],
            )
        )
    return content


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        user_id=dict(type="str", required=False, no_log=False),
        source=dict(type="str", required=False, no_log=False),
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

    content = list_users(helper)
    result["json"] = content
    result["changed"] = False

    module.exit_json(**result)


if __name__ == "__main__":
    main()
