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
import threading
import time
from io import StringIO
from unittest import TestResult, TestCase

from . import save_images
from .log.handler_factory import HandlerFactory
from .retry_on_exception import no_retry_lists, retry_lists


class Result(TestResult):
    """
    定义继承自 unittest.TestResult 的 类。
    这里重写了 unittest.TestResult 的多个方法，比如 startTest(self, test) 等等
    """

    def __init__(self, LANG, tries, delay, back_off, max_delay, retry):
        super().__init__()
        self.success_count = 0
        self.failure_count = 0
        self.skip_count = 0
        self.error_count = 0
        self.success_set = set()
        self.failure_set = set()
        self.skip_set = set()
        self.error_set = set()
        self.stderr_steams = StringIO()
        self.stderr_steams.write("\n")
        self.stdout_steams = StringIO()
        self.stdout_steams.write("\n")
        self.LANG = LANG
        self.tries, self.delay, self.back_off, self.max_delay, self.retry = tries, delay, back_off, max_delay, retry
        """
        返回结果是一个5个属性的字典的列表
        (
          result_code (0: success; 1: fail; 2: error; 3: skip),
          testCase_object,
          test_output dict(list(string)),
          image_paths dict,
          tries int,
          style dict
        )
        """
        self.result = []
        self.result_tmp = {}
        self.time = {}

    def startTest(self, test):
        logging.info((self.LANG == "cn" and "开始测试： {}" or "Start Test: {}").format(test))
        current_id = str(threading.current_thread().ident)
        if current_id in self.result_tmp:
            self.result_tmp[current_id]["tries"] += 1
        else:
            self.result_tmp[current_id] = dict(
                result_code=0,
                testCase_object=test,
                test_output={},
                image_paths={},
                tries=0,
                retry=True,
                style={},
                local_delay=self.delay
            )

        self.time[str(threading.current_thread().ident)] = time.time()
        TestResult.startTest(self, test)

    def stopTest(self, test):
        end_time = time.time()
        logging.info((self.LANG == "cn" and "测试结束： {}" or "Stop Test: {}").format(test))
        logging.info((self.LANG == "cn" and "耗时： {}" or "Duration: {}").format(
            end_time - self.time[str(threading.current_thread().ident)]))
        current_id = str(threading.current_thread().ident)
        tries = self.result_tmp[current_id]["tries"]
        if current_id in save_images.imageList:
            tmp = save_images.imageList.pop(current_id)
            self.result_tmp[current_id]["image_paths"][tries] = tmp
        tmp = HandlerFactory.get_stream_value()
        self.result_tmp[current_id]["test_output"][tries] = tmp

        # 停止重试
        test_name = test.__class__.__name__ + "." + test.__getattribute__("_testMethodName")
        if (not self.retry and test_name not in retry_lists) or (
                self.retry and test_name in no_retry_lists
        ) or self.tries <= tries or self.result_tmp[current_id]["result_code"] in (0, 3):
            self.result_tmp[current_id]["retry"] = False

        if self.result_tmp[current_id]["retry"]:
            # 重试
            if self.result_tmp[current_id]["local_delay"] > self.max_delay:
                self.result_tmp[current_id]["local_delay"] = self.max_delay
            logging.info(
                (self.LANG == "cn" and "等待 {} 秒后重试" or "Retrying in {} seconds...").format(
                    self.result_tmp[current_id]["local_delay"]
                )
            )
            time.sleep(self.result_tmp[current_id]["local_delay"])
            self.result_tmp[current_id]["local_delay"] *= self.back_off
            test(self)
        else:
            # 最后清理
            if current_id in self.success_set:
                self.success_set.remove(current_id)
            if current_id in self.failure_set:
                self.failure_set.remove(current_id)
            if current_id in self.skip_set:
                self.skip_set.remove(current_id)
            if current_id in self.error_set:
                self.error_set.remove(current_id)
            if "retry" in self.result_tmp[current_id]:
                del self.result_tmp[current_id]["retry"]
            if "local_delay" in self.result_tmp[current_id]:
                del self.result_tmp[current_id]["local_delay"]
            # 产生结果
            self.result.append(self.result_tmp.pop(current_id))

    def addSkip(self, test, reason):
        TestResult.addSkip(self, test, reason)

        self._steams_write_doc("Skip", test)

        logging.info((self.LANG == "cn" and "跳过测试： {}\n{}" or "Skip Test: {}\n{}").format(test, reason))

        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = 3
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = 3
        if current_id not in self.skip_set:
            self.skip_count += 1
            self.skip_set.add(current_id)

    def addSuccess(self, test):
        TestResult.addSuccess(self, test)

        self._steams_write_doc("Pass", test)

        logging.info((self.LANG == "cn" and "测试执行通过： {}" or "Pass Test: {}").format(test))

        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = 0
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = 0
        if current_id not in self.success_set:
            self.success_count += 1
            self.success_set.add(current_id)
        if current_id in self.failure_set:
            self.failure_count -= 1
        if current_id in self.error_set:
            self.error_count -= 1

    def addError(self, test, err):
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]

        self._steams_write_doc("Error", test)

        logging.error((self.LANG == "cn" and "测试产生错误： {}\n{}" or "Error Test: {}\n{}").format(test, _exc_str))

        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = 2
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = 2
        if current_id not in self.error_set:
            self.error_count += 1
            self.error_set.add(current_id)

    def addFailure(self, test, err):
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]

        self._steams_write_doc("Fail", test)

        logging.warning((self.LANG == "cn" and "测试未通过： {}\n{}" or "Failure: {}\n{}").format(test, _exc_str))

        current_id = str(threading.current_thread().ident)
        self.result_tmp[current_id]["result_code"] = 1
        self.result_tmp[current_id]["style"][self.result_tmp[current_id]["tries"]] = 1
        if current_id not in self.failure_set:
            self.failure_count += 1
            self.failure_set.add(current_id)

    def _steams_write_doc(self, result: str, test: TestCase):
        if result == "Pass":
            steams = self.stdout_steams
        else:
            steams = self.stderr_steams

        steams.write(f"{result}\t")
        steams.write(str(test))
        doc = "_testMethodDoc" in test.__dir__() and test.__getattribute__("_testMethodDoc") or ""
        if doc:
            steams.write("\t")
            steams.write(doc.strip().split("\n")[0])
        steams.write("\n")
