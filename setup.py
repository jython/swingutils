# coding: utf-8
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if not 'java' in sys.platform.lower():
    raise Exception('This package can only be installed on Jython.')

long_description = open('README.rst').read()

setup(
    name='jython-swingutils',
    version='1.0',
    description="Makes using Java's Swing UI toolkit easy on Jython",
    long_description=long_description,
    author='Alex Gronholm',
    author_email='alex.gronholm+pypi@nextday.fi',
    url='http://pypi.python.org/jython-swingutils/',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.5',
      'Programming Language :: Java',
      'Topic :: Software Development :: User Interfaces'
    ],
    keywords='jython swing',
    license='MIT',
    packages=[
        'swingutils',
        'swingutils.binding',
        'swingutils.binding.adapters',
        'swingutils.dialogs',
        'swingutils.models',
        'swingutils.thirdparty',
        'swingutils.threads'
    ],
)
