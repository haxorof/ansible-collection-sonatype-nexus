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
    nexus_blobstore_commons,
)

DOCUMENTATION = r"""
---
module: nexus_blobstore_file
short_description: Manage blob stores of type file
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def create_blobstore(helper):
    blobstore_type = "file"
    changed = True
    # FileBlobStoreApiCreateRequest
    data = {
        "softQuota": NexusHelper.camalize_param(helper, "soft_quota"),
        "name": helper.module.params["name"],
        "path": (
            helper.module.params["path"]
            if helper.module.params["path"]
            else helper.module.params["name"]
        ),
    }

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["blobstores"] + "/" + blobstore_type).format(
            url=helper.module.params["url"],
        ),
        method="POST",
        data=data,
    )
    if info["status"] not in [204]:
        if info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to create blob store \
                    '{helper.module.params['name']}' of type '{blobstore_type}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to create blob store '{helper.module.params['name']}', \
                    http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def update_blobstore(helper, current_data):
    changed = True
    blobstore_type = "file"
    # FileBlobStoreApiUpdateRequest
    data = {
        "softQuota": NexusHelper.camalize_param(helper, "soft_quota"),
        "path": (
            helper.module.params["name"]
            if helper.module.params["path"]
            else helper.module.params["path"]
        ),
    }

    normalized_data = helper.clean_dict_list(data)
    normalized_current_data = helper.clean_dict_list(current_data)

    changed = not helper.is_json_data_equal(normalized_data, normalized_current_data[0])

    if changed is False:
        return current_data, False

    info, content = helper.request(
        api_url=(
            helper.NEXUS_API_ENDPOINTS["blobstores"] + "/" + blobstore_type + "/{name}"
        ).format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="PUT",
        data=data,
    )
    if info["status"] not in [204]:
        if info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to update blob store '{helper.module.params['name']}' \
                    of type '{blobstore_type}'."
            )
        elif info["status"] == 404:
            helper.module.fail_json(
                msg=f"Blob store '{helper.module.params['name']}' of type '{blobstore_type}' not found."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update blob store '{helper.module.params['name']}' of type '{blobstore_type}', \
                    http_status={info['status']}, error_msg='{info['msg']}."
            )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
            "name": {"type": "str", "no_log": False, "required": True},
        }
    )
    argument_spec.update(nexus_blobstore_commons.file_blob_store_api_model())
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = {
        "changed": False,
        "name": module.params["name"],  # type: ignore
        "state": module.params["state"],  # type: ignore
        "messages": [],
        "json": {},
    }

    content = {}
    changed = True
    existing_blobstore = nexus_blobstore_commons.get_blobstore(helper, "file")
    if module.params["state"] == "present":  # type: ignore
        if existing_blobstore:
            content, changed = update_blobstore(helper, existing_blobstore)
        else:
            content, changed = create_blobstore(helper)
    else:
        if existing_blobstore:
            content, changed = nexus_blobstore_commons.delete_blobstore(helper)
        else:
            changed = False
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
