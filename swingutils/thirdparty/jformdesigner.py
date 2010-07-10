"""
This module facilitates using forms created with
`JFormDesigner <http://www.jformdesigner.com/>`_. It requires that you have the
JFormDesigner form loader library (jfd-loader.jar) in your class path.

"""

try:
    from com.jformdesigner.runtime import FormLoader, FormCreator
except ImportError:
    raise ImportError('JFormDesigner runtime library not found. '
                      'Make sure you have jfd-loader.jar on your CLASSPATH.')

__all__ = ('FormWrapper', 'PanelWrapper', 'WindowWrapper')


class _CreatorWrapper(FormCreator):
    def __getattr__(self, key):
        return self.getComponent(key)


class FormWrapper(object):
    """
    Acts as a proxy to a JFormDesigner form.
    When you load a form into it, you can access any named component as an
    attribute of this class (provided that said class does not have any
    attributes of its own that would shadow the component names).
    
    It is recommended that users don't use this class directly, but rather
    subclass one of its descendants (PanelWrapper, WindowWrapper etc).

    """

    c = None

    def loadform(self, formName=None):
        """
        Loads a .jfd form with the given name.
        If the full path is not given explicitly, then it is derived from the
        module path of the current class (``self``).

        :param formName: a complete file path, or just the form filename,
                         or just the form name without the .jfd suffix

        """
        if formName is None or not '/' in formName:
            modulePath = self.__class__.__module__.split('.')[:-1]
            modulePath = '/'.join(modulePath)
            fileName = formName if formName else self.__class__.__name__
            if not fileName.lower().endswith('.jfd'):
                fileName += '.jfd'
            if modulePath:
                formName = '%s/%s' % (modulePath, fileName)
            else:
                formName = fileName

        formModel = FormLoader.load(formName)
        self.c = _CreatorWrapper(formModel)
        self.c.target = self


class PanelWrapper(FormWrapper):
    """
    Wraps a form that has a JPanel as its root element.
    Attributes of that panel can be accessed as the attributes of this class.

    See the documentation for the :class:`~FormWrapper` class for more
    information.

    """
    def __init__(self, formName=None):
        self.loadform(formName)
        self._panel = self.c.createPanel()

    @property
    def panel(self):
        return self._panel


class WindowWrapper(FormWrapper):
    """
    Wraps a form that has a Window (or any of its descendants) as its root
    element. Attributes of that window can be accessed as the attributes of
    this class.

    See the documentation for the :class:`~FormWrapper` class for more
    information.

    """

    def __init__(self, formName=None, owner=None):
        """
        :param owner: owner (parent) of the created window

        """
        self.loadform(formName)
        self._window = self.c.createWindow(owner)

    @property
    def window(self):
        return self._window
