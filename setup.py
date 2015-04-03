import sys

from setuptools import setup, find_packages

if 'java' not in sys.platform.lower():
    raise Exception('This package can only be installed on Jython.')

long_description = open('README.rst').read()

setup(
    name='jython-swingutils',
    version='2.0.0',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: Jython',
        'Topic :: Software Development :: User Interfaces'
    ],
    install_requires=['futures >= 2.2.0'],
    keywords='jython swing',
    license='MIT',
    packages=find_packages(exclude=['test'])
)
