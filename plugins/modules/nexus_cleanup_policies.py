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
module: cleanup-policies
short_description: Manage cleanup policies
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def get_cleanup_policy(helper):
    info, content = helper.request(
        api_url=(get_api_endpoint(helper) + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="GET",
    )
    policy_exists = info["status"] in [200]

    return policy_exists, content


def create_cleanup_policy(helper):
    changed = True
    artifact_format = helper.module.params["format"]
    data = {
        "notes": helper.module.params["notes"],
        "name": helper.module.params["name"],
        "format": helper.module.params["format"],
        "criteriaLastBlobUpdated": helper.module.params["criteria_last_blob_updated"],
        "criteriaLastDownloaded": helper.module.params["criteria_last_downloaded"],
    }

    # Append criteria based on format
    if artifact_format in ["maven2", "npm"]:
        data.update(
            {
                "criteriaReleaseType": helper.module.params["criteria_release_type"],
                "criteriaAssetRegex": helper.module.params["criteria_asset_regex"],
            }
        )
    elif artifact_format != "*":
        data.update(
            {
                "criteriaAssetRegex": helper.module.params["criteria_asset_regex"],
            }
        )

    info, content = helper.request(
        api_url=get_api_endpoint(helper).format(url=helper.module.params["url"]),
        method="POST",
        data=data,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(
                msg=f"Cleanup policy '{helper.module.params['name']}' already exists or Required parameters missing."
            )
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to create cleanup policy '{helper.module.params['name']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to create cleanup policy, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def update_cleanup_policy(helper, existing_data):
    changed = True
    artifact_format = helper.module.params["format"]
    data = {
        "notes": helper.module.params["notes"],
        "name": helper.module.params["name"],
        "format": helper.module.params["format"],
        "criteriaLastBlobUpdated": helper.module.params["criteria_last_blob_updated"],
        "criteriaLastDownloaded": helper.module.params["criteria_last_downloaded"],
    }

    # Append criteria based on format
    if artifact_format in ["maven2", "npm"]:
        data.update(
            {
                "criteriaReleaseType": helper.module.params["criteria_release_type"],
                "criteriaAssetRegex": helper.module.params["criteria_asset_regex"],
            }
        )
    elif artifact_format != "*":
        data.update(
            {
                "criteriaAssetRegex": helper.module.params["criteria_asset_regex"],
            }
        )

    existing_data.pop("inUseCount", None)
    normalized_data = helper.clean_dict_list(data)
    normalized_existing_data = helper.clean_dict_list(existing_data)
    changed = not helper.is_json_data_equal(normalized_data, normalized_existing_data)

    if changed is False:
        return existing_data, False

    info, content = helper.request(
        api_url=(get_api_endpoint(helper) + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="PUT",
        data=data,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(msg="Required parameters missing.")
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to update cleanup policy '{helper.module.params['name']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update cleanup policy, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def delete_cleanup_policy(helper):
    info, content = helper.request(
        api_url=(get_api_endpoint(helper) + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="DELETE",
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to delete cleanup policy '{helper.module.params['name']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to delete cleanup policy, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, True


def get_api_endpoint(helper):
    return helper.NEXUS_API_ENDPOINTS[
        (
            "cleanup-policies-internal"
            if helper.module.params["use_internal_api"]
            else "cleanup-policies"
        )
    ]


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "notes": {"type": "str", "required": False},
            "criteria_last_blob_updated": {"type": "int", "required": False},
            "criteria_last_downloaded": {"type": "int", "required": False},
            "criteria_release_type": {"type": "str", "required": False},
            "criteria_asset_regex": {"type": "str", "required": False},
            "retain": {"type": "int", "required": False},
            "name": {"type": "str"},
            "format": {"type": "str", "required": False},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
            "use_internal_api": {
                "type": "bool",
                "default": False,
            },  # Use internal API at own risk
        }
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    result = {
        "changed": False,
        "name": module.params["name"],  # type: ignore
        "state": module.params["state"],  # type: ignore
        "messages": [],
        "json": {},
    }

    content = {}
    changed = True
    policy_exists, existing_policy = get_cleanup_policy(helper)

    if module.params["state"] == "present":  # type: ignore
        if policy_exists is True:
            content, changed = update_cleanup_policy(helper, existing_policy)
        else:
            content, changed = create_cleanup_policy(helper)
    else:
        if policy_exists is True:
            content, changed = delete_cleanup_policy(helper)
        else:
            changed = False

    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
