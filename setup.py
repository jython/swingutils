# coding: utf-8
import sys

try:
    from distribute.core import setup, find_packages
except ImportError:
    from setuptools import setup, find_packages

if not 'java' in sys.platform.lower():
    raise Exception('This package can only be installed on Jython.')

setup(
    name='jython-swingutils',
    version='0.1',
    description="Makes using Java's Swing UI toolkit easy on Jython",
    long_description="""\
A collection of utility classes and helper functions to make it easier to build
Swing user interfaces with Jython. The helpers provide "pythonic" alternatives
to often clumsy Java interfaces.

Included in this package:
 * enhanced table and list models
 * JavaBean support
 * enhanced file chooser
 * shortcuts for common dialogs
 * wrappers for loading `JFormDesigner <http://www.jformdesigner.com/>`_ forms
 * decorators and functions for invoking Swing code from other threads
 
More will follow as the project progresses.

There are no releases yet, but you can check out the code from
`BitBucket <http://bitbucket.org/agronholm/jython-swingutils/>`_.
""",
    author='Alex Gronholm',
    author_email='swingutils@nextday.fi',
    url='http://pypi.python.org/jython-swingutils/',
    classifiers=[
      'Development Status :: 2 - Pre-Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.5',
      'Programming Language :: Java',
    ],
    keywords='jython swing',
    license='MIT',
    packages=find_packages(),
)
