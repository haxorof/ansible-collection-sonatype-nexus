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
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def main():
    NexusRepositoryHelper.generic_repository_proxy_module(
        endpoint_path="/p2/proxy",
    )


if __name__ == "__main__":
    main()
