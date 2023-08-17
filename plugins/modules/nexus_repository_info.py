#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_repository_docker_proxy_info
short_description: List Docker proxy repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
    NexusRepositoryHelper,
)


def generic_repositories_filter(item, helper):
    match = True
    if helper.module.params["type"] is not None:
        match &= item["type"] == helper.module.params["type"]
    if helper.module.params["format"] is not None:
        match &= item["format"] == helper.module.params["format"]
    if helper.module.params["name"] is not None:
        match &= item["name"] == helper.module.params["name"]
    return match


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False, no_log=False),
        type=dict(type="str", required=False, no_log=False),
        format=dict(type="str", required=False, no_log=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = dict(
        changed=False,
        messages=[],
        json={},
    )

    content = NexusRepositoryHelper.list_filtered_repositories(
        helper, generic_repositories_filter
    )
    result["json"] = content
    result["changed"] = False

    module.exit_json(**result)


if __name__ == "__main__":
    main()
