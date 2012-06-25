__author__ = 'jeffrey'

import logging

log = logging.getLogger('scraper')
log.setLevel(logging.DEBUG)
if not len(log.handlers):
    handler = logging.FileHandler(filename='log.txt')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)