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
    NexusRepositoryHelper,
)

DOCUMENTATION = r"""
---
module: nexus_repository_nuget_proxy
short_description: Manage NuGet proxy repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def repository_filter(item, helper):
    return item["name"] == helper.module.params["name"]


def main():
    endpoint_path_to_use = "/nuget/proxy"
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "format": {"type": "str", "choices": ["nuget"], "required": False},
            "type": {"type": "str", "choices": ["proxy"], "required": False},
            "nuget_proxy": {
                "type": "dict",
                "apply_defaults": True,
                "options": {
                    "query_cache_item_max_age": {"type": "int", "default": 3600},
                    "nuget_version": {
                        "type": "str",
                        "choices": ["V2", "V3"],
                        "default": "V3",
                    },
                },
            },
        }
    )
    argument_spec.update(
        NexusRepositoryHelper.common_proxy_argument_spec(endpoint_path_to_use)
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    changed, content = True, {}
    existing_data = NexusRepositoryHelper.list_filtered_repositories(
        helper, repository_filter
    )
    if module.params["state"] == "present":  # type: ignore
        endpoint_path = endpoint_path_to_use
        additional_data = {
            "nugetProxy": NexusHelper.camalize_param(helper, "nuget_proxy"),
        }
        if len(existing_data) > 0:
            content, changed = NexusRepositoryHelper.update_repository(
                helper, endpoint_path, additional_data, existing_data[0]
            )
        else:
            content, changed = NexusRepositoryHelper.create_repository(
                helper, endpoint_path, additional_data
            )
    else:
        if len(existing_data) > 0:
            content, changed = NexusRepositoryHelper.delete_repository(helper)
        else:
            changed = False
    result = NexusHelper.generate_result_struct()
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
