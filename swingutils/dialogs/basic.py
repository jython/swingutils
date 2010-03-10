"""
Contains convenient shortcuts to JOptionPane methods that show different kinds
of dialogs.

"""
from javax.swing import JOptionPane

__all__ = ('showErrorDialog', 'showWarningDialog', 'showMessageDialog')


def showErrorDialog(error, title=u'Error', parent=None):
    JOptionPane.showMessageDialog(parent, error, title,
                                  JOptionPane.ERROR_MESSAGE)


def showWarningDialog(message, title=u'Warning', parent=None):
    JOptionPane.showMessageDialog(parent, message, title,
                                  JOptionPane.WARNING_MESSAGE)


def showMessageDialog(message, title, parent=None):
    JOptionPane.showMessageDialog(parent, message, title,
                                  JOptionPane.INFORMATION_MESSAGE)
