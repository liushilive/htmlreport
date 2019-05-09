import base64
import logging
import random
import unittest

from HTMLReport import ddt, retry, TestRunner, addImage


class TS_1(unittest.TestCase):
    """第一组测试"""

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
            alt = """百度一下你就知道了，我是一个很长很长的文本哦,
我还换行了哦
再来一个"""
            addImage(image, "百度 {}".format(random.randint(0, 10)), alt)
            addImage(image, "百度 {}".format(random.randint(0, 10)), alt)
            addImage(image, "百度 {}".format(random.randint(0, 10)), alt)
            addImage(image, "百度 {}".format(random.randint(0, 10)), alt)
            addImage(image, "百度 {}".format(random.randint(0, 10)), alt)


@ddt.ddt
class TS_2(unittest.TestCase):
    """第二组测试"""

    def setUp(self) -> None:
        logging.info("测试开始")

    def tearDown(self) -> None:
        logging.info("测试结束")

    @retry
    @ddt.data(*range(1, 6))
    def test_a(self, n):
        """
        数据驱动
        :param n:
        :return:
        """
        self.assertEqual(n, random.randint(1, 6))


class TS_3(unittest.TestCase):
    """
    第三组测试
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
        """
        测试 setUpClass
        :return:
        """
        self.__class__.n += 1
        logging.info(f"运行修改：{self.n}")

    def test_2(self):
        """
        测试 setUpClass
        :return:
        """
        self.__class__.n += 1
        logging.info(f"运行修改：{self.n}")


if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TS_1))
    suite.addTests(loader.loadTestsFromTestCase(TS_2))
    suite.addTests(loader.loadTestsFromTestCase(TS_3))

    TestRunner(
        report_file_name='index',
        output_path='report',
        title='一个简单的测试报告',
        description='随意描述',
        thread_count=10,
        thread_start_wait=0,
        tries=5,
        retry=False,
        sequential_execution=True,
        lang='cn'
    ).run(suite, debug=True)
