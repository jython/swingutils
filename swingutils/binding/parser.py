import ast
import weakref

from swingutils.binding.adapters import registry


class BindingNode(object):
    __slots__ = ('callback', 'globals_', 'parent')
    adapter = None
    next = None

    def __init__(self, callback, globals_, options):
        self.callback = callback
        self.globals_ = globals_
        self.options = options

    def getAdapter(self):
        return None

    def handleEvent(self, event):
        self.callback()
        if self.next:
            self.next.unbind()
            parent = self.parent() if self.parent else None
            if parent:
                self.next.bind(parent)

    def bind(self, parent):
        self.parent = weakref.ref(parent)
        self.adapter = registry.getPropertyAdapter(parent, self.attr,
                                                   self.options)

        if self.adapter:
            self.adapter.addListeners(parent, self.handleEvent)

        if self.next:
            value = self.getValue(parent, self.globals_)
            if value is not None:
                self.next.bind(value)

    def unbind(self):
        if hasattr(self, 'parent'):
            del self.parent
        if self.adapter:
            self.adapter.removeListeners()
            del self.adapter
        if self.next:
            self.next.unbind()


class AttributeNode(BindingNode):
    def __init__(self, attr, callback, globals_, options):
        BindingNode.__init__(self, callback, globals_, options)
        self.attr = attr

    def getValue(self, parent, globals_):
        return getattr(parent, self.attr)

    def getAdapter(self, parent):
        return registry.getPropertyAdapter(parent, self.attr, self.options)


class SubscriptNode(BindingNode):
    def __init__(self, node, callback, globals_, options):
        BindingNode.__init__(self, callback, globals_, options)
        value = ast.Name(identifier='___binding_parent')
        subscript = ast.Subscript(value=value, slice=node.slice,
                                  expr_context=node.expr_context)
        expr = ast.Expression(body=subscript)
        self.code = compile(expr, '$$binding-subscript$$', 'eval')

    def getValue(self, parent):
        slice = eval(self.code, self.globals_, dict(___binding_parent=parent))
        return parent[slice]

    def getAdapter(self, parent):
        return registry.getListAdapter(parent, self.options)


class CallNode(BindingNode):
    def __init__(self, node, callback, globals_, options):
        BindingNode.__init__(self, callback, globals_, options)
        func = ast.Name(identifier='___binding_parent')
        call = ast.Call(func=func, args=node.args, keywords=node.keywords,
                        starargs=node.starargs, kwargs=node.kwargs)
        expr = ast.Expression(body=call)
        self.code = compile(expr, '$$binding-call$$', 'eval')

    def getValue(self, parent):
        return eval(self.code, self.globals_, dict(___binding_parent=parent))


class ChainVisitor(ast.NodeVisitor):
    def __init__(self, callback, globals_, options):
        self.callback = callback
        self.globals_ = globals_
        self.options = options
        self.chains = []
        self.lastNode = None

    def addNode(self, node):
        node.next = self.lastNode
        self.lastNode = node

    def visit_Name(self, node):
        # Names are treated as attributes of the root object
        self.addNode(AttributeNode(node.id, self.callback, self.globals_,
                                   self.options))
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
        for key, value in ast.iter_fields(node):
            if key != 'target':
                # target can contain new variable declarations, so skip it
                self.visit(value)


def createChains(expr, callback, globals_, options):
    root = ast.parse(expr, '$$binding-expression$$', 'eval')
    visitor = ChainVisitor(callback, globals_, options)
    visitor.visit(root)
    return visitor.chains
