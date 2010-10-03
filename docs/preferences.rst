Preferences
===========

Java offers a `preferences system
<http://download.oracle.com/javase/1.5.0/docs/guide/preferences/index.html>`_
that allows storing system-wide and per-user preferences. You can store
simple numeric or textual values in each preferences node as key-value pairs.
Jython-Swingutils provides a more pythonic interface to this functionality.

To access preferences, you need to get a
:class:`~swingutils.preferences.PreferencesNode` by calling either
:func:`~swingutils.preferences.getSystemPrefs` or
:func:`~swingutils.preferences.getUserPrefs`::

    from swingutils.preferences import getUserPrefs

    prefs = getUserPrefs('/my/demo/app')
    prefs['username'] = 'Someone'

Dict-like access only works with string values. To store or retrieve numeric
values, you need to use the `get` and `put` methods and provide a default
value when retrieving values::

    width = prefs.get('windowWidth', 800)
    prefs.put('windowWidth', 1000)


Preferences adapters
--------------------

When combined with :doc:`Binding <binding>`, the preferences system is really
easy to use for making applications remember things like window position or
size. Preferences adapters are objects that are bound to a specific key on a
specific preferences node with a set default value, making them easy to bind
to::

    from swingutils.preferences import getUserPrefs, PreferencesAdapter
    from swingutils.bindings import BindingGroup, TWOWAY

    prefs = getUserPrefs('/my/demo/app')
    adapter = PreferencesAdapter(prefs, 'windowWidth', 400)
    group = BindingGroup()
    group.bind(adapter, 'value', window, 'width')
