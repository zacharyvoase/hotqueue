#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from distutils.core import setup


rel_file = lambda *args: os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

def read_from(filename):
    fp = open(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def get_version():
    data = read_from(rel_file('hotqueue', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", data).group(1)

def get_long_description():
    return read_from(rel_file('README.rst'))


setup(
    name             = 'hotqueue',
    license          = 'MIT',
    version          = get_version(),
    author           = 'Richard Henry',
    author_email     = 'richardhenry@me.com',
    url              = 'http://github.com/richardhenry/hotqueue',
    description      = 'HotQueue is a Python library that allows you to use `Redis as a message queue within your Python programs.',
    long_description = get_long_description(),
    packages         = ['hotqueue'],
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

