===========
rtlogplayer
===========

Introduction
============

rtlogplayer is a GUI-based log player for OpenRTM-aist. It can play back
the log files recorded using rtshell's rtlog command. During play back,
you can change the target components to which data is sent and jump to
any position in the log file.

This software is developed at the National Institute of Advanced
Industrial Science and Technology. Approval number
. The development was financially supported by
the New Energy and Industrial Technology Development Organisation
Project for Strategic Development of Advanced Robotics Elemental
Technologies.  This software is licensed under the Eclipse Public
License -v 1.0 (EPL). See LICENSE.txt.


Requirements
============

rtlogplayer requires ``rtctree 3.0`` and ``rtshell 3.0``. It also
requires the Python version of ``OpenRTM-aist-1.0``.


Installation
============

There are several methods of installation available:

 1. Download the source from either the repository (see "Repository,"
 below) or a source archive, extract it somewhere, and install it into
 your Python distribution:

   a) Extract the source, e.g. to a directory /home/blag/src/rtlogplayer

   b) Run setup.py to install rtlogplayer to your default Python
   installation::

      $ python setup.py install

   c) If necessary, set environment variables. These should be set by
   default, but if not you will need to set them yourself. On Windows,
   you will need to ensure that your Python site-packages directory is
   in the PYTHONPATH variable and the Python scripts directory is in the
   PATH variable.  Typically, these will be something like
   ``C:\Python26\Lib\site-packages\`` and ``C:\Python26\Scripts\``,
   respectively (assuming Python 2.6 installed in ``C:\Python26\``).

 2. Use the Windows installer. This will perform the same job as running
 setup.py (see #2), but saves opening a command prompt. You may still
 need to add paths to your environment variables (see step c, above).


Repository
==========

The latest source is stored in a Git repository at github, available at
``http://github.com/gbiggs/rtlogplayer``. You can download it as a zip
file or tarball by clicking the "Download Source" link in the top right
of the page.  Alternatively, use Git to clone the repository. This is
better if you wish to contribute patches::

  $ git clone git://github.com/gbiggs/rtlogplayer.git


Changelog
=========

