#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

def list_scripts(helper):
    info, content = helper.request(
        api_url=helper.NEXUS_API_ENDPOINTS["script"].format(
            url=helper.module.params["url"]
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content = content["json"]
    elif info["status"] == 403:
        helper.module.fail_json(msg="Insufficient permissions to read scripts.")
    else:
        helper.module.fail_json(
            msg=f"Failed to read scripts, http_status={info['status']}."
        )
    return content
