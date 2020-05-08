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

本页代码改写：https://github.com/datadriventests/ddt

在其基础上进行改写以符合个性化需求。
"""
import logging
import re
from functools import wraps

from . import retry_on_exception

_DATA_ATTR: str = "%values"  # 存储测试必须运行的数据
_UNPACK_ATTR: str = "%unpack"  # 解包
_index_len: int = 1  # 默认最大的case索引长度

trivial_types = (type(None), bool, int, float, str)


def _is_trivial(value):
    if isinstance(value, trivial_types):
        return True
    elif isinstance(value, (list, tuple)):
        return all(map(_is_trivial, value))
    return False


def unpack(func):
    """
    方法装饰器添加解包特性
    """
    setattr(func, _UNPACK_ATTR, True)
    return func


def data(*values):
    """
    方法装饰器添加到 unittest.TestCase 实例的方法中

    接收位置参数，构成数据驱动
    """
    global _index_len
    _index_len = len(str(len(values)))
    return iter_data(values)


def iter_data(iterable):
    """
    方法装饰器添加到 unittest.TestCase 实例的方法中

    接收可迭代对象，构成数据驱动
    """

    def wrapper(func):
        setattr(func, _DATA_ATTR, iterable)
        return func

    return wrapper


def _mk_test_name(name, value, index: int = 0):
    """
    为测试用例生成一个新名称。

    它将采用原始测试名称，并附加一个序号索引和该值的字符串表示形式，并将结果转换为有效的Python标识符，方法是用`_``替换多余的字符。
    """

    # 在索引之前添加0以保持顺序
    index = f"{index + 1:0{_index_len}}"
    if not _is_trivial(value):
        return f"{name}_{index}"
    try:
        value = str(value)
    except UnicodeEncodeError:
        value = value.encode("ascii", "backslashreplace")
    test_name = f"{name}_{index}_{value}"
    return re.sub(r"\W|^(?=\d)", "_", test_name)


def _feed_data(func, new_name, *args, **kwargs):
    """
    这个内部方法装饰器将测试数据项提供给测试

    """

    @wraps(func)
    def wrapper(self):
        if args:
            logging.info(f"args:\n{args}")
        if kwargs:
            logging.info(f"kwargs:\n{kwargs}")
        return func(self, *args, **kwargs)

    wrapper.__name__ = new_name
    wrapper.__wrapped__ = func

    return wrapper


def _add_test(cls, test_name, func, *args, **kwargs):
    """
    向该类添加一个测试用例

    测试将基于现有的功能，但会给它一个新名称。
    """
    setattr(cls, test_name, _feed_data(func, test_name, *args, **kwargs))
    # 测试重试
    if hasattr(func, retry_on_exception.__retry):
        retry_on_exception.retry_lists.append(cls.__name__ + "." + test_name)
    if hasattr(func, retry_on_exception.__no_retry):
        retry_on_exception.no_retry_lists.append(cls.__name__ + "." + test_name)


def ddt(cls):
    """
    “unittest.TestCase”的子类的类装饰器。

    将这个装饰器应用到测试用例类，然后用 @data 装饰测试方法。

    对于用 @data 装饰的每个方法，这将有效地构建数据驱动。

    测试方法的名称遵循模式 original_test_name_{ordinal}_{data}

    ordinal 是数据参数的位置，从1开始。

    对于数据，使用数据值的字符串表示形式转换为有效的Python标识符
    """
    for name, func in list(cls.__dict__.items()):
        if hasattr(func, _DATA_ATTR):
            for i, v in enumerate(getattr(func, _DATA_ATTR)):
                test_name = _mk_test_name(name, getattr(v, "__name__", v), i)
                if hasattr(func, _UNPACK_ATTR):
                    if isinstance(v, tuple) or isinstance(v, list):
                        _add_test(cls, test_name, func, *v)
                    elif isinstance(v, dict):
                        # 解包字典
                        _add_test(cls, test_name, func, **v)
                else:
                    _add_test(cls, test_name, func, v)
            delattr(cls, name)

            # 测试重试
            func.__qualname__ in retry_on_exception.retry_lists and retry_on_exception.retry_lists.remove(
                func.__qualname__)
            func.__qualname__ in retry_on_exception.no_retry_lists and retry_on_exception.no_retry_lists.remove(
                func.__qualname__)
    return cls
