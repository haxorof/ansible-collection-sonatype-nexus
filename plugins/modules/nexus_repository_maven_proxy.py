#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import humps

DOCUMENTATION = r"""
---
module: nexus_repository_maven_proxy
short_description: Manage Maven proxy repositories
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

def repository_filter(item, helper):
    return item["name"] == helper.module.params["name"]

def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        maven=dict(
            type='dict',
            apply_defaults=True,
            options=dict(
                version_policy=dict(type="str", choices=["RELEASE", "SNAPSHOT", "MIXED"], default="RELEASE"),
                layout_policy=dict(type="str", choices=["STRICT", "PERMISSIVE"], default="STRICT"),
                content_disposition=dict(type="str", choices=["INLINE", "ATTACHMENT"], default="INLINE"),
            ),
        ),
    )
    argument_spec.update(NexusRepositoryHelper.common_proxy_argument_spec())
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

    changed, content = True, {}
    existing_data = NexusRepositoryHelper.list_filtered_repositories(helper, repository_filter)
    if module.params["state"] == "present":
        endpoint_path = "/maven/proxy"
        additional_data = {
            "maven": NexusHelper.camalize_param(helper, "maven"),
        }
        if len(existing_data) > 0:
            content, changed = NexusRepositoryHelper.update_repository(helper, endpoint_path, additional_data, existing_data[0])
        else:
            content, changed = NexusRepositoryHelper.create_repository(helper, endpoint_path, additional_data)
    else:
        if len(existing_data) > 0:
            content, changed = NexusRepositoryHelper.delete_repository(helper)
        else:
            changed = False
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
