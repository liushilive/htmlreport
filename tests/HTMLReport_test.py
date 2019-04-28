import base64
import logging
import random
import unittest

import HTMLReport
from HTMLReport import addImage, logger, ddt, retry, no_retry, log


def parse_int(s):
    return int(s)


LOG = logging.getLogger(__name__)


@ddt.ddt
class test_1th(unittest.TestCase):
    def setUp(self):
        # logger().info("setUp")
        log.debug("setUp")
        # log.info("setUp")

    def tearDown(self):
        log.info("tearDown")

    @classmethod
    def setUpClass(cls):
        log.info("setUpClass")
        cls.i = 0

    @classmethod
    def tearDownClass(cls):
        log.info("tearDownClass")

    @retry
    @ddt.data(1, 2, 3)
    def test_error(self, x):
        """测试错误"""
        log.error("测试错误 {}".format(x))
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
        if random.randint(1, 6) != 6:
            raise ValueError

    def test_isupper(self):
        """测试isupper"""
        logger().info("测试isupper")
        LOG.info("11111111111111111111111111111111111111111111111111111")
        self.assertTrue('FOO'.isupper(), "真")
        self.assertFalse('Foo'.isupper(), '假')

    @retry
    def test_fail_retry(self):
        """测试失败重试"""
        logger().info("测试失败")
        self.i += 1
        self.assertEqual(3, self.i, "相等")

    @no_retry
    def test_fail(self):
        log.info("测试失败")
        self.assertEqual(30, self.i, "相等")

    @unittest.skip("这是一个跳过的测试")
    def test_skip(self):
        logger().warning("测试跳过")
        pass


class test_2th(unittest.TestCase):
    def test_bad_int(self):
        """测试异常类型"""
        logger().info("测试异常类型")
        self.assertRaises(ValueError, parse_int("1.5"), 'N/A')

    def test_upper(self):
        """测试相等"""
        logger().critical('测试相等')
        self.assertEqual('foo'.upper(), '00')


class test_第三个测试(unittest.TestCase):
    a = None

    @classmethod
    def setUpClass(cls):
        """公共"""
        cls.a = 3
        LOG.info("a : {}".format(cls.a))

    @classmethod
    def tearDownClass(cls):
        LOG.info("a : {}".format(cls.a))

    def test_True(self):
        """测试True"""
        test_第三个测试.a += 1
        self.assertTrue(self.a)

    @retry
    def test_False(self):
        """测试FALSE"""
        test_第三个测试.a -= 1
        self.assertFalse(self.a)


if __name__ == '__main__':
    # 测试套件
    suite = unittest.TestSuite()
    # 测试用例加载器
    loader = unittest.TestLoader()
    # 把测试用例加载到测试套件中
    suite.addTests(loader.loadTestsFromTestCase(test_1th))
    suite.addTests(loader.loadTestsFromTestCase(test_2th))
    suite.addTests(loader.loadTestsFromTestCase(test_第三个测试))

    # 测试用例执行器
    runner = HTMLReport.TestRunner(
        report_file_name='index',
        output_path='report',
        title='一个简单的测试报告',
        description='随意描述',
        thread_count=5,
        thread_start_wait=0,
        tries=5,
        retry=True,
        sequential_execution=True,
        lang='cn'
    )
    # 执行测试用例套件
    runner.run(suite)
