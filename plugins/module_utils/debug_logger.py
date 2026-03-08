#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the haxorof.sonatype_nexus project
# MIT License (see COPYING or https://opensource.org/license/mit/)

# Usage for troubleshooting only:
# from ansible_collections.haxorof.sonatype_nexus.plugins.module_utils.debug_logger import DebugLogger
# DebugLogger.debug("%s", "testing")

import logging
import os

class DebugLogger:
    enabled = True
    logfile = f"{os.environ.get('DEBUG_LOG_PATH')}/ansible_debug.log"
    initialized = False

    @classmethod
    def enable(cls, logfile=None):
        cls.enabled = True
        if logfile:
            cls.logfile = logfile

    @classmethod
    def _init_logger(cls):
        if cls.initialized or not cls.enabled:
            return

        os.makedirs(os.path.dirname(cls.logfile), exist_ok=True)

        logging.basicConfig(
            filename=cls.logfile,
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(message)s"
        )
        cls.initialized = True

    @classmethod
    def debug(cls, msg, *args):
        if cls.enabled:
            cls._init_logger()
            logging.debug(msg, *args)

    @classmethod
    def info(cls, msg, *args):
        if cls.enabled:
            cls._init_logger()
            logging.info(msg, *args)

    @classmethod
    def error(cls, msg, *args):
        if cls.enabled:
            cls._init_logger()
            logging.error(msg, *args)
