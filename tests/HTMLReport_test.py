import base64
import logging
import random
import unittest

from HTMLReport import ddt, TestRunner, addImage, no_retry, retry


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
                addImage(image, f"百度 {i}", alt)


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
