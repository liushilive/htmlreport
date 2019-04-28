# HTMLReport

`HTMLReport`是一个单元测试测试运行器，可以将测试结果保存在 Html 文件中，用于人性化的结果显示。

仅支持**Python 3.x**

* [The report template](https://liushilive.github.io/report/report/#en)

* [报告样板](https://liushilive.github.io/report/report/#cn)

## 安装

要安装 HTMLReport，请在终端中运行此命令

```bash
pip install HTMLReport
```

这是安装HTMLReport的首选方法，因为它将始终安装最新的稳定版本。如果您没有安装[pip](https://pip.pypa.io/)，则该[Python安装指南](http://docs.python-guide.org/en/latest/starting/installation/ "Python安装指南")可以指导您完成该过程。

## 使用方法

```python
import unittest
import random
from HTMLReport import (TestRunner,
                        log,
                        ddt,
                        retry)


class TS_1(unittest.TestCase):
    def setUp(self) -> None:
        log.info("测试开始")

    def tearDown(self) -> None:
        log.info("测试结束")

    def test_true(self):
        self.assertTrue(True)

    def test_false(self):
        self.assertTrue(False)

    def test_error(self):
        self.assertTrue(int("5.2"))


@ddt.ddt
class TS_2(unittest.TestCase):
    def setUp(self) -> None:
        log.info("测试开始")

    def tearDown(self) -> None:
        log.info("测试结束")

    @ddt.data(*range(1, 6))
    @retry
    def test_a(self, n):
        self.assertEqual(n, random.randint(1, 6))


if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TS_1))
    suite.addTests(loader.loadTestsFromTestCase(TS_2))

    TestRunner(
        report_file_name='index',
        output_path='report',
        title='一个简单的测试报告',
        description='随意描述',
        thread_count=5,
        thread_start_wait=0,
        tries=5,
        retry=False,
        sequential_execution=True,
        lang='cn'
    ).run(suite)
```

### 日志

为测试报告中添加过程日志，在多线程下，在报告中会分别记录每个线程的日志，同时会产生与测试报告同名的测试 log 文件。

```python
from HTMLReport import log

log.info("测试")
log.debug("测试")
log.warning("测试")
log.error("测试")
log.critical("测试")
```

### 图片信息

为测试报告添加图片信息，请将图片信息编码为 base64 编码。

如采用的是 selenium 截屏，请使用 `get_screenshot_as_base64()` 方法获取 base64 encoded string 作为参数传入。

本库会自动将图片保存在报告路径下的`images`目录下，并嵌入到报告中。

```python
import base64
from HTMLReport import addImage

with open("baidu.png", 'rb') as f:
    image = base64.b64encode(f.read())
    addImage(image, "图片标题", "图片描述")
```

### 失败重试

测试方法前加入装饰器 `@retry` `@no_retry`，用于重试与不重试

### 数据驱动

测试类前加入装饰器 `@ddt.ddt` 

测试方法前加入装饰器 `@ddt.data(*data)`

>

如果您有其他的需求，请发邮件给我：<liushilive@outlook.com> ， 祝您使用愉快！

Links:

---------

* [https://liushilive.github.io](https://liushilive.github.io "Github")
