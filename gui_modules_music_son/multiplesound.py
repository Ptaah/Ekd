#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of ekd - Sound module
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

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from music_son_base_sox import choixSonSortieWidget


class selectJoinMultipleSound(QWidget) :
    def __init__(self, exp=1, parent=None) :
      QWidget.__init__(self)
      self.parent=parent
      self.exp=exp
      self.setupUi()

      self.lastdir = os.path.expanduser("~")

      self.connect(self.upSoundFile, SIGNAL("clicked()"), self.setUpFile)
      self.connect(self.downSoundFile, SIGNAL("clicked()"), self.setDownFile)

    def addSoundAction(self, files) :
      for fichier in files :
        if not len(self.lstSoundFile.findItems(fichier, Qt.MatchExactly)) > 0 :
          self.lstSoundFile.addItem(fichier)
      self.checkValid()

    def checkValid(self) :
      if self.lstSoundFile.count() > 0 :
        self.parent.boutApp.setEnabled(True)
      else :
        self.parent.boutApp.setEnabled(False)

    def setUpFile(self) :
      z = self.lstSoundFile.currentRow()
      if z > 0 :
        self.lstSoundFile.insertItem(z-1,QListWidgetItem(self.lstSoundFile.takeItem(z)))
        self.lstSoundFile.setCurrentRow(z-1)

    def delFile(self,files) :
      if len(files) == 0 :
        self.lstSoundFile.clear()
      else :
        x=0
        while x < self.lstSoundFile.count() :
          if unicode(self.lstSoundFile.item(x).text()) not in files :
            self.lstSoundFile.takeItem(x)
          x += 1
      self.checkValid()

    def setDownFile(self) :
      z = self.lstSoundFile.currentRow()
      if z < self.lstSoundFile.count()-1 :
        self.lstSoundFile.insertItem(z+1,QListWidgetItem(self.lstSoundFile.takeItem(z)))
        self.lstSoundFile.setCurrentRow(z+1)

    def getListFile(self) :
      if self.lstSoundFile.count() > 0 :
        lst = []
        x = 0
        while x < self.lstSoundFile.count() :
          qsfile = self.lstSoundFile.item(x).text()
          lst.append(unicode(qsfile.toUtf8(),"utf-8"))
          x += 1
        return lst
      else :
        return None

    def getFileExt(self) :
      print self.parent.parent.soxSuppFormat[self.choixFormatAudio.formatSound.currentIndex()]
      return self.parent.parent.soxSuppFormat[self.choixFormatAudio.formatSound.currentIndex()]

    def getNumFile(self) :
      return self.lstSoundFile.count()

    def setupUi(self):
        self.setObjectName("joinmsound")
        verticalLayout_3 = QVBoxLayout()
        verticalLayout_3.setObjectName("verticalLayout_3")
        if self.exp :
            self.choixFormatAudio = choixSonSortieWidget(self.parent.parent.soxSuppFormat)
            verticalLayout_3.addWidget(self.choixFormatAudio)
        self.groupBox_2 = QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lstSoundFile = QListWidget(self.groupBox_2)
        self.lstSoundFile.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.lstSoundFile.setViewMode(QListView.ListMode)
        self.lstSoundFile.setModelColumn(0)
        self.lstSoundFile.setObjectName("lstSoundFile")
        self.horizontalLayout_2.addWidget(self.lstSoundFile)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.upSoundFile = QToolButton(self.groupBox_2)
        self.upSoundFile.setIcon(QIcon(u"Icones"+os.sep+u"haut.png"))
        self.upSoundFile.setObjectName("upSoundFile")
        self.verticalLayout.addWidget(self.upSoundFile)
        self.downSoundFile = QToolButton(self.groupBox_2)
        self.downSoundFile.setIcon(QIcon(u"Icones"+os.sep+u"bas.png"))
        self.downSoundFile.setObjectName("downSoundFile")
        self.verticalLayout.addWidget(self.downSoundFile)
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        verticalLayout_3.addWidget(self.groupBox_2)
        self.setLayout(verticalLayout_3)
        self.retranslateUi()

    def setTitleAndTips(self, text1, text2=None) :
        if text2==None : text2 = text1
        self.groupBox_2.setTitle(text1)
        self.lstSoundFile.setToolTip(text2)


    def retranslateUi(self):
        self.groupBox_2.setTitle(_(u"Liste des fichiers à joindre"))
        self.lstSoundFile.setToolTip(_(u"Liste des fichiers son à joindre. <b>Pour information, vous pouvez monter et déscendre les fichiers grâce à la flèche haut et bas (les fichiers apparaissant en haut de la liste sont ceux qui seront au début du montage).</b>"))
        self.upSoundFile.setToolTip(_(u"Monter la ligne sélectionnée"))
        self.upSoundFile.setText(_(u"..."))
        self.downSoundFile.setToolTip(_(u"Descendre la ligne sélectionnée"))
        self.downSoundFile.setText(_(u"..."))

