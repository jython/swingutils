Access to resources
===================

This module provides a few shortcuts to accessing resources on the class path
in a uniform and transparent manner. The generic methods for this are
:func:`~swingutils.resources.getResource` and
:func:`~swingutils.resources.getResourceAsStream`. The difference between the
two is only that the first one fully loads the resource and returns the object,
while the second one only opens the resource as a stream and returns the
stream. The resources module also contains specialized shortcuts for loading
image icons for use in UI elements
(:func:`~swingutils.resources.loadImageIcon`) or plain Images
(:func:`~swingutils.resources.loadImage`).


Tips
----

The proper path to the resource to be loaded depends on the runtime
environment. You may need to remove the ``/`` prefix from the path for resource
loading to work. This seems to hold true at least for applications deployed via
Java Web Start.

You may find it convenient to create your own shortcuts for resource loading
that only take a file name (assuming you keep your resources in a single
location). This would look something like the following::

	from swingutils.resources import loadImageIcon
	
	loadImageIcon = lambda filename: loadImageIcon('application/resources/%s' % filename)
