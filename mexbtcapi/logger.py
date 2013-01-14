import sys
import logging


log = logging.getLogger('mexbtcapi')

hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('MEXBTCAPI: %(message)s')
hdlr.setFormatter(formatter)

log.addHandler(hdlr)
log.setLevel(logging.INFO)
