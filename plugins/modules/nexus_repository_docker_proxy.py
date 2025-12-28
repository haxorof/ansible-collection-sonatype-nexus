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
module: nexus_repository_docker_proxy
short_description: Manage Docker proxy repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def repository_filter(item, helper):
    return item["name"] == helper.module.params["name"]


def main():
    endpoint_path_to_use = "/docker/proxy"
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "docker": {
                "type": "dict",
                "apply_defaults": True,
                "options": {
                    "v1_enabled": {"type": "bool", "default": False},
                    "force_basic_auth": {"type": "bool", "default": True},
                    "http_port": {"type": "int"},
                    "https_port": {"type": "int"},
                    "subdomain": {"type": "str", "required": False, "no_log": False},
                },
            },
            "docker_proxy": {
                "type": "dict",
                "apply_defaults": True,
                "options": {
                    "index_type": {
                        "type": "str",
                        "choices": ["HUB", "REGISTRY", "CUSTOM"],
                        "default": "REGISTRY",
                    },
                    "index_url": {"type": "str", "required": False, "no_log": False},
                    "cache_foreign_layers": {"type": "bool", "default": False},
                    "foreign_layer_url_whitelist": {
                        "type": "list",
                        "elements": "str",
                        "required": False,
                        "no_log": False,
                        "default": [],
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
            "docker": NexusHelper.camalize_param(helper, "docker"),
            "dockerProxy": NexusHelper.camalize_param(helper, "docker_proxy"),
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
