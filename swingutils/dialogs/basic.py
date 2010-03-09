"""
Contains convenient shortcuts to JOptionPane methods that show different kinds
of dialogs. You can override the default error/warning dialog titles if your
application's language is not English.

"""
from javax.swing import JOptionPane


defaultErrorTitle = u'Error'
defaultWarningTitle = u'Warning'

def showErrorDialog(error, title=None, parent=None):
    title = title if title is not None else defaultErrorTitle
    JOptionPane.showMessageDialog(parent, error, title,
                                  JOptionPane.ERROR_MESSAGE)


def showWarningDialog(message, title=None, parent=None):
    title = title if title is not None else defaultWarningTitle
    JOptionPane.showMessageDialog(parent, message, title,
                                  JOptionPane.WARNING_MESSAGE)


def showMessageDialog(message, title, parent=None):
    JOptionPane.showMessageDialog(parent, message, title,
                                  JOptionPane.INFORMATION_MESSAGE)
