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
module: nexus_repository_npm_proxy
short_description: Manage NPM proxy repositories
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
        endpoint_path="/npm/proxy",
        existing_data_normalization=existing_data_normalization,
        arg_additions={
            "npm": {
                "type": "dict",
                "apply_defaults": True,
                "options": {
                    "remove_quarantined": {"type": "bool", "default": False},
                },
            },
        },
        request_data_additions={"npm": "camalize"},
    )


if __name__ == "__main__":
    main()
