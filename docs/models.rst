Models
======

The ``swingutils.models`` package offers a collection of useful models for most
Swing components that require the use of models.

List models
-----------

DelegateListModel
"""""""""""""""""

This class wraps a Python ``list`` object and implements the
:class:`javax.swing.ListModel` interface. You can access as any normal list,
but it also fires list events when its contents are modified.

Table models
------------

DelegateTableModel
""""""""""""""""""

This class wraps a Python ``list`` object and implements the
:class:`javax.swing.table.TableModel`` interface. All elements of the wrapped
list are expected to be lists or tuples (or any other indexed collections).
Column names and types are provided in the constructor as a series of
2-tuples::

    from java.lang import String, Integer
    
    from swingutils.models.table import DelegateTableModel

    model = DelegateTableModel(somedata, ('Name', String), ('Age', Integer), 'Hometown')

As you probably noticed, the last column was not a tuple, but a string.
This translates to ``('HomeTown', Object)``. The reason why types are given
as Java types is to give the default column renderer a hint for choosing the
correct renderer for this column.

ObjectTableModel
""""""""""""""""

This table model is much more useful than its parent class
(:class:`~swingutils.models.DelegateTableModel`). The contents of the wrapped
list object are expected to be objects, and columns are mapped to their
attributes. Therefore the constructor expects an series of 3-tuples
(name, type, attribute name). You can no longer use the name-only shortcut of
only providing the name as a string -- you have to give all three values.
You can also supply a callable in place of the attribute name, in which case
the callable is called with each object in the list as the argument. The return
value of this callable is then used to draw the table cell.

TableSelectionProxy
"""""""""""""""""""

This is a utility class that you can use on a table that has an
:class:`~swingutils.models.table.ObjectTableModel` as its model. It tracks the
table selection and provides the ``selectedValue`` and ``selectedModelRow``
bound properties.

Combo box models
----------------

DelegateComboBoxModel
"""""""""""""""""""""

This is basically the same as
:class:`~swingutils.models.list.DelegateListModel`, but works as a combo box
model.
