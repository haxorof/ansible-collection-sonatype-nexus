#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_security_anonymous_info
short_description: Get anonymous access setting
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)


def get_anonymous_setting(helper):
    endpoint = "anonymous"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content.pop("fetch_url_retries", None)
    elif info["status"] in [403]:
        helper.module.fail_json(
            msg="The user does not have permission to perform the operation."
        )
    else:
        helper.module.fail_json(
            msg="Failed to fetch anonymous setting., http_status={status}.".format(
                status=info["status"],
            )
        )
    return content


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
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

    content = get_anonymous_setting(helper)
    result["json"] = content
    result["changed"] = False

    module.exit_json(**result)


if __name__ == "__main__":
    main()
