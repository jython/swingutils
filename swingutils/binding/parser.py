from __future__ import unicode_literals
import ast
import weakref

from .adapters import registry


class BindingNode(object):
    adapter = None
    next = None
    lastParentRef = None

    def __init__(self, callback, locals_, options):
        self.callback = callback
        self.locals_ = locals_
        self.options = options
        self.logger = options.get('logger')

    def getAdapter(self, parent):
        return None

    def checkedGetValue(self, parent):
        """
        Retrieves the current node's value from the parent using the
        ``getValue`` implementation in a subclass. If an exception is raised,
        the returned value will be ``None`` unless the `ignoreErrors` option
        is ``False``, in which case the caught exception is re-raised.

        """
        try:
            value = self.getValue(parent)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            if self.logger:
                self.logger.debug('%s: error getting value',
                                  self, exc_info=True)
            if not self.options['ignoreErrors']:
                raise
            value = None

        return value

    def handleEvent(self, event=None):
        if self.logger:
            self.logger.debug('%s: change event triggered' % self)

        self.callback()

        if self.next:
            # Remove existing bindings from the next element onwards
            self.next.unbind()

            # Get the new value for this node using the last bound parent,
            # if it still exists
            if self.lastParentRef:
                parent = self.lastParentRef()
                if parent:
                    value = self.checkedGetValue(parent)
                    if value is not None:
                        self.next.bind(value)
                else:
                    del self.lastParentRef

    def bind(self, parent):
        if self.logger:
            self.logger.debug('%s: adding event listeners (parent=%s)', self,
                              parent)

        self.lastParentRef = weakref.ref(parent)
        self.adapter = self.getAdapter(parent)

        if self.adapter:
            try:
                self.adapter.addListeners(parent, self.handleEvent)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                if self.logger:
                    self.logger.debug('%s: error adding event listener',
                                      self, exc_info=True)
                if not self.options['ignoreErrors']:
                    raise

        if self.next:
            value = self.checkedGetValue(parent)
            if value is not None:
                self.next.bind(value)

    def unbind(self):
        if self.lastParentRef:
            del self.lastParentRef
        if self.adapter:
            self.adapter.removeListeners()
            del self.adapter
        if self.next:
            self.next.unbind()


class AttributeNode(BindingNode):
    __slots__ = 'attr'

    def __init__(self, attr, callback, locals_, options):
        BindingNode.__init__(self, callback, locals_, options)
        self.attr = attr

    def getValue(self, parent):
        return getattr(parent, self.attr)

    def getAdapter(self, parent):
        return registry.getPropertyAdapter(parent, self.options, self.attr)

    def __unicode__(self):
        if self.adapter and not isinstance(
                self.adapter, registry.defaultPropertyAdapter):
            adapterClassName = self.adapter.__class__.__name__
            return 'Attribute(%s, %s)' % (self.attr, adapterClassName)
        return 'Attribute(%s)' % self.attr


class VariableNode(BindingNode):
    __slots__ = 'name'

    def __init__(self, name, callback, locals_, options):
        BindingNode.__init__(self, callback, locals_, options)
        self.name = name

    def getValue(self, parent):
        return self.locals_.vars[self.name]

    def __unicode__(self):
        return 'Variable(%s)' % self.name


class SubscriptNode(BindingNode):
    __slots__ = 'code'

    def __init__(self, node, callback, locals_, options):
        BindingNode.__init__(self, callback, locals_, options)
        value = ast.Name(id='___binding_parent')
        subscript = ast.Subscript(value=value, slice=node.slice)
        expr = ast.Expression(body=subscript)
        self.code = compile(expr, '$$binding-subscript$$', 'eval')

    def getValue(self, parent):
        slice = eval(self.code, self.locals_, dict(___binding_parent=parent))
        return parent[slice]

    def getAdapter(self, parent):
        return registry.getListAdapter(parent, self.options)

    def __unicode__(self):
        if self.adapter and not isinstance(
                self.adapter, registry.defaultListAdapter):
            adapterClassName = self.adapter.__class__.__name__
            return 'Subscript(%s)' % adapterClassName
        return 'Subscript'


class CallNode(BindingNode):
    __slots__ = 'code'

    def __init__(self, node, callback, locals_, options):
        BindingNode.__init__(self, callback, locals_, options)
        func = ast.Name(id='___binding_parent', ctx=ast.Load())
        call = ast.Call(func=func, args=node.args, keywords=node.keywords,
                        starargs=node.starargs, kwargs=node.kwargs)
        expr = ast.Expression(body=call)
        self.code = compile(expr, '$$binding-call$$', 'eval')

    def getValue(self, parent):
        return eval(self.code, self.locals_, dict(___binding_parent=parent))

    def __unicode__(self):
        return 'Call'


class NameCollector(ast.NodeVisitor):
    def __init__(self):
        self.names = set()

    def visit_Name(self, node):
        self.names.add(node.id)


class ChainVisitor(ast.NodeVisitor):
    def __init__(self, callback, locals_, options):
        self.callback = callback
        self.locals_ = locals_
        self.options = options
        self.chains = []
        self.excludedNames = set()
        self.lastNode = None

    def addNode(self, node):
        node.next = self.lastNode
        self.lastNode = node

    def subnodeVisit(self, node, callback):
        if isinstance(node, list):
            for item in node:
                self.subnodeVisit(item, callback)
        elif isinstance(node, ast.AST):
            visitor = ChainVisitor(callback, self.locals_, self.options)
            visitor.visit(node)
            self.chains.extend(visitor.chains)

    def visit_Name(self, node):
        # Names are treated as attributes of the root object
        if node.id in self.locals_.vars:
            bindingNode = VariableNode(node.id, self.callback, self.locals_,
                                       self.options)
        elif node.id not in self.excludedNames:
            bindingNode = AttributeNode(node.id, self.callback, self.locals_,
                                        self.options)
        else:
            return

        self.addNode(bindingNode)

        # Finish this chain and start a new one
        self.chains.append(self.lastNode)
        self.lastNode = None

    def visit_Str(self, node):
        self.lastNode = None
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.addNode(AttributeNode(node.attr, self.callback, self.locals_,
                                   self.options))
        self.visit(node.value)

    def visit_Subscript(self, node):
        bindingNode = SubscriptNode(node, self.callback, self.locals_,
                                    self.options)
        self.addNode(bindingNode)
        self.subnodeVisit(node.slice, bindingNode.handleEvent)
        self.visit(node.value)

    def visit_Call(self, node):
        bindingNode = CallNode(node, self.callback, self.locals_,
                               self.options)
        self.addNode(bindingNode)
        for key, value in ast.iter_fields(node):
            if key == 'func':
                self.visit(value)
            elif value:
                self.subnodeVisit(value, bindingNode.handleEvent)

    def visit_Lambda(self, node):
        collector = NameCollector()
        collector.visit(node.args)
        self.excludedNames.update(collector.names)
        self.visit(node.body)
        self.excludedNames.clear()

    def visit_GeneratorExp(self, node):
        for comprehension in node.generators:
            visitor = NameCollector()
            visitor.visit(comprehension.target)
            self.excludedNames.update(visitor.names)
            for key, value in ast.iter_fields(comprehension):
                if key != 'target':
                    self.visit(value)

        self.visit(node.elt)
        self.excludedNames.clear()

    visit_ListComp = visit_GeneratorExp


def createChains(expr, callback, locals_, options):
    root = ast.parse(expr, '$$binding-expression$$', 'eval')
    visitor = ChainVisitor(callback, locals_, options)
    visitor.visit(root)
    return visitor.chains
