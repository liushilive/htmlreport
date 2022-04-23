# HTMLReport

[![Downloads](https://pepy.tech/badge/htmlreport)](https://pepy.tech/project/htmlreport)

`HTMLReport`是一个单元测试测试运行器，可以将测试结果保存在 Html 文件中，用于人性化的结果显示。

仅支持**Python 3.x**

* [The report template](https://liushilive.github.io/report/report/#en)

* [报告样板](https://liushilive.github.io/report/report/#cn)

## 安装

要安装 HTMLReport，请在终端中运行此命令

```bash
pip install HTMLReport
```

这是安装HTMLReport的首选方法，因为它将始终安装最新的稳定版本。 如果您没有安装 [pip](https://pip.pypa.io/)，
则该 [Python安装指南](http://docs.python-guide.org/en/latest/starting/installation/ "Python安装指南")
可以指导您完成该过程。

## 使用方法

### 日志

为测试报告中添加过程日志，在多线程下，在报告中会分别记录每个线程的日志，同时会产生与测试报告同名的测试 log 文件。

```python
import logging

logging.info("测试")
logging.debug("测试")
logging.warning("测试")
logging.error("测试")
logging.critical("测试")
```

### 图片信息

为测试报告添加图片信息，请将图片信息编码为 base64 编码。

如采用的是 selenium 截屏，请使用 `get_screenshot_as_base64()` 方法获取 base64 encoded string 作为参数传入。

本库会自动将图片保存在报告路径下的`images`目录下，并嵌入到报告中。

```python
import base64
from HTMLReport import add_image

with open("baidu.png", 'rb') as f:
    image = base64.b64encode(f.read())
    add_image(image, "图片标题", "图片描述")
```

### 失败重试

测试方法前加入装饰器 `@retry` `@no_retry`，用于重试与不重试

### 数据驱动

测试类前加入装饰器 `@ddt.ddt`

测试方法前加入装饰器 `@ddt.data(*data)`

### 实例

```python
import base64
import logging
import random
import unittest

from HTMLReport import ddt, TestRunner, add_image, no_retry, retry


class TestOne(unittest.TestCase):
    """常规测试"""

    def setUp(self) -> None:
        logging.debug("测试开始")
        logging.info("测试开始")
        logging.warning("测试开始")
        logging.error("测试开始")

    def tearDown(self) -> None:
        logging.info("测试结束")

    def test_true(self):
        """
        测试通过
        """
        self.assertTrue(True)

    def test_false(self):
        """
        测试失败

        :return:
        """
        self.assertTrue(False)

    def test_error(self):
        """
        测试异常

        :return:
        """
        self.assertTrue(int("5.2"))

    @unittest.skip("跳过用例")
    def test_skip(self):
        """
        测试跳过

        :return:
        """
        self.assertTrue(int("5.2"))

    def test_skip_(self):
        """
        测试中途跳过

        :return:
        """
        logging.info("准备跳过")
        self.skipTest("中途跳过")
        self.assertTrue(int("5.2"))

    def test_image(self):
        """测试截图"""
        with open("baidu.png", 'rb') as f:
            image = base64.b64encode(f.read())
            alt = """百度一下，你就知道了。"""
            for i in range(5):
                add_image(image, f"百度 {i}", alt)


@ddt.ddt
class TestDDT(unittest.TestCase):
    """DDT 测试"""

    def setUp(self) -> None:
        logging.info("测试开始")

    def tearDown(self) -> None:
        logging.info("测试结束")

    @ddt.data(*range(3))
    def test_a(self, n):
        self.assertEqual(n, random.randint(0, 2))


@ddt.ddt
class TestNoRetry(unittest.TestCase):
    """测试 DDT 不重试"""

    def setUp(self) -> None:
        logging.info("测试开始")

    def tearDown(self) -> None:
        logging.info("测试结束")

    @no_retry
    @ddt.data(*range(3))
    def test_a(self, n):
        self.assertEqual(n, random.randint(0, 2))


@ddt.ddt
class TestRetry(unittest.TestCase):
    """测试 DDT 重试"""

    def setUp(self) -> None:
        logging.info("测试开始")

    def tearDown(self) -> None:
        logging.info("测试结束")

    @retry
    @ddt.data(*range(3))
    def test_a(self, n):
        self.assertEqual(n, random.randint(0, 2))


class TestClassMethod(unittest.TestCase):
    """
    测试 setUpClass
    """

    n = 0

    @classmethod
    def setUpClass(cls) -> None:
        logging.info(f"初始计数：{cls.n}")

    @classmethod
    def tearDownClass(cls) -> None:
        logging.info(f"最终计数：{cls.n}")

    def setUp(self) -> None:
        logging.info(f"前置计数：{self.n}")

    def tearDown(self) -> None:
        logging.info(f"后置计数：{self.n}")

    def test_1(self):
        self.__class__.n += 1
        logging.info(f"运行修改：{self.n}")

    def test_2(self):
        self.__class__.n += 1
        logging.info(f"运行修改：{self.n}")
        self.assertTrue(False)


if __name__ == '__main__':
    test_runner = TestRunner(
        report_file_name="index",
        output_path="report",
        title="一个简单的测试报告",
        description="随意描述",
        thread_count=5,
        thread_start_wait=0.1,
        tries=3,
        delay=0,
        back_off=1,
        retry=True,
        sequential_execution=True,
        lang="cn"
    )
    suite = unittest.TestSuite()
    suite_sub = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite_sub.addTests(loader.loadTestsFromTestCase(TestOne))
    suite_sub.addTests(loader.loadTestsFromTestCase(TestDDT))
    suite.addTests(suite_sub)
    suite.addTests(loader.loadTestsFromTestCase(TestRetry))
    suite.addTests(loader.loadTestsFromTestCase(TestNoRetry))
    suite.addTests(loader.loadTestsFromTestCase(TestClassMethod))
    suite.addTests(loader.loadTestsFromNames(["HTMLReport_test.TestClassMethod"]))
    test_runner.run(suite)

```

> 如果您有其他的需求，请发邮件给我：<liushilive@outlook.com> ， 祝您使用愉快！

Links:

---------

* [https://liushilive.github.io](https://liushilive.github.io "Github")
