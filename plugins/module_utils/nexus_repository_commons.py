#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

def hosted_repo_data_normalization(input_data):
    # This is required because API will only return latestPolicy if
    # writePolicy is set to ALLOW_ONCE (Disable redeploy).
    if input_data.get("storage"):  # type: ignore
        if (
            input_data["storage"].get("writePolicy")  # type: ignore
            and input_data["storage"]["writePolicy"]  # type: ignore
            != "ALLOW_ONCE"
        ):
            input_data["storage"].pop("latestPolicy", None)  # type: ignore
    return input_data
