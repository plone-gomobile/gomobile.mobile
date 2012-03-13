from setuptools import setup, find_packages
import os

version = '1.0.4'

setup(name='gomobile.mobile',
      version=version,
      description="Core package for mobilizing Plone CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        ],
      keywords='mobile sniffer cms WAP plone',
      author='mFabrik Reseacrh Oy',
      author_email='research@mfabrik.com',
      url='http://webandmobile.mfabrik.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gomobile'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.AdvancedQuery',
          'plone.behavior',
          'plone.directives.form',
          'zope.schema',
          'zope.interface',
          'zope.component',
          'plone.postpublicationhook',
          'plone.app.z3cform',
          'httplib2',
          'uuid',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
