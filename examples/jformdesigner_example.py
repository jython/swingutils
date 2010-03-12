from java.awt.event import MouseListener

from swingutils.thirdparty.jformdesigner import WindowWrapper
from swingutils.threads import asyncSwingTask
from swingutils.events import addEventListener


class JFormDesignerDemoFrame(WindowWrapper):
    def __init__(self):
        # The form name will be automatically determined from the class name
        WindowWrapper.__init__(self)
        self.firstField.text = u"Some text"
        self.readOnlyField.text = u"Can't change this"
        self.editorPane.text = u'Sample text'
        addEventListener(self.exitButton, MouseListener, 'mouseClicked',
                         lambda event: self.window.dispose())


@asyncSwingTask
def createGUI():
    # All Swing operations should be executed in the Event Dispatch Thread
    JFormDesignerDemoFrame().visible = True


if __name__ == '__main__':
    createGUI()