#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

def docker_attributes():
    """ Directly maps to DockerAttributes """
    return {
        "type": "dict",
        "apply_defaults": True,
        "options": {
            "v1_enabled": {"type": "bool", "default": False},
            "force_basic_auth": {"type": "bool", "default": True},
            "http_port": {"type": "int", "required": False},
            "https_port": {"type": "int", "required": False},
            "subdomain": {"type": "str", "required": False},
            "path_enabled": {"type": "bool", "required": False},
        },
    }
