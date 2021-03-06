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

Model wrapper around the RTC Tree.

'''


from PySide import QtCore
from PySide import QtGui
import rtctree.exceptions
import rtctree.tree


class RTCTree(QtCore.QAbstractItemModel):
    def __init__(self, servers=[], parent=None):
        super(RTCTree, self).__init__(parent)
        self._tree = rtctree.tree.RTCTree(servers=servers)
        self._root = self._tree.get_node(['/'])

    @property
    def tree(self):
        return self._tree

    def add_server(self, server):
        row = len(self._root.children)
        res = None
        self.beginResetModel()
        try:
            self._tree.add_name_server(server)
        except rtctree.exceptions.InvalidServiceError, e:
            res = e.args[0]
        self.endResetModel()
        return res

    def rem_server(self, index):
        node = index.internalPointer()
        row = self._root.children.index(node)
        self.beginResetModel()
        self._root.remove_child(node)
        self.endResetModel()

    def release_orb(self):
        self._tree.give_away_orb()

    def get_path(self, index):
        if not index.isValid():
            return []
        return index.internalPointer().full_path_str

    def _get_port_info(self, port):
        result = '<html>'
        for k in port.properties.keys():
            result += '<b>{0}:</b> {1}<br/>\n'.format(k, port.properties[k])
        return result[:-1] + '</html>'

    def _get_comp_info(self, comp):
        profile_items = [('Category', comp.category),
                         ('Description', comp.description),
                         ('Instance name', comp.instance_name),
                         ('Type name', comp.type_name),
                         ('Vendor', comp.vendor),
                         ('Version', comp.version)]
        if comp.parent:
            profile_items.append(('Parent', comp.parent.name))
        if comp.is_composite:
            if comp.is_composite_member:
                profile_items.append(('Type', 'Composite composite member'))
            else:
                profile_items.append(('Type', 'Composite'))
        elif comp.is_composite_member:
            profile_items.append(('Type', 'Monolithic composite member'))
        else:
            profile_items.append(('Type', 'Monolithic'))
        result = '<html>'
        for item in profile_items:
            result += '<b>{0}:</b> {1}<br/>'.format(item[0], item[1])
        return result[:-1] + '</html>'

    def is_nameserver(self, index):
        if type(index.internalPointer()) == rtctree.nameserver.NameServer:
            return True
        return False

    def is_port(self, index):
        if type(index.internalPointer()) == rtctree.ports.DataInPort:
            return True
        return False

    def columnCount(self, parent):
        return 1

    def index(self, row, col, parent):
        if not parent.isValid():
            # Root -> return a name server
            if row < len(self._root.children):
                return self.createIndex(row, col, self._root.children[row])
            else:
                return QtCore.QModelIndex()
        elif self.is_port(parent):
            # Ports have no children
            return QtCore.QModelIndex()
        elif parent.internalPointer().is_component:
            # Return a port
            if row < len(parent.internalPointer().inports):
                return self.createIndex(row, col,
                    parent.internalPointer().inports[row])
            else:
                # Component without any ports
                return QtCore.QModelIndex()
        else:
            # Must be a directory (nothing else would get rows > 0)
            return self.createIndex(row, col,
                parent.internalPointer().children[row])

    def parent(self, index):
        if not index.isValid():
            # Root
            return QtCore.QModelIndex()
        if self.is_port(index):
            # Port's owner is a component
            port = index.internalPointer()
            return self.createIndex(port.owner.parent.children.index(
                port.owner), 0, port.owner)
        elif index.internalPointer().depth == 1:
            # Name servers have no parent
            return QtCore.QModelIndex()
        else:
            # Must be a node
            node = index.internalPointer()
            parent = node.parent
            grandparent = parent.parent
            return self.createIndex(grandparent.children.index(parent), 0,
                    node.parent)

    def rowCount(self, parent):
        if not parent.isValid():
            # Root
            return len(self._root.children)
        elif self.is_port(parent):
            # Ports have no rows
            return 0
        elif parent.internalPointer().is_component:
            # Return port count
            return len(parent.internalPointer().inports)
        else:
            # Any other node
            return len(parent.internalPointer().children)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return index.internalPointer().name
        elif role == QtCore.Qt.StatusTipRole:
            obj = index.internalPointer()
            if self.is_port(index):
                return '{0}:{1} ({2})'.format(obj.owner.full_path_str, obj.name,
                        obj.properties['dataport.data_type'])
            else:
                return obj.full_path_str
        elif role == QtCore.Qt.ToolTipRole:
            if self.is_port(index):
                return self._get_port_info(index.internalPointer())
            elif index.internalPointer().is_component:
                return self._get_comp_info(index.internalPointer())
            else:
                return index.internalPointer().full_path_str
        return None

