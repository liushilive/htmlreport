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
from logging import Handler, getLevelName

_LOGGER_FORMAT = "%(asctime)s %(thread)7d %(levelname)8s %(filename)s(%(lineno)d) - %(message)s"


class _StreamHandler(Handler):
    """
    分线程日志流记录
    """

    terminator = '\n'

    def __init__(self, streams=None):
        """
        初始化处理程序
        """
        Handler.__init__(self)
        if streams is None:
            streams = {}
        self.streams = streams

    def flush(self):
        """
        刷新流
        """
        self.acquire()
        steam_id = str(threading.current_thread().ident)
        try:
            if self.streams.get(steam_id) and hasattr(self.streams[steam_id], "flush"):
                self.streams[steam_id].flush()
        finally:
            self.release()

    def emit(self, record):
        """
        记录
        """
        try:
            msg = self.format(record)
            steam_id = str(threading.current_thread().ident)
            if steam_id not in self.streams:
                self.streams[steam_id] = StringIO()
            stream = self.streams[steam_id]
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = getLevelName(self.level)
        steam_id = str(threading.current_thread().ident)
        name = getattr(self.streams[steam_id], "name", "")
        if name:
            name += " "
        return f"<{self.__class__.__name__} {name}({level})>"


class InfoOrLessCritical(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.WARNING


class HandlerFactory(object):
    handlers = {}
    streams = {}

    @classmethod
    def get_std_out_handler(cls):
        if "std_out_handler" not in cls.handlers:
            std_out_handler = logging.StreamHandler(sys.stdout)
            std_out_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            std_out_handler.addFilter(InfoOrLessCritical())
            cls.handlers["std_out_handler"] = std_out_handler

        return cls.handlers["std_out_handler"]

    @classmethod
    def get_std_err_handler(cls):
        if "std_err_handler" not in cls.handlers:
            std_err_handler = logging.StreamHandler(sys.stderr)
            std_err_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            std_err_handler.setLevel(logging.WARNING)
            cls.handlers["std_err_handler"] = std_err_handler

        return cls.handlers["std_err_handler"]

    @classmethod
    def get_rotating_file_handler(cls, log_path, max_bytes=0, backup_count=0):
        if "rotating_file_handler" not in cls.handlers:
            cls.handlers["rotating_file_handler"] = {}

        if log_path not in cls.handlers["rotating_file_handler"]:
            rotating_file_handler = logging.handlers.RotatingFileHandler(
                log_path, "a", max_bytes, backup_count, encoding="utf8")
            rotating_file_handler.setLevel(logging.NOTSET)
            rotating_file_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            cls.handlers["rotating_file_handler"][log_path] = rotating_file_handler

        return cls.handlers["rotating_file_handler"][log_path]

    @classmethod
    def get_stream_handler(cls):
        if "rotating_stream_handler" not in cls.handlers:
            rotating_stream_handler = _StreamHandler(cls.streams)
            rotating_stream_handler.setFormatter(logging.Formatter(_LOGGER_FORMAT))
            cls.handlers["rotating_stream_handler"] = rotating_stream_handler

        return cls.handlers["rotating_stream_handler"]

    @classmethod
    def get_stream_value(cls):
        steam_id = str(threading.current_thread().ident)
        if steam_id in cls.streams:
            stream = cls.streams[steam_id].getvalue()
            cls.streams[steam_id].truncate(0)
            cls.streams[steam_id].seek(0)
            return stream
        return ""
