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
module: nexus_routing_rule
short_description: Manage routing rules
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def routing_rule_exists(helper):
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["routing-rules"] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="GET",
    )
    rule_exists = info["status"] in [200]

    return rule_exists, content


def create_routing_rule(helper: NexusHelper):
    changed = True
    data = {
        "name": helper.module.params["name"],
        "description": helper.module.params["description"],
        "mode": helper.module.params["mode"],
        "matchers": helper.module.params["matchers"],
    }
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["routing-rules"]).format(
            url=helper.module.params["url"],
        ),
        method="POST",
        data=data,
    )
    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(
                msg=f"A routing rule with the same name '{helper.module.params['name']}' \
                    already exists or required parameters missing."
            )
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to create routing rule '{helper.module.params['name']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to create routing rule '{helper.module.params['name']}', \
                    http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def delete_routing_rule(helper: NexusHelper):
    changed = True

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["routing-rules"] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="DELETE",
    )
    if not helper.is_request_status_ok(info):
        if info["status"] in [404]:
            # Routing rule not found = OK
            changed = False
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to delete routing rule '{helper.module.params['name']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to delete routing rule '{helper.module.params['name']}', \
                    http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def update_routing_rule(helper: NexusHelper, current_data):
    changed = True
    data = {
        "name": helper.module.params["name"],
        "description": helper.module.params["description"],
        "mode": helper.module.params["mode"],
        "matchers": helper.module.params["matchers"],
    }
    changed = not helper.is_json_data_equal(data, current_data)
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["routing-rules"] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="PUT",
        data=data,
    )
    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(
                msg=f"A routing rule with the same name '{helper.module.params['name']}' \
                    already exists or required parameters missing."
            )
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to update routing rule '{helper.module.params['name']}'."
            )
        elif info["status"] in [404]:
            helper.module.fail_json(
                msg=f"Routing rule '{helper.module.params['name']}' not found."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update routing rule '{helper.module.params['name']}', \
                    http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "name": {"type": "str", "required": True, "no_log": False},
            "description": {"type": "str", "required": False, "no_log": False},
            "mode": {
                "type": "str",
                "required": False,
                "no_log": False,
                "default": "BLOCK",
                "choices": ["ALLOW", "BLOCK"],
            },
            "matchers": {
                "type": "list",
                "elements": "str",
                "required": False,
                "no_log": False,
                "default": [],
            },
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
        }
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content = {}
    changed = True
    rule_exists, existing_rule = routing_rule_exists(helper)
    if module.params["state"] == "present":  # type: ignore
        if rule_exists:
            content, changed = update_routing_rule(helper, existing_rule)
        else:
            content, changed = create_routing_rule(helper)
    else:
        if rule_exists:
            content, changed = delete_routing_rule(helper)
        else:
            changed = False
    result = NexusHelper.generate_result_struct(
        changed,
        content,
        {
            "name": module.params["name"],  # type: ignore
            "state": module.params["state"],  # type: ignore
        },
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
