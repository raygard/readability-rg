#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Modelled on setup.py from Hynek Schlawack's attrs package.


from __future__ import division, print_function, unicode_literals

import codecs
import os
import re

from setuptools import find_packages, setup


###############################################################################


# PyPI package name:
NAME = 'readability_rg'
PACKAGES = find_packages(where='src')
META_PATH = os.path.join('src', 'readability', '__init__.py')
KEYWORDS = ['readability', 'Flesch', 'Flesch-Kincaid']
CLASSIFIERS = [

    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',

    'Topic :: Education',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Linguistic',

]

###############################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string.'.format(meta=meta))


VERSION = find_meta('version')
URI = find_meta('uri')
LONG = (
    read('README.rst') + '\n\n' +
    'Release Information\n' +
    '===================\n\n' +
    re.search('(\d+.\d.\d \(.*?\)\n.*?)\n\n\n----\n\n\n',
              read('CHANGELOG.rst'), re.S).group(1) +
    '\n\n' +
#    '`Full changelog ' +
#    '<{uri}en/stable/changelog.html>`_.\n\n'.format(uri=URI) +
    read('AUTHORS.rst')
)


if __name__ == '__main__':
    setup(
        name=NAME,
        description=find_meta('description'),
        license=find_meta('license'),
##<<<          url=find_meta('uri'),
##<<<          version=find_meta('version'),
        url=URI,
        version=VERSION,
        author=find_meta('author'),
        author_email=find_meta('email'),
        maintainer=find_meta('author'),
        maintainer_email=find_meta('email'),
        keywords=KEYWORDS,
##<<<          long_description=read('README.rst'),
        long_description=LONG,
        packages=PACKAGES,
        package_dir={'': 'src'},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        #install_requires=INSTALL_REQUIRES,
    )
