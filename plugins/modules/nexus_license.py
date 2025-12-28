#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

import base64
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)

DOCUMENTATION = r"""
---
module: nexus_license
short_description: Manage Nexus license
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def upload_license(helper):
    endpoint = "license"
    changed = True
    encoded_license = helper.module.params["license_data"]
    license_bytes = base64.b64decode(encoded_license)

    headers = {"Content-Type": "application/octet-stream", "Accept": "application/json"}

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(
            url=helper.module.params["url"]
        ),
        method="POST",
        data=license_bytes,
        headers=headers,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(msg=f"Required parameters missing.{info}")
        elif info["status"] == 403:
            helper.module.fail_json(msg="Insufficient permissions to upload license.")
        else:
            helper.module.fail_json(
                msg=f"Failed to upload license, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def delete_license(helper):
    endpoint = "license"
    changed = True

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(
            url=helper.module.params["url"]
        ),
        method="DELETE",
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(msg="Insufficient permissions to delete license.")
        else:
            helper.module.fail_json(
                msg=f"Failed to delete license, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        state={"type": "str", "choices": ["present", "absent"], "default": "present"},
        license_data={"type": "str"},
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = {
        "changed": False,
        "state": module.params["state"],  # type: ignore
        "messages": [],
        "json": {},
    }

    content = {}
    changed = True

    if module.params["state"] == "present":  # type: ignore
        content, changed = upload_license(helper)
    else:
        content, changed = delete_license(helper)
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
