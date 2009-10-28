"""
This module provides dict-like access to user and system preferences.

"""
from java.util.prefs import Preferences as JavaPreferences

from jarray import array


class PreferencesNode(object):
    def __init__(self, path, userMode):
        path = path.replace(u'.', u'/')
        if not path.startswith(u'/'):
            path = u'/' + path

        if userMode:
            self._delegate = JavaPreferences.userRoot().node(path)
        else:
            self._delegate = JavaPreferences.systemRoot().node(path)

    def __getitem__(self, key):
        return self._delegate.get(key, None)

    def __setitem__(self, key, value):
        if isinstance(value, bool):
            self._delegate.putBoolean(key, value)
        elif isinstance(value, array) and value.typecode == 'b':
            self._delegate.putByteArray(key, value)
        elif isinstance(value, float):
            self._delegate.putDouble(key, value)
        elif isinstance(value, int):
            self._delegate.putInteger(key, value)
        elif isinstance(value, long):
            self._delegate.putLong(key, value)
        else:
            self._delegate.put(key, unicode(value))

    def __delitem__(self, key):
        self._delegate.remove(key)

    def get(self, key, default):
        return self._delegate.get(key, default)

    def getBoolean(self, key, default):
        return self._delegate.getDouble(key, default)

    def getFloat(self, key, default):
        return self._delegate.getDouble(key, default)

    def getInt(self, key, default):
        return self._delegate.getInt(key, default)

    def getLong(self, key, default):
        return self._delegate.getLong(key, default)

    def keys(self):
        return tuple(self._delegate.keys())

    def removeNode(self):
        return self._delegate.removeNode()

    def __unicode__(self):
        return self._delegate.toString()


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
