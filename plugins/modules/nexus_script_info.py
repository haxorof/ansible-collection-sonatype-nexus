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
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils import (
    nexus_script_commons,
)

DOCUMENTATION = r"""
---
module: nexus_script_info
short_description: List Nexus scripts
"""

EXAMPLES = r"""
"""
RETURN = r"""
"""


def main():
    argument_spec = NexusHelper.nexus_argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[("username", "password")],
    )
    helper = NexusHelper(module)
    result = NexusHelper.generate_result_struct(
        False, nexus_script_commons.list_scripts(helper)
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
