#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''RTLogPlayer

Copyright (C) 2011
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Thread object that manages the playback of data.

'''


from PySide import QtCore


class LogPlayer(QtCore.QThread):
    def __init__(self, log, parent=None):
        super(LogPlayer, self).__init__(parent)
        self._log = log
        self._m = QtCore.QMutex()
        # When True, run() will exit
        self._stop = False

    def stop(self):
        self._m.lock()
        self._stop = True
        self._m.unlock()

    def run(self):
        # Start the event loop for QTimer support
        self.exec_()
        # Get ready to play
        # Check flags
        if not self._check_flags():
            # A stop flag was set
            return

    def _check_flags(self):
        res = False
        self._m.lock()
        if self._stop:
            res = True
        self._m.unlock()
        return res


# vim: tw=79

