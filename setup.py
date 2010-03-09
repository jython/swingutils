# coding: utf-8
from distutils.core import setup
import sys

if not 'java' in sys.platform.lower():
    raise Exception('This package can only be installed on Jython.')

setup(
    name='jython-swingutils',
    version='0.2',
    description="Makes using Java's Swing UI toolkit easy on Jython",
    long_description="""\
A collection of utility classes and helper functions to make it easier to build
Swing user interfaces with Jython. The helpers provide "pythonic" alternatives
to often clumsy Java APIs.

Included in this package:
 * enhanced table, list and combobox models
 * JavaBeans support and automatic property change notification
 * an alternative API for adding/removing event listeners
 * property binding
 * enhanced file chooser
 * preferences access
 * text field formatters
 * shortcuts for common dialogs
 * wrappers for loading `JFormDesigner <http://www.jformdesigner.com/>`_ forms
 * decorators and functions for safely accessing the GUI from any thread
 * support for running background tasks in separate threads

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
    packages=[
        'swingutils',
        'swingutils.binding',
        'swingutils.binding.adapters',
        'swingutils.models',
        'swingutils.thirdparty'
    ],
)
