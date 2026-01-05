#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type


def file_blob_store_api_model():
    """Directly maps to FileBlobStoreApiModel"""
    return {
        "soft_quota": soft_quota_argument_spec(),
        "path": {"type": "str", "required": False, "no_log": False},
    }


def soft_quota_argument_spec():
    """Directly maps to BlobStoreApiSoftQuota"""
    return {
        "type": "dict",
        "apply_defaults": False,
        "options": {
            "type": {
                "type": "str",
                "choices": ["spaceRemainingQuota", "spaceUsedQuota "],
                "default": "spaceRemainingQuota",
            },
            "limit": {"type": "int", "default": 0},
        },
    }


def get_blobstore(helper, blobstore_type):
    endpoint = "blobstores"
    info, content = helper.request(
        api_url=(
            helper.NEXUS_API_ENDPOINTS[endpoint] + "/" + blobstore_type + "/{name}"
        ).format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="GET",
    )
    if info["status"] in [200]:
        content = [content]
    elif info["status"] in [404]:
        content = []
    elif info["status"] == 403:
        helper.module.fail_json(
            msg=f"Insufficient permissions to read configuration for blob store '{helper.module.params['name']}' \
                of type '{blobstore_type}'."
        )
    else:
        helper.module.fail_json(
            msg=f"Failed to read configration for blob store '{helper.module.params['name']}' \
                of type '{blobstore_type}', http_status={info['status']}, error_msg='{info['msg']}."
        )
    return content


def delete_blobstore(helper):
    changed = True
    endpoint = "blobstores"
    info, content = helper.request(
        api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}").format(
            url=helper.module.params["url"],
            name=helper.module.params["name"],
        ),
        method="DELETE",
    )
    if info["status"] not in [204]:
        if info["status"] in [404]:
            changed = False
        elif info["status"] == 403:
            helper.module.fail_json(
                msg=f"Insufficient permissions to delete blob store '{helper.module.params['name']}'."
            )
        else:
            helper.module.fail_json(
                msg=f"Failed to delete blob store '{helper.module.params['name']}', \
                    http_status={info['status']}, error_msg='{info['msg']}."
            )

    return content, changed
