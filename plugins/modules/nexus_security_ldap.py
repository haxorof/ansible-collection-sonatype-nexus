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
module: nexus_security_ldap
short_description: Manage LDAP servers in Nexus
"""
EXAMPLES = r"""
"""
RETURN = r"""
"""


def get_ldap_server(helper):
    """Retrieve the LDAP server configuration by name."""
    ldap_name = (
        helper.module.params.get("current_ldap_name")
        or helper.module.params["ldap_name"]
    )  # Use current_ldap_name if specified
    endpoint = "ldap"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}").format(
            url=helper.module.params["url"],
            name=ldap_name,
        ),
        method="GET",
    )
    if info["status"] == 200:
        return content

    if info["status"] == 404:
        return None  # Return None if not found

    if info["status"] == 403:
        helper.module.fail_json(
            msg=f"Insufficient permissions to read LDAP server '{ldap_name}'."
        )
    else:
        helper.module.fail_json(
            msg=f"Failed to read LDAP server '{ldap_name}', http_status={info['status']}."
        )
    return content


def get_ldap_data(helper):
    """Assemble the data structure for LDAP server configuration."""
    return {
        "name": helper.module.params["ldap_name"],
        "protocol": helper.module.params["ldap_protocol"],
        "useTrustStore": helper.module.params["ldap_use_trust_store"],
        "host": helper.module.params["ldap_host"],
        "port": helper.module.params["ldap_port"],
        "searchBase": helper.module.params["ldap_search_base"],
        "authScheme": helper.module.params["ldap_auth_scheme"],
        "authRealm": helper.module.params["ldap_auth_realm"],
        "authUsername": helper.module.params["ldap_auth_username"],
        "authPassword": helper.module.params["ldap_auth_password"],
        "connectionTimeoutSeconds": helper.module.params[
            "ldap_connection_timeout_seconds"
        ],
        "connectionRetryDelaySeconds": helper.module.params[
            "ldap_connection_retry_delay_seconds"
        ],
        "maxIncidentsCount": helper.module.params["ldap_max_incidents_count"],
        "userBaseDn": helper.module.params["ldap_user_base_dn"],
        "userSubtree": helper.module.params["ldap_user_subtree"],
        "userObjectClass": helper.module.params["ldap_user_object_class"],
        "userLdapFilter": helper.module.params["ldap_user_ldap_filter"],
        "userIdAttribute": helper.module.params["ldap_user_id_attribute"],
        "userRealNameAttribute": helper.module.params["ldap_user_real_name_attribute"],
        "userEmailAddressAttribute": helper.module.params[
            "ldap_user_email_address_attribute"
        ],
        "userPasswordAttribute": helper.module.params["ldap_user_password_attribute"],
        "ldapGroupsAsRoles": helper.module.params["ldap_group_as_roles"],
        "groupType": helper.module.params["ldap_group_type"],
        "groupBaseDn": helper.module.params["ldap_group_base_dn"],
        "groupSubtree": helper.module.params["ldap_group_subtree"],
        "groupObjectClass": helper.module.params["ldap_group_object_class"],
        "groupIdAttribute": helper.module.params["ldap_group_id_attribute"],
        "groupMemberAttribute": helper.module.params["ldap_group_member_attribute"],
        "groupMemberFormat": helper.module.params["ldap_group_member_format"],
        "userMemberOfAttribute": helper.module.params["ldap_user_member_of_attribute"],
    }


def create_ldap_server(helper):
    """Create a new LDAP server."""
    data = get_ldap_data(helper)
    endpoint = "ldap"

    # Check if the LDAP server already exists
    existing_ldap = get_ldap_server(helper)
    if existing_ldap:
        return existing_ldap, False

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"]
        ),
        method="POST",
        data=data,
    )
    if info["status"] == 201:
        content = {
            "msg": f"LDAP server '{helper.module.params['ldap_name']}' created successfully"
        }
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.module.fail_json(
            msg=f"Failed to create LDAP server {helper.module.params['ldap_name']}, \
                http_status={info['status']}, error_msg='{info['msg']}'."
        )
    return content, True


def update_ldap_server(helper, existing_ldap):
    """Update an existing LDAP server if differences are found."""
    data = get_ldap_data(helper)  # Get the desired configuration
    endpoint = "ldap"

    # Use current_ldap_name if specified; otherwise, use the desired ldap_name
    ldap_name = (
        helper.module.params.get("current_ldap_name")
        or helper.module.params["ldap_name"]
    )

    new_existing_ldap = existing_ldap.copy()
    new_existing_ldap.pop("id", None)
    new_existing_ldap.pop("authUsername", None)
    new_existing_ldap.pop("groupSubtree", None)
    new_data = data.copy()
    new_data.pop("authUsername", None)
    new_data.pop("authPassword", None)
    new_data.pop("groupSubtree", None)

    new_existing_ldap = {
        **new_existing_ldap,
        "protocol": (new_existing_ldap.get("protocol") or "").lower(),
    }
    new_existing_ldap = {
        **new_existing_ldap,
        "groupType": (new_existing_ldap.get("groupType") or "").lower(),
    }

    normalized_data = helper.clean_dict_list(new_data)
    normalized_exisiting_data = helper.clean_dict_list(new_existing_ldap)

    changed = not helper.is_json_data_equal(normalized_data, normalized_exisiting_data)

    if (
        changed is False
        and helper.module.params["ldap_auth_username"] == existing_ldap["authUsername"]
        and (
            helper.module.params["ldap_auth_password"] is None
            or helper.module.params["ldap_auth_password"] == ""
        )
    ):
        return existing_ldap, False

    data["id"] = existing_ldap["id"]
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}").format(
            url=helper.module.params["url"],
            name=ldap_name,
        ),
        method="PUT",
        data=data,
    )
    if info["status"] in [204]:
        return data, changed

    if info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg=f"Failed to update LDAP server {ldap_name}, \
                http_status={info['status']}, error_msg='{info.get('msg', 'Unknown error')}'."
        )

    return content, changed


def delete_ldap_server(helper):
    """Delete an existing LDAP server."""
    endpoint = "ldap"
    changed = True
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["ldap_name"],
        ),
        method="DELETE",
    )
    if info["status"] in [404]:
        return {}, False

    if info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.module.fail_json(
            msg=f"Failed to delete LDAP server {helper.module.params['ldap_name']}, \
                http_status={info['status']}, error_msg='{info['msg']}'."
        )
    elif info["status"] == 204:
        content = {
            "msg": f"LDAP server '{helper.module.params['ldap_name']}' deleted successfully"
        }
    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        {
            "method": {"type": "str", "choices": ["GET"], "required": False},
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "required": False,
            },
            "current_ldap_name": {"type": "str", "required": False},
            "ldap_name": {"type": "str", "required": True},
            "url": {"type": "str", "required": True},
            "ldap_protocol": {
                "type": "str",
                "choices": ["ldap", "ldaps"],
                "required": False,
            },
            "ldap_host": {"type": "str", "required": False},
            "ldap_port": {"type": "int", "required": False},
            "ldap_search_base": {"type": "str", "required": False},
            "ldap_auth_scheme": {
                "type": "str",
                "choices": ["NONE", "SIMPLE", "DIGEST_MD5", "CRAM_MD5"],
                "required": False,
            },
            "ldap_connection_timeout_seconds": {"type": "int", "required": False},
            "ldap_connection_retry_delay_seconds": {"type": "int", "required": False},
            "ldap_max_incidents_count": {"type": "int", "required": False},
            "ldap_auth_password": {"type": "str", "required": False, "no_log": True},
            "ldap_group_type": {
                "type": "str",
                "choices": ["static", "dynamic"],
                "required": False,
            },
            "ldap_auth_realm": {"type": "str", "required": False},
            "ldap_auth_username": {"type": "str", "required": False},
            "ldap_user_member_of_attribute": {"type": "str", "required": False},
            "ldap_use_trust_store": {
                "type": "bool",
                "required": False,
                "default": False,
            },
            "ldap_user_base_dn": {"type": "str", "required": False},
            "ldap_user_subtree": {"type": "bool", "required": False, "default": False},
            "ldap_user_object_class": {"type": "str", "required": False},
            "ldap_user_ldap_filter": {"type": "str", "required": False},
            "ldap_user_id_attribute": {"type": "str", "required": False},
            "ldap_user_real_name_attribute": {"type": "str", "required": False},
            "ldap_user_email_address_attribute": {"type": "str", "required": False},
            "ldap_user_password_attribute": {
                "type": "str",
                "required": False,
                "no_log": True,
            },
            "ldap_group_as_roles": {
                "type": "bool",
                "required": False,
                "default": False,
            },
            "ldap_group_base_dn": {"type": "str", "required": False},
            "ldap_group_subtree": {"type": "bool", "required": False, "default": False},
            "ldap_group_object_class": {"type": "str", "required": False},
            "ldap_group_id_attribute": {"type": "str", "required": False},
            "ldap_group_member_attribute": {"type": "str", "required": False},
            "ldap_group_member_format": {"type": "str", "required": False},
        }
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )

    helper = NexusHelper(module)

    content = {}
    changed = False

    if module.params["method"] == "GET":  # type: ignore
        existing_ldap = get_ldap_server(helper)
        content = existing_ldap if existing_ldap else {}
    else:
        existing_ldap = get_ldap_server(helper)
        if module.params["state"] == "present":  # type: ignore
            if existing_ldap:
                content, changed = update_ldap_server(helper, existing_ldap)
            else:
                content, changed = create_ldap_server(helper)
        else:  # state == "absent"
            if existing_ldap:
                content, changed = delete_ldap_server(helper)
                module.params["state"] = "absent"  # type: ignore
            else:
                changed = False

    result = NexusHelper.generate_result_struct()
    result["json"] = content
    result["changed"] = changed
    module.exit_json(**result)


if __name__ == "__main__":
    main()
