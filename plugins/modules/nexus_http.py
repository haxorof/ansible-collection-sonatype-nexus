#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import NexusHelper
import copy

DOCUMENTATION = r"""
---
module: nexus_http
short_description: Manage http setting
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

def remove_disabled_proxies_data(config):
    keys_to_remove = []
    for key, value in config.items():
        if isinstance(value, dict):
            if value.get("enabled") is False:
                keys_to_remove.append(key)
            else:
                # Recursively clean nested dictionaries
                config[key] = remove_disabled_proxies_data(value)
    for key in keys_to_remove:
        del config[key]
    return config

def get_http_setting(helper):
    endpoint = "http"
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(url=helper.module.params["url"]),
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

def update_http_setting(helper, existing_data):
    endpoint = "http"
    changed = True

    data = {
        "userAgent": helper.module.params["user_agent"],
        "timeout": helper.module.params["timeout"],
        "retries": helper.module.params["connection_retries"],
        "nonProxyHosts": helper.module.params["non_proxy_hosts"],
        "httpProxy": {
            "enabled": helper.module.params["http_proxy"]["enabled"],
            "host": helper.module.params["http_proxy"]["host"],
            "port": helper.module.params["http_proxy"]["port"],
            "authInfo": {
                "enabled": helper.module.params["http_proxy"]["auth_info"]["enabled"],
                "username": helper.module.params["http_proxy"]["auth_info"]["username"],
                "password": helper.module.params["http_proxy"]["auth_info"]["password"],
                "ntlmHost": helper.module.params["http_proxy"]["auth_info"]["ntlm_host"],
                "ntlmDomain": helper.module.params["http_proxy"]["auth_info"]["ntlm_domain"],
            },
        },
        "httpsProxy": {
            "enabled": helper.module.params["https_proxy"]["enabled"],
            "host": helper.module.params["https_proxy"]["host"],
            "port": helper.module.params["https_proxy"]["port"],
            "authInfo": {
                "enabled": helper.module.params["https_proxy"]["auth_info"]["enabled"],
                "username": helper.module.params["https_proxy"]["auth_info"]["username"],
                "password": helper.module.params["https_proxy"]["auth_info"]["password"],
                "ntlmHost": helper.module.params["https_proxy"]["auth_info"]["ntlm_host"],
                "ntlmDomain": helper.module.params["https_proxy"]["auth_info"]["ntlm_domain"],
            },
        },
    }

    password_http_proxy = data["httpProxy"]["authInfo"]["password"]
    password_https_proxy = data["httpsProxy"]["authInfo"]["password"]
    new_data = copy.deepcopy(data)
    new_data = remove_disabled_proxies_data(new_data)
    normalized_data = helper.clean_dict_list(new_data)
    normalized_current_data = helper.clean_dict_list(existing_data)

    changed = not helper.is_json_data_equal(normalized_data, normalized_current_data)

    if changed is False and (password_http_proxy is None or password_http_proxy == "")  and (password_https_proxy is None or password_https_proxy == ""):
        return existing_data, False

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(url=helper.module.params["url"]),
        method="PUT",
        data=data,
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(
                msg="Required parameters missing."
            )
        elif info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to update http settings."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update http settings, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed

def delete_http_setting(helper):
    endpoint = "http"
    changed = True

    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(url=helper.module.params["url"]),
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

    return content, changed

def main():
    # pylint: disable=too-many-locals
    auth_info_options = {
        "enabled": {"type": "bool", "default": False},
        "username": {"type": "str", "default": ""},
        "password": {"type": "str", "default": "", "no_log": True},
        "ntlm_host": {"type": "str", "default": ""},
        "ntlm_domain": {"type": "str", "default": ""},
    }
    proxy_options = {
        "enabled": {"type": "bool", "default": False},
        "host": {"type": "str", "default": ""},
        "port": {"type": "str", "default": ""},
        "auth_info": {
            "type": "dict",
            "default": {},
            "options": auth_info_options,
        },
    }
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        user_agent={"type": "str", "required": False, "default": ""},
        timeout={"type": "int", "required": False, "default": 20},
        connection_retries={"type": "int", "required": False, "default": 2},
        non_proxy_hosts={"type": "list", "required": False, "default": []},
        http_proxy = {"type": "dict", "default": {}, "options": proxy_options},
        https_proxy = {"type": "dict", "default": {}, "options": proxy_options},
        state={"type": "str", "choices": ["present", "absent"], "default": "present"},
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    result = {
        "changed": False,
        "state": module.params["state"],
        "messages": [],
        "json": {},
    }

    content = {}
    changed = True
    existing_setting = get_http_setting(helper)

    if module.params["state"] == "present":
        content, changed = update_http_setting(helper, existing_setting)
    else:
        content, changed = delete_http_setting(helper)
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)

if __name__ == "__main__":
    main()
