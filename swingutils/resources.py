"""
This module contains helper functions to load resources (=files) contained
in jars, or anywhere else in the class path.

"""
from __future__ import unicode_literals

from java.lang import Thread

__all__ = ('getResource', 'getResourceAsStream', 'loadImage', 'loadImageIcon')


def getResource(path, classloader=None):
    """
    Loads a resource from anywhere on the classpath.

    :param path: path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`java.lang.Object`

    """
    classloader = classloader or Thread.currentThread().contextClassLoader
    return classloader.getResource(path)


def getResourceAsStream(path, classloader=None):
    """
    Opens a stream to a resource anywhere on the classpath.

    :param path: path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`java.io.InputStream`

    """
    classloader = classloader or Thread.currentThread().contextClassLoader
    return classloader.getResourceAsStream(path)


def loadImage(path, classloader=None):
    """Loads an image resource as java.awt.Image from anywhere on the
    class path. Supported image types are JPEG, PNG and GIF, and possibly
    others if you have installed any extensions to the ImageIO system (such as
    `Java Advanced Imaging
    <http://java.sun.com/javase/technologies/desktop/media/jai/>`_).

    :param path: path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`java.awt.Image`

    """
    from javax.imageio import ImageIO

    stream = getResourceAsStream(path, classloader)
    return ImageIO.read(stream)


def loadImageIcon(path, classloader=None):
    """Loads an image resource as an ImageIcon from anywhere on the
    class path.

    :param path: Path to the resource (separate elements with '/')
    :param classloader: class loader to use for loading the resource
    :rtype: :class:`javax.swing.ImageIcon`

    """
    from javax.swing import ImageIcon

    resource = getResource(path, classloader)
    return ImageIcon(resource)
