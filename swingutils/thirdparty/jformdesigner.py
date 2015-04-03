"""
This module facilitates using forms created with
`JFormDesigner <http://www.jformdesigner.com/>`_. It requires that you have the
JFormDesigner form loader library (jfd-loader.jar) in your class path.

"""
from __future__ import unicode_literals

from java.lang import Exception as JavaException
from java.lang.reflect import InvocationHandler

try:
    from com.jformdesigner.runtime import FormLoader, FormCreator, \
        NoSuchComponentException
except ImportError:
    raise ImportError('JFormDesigner runtime library not found. '
                      'Make sure you have jfd-loader.jar on your CLASSPATH.')

__all__ = ('FormLoadException', 'FormWrapper', 'PanelWrapper', 'WindowWrapper')


class FormLoadException(Exception):
    """Raised when the specified form could not be loaded."""

    def __init__(self, formname, e):
        self.formname = formname
        self.parent = e

    def __unicode__(self):
        return 'Unable to load form %s: %s' % (self.formname, self.parent)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class JythonInvocationHandler(InvocationHandler):
    def __init__(self, method):
        self.method = method

    def invoke(self, proxy, method, args):
        return self.method(*args)


class JythonFormCreator(FormCreator):
    def newEventInvocationHandler(self, listenerMethod, handlerMethod,
                                  paramTypes):
        method = self.target
        for part in handlerMethod.split('.'):
            method = getattr(method, part, None)
        return JythonInvocationHandler(method)


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
        if self._creator:
            try:
                return self._creator.getBean(key)
            except NoSuchComponentException:
                pass
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (type(self), key))

    def loadform(self, formName=None, createAll=True):
        """
        Loads a .jfd form with the given name.
        If the full path is not given explicitly, then it is derived from the
        module path of the current class (``self``).

        :param formName: a complete file path, or just the form filename,
                         or just the form name without the .jfd suffix
        :param createAll: True to create all components so that they are
                          immediately accessible after this call returns

        """
        if formName is None or '/' not in formName:
            modulePath = self.__class__.__module__.split('.')[:-1]
            modulePath = '/'.join(modulePath)
            fileName = formName if formName else self.__class__.__name__
            if not fileName.lower().endswith('.jfd'):
                fileName += '.jfd'
            if modulePath:
                formName = '%s/%s' % (modulePath, fileName)
            else:
                formName = fileName

        try:
            formModel = FormLoader.load(formName)
        except JavaException, e:
            raise FormLoadException(formName, e)

        self._creator = JythonFormCreator(formModel)
        self._creator.target = self
        if createAll:
            self._creator.createAll()


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
            object.__setattr__(self, key, value)


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

    @property
    def panel(self):
        return self._delegate


class WindowWrapper(_DelegateWrapper):
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
        self.loadform(formName, False)
        self._delegate = self._creator.createWindow(owner)
        self._creator.createAll()

    @property
    def window(self):
        return self._delegate
