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

Log information dialog.

'''


import os
from PySide import QtCore
from PySide import QtGui
import time


class LogInfoDlg(QtGui.QDialog):
    def __init__(self, log, filename, parent=None):
        super(LogInfoDlg, self).__init__(parent)
        self._make_widgets(log, filename)
        self.setWindowTitle(self.tr('Log information'))

    def _make_widgets(self, log, filename):
        top_layout = QtGui.QVBoxLayout()

        statinfo = os.stat(filename)
        size = statinfo.st_size
        if size > 1024 * 1024 * 1024: # GiB
            size_str = '{0:.2f}GiB ({1}B)'.format(size / (1024.0 * 1024 * 1024), size)
        elif size > 1024 * 1024: # MiB
            size_str = '{0:.2f}MiB ({1}B)'.format(size / (1024.0 * 1024), size)
        elif size > 1024: # KiB
            size_str = '{0:.2f}KiB ({1}B)'.format(size / 1024.0, size)
        else:
            size_str = '{0}B'.format(size)

        start_time, channels = log.metadata
        open_bold = '<html><b>'
        close_bold = '</b></html>'
        form = QtGui.QFormLayout()
        fn_lbl = QtGui.QLabel(filename)
        form.addRow(open_bold + self.tr('File name:') + close_bold, fn_lbl)
        start_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                time.localtime(start_time))
        start_lbl = QtGui.QLabel(start_time_str + ' ({0})'.format(start_time))
        form.addRow(open_bold + self.tr('Start time:') + close_bold, start_lbl)
        first_ind, first_time = log.start
        first_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                time.localtime(first_time.float))
        first_lbl = QtGui.QLabel(first_time_str + ' ({0})'.format(first_time))
        form.addRow(open_bold + self.tr('First entry time:') + close_bold,
                first_lbl)
        end_ind, end_time = log.end
        end_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                time.localtime(end_time.float))
        end_lbl = QtGui.QLabel(end_time_str + ' ({0})'.format(end_time))
        form.addRow(open_bold + self.tr('Last entry time:') + close_bold,
                end_lbl)
        num_lbl = QtGui.QLabel(str(end_ind + 1))
        form.addRow(open_bold + self.tr('Number of entries:') + close_bold,
                num_lbl)
        top_layout.addLayout(form)

        chan_lbl = QtGui.QLabel(open_bold + self.tr('Channels') + close_bold)
        top_layout.addWidget(chan_lbl)

        chan_mdl = ChannelModel(channels)
        chans = QtGui.QTreeView()
        chans.setObjectName('ChanInfo')
        chans.setHeaderHidden(True)
        chans.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        chans.setModel(chan_mdl)
        top_layout.addWidget(chans)

        close_layout = QtGui.QHBoxLayout()
        close_layout.addStretch()
        close_btn = QtGui.QPushButton(self.tr('Close'))
        close_btn.setObjectName('InfoCloseBtn')
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        close_layout.addStretch()
        top_layout.addLayout(close_layout)

        self.setLayout(top_layout)


class ChannelModel(QtCore.QAbstractItemModel):
    def __init__(self, chans, parent=None):
        super(ChannelModel, self).__init__(parent)
        self._load_chans(chans)

    def _load_chans(self, chans):
        self._channels = []
        for c in chans:
            self._channels.append(Channel(c))

    def columnCount(self, parent):
        return 1

    def index(self, row, col, parent):
        if not parent.isValid():
            # Root
            return self.createIndex(row, col, self._channels[row])
        elif type(parent.internalPointer()) == Channel:
            # Channel
            chan = parent.internalPointer()
            if row == 0:
                return self.createIndex(row, col, chan.datatype)
            elif row == 1:
                return self.createIndex(row, col, chan.source)
            else:
                return QtCore.QModelIndex()
        else:
            # Channel info row - no children
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            # Root
            return QtCore.QModelIndex()
        elif type(index.internalPointer()) == Channel:
            # Channel
            return QtCore.QModelIndex()
        else:
            # Channel item
            chan = index.internalPointer().parent
            return self.createIndex(self._channels.index(chan), 1, chan)

    def rowCount(self, parent):
        if not parent.isValid():
            # Root
            return len(self._channels)
        elif type(parent.internalPointer()) == Channel:
            # Channels always have 2 rows
            return 2
        else:
            return 0

    def data(self, index, role):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return None
        if type(index.internalPointer()) == Channel:
            return index.internalPointer().name.val
        else:
            return index.internalPointer().val


class Channel(object):
    def __init__(self, chan):
        self._name = ChanVal(chan.name, self)
        self._datatype = ChanVal(chan.type_name, self)
        self._source = ChanVal(chan.raw, self)

    def __str__(self):
        return '{0}/{1}'.format(self.name.val, self.datatype.val)

    @property
    def datatype(self):
        return self._datatype

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source


class ChanVal(object):
    def __init__(self, val, parent):
        self._val = val
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    @property
    def val(self):
        return self._val

