import logging

class COLOR:
    BLUE = "\033[34m"
    BOLD_MAGENTA = "\033[35;1m"
    BOLD_GREEN = "\033[32;1m"
    BOLD_LIGHT_MAGENTA = "\033[95;1m"
    LIGHT_GRAY = "\033[37m"
    BOLD_RED = "\033[31;1m"
    BOLD_LIGHT_GRAY = "\033[37;1m"
    YELLOW = "\033[33m"
    DARK_GRAY = "\033[90m"
    BOLD_CYAN = "\033[36;1m"
    LIGHT_RED = "\033[91m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_GREEN = "\033[92m"
    RESET = "\033[0m"
    BOLD_DARK_GRAY = "\033[90;1m"
    BOLD_LIGHT_YELLOW = "\033[93;1m"
    BOLD_LIGHT_RED = "\033[91;1m"
    BOLD_LIGHT_GREEN = "\033[92;1m"
    LIGHT_YELLOW = "\033[93m"
    BOLD_LIGHT_BLUE = "\033[94;1m"
    BOLD_LIGHT_CYAN = "\033[96;1m"
    LIGHT_BLUE = "\033[94m"
    BOLD_WHITE = "\033[97;1m"
    LIGHT_CYAN = "\033[96m"
    BLACK = "\033[30m"
    BOLD_YELLOW = "\033[33;1m"
    BOLD_BLUE = "\033[34;1m"
    GREEN = "\033[32m"
    WHITE = "\033[97m"
    BOLD_BLACK = "\033[30;1m"
    RED = "\033[31m"
    UNDERLINE = "\033[4m"

class BACKGROUND:
    BLUE = "\033[44m"
    LIGHT_GRAY = "\033[47m"
    YELLOW = "\033[43m"
    DARK_GRAY = "\033[100m"
    LIGHT_RED = "\033[101m"
    CYAN = "\033[46m"
    MAGENTA = "\033[45m"
    LIGHT_MAGENTA = "\033[105m"
    LIGHT_GREEN = "\033[102m"
    RESET = "\033[0m"
    LIGHT_YELLOW = "\033[103m"
    LIGHT_BLUE = "\033[104m"
    LIGHT_CYAN = "\033[106m"
    BLACK = "\033[40m"
    GREEN = "\033[42m"
    WHITE = "\033[107m"
    RED = "\033[41m"

logging.SUCCESS = logging.INFO + 1
logging.addLevelName(logging.SUCCESS, "SUCCESS")

logging.Logger.success = lambda self, *args, **kwargs: self.log(logging.SUCCESS, *args, **kwargs)

LOGGER = logging.getLogger("log")


class CustomFormatter(logging.Formatter):
    def __init__(self, fmt, extra=None):
        super().__init__()
        self.fmt = fmt
        self.extra = extra
        self.FORMATS = {
            logging.DEBUG: self.fmt.format(COLOR.BOLD_WHITE, COLOR.CYAN, COLOR.BOLD_WHITE, COLOR.LIGHT_CYAN, COLOR.BOLD_WHITE, COLOR.WHITE),
            logging.INFO: self.fmt.format(COLOR.BOLD_WHITE, COLOR.CYAN, COLOR.BOLD_WHITE, COLOR.BOLD_BLUE, COLOR.BOLD_WHITE, COLOR.WHITE),
            logging.WARNING: self.fmt.format(COLOR.BOLD_WHITE, COLOR.CYAN, COLOR.BOLD_WHITE, COLOR.BOLD_YELLOW, COLOR.BOLD_WHITE, COLOR.WHITE),
            logging.ERROR: self.fmt.format(COLOR.BOLD_WHITE, COLOR.CYAN, COLOR.BOLD_WHITE, COLOR.BOLD_RED, COLOR.BOLD_WHITE, COLOR.WHITE),
            logging.CRITICAL: self.fmt.format(COLOR.BOLD_WHITE, COLOR.CYAN, COLOR.BOLD_WHITE, BACKGROUND.LIGHT_RED, COLOR.RESET+COLOR.BOLD_WHITE, COLOR.WHITE),
            logging.SUCCESS: self.fmt.format(COLOR.BOLD_WHITE, COLOR.CYAN, COLOR.BOLD_WHITE, COLOR.BOLD_LIGHT_GREEN, COLOR.BOLD_WHITE, COLOR.WHITE)
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.extra)
        return formatter.format(record)



LOGGER_HANDLER = logging.StreamHandler()


LOGGER_HANDLER.setFormatter(CustomFormatter("\r{0}[{1}%(asctime)s{2}] [{3}%(levelname)s{4}] {5}%(message)s", "%H:%M:%S"))


LOGGER.addHandler(LOGGER_HANDLER)

LOGGER.setLevel(logging.DEBUG)
