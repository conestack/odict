# Copyright 2003-2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2 or later

from setuptools import setup, find_packages
import sys, os

version = '1.2'
shortdesc = 'Ordered dictionary.'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='odict',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: OS Independent',
            'Programming Language :: Python', 
            'Topic :: Software Development',       
      ],
      keywords='odict',
      author='bearophile, rnix',
      author_email='rnix@squarewave.at',
      url=u'https://svn.plone.org/svn/archetypes/AGX/odict',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=True,
      install_requires=['setuptools'],
      extras_require = {},
      )