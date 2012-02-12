Python-MtGox
============

This is an interface to MtGox's API version 1

Depends on simplejson :
  http://undefined.org/python/#simplejson http://pypi.python.org/pypi/simplejson


## INSTALL

$ python setup.py install


## EXAMPLE

import mtgox


mtgox.ticker("USD")

account = mtgox.Private(key, secret)

account.info()
