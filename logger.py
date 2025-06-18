import logging

# Create the shared logger instance
logger = logging.getLogger("VPN")
logger.setLevel(logging.INFO)  # <-- VERY IMPORTANT: sets the logging level

def set_log_file(path: str):
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # File logging
    file_handler = logging.FileHandler(path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)  # Ensure file handler respects INFO level

    # Optional console logging
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def log(title: str, data: str = ""):
    """Central log call."""
    logger.info(f"{title}: {data}")

def log_error(title: str, data: str = ""):
    """Central error log call."""
    logger.error(f"{title}: {data}")
