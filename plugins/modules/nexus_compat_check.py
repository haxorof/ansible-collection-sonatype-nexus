#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

from packaging.version import Version
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusVersion,
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


def get_compatibility_notes(nexus_version: NexusVersion) -> list:
    pro_modules = [
        "nexus_cleanup_policies",
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
    if Version(nexus_version.version) < Version("3.87.0"):
        # NEXUS-43742 – Cleanup policies in Sonatype Nexus Repository can
        #               now be created via the REST API for all formats
        #               using "*" as the format value, ensuring support
        #               for automated, multi-format policy management.
        compatibility_notes.append(
            "[3.87.0] nexus_cleanup_policies will not handle '*' format correctly (NEXUS-43742)."
        )
    if Version(nexus_version.version) < Version("3.82.0"):
        # New Cleanup PoCapabilities API to view, create, update, and delete capabilities.
        compatibility_notes.append(
            "[3.82.0] nexus_capabilities will not work due to missing Capabilities API."
        )
    if Version(nexus_version.version) < Version("3.70.0"):
        # New Cleanup Policies API.
        # https://help.sonatype.com/en/sonatype-nexus-repository-3-70-0-release-notes.html
        compatibility_notes.append(
            "[3.70.0] nexus_cleanup_policies will not work due to missing Cleanup Policies API."
        )

    if nexus_version.edition == "COMMUNITY":
        compatibility_notes.append(
            "Some modules will not work that requires PRO edition of Nexus: "
            + ", ".join(pro_modules)
            + "."
        )

    return compatibility_notes


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[("username", "password")],
    )

    helper = NexusHelper(module)
    content = {}
    nexus_version:NexusVersion = helper.get_nexus_version(helper.module.params["url"])
    if nexus_version:
        compatibility_notes = get_compatibility_notes(nexus_version)
        content = {
            "version": nexus_version.version,
            "edition": nexus_version.edition,
            "compatiblity_notes": compatibility_notes,
        }
    else:
        helper.module.fail_json(msg="Failed to get Nexus version information.")

    result = NexusHelper.generate_result_struct(False, content)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
