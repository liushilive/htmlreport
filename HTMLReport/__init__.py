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

测试报告生成器
"""
__author__ = '刘士'
__version__ = '2.0.0'

import warnings

from .tools import data_driven as ddt
from .tools.log.logger import Log
from .tools.save_images import addImage
from .tools.retry_on_exception import retry, no_retry
from HTMLReport.test_runner import TestRunner

# 日志记录器
log = Log()


def logger():
    """不赞同使用此方法，请使用

    from HTMLReport import log

    log.info("")

    """
    warnings.warn("""不赞同使用此方法，请使用
    
    from HTMLReport import log

    log.info("")
    
    """, DeprecationWarning, stacklevel=2)

    return tools.log.logger.GeneralLogger().get_logger()


def AddImage(base64_data: bytes, title: str = "", describe: str = ""):
    """不赞同使用此方法，请使用

    from HTMLReport import addImage

    addImage(base64_data, title, describe)

    """
    warnings.warn("""不赞同使用此方法，请使用
    
    from HTMLReport import addImage
    
    addImage(base64_data, title, describe)
    
    """, DeprecationWarning, stacklevel=2)

    addImage(base64_data, title, describe)


__all__ = ["AddImage", "addImage", "log", "TestRunner", "logger", "ddt", "retry", "no_retry"]
