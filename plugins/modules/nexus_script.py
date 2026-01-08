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
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils import (
    nexus_script_commons,
)

DOCUMENTATION = r"""
---
module: nexus_script
short_description: Manage scripts in Nexus
"""
EXAMPLES = r"""
"""
RETURN = r"""
"""


def create_script(helper):
    changed = True
    data = {
        "name": helper.module.params["name"],
        "type": "groovy",
        "content": helper.module.params["content"],
    }
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["script"].format(
            url=helper.module.params["url"]
        ),
        method="POST",
        data=data,
    )

    if info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.module.fail_json(
            msg=f"Failed to create script {helper.module.params['name']}, \
                http_status={info['status']}, error_msg='{info['msg']}'."
        )

    return content, changed


def delete_script(helper):
    changed = True
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["script"] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="DELETE",
    )

    if info["status"] in [404]:
        content.pop("fetch_url_retries", None)
        changed = False
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.module.fail_json(
            msg=f"Failed to delete script {helper.module.params['name']}, \
                http_status={info['status']}, error_msg='{info['msg']}'."
        )

    return content, changed


def update_script(helper, existing_script):
    changed = True
    data = {
        "name": existing_script["name"],
        "type": "groovy",
        "content": helper.module.params["content"],
    }
    if helper.is_json_data_equal(data, existing_script):
        return existing_script, False

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["script"] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="PUT",
        data=data,
    )

    if info["status"] in [204]:
        content = data
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg=f"Failed to update script {helper.module.params['name']}, \
                http_status={info['status']}, error_msg='{info['msg']}'."
        )

    return content, changed


def manage_script(helper):
    state = helper.module.params["state"]
    content = {}
    changed = True

    if state == "present":
        existing_scripts = nexus_script_commons.list_scripts(helper)
        existing_script = next(
            (
                script
                for script in existing_scripts
                if script["name"] == helper.module.params["name"]
            ),
            None,
        )
        if existing_script:
            content, changed = update_script(helper, existing_script)
        else:
            content, changed = create_script(helper)
    else:
        content, changed = delete_script(helper)

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "name": {"type": "str", "required": True, "no_log": False},
            "content": {"type": "str", "required": False, "no_log": False},
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
    changed = False

    if module.params["state"] == "present":  # type: ignore
        existing_scripts = nexus_script_commons.list_scripts(helper)
        existing_script = next(
            (
                script
                for script in existing_scripts
                if script["name"] == module.params["name"]  # type: ignore
            ),
            None,
        )
        if existing_script:
            content, changed = update_script(helper, existing_script)
        else:
            content, changed = create_script(helper)
    else:
        content, changed = delete_script(helper)

    result = NexusHelper.generate_result_struct(changed, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
