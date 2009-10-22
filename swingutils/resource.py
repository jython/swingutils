"""
This module contains helper functions to load resources (=files) contained
in jars, or anywhere else in the class path.

"""

from org.python.util import jython

__all__ = ('getResource', 'getResourceAsStream', 'loadImage', 'loadImageIcon')


def getResource(path, classloader=jython.classloader):
    """
    Loads a resource from anywhere on the classpath.
    
    :param path: path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`java.lang.Object`

    """
    return classloader.getResource(path)


def getResourceAsStream(path, classloader=jython.classloader):
    """
    Opens a stream to a resource anywhere on the classpath.
    
    :param path: path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`java.io.InputStream`

    """
    return classloader.getResourceAsStream(path)


def loadImage(path, classloader=jython.classloader):
    """Loads an image resource as java.awt.Image from anywhere on the
    class path. Supported image types are JPEG, PNG and GIF, and possibly
    others if 
    
    :param path: path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`java.awt.Image`
    
    """
    from javax.imageio import ImageIO

    stream = getResourceAsStream(path, classloader)
    return ImageIO.read(stream)


def loadImageIcon(path, classloader=jython.classloader):
    """Loads an image resource as an ImageIcon from anywhere on the
    class path.
    
    :param path: Path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`javax.swing.ImageIcon`

    """
    from javax.swing import ImageIcon

    return ImageIcon(loadImage(path, classloader))
