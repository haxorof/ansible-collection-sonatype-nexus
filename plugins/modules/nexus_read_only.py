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
module: nexus_read_only
short_description: Manage read-only system status
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def update_read_only(helper):
    endpoint = "read-only"
    info = None
    content = None
    changed = True

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{action}").format(
            url=helper.module.params["url"],
            action=helper.module.params["status"],
        ),
        method="POST",
    )

    if info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif info["status"] in [404]:
        # No change to read-only state
        changed = False
        content.pop("fetch_url_retries", None)
    elif not helper.is_request_status_ok(info):
        helper.generic_failure_msg("Failed to update read-only", info)

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        status={
            "type": "str",
            "choices": ["freeze", "release", "force-release"],
            "default": "freeze",
        },
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content = {}
    changed = True
    if not module.check_mode:
        content, changed = update_read_only(helper)
    result = NexusHelper.generate_result_struct({"status": module.params["status"]})  # type: ignore
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
