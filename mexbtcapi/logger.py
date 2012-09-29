import sys
import logging
log= logging.getLogger('mexbtcapi')
formatter = logging.Formatter('MEXBTCAPI: %(message)s')
hdlr = logging.StreamHandler( sys.stdout )
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 
log.setLevel(logging.INFO)
