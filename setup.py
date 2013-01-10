from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README')

setup(name='mexbtcapi',
      version='0.1',
      description="The Multi-Exchange Bitcoin API",
      long_description = README,
      author="Goncalo Pinheira",
      author_email="goncalopp+pypi@quorumverita.com",
      url='https://github.com/goncalopp/mexbtcapi',
      packages = ['mexbtcapi',
                  'mexbtcapi.util',
                  'mexbtcapi.concepts',
                  'mexbtcapi.api',
                  'mexbtcapi.api.mtgox',
                  'mexbtcapi.api.mtgox.http_v1',
                  'mexbtcapi.api.mtgox.streaming',
                 ],
      classifiers = \
              [
              'Development Status :: 2 - Pre-Alpha',
              'Intended Audience :: Developers',
              'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Topic :: Software Development :: Libraries',
               ]
      )
