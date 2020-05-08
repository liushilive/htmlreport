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
__retry = "%retry"  # 重试
__no_retry = "%no_retry"  # 不重试

retry_lists = [
    # 存储重试列表
]

no_retry_lists = [
    # 存储不重试列表
]


def retry(func):
    """
    方法装饰器添加重试特性
    """
    setattr(func, __retry, True)
    if func.__qualname__ in no_retry_lists:
        raise ValueError("不允许同时存在 @retry 与 @no_retry")
    retry_lists.append(func.__qualname__)
    return func


def no_retry(func):
    """
    方法装饰器添加不重试特性
    """
    setattr(func, __no_retry, True)
    if func.__qualname__ in retry_lists:
        raise ValueError("不允许同时存在 @retry 与 @no_retry")
    no_retry_lists.append(func.__qualname__)
    return func
