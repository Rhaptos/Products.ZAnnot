from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='Products.ZAnnot',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rhaptos team',
      author_email='rhaptos@cnx.org',
      url='http://rhaptos.org',
      license='',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      tests_require = [
           'zope.testing>=3.5',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

