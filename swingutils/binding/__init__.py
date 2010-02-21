"""
This module lets you synchronize properties between two objects.

The adapter objects returned by the binding methods store their endpoints
using weak references, and automatically sever the connection if either side is
garbage collected.

"""
from cStringIO import StringIO
from tokenize import generate_tokens, TokenError, untokenize
import logging

from swingutils.events import addPropertyListener
from swingutils.binding.adapters import registry


READ_ONCE = 0
READ_ONLY = 1
READ_WRITE = 2

class CompoundWriteError(Exception):
    def __init__(self):
        Exception.__init__(self, 'Attempted to write to a compound expression')


class ExpressionClause(object):
    reader = None
    writer = None

    def __init__(self, source, tokens):
        self.source = source
        self.reader = compile(source, '$$binding-reader$$', 'eval')
        self.parts = []

        nexttokens = []
        nesting_level = 0
        for t in tokens:
            if t[1] in u'{([':
                nesting_level += 1
            elif t[1] in u'})]':
                nesting_level -= 1
            elif t[1] == '.' and nesting_level == 0:
                self._addPart(nexttokens)
                del nexttokens[:]
            nexttokens.append(t)
        self._addPart(nexttokens)

    def _addPart(self, tokens):
        if len(tokens) == 1 and tokens[0][0] == 1:
            # Token type 1 = NAME (an identifier)
            self.parts.append(tokens[0][1])
        else:
            text = untokenize(tokens)
            code = compile(text, '$$binding-reader$$', 'eval')
            self.parts.append(code)

    def getValue(self, obj):
        return eval(self.reader, globals(), obj.__dict__)

    def setValue(self, obj, value):
        if not self.writer:
            code = '%s=__binding_value' % self.source
            self.writer = compile(code, '$$binding-writer$$', 'exec')

        writerGlobals = globals().copy()
        writerGlobals['__binding_value'] = value
        exec(self.writer, writerGlobals, obj.__dict__)


class BindingExpression(object):
    def __init__(self, root, expr, logger=logging.getLogger(__name__)):
        self.root = root
        self.parseExpression(expr)

    def parseExpression(self, expr):
        """
        Separates ``expr`` into plain strings and expression clauses and
        stores them in ``self.parts``.
        
        :type expr: str or unicode

        """
        pos = 0
        end = max(len(expr) - 1, 0)
        self.parts = []
        while pos < end:
            newpos = expr.find(u'${', pos)
            if newpos >= 0:
                # Store any plain text leading up to this expression
                if newpos > pos:
                    self.parts.append(expr[pos:newpos])

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
                self.parts.append(ExpressionClause(source, tokens))
                pos = newpos + expr_end + 3
                continue

            # The rest is plain text
            self.parts.append(expr[pos:])
            return

    def getValue(self):
        results = []
        for part in self.parts:
            if isinstance(part, ExpressionClause):
                try:
                    result = part.getValue(self.root)
                except:
                    self.logger.debug(u'Error evaluating expression "%s"',
                                      part.source, exc_info=True)
                    continue
                results.append(result)
            else:
                results.append(part)

        # Always return a string if the expression contains more than one part,
        # otherwise return the result as is, or None
        if len(self.parts) == 1:
            return results[0] if results else None

        return u''.join([unicode(r) for r in results])

    def setValue(self, value):
        if len(self.parts) > 1:
            raise CompoundWriteError
        self.parts[0].setValue(self.root, value)


class Binding(object):
    def __init__(self, source, source_expr, target, target_expr, mode, logger):
        self.source = BindingExpression(source, source_expr)
        self.target = BindingExpression(target, target_expr)
        self.mode = mode
        self.logger = logger
        self.sync()

    def sync(self):
        self.target.setValue(self.source.getValue())

    def unbind(self):
        self.source.unbind()
        self.target.unbind()


class BindingGroup(object):
    def __init__(self, name=None, logger=None):
        self.logger = logger
        self.bindings = []

    def bind(self, source, source_expr, target, target_expr, **options):
        b = Binding(source, source_expr, target, target_expr, options)
        self.bindings.append(b)

    def syncAll(self):
        for b in self.bindings:
            b.sync()

    def unbindAll(self):
        for b in self.bindings:
            b.unbind()
        del self.bindings[:]


globalGroup = BindingGroup('root', logging.getLogger(__name__))
bind = globalGroup.bind
