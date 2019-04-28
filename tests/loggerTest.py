import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from HTMLReport.tools.log.HandlerFactory import HandlerFactory
from HTMLReport.tools.log.Logger import GeneralLogger


def worker(message):
    logger = GeneralLogger().get_logger(True)
    print("Start")
    logger.info(message + ' info')
    logger.debug(message + ' 调试')
    logger.warning(message + ' 警告')
    logger.error(message + ' 错误')
    print("end")
    print("--------------\n", str(threading.current_thread().ident),
          HandlerFactory.get_stream_value(), "\n-----------------")


GeneralLogger().set_log_path('report/test.log')
GeneralLogger().set_log_by_thread_log(True)
GeneralLogger().set_log_level(logging.DEBUG)
main_logger = GeneralLogger().get_logger()
main_logger.debug('debug')
main_logger.warning('warning')
main_logger.info('info')
main_logger.error('error')

with ThreadPoolExecutor(10) as pool:
    args = 'worker '
    for arg in range(2):
        pool.submit(worker, args + str(arg))
