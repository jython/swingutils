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
