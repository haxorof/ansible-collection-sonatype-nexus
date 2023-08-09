#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_routing_rule
short_description: List routing rule(s)
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)


def get_routing_rule(helper):
    endpoint = "routing-rules"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content.pop("fetch_url_retries", None)
        content = [content]
    if info["status"] in [404]:
        content = []
    elif info["status"] == 403:
        helper.module.fail_json(
            msg="Insufficient permissions to read routing rule '{routing_rule_name}'.".format(
                routing_rule_name=helper.module.params["name"],
            )
        )
    elif info["status"] not in [200, 404]:
        helper.module.fail_json(
            msg="Failed to read routing rule '{routing_rule_name}', http_status={status}.".format(
                routing_rule_name=helper.module.params["name"],
                status=info["status"],
            )
        )
    return content

def list_routing_rule(helper):
    endpoint = "routing-rules"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content.pop("fetch_url_retries", None)
        content = content["json"]
    if info["status"] in [404]:
        content.pop("fetch_url_retries", None)
    elif info["status"] == 403:
        helper.module.fail_json(
            msg="Insufficient permissions to read routing rule '{routing_rule_name}'.".format(
                routing_rule_name=helper.module.params["name"],
            )
        )
    elif info["status"] not in [200, 404]:
        helper.module.fail_json(
            msg="Failed to read routing rule '{routing_rule_name}', http_status={status}.".format(
                routing_rule_name=helper.module.params["name"],
                status=info["status"],
            )
        )
    return content

def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False, no_log=False),
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

    content = {}
    if module.params["name"] == None:
        content = list_routing_rule(helper)
    else:
        content = get_routing_rule(helper)
    result["json"] = content
    result["changed"] = False

    module.exit_json(**result)


if __name__ == "__main__":
    main()
