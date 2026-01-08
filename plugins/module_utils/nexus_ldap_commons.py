#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

def get_ldap_server(helper):
    """Retrieve the LDAP server configuration by name."""
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["ldap"] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["ldap_name"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        return content

    if info["status"] in [404]:
        content = {}
    elif info["status"] == 403:
        helper.module.fail_json(
            msg=f"Insufficient permissions to read LDAP server '{helper.module.params['ldap_name']}'."
        )
    else:
        helper.module.fail_json(
            msg=f"Failed to read LDAP server '{helper.module.params['ldap_name']}', http_status={info['status']}."
        )
    return content
