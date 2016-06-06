#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Soapfish is a SOAP library for Python capable of generating Python modules from
WSDL documents and providing a dispatcher for the Django framework.
'''

import re
import sys

from setuptools import setup, find_packages

import soapfish

if (3, 0) <= sys.version_info < (3, 3):
    sys.stderr.write('soapfish requires at Python 3.3 (or later)')
    sys.exit(1)

def requires_from_file(filename):
    requirements = []
    with open(filename, 'r') as requirements_fp:
        for line in requirements_fp.readlines():
            match = re.search('^\s*([a-zA-Z][^#]+?)(\s*#.+)?\n$', line)
            if match:
                requirements.append(match.group(1))
    return requirements

setup(
    name='soapfish',
    version=soapfish.__version__,
    author=soapfish.__author__,
    author_email=soapfish.__email__,
    url='https://github.com/vpistis/soapfish',
    description='A SOAP library for Python',
    long_description=open('README.md').read() + open('CHANGES.txt').read() + open('TODO.txt').read(),
    download_url='',
    license='New BSD License',
    packages=find_packages(exclude=("examples", "tests",)),
    include_package_data=True,
    install_requires=requires_from_file('requirements.txt'),
    tests_require=requires_from_file('dev_requirements.txt'),
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'py2wsdl=soapfish.py2wsdl:main',
            'py2xsd=soapfish.py2xsd:main',
            'wsdl2py=soapfish.wsdl2py:main',
            'xsd2py=soapfish.xsd2py:main',
        ],
    },
    platforms=['OS Independent'],
    keywords=['SOAP', 'WSDL', 'web service'],
    classifiers=[
        'Development Status :: 5 - RC',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
