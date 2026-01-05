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
    nexus_repository_commons,
)

DOCUMENTATION = r"""
---
module: nexus_repository_docker_hosted
short_description: Manage Docker hosted repositories
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""


def docker_hosted_storage_attributes():
    """Directly maps to DockerHostedStorageAttributes"""
    ret_spec = NexusRepositoryHelper.hosted_storage_attributes()
    ret_spec["options"]["latest_policy"] = {
        "type": "bool",
        "default": False,
    }
    return ret_spec


def main():
    NexusRepositoryHelper.generic_repository_hosted_module(
        endpoint_path="/docker/hosted",
        data_normalization=nexus_repository_commons.hosted_repo_data_normalization,
        arg_additions={
            "docker": nexus_repository_docker_commons.docker_attributes(),
            "storage": docker_hosted_storage_attributes(),
        },
        request_data_additions={
            "docker": "camalize",
        },
    )


if __name__ == "__main__":
    main()
