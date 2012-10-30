from distutils.core import setup
setup(name='mexbtcapi',
      version='0.1',
      description="The Multi-Exchange Bitcoin API",
      author="Goncalo Pinheira",
      author_email="goncalopp@gmail.com",
      url='https://github.com/goncalopp/mexbtcapi',
      packages = ['mexbtcapi',
                  'mexbtcapi.util',
                  'mexbtcapi.concepts',
                  'mexbtcapi.api',
                  'mexbtcapi.api.mtgox',
                  'mexbtcapi.api.mtgox.http_v1',
                  'mexbtcapi.api.mtgox.streaming',
                 ]
      )
