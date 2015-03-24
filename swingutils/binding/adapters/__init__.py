"""
This package houses binding adapters. A binding adapter is a helper object
that knows how to add event listeners to a particular target class (and remove
them). The registry is a central repository for the adapters, and vends adapter
instances when given a target object.

"""


class AdapterRegistry(object):
    defaultPropertyAdapter = None
    defaultListAdapter = None

    def __init__(self):
        self.propertyAdapters = {}
        self.listAdapters = {}

    def _getClassNames(self, cls, names=None, level=0):
        """Retrieves the class name of `cls` and names of its superclasses."""

        if names is None:
            names = []
        clsname = u'%s.%s' % (cls.__module__, cls.__name__)

        # Skip proxy classes
        if u'$' not in clsname:
            names.append(clsname)
        for basecls in cls.__bases__:
            self._getClassNames(basecls, names, level + 1)
        return names

    def registerDefaultPropertyAdapter(self, cls):
        self.defaultPropertyAdapter = cls
        return cls

    def registerDefaultListAdapter(self, cls):
        self.defaultListAdapter = cls
        return cls

    def registerPropertyAdapter(self, cls):
        classNames = cls.__targetclass__
        if isinstance(cls.__targetclass__, basestring):
            classNames = (cls.__targetclass__,)

        properties = cls.__targetproperty__
        if isinstance(cls.__targetproperty__, basestring):
            properties = (cls.__targetproperty__,)

        for className in classNames:
            for property in properties:
                key = (className, property)
                self.propertyAdapters[key] = cls

        return cls

    def registerListAdapter(self, cls):
        key = cls.__targetclass__
        self.listAdapters[key] = cls
        return cls

    def getPropertyAdapter(self, obj, options, property):
        # Gather a list of class names from the inheritance chain
        targetClassNames = self._getClassNames(obj.__class__)
        targetClassNames.sort()

        # Find the nearest matching adapter for this class
        adapterClass = self.defaultPropertyAdapter
        for className in targetClassNames:
            key = (className, property)
            if key in self.propertyAdapters:
                adapterClass = self.propertyAdapters[key]
                break

        if adapterClass:
            return adapterClass(options, property)

    def getListAdapter(self, obj, options):
        # Gather a list of class names from the inheritance chain
        targetClassNames = self._getClassNames(obj.__class__)
        targetClassNames.sort()

        # Find the nearest matching adapter for this class
        adapterClass = self.defaultListAdapter
        for className in targetClassNames:
            if className in self.listAdapters:
                adapterClass = self.listAdapters[className]
                break

        if adapterClass:
            return adapterClass(options)

    def dumpAdapters(self):
        """Prints a list of all registered adapters to standard output."""

        print 'Registered property adapters:'
        for key in sorted(self.propertyAdapters.keys()):
            adapter = self.propertyAdapters[key]
            print '* %s (class=%s property=%s)' % (adapter.__name__, key[0],
                                                   key[1])

        print
        print 'Registered list adapters:'
        for key in sorted(self.listAdapters.keys()):
            adapter = self.listAdapters[key]
            print '* %s (class=%s)' % (adapter, key)

registry = AdapterRegistry()


class BindingAdapter(object):
    """A generic base class for binding adapters."""

    __slots__ = ('listeners')

    def __init__(self, options):
        self.listeners = {}

    def addListeners(self, parent, callback, *args, **kwargs):
        pass

    def removeListeners(self, *names):
        if not names:
            names = self.listeners.keys()

        for name in names:
            l = self.listeners.pop(name)
            if l:
                l.unlisten()
