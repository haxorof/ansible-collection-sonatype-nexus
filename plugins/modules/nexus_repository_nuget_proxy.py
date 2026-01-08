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
module: nexus_repository_nuget_proxy
short_description: Manage NuGet proxy repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def existing_data_normalization(normalized_existing_data):
    if normalized_existing_data.get("storage"):  # type: ignore
        normalized_existing_data["storage"].pop("writePolicy", None)  # type: ignore
    return normalized_existing_data


def main():
    NexusRepositoryHelper.generic_repository_proxy_module(
        endpoint_path="/nuget/proxy",
        existing_data_normalization=existing_data_normalization,
        arg_additions={
            "nuget_proxy": {
                "type": "dict",
                "apply_defaults": True,
                "options": {
                    "query_cache_item_max_age": {"type": "int", "default": 3600},
                    "nuget_version": {
                        "type": "str",
                        "choices": ["V2", "V3"],
                        "default": "V3",
                    },
                },
            },
        },
        request_data_additions={"nuget_proxy": "camalize"},
    )


if __name__ == "__main__":
    main()
