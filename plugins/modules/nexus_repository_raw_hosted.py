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
module: nexus_repository_raw_hosted
short_description: Manage Raw hosted repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def main():
    NexusRepositoryHelper.generic_repository_hosted_module(
        endpoint_path="/raw/hosted",
        data_normalization=nexus_repository_commons.hosted_repo_data_normalization,
        arg_additions={
            "raw": {
                "type": "dict",
                "apply_defaults": True,
                "options": {
                    "content_disposition": {
                        "type": "str",
                        "choices": ["ATTACHMENT", "INLINE"],
                        "default": "ATTACHMENT",
                    },
                },
            },
        },
        request_data_additions={
            "raw": "camalize",
        },
    )


if __name__ == "__main__":
    main()
