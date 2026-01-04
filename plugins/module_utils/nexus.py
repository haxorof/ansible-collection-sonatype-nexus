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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url, basic_auth_header

def repository_name_filter(item, helper):
    return item["name"] == helper.module.params["name"]
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
        if not param_name:
            raise ValueError(
                "Bug: Cannot be empty param_name into camalize_param method!"
            )
        ret_value = (
            ret_default
            if not helper.module.params[param_name]
            else humps.camelize(helper.module.params[param_name])
        )
        return ret_value

    @staticmethod
    def generate_result_struct(
        changed: bool = False, json_data=None, messages=None, result_additions=None
    ) -> dict:
        if json_data is None:
            json_data = {}
        if messages is None:
            messages = []
        result = {
            "changed": changed,
            "json": json_data,
            "messages": messages,
        }
        if result_additions:
            result.update(result_additions)
        return result

    @staticmethod
    def nexus_argument_spec():
        """Common module arguments"""
        return {
            "url": {
                "type": "str",
                "no_log": False,
                "default": NexusHelper.NEXUS_API_URL,
                "fallback": (env_fallback, ["NEXUS_URL"]),
            },
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
            "validate_certs": {
                "type": "bool",
                "default": True,
                "fallback": (env_fallback, ["NEXUS_VALIDATE_CERTS"]),
            },
            "use_proxy": {"type": "bool", "default": True},
            "return_content": {"type": "bool", "default": True},
            "sleep": {"type": "int", "default": 0},
            "retries": {"type": "int", "default": 1},
        }

    def __init__(self, module):
        self.module = module
        self.module.params["url_username"] = self.module.params["username"]
        self.module.params["url_password"] = self.module.params["password"]
        if not self.module.params["url"]:
            self.module.params["url"] = self.NEXUS_API_URL

    def generic_authn_failure_msg(self):
        self.module.fail_json(msg="Authentication required.")

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

    # pylint: disable-next=too-many-branches
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
        response = None
        info = {}
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
            if info and info["status"] != -1:
                break
            time.sleep(self.module.params["sleep"])
            retries += 1

        content = {}

        if response:
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
        elif info["status"] in [503, 500]:
            self.module.fail_json(msg="Unavailable to service requests.")
        elif info["status"] == -1:
            self.module.fail_json(msg=info['msg'])

        # For debugging
        # if info['status'] not in [200]:
        #     self.module.fail_json(msg="{info} # {content}".format(info=info, content=content))
        return info, content

    def is_request_status_ok(self, info) -> bool:
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
        """ Compares JSON data and is considered equal if all keys and its values in new_data exists in existing_data.

        Args:
            new_data (_type_): new data.
            existing_data (_type_): existing data.

        Returns:
            _type_: Returns true if all keys and its values in new_data exists in existing_data.
        """
        return all(
            existing_data[k] == v for k, v in new_data.items() if k in existing_data
        )

    # def is_json_data_equal(self, new_data, existing_data):
    #     # Handle case where both are dicts
    #     if isinstance(new_data, dict) and isinstance(existing_data, dict):
    #         # Case: 'password' only in new_data
    #         if "password" not in existing_data and "password" in new_data:
    #             return False
    #         # Case: 'password' in both and masked in existing_data
    #         if "password" in new_data and "password" in existing_data:
    #             new_data = new_data.copy()
    #             existing_data = existing_data.copy()
    #             new_data.pop("password", None)
    #             existing_data.pop("password", None)
    #         # Compare keys
    #         if set(new_data.keys()) != set(existing_data.keys()):
    #             return False
    #         # Recursively compare values
    #         return all(
    #             self.is_json_data_equal(new_data[k], existing_data[k]) for k in new_data
    #         )
    #     # Handle case where both are lists
    #     if isinstance(new_data, list) and isinstance(existing_data, list):
    #         # Normalize and sort lists for comparison
    #         new_normalized = sorted([str(item).strip() for item in new_data])
    #         existing_normalized = sorted([str(item).strip() for item in existing_data])
    #         return new_normalized == existing_normalized
    #     # Fallback to direct comparison
    #     return new_data == existing_data

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

# pylint: disable-next=too-many-public-methods
class NexusRepositoryHelper:

    @staticmethod
    def storage_attributes():
        """Directly maps to StorageAttributes"""
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "blob_store_name": {"type": "str", "default": "default"},
                "strict_content_type_validation": {"type": "bool", "default": True},
            },
        }

    @staticmethod
    def hosted_storage_attributes():
        """Directly maps to HostedStorageAttributes"""
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "blob_store_name": {"type": "str", "default": "default"},
                "strict_content_type_validation": {"type": "bool", "default": True},
                "write_policy": {
                    "type": "str",
                    "choices": ["ALLOW", "ALLOW_ONCE", "DENY"],
                    "default": "ALLOW_ONCE",
                },
            },
        }

    @staticmethod
    def cleanup_policy_attributes():
        """Directly maps to CleanupPolicyAttributes"""
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
        """Directly maps to ProxyAttributes"""
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
    def negative_cache_attributes():
        """Directly maps to NegativeCacheAttributes"""
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "enabled": {"type": "bool", "default": True},
                "time_to_live": {"type": "int", "default": 1440},
            },
        }

    @staticmethod
    def http_client_attributes():
        """Directly maps to HttpClientAttributes"""
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "blocked": {"type": "bool", "default": False},
                "auto_block": {"type": "bool", "default": True},
                "connection": NexusRepositoryHelper.http_client_connection_attributes(),
                "authentication": NexusRepositoryHelper.http_client_connection_authentication_attributes(),
            },
        }

    @staticmethod
    def http_client_connection_attributes():
        """Directly maps to HttpClientConnectionAttributes"""
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "retries": {"type": "int"},  # min 0, max 10
                "user_agent_suffix": {"type": "str", "required": False},
                "timeout": {"type": "int"},  # min 1, max 3600
                "enable_circular_redirects": {"type": "bool", "default": False},
                "enable_cookies": {"type": "bool", "default": False},
                "use_trust_store": {"type": "bool", "default": False},
            },
        }

    @staticmethod
    def http_client_connection_authentication_attributes():
        """Directly maps to HttpClientConnectionAuthenticationAttributes"""
        return {
            "type": "dict",
            "options": {
                "type": {
                    "type": "str",
                    "choices": ["username", "ntlm", "bearerToken"],
                    "default": "username",
                    "required": False,
                },
                "username": {"type": "str", "required": False},
                "password": {"type": "str", "no_log": True, "required": False},
                "ntlmHost": {"type": "str", "required": False},
                "ntlmDomain": {"type": "str", "required": False},
                "bearerToken": {"type": "str", "required": False},
            },
        }

    @staticmethod
    def replication_attributes():
        """Directly maps to ReplicationAttributes"""
        return {
            "type": "dict",
            "options": {
                "preemptive_pull_enabled": {"type": "bool", "default": False},
                "asset_path_regex": {"type": "str", "required": False},
            },
        }

    @staticmethod
    def component_attributes():
        """Directly maps to ComponentAttributes"""
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {"proprietary_components": {"type": "bool", "default": False}},
        }

    @staticmethod
    def group_attributes():
        """Directly maps to GroupAttributes"""
        return {
            "type": "dict",
            "options": {
                "member_names": {
                    "type": "list",
                    "elements": "str",
                    "default": [],
                },
            },
        }

    @staticmethod
    def http_client_attributes_with_preemptive_auth():
        """Directly maps to HttpClientAttributesWithPreemptiveAuth"""
        return {
            "type": "dict",
            "apply_defaults": True,
            "options": {
                "blocked": {"type": "bool", "default": False},
                "auto_block": {"type": "bool", "default": True},
                "connection": NexusRepositoryHelper.http_client_connection_attributes(),
                "authentication":
                NexusRepositoryHelper.http_client_connection_authentication_attributes_with_preemptive(),
            },
        }

    @staticmethod
    def http_client_connection_authentication_attributes_with_preemptive():
        """Directly maps to HttpClientConnectionAuthenticationAttributesWithPreemptive"""
        ret_spec = (
            NexusRepositoryHelper.http_client_connection_authentication_attributes()
        )
        ret_spec["options"]["preemptive"] = {
            "type": "bool",
            "default": False,
            "required": False,
        }
        return ret_spec

    @staticmethod
    def group_deploy_attributes():
        """Directly maps to GroupDeployAttributes"""
        ret_spec = NexusRepositoryHelper.group_attributes()
        ret_spec["options"]["writable_member"] = {
            "type": "str",
        }
        return ret_spec

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
    def list_filtered_repositories(helper, list_filter=repository_name_filter):
        content = NexusRepositoryHelper.list_repositories(helper)
        content = list(filter(lambda item: list_filter(item, helper), content))
        return content

    @staticmethod
    def create_repository_new(
        helper: NexusHelper, endpoint_path: str, data: dict
    ):
        changed = True
        info, content = helper.request(
            api_url=(helper.NEXUS_API_ENDPOINTS["repositories"] + endpoint_path).format(
                url=helper.module.params["url"],
            ),
            method="POST",
            data=data,
        )
        if info["status"] not in [201]:
            if info["status"] == 401:
                helper.generic_authn_failure_msg()
            elif info["status"] == 403:
                helper.generic_permission_failure_msg()
            else:
                helper.module.fail_json(
                    msg=f"Failed to create repository {helper.module.params['name']}, \
                        http_status={info['status']}, error_msg='{info['msg']}, body={info['body']}'."
                )

        return content, changed

    @staticmethod
    def update_repository_new(
        helper: NexusHelper,
        endpoint_path: str,
        data: dict,
        existing_data: dict,
        existing_data_normalization=None
    ):
        normalized_data = helper.clean_dict_list(data)
        normalized_existing_data = helper.clean_dict_list(existing_data)

        normalized_existing_data.pop("format", None)  # type: ignore
        normalized_existing_data.pop("type", None)  # type: ignore
        normalized_existing_data.pop("url", None)  # type: ignore
        if existing_data_normalization:
            normalized_existing_data = existing_data_normalization(normalized_existing_data)
        # Delete password from structure because API will never return it.
        got_password = False
        if (normalized_data.get("httpClient")  # type: ignore
            and normalized_data["httpClient"].get("authentication")  # type: ignore
        ):
            got_password = normalized_data["httpClient"]["authentication"].get("password") is not None  # type: ignore
            normalized_data["httpClient"]["authentication"].pop("password", None)  # type: ignore

        changed = not helper.is_json_data_equal(
            normalized_data, normalized_existing_data
        )
        if not changed and not got_password:
            return existing_data, False

        # helper.module.fail_json(msg=f"\n\n{changed}\n\n{normalized_existing_data}\n\n{normalized_data}\n")

        info, content = helper.request(
            api_url=(
                helper.NEXUS_API_ENDPOINTS["repositories"] + "{path}/{repository}"
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
                helper.generic_authn_failure_msg()
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
        info, content = helper.request(
            api_url=(helper.NEXUS_API_ENDPOINTS["repositories"] + "/{name}").format(
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
                helper.generic_authn_failure_msg()
            elif info["status"] == 403:
                helper.generic_permission_failure_msg()
            else:
                helper.module.fail_json(
                    msg=f"Failed to delete {helper.module.params['name']}., \
                        http_status={info['status']}, error_msg='{info['msg']}'."
                )

        return content, changed

    @staticmethod
    def create_update_repository(
        helper: NexusHelper, endpoint_path: str, data: dict, existing_data: list, existing_data_normalization=None
    ):
        if len(existing_data) > 0:
            return NexusRepositoryHelper.update_repository_new(
                helper, endpoint_path, data, existing_data[0], existing_data_normalization
            )
        return NexusRepositoryHelper.create_repository_new(
            helper, endpoint_path, data
        )

    @staticmethod
    def generic_repository_proxy_module(
        endpoint_path:str,
        repository_filter=repository_name_filter,
        existing_data_normalization=None,
        arg_additions=None,
        request_data_additions=None
    ):
        argument_spec = NexusHelper.nexus_argument_spec()
        argument_spec.update(
            {
                "state": {
                    "type": "str",
                    "choices": ["online", "offline", "present", "absent"],
                    "default": "present",
                },
                "name": {"type": "str", "no_log": False, "required": True},
                "http_client": NexusRepositoryHelper.http_client_attributes(),
                "negative_cache": NexusRepositoryHelper.negative_cache_attributes(),
                "proxy": NexusRepositoryHelper.proxy_argument_spec(),
                "storage": NexusRepositoryHelper.storage_attributes(),
                # Optional
                "cleanup": NexusRepositoryHelper.cleanup_policy_attributes(),
                "routing_rule_name": {"type": "str", "no_log": False, "required": False},
                "replication": NexusRepositoryHelper.replication_attributes(),
            }
        )
        if arg_additions:
            argument_spec.update(arg_additions)

        module = AnsibleModule(
            argument_spec=argument_spec,
            supports_check_mode=True,
            required_together=[("username", "password")],
        )

        helper = NexusHelper(module)

        changed, content = False, {}
        existing_data = NexusRepositoryHelper.list_filtered_repositories(
            helper, repository_filter
        )
        if helper.module.params["state"] == "absent":  # type: ignore
            if len(existing_data) > 0:
                content, changed = NexusRepositoryHelper.delete_repository(helper)
        else:
            # <X>ProxyRepositoryApiRequest
            data = {
                "name": module.params["name"], # type: ignore
                "online": module.params["state"] == "online" or module.params["state"] == "present", # type: ignore
                "httpClient": NexusHelper.camalize_param(helper, "http_client"),
                "negativeCache": NexusHelper.camalize_param(helper, "negative_cache"),
                "proxy": NexusHelper.camalize_param(helper, "proxy"),
                "storage": NexusHelper.camalize_param(helper, "storage"),
                "cleanup": NexusHelper.camalize_param(helper, "cleanup"),
                "routingRuleName": helper.module.params["routing_rule_name"],  # type: ignore
                "replication": NexusHelper.camalize_param(helper, "replication"),
            }
            if not request_data_additions:
                request_data_additions = {}
            for k, v in request_data_additions.items():
                if v == "camalize":
                    data[humps.camelize(k)] = NexusHelper.camalize_param(helper, k)
                else:
                    data[humps.camelize(k)] = module.params[k]

            content, changed = NexusRepositoryHelper.create_update_repository(
                helper, endpoint_path, data, existing_data, existing_data_normalization
            )
        result = NexusHelper.generate_result_struct(changed, content)
        module.exit_json(**result)

    @staticmethod
    def generic_repository_group_module(
        endpoint_path:str,
        repository_filter=repository_name_filter,
        existing_data_normalization=None,
        arg_additions=None,
        request_data_additions=None
    ):
        argument_spec = NexusHelper.nexus_argument_spec()
        argument_spec.update(
            {
                "state": {
                    "type": "str",
                    "choices": ["online", "offline", "present", "absent"],
                    "default": "present",
                },
                "name": {"type": "str", "no_log": False, "required": True},
                "storage": NexusRepositoryHelper.storage_attributes(),
                "group": NexusRepositoryHelper.group_deploy_attributes(),
            }
        )
        if arg_additions:
            argument_spec.update(arg_additions)

        module = AnsibleModule(
            argument_spec=argument_spec,
            supports_check_mode=True,
            required_together=[("username", "password")],
        )

        helper = NexusHelper(module)

        changed, content = False, {}
        existing_data = NexusRepositoryHelper.list_filtered_repositories(
            helper, repository_filter
        )
        if helper.module.params["state"] == "absent":  # type: ignore
            if len(existing_data) > 0:
                content, changed = NexusRepositoryHelper.delete_repository(helper)
        else:
            # <X>GroupRepositoryApiRequest
            data = {
                "name": module.params["name"],  # type: ignore
                "online": module.params["state"] == "online" or module.params["state"] == "present",  # type: ignore
                "storage": NexusHelper.camalize_param(helper, "storage"),
                "group": NexusHelper.camalize_param(helper, "group"),
            }
            if not request_data_additions:
                request_data_additions = {}
            for k, v in request_data_additions.items():
                if v == "camalize":
                    data[humps.camelize(k)] = NexusHelper.camalize_param(helper, k)
                else:
                    data[humps.camelize(k)] = module.params[k]

            content, changed = NexusRepositoryHelper.create_update_repository(
                helper, endpoint_path, data, existing_data, existing_data_normalization
            )
        result = NexusHelper.generate_result_struct(changed, content)

        module.exit_json(**result)

    @staticmethod
    def generic_repository_hosted_module(
        endpoint_path:str,
        repository_filter=repository_name_filter,
        existing_data_normalization=None,
        arg_additions=None,
        request_data_additions=None
    ):
        argument_spec = NexusHelper.nexus_argument_spec()
        argument_spec.update(
            {
                "state": {
                    "type": "str",
                    "choices": ["online", "offline", "present", "absent"],
                    "default": "present",
                },
                "name": {"type": "str", "no_log": False, "required": True},
                "storage": NexusRepositoryHelper.hosted_storage_attributes(),
                "cleanup": NexusRepositoryHelper.cleanup_policy_attributes(),
                "component": NexusRepositoryHelper.component_attributes(),
            }
        )
        if arg_additions:
            argument_spec.update(arg_additions)

        module = AnsibleModule(
            argument_spec=argument_spec,
            supports_check_mode=True,
            required_together=[("username", "password")],
        )

        helper = NexusHelper(module)

        changed, content = False, {}
        existing_data = NexusRepositoryHelper.list_filtered_repositories(
            helper, repository_filter
        )
        if helper.module.params["state"] == "absent":  # type: ignore
            if len(existing_data) > 0:
                content, changed = NexusRepositoryHelper.delete_repository(helper)
        else:
            # <X>HostedRepositoryApiRequest
            data = {
                "name": module.params["name"],  # type: ignore
                "online": module.params["state"] == "online" or module.params["state"] == "present",  # type: ignore
                "storage": NexusHelper.camalize_param(helper, "storage"),
                "cleanup": NexusHelper.camalize_param(helper, "cleanup"),
                "component": NexusHelper.camalize_param(helper, "component"),
            }
            if not request_data_additions:
                request_data_additions = {}
            for k, v in request_data_additions.items():
                if v == "camalize":
                    data[humps.camelize(k)] = NexusHelper.camalize_param(helper, k)
                else:
                    data[humps.camelize(k)] = module.params[k]

            content, changed = NexusRepositoryHelper.create_update_repository(
                helper, endpoint_path, data, existing_data, existing_data_normalization
            )
        result = NexusHelper.generate_result_struct(changed, content)

        module.exit_json(**result)

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
