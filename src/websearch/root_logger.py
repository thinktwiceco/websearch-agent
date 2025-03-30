import logging
from enum import Enum

from pydantic_settings import BaseSettings

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10

class LevelString(Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LogLevel(BaseSettings):
    BROSER_SEARCHLOG_LEVEL: LevelString = LevelString.INFO

    def to_int(self) -> int:
        return {
            LevelString.CRITICAL: CRITICAL,
            LevelString.ERROR: ERROR,
            LevelString.WARNING: WARNING,
            LevelString.INFO: INFO,
            LevelString.DEBUG: DEBUG,
        }[self.BROSER_SEARCHLOG_LEVEL]

log_level = LogLevel()

# Configure the root logger with custom formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



# Create a logger object
_root_logger = logging.getLogger()

class RootLogger:
    def __init__(self,
            logger: logging.Logger = _root_logger,
            name: str = "websearch",
            level: int = log_level.to_int()):

        self.logger = logger
        self.name = name
        self.level = level

    def getChild(self, name: str):
        return RootLogger(self.logger, self.name + "." + name)

    def log_prompt(self, agent: str, message: str):
        self.logger.info("==============[ 🔍 request for "+agent+" ]================")
        for line in message.split("\n"):
            self.logger.info(line)

    def log_response(self, agent: str, message: str):
        self.logger.info("==============[ 💬 response from "+agent+" ]================")
        for line in message.split("\n"):
            self.logger.info(line)

    def debug_system_prompt(self, agent: str, message: str):
        self.logger.info("")
        self.logger.info("+------------[ 🤖 system prompt for "+agent+"]------------------+")
        for line in message.split("\n"):
            self.logger.info("| "+line)
        self.logger.info("+---------------------------------------------------------------+")
        self.logger.info("")

    def info(self, message: str):
        self.logger.info("🟢 "+message)

    def debug(self, message: str):
        self.logger.debug("🔵 "+message)

    def warning(self, message: str):
        self.logger.warning("🟡 "+ message)

    def error(self, message: str):
        self.logger.error("🔴 "+message)


root_logger = RootLogger(_root_logger, "websearch")

root_logger.info("LogLevel: "+str(log_level.BROSER_SEARCHLOG_LEVEL))

root_logger.info("INFO: Hello, world!")
root_logger.debug("DEBUG: Hello, world!")
root_logger.warning("WARNING: Hello, world!")
root_logger.error("ERROR: Hello, world!")
