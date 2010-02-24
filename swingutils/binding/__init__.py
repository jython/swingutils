"""
This module lets you automatically synchronize properties between two objects.

Some UI components require special handling to get them to behave as expected,
and this is provided by a collection of adapters. Adapters are used
automatically when a matching object is encountered.

"""
from cStringIO import StringIO
from tokenize import generate_tokens, TokenError, untokenize
import __builtin__
import logging

from swingutils.events import addPropertyListener
from swingutils.binding.adapters import registry


READ_ONCE = 0
READ_ONLY = 1
READ_WRITE = 2


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


class LocalsDict(object):
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, key):
        try:
            return getattr(self.obj, key)
        except AttributeError:
            raise KeyError

    def __setitem__(self, key, value):
        setattr(self.obj, key, value)

    def __contains__(self, key):
        return hasattr(self.obj, key)


class ClausePart(object):
    PROPERTY = 0
    LIST = 1
    CODE = 2

    adapter = None

    def __init__(self, tokens, options):
        self.options = options

        if len(tokens) == 1 and tokens[0][0] == 1:
            # Token type 1 = NAME (an identifier)
            self.type_ = self.PROPERTY
            self.item = tokens[0][1]
        elif tokens[0][1] == '[':
            # Start of a list expression
            self.type_ = self.LIST
            text = '___binding_value%s' % untokenize(tokens)
            self.item = compile(text, '$$binding-list$$', 'eval')
        else:
            # Any other expression
            self.type_ = self.CODE
            text = untokenize(tokens)
            self.item = compile(text, '$$binding-code$$', 'eval')

    def getValue(self, obj):
        if self.type_ == self.PROPERTY:
            return getattr(obj, self.item, None)

        clauseGlobals = {'__builtins__': __builtin__}
        if self.type_ == self.LIST:
            clauseGlobals['___binding_value'] = obj
        return eval(self.item, clauseGlobals, {})

    def bind(self, obj, callback, *args, **kwargs):
        self.unbind()

        if self.type_ == self.PROPERTY:
            self.adapter = registry.getPropertyAdapter(obj, self.options)
            self.adapter.addListener(obj, self.item, callback, *args, **kwargs)
        elif self.type_ == self.LIST:
            self.adapter = registry.getListAdapter(obj, self.options)
            self.adapter.addListener(obj, callback, *args, **kwargs)

    def unbind(self):
        if self.adapter:
            self.adapter.removeListener()
            del self.adapter


class ExpressionClause(object):
    reader = None
    writer = None
    parts = None

    def __init__(self, source, tokens, options):
        self.source = source
        self.tokens = tokens
        self.options = options

    def getValue(self, obj):
        if not self.reader:
            self.reader = compile(self.source, '$$binding-reader$$', 'eval')
        return eval(self.reader, globals(), LocalsDict(obj))

    def setValue(self, obj, value):
        if not self.writer:
            self.writer = compile('%s=___binding_value' % self.source,
                                  '$$binding-writer$$', 'exec')
        writerGlobals = globals().copy()
        writerGlobals['___binding_value'] = value
        exec(self.writer, writerGlobals, LocalsDict(obj))

    def _splitExpression(self):
        """Breaks the given expression into parts for event listening."""
        self.parts = []
        storedTokens = []
        nestingLevel = 0
        for t in self.tokens:
            if t[1] in u'{([':
                nestingLevel += 1
            elif t[1] in u'})]':
                nestingLevel -= 1

            if nestingLevel == 0:
                if t[1] == '.':
                    self.parts.append(ClausePart(storedTokens, self.options))
                    del storedTokens[:]
                    continue
                if t[1] == ']':
                    storedTokens.append(t)
                    self.parts.append(ClausePart(storedTokens, self.options))
                    del storedTokens[:]
                    continue

            storedTokens.append(t)

        if storedTokens:
            self.parts.append(ClausePart(storedTokens, self.options))

        # The tokens are never needed again
        del self.tokens

    def _partChanged(self, event, obj, callback, index):
        """
        Rebinds the chain from the point it was changed from, and calls the
        parent callback.

        """
        self.bind(obj, callback, index)
        callback()

    def bind(self, obj, callback, index=0):
        if self.parts is None:
            self._splitExpression()

        for i, part in enumerate(self.parts[index:]):
            if obj is None:
                return
            part.bind(obj, self._partChanged, obj, callback, i)
            obj = part.getValue(obj)
    
    def unbind(self):
        if self.parts:
            for part in self.parts:
                part.unbind()


class BindingExpression(object):
    def __init__(self, parts):
        self.parts = parts

    @classmethod
    def create(cls, expr, options):
        bindingExpr = cls([])
        pos = 0
        end = max(len(expr) - 1, 0)
        while pos < end:
            newpos = expr.find(u'${', pos)
            if newpos == -1:
                break

            # Store any plain text leading up to this expression
            if newpos > pos:
                bindingExpr.parts.append(expr[pos:newpos])

            # Find the matching }, taking nested {} into account
            expr_buf = StringIO(expr[newpos + 2:])
            expr_end = None
            nesting_level = 0
            tokens = []
            try:
                for token in generate_tokens(expr_buf.readline):
                    if token[1] == u'{':
                        nesting_level += 1
                    elif token[1] == u'}':
                        if nesting_level > 0:
                            nesting_level -= 1
                        else:
                            expr_end = token[2][1]
                            break
                    tokens.append(token)
            except TokenError:
                raise Exception('Unmatched }: %s' % expr[newpos:])

            # Create the expression clause
            source = expr_buf.value[:expr_end]
            clause = ExpressionClause(source, tokens, options)
            bindingExpr.parts.append(clause)
            pos = newpos + expr_end + 3
            continue

        # The rest is plain text
        leftover = expr[pos:]
        if leftover:
            bindingExpr.parts.append(expr[pos:])

        return bindingExpr

    def __add__(self, expr):
        return BindingExpression(self.parts + expr.parts)

    def getValue(self, obj):
        results = []
        for part in self.parts:
            if isinstance(part, ExpressionClause):
                try:
                    result = part.getValue(obj)
                except Exception, e:
                    raise BindingReadError('Error evaluating expression %s' %
                                           (part.source, e))
                results.append(result)
            else:
                results.append(part)

        # Always return a string if the expression contains more than one part,
        # otherwise return the result as is, or None
        if len(self.parts) == 1:
            return results[0] if results else None

        return u''.join([unicode(r) for r in results])

    def setValue(self, obj, value):
        if len(self.parts) > 1:
            raise BindingWriteError('Cannot write to a compound expression')
        if not isinstance(self.parts[0], ExpressionClause):
            raise BindingWriteError('Cannot write to a plain-string expression')
        self.parts[0].setValue(obj, value)

    def bind(self, obj, callback):
        for part in self.parts:
            if isinstance(part, ExpressionClause):
                part.bind(obj, callback)

    def unbind(self):
        for part in self.parts:
            if isinstance(part, ExpressionClause):
                part.unbind()


class Binding(object):
    # Flag that prevents infinite loops
    _syncing = False

    def __init__(self, source, sourceExpression, target, targetExpression,
                 options):
        self.logger = options.get('logger')
        self.mode = options.get('mode')
        self.source = source
        self.target = target
        if isinstance(sourceExpression, BindingExpression):
            self.sourceExpression = sourceExpression
        else:
            self.sourceExpression = BindingExpression.create(sourceExpression,
                                                             options)
        if isinstance(targetExpression, BindingExpression):
            self.targetExpression = targetExpression
        else:
            self.targetExpression = BindingExpression.create(targetExpression,
                                                             options)

        if self.mode >= READ_ONLY:
            self.sourceExpression.bind(source, self.sourceChanged)
        if self.mode == READ_WRITE:
            self.targetExpression.bind(target, self.targetChanged)
        
        self.syncSourceToTarget()

    def sourceChanged(self):
        self.logger.debug('Source changed')
        self.syncSourceToTarget()

    def targetChanged(self):
        self.logger.debug('Target changed')
        self.syncTargetToSource()

    def syncSourceToTarget(self):
        if self._syncing:
            return

        self._syncing = True
        try:
            value = self.sourceExpression.getValue(self.source)
            self.targetExpression.setValue(self.target, value)
        except Exception:
            self.logger.exception('Error syncing source -> target')
        finally:
            self._syncing = False

    def syncTargetToSource(self):
        if self._syncing:
            return

        self._syncing = True
        try:
            value = self.targetExpression.getValue(self.target)
            self.sourceExpression.setValue(self.source, value)
        except Exception:
            self.logger.exception('Error syncing target -> source')
        finally:
            self._syncing = False

    def unbind(self):
        self.sourceExpression.unbind()
        self.targetExpression.unbind()


class BindingGroup(object):
    def __init__(self, **options):
        self.options = options
        self.options.setdefault('logger', logging.getLogger(__name__))
        self.options.setdefault('mode', READ_ONLY)
        self.bindings = []

    def bind(self, source, source_expr, target, target_expr, **options):
        combined_opts = self.options.copy()
        combined_opts.update(options)
        b = Binding(source, source_expr, target, target_expr, combined_opts)
        self.bindings.append(b)

    def sync(self):
        for b in self.bindings:
            b.syncSourceToTarget()

    def unbindAll(self):
        for b in self.bindings:
            b.unbind()
        del self.bindings[:]

defaultGroup = BindingGroup()
bind = defaultGroup.bind
