"""Logging configuration and utilities for the websearch package.

This module provides logging functionality with customizable log levels
and specialized formatters for different types of content like prompts,
responses, and system messages. It configures the root logger and
provides a convenient RootLogger wrapper class.
"""

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
    """Enum representing log level names as strings.

    These string values map to their corresponding numeric log levels.
    """

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LogLevel(BaseSettings):
    """Configuration class for log levels using Pydantic settings.

    Attributes:
        BROWSER_SEARCHLOG_LEVEL (LevelString): The configured log level for the browser search,
            defaults to INFO.
    """

    BROWSER_SEARCHLOG_LEVEL: LevelString = LevelString.INFO

    def to_int(self) -> int:
        """Convert the configured log level to its integer representation.

        Returns:
            int: The integer value of the configured log level.
        """
        return {
            LevelString.CRITICAL: CRITICAL,
            LevelString.ERROR: ERROR,
            LevelString.WARNING: WARNING,
            LevelString.INFO: INFO,
            LevelString.DEBUG: DEBUG,
        }[self.BROWSER_SEARCHLOG_LEVEL]


log_level = LogLevel()

# Configure the root logger with custom formatting
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# Create a logger object
_root_logger = logging.getLogger()


class RootLogger:
    """A wrapper around the standard logging.Logger with additional functionality.

    This class provides custom logging methods for prompts, responses, and system
    messages with specialized formatting.

    Args:
        logger (logging.Logger): The logger instance to wrap, defaults to the root logger.
        name (str): The name for this logger, defaults to "websearch".
        level (int): The log level to use, defaults to the configured log level.
    """

    def __init__(
        self,
        logger: logging.Logger = _root_logger,
        name: str = "websearch",
        level: int = log_level.to_int(),
    ):
        """Initialize the RootLogger with a logger instance, name, and level.

        Args:
            logger (logging.Logger): The logger instance to wrap, defaults to the root logger.
            name (str): The name for this logger, defaults to "websearch".
            level (int): The log level to use, defaults to the configured log level.
        """
        self.logger = logger
        self.name = name
        self.level = level

    def getChild(self, name: str):
        """Create a child logger with a hierarchical name.

        Args:
            name (str): The suffix to append to the current logger name.

        Returns:
            RootLogger: A new RootLogger instance with the combined name.
        """
        return RootLogger(self.logger, self.name + "." + name)

    def log_prompt(self, agent: str, message: str):
        """Log a prompt request with special formatting.

        Args:
            agent (str): The name of the agent receiving the prompt.
            message (str): The content of the prompt.
        """
        self.logger.info(
            "==============[ 🔍 request for " + agent + " ]================"
        )
        for line in message.split("\n"):
            self.logger.info(line)

    def log_response(self, agent: str, message: str):
        """Log a response with special formatting.

        Args:
            agent (str): The name of the agent providing the response.
            message (str): The content of the response.
        """
        self.logger.info(
            "==============[ 💬 response from " + agent + " ]================"
        )
        for line in message.split("\n"):
            self.logger.info(line)

    def debug_system_prompt(self, agent: str, message: str):
        """Log a system prompt with special formatting.

        Args:
            agent (str): The name of the agent receiving the system prompt.
            message (str): The content of the system prompt.
        """
        self.logger.info("")
        self.logger.info(
            "+------------[ 🤖 system prompt for " + agent + "]------------------+"
        )
        for line in message.split("\n"):
            self.logger.info("| " + line)
        self.logger.info(
            "+---------------------------------------------------------------+"
        )
        self.logger.info("")

    def info(self, message: str):
        """Log an info level message with a green circle prefix.

        Args:
            message (str): The message to log.
        """
        self.logger.info("🟢 " + message)

    def debug(self, message: str):
        """Log a debug level message with a blue circle prefix.

        Args:
            message (str): The message to log.
        """
        self.logger.debug("🔵 " + message)

    def warning(self, message: str):
        """Log a warning level message with a yellow circle prefix.

        Args:
            message (str): The message to log.
        """
        self.logger.warning("🟡 " + message)

    def error(self, message: str):
        """Log an error level message with a red circle prefix.

        Args:
            message (str): The message to log.
        """
        self.logger.error("🔴 " + message)


root_logger = RootLogger(_root_logger, "websearch")

root_logger.info("LogLevel: " + str(log_level.BROWSER_SEARCHLOG_LEVEL))

root_logger.info("INFO: Hello, world!")
root_logger.debug("DEBUG: Hello, world!")
root_logger.warning("WARNING: Hello, world!")
root_logger.error("ERROR: Hello, world!")
