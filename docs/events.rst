Event listening
===============

This module contains an alternate implementation for listening to UI events.
The usual Jython way to do this is to assign a callable to an
`event property`::

    button.actionPerformer = myhandler

While this approach is dead simple, it has two drawbacks. First off, you can
only assign a single handler at a time, so you have to track which
components you added an event to so you don't accidentally do it twice.
Second, it is impossible to remove an event listener that was added this way.
Not even assigning ``None`` to the event property will remove the listener.

This module eliminates both problems at once. You have to be a bit more
explicit when adding event listeners though::

    from java.awt.event import ActionListener

    from swingutils.events import addEventListener

    def listener(event):
        print "Button was pushed"

    listener = addEventListener(button, ActionListener, 'actionPerformed', myhandler)

And to remove the listener later::

    listener.unlisten()

That's it! You can of course discard the returned listener object if you don't
plan to unlisten later on.

To listen to changes to individual properties (PropertyChangeEvents), you have
to use a different function::

    from swingutils.events import addPropertyListener

    def listener(event):
        print "Button's text changed to %s" % event.newValue

    addPropertyListener(button, 'text', listener)

Both of these functions also support specifying extra positional and keyword
arguments, which are passed through to the listener::

    from java.awt.event import ActionListener

    from swingutils.events import addEventListener

    def listener(event, somearg, anotherarg):
        print "Button was pushed, and somearg is %s and anotherarg is %s" % (somearg, anotherarg)

    listener = addEventListener(button, ActionListener, 'actionPerformed', myhandler, 'foo', anotherarg='bar')
