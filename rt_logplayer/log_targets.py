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
        self._channels = []

    def clear(self):
        self.beginRemoveRows()
        self._channels = []
        self.endRemoveRows()

    def load_log(self, fn):
        self.beginInsertRows()
        self.endInsertRows()
        raise NotImplemented

    def columnCount(self, parent):
        if parent.isValid():
            return 
        if self._channels[parent.row].num_targets == 0:
            return 1
        else:
            return 2

    def index(self, row, col, parent):
        

    def parent(self):
        pass

    def rowCount(self, parent):
        if parent.column == 0:
            print 'Returning num channels for rows'
            return len(self._channels)
        else:
            print 'Returning num_targets for rows'
            return self._channels[row].num_targets

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


class Channel:
    def __init__(self, name):
        self._name = name
        self._targets = []

    def add_target(self, target):
        self._targets.append(target)

    def rem_target(self, target):
        self._targets.remove(target)

    @property
    def num_targets(self):
        return len(self._targets)


def Target:
    def __init__(self, path, port, parent):
        self._path = path
        self._port = port
        self.parent = parent
        self.short = path[-1] + ':' + port
        self.full = '/'.join(path) + ':' + port


# vim: tw=79

