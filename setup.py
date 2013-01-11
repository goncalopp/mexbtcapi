from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='mexbtcapi',
      version='0.1',
      description="The Multi-Exchange Bitcoin API",
      long_description=read('README'),
      author="Goncalo Pinheira",
      author_email="goncalopp+pypi@quorumverita.com",
      url='https://github.com/goncalopp/mexbtcapi',
      license='CC0',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      classifiers=[
              'Development Status :: 2 - Pre-Alpha',
              'Intended Audience :: Developers',
              'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Topic :: Software Development :: Libraries',
               ],

)
