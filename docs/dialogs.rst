Dialogs
=======

Jython-Swingutils provides a friendlier interface for displaying some common
dialogs.

Basic dialogs
-------------

The :mod:`swingutils.dialogs.basic` module offers a slightly more convenient
api for showing some basic dialogs::

    from swingutils.dialogs.basic import showErrorDialog, showWarningDialog, showMessageDialog
    
    showErrorDialog('Something terrible has happened!')

    showWarningDialog('This could be bad...!')
    
    showMessageDialog('Hello there', 'Random message')

If your application's language is not English, and you wish to override the
default titles, you can do this::

    from functools import partial
    
    showErrorDialog = partial(showErrorDialog, title='Fehler')

File chooser dialogs
--------------------

The file chooser dialogs provide you with the following enhancements over the
standard Java ones:

* Dialogs remember the last directory a file was saved to / opened from
* Save dialogs automatically fill in the file suffix if it's missing
* Easy file filters, without having to create your own
  :class:`~javax.swing.filechooser.FileFilter` subclasses

Examples::

    from swingutils.preferences import getUserPrefs
    from swingutils.dialogs.filechooser import showOpenDialog, showSaveDialog, SimpleFileFilter
    
    prefs = getUserPrefs('/some/example/app')
    txtFilter = SimpleFileFilter('.txt', None, 'Text files')
    files = showOpenDialog(txtFilter, prefs=prefs, prefkey='loadedFiles', multiselect=True)
    
    file = showSaveDialog(txtFilter, prefs=prefs, prefkey='savedFiles')
    