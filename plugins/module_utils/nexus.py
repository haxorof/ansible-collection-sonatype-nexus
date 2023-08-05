# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import time
import pathlib
import os
import stat
import git

from os import close
from tempfile import mkstemp
from traceback import format_exc

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url, basic_auth_header

#
# class: NexusHelper
#

class NexusHelper:
    NEXUS_API_URL = 'https://localhost'

    NEXUS_API_ENDPOINTS = {
        'routing-rules': '{url}/service/rest/v1/routing-rules',
    }

    def __init__(self, module):
        self.module = module
        self.module.params['url_username'] = self.module.params['username']
        self.module.params['url_password'] = self.module.params['password']
        if self.module.params['url'] is None:
            self.module.params['url'] = self.NEXUS_API_URL

    @staticmethod
    def nexus_argument_spec():
        return dict(
            url=dict(type='str', no_log=False, required=False),
            username=dict(type='str', no_log=False, required=False, default=None, aliases=['user'],
                          fallback=(env_fallback, ['NEXUS_USERNAME'])),
            password=dict(type='str', no_log=True, required=False, default=None),
            validate_certs=dict(type='bool', default=True),
            use_proxy=dict(type='bool', default=True),
            return_content=dict(type='bool', default=True),
            sleep=dict(type='int', default=5),
            retries=dict(type='int', default=3),
        )

    def request(self, api_url, method, data=None, headers=None):
        headers = headers or {}

        headers.update({
            'Authorization': basic_auth_header(self.module.params['username'], self.module.params['password'])
        })

        if isinstance(data, dict):
            data = self.module.jsonify(data)
            if not ('Content-type' in headers):
                headers.update({
                    'Content-type': 'application/json',
                })

        retries = 1
        while retries <= self.module.params['retries']:
            response, info = fetch_url(
                module=self.module,
                url=api_url,
                method=method,
                headers=headers,
                data=data,
                force=True,
                use_proxy=self.module.params['use_proxy'],
            )
            if (info is not None) and (info['status'] != -1):
                break
            time.sleep(self.module.params['sleep'])
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
                        content['json'] = js
                except ValueError as e:
                    content['content'] = body

        content['fetch_url_retries'] = retries

        return info, content
