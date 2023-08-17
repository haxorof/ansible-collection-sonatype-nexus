#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import time
import os
import stat

from os import close
from tempfile import mkstemp
from traceback import format_exc

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url, basic_auth_header


class NexusHelper:
    NEXUS_API_URL = "http://localhost:8081"
    NEXUS_API_BASE_PATH = "/service/rest"

    NEXUS_API_ENDPOINTS = {
        "anonymous": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/anonymous",
        # "assets": "{url}" + NEXUS_API_BASE_PATH + "/v1/assets",
        # "azureblobstore": "{url}" + NEXUS_API_BASE_PATH + "/v1/azureblobstore",
        # "blobstores": "{url}" + NEXUS_API_BASE_PATH + "/v1/blobstores",
        # "certificates": "{url}" + NEXUS_API_BASE_PATH + "/v1/ssl",
        # "components": "{url}" + NEXUS_API_BASE_PATH + "/v1/components",
        # "content-selectors": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/content-selectors",
        # "email": "{url}" + NEXUS_API_BASE_PATH + "/v1/email",
        # "formats": "{url}" + NEXUS_API_BASE_PATH + "/v1/formats",
        # "iq": "{url}" + NEXUS_API_BASE_PATH + "/v1/iq",
        # "ldap": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/ldap",
        # "lifecycle": "{url}" + NEXUS_API_BASE_PATH + "/v1/lifecycle",
        # "privileges": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/privileges",
        "read-only": "{url}" + NEXUS_API_BASE_PATH + "/v1/read-only",
        # "realms": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/realms",
        # "repositories": "{url}" + NEXUS_API_BASE_PATH + "/v1/repositories",
        "repository-settings": "{url}" + NEXUS_API_BASE_PATH + "/v1/repositorySettings",
        # "roles": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/roles",
        "routing-rules": "{url}" + NEXUS_API_BASE_PATH + "/v1/routing-rules",
        # "script": "{url}" + NEXUS_API_BASE_PATH + "/v1/script",
        # "search": "{url}" + NEXUS_API_BASE_PATH + "/v1/search",
        "status": "{url}" + NEXUS_API_BASE_PATH + "/v1/status",
        # "support": "{url}" + NEXUS_API_BASE_PATH + "/v1/support",
        # "system": "{url}" + NEXUS_API_BASE_PATH + "/v1/system",
        # "tasks": "{url}" + NEXUS_API_BASE_PATH + "/v1/tasks",
        "user-sources": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/user-sources",
        "users": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/users",
    }

    def __init__(self, module):
        self.module = module
        self.module.params["url_username"] = self.module.params["username"]
        self.module.params["url_password"] = self.module.params["password"]
        if self.module.params["url"] is None:
            self.module.params["url"] = self.NEXUS_API_URL

    @staticmethod
    def nexus_argument_spec():
        return dict(
            url=dict(type="str", no_log=False, required=False),
            username=dict(
                type="str",
                no_log=False,
                required=False,
                default=None,
                aliases=["user"],
                fallback=(env_fallback, ["NEXUS_USERNAME"]),
            ),
            password=dict(
                type="str",
                no_log=True,
                required=False,
                default=None,
                fallback=(env_fallback, ["NEXUS_PASSWORD"]),
            ),
            validate_certs=dict(type="bool", default=True),
            use_proxy=dict(type="bool", default=True),
            return_content=dict(type="bool", default=True),
            sleep=dict(type="int", default=5),
            retries=dict(type="int", default=3),
        )

    def request(self, api_url, method, data=None, headers=None):
        headers = headers or {}

        headers.update(
            {
                "Authorization": basic_auth_header(
                    self.module.params["username"], self.module.params["password"]
                )
            }
        )

        if isinstance(data, dict):
            data = self.module.jsonify(data)
            if not ("Content-type" in headers):
                headers.update(
                    {
                        "Content-type": "application/json",
                    }
                )

        retries = 1
        while retries <= self.module.params["retries"]:
            response, info = fetch_url(
                module=self.module,
                url=api_url,
                method=method,
                headers=headers,
                data=data,
                force=True,
                use_proxy=self.module.params["use_proxy"],
            )
            if (info is not None) and (info["status"] != -1):
                break
            time.sleep(self.module.params["sleep"])
            retries += 1

        content = {}

        if response is not None:
            body = to_text(response.read())
            if body:
                try:
                    js = json.loads(body)
                    if isinstance(js, dict):
                        content = js
                    else:
                        content["json"] = js
                except ValueError as e:
                    content["content"] = body

        content["fetch_url_retries"] = retries

        # For debugging
        # if info["status"] not in [200]:
        #     self.module.fail_json(msg="{info} # {content}".format(info=info, content=content))
        return info, content

    def generate_url_query(self, params: dict):
        """Generates a complete URL query including question mark.

        Args:
            params (dict): A dictionary with query parameter key and what module parameter to map it with

        Returns:
            string: Returns a query as a string including question mark in front.
        """
        query_params = []
        for k, v in params.items():
            if self.module.params[v] != None:
                query_params.append(
                    "{key}={value}".format(key=k, value=self.module.params[v])
                )
        query = "&".join(query_params)
        return "?" + query if len(query) > 0 else ""

    def is_json_data_equal(self, new_data, existing_data):
        return all(
            existing_data[k] == v for k, v in new_data.items() if k in existing_data
        )


class NexusRepositoryHelper:
    def list_repositories(helper):
        endpoint = "repository-settings"
        info, content = helper.request(
            api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
                url=helper.module.params["url"],
            ),
            method="GET",
        )
        if info["status"] in [200]:
            content.pop("fetch_url_retries", None)
            content = content["json"]
        else:
            helper.module.fail_json(
                msg="Failed to list repositories, http_status={http_status}, error_msg='{error_msg}'.".format(
                    http_status=info["status"],
                    error_msg=info["msg"],
                )
            )
        return content

    def list_filtered_repositories(helper, repository_filter):
        content = NexusRepositoryHelper.list_repositories(helper)
        content = list(filter(lambda item: repository_filter(item, helper), content))
        return content
