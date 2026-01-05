#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

import re
from packaging.version import Version
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusHelper,
)

DOCUMENTATION = r"""
---
module: nexus_roles_info
short_description: Retrieve Nexus roles configuration
"""
EXAMPLES = r"""
"""
RETURN = r"""
"""


def get_compatibility_notes(nexus_version: str, nexus_edition: str) -> list:
    pro_modules = [
        "nexus_http",
        "nexus_security_user_token",
    ]
    compatibility_notes = []
    # Information may come from https://help.sonatype.com/en/release-notes.html

    # if Version(nexus_version) < Version("3.88.0"):
    #     # NEXUS-45941 – The REST API for creating Maven group repositories
    #     #               now correctly honors the specified versionPolicy.
    #     compatibility_notes.append(
    #         "[3.88.0] nexus_repository_maven_group will not correctly set " +
    #         "'Version Policy' and it will always be 'Release' " +
    #         "(NEXUS-45941 / https://github.com/sonatype/nexus-public/issues/702)."
    #     )
    if Version(nexus_version) < Version("3.87.0"):
        # NEXUS-43742 – Cleanup policies in Sonatype Nexus Repository can
        #               now be created via the REST API for all formats
        #               using "*" as the format value, ensuring support
        #               for automated, multi-format policy management.
        compatibility_notes.append(
            "[3.87.0] nexus_cleanup_policies will not handle '*' format correctly (NEXUS-43742)."
        )
    if Version(nexus_version) < Version("3.82.0"):
        # New Cleanup PoCapabilities API to view, create, update, and delete capabilities.
        compatibility_notes.append(
            "[3.82.0] nexus_capabilities will not work due to missing Capabilities API."
        )
    if Version(nexus_version) < Version("3.70.0"):
        # New Cleanup Policies API.
        # https://help.sonatype.com/en/sonatype-nexus-repository-3-70-0-release-notes.html
        compatibility_notes.append(
            "[3.70.0] nexus_cleanup_policies will not work due to missing Cleanup Policies API."
        )

    if nexus_edition == "COMMUNITY":
        compatibility_notes.append(
            "Some modules will not work that requires PRO edition of Nexus: "
            + ", ".join(pro_modules)
            + "."
        )

    return compatibility_notes


def get_nexus_version(helper: NexusHelper):
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS["system"] + "/node").format(
            url=helper.module.params["url"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content = info["server"]
    elif info["status"] == 403:
        helper.generic_permission_failure_msg()
    else:
        helper.module.fail_json(
            msg=f"Failed to Nexus version information, http_status={info['status']}."
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
    content = {}
    server_header = get_nexus_version(helper)
    match = re.search(r"Nexus/([^ ]+) \(([^)]+)\)", str(server_header))
    if match:
        nexus_version = match.group(1)
        nexus_edition = match.group(2)
        compatibility_notes = get_compatibility_notes(nexus_version, nexus_edition)
        content = {
            "version": nexus_version,
            "edition": nexus_edition,
            "compatiblity_notes": compatibility_notes,
        }
    else:
        helper.module.fail_json(
            msg=f"Unsupported Nexus server information format in HTTP header detected, server_header={server_header}."
        )

    result = NexusHelper.generate_result_struct(False, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
