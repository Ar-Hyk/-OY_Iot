import logging
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


# 日志等级，critical > error > warning > info > debug
class Logger:
    def __init__(self, file_dir=None):
        if file_dir is None:
            file_dir = './log.log'
        # 日志器- Logger
        self.logger = logging.getLogger('logger')

        # 处理器- Handler
        debug_stream = logging.StreamHandler()
        info_stream = logging.StreamHandler()
        warning_stream = logging.StreamHandler()
        error_stream = logging.StreamHandler()
        # file = logging.FileHandler(file_dir, encoding='utf-8')
        file = TimedRotatingFileHandler(file_dir, when='d', interval=1, backupCount=7, encoding='utf-8')

        debug_stream.setLevel(logging.DEBUG)
        info_stream.setLevel(logging.INFO)
        warning_stream.setLevel(logging.WARNING)
        error_stream.setLevel(logging.ERROR)
        file.setLevel(logging.DEBUG)

        # 格式器- Formatter
        debug_formatter = logging.Formatter(f'{Colored.CYAN}[%(asctime)s][%(levelname)s]:  %(message)s')
        info_formatter = logging.Formatter(f'{Colored.GREEN}[%(asctime)s][%(levelname)s]:  %(message)s')
        warning_formatter = logging.Formatter(f'{Colored.FUCHSIA}[%(asctime)s][%(levelname)s]:  %(message)s')
        error_formatter = logging.Formatter(f'{Colored.RED}[%(asctime)s][%(levelname)s]:  %(message)s')
        f_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')

        # Handle设置
        debug_stream.setFormatter(debug_formatter)
        info_stream.setFormatter(info_formatter)
        warning_stream.setFormatter(warning_formatter)
        error_stream.setFormatter(error_formatter)
        file.setFormatter(f_formatter)

        # 过滤器- Filter
        class debug_filter(logging.Filter):
            def filter(self, record):
                return record.levelname == 'DEBUG'

        class info_filter(logging.Filter):
            def filter(self, record):
                return record.levelname == 'INFO'

        class warning_filter(logging.Filter):
            def filter(self, record):
                return record.levelname == 'WARNING'

        class error_filter(logging.Filter):
            def filter(self, record):
                return record.levelname == 'ERROR'

        debug_stream.addFilter(debug_filter())
        info_stream.addFilter(info_filter())
        warning_stream.addFilter(warning_filter())
        error_stream.addFilter(error_filter())

        # Logger设置
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(debug_stream)
        self.logger.addHandler(info_stream)
        self.logger.addHandler(warning_stream)
        self.logger.addHandler(error_stream)
        self.logger.addHandler(file)
