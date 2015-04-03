"""
This module lets you automatically synchronize properties between two objects.

Some UI components require special handling to get them to behave as expected,
and this is provided by a collection of adapters. Adapters are used
automatically when a matching object is encountered.

"""
from __future__ import unicode_literals
import __builtin__
import sys

from swingutils.binding.parser import createChains
from swingutils.binding.adapters import swing  # flake8: noqa

# Synchronization modes
MANUAL = 0
ONEWAY = 1
TWOWAY = 2


class _LocalsProxy(object):
    def __init__(self, obj, options):
        self.obj = obj
        self.vars = options['vars'].copy() if 'vars' in options else {}

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

    def __init__(self, root, source, **options):
        self.root = root
        self.source = source
        self.options = options
        self.globals = dict(__builtins__=__builtin__)
        self.locals = _LocalsProxy(root, self.options)

    def getValue(self):
        if not self.reader:
            self.reader = compile(self.source, '$$binding-reader$$', 'eval')

        return eval(self.reader, self.globals, self.locals)

    def setValue(self, value):
        if not self.writer:
            self.writer = compile('%s=___binding_value' % self.source,
                                  '$$binding-writer$$', 'exec')

        self.locals.vars['___binding_value'] = value
        try:
            exec(self.writer, self.globals, self.locals)
        finally:
            del self.locals.vars['___binding_value']

    def bind(self, callback):
        if self.chains is None:
            self.chains = createChains(self.source, callback, self.locals,
                                       self.options)

        for chain in self.chains:
            chain.bind(self.root)

    def unbind(self):
        if self.chains:
            for chain in self.chains:
                chain.unbind()

    def dump(self, indent=0, outfile=None):
        """
        Prints the list of binding chains in this expression to standard
        output or `outfile` if one was provided.

        """
        outfile = outfile or sys.stdout
        indentspace = u' ' * indent
        print >> outfile, u'%sSource code: %s' % (indentspace, self.source)
        if not self.chains:
            self.chains = createChains(self.source, None, self.locals,
                                       self.options)

        for i, chain in enumerate(self.chains):
            node = chain
            txts = []
            while node:
                txts.append(unicode(node))
                node = node.next
            print >> outfile, u'%sChain %d: %s' % (indentspace, i + 1,
                                                   u' -> '.join(txts))


class Binding(object):
    """
    Holds two expressions -- target and source, and manages synchronization
    between them.

    """

    # Flag that prevents infinite loops
    _syncing = False

    def __init__(self, source, sourceExpression, target, targetExpression,
                 **options):
        self.logger = options.get('logger')
        self.mode = options.get('mode')
        self.ignoreErrors = options.get('ignoreErrors')
        self.errorValue = options.get('errorValue')

        if isinstance(sourceExpression, BindingExpression):
            self.sourceExpression = sourceExpression
        else:
            self.sourceExpression = BindingExpression(source, sourceExpression,
                                                      **options)
        if isinstance(targetExpression, BindingExpression):
            self.targetExpression = targetExpression
        else:
            self.targetExpression = BindingExpression(target, targetExpression,
                                                      **options)

    def sourceChanged(self):
        if self.logger:
            self.logger.debug(u'Source (%s) changed',
                              self.sourceExpression.source)
        self.sync(False)

    def targetChanged(self):
        if self.logger:
            self.logger.debug(u'Target (%s) changed',
                              self.targetExpression.source)
        self.sync(True)

    def sync(self, reverse=False):
        """
        Evalutes the source expression and copies the result to the location
        pointed the target expression. Synchronizing in either direction will
        not trigger any further automatic synchronizations within the same
        binding.

        """
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
            if self.logger:
                self.logger.debug('Error reading from %s', source,
                                  exc_info=True)
            if not self.ignoreErrors:
                raise
            value = self.errorValue

        if self.logger:
            self.logger.debug('Writing %s value (%s) to %s', source,
                              repr(value), target)
        self._syncing = True
        try:
            targetExpression.setValue(value)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            if self.logger:
                self.logger.debug('Error writing to %s', target,
                                  exc_info=True)
            if not self.ignoreErrors:
                raise
        finally:
            self._syncing = False

    def bind(self):
        """
        Causes event listeners to be added in source and target expression as
        dictated by the current synchronization mode. Releases any existing
        event listeners first to ensure that they aren't added twice.

        """
        self.unbind()
        if self.mode >= ONEWAY:
            self.sourceExpression.bind(self.sourceChanged)
        if self.mode == TWOWAY:
            self.targetExpression.bind(self.targetChanged)

    def unbind(self):
        """
        Releases all event listeners from both source and target expressions.

        """
        self.sourceExpression.unbind()
        self.targetExpression.unbind()

    def dump(self, indent=0, outfile=None):
        """
        Prints the source code of source and target expressions plus their
        binding chains to the standard output or `outfile` if one was provided.

        """
        outfile = outfile or sys.stdout
        indentspace = u' ' * indent
        print >> outfile, indentspace + u'Source:'
        self.sourceExpression.dump(indent + 2)
        print >> outfile, indentspace + u'Target:'
        self.targetExpression.dump(indent + 2)


class BindingGroup(object):
    """
    Binding groups are containers for a number of Bindings.
    Each group provides default options for any bindings created through it,
    and allow synchronizing all bindings in them at once.

    """
    def __init__(self, **options):
        self.options = options
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
        b = Binding(source, source_expr, target, target_expr, **combined_opts)
        self.bindings.append(b)
        b.bind()
        if b.mode != MANUAL:
            b.sync()
        return b

    def unbind(self):
        """Releases all event listeners from all bindings in this group."""

        for b in self.bindings:
            b.unbind()
        del self.bindings[:]

    def sync(self, reverse=False):
        """
        Synchronizes all bindings in this group.

        :param reverse: ``True`` to synchronize targets to sources,
                        ``False`` to synchronize sources to targets

        """
        for b in self.bindings:
            b.sync(reverse)

    def dump(self, indent=0, outfile=None):
        """
        Prints the source code of source and target expressions plus their
        binding chains for every binding in this group to the standard output,
        or `outfile` if one was provided.

        """
        outfile = outfile or sys.stdout
        indentspace = u' ' * indent
        for i, b in enumerate(self.bindings):
            print >> outfile, u'%sBinding %d:' % (indentspace, i + 1)
            b.dump(indent + 2, outfile)
