import logging

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Define logging functions for different levels
def info(*args):
    message = " ".join(str(a) for a in args)
    logging.info(message)

def warning(*args):
    message = " ".join(str(a) for a in args)
    logging.warning(message)

def error(*args):
    message = " ".join(str(a) for a in args)
    logging.error(message)