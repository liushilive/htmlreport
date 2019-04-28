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
import HTMLReport

# 测试套件
suite = unittest.TestSuite()
# 测试用例加载器
loader = unittest.TestLoader()
# 把测试用例加载到测试套件中
suite.addTests(loader.loadTestsFromTestCase(TestStringMethods))

# 测试用例执行器
runner = HTMLReport.TestRunner(report_file_name='test',  # 报告文件名，如果未赋值，将采用“test+时间戳”
                               output_path='report',  # 保存文件夹名，默认“report”
                               title='测试报告',  # 报告标题，默认“测试报告”
                               description='无测试描述',  # 报告描述，默认“测试描述”
                               thread_count=1,  # 并发线程数量（无序执行测试），默认数量 1
                               thread_start_wait=3,  # 各线程启动延迟，默认 0 s
                               sequential_execution=False,  # 是否按照套件添加(addTests)顺序执行，
                               # 会等待一个addTests执行完成，再执行下一个，默认 False
                               # 如果用例中存在 tearDownClass ，建议设置为True，
                               # 否则 tearDownClass 将会在所有用例线程执行完后才会执行。
                               # lang='en'
                               lang='cn'  # 支持中文与英文，默认中文
                               )
# 执行测试用例套件
runner.run(suite)
```

### 日志

为测试报告中添加过程日志，在多线程下，在报告中会分别记录每个线程的日志，同时会产生与测试报告同名的测试 log 文件。

```python
from HTMLReport import logger

logger().info("测试")
logger().debug("测试")
logger().warning("测试")
logger().error("测试")
logger().critical("测试")
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

>

如果您有其他的需求，请发邮件给我：<liushilive@outlook.com> ， 祝您使用愉快！

Links:

---------

* [https://liushilive.github.io](https://liushilive.github.io "Github")
