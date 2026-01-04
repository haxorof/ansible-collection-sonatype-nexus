#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusRepositoryHelper,
)

DOCUMENTATION = r"""
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def repository_filter(item, helper):
    return item["name"] == helper.module.params["name"]


def main():
    NexusRepositoryHelper.generic_repository_proxy_module(
        endpoint_path="/p2/proxy", repository_filter=repository_filter
    )

    # endpoint_path_to_use = "/p2/proxy"
    # argument_spec = NexusHelper.nexus_argument_spec()
    # argument_spec.update({})
    # argument_spec.update(
    #     NexusRepositoryHelper.common_proxy_argument_spec(endpoint_path_to_use)
    # )
    # module = AnsibleModule(
    #     argument_spec=argument_spec,
    #     supports_check_mode=True,
    #     required_together=[("username", "password")],
    # )
    # helper = NexusHelper(module)
    # existing_data = NexusRepositoryHelper.list_filtered_repositories(
    #     helper, repository_filter
    # )
    # content = {}
    # if module.params["state"] == "present":  # type: ignore
    #     endpoint_path = endpoint_path_to_use
    #     additional_data = {}
    #     if len(existing_data) > 0:
    #         content, changed = NexusRepositoryHelper.update_repository(
    #             helper, endpoint_path, additional_data, existing_data[0]
    #         )
    #     else:
    #         content, changed = NexusRepositoryHelper.create_repository(
    #             helper, endpoint_path, additional_data
    #         )
    # else:
    #     if len(existing_data) > 0:
    #         content, changed = NexusRepositoryHelper.delete_repository(helper)
    #     else:
    #         changed = False
    # result = NexusHelper.generate_result_struct(changed, content)

    # module.exit_json(**result)


if __name__ == "__main__":
    main()
