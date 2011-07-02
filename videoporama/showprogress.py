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

# Form implementation generated from reading ui file 'showprogress.ui'
#
# Created: Sat Sep  6 12:55:08 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_showprogress(object):
    def setupUi(self, showprogress):
        showprogress.setObjectName("showprogress")
        showprogress.resize(271, 343)
        self.pushButton1 = QtGui.QPushButton(showprogress)
        self.pushButton1.setGeometry(QtCore.QRect(140, 300, 120, 30))
        self.pushButton1.setObjectName("pushButton1")
        self.label1 = QtGui.QLabel(showprogress)
        self.label1.setGeometry(QtCore.QRect(10, 0, 230, 30))
        self.label1.setWordWrap(False)
        self.label1.setObjectName("label1")
        self.progressBar1 = QtGui.QProgressBar(showprogress)
        self.progressBar1.setGeometry(QtCore.QRect(10, 30, 251, 31))
        self.progressBar1.setProperty("value", QtCore.QVariant(0))
        self.progressBar1.setObjectName("progressBar1")
        self.viewimg = QtGui.QGraphicsView(showprogress)
        self.viewimg.setGeometry(QtCore.QRect(10, 100, 252, 189))
        self.viewimg.setObjectName("viewimg")
        self.info = QtGui.QLabel(showprogress)
        self.info.setGeometry(QtCore.QRect(10, 70, 251, 20))
        self.info.setObjectName("info")

        self.retranslateUi(showprogress)
        QtCore.QMetaObject.connectSlotsByName(showprogress)

    def retranslateUi(self, showprogress):
        showprogress.setWindowTitle(QtGui.QApplication.translate("showprogress", "Display progress", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton1.setText(QtGui.QApplication.translate("showprogress", "Clo&se", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton1.setShortcut(QtGui.QApplication.translate("showprogress", "Alt+S", None, QtGui.QApplication.UnicodeUTF8))
        self.label1.setText(QtGui.QApplication.translate("showprogress", "Convert in progress", None, QtGui.QApplication.UnicodeUTF8))

