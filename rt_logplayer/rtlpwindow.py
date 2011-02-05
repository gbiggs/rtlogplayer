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

Main window implementation.

'''


import math
from PySide import QtCore
from PySide import QtGui
import rtctree

import ilog
import log_targets
import simpkl_log
import rtctree_mdl


class RTLPWindow(QtGui.QMainWindow):
    NO_FILE = 1
    STOPPED = 2
    PLAYING = 3

    def __init__(self, parent=None):
        super(RTLPWindow, self).__init__(parent)
        self._log = None
        self._log_targets = None
        self._tree = None
        self.setWindowTitle('RTLogPlayer')
        self.setObjectName('RTLogPlayer')
        self._make_actions()
        self._make_status_bar()
        self._make_widgets()
        self.resize(600, 300)
        self._update_timeline()

    def _make_actions(self):
        self._open_act = QtGui.QAction(self.tr('&Open log'), self)
        self._open_act.setShortcuts(QtGui.QKeySequence.Open)
        self._open_act.setStatusTip(self.tr('Open a log file'))
        self._open_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_DialogOpenButton))
        self._open_act.triggered.connect(self._open_log)

        self._close_act = QtGui.QAction(self.tr('&Close log'), self)
        self._close_act.setShortcuts(QtGui.QKeySequence.Close)
        self._close_act.setStatusTip(self.tr('Close the log file'))
        self._close_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_DialogCloseButton))
        self._close_act.triggered.connect(self._close_log)
        self._close_act.setEnabled(False)

        self._exit_act = QtGui.QAction(self.tr('E&xit'), self)
        self._exit_act.setShortcuts(QtGui.QKeySequence.Quit)
        self._exit_act.setStatusTip(self.tr('Exit RTLogPlayer'))
        self._exit_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_MessageBoxCritical))
        self._exit_act.triggered.connect(self.close)

        self._log_info_act = QtGui.QAction(self.tr('Log &Information'), self)
        self._log_info_act.setShortcuts([QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_I)])
        self._log_info_act.setStatusTip(self.tr('View log information'))
        self._log_info_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_MessageBoxInformation))
        self._log_info_act.triggered.connect(self._show_log_info)
        self._log_info_act.setEnabled(False)

        self._add_ns_act = QtGui.QAction(self.tr('&Add name server'), self)
        self._add_ns_act.setShortcuts([QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_A)])
        self._add_ns_act.setStatusTip(self.tr('Add a name server to the RTC '
            'Tree'))
        self._add_ns_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_FileDialogNewFolder))
        self._add_ns_act.triggered.connect(self._add_ns)

        self._rem_ns_act = QtGui.QAction(self.tr('&Remove name server'), self)
        self._rem_ns_act.setShortcuts([QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_R)])
        self._rem_ns_act.setStatusTip(self.tr('Remove a name server from the '
            'RTC Tree'))
        self._rem_ns_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_DialogCloseButton))
        self._rem_ns_act.triggered.connect(self._rem_ns)
        self._rem_ns_act.setEnabled(False)

        self._tb = self.addToolBar(self.tr('Log'))
        self._tb.setObjectName('Toolbar')
        self._tb.addAction(self._open_act)
        self._tb.addAction(self._close_act)
        self._tb.addAction(self._log_info_act)
        self._tb.addSeparator()
        self._tb.addAction(self._add_ns_act)
        self._tb.addAction(self._rem_ns_act)
        self._tb.addSeparator()
        self._tb.addAction(self._exit_act)
        self._tb.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self._tb)

    def _make_status_bar(self):
        sb = self.statusBar()
        self._sb_time = QtGui.QLabel()
        self._sb_time.setObjectName('StatBarTime')
        self._sb_time.setText('No log')
        self._sb_lst_info = QtGui.QLabel()
        self._sb_lst_info.setObjectName('StatBarLstInfo')
        sb.addWidget(self._sb_time)

    def _make_widgets(self):
        central = QtGui.QWidget(self)
        vbox = QtGui.QVBoxLayout(central)

        # Timeline
        row = QtGui.QHBoxLayout()
        self._start_lbl = QtGui.QLabel('0')
        self._start_lbl.setAlignment(QtCore.Qt.AlignRight |
                QtCore.Qt.AlignVCenter)
        row.addWidget(self._start_lbl)
        self._tl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self._tl.setObjectName('Timeline')
        self._tl.setTickPosition(QtGui.QSlider.TicksBelow)
        self._tl.setSingleStep(1)
        self._tl.setPageStep(60)
        self._tl.setEnabled(False)
        self._tl.sliderMoved.connect(self._scan)
        self._tl.sliderReleased.connect(self._skip_to)
        row.addWidget(self._tl)
        self._end_lbl = QtGui.QLabel('0')
        row.addWidget(self._end_lbl)
        vbox.addLayout(row)

        # Playback control
        row = QtGui.QHBoxLayout()
        row.addStretch()
        self._rewind_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_MediaSkipBackward), '')
        self._rewind_btn.setObjectName('RewindBtn')
        self._rewind_btn.setStatusTip(self.tr('Rewind to the start'))
        self._rewind_btn.clicked.connect(self._rewind)
        self._rewind_btn.setEnabled(False)
        row.addWidget(self._rewind_btn)
        self._skip_back_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_MediaSeekBackward), '')
        self._skip_back_btn.setObjectName('SkipBackBtn')
        self._skip_back_btn.setStatusTip(self.tr('Skip backwards 60s'))
        self._skip_back_btn.clicked.connect(self._skip_back)
        self._skip_back_btn.setEnabled(False)
        row.addWidget(self._skip_back_btn)
        self._play_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_MediaPlay), '')
        self._play_btn.setObjectName('PlayBtn')
        self._play_btn.setShortcut(QtGui.QKeySequence(
            QtCore.Qt.Key_Space))
        self._play_btn.setStatusTip(self.tr('Start playback'))
        self._play_btn.clicked.connect(self._playpause)
        self._play_btn.setEnabled(False)
        row.addWidget(self._play_btn)
        self._skip_fwd_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_MediaSeekForward), '')
        self._skip_fwd_btn.setObjectName('SkipFwdBtn')
        self._skip_fwd_btn.setStatusTip(self.tr('Skip forwards 60s'))
        self._skip_fwd_btn.clicked.connect(self._skip_fwd)
        self._skip_fwd_btn.setEnabled(False)
        row.addWidget(self._skip_fwd_btn)
        self._stop_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_MediaPause), '')
        self._play_btn.setObjectName('StopBtn')
        self._stop_btn.setStatusTip(self.tr('Stop playback'))
        self._stop_btn.clicked.connect(self._stop)
        self._stop_btn.setEnabled(False)
        row.addWidget(self._stop_btn)
        row.addStretch()
        vbox.addLayout(row)

        # Target display
        row = QtGui.QHBoxLayout()
        col = QtGui.QVBoxLayout()
        tree_lbl = QtGui.QLabel(self.tr('RTC Tree'))
        col.addWidget(tree_lbl)
        self._tree_view = QtGui.QTreeView()
        self._tree_view.setObjectName('RTCTreeView')
        self._tree_view.setMouseTracking(True)
        col.addWidget(self._tree_view)
        row.addLayout(col)
        col = QtGui.QVBoxLayout()
        col.addStretch()
        self._add_tgt_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_ArrowRight), '')
        self._add_tgt_btn.setObjectName('AddTgtBtn')
        self._add_tgt_btn.setStatusTip(self.tr(
            'Add the selected port as a channel target'))
        self._add_tgt_btn.clicked.connect(self._add_target)
        self._add_tgt_btn.setEnabled(False)
        col.addWidget(self._add_tgt_btn)
        self._rem_tgt_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_ArrowLeft), '')
        self._rem_tgt_btn.setObjectName('RemTgtBtn')
        self._rem_tgt_btn.setStatusTip(self.tr(
            'Remove the selected channel target'))
        self._rem_tgt_btn.clicked.connect(self._rem_target)
        self._rem_tgt_btn.setEnabled(False)
        col.addWidget(self._rem_tgt_btn)
        col.addStretch()
        row.addLayout(col)
        # Channel display
        col = QtGui.QVBoxLayout()
        chan_lbl = QtGui.QLabel(self.tr('Channels'))
        col.addWidget(chan_lbl)
        self._chan_view = QtGui.QTreeView()
        self._chan_view.setObjectName('ChanView')
        self._chan_view.setMouseTracking(True)
        col.addWidget(self._chan_view)
        row.addLayout(col)
        vbox.addLayout(row)

        self.setCentralWidget(central)

    def _enable_ui(self, mode):
        if mode == self.NO_FILE:
            self._open_act.setEnabled(True)
            self._close_act.setEnabled(False)
            self._log_info_act.setEnabled(False)
            self._mng_tgts_act.setEnabled(False)
            self._add_tgt_btn.setEnabled(False)
            self._rem_tgt_btn.setEnabled(False)
            self._play_btn.setEnabled(False)
            self._stop_btn.setEnabled(False)
            self._skip_back_btn.setEnabled(False)
            self._skip_fwd_btn.setEnabled(False)
            self._rewind_btn.setEnabled(False)
            self._tl.setEnabled(False)
        elif mode == self.STOPPED:
            self._open_act.setEnabled(False)
            self._close_act.setEnabled(True)
            self._log_info_act.setEnabled(True)
            self._mng_tgts_act.setEnabled(True)
            self._play_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._skip_back_btn.setEnabled(True)
            self._skip_fwd_btn.setEnabled(True)
            self._rewind_btn.setEnabled(True)
            self._tl.setEnabled(True)
        elif mode == self.PLAYING:
            self._open_act.setEnabled(False)
            self._close_act.setEnabled(True)
            self._log_info_act.setEnabled(True)
            self._mng_tgts_act.setEnabled(True)
            self._play_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            self._skip_back_btn.setEnabled(True)
            self._skip_fwd_btn.setEnabled(True)
            self._rewind_btn.setEnabled(True)
            self._tl.setEnabled(True)

    def _add_ns(self):
        print 'Add name server'

    def _rem_ns(self):
        print 'Remove name server'

    def _sel_channel(self, index):
        self._tgt_lst.setModel(self._log_targets)
        self._tgt_lst.setRootIndex(index)
        self._tgt_lst.clearSelection()
        self._add_tgt_btn.setEnabled(True)
        self._rem_tgt_btn.setEnabled(False)

    def _sel_tgt(self, index):
        self._rem_tgt_btn.setEnabled(True)

    def _update_timeline(self):
        if self._log:
            start = int(math.floor(0))
            end = int(math.ceil(self._log.end[1].float -
                self._log.start[1].float))
        else:
            start = 0
            end = 0
        self._start_lbl.setText('{0}'.format(start))
        self._end_lbl.setText('{0}'.format(end))
        self._tl.setMinimum(start)
        self._tl.setMaximum(end)
        self._tl.setTickInterval((end - start) / 15)
        self._tl.setValue(start)

    # Log file management
    def _open_log(self):
        '''Open a log file.'''
        #fn = QtGui.QFileDialog.getOpenFileName(parent=self,
            #caption=self.tr('Open log file'),
            #filter=self.tr('OpenRTM log files (*.rtlog)'))
        fn = ['/home/geoff/research/src/rtlogplayer/test.rtlog']
        if not fn[0]:
            return
        self._log = simpkl_log.SimplePickleLog(filename=fn[0], mode='r')
        self._log_targets = log_targets.LogTargets(self._log, parent=self)
        self._tree = rtctree_mdl.RTCTree()
        self._chan_lst.setModel(self._log_targets)
        self._comp_lst.setModel(self._tree)
        self._update_timeline()
        self._enable_ui(self.STOPPED)

    def _close_log(self):
        self._chan_lst.setModel(None)
        self._tgt_lst.setModel(None)
        self._comp_lst.setModel(None)
        self._log_targets = None
        self._log = None
        self._tree = None
        self._update_timeline()
        self._enable_ui(self.NO_FILE)

    def _show_log_info(self):
        '''Show the log file's information.'''
        print 'Show log info'

    # Playback control
    def _playpause(self):
        '''Plays or pauses playback.'''
        print 'Play/pause'
        self._enable_ui(self.PLAYING)

    def _rewind(self):
        '''Rewind the log file.'''
        print 'Rewind'

    def _scan(self, pos):
        '''Show the current scanning position.'''
        self._sb_time.setText('Skip to: {0}'.format(pos))

    def _skip_back(self):
        '''Skip backwards 60 seconds.'''
        print 'Skip backward'

    def _skip_fwd(self):
        '''Skip forwards 60 seconds.'''
        print 'Skip forward'

    def _skip_to(self):
        '''Skip the log to a specified point.'''
        self._sb_time.setText('Log position: {0}'.format(self._tl.value()))

    def _stop(self):
        '''Stop playback.'''
        print 'Stop'
        self._enable_ui(self.STOPPED)

    # Target management
    def _add_target(self):
        '''Add a new channel target.'''
        print 'Add target'

    def _rem_target(self):
        '''Remove a channel target.'''
        print 'Remove target'


# vim: tw=79

