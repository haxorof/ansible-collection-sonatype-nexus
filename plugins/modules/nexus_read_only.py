#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_read_only
short_description: Manage read-only system status
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)

def update_read_only(helper):
    endpoint = "read-only"
    info = None
    content = None
    changed = True
    successful = False

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{action}").format(
            url=helper.module.params["url"],
            action=helper.module.params["status"],
        ),
        method="POST",
    )

    if info["status"] in [204]:
        # System is now read-only / System is no longer read-only
        successful = True
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif info["status"] in [404]:
        # No change to read-only state
        changed = False
        successful = True

    if successful:
        content.pop("fetch_url_retries", None)

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        status=dict(type="str", choices=["freeze", "release", "force-release"], default="freeze"),
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
        status=module.params["status"],
        messages=[],
        json={},
    )

    content = {}
    changed = True
    if not module.check_mode:
        content, changed = update_read_only(helper)
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
