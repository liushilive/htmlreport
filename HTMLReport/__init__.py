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
__version__ = '2.0.4a'

from .src.test_runner import TestRunner
from .src.tools import data_driven as ddt
from .src.tools.retry_on_exception import retry, no_retry
from .src.tools.save_images import addImage

__all__ = [
    "addImage",
    "TestRunner",
    "ddt",
    "retry",
    "no_retry",
    "__author__",
    "__version__"
]
