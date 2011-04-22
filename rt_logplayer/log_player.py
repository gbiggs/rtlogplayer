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
import sys
import time
import traceback


class LogPlayer(QtCore.QThread):
    NO_CHANGE = 0
    STOP = 1
    JUMP = 2
    # Signals
    finished = QtCore.Signal()
    pos_update = QtCore.Signal(int)

    def __init__(self, log, facade, rate=1.0, parent=None):
        super(LogPlayer, self).__init__(parent)
        self._l = log
        self._c = facade
        self._rate = 1.0
        self._start, port_specs = log.metadata
        self._m = QtCore.QMutex()
        # When True, run() will exit
        self._stop = False
        # When True, the position has been changed (e.g. rewind)
        self._jump = False

    def rewind(self):
        self._m.lock()
        self._l.seek(timestamp=self._l.start[1])
        self._jump = True
        self._m.unlock()
        self.pos_update.emit(self._cur_pos().float)

    def skip_back(self):
        new_pos = self._cur_pos().float - 60
        if new_pos < self._l.start[1].float:
            new_pos = self._l.start[1].float
        self._m.lock()
        self._l.seek(timestamp=new_pos)
        self._jump = True
        self._m.unlock()
        self.pos_update.emit(self._cur_pos().float)

    def skip_forward(self):
        new_pos = self._cur_pos().float + 60
        if new_pos > self._l.end[1].float:
            new_pos = self._l.end[1].float
        self._m.lock()
        self._l.seek(timestamp=new_pos)
        self._jump = True
        self._m.unlock()
        self.pos_update.emit(self._cur_pos().float)

    def skip_to(self, new_pos):
        self._m.lock()
        self._l.seek(timestamp=new_pos)
        self._jump = True
        self._m.unlock()
        self.pos_update.emit(self._cur_pos().float)

    def stop(self):
        self._m.lock()
        self._stop = True
        self._m.unlock()

    def run(self):
        try:
            # Get ready to play
            self._jump = False
            self._stop = False
            self._update_times()
            # "Play it again, Sam." is a misquotation.
            while True:
                # Calculate the current time in log-time
                now = (((time.time() - self._start_time) * self._rate) +
                        self._play_start)
                while self._cur_pos() <= now:
                    if (now - self._last_pos_update) > 0.5:
                        self._last_pos_update = self._cur_pos().float - self._start
                        self.pos_update.emit(self._cur_pos().float)
                    if not self._play_one_entry():
                        # End of log
                        self.finished.emit()
                        return
                # Check flags
                flags = self._check_flags()
                if flags == self.STOP:
                    # A stop flag was set
                    self.pos_update.emit(self._l.end[1].float)
                    return
                elif flags == self.JUMP:
                    # The user has changed the log position
                    self._update_times()
                else:
                    # Sleep until the next entry
                    if not self._wait_for_next():
                        self.pos_update.emit(self._l.end[1].float)
                        return
        except:
            traceback.print_exc()

    def _check_flags(self):
        res = self.NO_CHANGE
        self._m.lock()
        if self._stop:
            self._stop = False
            res = self.STOP
        elif self._jump:
            self._jump = False
            res = self.JUMP
        self._m.unlock()
        return res

    def _cur_pos(self):
        self._m.lock()
        res = self._l.pos[1]
        self._m.unlock()
        return res

    def _play_one_entry(self):
        # Read the next entry from the log file
        self._m.lock()
        entries = self._l.read()
        self._m.unlock()
        #print 'Playing entry {0}'.format(entries)
        if len(entries) == 0:
            # End of log
            return False
        index, ts, entry = entries[0]
        p_name, data = entry
        self._c.ports[p_name].port.write(data)
        return True

    def _update_times(self):
        self._play_start = self._cur_pos().float
        self._start_time = time.time()
        self._offset = self._start_time - self._play_start
        self._last_pos_update = self._cur_pos().float - self._start
        self.pos_update.emit(self._cur_pos().float)

    def _wait_for_next(self):
        # Calculate the current time in log-time
        now = (((time.time() - self._start_time) * self._rate) +
                self._play_start)
        sleep_time = (self._cur_pos().float - now) * 1e6 # Convert to microseconds
        #print 'Sleep time is {0}'.format(sleep_time)
        if sleep_time <= 0:
            return
        # Sleep
        SLEEP_PERIOD = 1e6
        #print 'Starting sleep at {0}'.format(time.time())
        while sleep_time > 0:
            if sleep_time < SLEEP_PERIOD:
                self.usleep(sleep_time)
            else:
                self.usleep(SLEEP_PERIOD) # Sleep for a tenth of a second
            sleep_time -= SLEEP_PERIOD
            # Check flags
            flags = self._check_flags()
            if flags == self.STOP:
                #print 'Sleep broken by stop at {0}'.format(time.time())
                return False
            elif flags == self.JUMP:
                self._update_times()
                #print 'Sleep broken by jump at {0}'.format(time.time())
                return True
        #print 'Sleep done at {0}'.format(time.time())
        return True


# vim: tw=79

