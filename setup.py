#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtlogplayer

Copyright (C) 2011
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

rtlogplayer install script.

'''


from distutils.core import setup


setup(name='rtlogplayer',
      version='1.0.0',
      description='GUI player for rtlog files.',
      long_description='GUI player for OpenRTM-aist, supporting rtlog files.',
      author='Geoffrey Biggs',
      author_email='git@killbots.net',
      url='http://github.com/gbiggs/rtlogplayer',
      license='EPL',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: EPL License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          ],
      packages=['rt_logplayer'],
      scripts=['rtlogplayer']
      )


# vim: tw=79

