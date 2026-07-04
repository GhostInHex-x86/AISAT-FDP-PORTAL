import os
import logging
from config import LOG_FOLDER

LOG_FILE = os.path.join(LOG_FOLDER, "app.log")

os.makedirs(LOG_FOLDER, exist_ok=True)

logger = logging.getLogger("fdp_portal")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
