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
    def __init__(self, log, parent=None):
        super(LogTargets, self).__init__(parent)
        self._load_chans(log)

    def _load_chans(self, log):
        start_time, chans = log.metadata
        self._channels = []
        for ii, c in enumerate(chans):
            self._channels.append(Channel(ii, c.name, c.type_name, c.raw))

    def add_target(self, chan, target):
        port = target.internalPointer()
        tgt_row = chan.internalPointer().num_targets
        self.beginInsertRows(chan, tgt_row, tgt_row)
        chan.internalPointer().add_target(port.owner.full_path, port.name)
        self.endInsertRows()

    def rem_target(self, chan, target):
        self.beginRemoveRows(chan, target.row(), target.row())
        chan.internalPointer().rem_target(target.internalPointer())
        self.endRemoveRows()

    def columnCount(self, parent):
        return 1

    def index(self, row, col, parent):
        if not parent.isValid():
            # Root
            return self.createIndex(row, col, self._channels[row])
        elif parent.internalPointer().parent == None:
            # Channel
            if row >= self._channels[parent.row()].num_targets:
                return QtCore.QModelIndex()
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
                return 'Target: ' + index.internalPointer().full
            else:
                # Channel
                chan = index.internalPointer()
                return 'Channel {0}: {1} ({2})'.format(chan.index, chan.name,
                        chan.data_type)
        elif role == QtCore.Qt.ToolTipRole:
            if index.internalPointer().parent:
                # Target
                return index.internalPointer().full
            else:
                # Channel
                chan = index.internalPointer()
                result = 'Channel {0}: {1} (Data type: {2})\nSources:\n'.format(
                        chan.index, chan.name, chan.data_type)
                for s in chan.sources:
                    result += '  ' + s + '\n'
                return result[:-1]
        return None


class Channel(object):
    def __init__(self, index, name, data_type, sources):
        self._index = index
        self._name = name
        self._data_type = data_type
        self._srcs = sources
        self._targets = []

    def __str__(self):
        return self.name + '->' + str(self.targets)

    def add_target(self, path, port):
        self._targets.append(Target(path, port, self))

    def rem_target(self, target):
        self._targets.remove(target)

    @property
    def data_type(self):
        return self._data_type

    @property
    def index(self):
        return self._index

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
    def sources(self):
        return self._srcs

    @property
    def targets(self):
        return self._targets


class Target(object):
    def __init__(self, path, port, parent):
        self._path = path
        self._port = port
        self._parent = parent
        self._short = path[-1] + ':' + port
        if path[0] == '/':
            path = path[1:]
        self._full = '/' + '/'.join(path) + ':' + port

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

