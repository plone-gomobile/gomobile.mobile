from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='gomobile.mobile',
      version=version,
      description="GoMobile is a Plone add-on product to turn Plone to converged web and mobile content management system",
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
      keywords='mobile sniffer cms',
      author='GoMobile community',
      author_email='mikko.ohtamaa@twinapex.com',
      url='http://www.twinapex.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gomobile'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
