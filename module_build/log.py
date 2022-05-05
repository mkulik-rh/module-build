import logging
import sys
import time

logger = logging.getLogger("module-build")


def init_logging(cwd, yaml_filename, logger, verbose):
    main_log_file_path = cwd + "/{yaml}-module-build-{timestamp}.log".format(
        yaml=yaml_filename,
        timestamp=int(time.time())
    )
    log_format = '%(asctime)s | %(levelname)s | %(message)s'

    logger_lvl = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(logger_lvl)

    log_formatter = logging.Formatter(log_format)

    # Create file handler for logging to a file (logs all five levels)
    file_handler = logging.FileHandler(main_log_file_path)
    file_handler.setLevel(logger_lvl)
    file_handler.setFormatter(log_formatter)

    # Create stdout handler for logging to the console (logs all five levels)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logger_lvl)
    stdout_handler.setFormatter(CustomFormatter(log_format))

    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)


class CustomFormatter(logging.Formatter):

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.fmt_split = self.fmt.split("|")
        self.FORMATS = {
            logging.DEBUG: f"{self.fmt_split[0]}|{self.grey}{self.fmt_split[1]}{self.reset}|{self.fmt_split[2]}",
            logging.INFO: f"{self.fmt_split[0]}|{self.blue}{self.fmt_split[1]}{self.reset}|{self.fmt_split[2]}",
            logging.WARNING: f"{self.fmt_split[0]}|{self.yellow}{self.fmt_split[1]}{self.reset}|{self.fmt_split[2]}",
            logging.ERROR: f"{self.fmt_split[0]}|{self.red}{self.fmt_split[1]}{self.reset}|{self.fmt_split[2]}",
            logging.CRITICAL: f"{self.fmt_split[0]}|{self.bold_red}{self.fmt_split[1]}{self.reset}|{self.fmt_split[2]}",
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
