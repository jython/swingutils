"""
This module provides helper classes and functions for accessing Java's
Preferences system.

"""
from __future__ import unicode_literals
from types import NoneType
from array import array

from java.util.prefs import Preferences as JavaPreferences
from java.lang import Integer, Long, Float, Double, Boolean, String


class PreferencesNode(object):
    """
    Provides a pythonic interface (including dict-like access) to the
    preferences node at the given path. The preferred method of obtaining these
    is via :func:`getUserPrefs` or :func:`getSystemPrefs`.

    """
    def __init__(self, path, userMode):
        path = path.replace('.', '/')
        if not path.startswith('/'):
            path = '/' + path

        if userMode:
            self._delegate = JavaPreferences.userRoot().node(path)
        else:
            self._delegate = JavaPreferences.systemRoot().node(path)

    def __getitem__(self, key):
        return self.get(key, None)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        self._delegate.remove(key)

    def __contains__(self, key):
        return key in self._delegate.keys()

    def get(self, key, default):
        if isinstance(default, (bool, Boolean)):
            return self._delegate.getBoolean(key, default)
        elif isinstance(default, array) and default.typecode == 'b':
            return self._delegate.getByteArray(key, default)
        elif isinstance(default, Float):
            return self._delegate.getFloat(key, default)
        elif isinstance(default, (float, Double)):
            return self._delegate.getDouble(key, default)
        elif isinstance(default, Integer):
            return self._delegate.getInt(key, default)
        elif isinstance(default, (int, long, Long)):
            return self._delegate.getLong(key, default)
        elif isinstance(default, (str, unicode, String, NoneType)):
            return self._delegate.get(key, default)
        else:
            raise ValueError('Unsupported default type %s' % type(default))

    def put(self, key, value):
        if isinstance(value, (bool, Boolean)):
            self._delegate.putBoolean(key, value)
        elif isinstance(value, array) and value.typecode == 'b':
            self._delegate.putByteArray(key, value)
        elif isinstance(value, Float):
            self._delegate.putFloat(key, value)
        elif isinstance(value, (float, Double)):
            self._delegate.putDouble(key, value)
        elif isinstance(value, Integer):
            self._delegate.putInt(key, value)
        elif isinstance(value, (int, long, Long)):
            self._delegate.putLong(key, value)
        elif isinstance(value, (str, unicode, String)):
            self._delegate.put(key, value)
        else:
            raise ValueError('Unsupported value type %s' % type(value))

    def keys(self):
        return tuple(self._delegate.keys())

    def removeNode(self):
        return self._delegate.removeNode()

    def remove(self, key):
        self._delegate.remove(key)

    def __unicode__(self):
        return self._delegate.toString()


class PreferencesAdapter(object):
    """
    Represents the value of the given key in the given preferences node.
    The ``value`` attribute can be read, written to and deleted, which causes
    the appropriate action to be taken with the associated preferences node.

    :param node: a preferences node, obtained through :func:`getUserPrefs` or
                 :func:`getSystemPrefs`
    :type node: :class:`PreferencesNode`
    :param key: name of the preference within the node
    :type key: str
    :param default: Default value to return when the key does not exist

    """
    def __init__(self, node, key, default):
        if node is None:
            raise ValueError('The node must not be None')
        if key is None:
            raise ValueError('The key must not be None')

        self.node = node
        self.key = key
        self.default = default

    @property
    def value(self):
        return self.node.get(self.key, self.default)

    @value.setter
    def value(self, value):
        self.node.put(self.key, value)

    @value.deleter
    def value(self):
        self.node.remove(self.key)


def getUserPrefs(path):
    """
    Returns a preferences node from current user's preferences for the given
    path.

    :param path: path to a preferences node (existing or not)
    :return: a dict-like preferences node
    :rtype: :class:`PreferencesNode`

    """
    return PreferencesNode(path, True)


def getSystemPrefs(path):
    """
    Returns a preferences node from system-wide preferences for the given path.

    :param path: path to a preferences node (existing or not)
    :return: a dict-like preferences node
    :rtype: :class:`PreferencesNode`

    """
    return PreferencesNode(path, False)
