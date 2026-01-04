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
module: nexus_repository_docker_proxy
short_description: Manage Docker proxy repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def repository_filter(item, helper):
    return item["name"] == helper.module.params["name"]


def existing_data_normalization(normalized_existing_data):
    if normalized_existing_data.get("storage"):  # type: ignore
        normalized_existing_data["storage"].pop("writePolicy", None)  # type: ignore
    return normalized_existing_data


def docker_proxy_attributes():
    return {
        "type": "dict",
        "apply_defaults": True,
        "options": {
            "index_type": {
                "type": "str",
                "choices": ["HUB", "REGISTRY", "CUSTOM"],
                "default": "REGISTRY",
            },
            "index_url": {"type": "str", "required": False, "no_log": False},
            "cache_foreign_layers": {"type": "bool", "default": False},
            "foreign_layer_url_whitelist": {
                "type": "list",
                "elements": "str",
                "required": False,
                "no_log": False,
                "default": [],
            },
        },
    }


def main():
    NexusRepositoryHelper.generic_repository_proxy_module(
        endpoint_path="/docker/proxy",
        repository_filter=repository_filter,
        existing_data_normalization=existing_data_normalization,
        arg_additions={
            "docker": nexus_repository_docker_commons.docker_attributes(),
            "docker_proxy": docker_proxy_attributes(),
        },
        request_data_additions={
            "docker": "camalize",
            "docker_proxy": "camalize",
        },
    )


if __name__ == "__main__":
    main()
