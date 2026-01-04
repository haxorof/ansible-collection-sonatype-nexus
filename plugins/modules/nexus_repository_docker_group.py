#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.nexus import (
    NexusRepositoryHelper,
)
from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils import (
    nexus_repository_docker_commons,
)

DOCUMENTATION = r"""
---
module: nexus_repository_docker_group
short_description: Manage Docker group repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def main():
    NexusRepositoryHelper.generic_repository_group_module(
        endpoint_path="/docker/group",
        arg_additions={
            "docker": nexus_repository_docker_commons.docker_attributes(),
        },
        request_data_additions={
            "docker": "camalize",
        },
    )


if __name__ == "__main__":
    main()
