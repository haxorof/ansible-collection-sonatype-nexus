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
module: capabilities
short_description: Manage capabilities
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def get_capability(helper, match_type):
    endpoint = "capabilities"
    _, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )

    content_list = content["json"]
    existing_capability = next(
        (item for item in content_list if item["type"] == match_type), None
    )
    capability_exists = existing_capability is not None
    capability_id = existing_capability["id"] if capability_exists else None

    return capability_exists, existing_capability, capability_id


def create_capability(helper):
    changed = True
    endpoint = "capabilities"
    data = {
        "id": helper.module.params["id"],
        "type": helper.module.params["type"],
        "notes": helper.module.params["notes"],
        "enabled": helper.module.params["enabled"],
        "properties": helper.module.params["properties"],
    }

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(
            url=helper.module.params["url"]
        ),
        method="POST",
        data=data,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(
                msg=f"Capabilities '{helper.module.params['id']}' already exists or Required parameters missing."
            )
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to create Capabilities '{helper.module.params['id']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to create Capabilities, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def update_capability(helper, existing_data, capability_id):
    changed = True
    endpoint = "capabilities"
    data = {
        "id": capability_id,
        "type": helper.module.params["type"],
        "notes": helper.module.params["notes"],
        "enabled": helper.module.params["enabled"],
        "properties": helper.module.params["properties"],
    }

    normalized_data = helper.clean_dict_list(data)
    normalized_existing_data = helper.clean_dict_list(existing_data)
    changed = not helper.is_json_data_equal(normalized_data, normalized_existing_data)

    if changed is False:
        return existing_data, False

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{capability_id}").format(
            url=helper.module.params["url"],
            capability_id=capability_id,
        ),
        method="PUT",
        data=data,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(msg="Required parameters missing.")
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to update Capabilities '{helper.module.params['id']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update Capabilities, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def delete_capability(helper, capability_id):
    changed = True
    endpoint = "capabilities"

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{capability_id}").format(
            url=helper.module.params["url"],
            capability_id=capability_id,
        ),
        method="DELETE",
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to delete Capabilities '{helper.module.params['id']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to delete Capabilities, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        id={"type": "str", "required": False},
        type={"type": "str", "required": True},
        notes={"type": "str", "required": False},
        enabled={"type": "bool", "required": False},
        properties={"type": "dict", "required": False, "default": {}},
        state={"type": "str", "choices": ["present", "absent"], "default": "present"},
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    result = {
        "changed": False,
        "id": module.params["type"],  # type: ignore
        "state": module.params["state"],  # type: ignore
        "messages": [],
        "json": {},
    }

    content = {}
    changed = True
    match_type = module.params["type"]  # type: ignore
    capability_exists, existing_capability, capability_id = get_capability(
        helper, match_type
    )

    if module.params["state"] == "present":  # type: ignore
        if capability_exists is True:
            content, changed = update_capability(
                helper, existing_capability, capability_id
            )
        else:
            content, changed = create_capability(helper)
    else:
        if capability_exists is True:
            content, changed = delete_capability(helper, capability_id)
        else:
            changed = False

    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
