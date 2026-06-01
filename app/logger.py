from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")
# Optional: Add file logging
# logger.add("cryptokali.log", rotation="10 MB")
