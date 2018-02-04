#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

if sys.version_info.major == 2:
    install_requires = [
        "requests", 
        "pyyaml", 
        "web3",
        "pynacl",
        "bitcoin",
        'ethereum',
        "web3"
    ]
else:
    install_requires = [
        "requests", 
        "pyyaml",
        "pynacl",
        "gevent", 
        "uwsgi", 
        "ws4py", 
        "web3",
    ]


from setuptools import (
    setup,
    find_packages,
)

setup(
    name='xio',
    version='0.0.2',
    python_requires='>=2.7.*',
    description="""simple micro framework for microservices""",
    long_description=open('README.md').read(),
    author='Ludovic Jacquelin',
    author_email='ludovic.jacquelin@gmail.com',
    url='https://github.com/inxio/xio',
    include_package_data=True,
    install_requires= install_requires,
    py_modules=['xio'],
    #scripts=['xio/bin/xio'],
    license="MIT",
    zip_safe=False,
    keywords='microservices',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
