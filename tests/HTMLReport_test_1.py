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
