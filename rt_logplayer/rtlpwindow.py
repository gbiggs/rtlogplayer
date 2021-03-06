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
import OpenRTM_aist
from PySide import QtCore
from PySide import QtGui
import RTC
import rtctree.exceptions
import rtctree.utils
import rtshell.comp_mgmt
import rtshell.modmgr
import sys
import time

import facade_comp
import ilog
import log_info
import log_player
import log_targets
import simpkl_log
import rtctree_mdl


class RTLPWindow(QtGui.QMainWindow):
    NO_FILE = 1
    STOPPED = 2
    PLAYING = 3

    def __init__(self, parent=None):
        super(RTLPWindow, self).__init__(parent)
        # Stores the loaded log file
        self._log = None
        self._log_fn = None
        # Plays the log file
        self._log_player = None
        # The model representing channels and targets in the log
        self._log_targets = None
        # The model wrapper for the RTC Tree
        self._tree = None
        # Stores the index of the currently-selected channel
        self._cur_chan = None
        # The module manager
        self._mm = rtshell.modmgr.ModuleMgr()
        # An ever-increasing counter to track connections
        self._id_cnt = 0

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
            QtGui.QStyle.SP_ComputerIcon))
        self._add_ns_act.triggered.connect(self._add_ns)
        self._add_ns_act.setEnabled(False)

        self._rem_ns_act = QtGui.QAction(self.tr('&Remove name server'), self)
        self._rem_ns_act.setShortcuts([QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_R)])
        self._rem_ns_act.setStatusTip(self.tr('Remove a name server from the '
            'RTC Tree'))
        self._rem_ns_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_DialogCloseButton))
        self._rem_ns_act.triggered.connect(self._rem_ns)
        self._rem_ns_act.setEnabled(False)

        self._add_path_act = QtGui.QAction(self.tr('Add &module path'), self)
        self._add_path_act.setShortcuts([QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_M)])
        self._add_path_act.setStatusTip(self.tr('Add a path to the module '
            'search path'))
        self._add_path_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_FileDialogNewFolder))
        self._add_path_act.triggered.connect(self._add_mod_path)

        self._load_mod_act = QtGui.QAction(self.tr('&Load Python module'),
                self)
        self._load_mod_act.setShortcuts([QtGui.QKeySequence(
            QtCore.Qt.CTRL + QtCore.Qt.Key_L)])
        self._load_mod_act.setStatusTip(self.tr('Load a Python module '
            'containing a data type'))
        self._load_mod_act.setIcon(self.style().standardIcon(
            QtGui.QStyle.SP_FileIcon))
        self._load_mod_act.triggered.connect(self._load_mod)

        self._tb = self.addToolBar(self.tr('Log'))
        self._tb.setObjectName('Toolbar')
        self._tb.addAction(self._open_act)
        self._tb.addAction(self._close_act)
        self._tb.addAction(self._log_info_act)
        self._tb.addSeparator()
        self._tb.addAction(self._add_ns_act)
        self._tb.addAction(self._rem_ns_act)
        self._tb.addSeparator()
        self._tb.addAction(self._add_path_act)
        self._tb.addAction(self._load_mod_act)
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
        self._play_btn.clicked.connect(self._play)
        self._play_btn.setEnabled(False)
        row.addWidget(self._play_btn)
        self._stop_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_MediaStop), '')
        self._play_btn.setObjectName('StopBtn')
        self._stop_btn.setStatusTip(self.tr('Stop playback'))
        self._stop_btn.clicked.connect(self._stop)
        self._stop_btn.setEnabled(False)
        row.addWidget(self._stop_btn)
        self._skip_fwd_btn = QtGui.QPushButton(self.style().standardIcon(
            QtGui.QStyle.SP_MediaSeekForward), '')
        self._skip_fwd_btn.setObjectName('SkipFwdBtn')
        self._skip_fwd_btn.setStatusTip(self.tr('Skip forwards 60s'))
        self._skip_fwd_btn.clicked.connect(self._skip_fwd)
        self._skip_fwd_btn.setEnabled(False)
        row.addWidget(self._skip_fwd_btn)
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
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self._tree_view.clicked.connect(self._sel_rtctree)
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
        self._chan_view.setHeaderHidden(True)
        self._chan_view.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self._chan_view.clicked.connect(self._sel_channel)
        col.addWidget(self._chan_view)
        row.addLayout(col)
        vbox.addLayout(row)

        self.setCentralWidget(central)

    def _enable_ui(self, mode):
        if mode == self.NO_FILE:
            self._open_act.setEnabled(True)
            self._close_act.setEnabled(False)
            self._log_info_act.setEnabled(False)
            self._add_ns_act.setEnabled(False)
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
            self._add_ns_act.setEnabled(True)
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
            self._add_ns_act.setEnabled(True)
            self._play_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            self._skip_back_btn.setEnabled(True)
            self._skip_fwd_btn.setEnabled(True)
            self._rewind_btn.setEnabled(True)
            self._tl.setEnabled(True)

    def closeEvent(self, event):
        if self._log:
            self._close_log()
        event.accept()

    def _add_mod_path(self):
        path = QtGui.QFileDialog.getExistingDirectory(self,
            self.tr('Select module path'))
        if path:
            sys.path.insert(0, path)

    def _load_mod(self):
        mod, ok = QtGui.QInputDialog.getText(self, self.tr('Load Python odule'),
                self.tr('Module name:'), text='')
        if not ok:
            return
        self._mm.load_mods_and_poas([mod])

    def _add_ns(self):
        ns, ok = QtGui.QInputDialog.getText(self, self.tr('Add name server'),
                self.tr('Address:'), text='localhost')
        if ok:
            if not self._tree:
                self._make_tree(ns)
            else:
                res = self._tree.add_server(ns)
                if res:
                    QtGui.QMessageBox.warning(self, self.tr('Add name server'),
                        self.tr('Invalid CORBA naming service: '
                            '{0}').format(res))

    def _make_tree(self, servers=[]):
        try:
            self._tree = rtctree_mdl.RTCTree(servers=servers)
        except rtctree.exceptions.InvalidServiceError, e:
            QtGui.QMessageBox.warning(self, self.tr('Load RTC Tree'),
                self.tr('Invalid CORBA naming service: {0}').format(e.args[0]))
            self._tree = None

    def _rem_ns(self):
        ns = self._tree_view.selectedIndexes()[0]
        self._tree.rem_server(ns)

    def _sel_channel(self, index):
        if type(index.internalPointer()) == log_targets.Channel:
            self._cur_chan = index
            self._rem_tgt_btn.setEnabled(False)
            if self._port_selected():
                self._add_tgt_btn.setEnabled(True)
        elif type(index.internalPointer()) == log_targets.Target:
            self._cur_chan = self._log_targets.parent(index)
            self._rem_tgt_btn.setEnabled(True)
            if self._port_selected():
                self._add_tgt_btn.setEnabled(True)
        else:
            self._cur_chan = None
            self._rem_tgt_btn.setEnabled(False)
            self._add_tgt_btn.setEnabled(False)

    def _sel_rtctree(self, index):
        if self._tree.is_port(index) and self._cur_chan:
            self._add_tgt_btn.setEnabled(True)
            self._rem_ns_act.setEnabled(False)
        elif self._tree.is_nameserver(index):
            self._add_tgt_btn.setEnabled(False)
            self._rem_ns_act.setEnabled(True)
        else:
            self._add_tgt_btn.setEnabled(False)
            self._rem_ns_act.setEnabled(False)

    def _port_selected(self):
        sel = self._tree_view.selectedIndexes()
        if not sel:
            return False
        if self._tree.is_port(sel[0]):
            return True
        return False

    def _update_timeline(self):
        if self._log:
            start = self._log.start[1].float
            end = self._log.end[1].float
            self._start_lbl.setText(time.strftime('%Y%m%d\n%H:%M:%S',
                    time.localtime(start)))
            self._end_lbl.setText(time.strftime('%Y%m%d\n%H:%M:%S',
                    time.localtime(end)))
        else:
            start = 0
            end = 0
            self._start_lbl.setText('-')
            self._end_lbl.setText('-')
        self._tl.setMinimum(start)
        self._tl.setMaximum(end)
        self._tl.setTickInterval((end - start) / 15)
        self._tl.setValue(start)

    # Log file management
    def _open_log(self):
        '''Open a log file.'''
        fn = QtGui.QFileDialog.getOpenFileName(parent=self,
            caption=self.tr('Open log file'),
            filter=self.tr('OpenRTM log files (*.rtlog)'))
        if not fn[0]:
            return
        self._log_fn = fn[0]
        self._log = simpkl_log.SimplePickleLog(filename=fn[0], mode='r')
        self._log_targets = log_targets.LogTargets(self._log, parent=self)
        self._chan_view.setModel(self._log_targets)
        self._make_tree()
        self._tree_view.setModel(self._tree)
        self._update_timeline()
        self._setup_player()
        self._set_sb_time('Log position', self._log.start[1].float)
        self._enable_ui(self.STOPPED)

    def _close_log(self):
        self._chan_view.setModel(None)
        self._tree_view.setModel(None)
        self._destroy_player()
        self._log_targets = None
        self._log = None
        self._tree = None
        self._update_timeline()
        self._enable_ui(self.NO_FILE)

    def _show_log_info(self):
        '''Show the log file's information.'''
        info_dlg = log_info.LogInfoDlg(self._log, self._log_fn, parent=self)
        info_dlg.exec_()

    # Playback functionality
    def _make_facade(self, port_specs=[]):
        '''Creates an empty component to provide the ports for playback.'''
        comp_name, self._mgr = rtshell.comp_mgmt.make_comp('rtlp_player',
                self._tree.tree, facade_comp.Facade, port_specs)
        self._comp = rtshell.comp_mgmt.find_comp_in_mgr(comp_name, self._mgr)

    def _del_facade(self):
        '''Deletes the facade component.'''
        self._comp = None
        self._tree.release_orb()
        rtshell.comp_mgmt.shutdown(self._mgr)
        self._mgr = None

    def _setup_player(self):
        '''Creates the facade component and the playback thread.'''
        def to_output(ps):
            ps._input = False

        st, chans = self._log.metadata
        specs = [to_output(c) for c in chans]
        self._make_facade(port_specs=chans)
        self._log_player = log_player.LogPlayer(self._log, self._comp)
        self._log_player.finished.connect(self._playback_done)
        self._log_player.pos_update.connect(self._pos_update)

    def _destroy_player(self):
        '''Stops the playback thread and destroys the facade component.'''
        self._log_player.stop()
        self._log_player.wait()
        self._log_player = None
        self._del_facade()

    def _playback_done(self):
        self._enable_ui(self.STOPPED)

    def _pos_update(self, new_pos):
        self._tl.setValue(new_pos)
        self._set_sb_time('Log position', new_pos)

    def _set_sb_time(self, msg, new_pos):
        self._sb_time.setText('{0}: {1}'.format(msg, time.strftime(
            '%Y%m%d %H:%M:%S', time.localtime(new_pos))))

    # Playback control
    def _play(self):
        '''Starts playback.'''
        self._enable_ui(self.PLAYING)
        self._log_player.start()

    def _rewind(self):
        '''Rewind the log file.'''
        self._log_player.rewind()

    def _scan(self, pos):
        '''Show the current scanning position.'''
        self._set_sb_time('Skip to', pos)

    def _skip_back(self):
        '''Skip backwards 60 seconds.'''
        self._log_player.skip_back()

    def _skip_fwd(self):
        '''Skip forwards 60 seconds.'''
        self._log_player.skip_forward()

    def _skip_to(self):
        '''Skip the log to a specified point.'''
        self._log_player.skip_to(self._tl.value())

    def _stop(self):
        '''Stop playback.'''
        self._log_player.stop()
        self._enable_ui(self.STOPPED)

    # Target management
    def _add_target(self):
        '''Add a new channel target.'''
        # Can only call this function when a port is selected
        tgt = self._tree_view.selectedIndexes()[0]
        # Connect the component
        res, conn_id = self._connect_port(tgt.internalPointer())
        if not res:
            return
        # Update the RTC Tree object's connections list
        tgt.internalPointer().reparse()
        # Add the target to the tree
        self._log_targets.add_target(self._cur_chan, tgt, conn_id)
        self._chan_view.setExpanded(self._cur_chan, True)

    def _rem_target(self):
        '''Remove a channel target.'''
        # Can only call this function when a target is selected
        tgt = self._chan_view.selectedIndexes()[0]
        conn = tgt.internalPointer().port.get_connection_by_id(
                tgt.internalPointer().conn_id)
        conn.disconnect()
        self._log_targets.rem_target(self._cur_chan, tgt)

    def _connect_port(self, tgt):
        '''Make the connection to another component's port.'''
        def find_local_port(name, ports):
            for p in ports:
                if p.get_port_profile().name.split('.')[-1] == name:
                    return p

        props = {'dataport.dataflow_type': 'push',
                'dataport.interface_type': 'corba_cdr',
                'dataport.subscription_type': 'new',
                'dataport.data_type': tgt.properties['dataport.data_type']}
        local_name = self._cur_chan.internalPointer().name
        local_port = find_local_port(local_name, self._comp.get_ports())
        id = '{0}'.format(self._id_cnt)
        self._id_cnt += 1
        prof = RTC.ConnectorProfile(local_name + '_' + tgt.name, id,
                [local_port, tgt.object], rtctree.utils.dict_to_nvlist(props))
        res, connector = local_port.connect(prof)
        if res != RTC.RTC_OK:
            QtGui.QMessageBox.warning(self, self.tr('Add target'),
                    self.tr('Failed to create connection.'))
            return False, 0
        return True, id


# vim: tw=79

