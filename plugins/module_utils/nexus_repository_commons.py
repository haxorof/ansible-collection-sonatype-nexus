#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

def hosted_repo_data_normalization(input_data, existing_data = None):
    # This is required because API in some Nexus versions will only return latestPolicy if
    # writePolicy is set to ALLOW_ONCE (Disable redeploy).
    if input_data.get("storage"):  # type: ignore
        if (
            existing_data is not None
            and existing_data["storage"].get("latestPolicy") is None
        ):
            input_data["storage"].pop("latestPolicy", None)  # type: ignore
    return input_data

def proxy_repo_data_normalization(input_data, existing_data = None):
    # preserveEncodedCharacters added since 3.90
    if (
        input_data.get("proxy")  # type: ignore
        and existing_data is not None
        and existing_data["proxy"].get("preserveEncodedCharacters") is None
    ):
        input_data["proxy"].pop("preserveEncodedCharacters", None)  # type: ignore
    return input_data
