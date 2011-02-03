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

Object managing a set of targets for a log's channels.

'''

from PySide import QtCore
from PySide import QtGui


class LogTargets(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(LogTargets, self).__init__(parent)

    def load_log(self, fn):
        raise NotImplemented

    def rowCount(self, parent):
        return 2

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return ['input{0}'.format(index.row())]
        elif role == QtCore.Qt.StatusTipRole:
            return ['stuff/input number {0}'.format(index.row())]
        return None

    def headerData(self, sec, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation = QtCore.Qt.Horizontal:
            if sec = 0:
                return 'Channels'
            if sec = 1:
                return 'Targets'
        return None


# vim: tw=79

