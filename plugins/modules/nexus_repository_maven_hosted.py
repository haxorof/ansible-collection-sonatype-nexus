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
    nexus_repository_commons,
)

DOCUMENTATION = r"""
---
module: nexus_repository_maven_hosted
short_description: Manage hosted Maven repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def main():
    NexusRepositoryHelper.generic_repository_hosted_module(
        endpoint_path="/maven/hosted",
        data_normalization=nexus_repository_commons.hosted_repo_data_normalization,
        arg_additions={
            "maven": {
                "type": "dict",
                "apply_defaults": True,
                "options": {
                    "version_policy": {
                        "type": "str",
                        "choices": ["RELEASE", "SNAPSHOT", "MIXED"],
                        "default": "RELEASE",
                    },
                    "layout_policy": {
                        "type": "str",
                        "choices": ["STRICT", "PERMISSIVE"],
                        "default": "STRICT",
                    },
                    "content_disposition": {
                        "type": "str",
                        "choices": ["INLINE", "ATTACHMENT"],
                        "default": "INLINE",
                    },
                },
            },
        },
        request_data_additions={
            "maven": "camalize",
        },
    )


if __name__ == "__main__":
    main()
