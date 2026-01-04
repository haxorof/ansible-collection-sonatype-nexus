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

DOCUMENTATION = r"""
---
module: nexus_repository_npm_group
short_description: Manage NPM group repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def repository_filter(item, helper):
    return item["name"] == helper.module.params["name"]


def main():
    NexusRepositoryHelper.generic_repository_group_module(
        endpoint_path="/npm/group",
        repository_filter=repository_filter,
    )


if __name__ == "__main__":
    main()
