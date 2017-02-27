===================================================================
TestVox: Web based Framework for Running Subjective Listening Tests
===================================================================
:Contact: Alok Parlikar <aup@cs.cmu.edu>
:Date: July 2012

What is TestVox?
================

Speech research often requires scientists to conduct subjective
listening tests to compare their methods against other
methods. Research in Text-to-Speech, for example, often requires
conducting listening tests to determine if new synthetic voices are
better than earlier voices.

TestVox helps you to quickly set up listening tasks. It comes with a
webserver of itself, so you can host it without worrying about complex
system administration. It is compatible with Amazon Mechanical Turk,
so you can post tasks (HITs) on that crowdsourcing platform to recruit
participants and get results quickly.

Obtaining TestVox
=================

TestVox is available in two different formats: source-code, and
pre-built. If you only want to use TestVox to run a set of supported
tests, please download the pre-built version and get started. If you
would like to contribute to the source of TestVox, make changes, add
new tests, etc., please download the sources.

* `Download Prebuilt Version`_ and get going!
* Obtain the `source code`_

.. _`Download Prebuilt Version`: http://bitbucket.org/happyalu/testvox/downloads
.. _`source code`: http://www.bitbucket.org/happyalu/testvox/overview


Using the Pre-Built Version
===========================

You will need Python 2.7 to be installed on your machine in order to
use TestVox. Visit http://www.python.org to obtain a version for your OS.

::

  # unzip the distribution
  unzip TestVox-prebuilt.zip

  # start the webserver
  cd TestVox-prebuilt
  python testvox_server.py

The Pre-Built version includes redistribution of the following python packages:

* CherryPy
* PyYAML
* Jinja2
* Web2PY DAL

License information of these packages can be found together with the packages in the ext_tools directory.

Building from Sources
=====================

Before you can build from sources, you need the following:

* Python 2.7: Get from http://www.python.org
* PyJS: Get from http://www.pyjs.org

Build Instructions
------------------

::

  # First Make sure Python works
  $ python --version

  # Environment Variable for PyJS:
  $ export PYJAMAS_HOME=/path/to/pyjs

  # Make sure PyJS is set up correctly
  $ cd $PYJAMAS_HOME
  $ python bootstrap.py

  # clone TestVox git repository
  $ git clone url/testvox.git
  $ cd testvox

  # build a debug version
  $ python setup.py

  # build a release version
  $ python setup.py --task=build_release

  # build a pre-built distribution
  $ python setup.py --task=deploy
