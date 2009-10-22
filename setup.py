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
