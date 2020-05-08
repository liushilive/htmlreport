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
import datetime
import logging
import os
import queue
import random
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Manager
from unittest.suite import TestSuite
from xml.sax import saxutils

from HTMLReport import __author__, __version__
from .tools import save_images
from .tools.log.handler_factory import HandlerFactory
from .tools.result import Result
from .tools.template import TemplateMixin


def _isnotsuite(test):
    """A crude way to tell apart testcases and suites with duck-typing

    :param test:
    :return:
    """
    try:
        iter(test)
    except TypeError:
        return True
    return False


class TestRunner(TemplateMixin, TestSuite):
    """测试执行器"""

    def __init__(self, report_file_name: str = None, log_file_name: str = None, output_path: str = None,
                 title: str = None, description: str = None, tries: int = 0, delay: float = 1, back_off: float = 1,
                 max_delay: float = 120, retry: bool = True, thread_count: int = 1, thread_start_wait: float = 0,
                 sequential_execution: bool = False, lang: str = "cn"):
        """测试执行器

        :param report_file_name: 报告文件名，如果未赋值，将采用“test+时间戳”
        :param log_file_name: 日志文件名，如果未赋值，将采用报告文件名，如果报告文件名也没有，将采用“test+时间戳”
        :param output_path: 报告保存文件夹名，默认“report”
        :param title: 报告标题，默认“测试报告”
        :param description: 报告描述，默认“无测试描述”
        :param tries: 重试次数
        :param delay: 重试延迟间隔，单位为 秒
        :param back_off: 扩展每次重试等待时间的乘数
        :param max_delay: 最大重试等待时间长度，单位为 秒
        :param retry: 如果为 True 表示所有用例遵循重试规则，False 只针对添加了 @retry 用例有效
        :param thread_count: 并发线程数量（无序执行测试），默认数量 1
        :param thread_start_wait: 各线程启动延迟，默认 0 s
        :param sequential_execution: 是否按照套件添加(addTests)顺序执行， 会等待一个addTests执行完成，再执行下一个，默认 False。
                如果用例中存在 tearDownClass ，建议设置为True，否则 tearDownClass 将会在所有用例线程执行完后才会执行。
        :param lang: ("cn", "en") 支持中文与英文报告输出，默认采用中文
        """
        super().__init__()
        self.LANG = lang in ("cn", "en") and lang or "cn"

        self.title = title or (self.LANG == "cn" and self.DEFAULT_TITLE or self.DEFAULT_TITLE_en)
        self.description = description or (
                self.LANG == "cn" and self.DEFAULT_DESCRIPTION or self.DEFAULT_DESCRIPTION_en)

        self.thread_count = thread_count
        self.thread_start_wait = thread_start_wait
        self.sequential_execution = sequential_execution

        save_images.report_path = report_path = os.path.join(output_path or "report")
        dir_to = os.path.join(os.getcwd(), report_path)
        if not os.path.exists(dir_to):
            os.makedirs(dir_to)

        random_name = f"test_{time.strftime('%Y_%m_%d_%H_%M_%S')}_{random.randint(1, 999)}"
        report_name = f'{report_file_name or random_name}.html'

        self.log_name = f"{log_file_name or report_file_name or random_name}.log"
        self.path_file = os.path.join(dir_to, report_name)
        self.log_file_name = os.path.join(dir_to, self.log_name)

        logging.getLogger().addHandler(HandlerFactory.get_rotating_file_handler(self.log_file_name))

        self.startTime = datetime.datetime.now()
        self.stopTime = datetime.datetime.now()

        if tries < 0:
            raise ValueError((lang == "cn"
                              and "tries = {} 必须大于或等于 0"
                              or "tries = {} must be greater than or equal to 0").format(tries))
        if delay < 0:
            raise ValueError((lang == "cn"
                              and "delay = {} 必须大于或等于 0"
                              or "delay = {} must be greater than or equal to 0").format(delay))
        if back_off < 1:
            raise ValueError((lang == "cn"
                              and "back_off = {} 必须大于或等于 1"
                              or "back_off = {} must be greater than or equal to 1").format(back_off))
        if max_delay < delay:
            raise ValueError((lang == "cn"
                              and "max_delay = {} 必须大于或等于 delay = {}"
                              or "max_delay = {} must be greater than or equal to delay = {}").format(max_delay, delay))
        self.tries, self.delay, self.back_off, self.max_delay, self.retry = tries, delay, back_off, max_delay, retry
        self.tc_dict = Manager().dict()

    def _threadPoolExecutorTestCase(self, tmp_list, result):
        """多线程运行"""
        with ThreadPoolExecutor(self.thread_count) as pool:
            for test_case in tmp_list:
                if _isnotsuite(test_case):
                    self._tearDownPreviousClass(test_case, result)
                    self._handleModuleFixture(test_case, result)
                    self._handleClassSetUp(test_case, result)
                    result._previousTestClass = test_case.__class__

                    if (getattr(test_case.__class__, "_classSetupFailed", False) or
                            getattr(result, "_moduleSetUpFailed", False)):
                        continue
                pool.submit(test_case, result)

                self.tc_dict[test_case.__class__] -= 1
                if self.tc_dict[test_case.__class__] == 0:
                    self._tearDownPreviousClass(None, result)

                time.sleep(self.thread_start_wait)

        self._handleModuleTearDown(result)

    def run(self, test: TestSuite, debug: bool = False):
        """
        运行给定的测试用例或测试套件。

        :param test: 测试用例或套件
        :param debug: 调试模式
        """
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        result = Result(self.LANG, self.tries, self.delay, self.back_off, self.max_delay, self.retry)
        if self.LANG == "cn":
            logging.info(f"预计并发线程数：{str(self.thread_count)}")
        else:
            logging.info(f"The number of concurrent threads is expected to be {str(self.thread_count)}")

        for test_case in test:
            tmp_class_name = test_case.__class__
            if tmp_class_name not in self.tc_dict:
                self.tc_dict[tmp_class_name] = 0
            else:
                self.tc_dict[tmp_class_name] += 1

        if self.sequential_execution:
            # 执行套件添加顺序
            test_case_queue = queue.Queue()
            L = []
            tmp_key = None
            for test_case in test:
                tmp_class_name = test_case.__class__
                if tmp_key == tmp_class_name:
                    L.append(test_case)
                else:
                    tmp_key = tmp_class_name
                    if len(L) != 0:
                        test_case_queue.put(L.copy())
                        L.clear()
                    L.append(test_case)
            if len(L) != 0:
                test_case_queue.put(L.copy())
            while not test_case_queue.empty():
                tmp_list = test_case_queue.get()
                self._threadPoolExecutorTestCase(tmp_list, result)
        else:
            # 无序执行
            self._threadPoolExecutorTestCase(test, result)

        self.stopTime = datetime.datetime.now()
        if result.stdout_steams.getvalue().strip():
            logging.info(result.stdout_steams.getvalue())
        if result.stderr_steams.getvalue().strip():
            logging.error(result.stderr_steams.getvalue())

        if self.LANG == "cn":
            s = "\n测试结束！\n运行时间: {time}\n共计执行用例数量：{count}\n执行成功用例数量：{Pass}" \
                "\n执行失败用例数量：{fail}\n跳过执行用例数量：{skip}\n产生异常用例数量：{error}\n"
        else:
            s = "\nEOT！\nRan {count} tests in {time}\n\nPASS：{Pass}" \
                "\nFailures：{fail}\nSkipped：{skip}\nErrors：{error}\n"
        count = result.success_count + result.failure_count + result.error_count + result.skip_count
        s = s.format(
            time=self.stopTime - self.startTime,
            count=count,
            Pass=result.success_count,
            fail=result.failure_count,
            skip=result.skip_count,
            error=result.error_count
        )
        self._generateReport(result)
        logging.info(s)

        return result

    @staticmethod
    def _sortResult(result_list):
        """unittest不以任何特定的顺序运行。在这里把它们按类分组。"""
        remap = {}
        classes = []
        for dic in result_list:
            n = dic.get("result_code")
            t = dic.get("testCase_object")
            o = dic.get("test_output")
            i = dic.get("image_paths")
            r = dic.get("tries")
            s = dic.get("style")

            cls = t.__class__
            if cls not in remap:
                remap[cls] = []
                classes.append(cls)
            remap[cls].append((n, t, o, i, r, s))

        r = [(cls, remap[cls]) for cls in classes]
        return r

    def _generateReport(self, result):
        """生成报告"""
        generator = f"HTMLReport {__author__} {__version__}"
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(result)
        log_file = self._generate_log(self.log_name)
        report = self._generate_report(result)

        ending = self._generate_ending()
        js = self._generate_js()
        output = self.HTML_TMPL.format(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            js=js,
            lang=self.LANG,
            heading=heading,
            log=log_file,
            report=report,
            ending=ending
        )

        with open(self.path_file, "w", encoding="utf8") as report_file:
            report_file.write(output)

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, result):
        heading = self.HEADING_TMPL.format(
            title=saxutils.escape(self.title),
            startTime=str(self.startTime)[:19],
            endTime=str(self.stopTime)[:19],
            duration=self.stopTime - self.startTime,
            total=result.success_count + result.failure_count + result.error_count + result.skip_count,
            Pass=result.success_count,
            fail=result.failure_count,
            error=result.error_count,
            skip=result.skip_count,
            description=saxutils.escape(self.description).replace("\n", "<br />"),
        )
        return heading

    def _generate_report(self, result):
        rows = []
        nrs = 0
        sortedResult = self._sortResult(result.result)
        for cid, (cls, cls_results) in enumerate(sortedResult):
            np = nf = ne = ns = nr = 0
            for n, t, o, i, r, s in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                elif n == 2:
                    ne += 1
                elif n == 3:
                    ns += 1
                nr += r
            nrs += nr

            # 格式化类描述
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = f"{cls.__module__}.{cls.__name__}"
            doc = cls.__doc__ and cls.__doc__.strip().split("\n")[0] or ""
            desc = doc and f"{name}: {doc}" or name
            count = np + nf + ne + ns
            row = self.REPORT_CLASS_TMPL.format(
                style=ne > 0 and "errorClass" or nf > 0 and "failClass" or np > 0 and "passClass" or "skipClass",
                desc=desc,
                count=count,
                Pass=np,
                fail=nf,
                error=ne,
                skip=ns,
                tries=nr,
                statistics=np / (count == 0 and 1 or count),
                cid=f"c{cid + 1}",
            )
            rows.append(row)

            for tid, (n, t, o, i, r, s) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, i, r, s)

        count = result.success_count + result.failure_count + result.error_count + result.skip_count
        report = self.REPORT_TMPL.format(
            test_list="".join(rows),
            count=count,
            Pass=result.success_count,
            fail=result.failure_count,
            skip=result.skip_count,
            error=result.error_count,
            tries=nrs,
            statistics=result.success_count / (count == 0 and 1 or count)
        )
        return report

    def _generate_report_test(self, rows, cid, tid, n, t, o, i, r, s):
        # 0: success; 1: fail; 2: error; 3: skip
        tid = (n == 0 and "p" or n == 3 and "s" or n == 2 and "e" or "f") + f"t{cid + 1}.{tid + 1}"
        name = t.id().split(".")[-1]
        doc = "_testMethodDoc" in t.__dir__() and t.__getattribute__("_testMethodDoc") or ""
        doc = doc.strip().split("\n")[0]
        desc = doc and f"{name}: {doc}" or name

        row = self.REPORT_TEST_WITH_OUTPUT_TMPL.format(
            tid=tid,
            tid1=r == 0 and tid + ".1" or tid,
            style=(n == 0 and "passCase" or n == 2 and "errorCase" or
                   n == 1 and "failCase" or n == 3 and "skipCase" or "none"),
            desc=desc,
            status_cn=self.STATUS_cn[n],
            status_en=self.STATUS_en[n],
            count=r + 1,
            tries=r
        )
        rows.append(row)

        for x in range(0, r + 1):
            img_list = ""
            if i.get(x) is not None:
                for img in i.get(x):
                    img_list += self._generate_img(img)

            script = self.REPORT_TEST_OUTPUT_TMPL.format(
                id=f"{tid}.{x + 1}",
                output=saxutils.escape(o.get(x))
            )
            if r == 0:
                row = self.REPORT_TEST_WITH_OUTPUT_SUB_TMPL.format(
                    tid=tid,
                    script=script,
                    img=img_list,
                    r=x + 1,
                )
                rows.append(row)
            else:
                row = self.REPORT_TEST_WITH_OUTPUT_SUB_RETRY_TMPL.format(
                    tid=tid,
                    r=x + 1,
                    style=(s.get(x) == 0 and "passCase" or s.get(x) == 2 and "errorCase" or
                           s.get(x) == 1 and "failCase" or s.get(x) == 3 and "skipCase" or "none"),
                    n=x + 1,
                    status_cn=self.STATUS_cn[s.get(x)],
                    status_en=self.STATUS_en[s.get(x)],
                    count=r + 1
                )
                rows.append(row)

                row = self.REPORT_TEST_WITH_OUTPUT_SUB_TMPL.format(
                    tid=tid,
                    script=script,
                    img=img_list,
                    r=x + 1
                )
                rows.append(row)

    def _generate_ending(self):
        return self.ENDING_TMPL

    def _generate_js(self):
        return self.JS

    def _generate_log(self, log_file):
        return self.REPORT_LOG_FILE_TMPL.format(
            log_file=log_file)

    def _generate_img(self, img):
        return self.REPORT_IMG_TMPL.format(img_src=img[0], alt=img[1], title=img[2])
