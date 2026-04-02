import logging

def get_logger(name):
    logger_name = "client"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # # Adding a handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s][%(name)s] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

