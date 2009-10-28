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

__all__ = ('FormCreatorWrapper', 'PanelWrapper', 'WindowWrapper')


class FormWrapper(object):
    """
    Acts as a proxy to a JFormDesigner form.
    When you load a form into it, you can access any named component as an
    attribute of this class (provided that said class does not have any
    attributes of its own that would shadow the component names).
    
    It is recommended that users don't use this class directly, but rather
    subclass one of its descendants (PanelWrapper, WindowWrapper etc).

    """

    _creator = None

    def __getattr__(self, key):
        if not self._creator:
            raise Exception('No form has been loaded yet')
        return self._creator.getComponent(key)

    def loadform(self, formName=None):
        """
        Loads a .jfd form with the given name.
        If the full path is not given explicitly, then it is derived from the
        module path of the current class (``self``).

        :param formName: a complete file path, or just the form filename,
                         or just the form name without the .jfd suffix

        """
        if formName is None or not '/' in formName:
            modulepath = self.__class__.__module__.split('.')[:-1]
            modulepath = '/'.join(modulepath)
            filename = formName if formName else self.__class__.__name__
            if not filename.lower().endswith('.jfd'):
                filename += '.jfd'
            formName = '%s/%s' % (modulepath, filename)
        formModel = FormLoader.load(formName)
        self._creator = FormCreator(formModel)
        self._creator.target = self


class _DelegateWrapper(FormWrapper):
    _delegate = None

    def __getattr__(self, key):
        if hasattr(self._delegate, key):
            return getattr(self._delegate, key)
        return FormWrapper.__getattr__(self, key)

    def __setattr__(self, key, value):
        if self._delegate and hasattr(self._delegate, key):
            setattr(self._delegate, key, value)
        else:
            object.__setattr__(key, value)


class PanelWrapper(_DelegateWrapper):
    """
    Wraps a form that has a JPanel as its root element.
    Attributes of that panel can be accessed as the attributes of this class.

    See the documentation for the :class:`~FormWrapper` class for more
    information.

    """
    def __init__(self, formName=None):
        self.loadform(formName)
        self._delegate = self._creator.createPanel()


class WindowWrapper(_DelegateWrapper):
    """
    Wraps a form that has a Window (or any of its descendants) as its root
    element. Attributes of that panel can be accessed as the attributes of this
    class.

    See the documentation for the :class:`~FormWrapper` class for more
    information.

    """

    def __init__(self, formName=None, owner=None):
        """
        :param owner: owner (parent) of the created window

        """
        self.loadform(formName)
        self._delegate = self._creator.createWindow(owner)
