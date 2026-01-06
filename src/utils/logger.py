import logging
import os

if not os.path.exists("logs"):
    os.makedirs("logs")

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/sentinel.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("CyberSentinel")