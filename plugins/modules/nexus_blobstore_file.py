#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_blobstore_file
short_description: Manage blob stores of type file
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
    NexusBlobstoreHelper,
)


def create_blobstore(helper):
    endpoint = "blobstores"
    blobstore_type = "file"
    changed = True
    data = {
        "softQuota": NexusHelper.camalize_param(helper, "soft_quota"),
        "name": helper.module.params["name"],
        "path": helper.module.params["name"] if helper.module.params["path"] == None or helper.module.params["path"] == "" else helper.module.params["path"],
    }

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/" + blobstore_type).format(
            url=helper.module.params["url"],
        ),
        method="POST",
        data=data,
    )
    if info["status"] not in [204]:
        if info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to create blob store '{name}' of type '{type}'.".format(
                    name=helper.module.params["name"],
                    type=blobstore_type,
                )
            )
        else:
            helper.module.fail_json(
                msg="Failed to create blob store '{name}', http_status={http_status}, error_msg='{error_msg}'.".format(
                    name=helper.module.params["name"],
                    http_status=info["status"],
                    error_msg=info["msg"],
                )
            )

    return content, changed


def update_blobstore(helper, current_data):
    changed = True
    blobstore_type = "file"
    endpoint = "blobstores"
    data = {
        "softQuota": NexusHelper.camalize_param(helper, "soft_quota"),
        "path": helper.module.params["name"] if helper.module.params["path"] == None or helper.module.params["path"] == "" else helper.module.params["path"],
    }

    normalized_data = helper.clean_dict_list(data)
    normalized_current_data = helper.clean_dict_list(current_data)

    changed = not helper.is_json_data_equal(normalized_data, normalized_current_data[0])

    if changed is False:
        return current_data, False

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/" + blobstore_type + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="PUT",
        data=data,
    )
    if info["status"] not in [204]:
        if info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to update blob store '{name}' of type '{type}'.".format(
                    name=helper.module.params["name"],
                    type=blobstore_type,
                )
            )
        elif info["status"] == 404:
            helper.module.fail_json(
                msg="Blob store '{name}' of type '{type}' not found.".format(
                    name=helper.module.params["name"],
                    type=blobstore_type,
                )
            )
        else:
            helper.module.fail_json(
                msg="Failed to update blob store '{name}' of type '{type}', http_status={status}, error_msg='{error_msg}.".format(
                    name=helper.module.params["name"],
                    type=blobstore_type,
                    status=info["status"],
                    error_msg=info["msg"],
                )
            )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        path=dict(type="str", required=False, no_log=False),
    )
    argument_spec.update(NexusBlobstoreHelper.common_argument_spec())
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = dict(
        changed=False,
        name=module.params["name"],
        state=module.params["state"],
        messages=[],
        json={},
    )

    content = {}
    changed = True
    existing_blobstore = NexusBlobstoreHelper.get_blobstore(helper, "file")
    if module.params["state"] == "present":
        if existing_blobstore:
            content, changed = update_blobstore(helper, existing_blobstore)
        else:
            content, changed = create_blobstore(helper)
    else:
        if existing_blobstore:
            content, changed = NexusBlobstoreHelper.delete_blobstore(helper)
        else:
            changed = False
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()