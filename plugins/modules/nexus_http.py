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
module: nexus_http
short_description: Manage http setting
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def get_http_setting(helper: NexusHelper):
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["http"].format(
            url=helper.module.params["url"]
        ),
        method="GET",
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to get http settings."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to get http settings, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content


def auth_settings_request_data(helper: NexusHelper, root_key: str):
    return {
        "enabled": helper.module.params[root_key]["auth_info"]["enabled"],
        "username": helper.module.params[root_key]["auth_info"]["username"],
        "password": helper.module.params[root_key]["auth_info"]["password"],
        "ntlmHost": helper.module.params[root_key]["auth_info"]["ntlm_host"],
        "ntlmDomain": helper.module.params[root_key]["auth_info"]["ntlm_domain"],
    }


def proxy_settings_request_data(helper: NexusHelper, secure_http: bool):
    key_suffix = "http"
    if secure_http:
        key_suffix = "https"
    return {
        "enabled": helper.module.params[f"{key_suffix}_proxy"]["enabled"],
        "host": helper.module.params[f"{key_suffix}_proxy"]["host"],
        "port": helper.module.params[f"{key_suffix}_proxy"]["port"],
        "authInfo": auth_settings_request_data(helper, f"{key_suffix}_proxy"),
    }


def http_settings_request_data(helper: NexusHelper):
    return {
        "userAgent": helper.module.params["user_agent"],
        "timeout": helper.module.params["timeout"],
        "retries": helper.module.params["connection_retries"],
        "nonProxyHosts": helper.module.params["non_proxy_hosts"],
        "httpProxy": proxy_settings_request_data(helper, False),
        "httpsProxy": proxy_settings_request_data(helper, True),
    }


def update_http_setting(helper: NexusHelper, existing_data):
    data = http_settings_request_data(helper)

    normalized_data = helper.delete_all_none_values(data)
    passwords_removed, normalized_data = helper.delete_all_password_keys(data)
    if normalized_data["nonProxyHosts"]:  # type: ignore
        normalized_data["nonProxyHosts"].sort()  # type: ignore
    if normalized_data["httpProxy"]["authInfo"]["enabled"] is False:  # type: ignore
        normalized_data["httpProxy"]["authInfo"] = None  # type: ignore
    if normalized_data["httpsProxy"]["authInfo"]["enabled"] is False:  # type: ignore
        normalized_data["httpsProxy"]["authInfo"] = None  # type: ignore
    # Adjust existing data for comparison reason only due to default values of arguments into module
    existing_passwords_removed, existing_data = helper.delete_all_password_keys(
        existing_data
    )
    if existing_data["nonProxyHosts"]:  # type: ignore
        existing_data["nonProxyHosts"].sort()  # type: ignore
    if existing_data["userAgent"] is None:
        existing_data["userAgent"] = ""  # type: ignore

    changed = not helper.is_json_data_equal(normalized_data, existing_data)
    if changed is False and not passwords_removed and not existing_passwords_removed:
        return existing_data, False

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["http"].format(
            url=helper.module.params["url"]
        ),
        method="PUT",
        data=data,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(msg="Required parameters missing.")
        elif info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to update http settings."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update http settings, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed


def delete_http_setting(helper: NexusHelper):
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["http"].format(
            url=helper.module.params["url"]
        ),
        method="DELETE",
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to delete http settings."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to delete http settings, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, True


def auth_settings_xo():
    """Directly maps to AuthSettingsXo"""
    return {
        "enabled": {"type": "bool", "default": False},
        "username": {"type": "str"},
        "password": {"type": "str", "no_log": True},
        "ntlm_host": {"type": "str"},
        "ntlm_domain": {"type": "str"},
    }


def proxy_settings_xo():
    """Directly maps to ProxySettingsXo"""
    return {
        "enabled": {"type": "bool", "default": False},
        "host": {"type": "str"},
        "port": {"type": "str"},
        "auth_info": {
            "type": "dict",
            "apply_defaults": True,
            "options": auth_settings_xo(),
        },
    }


def http_settings_xo():
    """Directly maps to HttpSettingsXo"""
    return {
        "user_agent": {"type": "str", "default": ""},
        "timeout": {"type": "int", "default": 10},
        "connection_retries": {"type": "int", "default": 1},
        "non_proxy_hosts": {"type": "list", "default": []},
        "http_proxy": {
            "type": "dict",
            "apply_defaults": True,
            "options": proxy_settings_xo(),
        },
        "https_proxy": {
            "type": "dict",
            "apply_defaults": True,
            "options": proxy_settings_xo(),
        },
        "state": {
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
    }


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(http_settings_xo())

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    content = {}
    changed = False
    existing_setting = get_http_setting(helper)

    if module.params["state"] == "present":  # type: ignore
        content, changed = update_http_setting(helper, existing_setting)
    else:
        content, changed = delete_http_setting(helper)
    result = NexusHelper.generate_result_struct(changed, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
