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
import logging.handlers
import os

from .handler_factory import *


class InfoOrLessCritical(logging.Filter):
    def filter(self, record):
        return record.levelno < LOG_LEVEL_WARNING


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class GeneralLogger(object):
    def __init__(self, level=LOG_LEVEL_NOTSET, log_by_thread=False, log_path='', max_bytes=0, backup_count=0,
                 stream=StringIO()):
        # 设置根记录器
        logging.getLogger().setLevel(LOG_LEVEL_NOTSET)
        logging.getLogger().addHandler(HandlerFactory.get_std_out_handler())
        logging.getLogger().addHandler(HandlerFactory.get_std_err_handler())
        logging.getLogger().addHandler(HandlerFactory.get_stream_handler())
        # 默认日志设置
        self._loggers = {}
        self._log_level = level
        self._main_thread_id = str(self.get_current_thread_id())
        self._log_destination = LOG_TARGET_CONSOLE
        self._log_by_thread = log_by_thread
        self._log_path = log_path
        self._log_file_max_bytes = max_bytes
        self._log_file_backup_count = backup_count
        self.stream = stream

    @staticmethod
    def get_current_thread_id():
        return threading.current_thread().ident

    @staticmethod
    def get_current_thread_name():
        return threading.current_thread().name

    def get_log_file_name(self):
        log_path = os.path.abspath(self._log_path)
        base_name = os.path.basename(log_path)
        base_dir = os.path.dirname(log_path)

        if os.path.isdir(log_path):
            # 只提供了文件夹路径，为日志文件创建一个名称
            return os.path.join(log_path, base_name)
        elif base_name and '.' not in base_name:
            # 创建路径
            os.makedirs(log_path)
            return os.path.join(log_path, base_name)
        else:
            return os.path.join(base_dir, base_name)

    def get_logger(self, is_stream: bool = False) -> logging.Logger:
        """添加日志到报告文件中

        :return: 日志对象
        """
        name = self._main_thread_id

        if self._log_by_thread:
            current_id = str(self.get_current_thread_id())

            if current_id != self._main_thread_id:
                # 将子线程的日志记录器作为主记录器的子进程
                # 因此，来自子线程的日志将由主日志程序处理。
                # 否则，主日志将不包含子日志。
                name = self._main_thread_id + '.' + current_id

        if name not in self._loggers:
            self.set_logger(name, is_stream)
        return self._loggers[name]

    def set_logger(self, name, is_stream=False):
        if name not in self._loggers:
            if name == self._main_thread_id:
                new_logger = logging.getLogger()
            else:
                new_logger = logging.getLogger(name)
            new_logger.setLevel(self._log_level)

            if self._log_path:
                if is_stream:
                    new_logger.addHandler(HandlerFactory.get_stream_handler())
                else:
                    # 如果启用了线程，日志路径将会变化
                    log_path = self.get_log_file_name()
                    new_logger.addHandler(HandlerFactory.get_rotating_file_handler(
                        log_path, self._log_file_max_bytes, self._log_file_backup_count))

            self._loggers[name] = new_logger

    def set_log_path(self, file_path, max_bytes=0, backup_count=0):
        if isinstance(file_path, str):
            self._log_path = file_path
        if isinstance(max_bytes, int):
            self._log_file_max_bytes = max_bytes
        if isinstance(backup_count, int):
            self._log_file_backup_count = backup_count

    def set_log_level(self, new_level):
        self._log_level = new_level
        for instanceLogger in self._loggers.values():
            instanceLogger.setLevel(self._log_level)

    def set_log_by_thread_log(self, log_by_thread):
        self._log_by_thread = log_by_thread
        # 如果启用了线程日志，只启用主日志记录器
        for instanceLogger in self._loggers.values():
            instanceLogger.disabled = not self._log_by_thread
        try:
            self._loggers[self._main_thread_id].disabled = self._log_by_thread
        except KeyError:
            pass


class Log(object):
    @property
    def debug(self):
        return GeneralLogger().get_logger().debug

    @property
    def info(self):
        return GeneralLogger().get_logger().info

    @property
    def warning(self):
        return GeneralLogger().get_logger().warning

    @property
    def error(self):
        return GeneralLogger().get_logger().error

    @property
    def exception(self):
        return GeneralLogger().get_logger().exception

    @property
    def critical(self):
        return GeneralLogger().get_logger().critical

    fatal = critical
