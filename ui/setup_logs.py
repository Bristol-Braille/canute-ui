import logging


def setup_logs(config, loglevel):
    log_file = config.get('files', 'log_file')
    log_format = logging.Formatter(
        '%(asctime)s - %(name)-16s - %(levelname)-8s - %(message)s')
    # configure the client logging
    log = logging.getLogger('')
    # has to be set to debug as is the root logger
    log.setLevel(logging.DEBUG)

    # create console handler and set level to info
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    # create formatter for console
    ch.setFormatter(log_format)
    log.addHandler(ch)

    # create file handler and set to debug
    fh = logging.FileHandler(log_file)
    fh.setLevel(loglevel)

    fh.setFormatter(log_format)
    log.addHandler(fh)

    return log
