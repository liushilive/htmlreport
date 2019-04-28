#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

if sys.version_info < (3, 7):
    print(u"The minimum support Python 3.7\n支持最低版本 3.7")
    exit(1)

from setuptools import find_packages
from setuptools import setup

from HTMLReport import __version__, __author__


setup(
    name='HTMLReport',
    version=__version__,
    description="Python3 Unittest HTML报告生成器",
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author=__author__,
    author_email='liushilive@outlook.com',
    url='http://liushilive.github.io',
    project_urls={
        'The report template': 'https://liushilive.github.io/report/report/#en',
        '报告样板': 'https://liushilive.github.io/report/report/#cn'
    },
    packages=find_packages(),
    package_dir={'HTMLReport': 'HTMLReport'},
    include_package_data=True,
    license="Apache 2.0",
    zip_safe=False,
    keywords='HtmlTestRunner test runner html reports unittest',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Testing :: Unit',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    test_suite='tests'
)
