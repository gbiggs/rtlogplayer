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

Facade component - provides a front to create some ports on.

'''

import RTC
import rtshell.gen_comp


class Facade(rtshell.gen_comp.GenComp):
    '''This component does nothing for itself. It is a place-holder to stick
    ports to.'''
    def __init__(self, mgr, port_specs, *args, **kwargs):
        rtshell.gen_comp.GenComp.__init__(self, mgr, port_specs, *args,
                **kwargs)

    def _behv(self, ec_id):
        return RTC.RTC_OK, 0

    def add_conn(self, tgt, chan):
        print tgt
        print chan
        return 1

    @property
    def ports(self):
        return self._ports

