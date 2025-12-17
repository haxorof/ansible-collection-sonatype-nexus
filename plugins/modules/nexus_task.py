#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import NexusHelper

DOCUMENTATION = r"""
---
module: nexus_tasks
short_description: Manage Nexus tasks settings
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

def get_tasks_list(helper):
    endpoint = "tasks"
    task_exists = False
    task_id = None

    _, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "?type=" + "{type}").format(
            url=helper.module.params["url"],
            type=helper.module.params["type"],
        ),
        method="GET",
    )


    # Try to extract the list of tasks from the response
    task_list = []
    if isinstance(content, list):
        task_list = content
    elif isinstance(content, dict):
        # Try common keys that might contain the task list
        task_list = content.get("items") or content.get("tasks") or []
    else:
        helper.module.fail_json(msg="Unexpected response format: expected a list or dict containing tasks.")
    existing_task = None
    for task in task_list:
        if task.get("name") == helper.module.params["name"]:
            task_exists = True
            existing_task = task
            task_id = task.get("id")
            break
    return task_exists, existing_task, task_id

def create_task(helper):
    endpoint = "tasks"
    data = {
        "type": helper.module.params["type"],
        "name": helper.module.params["name"],
        "enabled": helper.module.params["enabled"],
        "alertEmail": helper.module.params["alert_email"],
        "notificationCondition": helper.module.params["notification_condition"],
        "frequency": {
            "schedule": helper.module.params["frequency"]["schedule"],
            "startDate": helper.module.params["frequency"]["start_date"],
            "timeZoneOffset": helper.module.params["frequency"]["time_zone_offset"],
            "recurringDays": helper.module.params["frequency"]["recurring_days"],
            "cronExpression": helper.module.params["frequency"]["cron_expression"],
            },
        "properties": NexusHelper.camalize_param(helper, "properties"),
    }
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS[endpoint].format(url=helper.module.params["url"]),
        method="POST",
        data=data,
    )
    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(
                msg=f"Bad request, error_msg='{info['body']}'."
            )
        elif info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to create task."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to create task , http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, True

def update_task(helper, task_id, existing_data):
    endpoint = "tasks"

    data = {
        "name": helper.module.params["name"],
        "enabled": helper.module.params["enabled"],
        "alertEmail": helper.module.params["alert_email"],
        "notificationCondition": helper.module.params["notification_condition"],
        "frequency": {
            "schedule": helper.module.params["frequency"]["schedule"],
            "startDate": helper.module.params["frequency"]["start_date"],
            "timeZoneOffset": helper.module.params["frequency"]["time_zone_offset"],
            "recurringDays": helper.module.params["frequency"]["recurring_days"],
            "cronExpression": helper.module.params["frequency"]["cron_expression"],
            },
        "properties": NexusHelper.camalize_param(helper, "properties"),
    }

    if existing_data['name'] == data['name']:
        changed = False
    else:
        changed = True

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{task_id}").format(
            url=helper.module.params["url"],
            task_id=task_id,
        ),
        method="PUT",
        data=data,
    )
    if not helper.is_request_status_ok(info):
        if info["status"] == 400:
            helper.module.fail_json(
                msg=f"Bad request, error_msg='{info['body']}'."
            )
        elif info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to update tasks."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to update tasks, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, changed

def delete_task(helper, task_id ):
    endpoint = "tasks"

    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{task_id}").format(
            url=helper.module.params["url"],
            task_id=task_id,
        ),
        method="DELETE"
    )

    if not helper.is_request_status_ok(info):
        if info["status"] == 403:
            helper.module.fail_json(
                msg="Insufficient permissions to delete task."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to delete task, http_status={info['status']}, error_msg='{info['msg']}'."
            )

    return content, True

def main():
    frequency_options = {
        "schedule": {"type": "str", "choices": ["manual", "once", "hourly", "daily", "weekly", "monthly", "cron"], "required": True},
        "start_date": {"type": "int", "default": None},
        "time_zone_offset": {"type": "str", "default": ""},
        "recurring_days": {"type": "list", "default": []},
        "cron_expression": {"type": "str", "default": ""},
    }
    argument_spec = NexusHelper.nexus_argument_spec()
    argument_spec.update(
        state={"type": "str", "choices": ["present", "absent"], "default": "present"},
        type={"type": "str", "required": True},
        name={"type": "str", "required": True},
        enabled={"type": "bool", "required": False, "default": True},
        alert_email={"type": "str", "required": False, "default": ""},
        notification_condition={"type": "str", "required": False, "choices": ["FAILURE", "SUCCESS_FAILURE"], "default": "FAILURE"},
        frequency={"type": "dict", "required": True,  "options": frequency_options},
        properties={"type": "dict", "required": False, "default": {}},

    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)

    # Seed the result dict in the object
    result = {
        "changed": False,
        "state": module.params["state"],
        "messages": [],
        "json": {},
    }
    content = {}
    changed = True
    task_exists, existing_task, task_id = get_tasks_list(helper)

    if module.params["state"] == "present":
        if task_exists is True:
            content, changed = update_task(helper, task_id, existing_task)
        else:
            content, changed = create_task(helper)
    else:
        if task_exists is True:
            content, changed = delete_task(helper, task_id)
        else:
            changed = False

    result["json"] = content
    result["changed"] = changed

    module.exit_json(**result)

if __name__ == "__main__":
    main()
