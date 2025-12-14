"""
Logging configuration for the crowd monitoring system.
"""

import logging
import sys

# Configure logging with ASCII-safe formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crowd_monitor.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name)
