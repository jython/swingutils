Deploying Jython/Swing applications
===================================

The easiest deployment method for desktop Java applications is
`Java Web Start <http://en.wikipedia.org/wiki/Java_Web_Start>`_.
This involves serving the application files from a web server.

Steps required to publish your application with Java Web Start:

#. Create a code signing key if you don't have one already, using
   `keytool <http://download.oracle.com/javase/6/docs/technotes/tools/solaris/keytool.html>`_
#. Get the standalone Jython jar (use the Jython installer) and sign the jar
   with `jarsigner <http://download.oracle.com/javase/6/docs/technotes/tools/solaris/jarsigner.html>`_
   using your own key
#. Sign your copy of jython-swingutils.jar
#. Copy both jars to your web server's application directory (the one you're
   serving your application files from)
#. Create a JNLP file for your application (a sample can be found in the
   ``examples`` directory) and copy it to the web server
#. Build and sign your application's jar file(s) and copy them to web server

To install the application, just point a web browser to the JNLP file and Java
should do the rest. You only need to repeat the last step when you update your
application. You can automate building and signing using
`ant <http://ant.apache.org/>`_ or similar tools. The Jython-SwingUtils
build.xml file should provide a good starting point for this. It just needs a
build.properties file to supply the necessary variables.

If your application depends on third party Python distributions (installed in
the "site-packages" directory), you need to include them in one or more .jar
files distributed with your application. You have to package them so that the
top level package directory (and not its contents!) is at the root of the jar
structure. Remember to add the jar file(s) to your .jnlp file.

The `Jump <http://gitorious.org/jump/>`_ tool by Olli Wang was specifically
designed for packaging Jython applications, but as of this writing, the
documentation is nowhere to be seen and the future of that project seems
uncertain. It might be worth a look anyway since it is loaded with useful
features.

.. seealso:: `Java Web Start tutorial <http://download.oracle.com/javase/tutorial/deployment/webstart/>`_
.. seealso:: `Deploying a Single JAR, the Jython Book <http://www.jython.org/jythonbook/en/1.0/DeploymentTargets.html#deploying-a-single-jar>`_
