#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import humps

DOCUMENTATION = r"""
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import NexusHelper, NexusRepositoryHelper

def repository_filter(item, helper):
    return item["name"] == helper.module.params["name"]

def main():
    endpoint_path_to_use = "/rubygems/hosted"
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        format=dict(type="str", choices=["rubygems"], required=False),
        type=dict(type="str", choices=["hosted"], required=False),
        rubygems=dict(
            type="dict",
            apply_defaults=True,
            default={},
            options=dict(
                component=dict(
                    type="dict",
                    apply_defaults=True,
                    default={},
                    options=dict(
                        proprietary_components=dict(type="bool", default=False)
                    )
                )
            )
        )
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
    result = dict(
        changed=False,
        messages=[],
        json={},
    )

    existing_data = NexusRepositoryHelper.list_filtered_repositories(
        helper, repository_filter
    )

    rubygems_params = module.params.get("rubygems") or {}
    storage_data = NexusHelper.camalize_param(helper, "storage") or {}
    additional_data = {
        "storage": storage_data,
        "component": rubygems_params.get("component"),
    }

    if module.params["state"] == "present":
        if existing_data:
            content, changed = NexusRepositoryHelper.update_repository(
                helper,
                endpoint_path_to_use,
                additional_data,
                existing_data[0],
            )
        else:
            content, changed = NexusRepositoryHelper.create_repository(
                helper,
                endpoint_path_to_use,
                additional_data,
            )
    else:
        if existing_data:
            content, changed = NexusRepositoryHelper.delete_repository(helper)
        else:
            content, changed = ({}, False)

    result["json"] = content
    result["changed"] = changed
    module.exit_json(**result)

if __name__ == "__main__":
    main()
