#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nexus_security_user
short_description: Create/Update/Delete user
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)


def list_users(helper):
    endpoint = "users"
    info, content = helper.request(
        api_url=(
            helper.NEXUS_API_ENDPOINTS[endpoint]
            + helper.generate_url_query(
                {
                    "userId": "user_id",
                }
            )
        ).format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content = content["json"]
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg="Failed to fetch users., http_status={status}.".format(
                status=info["status"],
            )
        )

    return content


def create_user(helper):
    changed = True
    data = {
        "emailAddress": helper.module.params["email_address"],
        "firstName": helper.module.params["first_name"],
        "lastName": helper.module.params["last_name"],
        "password": helper.module.params["user_password"],
        "roles": helper.module.params["roles"],
        "status": helper.module.params["status"],
        "userId": helper.module.params["user_id"],
    }
    endpoint = "users"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
            url=helper.module.params["url"],
        ),
        method="POST",
        data=data,
    )

    if info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.module.fail_json(
            msg="Failed to create user {user}, http_status={http_status}, error_msg='{error_msg}'.".format(
                error_msg=info["msg"],
                http_status=info["status"],
                user=helper.module.params["user_id"],
            )
        )

    return content, changed


def delete_user(helper):
    changed = True
    endpoint = "users"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{user_id}").format(
            url=helper.module.params["url"],
            user_id=helper.module.params["user_id"],
        ),
        method="DELETE",
    )

    if info["status"] in [404]:
        content.pop("fetch_url_retries", None)
        changed = False
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    elif not helper.is_request_status_ok(info):
        helper.module.fail_json(
            msg="Failed to delete {user}., http_status={http_status}, error_msg='{error_msg}'.".format(
                error_msg=info["msg"],
                http_status=info["status"],
                user=helper.module.params["user_id"],
            )
        )

    return content, changed


def update_user(helper, existing_user):
    changed = True
    data = {
        "userId": existing_user["userId"],
        "externalRoles": existing_user["externalRoles"],
        "readOnly": existing_user["readOnly"],
        "source": existing_user["source"],
    }
    if helper.module.params["email_address"]:
        data.update(
            {
                "emailAddress": helper.module.params["email_address"],
            }
        )
    else:
        data.update(
            {
                "emailAddress": existing_user["emailAddress"],
            }
        )
    if helper.module.params["status"]:
        data.update(
            {
                "status": helper.module.params["status"],
            }
        )
    else:
        data.update(
            {
                "status": existing_user["status"],
            }
        )
    if helper.module.params["first_name"]:
        data.update(
            {
                "firstName": helper.module.params["first_name"],
            }
        )
    else:
        data.update(
            {
                "firstName": existing_user["firstName"],
            }
        )
    if helper.module.params["last_name"]:
        data.update(
            {
                "lastName": helper.module.params["last_name"],
            }
        )
    else:
        data.update(
            {
                "lastName": existing_user["lastName"],
            }
        )
    if helper.module.params["roles"]:
        data.update(
            {
                "roles": helper.module.params["roles"],
            }
        )
    else:
        data.update(
            {
                "roles": existing_user["roles"],
            }
        )
    endpoint = "users"
    if helper.is_json_data_equal(data, existing_user):
        return existing_user, False

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{user_id}").format(
            url=helper.module.params["url"],
            user_id=helper.module.params["user_id"],
        ),
        method="PUT",
        data=data,
    )

    if info["status"] in [204]:
        content = data
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg="Failed to update user {user}., http_status={http_status}, error_msg='{error_msg}'.".format(
                error_msg=info["msg"],
                http_status=info["status"],
                user=helper.module.params["user_id"],
            )
        )

    return content, changed


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        email_address=dict(type="str", required=False, no_log=False),
        first_name=dict(type="str", required=False, no_log=False),
        last_name=dict(type="str", required=False, no_log=False),
        roles=dict(
            type="list", elements="str", required=False, no_log=False, default=list()
        ),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        status=dict(
            type="str",
            required=False,
            no_log=False,
            default="active",
            choices=["active", "disabled"],  # , "locked", "changepassword"
        ),
        user_id=dict(type="str", required=True, no_log=False),
        user_password=dict(type="str", required=False, no_log=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
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
    changed = True
    existing_user = list_users(helper)
    if len(existing_user) > 0:
        if module.params["state"] == "present":
            content, changed = update_user(helper, existing_user[0])
        else:
            content, changed = delete_user(helper)
    else:
        if module.params["state"] == "present":
            content, changed = create_user(helper)
        else:
            changed = False
    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()
