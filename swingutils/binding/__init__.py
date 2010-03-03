"""
This module lets you automatically synchronize properties between two objects.

Some UI components require special handling to get them to behave as expected,
and this is provided by a collection of adapters. Adapters are used
automatically when a matching object is encountered.

"""
from StringIO import StringIO
import __builtin__
import logging

from swingutils.events import addPropertyListener
from swingutils.binding.parser import createChains


# Synchronization modes
MANUAL = 0
ONEWAY = 1
TWOWAY = 2


class BindingError(Exception):
    """Base class for all binding exceptions."""


class BindingWriteError(BindingError):
    """Raised when there is an error writing to a binding expression."""
    def __init__(self, message):
        BindingError.__init__(self, message)


class BindingReadError(BindingError):
    """Raised when there is an error reading from a binding expression."""
    def __init__(self, message):
        BindingError.__init__(self, message)


class LocalsProxy(object):
    def __init__(self, obj, builtins, options, **kwargs):
        self.obj = obj
        self.vars = {}
        if builtins:
            self.vars['__builtins__'] = __builtin__
        if 'vars' in options:
            self.vars.update(options['vars'])
        self.vars.update(kwargs)

    def __getitem__(self, key):
        if key in self.vars:
            return self.vars[key]

        try:
            return getattr(self.obj, key)
        except AttributeError:
            raise KeyError

    def __setitem__(self, key, value):
        setattr(self.obj, key, value)

    def __contains__(self, key):
        return hasattr(self.obj, key)


class BindingExpression(object):
    reader = None
    writer = None
    chains = None

    def __init__(self, root, source, options=None):
        self.root = root
        self.source = source
        self.options = options or {}
        self.globalsDict = LocalsProxy(root, True, self.options)
        self.localsDict = LocalsProxy(root, False, self.options)

    def getValue(self):
        if not self.reader:
            self.reader = compile(self.source, '$$binding-reader$$', 'eval')

        return eval(self.reader, self.globalsDict)

    def setValue(self, value):
        if not self.writer:
            self.writer = compile('%s=___binding_value' % self.source,
                                  '$$binding-writer$$', 'exec')

        globals_ = dict(__builtins__=__builtin__, ___binding_value=value)
        exec(self.writer, globals_, self.localsDict)

    def bind(self, callback):
        if self.chains is None:
            self.chains = createChains(self.source, callback, self.globalsDict,
                                       self.options)

        for chain in self.chains:
            chain.bind(self.root)

    def unbind(self):
        if self.chains:
            for chain in self.chains:
                chain.unbind()


class Binding(object):
    # Flag that prevents infinite loops
    _syncing = False

    def __init__(self, source, sourceExpression, target, targetExpression,
                 options):
        self.logger = options.get('logger')
        self.mode = options.get('mode')
        self.ignoreErrors = options.get('ignoreErrors')

        if isinstance(sourceExpression, BindingExpression):
            self.sourceExpression = sourceExpression
        else:
            self.sourceExpression = BindingExpression(source, sourceExpression,
                                                      options)
        if isinstance(targetExpression, BindingExpression):
            self.targetExpression = targetExpression
        else:
            self.targetExpression = BindingExpression(target, targetExpression,
                                                      options)

    def sourceChanged(self):
        self.logger.debug(u'Source (%s) changed', self.sourceExpression.source)
        self.sync(False)

    def targetChanged(self):
        self.logger.debug(u'Target (%s) changed', self.targetExpression.source)
        self.sync(True)

    def sync(self, reverse=False):
        if self._syncing:
            return
        
        if reverse:
            sourceExpression = self.targetExpression
            targetExpression = self.sourceExpression
            source = 'target'
            target = 'source'
        else:
            sourceExpression = self.sourceExpression
            targetExpression = self.targetExpression
            source = 'source'
            target = 'target'
            
        try:
            value = sourceExpression.getValue()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.logger.debug(u'Error reading from %s', source, exc_info=True)
            if not self.ignoreErrors:
                raise
            value = None

        self.logger.debug(u'Writing target value (%s) to source', repr(value))
        self._syncing = True
        try:
            targetExpression.setValue(value)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.logger.debug(u'Error writing to %s', target, exc_info=True)
            if not self.ignoreErrors:
                raise
        finally:
            self._syncing = False

    def bind(self):
        self.unbind()
        if self.mode >= ONEWAY:
            self.sourceExpression.bind(self.sourceChanged)
        if self.mode == TWOWAY:
            self.targetExpression.bind(self.targetChanged)

    def unbind(self):
        self.sourceExpression.unbind()
        self.targetExpression.unbind()


class BindingGroup(object):
    def __init__(self, **options):
        self.options = options
        self.options.setdefault('logger', logging.getLogger(__name__))
        self.options.setdefault('mode', ONEWAY)
        self.options.setdefault('ignoreErrors', True)
        self.bindings = []

    def bind(self, source, source_expr, target, target_expr, **options):
        """
        Binds the source object to the target object using binding expressions.

        :type source_expr: string or :class:`~BindingExpression`
        :type target_expr: string or :class:`~BindingExpression`
        :rtype: :class:`~Binding`

        """
        combined_opts = self.options.copy()
        combined_opts.update(options)
        b = Binding(source, source_expr, target, target_expr, combined_opts)
        self.bindings.append(b)
        b.bind()
        if b.mode != MANUAL:
            b.sync()
        return b

    def unbind(self):
        for b in self.bindings:
            b.unbind()
        del self.bindings[:]

    def sync(self, reverse=False):
        for b in self.bindings:
            b.sync(reverse)
