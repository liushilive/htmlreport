"""
Copyright 2017 刘士

Licensed under the Apache License, Version 2.0 (the "License"): you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""
import logging
import logging.handlers

import sys
import threading

from io import StringIO

LOG_LEVEL_NOTSET = logging.NOTSET
LOG_LEVEL_DEBUG = logging.DEBUG
LOG_LEVEL_INFO = logging.INFO
LOG_LEVEL_WARNING = logging.WARNING
LOG_LEVEL_ERROR = logging.ERROR

# logger target
LOG_TARGET_CONSOLE = 0x1
LOG_TARGET_LOG_FILE = 0x10
LOG_TARGET_LOG_HTTP = 0x100

_LOGGER_FORMAT = "%(asctime)s [%(thread)7d] %(levelname)s %(filename)s(%(lineno)d) - %(message)s"


class InfoOrLessCritical(logging.Filter):
    def filter(self, record):
        return record.levelno < LOG_LEVEL_WARNING


class HandlerFactory(object):
    handlers = {}
    streams = {}

    @classmethod
    def get_std_out_handler(cls):
        if 'std_out_handler' not in cls.handlers:
            std_out_handler = logging.StreamHandler(sys.stdout)
            std_out_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            std_out_handler.addFilter(InfoOrLessCritical())
            cls.handlers['std_out_handler'] = std_out_handler

        return cls.handlers['std_out_handler']

    @classmethod
    def get_std_err_handler(cls):
        if 'std_err_handler' not in cls.handlers:
            std_err_handler = logging.StreamHandler(sys.stderr)
            std_err_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            std_err_handler.setLevel(LOG_LEVEL_WARNING)
            cls.handlers['std_err_handler'] = std_err_handler

        return cls.handlers['std_err_handler']

    @classmethod
    def get_rotating_file_handler(cls, log_path, max_bytes=0, backup_count=0):
        if 'rotating_file_handler' not in cls.handlers:
            cls.handlers['rotating_file_handler'] = {}

        if log_path not in cls.handlers['rotating_file_handler']:
            rotating_file_handler = logging.handlers.RotatingFileHandler(
                log_path, 'a', max_bytes, backup_count, encoding='utf8')
            rotating_file_handler.setLevel(LOG_LEVEL_NOTSET)
            rotating_file_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            cls.handlers['rotating_file_handler'][log_path] = rotating_file_handler

        return cls.handlers['rotating_file_handler'][log_path]

    @classmethod
    def get_stream_handler(cls):
        if 'rotating_stream_handler' not in cls.handlers:
            cls.handlers['rotating_stream_handler'] = {}
        steam_id = str(threading.current_thread().ident)
        if steam_id not in cls.handlers['rotating_stream_handler']:
            steam = StringIO()
            cls.streams[steam_id] = steam
            rotating_stream_handler = logging.StreamHandler(cls.streams[steam_id])
            rotating_stream_handler.set_name(steam_id)
            rotating_stream_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            cls.handlers['rotating_stream_handler'][steam_id] = rotating_stream_handler

        return cls.handlers['rotating_stream_handler'][steam_id]

    @classmethod
    def get_stream_value(cls):
        steam_id = str(threading.current_thread().ident)
        if steam_id in cls.streams:
            stream = cls.streams[steam_id].getvalue()
            cls.streams[steam_id].truncate(0)
            cls.streams[steam_id].seek(0)
            return stream
        return ""
