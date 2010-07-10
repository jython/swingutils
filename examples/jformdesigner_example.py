from java.awt.event import MouseListener

from swingutils.thirdparty.jformdesigner import WindowWrapper
from swingutils.threads.swing import swingRun
from swingutils.events import addEventListener


class JFormDesignerDemoFrame(WindowWrapper):
    def __init__(self):
        # The form name will be automatically determined from the class name
        WindowWrapper.__init__(self)
        self.c.firstField.text = u"Some text"
        self.c.readOnlyField.text = u"Can't change this"
        self.c.editorPane.text = u'Sample text'
        addEventListener(self.c.exitButton, MouseListener, 'mouseClicked',
                         lambda event: self.window.dispose())


@swingRun
def createGUI():
    # All Swing operations should be executed in the Event Dispatch Thread
    JFormDesignerDemoFrame().visible = True


if __name__ == '__main__':
    createGUI()