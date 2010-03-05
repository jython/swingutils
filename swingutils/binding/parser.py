import ast
import weakref

from swingutils.binding.adapters import registry


class BindingNode(object):
    adapter = None
    next = None
    lastParentRef = None

    def __init__(self, callback, globals_, options):
        self.callback = callback
        self.globals_ = globals_
        self.options = options
        self.logger = options.get('logger')

    def getAdapter(self, parent):
        return None

    def handleEvent(self, event=None):
        self.callback()
        if self.next:
            self.next.unbind()
            if self.lastParentRef:
                parent = self.lastParentRef()
                if parent:
                    self.next.bind(parent)
                else:
                    del self.lastParentRef

    def bind(self, parent):
        self.lastParentRef = weakref.ref(parent)
        self.adapter = self.getAdapter(parent)

        if self.adapter:
            try:
                self.adapter.addListeners(parent, self.handleEvent)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                if self.logger:
                    self.logger.debug(u'%s: error adding event listener' %
                                      self, exc_info=True)
                if not self.options['ignoreErrors']:
                    raise

        if self.next:
            try:
                value = self.getValue(parent)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                if self.logger:
                    self.logger.debug(u'%s: error getting value',
                                      self, exc_info=True)
                if not self.options['ignoreErrors']:
                    raise
                return

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

    def __init__(self, attr, callback, globals_, options):
        BindingNode.__init__(self, callback, globals_, options)
        self.attr = attr

    def getValue(self, parent):
        return getattr(parent, self.attr)

    def getAdapter(self, parent):
        return registry.getPropertyAdapter(parent, self.attr, self.options)

    def __unicode__(self):
        if self.adapter and not isinstance(self.adapter,
            registry.defaultPropertyAdapter):
            adapterClassName = self.adapter.__class__.__name__
            return u'Attribute(%s, %s)' % (self.attr, adapterClassName)
        return u'Attribute(%s)' % self.attr


class VariableNode(BindingNode):
    __slots__ = 'name'

    def __init__(self, name, callback, globals_, options):
        BindingNode.__init__(self, callback, globals_, options)
        self.name = name

    def getValue(self, parent):
        return self.globals_.vars[self.name]

    def __unicode__(self):
        return u'Variable(%s)' % self.name


class SubscriptNode(BindingNode):
    __slots__ = 'code'

    def __init__(self, node, callback, globals_, options):
        BindingNode.__init__(self, callback, globals_, options)
        value = ast.Name(id='___binding_parent')
        subscript = ast.Subscript(value=value, slice=node.slice)
        expr = ast.Expression(body=subscript)
        self.code = compile(expr, '$$binding-subscript$$', 'eval')

    def getValue(self, parent):
        slice = eval(self.code, self.globals_, dict(___binding_parent=parent))
        return parent[slice]

    def getAdapter(self, parent):
        return registry.getListAdapter(parent, self.options)

    def __unicode__(self):
        if self.adapter and not isinstance(self.adapter,
            registry.defaultListAdapter):
            adapterClassName = self.adapter.__class__.__name__
            return u'Subscript(%s)' % adapterClassName
        return u'Subscript'


class CallNode(BindingNode):
    __slots__ = 'code'

    def __init__(self, node, callback, globals_, options):
        BindingNode.__init__(self, callback, globals_, options)
        func = ast.Name(id='___binding_parent', ctx=ast.Load())
        call = ast.Call(func=func, args=node.args, keywords=node.keywords,
                        starargs=node.starargs, kwargs=node.kwargs)
        expr = ast.Expression(body=call)
        self.code = compile(expr, '$$binding-call$$', 'eval')

    def getValue(self, parent):
        return eval(self.code, self.globals_, dict(___binding_parent=parent))

    def __unicode__(self):
        return u'Call'


class NameCollector(ast.NodeVisitor):
    def __init__(self):
        self.names = set()
    
    def visit_Name(self, node):
        self.names.add(node.id)


class ChainVisitor(ast.NodeVisitor):
    def __init__(self, callback, globals_, options, chains, excludedNames):
        self.callback = callback
        self.globals_ = globals_
        self.options = options
        self.chains = chains
        self.excludedNames = excludedNames
        self.lastNode = None

    def addNode(self, node):
        node.next = self.lastNode
        self.lastNode = node

    def visit_Name(self, node):
        # Names are treated as attributes of the root object
        if node.id in self.globals_.vars:
            bindingNode = VariableNode(node.id, self.callback, self.globals_,
                                       self.options)
        elif node.id not in self.excludedNames:
            bindingNode = AttributeNode(node.id, self.callback, self.globals_,
                                        self.options)
        else:
            return

        self.addNode(bindingNode)
        self.chains.append(self.lastNode)
        self.lastNode = None

    def visit_Attribute(self, node):
        self.addNode(AttributeNode(node.attr, self.callback, self.globals_,
                                   self.options))
        self.visit(node.value)

    def visit_Subscript(self, node):
        self.addNode(SubscriptNode(node, self.callback, self.globals_,
                                   self.options))
        self.generic_visit(node)

    def visit_Call(self, node):
        self.addNode(CallNode(node, self.callback, self.globals_,
                              self.options))
        self.generic_visit(node)

    def visit_comprehension(self, node):
        # Collect variable declarations for exclusion in other fields
        visitor = NameCollector()
        visitor.visit(node.target)

        visitor = ChainVisitor(self.callback, self.globals_, self.options,
                               self.chains, visitor.names)
        for key, value in ast.iter_fields(node):
            if key != 'target':
                visitor.visit(value)


def createChains(expr, callback, globals_, options):
    root = ast.parse(expr, '$$binding-expression$$', 'eval')
    chains = []
    visitor = ChainVisitor(callback, globals_, options, chains, set())
    visitor.visit(root)
    return chains
