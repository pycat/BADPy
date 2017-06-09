import logging


def initialize_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)-8.8s] [%(filename)s : L.%(lineno)s - %(funcName)20.20s() ]"
                                  " %(message)s")
    formatter_info = logging.Formatter("[%(levelname)-8.8s] %(message)s")

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter_info)
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler("badpy_error.log", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler("badpy_all.log")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
