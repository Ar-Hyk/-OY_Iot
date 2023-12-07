import logging
import os
from logging.handlers import TimedRotatingFileHandler


class Colored:
    # 显示格式: \033[显示方式;前景色;背景色m
    # 只写一个字段表示前景色,背景色默认
    RED = '\033[31m'  # 红色
    GREEN = '\033[32m'  # 绿色
    YELLOW = '\033[33m'  # 黄色
    BLUE = '\033[34m'  # 蓝色
    FUCHSIA = '\033[35m'  # 紫红色
    CYAN = '\033[36m'  # 青蓝色
    WHITE = '\033[37m'  # 白色
    #: no color
    RESET = '\033[0m'  # 终端默认颜色


# # 日志等级，critical > error > warning > info > debug
# class Logger:
#     def __init__(self, file_dir=None):
#         if file_dir is None:
#             file_dir = './log.log'
#         # 日志器- Logger
#         self.logger = logging.getLogger()
#
#         # 处理器- Handler
#         debug_stream = logging.StreamHandler()
#         info_stream = logging.StreamHandler()
#         warning_stream = logging.StreamHandler()
#         error_stream = logging.StreamHandler()
#         # file = logging.FileHandler(file_dir, encoding='utf-8')
#         file = TimedRotatingFileHandler(file_dir, when='d', interval=1, backupCount=7, encoding='utf-8')
#
#         debug_stream.setLevel(logging.DEBUG)
#         info_stream.setLevel(logging.INFO)
#         warning_stream.setLevel(logging.WARNING)
#         error_stream.setLevel(logging.ERROR)
#         file.setLevel(logging.DEBUG)
#
#         # 格式器- Formatter
#         debug_formatter = logging.Formatter(f'{Colored.CYAN}[%(asctime)s][%(levelname)s]:  %(message)s')
#         info_formatter = logging.Formatter(f'{Colored.GREEN}[%(asctime)s][%(levelname)s]:  %(message)s')
#         warning_formatter = logging.Formatter(f'{Colored.FUCHSIA}[%(asctime)s][%(levelname)s]:  %(message)s')
#         error_formatter = logging.Formatter(f'{Colored.RED}[%(asctime)s][%(levelname)s]:  %(message)s')
#         f_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')
#
#         # Handle设置
#         debug_stream.setFormatter(debug_formatter)
#         info_stream.setFormatter(info_formatter)
#         warning_stream.setFormatter(warning_formatter)
#         error_stream.setFormatter(error_formatter)
#         file.setFormatter(f_formatter)
#
#         # 过滤器- Filter
#         class debug_filter(logging.Filter):
#             def filter(self, record):
#                 return record.levelname == 'DEBUG'
#
#         class info_filter(logging.Filter):
#             def filter(self, record):
#                 return record.levelname == 'INFO'
#
#         class warning_filter(logging.Filter):
#             def filter(self, record):
#                 return record.levelname == 'WARNING'
#
#         class error_filter(logging.Filter):
#             def filter(self, record):
#                 return record.levelname == 'ERROR'
#
#         debug_stream.addFilter(debug_filter())
#         info_stream.addFilter(info_filter())
#         warning_stream.addFilter(warning_filter())
#         error_stream.addFilter(error_filter())
#
#         # Logger设置
#         self.logger.setLevel(logging.DEBUG)
#         self.logger.addHandler(debug_stream)
#         self.logger.addHandler(info_stream)
#         self.logger.addHandler(warning_stream)
#         self.logger.addHandler(error_stream)
#         self.logger.addHandler(file)


# 日志器- Logger
logger = logging.getLogger()

# 处理器- Handler
__debug_stream = logging.StreamHandler()
__info_stream = logging.StreamHandler()
__warning_stream = logging.StreamHandler()
__error_stream = logging.StreamHandler()
# 滚动式日志
__file = TimedRotatingFileHandler(os.getenv('LOG_DIR'), when='d', interval=1, backupCount=7, encoding='utf-8')

__debug_stream.setLevel(logging.DEBUG)
__info_stream.setLevel(logging.INFO)
__warning_stream.setLevel(logging.WARNING)
__error_stream.setLevel(logging.ERROR)
__file.setLevel(logging.DEBUG)

# 格式器- Formatter
debug_formatter = logging.Formatter(f'{Colored.CYAN}[%(asctime)s][%(levelname)s]:  %(message)s')
info_formatter = logging.Formatter(f'{Colored.GREEN}[%(asctime)s][%(levelname)s]:  %(message)s')
warning_formatter = logging.Formatter(f'{Colored.FUCHSIA}[%(asctime)s][%(levelname)s]:  %(message)s')
error_formatter = logging.Formatter(f'{Colored.RED}[%(asctime)s][%(levelname)s]:  %(message)s')
f_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')

# Handle设置
__debug_stream.setFormatter(debug_formatter)
__info_stream.setFormatter(info_formatter)
__warning_stream.setFormatter(warning_formatter)
__error_stream.setFormatter(error_formatter)
__file.setFormatter(f_formatter)


# 过滤器- Filter
class __debug_filter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'DEBUG'


class __info_filter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'INFO'


class __warning_filter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'WARNING'


class __error_filter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'ERROR'


__debug_stream.addFilter(__debug_filter())
__info_stream.addFilter(__info_filter())
__warning_stream.addFilter(__warning_filter())
__error_stream.addFilter(__error_filter())

# Logger设置
logger.setLevel(logging.DEBUG)
logger.addHandler(__debug_stream)
logger.addHandler(__info_stream)
logger.addHandler(__warning_stream)
logger.addHandler(__error_stream)
logger.addHandler(__file)
