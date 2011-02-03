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
        self._channels = [Channel('chan1'), Channel('channel 2')]
        self._channels[0].add_target(['/', 'localhost', 'blag.rtc'], 'in')
        self._channels[0].add_target(['/', 'otherhost', 'blerg.rtc'], 'out')
        self._channels[1].add_target(['/', 'localhost', 'blorg.rtc'], 'A_port')

    def clear(self):
        self.beginRemoveRows()
        self._channels = []
        self.endRemoveRows()

    def load_log(self, fn):
        self.beginInsertRows()
        self.endInsertRows()
        raise NotImplemented

    def columnCount(self, parent):
        return 1

    def index(self, row, col, parent):
        if not parent.isValid():
            # Root
            return self.createIndex(row, col, self._channels[row])
        elif parent.internalPointer().parent == None:
            # Channel
            return self.createIndex(row, col, self._channels[parent.row()].targets[row])
        else:
            # Target (no children)
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            # Root
            return QtCore.QModelIndex()
        if index.internalPointer().parent:
            # Target
            chan = index.internalPointer().parent
            return self.createIndex(self._channels.index(chan), 0, chan)
        else:
            # Channel
            return QtCore.QModelIndex()

    def rowCount(self, parent):
        if not parent.isValid():
            # Root
            return len(self._channels)
        elif parent.internalPointer().parent:
            # Target
            return 0
        else:
            # Channel
            return self._channels[parent.row()].num_targets

    def data(self, index, role):
        if role == QtCore.Qt.StatusTipRole:
            print 'data', index,
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            if index.internalPointer().parent:
                # Target
                return index.internalPointer().short
            else:
                # Channel
                return index.internalPointer().name
        elif role == QtCore.Qt.StatusTipRole:
            if index.internalPointer().parent:
                # Target
                print index.internalPointer().full
                return index.internalPointer().full
            else:
                # Channel
                print index.internalPointer().name
                return index.internalPointer().name
        return None

    def headerData(self, sec, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if sec == 0:
                return 'Channels'
            if sec == 1:
                return 'Targets'
        return None


class Channel:
    def __init__(self, name):
        self._name = name
        self._targets = []

    def __str__(self):
        return self.name + '->' + str(self.targets)

    def add_target(self, path, port):
        self._targets.append(Target(path, port, self))

    def rem_target(self, path, port):
        self._targets.remove(Target(path, port, self))

    @property
    def name(self):
        return self._name

    @property
    def num_targets(self):
        return len(self._targets)

    @property
    def parent(self):
        return None

    @property
    def targets(self):
        return self._targets


class Target:
    def __init__(self, path, port, parent):
        self._path = path
        self._port = port
        self._parent = parent
        self._short = path[-1] + ':' + port
        self._full = '/'.join(path) + ':' + port

    def __str__(self):
        return self.full

    def __repr__(self):
        return self.full

    @property
    def parent(self):
        return self._parent

    @property
    def short(self):
        return self._short

    @property
    def full(self):
        return self._full


# vim: tw=79

