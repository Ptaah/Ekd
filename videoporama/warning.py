# -*- coding: utf-8 -*-
# This file is part of ekd - diaporama video module - This module is an integration of videoporama
# Videoporama is a program to make diaporama export in video file
# Copyright (C) 2007-2009  Olivier Ponchaut <opvg@edpnet.be>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Form implementation generated from reading ui file 'warning.ui'
#
# Created: Wed Sep  3 07:40:28 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_warning(object):
    def setupUi(self, warning):
        warning.setObjectName("warning")
        warning.resize(427, 120)
        self.closeb = QtGui.QPushButton(warning)
        self.closeb.setGeometry(QtCore.QRect(300, 80, 120, 30))
        self.closeb.setObjectName("closeb")
        self.texte = QtGui.QLabel(warning)
        self.texte.setGeometry(QtCore.QRect(10, 11, 411, 60))
        self.texte.setFrameShape(QtGui.QFrame.Box)
        self.texte.setWordWrap(False)
        self.texte.setObjectName("texte")

        self.retranslateUi(warning)
        QtCore.QMetaObject.connectSlotsByName(warning)

    def retranslateUi(self, warning):
        warning.setWindowTitle(QtGui.QApplication.translate("warning", "Warning", None, QtGui.QApplication.UnicodeUTF8))
        self.closeb.setText(QtGui.QApplication.translate("warning", "Clo&se", None, QtGui.QApplication.UnicodeUTF8))
        self.closeb.setShortcut(QtGui.QApplication.translate("warning", "Alt+S", None, QtGui.QApplication.UnicodeUTF8))
        self.texte.setText(QtGui.QApplication.translate("warning", "warning", None, QtGui.QApplication.UnicodeUTF8))

