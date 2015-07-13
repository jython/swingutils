v2.1.1
======

* Fixed addEventListener() not allowing built-in functions as event listeners


v2.1.0
======

* BACKWARDS INCOMPATIBLE: event handlers are now always sent the
  event as the first argument. While functions with no arguments
  were previously allowed as event handlers, this was never
  documented.
* BACKWARDS INCOMPATIBLE: @swingCoroutine now requires that wrapped
  callables are generator functions. While they were always intended
  to be used this way, it was previously allowed to decorate normal
  functions as well.
* Added the setDefaultCoroutineExceptionHandler() function in
  swingutils.threads.coroutine which allows you to set a default
  handler for any unhandled exceptions in @swingCoroutine.


v2.0.1
======

* Use super() to call superclass constructors in combo/list models as
  originally intended
* Added instructions for building jars


v2.0.0
======

Breaking changes:

* Switched exclusively to Python 2.7 syntax
* Removed the swingutils.defer.AsyncToken class in favor of Futures from
  concurrent.futures
* Renamed swingutils.defer.inlineCallbacks to swingCoroutine

Other changes:

* Switched version control system from Mercurial to Git
* Added the ability to add callables that don't take arguments as event
  listeners 
* Event listeners added in JFormDesigner work now
* Fixed incorrect information in a few docstrings
* Removed assertions from ObjectTableModel because they interfered with
  some table model proxying schemes


v1.0.2
======

* FIXED: BeanProperty was sharing the value across instances of host class
* CHANGED: ObjectTableModel now accepts a callable in place of an attribute name
* CHANGED: FormLoadException now contains the parent exception and displays it
  in the message


v1.0.1
======

* FIXED: The released distribution was missing README.rst, which prevented
  installation


v1.0 final
==========

* ADDED: Decorator wrapper for swingutils.threads.swing.runSwingLater
* ADDED: DocumentListener shortcuts in swingutils.events
* FIXED: EmptyNumberFormatter raised an AttributeException
* FIXED: Window owner was not getting set in
  swingutils.thirdparty.jformdesigner.WindowWrapper
* CHANGED: @inlineCallbacks now always returns an AsyncToken for consistency
* CHANGED: @inlineCallbacks now uses @swingRun instead of @swingCall to avoid
  certain undesirable side effects (the calling thread would get stuck waiting
  for the generator to exit)
* CHANGED: MirrorObject only fires events for properties for which there are
  registered listeners (if no global event listeners are registered)
* CHANGED: Removed MultiListenerWrapper which was redundant to begin with


v1.0b2
======

* ADDED: The installNumberFormat() function now accepts the ``nullable`` option
  and returns ``None`` when an empty value is parsed (instead of refusing to
  validate)
* ADDED: New methods in AbstractDelegateList: ``count()``, ``index()``,
  ``remove()``
* ADDED: ListDataListener shortcuts in swingutils.events
* FIXED: Functions decorated with ``@inlineCallbacks`` will now work even when
  they're not generators
* FIXED: List/table models generated change events with incorrect row ranges
* FIXED: Accidental type conversion when firing property change events
  (affected at least boolean values)
* FIXED: Use ``getBean()`` instead of ``getComponent()`` in JFormDesigner
  wrappers so that non-visual beans can be used too
* CHANGED: Bindings now use byte strings instead of unicode strings for logging
  (since ``__repr__()`` is supposed to give a bytestring)
* CHANGED: Table models now fire a tableDataChange event when the delegate is
  replaced
* CHANGED: TableSelectionMirror sets its delegate to ``None`` if multiple rows
  are selected


v1.0b1
======

First public release.
