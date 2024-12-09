import logging
from colorama import Fore, Style, init

init(autoreset=True)

class ColorfulLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.hasHandlers():
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.CustomFormatter())
            self.logger.addHandler(console_handler)

    class CustomFormatter(logging.Formatter):
        FORMATS = {
            logging.INFO: f"{Fore.GREEN}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
            logging.WARNING: f"{Fore.YELLOW}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
            logging.ERROR: f"{Fore.RED}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
            'DEFAULT': "%(asctime)s - %(levelname)s - %(message)s"
        }

        def format(self, record):
            log_format = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
            formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
            return formatter.format(record)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)
