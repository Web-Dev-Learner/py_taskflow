import logging
import structlog
from colorlog import ColoredFormatter

def setup_logger(service_name: str):
    """
    Configure a structured, colored logger for each service.
    Usage:
        logger = setup_logger("Scheduler")
    """
    # Define colored log format
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s] → %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    # Stream logs to console
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Create logger
    logger = logging.getLogger(service_name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Structlog configuration
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return logger
