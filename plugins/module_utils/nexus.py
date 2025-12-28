#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

from __future__ import absolute_import, division, print_function

# pylint: disable-next=invalid-name
__metaclass__ = type

import json
import time
import humps

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url, basic_auth_header


class NexusHelper:
    """General Nexus Helper Class"""

    NEXUS_API_URL = "http://localhost:8081"
    NEXUS_API_BASE_PATH = "/service/rest"

    NEXUS_API_ENDPOINTS = {
        "anonymous": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/anonymous",
        "blobstores": "{url}" + NEXUS_API_BASE_PATH + "/v1/blobstores",
        "capabilities": "{url}" + NEXUS_API_BASE_PATH + "/v1/capabilities",
        "cleanup-policies": "{url}" + NEXUS_API_BASE_PATH + "/internal/cleanup-policies",
        "email": "{url}" + NEXUS_API_BASE_PATH + "/v1/email",
        "http": "{url}" + NEXUS_API_BASE_PATH + "/v1/http",
        "ldap": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/ldap",
        "license": "{url}" + NEXUS_API_BASE_PATH + "/v1/system/license",
        "read-only": "{url}" + NEXUS_API_BASE_PATH + "/v1/read-only",
        "repositories": "{url}" + NEXUS_API_BASE_PATH + "/v1/repositories",
        "repository-settings": "{url}" + NEXUS_API_BASE_PATH + "/v1/repositorySettings",
        "roles": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/roles",
        "routing-rules": "{url}" + NEXUS_API_BASE_PATH + "/v1/routing-rules",
        "script": "{url}" + NEXUS_API_BASE_PATH + "/v1/script",
        "secret-encryption": "{url}" + NEXUS_API_BASE_PATH + "/v1/secrets/encryption/re-encrypt",
        "status": "{url}" + NEXUS_API_BASE_PATH + "/v1/status",
        "tasks": "{url}" + NEXUS_API_BASE_PATH + "/v1/tasks",
        "user-sources": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/user-sources",
        "users": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/users",
        "user-tokens": "{url}" + NEXUS_API_BASE_PATH + "/v1/security/user-tokens",
    }

    @staticmethod
    def camalize_param(helper, param_name, ret_default=None):
        ret_value = (
            ret_default
            if helper.module.params[param_name] is None
            else humps.camelize(helper.module.params[param_name])
        )
        return ret_value

    @staticmethod
    def generate_result_struct(additions=None):
        result = {
            "changed": False,
            "messages": [],
            "json": {},
        }
        if additions:
            result.update(additions)
        return result

    @staticmethod
    def nexus_argument_spec():
        """Common module arguments"""
        return {
            "url": {"type": "str", "no_log": False, "required": False},
            "username": {
                "type": "str",
                "no_log": False,
                "required": False,
                "default": None,
                "fallback": (env_fallback, ["NEXUS_USERNAME"]),
            },
            "password": {
                "type": "str",
                "no_log": True,
                "required": False,
                "default": None,
                "fallback": (env_fallback, ["NEXUS_PASSWORD"]),
            },
            "validate_certs": {"type": "bool", "default": True},
            "use_proxy": {"type": "bool", "default": True},
            "return_content": {"type": "bool", "default": True},
            "sleep": {"type": "int", "default": 5},
            "retries": {"type": "int", "default": 3},
        }

    def __init__(self, module):
        self.module = module
        self.module.params["url_username"] = self.module.params["username"]
        self.module.params["url_password"] = self.module.params["password"]
        if self.module.params["url"] is None:
            self.module.params["url"] = self.NEXUS_API_URL

    def generic_permission_failure_msg(self):
        self.module.fail_json(
            msg="The user does not have permission to perform the operation."
        )

    def generic_failure_msg(self, message, request_info):
        self.module.fail_json(
            msg=message
            + f", \
                http_status={request_info['status']}, \
                error_msg={request_info['msg']}, \
                body={request_info['body']}."
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
            if "Content-type" not in headers:
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
                except ValueError:
                    content["content"] = body

        if not self.is_request_status_ok(info):
            content["fetch_url_retries"] = retries

        if info["status"] == 401:
            self.module.fail_json(msg="Authentication required.")
        elif info["status"] in [503]:
            self.module.fail_json(msg="Unavailable to service requests.")

        # For debugging
        # if info['status'] not in [200]:
        #     self.module.fail_json(msg="{info} # {content}".format(info=info, content=content))
        return info, content

    def is_request_status_ok(self, info):
        return info["status"] in [200, 201, 204]

    def generate_url_query(self, params: dict):
        """Generates a complete URL query including question mark.

        Args:
            params (dict): A dictionary with query parameter key and what module parameter
                to map it with

        Returns:
            string: Returns a query as a string including question mark in front.
        """
        query_params = []
        for k, v in params.items():
            if self.module.params[v] is not None:
                query_params.append(f"{k}={self.module.params[v]}")
        query = "&".join(query_params)
        return "?" + query if len(query) > 0 else ""

    def is_json_data_equal(self, new_data, existing_data):
        # Handle case where both are dicts
        if isinstance(new_data, dict) and isinstance(existing_data, dict):
            # Case: 'password' only in new_data
            if "password" not in existing_data and "password" in new_data:
                return False
            # Case: 'password' in both and masked in existing_data
            if "password" in new_data and "password" in existing_data:
                new_data = new_data.copy()
                existing_data = existing_data.copy()
                new_data.pop("password", None)
                existing_data.pop("password", None)
            # Compare keys
            if set(new_data.keys()) != set(existing_data.keys()):
                return False
            # Recursively compare values
            return all(
                self.is_json_data_equal(new_data[k], existing_data[k]) for k in new_data
            )
        # Handle case where both are lists
        if isinstance(new_data, list) and isinstance(existing_data, list):
            # Normalize and sort lists for comparison
            new_normalized = sorted([str(item).strip() for item in new_data])
            existing_normalized = sorted([str(item).strip() for item in existing_data])
            return new_normalized == existing_normalized
        # Fallback to direct comparison
        return new_data == existing_data

    def clean_dict_list(self, d):
        if isinstance(d, dict):
            cleaned = {}
            for k, v in d.items():
                cleaned_value = self.clean_dict_list(v)
                if cleaned_value not in ("", [], {}, None):
                    cleaned[k] = cleaned_value
            return cleaned
        if isinstance(d, list):
            return [self.clean_dict_list(i) for i in d if i not in ("", [], {}, None)]
        return d


class NexusRepositoryHelper:

    @staticmethod
    def storage_argument_spec():
        return {
            "type": "dict",
            "options": {
                "blob_store_name": {
                    "type": "str",
                    "no_log": False,
                    "required": False,
                },  # Required for create
                "strict_content_type_validation": {"type": "bool", "default": True},
            },
        }

    @staticmethod
    def storage_argument_spec_hosted():
        storage_arg_spec_hosted = NexusRepositoryHelper.storage_argument_spec_common()
        storage_arg_spec_hosted["options"]["latest_policy"] = {
            "type": "bool",
            "default": False,
        }
        return storage_arg_spec_hosted

    @staticmethod
    def storage_argument_spec_common():
        return {
            "type": "dict",
            "options": {
                "blob_store_name": {"type": "str", "required": False},
                "strict_content_type_validation": {"type": "bool", "default": False},
                "write_policy": {
                    "type": "str",
                    "choices": ["ALLOW", "ALLOW_ONCE", "DENY"],
                    "default": "ALLOW",
                },
            },
        }

    @staticmethod
    def cleanup_policy_argument_spec():
        return {
            "type": "dict",
            "options": {
                "policy_names": {
                    "type": "list",
                    "elements": "str",
                    "required": False,
                    "no_log": False,
                    "default": [],
                },
            },
        }

    @staticmethod
    def proxy_argument_spec():
        return {
            "type": "dict",
            "options": {
                "remote_url": {
                    "type": "str",
                    "no_log": False,
                    "required": False,
                },  # Required for create/update
                "content_max_age": {"type": "int", "default": 1440},
                "metadata_max_age": {"type": "int", "default": 1440},
            },
        }

    @staticmethod
    def negative_cache_argument_spec():
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "enabled": {"type": "bool", "default": True},
                "time_to_live": {"type": "int", "default": 1440},
            },
        }

    @staticmethod
    def http_client_argument_spec():
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "blocked": {"type": "bool", "default": False},
                "auto_block": {"type": "bool", "default": True},
                "connection": {
                    "type": "dict",
                    "apply_defaults": True,
                    "options": {
                        "retries": {"type": "int"},
                        "user_agent_suffix": {
                            "type": "str",
                            "no_log": False,
                            "required": False,
                        },
                        "timeout": {"type": "int"},
                        "enable_circular_redirects": {"type": "bool", "default": False},
                        "enable_cookies": {"type": "bool", "default": False},
                        "use_trust_store": {"type": "bool", "default": False},
                    },
                },
                "authentication": {
                    "type": "dict",
                    "options": {
                        "type": {"type": "str", "no_log": False, "required": False},
                        "username": {"type": "str", "no_log": False, "required": False},
                        "password": {"type": "str", "no_log": True, "required": False},
                        "ntlmHost": {"type": "str", "no_log": False, "required": False},
                        "ntlmDomain": {
                            "type": "str",
                            "no_log": False,
                            "required": False,
                        },
                        "preemptive": {"type": "bool", "default": False},
                    },
                },
            },
        }

    @staticmethod
    def replication_argument_spec():
        return {
            "type": "dict",
            "options": {
                "preemptive_pull_enabled": {"type": "bool", "default": False},
                "asset_path_regex": {"type": "str", "no_log": False, "required": False},
            },
        }

    @staticmethod
    def common_proxy_argument_spec(endpoint_path_to_use):
        # Format with both write_policy + latest_policy
        hosted_with_latest = ["/docker/hosted"]
        # Format with write_policy
        hosted_with_common = [
            "/maven/hosted",
            "/npm/hosted",
            "/raw/hosted",
            "/helm/hosted",
            "/nuget/hosted",
            "/pypi/hosted",
            "/rubygems/hosted",
        ]
        if any(path in endpoint_path_to_use for path in hosted_with_latest):
            storage_spec = NexusRepositoryHelper.storage_argument_spec_hosted()
        elif any(path in endpoint_path_to_use for path in hosted_with_common):
            storage_spec = NexusRepositoryHelper.storage_argument_spec_common()
        else:
            storage_spec = NexusRepositoryHelper.storage_argument_spec()

        return {
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
            "name": {"type": "str", "no_log": False, "required": True},
            "online": {"type": "bool", "default": True},
            "cleanup": NexusRepositoryHelper.cleanup_policy_argument_spec(),
            "proxy": NexusRepositoryHelper.proxy_argument_spec(),
            "negative_cache": NexusRepositoryHelper.negative_cache_argument_spec(),
            "http_client": NexusRepositoryHelper.http_client_argument_spec(),
            "routing_rule": {"type": "str", "no_log": False, "required": False},
            "replication": NexusRepositoryHelper.replication_argument_spec(),
            "storage": storage_spec,
        }

    @staticmethod
    def list_repositories(helper):
        endpoint = "repository-settings"
        info, content = helper.request(
            api_url=(helper.NEXUS_API_ENDPOINTS[endpoint]).format(
                url=helper.module.params["url"],
            ),
            method="GET",
        )
        if info["status"] in [200]:
            content = content["json"]
        else:
            helper.generic_failure_msg("Failed to list repositories", info)
        return content

    @staticmethod
    def list_filtered_repositories(helper, repository_filter):
        content = NexusRepositoryHelper.list_repositories(helper)
        content = list(filter(lambda item: repository_filter(item, helper), content))
        return content

    @staticmethod
    def create_repository(helper, endpoint_path, additional_data):
        changed = True
        data = {
            "name": helper.module.params["name"],
            "online": helper.module.params["online"],
            "storage": NexusHelper.camalize_param(helper, "storage"),
            "cleanup": NexusHelper.camalize_param(helper, "cleanup"),
            "proxy": NexusHelper.camalize_param(helper, "proxy"),
            "negativeCache": NexusHelper.camalize_param(helper, "negative_cache"),
            "httpClient": NexusHelper.camalize_param(helper, "http_client"),
            "routingRule": helper.module.params["routing_rule"],
        }
        data.update(additional_data)
        # helper.module.fail_json(
        #     msg="{data}".format(
        #         data=data,
        #     )
        # )
        endpoint = "repositories"
        info, content = helper.request(
            api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + endpoint_path).format(
                url=helper.module.params["url"],
            ),
            method="POST",
            data=data,
        )

        if info["status"] not in [201]:
            if info["status"] == 401:
                helper.module.fail_json(msg="Authentication required.")
            elif info["status"] == 403:
                helper.generic_permission_failure_msg()
            else:
                helper.module.fail_json(
                    msg=f"Failed to create repository {helper.module.params['name']}, \
                        http_status={info['status']}, error_msg='{info['msg']}, body={info['body']}'."
                )

        return content, changed

    @staticmethod
    def update_repository(helper, endpoint_path, additional_data, existing_data):
        endpoint = "repositories"
        data = {
            "name": helper.module.params["name"],
            "online": helper.module.params["online"],
            "storage": NexusHelper.camalize_param(helper, "storage"),
            "cleanup": NexusHelper.camalize_param(helper, "cleanup"),
            "proxy": NexusHelper.camalize_param(helper, "proxy"),
            "negativeCache": NexusHelper.camalize_param(helper, "negative_cache"),
            "httpClient": NexusHelper.camalize_param(helper, "http_client"),
            "routingRule": helper.module.params["routing_rule"],
        }
        data.update(additional_data)

        if "hosted" in endpoint_path:
            # Clean up unwanted fields that should not be updated or are part of Nexus's default config
            existing_data.pop("format", None)
            existing_data.pop("type", None)
            existing_data.pop("url", None)
            data.pop("httpClient", None)
            data.pop("negativeCache", None)
            if "/docker/hosted" in endpoint_path:
                if isinstance(existing_data, dict) and isinstance(
                    existing_data.get("storage"), dict
                ):
                    existing_data["storage"].setdefault("latestPolicy", False)
            if "/nuget/hosted" not in endpoint_path:
                existing_data.pop("component", None)

        if "proxy" in endpoint_path:
            # Clean up unwanted fields that should not be updated or are part of Nexus's default config
            existing_data["storage"].pop("writePolicy", None)
            existing_data.pop("format", None)
            existing_data.pop("type", None)
            existing_data.pop("url", None)
            existing_data.update(
                {"routingRule": existing_data.pop("routingRuleName", None)}
            )
            if (
                isinstance(data, dict)
                and isinstance(data.get("httpClient"), dict)
                and isinstance(data["httpClient"].get("authentication"), dict)
            ):
                data["httpClient"]["authentication"].pop("preemptive", None)

        if "group" in endpoint_path:
            # Clean up unwanted fields that should not be updated or are part of Nexus's default config
            existing_data.pop("format", None)
            existing_data.pop("type", None)
            existing_data.pop("url", None)
            # existing_data.pop("online", None)
            data.pop("httpClient", None)
            data.pop("negativeCache", None)
            if "/raw/group" in endpoint_path:
                existing_data["storage"].pop("writePolicy", None)

        # Ensure data is a dictionary and contains the password
        password = None
        if (
            isinstance(data, dict)
            and isinstance(data.get("httpClient"), dict)
            and isinstance(data["httpClient"].get("authentication"), dict)
        ):
            password = data["httpClient"]["authentication"].get("password")
            if password:
                # Ensure existing_data has the correct nested structure
                if not isinstance(existing_data.get("httpClient"), dict):
                    existing_data["httpClient"] = {}
                if not isinstance(
                    existing_data["httpClient"].get("authentication"), dict
                ):
                    existing_data["httpClient"]["authentication"] = {}

                existing_data["httpClient"]["authentication"]["password"] = password

        normalized_data = helper.clean_dict_list(data)
        normalized_exisiting_data = helper.clean_dict_list(existing_data)

        changed = not helper.is_json_data_equal(
            normalized_data, normalized_exisiting_data
        )

        if not changed and password is None:
            return existing_data, False

        info, content = helper.request(
            api_url=(
                helper.NEXUS_API_ENDPOINTS[endpoint] + "{path}/{repository}"
            ).format(
                url=helper.module.params["url"],
                path=endpoint_path,
                repository=helper.module.params["name"],
            ),
            method="PUT",
            data=data,
        )

        if info["status"] not in [204]:
            if info["status"] == 401:
                helper.module.fail_json(msg="Authentication required.")
            elif info["status"] == 403:
                helper.generic_permission_failure_msg()
            else:
                helper.module.fail_json(
                    msg=f"Failed to update repository {helper.module.params['name']}, \
                        http_status={info['status']}, error_msg='{info['msg']}, body={info['body']}'."
                )

        return content, changed

    @staticmethod
    def delete_repository(helper):
        changed = True
        endpoint = "repositories"
        info, content = helper.request(
            api_url=(helper.NEXUS_API_ENDPOINTS[endpoint] + "/{name}").format(
                url=helper.module.params["url"],
                name=helper.module.params["name"],
            ),
            method="DELETE",
        )

        if info["status"] not in [204]:
            if info["status"] in [404]:
                content.pop("fetch_url_retries", None)
                changed = False
            elif info["status"] == 401:
                helper.module.fail_json(msg="Authentication required.")
            elif info["status"] == 403:
                helper.module.fail_json(
                    msg="The user does not have permission to perform the operation."
                )
            else:
                helper.module.fail_json(
                    msg=f"Failed to delete {helper.module.params['name']}., \
                        http_status={info['status']}, error_msg='{info['msg']}'."
                )

        return content, changed


class NexusBlobstoreHelper:

    @staticmethod
    def common_argument_spec():
        return {
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
            "name": {"type": "str", "no_log": False, "required": True},
            "soft_quota": NexusBlobstoreHelper.soft_quota_argument_spec(),
        }

    @staticmethod
    def soft_quota_argument_spec():
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

    @staticmethod
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

    @staticmethod
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
