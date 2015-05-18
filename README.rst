Jython Swing Utilities
======================

A collection of utility classes and helper functions to make it easier to build
Swing user interfaces with Jython. The helpers provide "pythonic" alternatives
to often clumsy Java APIs.

Included in this package:

* enhanced table, list and combobox models
* JavaBeans support and automatic property change notification
* an alternative API for adding/removing event listeners
* a powerful data binding system that supports Swing components
* preferences access
* text field formatters
* shortcuts for loading resources (images or generic data) via class loaders
* shortcuts for basic dialogs
* enhanced file selection dialogs
* wrappers for loading `JFormDesigner`_ forms
* decorators and functions for safely accessing the GUI from any thread
* support for running background tasks in separate threads

Requires Jython 2.7 or later.

Documentation can be found at the Python Packaging
`documentation repository`_.

The `source code`_ and the `issue tracker`_ can be found at GitHub.


Building jar files
------------------

To build a jar file, you need to tell ant where to find jython.jar, by
defining the ``jythonjarpath`` property, either as a command line option
to ant, or in the ``build.properties`` file.

To build a jar file containing the Python source files::

    ant srcjar

To build a jar containing compiled bytecode files::

    ant binjar


Building signed jar files
-------------------------

Signing the jar files requires three additional properties to be defined:
``signer``, ``storepass`` and ``keypass``. It also requires that you have a
matching code signing key in your keystore (``~/.keystore``).


To build a signed source jar::

    ant signsrcjar

To build a signed, compiled jar (suitable for `Java Web Start`_)::
    
    ant signbinjar


.. _JFormDesigner: http://www.jformdesigner.com/
.. _source code: https://github.com/jython/swingutils
.. _issue tracker: https://github.com/jython/swingutils/issues
.. _documentation repository: http://packages.python.org/jython-swingutils/
.. _Java Web Start: http://docs.oracle.com/javase/tutorial/deployment/webstart/
