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

"""

EXAMPLES = r"""
- name: Re-encrypt secret with a specific key
  haxorof.sonatype_nexus.nexus_security_secrets_encryption:
    url: "{{ nexus_base_url }}"
    username: admin
    password: "{{ nexus_admin_password }}"
    secret_key_id: somekey
    notify_email: user@example.com
  delegate_to: 127.0.0.1
"""

RETURN = r"""
"""


def reencrypt_secrets(helper):
    changed = True
    data = {
        "secretKeyId": helper.module.params["secret_key_id"],
        "notifyEmail": helper.module.params.get("notify_email", None),
    }
    endpoint = "secret-encryption"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="PUT",
        data=data,
    )

    if info["status"] in [200]:
        content = data
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg=f"Failed to re-encrypt secrets, http_status={info['status']}, error_msg='{info['msg']}'."
        )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        secret_key_id={"type": "str", "required": True},
        notify_email={"type": "str", "required": False},
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content, changed = reencrypt_secrets(helper)
    result = NexusHelper.generate_result_struct(changed, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
