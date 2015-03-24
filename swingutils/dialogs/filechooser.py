"""
Contains helpers for JFileChooser related functionality.

"""
from java.io import File
from javax.swing import JFileChooser
from javax.swing.filechooser import FileFilter

__all__ = ('SimpleFileFilter', 'createFileChooserDialog', 'showOpenDialog',
           'showSaveDialog')


class SimpleFileFilter(FileFilter):
    """
    A simple FileFilter class, suitable for use with the :func:`showSaveDialog`
    function, and of course Java's :class:`JFileChooser` class.

    """
    def __init__(self, suffixes, preferred=None, description=None):
        """
        :param suffixes: one or more file name extensions to accept
        :param preferred: suffix that may be used for automatically filling
                          a missing extension from a file name and building
                          the description string if none was defined
        :param description: textual description of the file filter

        """
        if isinstance(suffixes, basestring):
            self.suffixes = [suffixes]
        else:
            self.suffixes = list(suffixes)

        if preferred and preferred not in self.suffixes:
            self.suffixes.append(preferred)
        self.preferred = preferred or self.suffixes[0]

        # Add the . in the front
        for i in xrange(0, len(self.suffixes)):
            if not self.suffixes[i].startswith(u'.'):
                self.suffixes[i] = u'.%s' % self.suffixes[i]
        if not self.preferred.startswith(u'.'):
            self.preferred = u'.%s' % self.preferred

        self._description = (description or u'%s files' %
                             self.preferred[1:].upper())

    #
    # FileFilter methods
    #

    def accept(self, f):
        if f.isDirectory():
            return True

        fname = f.name.lower()
        for suffix in self.suffixes:
            if fname.endswith(suffix):
                return True

    def getDescription(self):
        return self._description


def createFileChooserDialog(filters, filename, prefs, prefkey, multiselect):
    """
    Creates a file chooser dialog that remembers its last directory.

    """
    fileChooser = JFileChooser()

    # Add filters
    if not hasattr(filters, '__iter__'):
        filters = (filters,)
    if filters:
        for filter in filters:
            fileChooser.addChoosableFileFilter(filter)
        fileChooser.fileFilter = filters[0]

    # Enable/disable multiple file select
    fileChooser.setMultiSelectionEnabled(multiselect)

    # Restore the last directory
    if prefs and prefkey:
        defaultDirName = prefs.get(prefkey, None)
        if defaultDirName:
            defaultDirectory = File(defaultDirName)
            if defaultDirectory.exists():
                fileChooser.currentDirectory = defaultDirectory

    # Preset the file name
    if filename:
        fileChooser.selectedFile = File(fileChooser.currentDirectory, filename)

    return fileChooser


def showOpenDialog(filters, filename=None, parent=None, prefs=None,
                   prefkey=None, multiselect=False):
    """
    Shows a save dialog that remembers the last directory based on the given
    preferences key. If the selected file filter has a 'suffix' attribute,
    it will be appended to the selected file name if it's missing.

    :param filters: a FileFilter (or several of them in an iterable)
    :param filename: default name for the new file
    :param parent: parent component to attach to
    :param prefs: a Preferences object to use for remembering the save
                  directory
    :param prefkey: key to use for saving/loading last save directory
    :param multiselect: `True` to allow multiple files to be selected
    :type filters: javax.swing.filechooser.FileFilter
    :type filename: str
    :type prefs: java.util.prefs.Preferences
    :type prefkey: str
    :return: list of selected files (if multiselect=True), else the selected
             file
    :rtype: java.io.File

    """
    fileChooser = createFileChooserDialog(filters, filename, prefs, prefkey,
                                          multiselect)

    if fileChooser.showOpenDialog(parent) != JFileChooser.APPROVE_OPTION:
        return () if multiselect else None

    # Save the current directory in preferences
    if prefs and prefkey:
        prefs.put(prefkey, fileChooser.currentDirectory.absolutePath)

    if multiselect:
        return fileChooser.selectedFiles
    return fileChooser.selectedFile


def showSaveDialog(filters, filename=None, parent=None, prefs=None,
                   prefkey=None):
    """
    Shows a save dialog that remembers the last directory based on the given
    preferences key. If the selected file filter has a 'suffix' attribute,
    it will be appended to the selected file names if it's missing.

    :param filters: a FileFilter (or several of them in an iterable)
    :param filename: default name for the new file
    :param parent: parent component to attach to
    :param prefs: a Preferences object to use for remembering the save
                  directory
    :param prefkey: key to use for saving/loading last save directory
    :type filters: javax.swing.filechooser.FileFilter
    :type filename: str
    :type prefs: java.util.prefs.Preferences
    :type prefkey: str
    :return: the selected file
    :rtype: java.io.File

    """
    fileChooser = createFileChooserDialog(filters, filename, prefs, prefkey,
                                          False)

    if fileChooser.showSaveDialog(parent) != JFileChooser.APPROVE_OPTION:
        return None

    # Save the current directory in preferences
    if prefs and prefkey:
        prefs.put(prefkey, fileChooser.currentDirectory.absolutePath)

    # Insert the suffix from the file filter if it's missing from the file name
    selectedFile = fileChooser.selectedFile
    filter = fileChooser.fileFilter
    if selectedFile and hasattr(filter, 'preferred') and not \
            selectedFile.name.lower().endswith(filter.preferred):
        selectedFile = File(selectedFile.path + filter.preferred)

    return selectedFile
