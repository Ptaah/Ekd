#!/usr/bin/python
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

import os
import Image
from __builtin__ import hex as hexp
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from animVideoporamaMan import *
from subprocess import *
from xml.dom import minidom
from xml.dom.minidom import Document
from interface import *
from process import *
from moteur_modules_common.EkdConfig import EkdConfig


class vid_widg(Ui_Videoporama) :
    def __init__(self, verifsformats, parent=None) :
      super(vid_widg, self).__init__(parent)
      self.retranslateUi()
      self.parent=parent
      self.verifsformats = verifsformats
      self.outputfileformat.addItems(self.verifsformats[4])
      z=self.checkfirsttime("o")
      self.home=os.path.expanduser("~")
      self.lastdir=self.home
      self.timeline.horizontalHeader().hide()
      self.timeline.verticalHeader().hide()
      self.timeline.setRowCount(1)
      self.timeline.setRowHeight(0,75)
      self.pfilee=0
      self.saveas=0
      self.index=-1
      self.actionMove_left.setDisabled(True)
      self.actionMove_right.setDisabled(True)
      self.serieBut.setDisabled(True)

      if os.name != 'nt' :
        self.I=EkdConfig.get("videoporamaconfig", "imgmgkdir")
      else :
        self.I=""

     # Chargement des données template
      fo=open(self.templatedir + os.sep +"template_data.idv","r")
      # Import des données template à partir du fichier idv
      self.datat=minidom.parse(fo)
      fo.close()
      self.data=self.datat

      # Create transition list
      self.LstTransi()
      self.typet.addItems(self.lstT)
      self.transiopt.addItem(self.tr("No Option"))
      # Display default values and configs
      self.affichedata(self.templatedir + os.sep + 'template_data.idv')

      sizes=QFontDatabase.standardSizes()
      Ssizes=QStringList()
      for size in sizes :
        Ssizes.append(str(size))
      self.fontSize.insertItems(0,Ssizes)
      self.fontSize.setCurrentIndex(6)
      FD=QFont(self.fontComboBox.currentText(),int(self.fontSize.currentText()))
      self.changeFont(FD)
      bckcol=QPalette()
      bckcol.setColor(QPalette.Base,Qt.black)
      self.fontColor.setPalette(bckcol)

      # Qt SLOT/SIGNAL connection
      self.connect(self.fontColorB,SIGNAL("pressed()"),self.setTextColor)
      self.connect(self.fontComboBox,SIGNAL("currentFontChanged(QFont)"),self.changeFont)
      self.connect(self.bold,SIGNAL("released()"),self.setBold)
      self.connect(self.Italic,SIGNAL("released()"),self.setItalic)
      self.connect(self.Souligne,SIGNAL("released()"),self.setUnderline)
      self.connect(self.textLeft,SIGNAL("pressed()"),self.setTextLeft)
      self.connect(self.textCenter,SIGNAL("pressed()"),self.setTextCenter)
      self.connect(self.textRight,SIGNAL("pressed()"),self.setTextRight)
      self.connect(self.addText,SIGNAL("pressed()"),self.addTextToImage)
      self.connect(self.updateText,SIGNAL("pressed()"),self.updateTextImage)
      self.connect(self.deleteText,SIGNAL("pressed()"),self.deleteTextImage)
      self.connect(self.emptyText,SIGNAL("pressed()"),self.emptyTextf)
      self.connect(self.fontSize,SIGNAL("currentIndexChanged(QString)"),self.changeSizeFont)
      self.connect(self.timeline,SIGNAL("itemSelectionChanged()"),self.selectionListe)
      self.connect(self.textEdit,SIGNAL("currentCharFormatChanged(QTextCharFormat)"),self.updateFont)
      self.connect(self.typet,SIGNAL("currentIndexChanged(int)"),self.chgTrOption)
      self.connect(self.transiopt,SIGNAL("currentIndexChanged(int)"),self.chgopttransi)
      self.connect(self.time,SIGNAL("valueChanged(int)"),self.chtime)
      self.connect(self.actionMove_right,SIGNAL("pressed()"),self.up)
      self.connect(self.actionMove_left,SIGNAL("pressed()"),self.down)
      self.connect(self.speedt,SIGNAL("activated(int)"),self.choixspeedt)
      self.connect(self.bgcolor,SIGNAL("lostFocus()"),self.chbgcolor)
      self.connect(self.bgfile,SIGNAL("lostFocus()"),self.chbgfile)
      self.connect(self.bgcolora,SIGNAL("clicked()"),self.setBgcolor)
      self.connect(self.soundfile,SIGNAL("lostFocus()"),self.chsndfile)
      self.connect(self.bgfilea,SIGNAL("clicked()"),self.setBgfile)
      self.connect(self.soundfilea,SIGNAL("clicked()"),self.sndfilea)
      self.connect(self.startZoomSize,SIGNAL("valueChanged(int)"),self.startZoomSizeA)
      self.connect(self.endZoomSize,SIGNAL("valueChanged(int)"),self.endZoomSizeA)
      self.connect(self.option,SIGNAL("currentChanged(int)"),self.setTabZoom)
      self.connect(self.chkZoom,SIGNAL("stateChanged(int)"),self.chkZoomAction)
      self.connect(self.validZoom,SIGNAL("pressed()"),self.validZoomAction)
      self.connect(self.imgformat,SIGNAL("activated(int)"),self.setImgFormat)
      self.connect(self.videof,SIGNAL("activated(int)"),self.choixvideof)
      self.connect(self.outputfileformat,SIGNAL("activated(int)"),self.choixoutputformat)
      self.connect(self.serieBut,SIGNAL("pressed()"),self.serie)


    ### Traduction de l'interface
    def retranslateUi(self):
      self.actionMove_left.setText(self.tr("Left"))
      self.actionMove_left.setToolTip(self.tr("Left"))
      self.actionMove_right.setText(self.tr("Right"))
      self.actionMove_right.setToolTip(self.tr("Right"))
      self.groupBox_6.setTitle(self.tr("Format"))
      self.label_11.setText(self.tr("Image format :"))
      self.imgformat.setItemText(0, self.tr("Normal - 4:3"))
      self.imgformat.setItemText(1, self.tr("Wide - 16:9"))
      self.label_2.setText(self.tr("Video format :"))
      self.videof.setItemText(0, self.tr("PAL (720x576)"))
      self.videof.setItemText(1, self.tr("NTSC (720x480)"))
      self.videof.setItemText(2, self.tr("SECAM (720x576)"))
      self.videof.setItemText(3, self.tr("HD 720"))
      self.videof.setItemText(4, self.tr("HD 1080"))
      self.videof.setItemText(5, self.tr("Web (384x288)"))
      self.videof.setItemText(6, self.tr("640x480"))
      self.label_9.setText(self.tr("Output file format :"))
      self.groupBox_5.setTitle(self.tr("Sound"))
      self.label_8.setText(self.tr("Sound file (wav, ogg, mp3) :"))
      self.soundfilea.setText(self.tr("..."))
      self.option.setTabText(self.option.indexOf(self.tab), self.tr("Montage options"))
      self.groupBox_3.setTitle(self.tr("Image"))
      self.label_3.setText(self.tr("Time display :"))
      self.label_4.setText(self.tr("Background file :"))
      self.bgfilea.setText(self.tr("..."))
      self.label_5.setText(self.tr("Background color :"))
      self.bgcolora.setText(self.tr("..."))
      self.groupBox_4.setTitle(self.tr("Transition"))
      self.label_10.setText(self.tr("Transition speed :"))
      self.speedt.setItemText(0, self.tr("Very slow"))
      self.speedt.setItemText(1, self.tr("Slow"))
      self.speedt.setItemText(2, self.tr("Medium"))
      self.speedt.setItemText(3, self.tr("Medium+"))
      self.speedt.setItemText(4, self.tr("Fast"))
      self.speedt.setItemText(5, self.tr("Very fast"))
      self.label_6.setText(self.tr("Transition type :"))
      self.label_7.setText(self.tr("Transition option :"))
      self.option.setTabText(self.option.indexOf(self.tabimage), self.tr("Image"))
      self.fontColorB.setText(self.tr("..."))
      self.bold.setText(self.tr("Bold"))
      self.bold.setToolTip(self.tr("Bold"))
      self.Italic.setText(self.tr("Italic"))
      self.Italic.setToolTip(self.tr("Italic"))
      self.Souligne.setText(self.tr("Underline"))
      self.Souligne.setToolTip(self.tr("Underline"))
      self.textLeft.setText(self.tr("Text left"))
      self.textCenter.setText(self.tr("Text center"))
      self.textRight.setText(self.tr("Text right"))
      self.addText.setText(self.tr("Add Text"))
      self.textLeft.setToolTip(self.tr("Text left"))
      self.textCenter.setToolTip(self.tr("Text center"))
      self.textRight.setToolTip(self.tr("Text right"))
      self.addText.setToolTip(self.tr("Add Text"))
      self.updateText.setToolTip(self.tr("Update selected text"))
      self.updateText.setText(self.tr("Update text"))
      self.deleteText.setToolTip(self.tr("Delete selected Text"))
      self.deleteText.setText(self.tr("Delete text"))
      self.emptyText.setText(self.tr("Empty"))
      self.emptyText.setToolTip(self.tr("Empty"))
      self.option.setTabText(self.option.indexOf(self.tabtext), self.tr("Text"))
      self.chkZoom.setText(self.tr("Zoom and travel ?"))
      self.validZoom.setText(self.tr("Validate"))
      self.groupBox_7.setTitle(self.tr("Image start"))
      self.label_13.setText(self.tr("Size :"))
      self.label_16.setText(self.tr("%"))
      self.groupBox_8.setTitle(self.tr("Image end"))
      self.label_14.setText(self.tr("Size :"))
      self.label_15.setText(self.tr("%"))
      self.option.setTabText(self.option.indexOf(self.tabzoom), self.tr("Zoom and travel"))
      self.function.setTitle(self.tr("Functions"))
      self.dureelab.setText(self.tr("Total duration :"))
      self.groupBox.setTitle(self.tr("Preview"))

    ### First time open function ###
    def checkfirsttime(self,p) : #OK QT4
      a, b, c, d = 0, 0, 0, 0
      pathname = os.path.dirname (sys.argv[0])
      refdir = os.path.abspath (pathname) + os.sep + u"videoporama" + os.sep + u"template" + os.sep
      if p=="o" :
        self.templatedir=unicode(QDir.homePath()) + os.sep + self.parent.configdir
      else :
        self.templatedir=refdir
      if (not os.path.exists(self.templatedir)) :
        print "Configuration directory doesn't exist"
        print "Create configuration directory at "+self.templatedir
        os.makedirs(self.templatedir)

      if (not os.path.exists(self.templatedir + os.sep + u"template_data.idv")) :
        d=1
        reffile=open(refdir + os.sep +u"template_data.idv","r")
        destfile=open(self.templatedir + os.sep + u"template_data.idv","w")
        destfile.write(reffile.read())
        destfile.close()

      ### check or create temporary dir
      self.T = EkdConfig.getTempDir() + os.sep + u"videoporamatmp"
      if (not os.path.exists(self.T)) :
        os.makedirs(self.T)

      if (c or d) :
        print "Configuration files not find (First time open ?)"
        if (a==c and b==d) :
          return False
        else :
          return True
      else :
        return False


    def setImgFormat(self,imgF) :
      self.updatexml(self.data,"imgformat",imgF)
      self.prjReload()

    def prjReload(self) :
      self.projetfile=self.T+ os.sep +u"tmp.idv"
      self.pfilee=1
      self.saveprojet()
      self.empty()
      self.bgfile.clear()
      self.bgcolor.clear()
      self.soundfile.clear()
      self.pfilee=0
      self.affichedata(self.T+ os.sep +u"tmp.idv")

    def saveprojet(self, urlfile=None): #OK QT4
      if urlfile :
        self.projetfile = urlfile
        self.pfilee=1
      if self.pfilee==0 or self.saveas==1 :
        tmppf=unicode(QFileDialog.getSaveFileName(self,"FileDialog",self.home, "*.idv"))
        if tmppf.endswith(u".idv") :
          self.projetfile=tmppf
        else :
          self.projetfile=tmppf+u".idv"

      b=self.data.getElementsByTagName('inputfile')[0]
      c=b.childNodes
      while b.hasChildNodes() :
        b.removeChild(c[0])
      nitem=self.timeline.columnCount()
      i=0
      doc = Document()
      while i<nitem :
        node=doc.createElement(u"img")
        node.setAttribute(u"transition",unicode(self.timeline.cellWidget(0,i).typet))
        node.setAttribute(u"tr_option",unicode(self.timeline.cellWidget(0,i).opttransi))
        node.setAttribute(u"speedt",unicode(self.timeline.cellWidget(0,i).speedt))
        node.setAttribute(u"time",unicode(self.timeline.cellWidget(0,i).time))
        node.setAttribute(u"bgcolor",unicode(self.timeline.cellWidget(0,i).bgcolor))
        node.setAttribute(u"bgfile",unicode(self.timeline.cellWidget(0,i).bgfile))
        node.setAttribute(u"urlimage",unicode(self.timeline.cellWidget(0,i).urlim))
        print "urlim = "+self.timeline.cellWidget(0,i).urlim
        if self.timeline.cellWidget(0,i).zoom==2 :
          startZoom=self.timeline.cellWidget(0,i).getZoomBoxInfo(1)
          endZoom=self.timeline.cellWidget(0,i).getZoomBoxInfo(0)
          if (startZoom != None and endZoom != None) :
            node.setAttribute(u"zoom",unicode("2"))
            node.setAttribute(u"zoomStart",unicode(startZoom))
            node.setAttribute(u"zoomEnd",unicode(endZoom))
          else :
            node.setAttribute(u"zoom",unicode("0"))

        c=b.appendChild(node)
        for item in self.timeline.cellWidget(0,i).scene.items() :
          if (item.data(0).toString()) == "Texte" :
            tor=doc.createElement(u"ftext")
            tor.setAttribute(u"x",unicode(item.x()))
            tor.setAttribute(u"y",unicode(item.y()))
            tor.setAttribute(u"width",u"310")
            txt=item.toHtml()
            txt.replace(u"<",u"[")
            txt.replace(u">",u"]")
            tor.setAttribute(u"text",unicode(txt))
            d=c.appendChild(tor)
        i=i+1
      try:
        fisa=open(self.projetfile,'w')
        fisa.write(self.data.toxml('utf-8'))
        fisa.close()
        self.pfilee=1
        print "Sauvegarde fichier temporaire OK"
      except:
        print "Erreur ecriture fichier temporaire de sauvegarde"


    def choixvideof(self,txt): #OK QT4
      self.updatexml(self.data,"videof",txt)
      self.displayLenght()
      self.prjReload()

    ### GUI_Main - Display data section ###
    def affichedata(self,xmlfile,n=0, disp=None): #OK QT4
      fo2=open(xmlfile,'r')
      #Import configurations data from xml file
      self.data=minidom.parse(fo2)
      fo2.close()
      # Options display

      # Set sound file
      try:
        self.soundfile.setText(self.data.getElementsByTagName('sndfile')[0].childNodes[0].nodeValue)
      except:
        None
      # Set video format
      try:
        self.videof.setCurrentIndex(int(self.data.getElementsByTagName('videof')[0].childNodes[0].nodeValue))
      except :
        None

      # Set image format
      try:
        self.imgformat.setCurrentIndex(int(self.data.getElementsByTagName('imgformat')[0].childNodes[0].nodeValue))
        self.imgformatd=self.imgformat.currentIndex()
      except:
        self.imgformatd=0

      if self.imgformatd==1 :
        if self.videof.currentIndex()==3 :
          self.imgwidth=1280
          self.imgwidthF=1280
          self.imgheight=720
          self.imgheightF=720
        elif self.videof.currentIndex()==4 :
          self.imgwidth=1920
          self.imgwidthF=1920
          self.imgheight=1080
          self.imgheightF=1080
        elif self.videof.currentIndex()==5 :
          self.imgwidth=512
          self.imgwidthF=384
          self.imgheight=288
          self.imgheightF=288
        elif self.videof.currentIndex()==6 :
          self.imgwidth=640
          self.imgwidthF=640
          self.imgheight=360
          self.imgheightF=480
        else :
          self.imgwidth=1024
          self.imgwidthF=720
          self.imgheight=576
          if self.videof.currentIndex()==1 :
            self.imgheightF=480
          else :
            self.imgheightF=576
      else :
        if self.videof.currentIndex()==3 :
          self.imgwidth=1280
          self.imgwidthF=1280
          self.imgheight=960
          self.imgheightF=720
        elif self.videof.currentIndex()==4 :
          self.imgwidth=1920
          self.imgwidthF=1920
          self.imgheight=1440
          self.imgheightF=1080
        elif self.videof.currentIndex()==5 :
          self.imgwidth=384
          self.imgwidthF=384
          self.imgheight=288
          self.imgheightF=288
        elif self.videof.currentIndex()==6 :
          self.imgwidth=640
          self.imgwidthF=640
          self.imgheight=480
          self.imgheightF=480
        else :
          self.imgwidth=768
          self.imgwidthF=720
          self.imgheight=576
          if self.videof.currentIndex()==1 :
            self.imgheightF=480
          else :
            self.imgheightF=576

      # Set output file format
      try:
        self.outputfileformat.setCurrentIndex(int(self.data.getElementsByTagName('outputf')[0].childNodes[0].nodeValue))
      except:
        None
      # Set file to export the project
      try:
        self.outputfile.setText(self.data.getElementsByTagName('outputfile')[0].childNodes[0].nodeValue)
      except:
        None
      k=0
      listfiles=[]
      for pictfile in self.data.getElementsByTagName('img'):
        try :
          compose=self.DisplayThumb(pictfile.getAttribute("urlimage"),k,
              pictfile.getAttribute("time"),
              pictfile.getAttribute("bgfile"),
              pictfile.getAttribute("bgcolor"),
              pictfile.getAttribute("transition"),
              pictfile.getAttribute("tr_option"),
              pictfile.getAttribute("speedt"))
        except :
          compose=self.DisplayThumb(pictfile.childNodes[0].nodeValue,k,
              "2","","0","0","0","3")

        if pictfile.getAttribute("zoom") == "2" :
          self.timeline.cellWidget(0,k).setZoom()
          self.timeline.cellWidget(0,k).setChkZoom(2)
          start=pictfile.getAttribute("zoomStart").split(":")
          end=pictfile.getAttribute("zoomEnd").split(":")
          self.timeline.cellWidget(0,k).setZoomBox(float(start[0]),float(start[1]),float(start[2]),float(start[3]),1)
          self.timeline.cellWidget(0,k).setZoomBox(float(end[0]),float(end[1]),float(end[2]),float(end[3]),0)
        else :
          self.timeline.cellWidget(0,k).setChkZoom(0)

        for texte in pictfile.getElementsByTagName('ftext') :
          try :
            Txt=QString(unicode(texte.getAttribute("text")))
            Txt.replace(u"[".encode('utf-8'),u"<".encode('utf-8'))
            Txt.replace(u"]".encode('utf-8'),u">".encode('utf-8'))
            text1=QGraphicsTextItem("hello")
            text1.setHtml(Txt)
            Txt=text1.toHtml() # permet d'enlever le paragraphe ajouté et inutile.
            Txt.replace(u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"> </p>'.encode('utf-8'),u"".encode('utf-8'))
            text1.setHtml(Txt)

            text1.setTextWidth(self.timeline.cellWidget(0,k).txtwide)
            text1.scale(self.timeline.cellWidget(0,k).txtzoom,self.timeline.cellWidget(0,k).txtzoom)
            text1.setPos(float(texte.getAttribute("x")),float(texte.getAttribute("y")))
            text1.setZValue(101)
            text1.setAcceptDrops(1)
            text1.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
            data=QVariant("Texte")
            text1.setData(0,data)

            compose.addItem(text1)
          except :
            None
        self.timeline.cellWidget(0,k).updatePix()
        listfiles.append(pictfile.getAttribute("urlimage"))
        k+=1
      if n and disp :
        disp.setFiles(listfiles)
        # Miniatures
        if disp.modeleBase.rowCount() > 0:
          disp.itemNum = 0
          disp.modelPreview = disp.modeleBase
          disp.modeAffichageCommun(disp.listeBase)
          disp.affiche_preview()
      if self.timeline.columnCount() != 0 :
        self.serieBut.setEnabled(True)
      self.displayLenght()

    def delete(self,i): #Different de videoporama
      self.timeline.removeColumn(i)
      self.displayLenght()
      j = self.timeline.columnCount()
      if j == 0 :
        self.serieBut.setDisabled(True)
        self.actionMove_left.setDisabled(True)
        self.actionMove_right.setDisabled(True)


    def chtime(self,val): #OK QT4
      try :
        self.timeline.cellWidget(0,self.index).time=val
        self.displayLenght()
      except :
        None

    def choixspeedt(self,txt): #OK QT4
      try :
        self.timeline.cellWidget(0,self.index).speedt=txt
        self.displayLenght()
      except :
        None

    def getFilesList(self): #Different de videoporama
      filesList=[]
      i=0
      while i <= self.timeline.columnCount() :
        if self.timeline.cellWidget(0,i) != None :
          filesList.append(self.timeline.cellWidget(0,i).urlim)
        i+=1
      return filesList

    def add(self): ##Different de videoporama
      files=QFileDialog.getOpenFileNames(self,"FileDialog",self.lastdir, "Images(*.jpg *.png *.gif *.xpm)")
      self.repaint()
      self.add2(files)

    def add2(self,files) : #Different de videoporama
      try :
        self.lastdir=self.findDir(files[0])
      except :
        None
      try :
        bgf=EkdConfig.get("videoporamaconfig","bgfile")
      except :
        bgf=""
      for file in files :
        k=self.timeline.columnCount()
        if file != u"" :
          self.DisplayThumb(file,k,
            EkdConfig.get("videoporamaconfig","time"),
            bgf,
            int(EkdConfig.get("videoporamaconfig","bgcolor"),16),
            EkdConfig.get("videoporamaconfig","typet"),
            0,
            EkdConfig.get("videoporamaconfig","speedt"))
      if self.timeline.columnCount() != 0 :
        self.serieBut.setEnabled(True)
      self.displayLenght()

    def empty(self): #OK QT4
      i=0
      while i<self.timeline.columnCount() :
        self.timeline.removeColumn(i)
      self.preview.hide()
      self.bgfile.clear()
      self.bgcolor.clear()
      self.displayLenght()
      self.serieBut.setDisabled(True)
      self.actionMove_left.setDisabled(True)
      self.actionMove_right.setDisabled(True)

    def DisplayThumb(self,file,col,time=1,bgfile="",bgcolor=0,typet=0,opttransi=0,speedt=3,zoom=0) : #QT4 OK
      compose=QGraphicsScene()
      compose.setSceneRect(0, 0, self.imgwidth, self.imgheight)
      if bgfile != "" :
        bkgpix = QPixmap(bgfile)
        bgim = compose.addPixmap(bkgpix.scaled(self.imgwidth,self.imgheight,Qt.IgnoreAspectRatio,Qt.SmoothTransformation))
        bgim.setData(0,QVariant(QString("backgroundi")))
      else :
        bgim=compose.addRect(0,0,self.imgwidth,self.imgheight,QPen(Qt.NoPen),QBrush(QColor.fromRgb(int(bgcolor))))
        bgim.setData(0,QVariant(QString("backgroundc")))
      bgim.setZValue(1)
      pix=QPixmap(file)
      im=compose.addPixmap(pix.scaled(self.imgwidth,self.imgheight,Qt.KeepAspectRatio,Qt.SmoothTransformation))
      im.setData(0,QVariant(QString("image")))
      we=im.pixmap().width()
      hi=im.pixmap().height()
      im.setZValue(20)
      im.setPos((self.imgwidth-we)/2,(self.imgheight-hi)/2)

      self.connect(compose,SIGNAL("selectionChanged ()"),self.displayEditText)
      pixl=myLabel(file,compose,col,time,bgfile,bgcolor,typet,opttransi,speedt,self.imgformatd,0,self.videof.currentIndex())
      self.timeline.insertColumn(col)
      self.timeline.setColumnWidth(col,pixl.wpix)
      self.timeline.setCellWidget(0,col,pixl)
      self.repaint()
      return compose

    def findDir(self,urlfile) :
      sl=urlfile.split("/")
      if not sl.isEmpty() :
        sl.removeAt(len(sl)-1)
      dirl=sl.join("/")
      return dirl+"/"

    def up(self): #OK QT4
      if self.index!=(self.timeline.columnCount()-1) :
        i=self.index
        pict=self.timeline.cellWidget(0,i).copy()
        nc=i+2
        self.timeline.insertColumn(nc)
        self.timeline.setColumnWidth(nc,pict.wpix)
        self.timeline.setCellWidget(0,nc,pict)
        self.timeline.removeColumn(i)
        self.timeline.cellWidget(0,i).col=i
        self.timeline.cellWidget(0,(i+1)).col=i+1
        self.timeline.setCurrentCell(0,i+1)

    def down(self): #OK QT4
      if self.index!=0 :
        i=self.index
        pict=self.timeline.cellWidget(0,i).copy()
        b=i+1
        nc=i-1
        self.timeline.insertColumn(nc)
        self.timeline.setColumnWidth(nc,pict.wpix)
        self.timeline.setCellWidget(0,nc,pict)
        self.timeline.removeColumn(b)
        self.timeline.cellWidget(0,i).col=i
        self.timeline.cellWidget(0,nc).col=nc
        self.timeline.setCurrentCell(0,nc)

    def changeFont(self,font) :
      self.textEdit.setFocus()
      self.textEdit.setCurrentFont(font)
      self.setItalic()
      self.setBold()
      self.setUnderline()
      self.changeSizeFont(self.fontSize.currentText())

    def changeSizeFont(self,size) :
      self.textEdit.setFocus()
      self.textEdit.setFontPointSize(int(size))

    def setItalic(self) :
      state=self.Italic.isChecked()
      self.textEdit.setFocus()
      self.textEdit.setFontItalic(state)

    def setBold(self) :
      state=self.bold.isChecked()
      self.textEdit.setFocus()
      if state :
        self.textEdit.setFontWeight(75)
      else :
        self.textEdit.setFontWeight(50)

    def setUnderline(self) :
      state=self.Souligne.isChecked()
      self.textEdit.setFocus()
      self.textEdit.setFontUnderline(state)

    def setTextColor(self) :
      colorb=QColorDialog.getColor(Qt.black,self)
      self.textEdit.setFocus()
      self.textEdit.setTextColor(colorb)
      bckcol=QPalette()
      bckcol.setColor(QPalette.Base,colorb)
      self.fontColor.setPalette(bckcol)

    def setTextLeft(self) :
      if (not self.textLeft.isChecked()) :
        self.textCenter.setChecked(0)
        self.textRight.setChecked(0)
        self.textEdit.selectAll()
        self.textEdit.setAlignment(Qt.AlignLeft)
      else :
        self.textLeft.setChecked(0)

    def setTextCenter(self) :
      self.textLeft.setDown(0)
      self.textCenter.setDown(1)
      self.textRight.setDown(0)
      self.textEdit.selectAll()
      self.textEdit.setAlignment(Qt.AlignCenter)

    def setTextRight(self) :
      self.textLeft.setDown(0)
      self.textCenter.setDown(0)
      self.textRight.setDown(1)
      self.textEdit.selectAll()
      self.textEdit.setAlignment(Qt.AlignRight)

    def addTextToImage(self) :
      try :
        self.preview.setInteractive(True)
        self.preview.setDragMode(QGraphicsView.ScrollHandDrag)
        scene=self.preview.scene()
        text=QGraphicsTextItem()
        text.setHtml(self.textEdit.toHtml())
        text.scale(self.timeline.cellWidget(0,self.index).txtzoom,self.timeline.cellWidget(0,self.index).txtzoom)
        text.setTextWidth(self.timeline.cellWidget(0,self.index).txtwide)
        text.setZValue(101)
        text.setAcceptDrops(1)
        text.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        data=QVariant("Texte")
        text.setData(0,data)
        scene.addItem(text)
        self.timeline.cellWidget(0,self.index).updatePix()
      except :
        None

    def updateTextImage(self) :
      try :
        item = self.timeline.cellWidget(0,self.index).selectItem()
        if item != None :
          item.setHtml(self.textEdit.toHtml())
          self.timeline.cellWidget(0,self.index).updatePix()
      except :
        None

    def deleteTextImage(self) :
      try :
        item = self.timeline.cellWidget(0,self.index).selectItem()
        if item != None :
          self.preview.scene().removeItem(item)
          self.timeline.cellWidget(0,self.index).updatePix()
      except :
        None

    def displayEditText(self) :
      try :
        item = self.timeline.cellWidget(0,self.index).selectItem()
        if item != None :
          self.textEdit.setHtml(item.toHtml())
      except :
        None

    def emptyTextf(self) :
      self.textEdit.clear()

    def rotateText(self,angle) :
      item = self.timeline.cellWidget(0,self.index).selectItem()
      if item != None :
        item.rotate(angle)
        self.timeline.cellWidget(0,self.index).updatePix()

    def updateFont(self,x=0) :
      font=self.textEdit.currentFont()
      self.fontComboBox.setEditText(font.family())
      i=self.fontSize.findText(str(int(font.pointSize())))
      self.fontSize.setCurrentIndex(i)
      self.Italic.setDown(x.fontItalic())
      self.Souligne.setDown(x.fontUnderline())
      if x.fontWeight() >= 63 :
        b=1
      else :
        b=0
      self.bold.setDown(b)

    ### Fonction de base ###
    def LstTransi(self): #QT4 OK
      self.lstT=QStringList()
      self.lstT.append(self.tr("None"))
      self.lstT.append(self.tr("Fade"))
      self.lstT.append(self.tr("Appear"))
      self.lstT.append(self.tr("Disappear"))
      self.lstT.append(self.tr("Slide"))
      self.lstT.append(self.tr("Cube"))
      self.lstT.append(self.tr("Push"))
      self.lstT.append(self.tr("Luma"))

    def chgTrOption(self,index) : #OK QT4
      try :
        z=self.getTrOptionLst(index)
        self.transiopt.clear()
        self.transiopt.addItems(z)
        self.timeline.cellWidget(0,self.index).typet=index
        self.displayLenght()
      except :
        None

    def getTrOptionLst(self,tr) : #OK QT4
      LS=QStringList()
      if tr < 4 :
        LS.append(self.tr("No Option"))
      elif tr >= 4 and tr < 7 :
        LS.append(self.tr("Left2Right"))
        LS.append(self.tr("Right2Left"))
        LS.append(self.tr("Top2Bottom"))
        LS.append(self.tr("Bottom2Top"))
      elif tr == 7 :
        b=os.listdir(os.getcwd()+os.sep+"videoporama/luma/")
        for c in b :
          d=os.path.splitext(c)
          if not d[0].startswith(".") :
            LS.append(d[0])
      return LS

    def displayLenght(self) : #QT4 OK
      self.totimage=0
      if self.videof.currentText()=="NTSC" :
        self.n=1
        imgpsec=30
        ips=float(30000/1001)
      else :
        self.n=0
        imgpsec=25
        ips=imgpsec
      dicspeed={"0":1,"1":2,"2":4,"3":5,"4":10,"5":20}
      speedtrans=dicspeed[str(EkdConfig.get("videoporamaconfig","speedt"))]
      frametransition = 100 / speedtrans
      k=0
      while k<self.timeline.columnCount() :
        self.totimage += self.timeline.cellWidget(0,k).imagetime(self.n)[1]+self.timeline.cellWidget(0,k).imagetime(self.n)[2]
        k+=1
      self.totimage+=frametransition

      sec=float(self.totimage) / ips
      seconde=str(sec % 60).split(".")
      minute=int(sec / 60)
      heure=int(minute / 60)
      timesnd="%s:%s:%s.%s" % (str(heure).rjust(2,'0'),str(minute).rjust(2,'0'),seconde[0].rjust(2,'0'),seconde[1].ljust(3,'0')[0:3])
      self.duration.setText(timesnd)

    def setTabZoom(self,n) :
      if (self.index != -1) :
        image=self.timeline.cellWidget(0,self.index)
        if n==3 :
          scene=image.setZoom()
          self.preview.setScene(scene)
          self.preview.show()
          self.preview.fitInView(scene.sceneRect(),Qt.KeepAspectRatio)
          self.preview.setInteractive(True)
          self.preview.setDragMode(QGraphicsView.ScrollHandDrag)
          self.validZoomAction()
        else :
          self.preview.setScene(image.Qscene())
          self.preview.show()
          self.preview.fitInView(0,0,self.imgwidth,self.imgheight,Qt.KeepAspectRatio)

    def validZoomAction(self) :
      if (self.index != -1) :
        scene=self.preview.scene()
        item=self.timeline.cellWidget(0,self.index).selectZoomBox(1)
        item2=self.timeline.cellWidget(0,self.index).selectZoomBox(0)
        if self.imgformat.currentIndex() == 0 :
          a=120
        else :
          a=90
        dessin=QPixmap(160,a)
        dessin2=QPixmap(160,a)
        if (item != None and item2 != None) :
          item.hide()
          item2.hide()
          scene.render(QPainter(dessin),QRectF(0,0,160,a),item.sceneBoundingRect())
          self.startZoomView.setPixmap(dessin)
          scene.render(QPainter(dessin2),QRectF(0,0,160,a),item2.sceneBoundingRect())
          self.endZoomView.setPixmap(dessin2)
          item.show()
          item2.show()

    def startZoomSizeA(self,zoom) :
      if (self.index != -1) :
        scene=self.preview.scene()
        item=self.timeline.cellWidget(0,self.index).selectZoomBox(1)
        try :
          wcdr=scene.width()*zoom/100
          hcdr=wcdr*self.imgheight/self.imgwidth
          item.setRect(0,0,wcdr,hcdr)
        except :
          None

    def endZoomSizeA(self,zoom) :
      if (self.index != -1) :
        scene=self.preview.scene()
        item=self.timeline.cellWidget(0,self.index).selectZoomBox(0)
        try :
          wcdr=scene.width()*zoom/100
          hcdr=wcdr*self.imgheight/self.imgwidth
          item.setRect(0,0,wcdr,hcdr)
        except :
          None

    def chkZoomAction(self,chk) :
      if (self.index != -1) :
        image=self.timeline.cellWidget(0,self.index)
        image.setChkZoom(chk)
        if (chk==0 and image.selectZoomBox(1)!=None and image.selectZoomBox(0)!=None) :
          image.composeZoom.removeItem(image.selectZoomBox(1))
          image.composeZoom.removeItem(image.selectZoomBox(0))
        else :
          if (image.selectZoomBox(1)==None and image.selectZoomBox(0)==None) :
            wcdr=image.composeZoom.width()*self.startZoomSize.value()/100
            hcdr=wcdr*self.imgheight/self.imgwidth
            image.setZoomBox(0,0,wcdr,hcdr,1)
            wcdr=image.composeZoom.width()*self.endZoomSize.value()/100
            hcdr=wcdr*self.imgheight/self.imgwidth
            image.setZoomBox(0,0,wcdr,hcdr,0)

    def selectionListe(self): # Function to display selected image - QT4 OK
      self.index = self.timeline.currentColumn()
      self.setTabZoom(self.option.currentIndex())
      image=self.timeline.cellWidget(0,self.index)
      try :
        optt=int(image.opttransi)
        self.typet.setCurrentIndex(int(image.typet))
        self.bgcolor.setText(self.colortohex(image.bgcolor))
        self.chbgcolor()
        self.bgfile.setText(image.bgfile)
        self.time.setValue(int(image.time))
        self.speedt.setCurrentIndex(int(image.speedt))
        self.transiopt.setCurrentIndex(optt)
        self.chkZoom.setChecked(image.zoom)
      except :
        None
      if self.index == 0 :
        self.actionMove_left.setDisabled(True)
      else :
        self.actionMove_left.setEnabled(True)
      if self.index == (self.timeline.columnCount()-1) :
        self.actionMove_right.setDisabled(True)
      else :
        self.actionMove_right.setEnabled(True)

    def chbgcolor(self): #OK QT4 !!!
      try :
        c=int(str(self.bgcolor.text()),16)
        self.timeline.cellWidget(0,self.index).bgcolor=c
        bckcol=QPalette()
        bckcol.setColor(QPalette.Base,QColor.fromRgb(c))
        self.bgcolor.setPalette(bckcol)
        self.update_bg_pix()
      except :
        None

    def setBgcolor(self): # OK QT4 !!!

      if self.index == -1 :
        messErr=QMessageBox(self)
        messErr.setText(_(u"<p>Avant de pouvoir sélectionner une couleur de fond, vous devez sélectionner une image dans la ligne du temps</p>"))
        messErr.setWindowTitle(_(u"Erreur"))
        messErr.setIcon(QMessageBox.Warning)
        messErr.exec_()
        
      else :
        if (self.data.getElementsByTagName('bgcolor')[0].childNodes[0].nodeValue != "0") :
          colorb=QColorDialog.getColor(QColor.fromRgb(int(self.data.getElementsByTagName('bgcolor')[0].childNodes[0].nodeValue)),self)
        else :
          colorb=QColorDialog.getColor(self.toqcolor("%s" % self.bgcolor.text()))
        red=colorb.red()
        green=colorb.green()
        blue=colorb.blue()
        xcolor=red*65536+green*256+blue
        try :
          self.timeline.cellWidget(0,self.index).bgcolor=xcolor
        except :
          None
        self.bgcolor.setText(self.colortohex(xcolor))
        self.chbgcolor()

    def update_bg_pix(self) :
      scene=self.timeline.cellWidget(0,self.index).scene
      bgcolor=self.timeline.cellWidget(0,self.index).bgcolor
      bgfile=self.timeline.cellWidget(0,self.index).bgfile
      shapelst=scene.items()
      for shape in shapelst :
        if shape.data(0).toString() == QString("backgroundc") :
          if bgfile == "" :
            # Modifié le 19/11/2009 : Simplification qui marche :)
            #shape.setBrush(QBrush(self.toqcolor(bgcolor)))
            shape.setBrush(QBrush(QColor.fromRgb(int(bgcolor))))
          else :
            scene.removeItem(shape)
            bkgpix = QPixmap(bgfile)
            bgim = scene.addPixmap(bkgpix.scaled(self.imgwidth,self.imgheight,Qt.KeepAspectRatio,Qt.SmoothTransformation))
            bgim.setData(0,QVariant(QString("backgroundi")))
        elif shape.data(0).toString() == QString("backgroundi") :
          if bgfile=="" :
            scene.removeItem(shape)
            bgcol = scene.addRect(0,0,self.imgwidth,self.imgheight,QPen(),QBrush(QColor.fromRgb(int(bgcolor))))
            bgcol.setData(0,QVariant(QString("backgroundc")))
          else :
            bkgpix = QPixmap(bgfile)
            shape.setPixmap(bkgpix.scaled(self.imgwidth,self.imgheight,Qt.KeepAspectRatio,Qt.SmoothTransformation))
      self.timeline.cellWidget(0,self.index).updatePix()

    def colortohex(self,color): #OK QT4 !!!
      r=int(int(color)/65536)
      g=int((int(color)-r*65536)/256)
      b=int(int(color)-r*65536-g*256)
      rr=hexp(r)
      gg=hexp(g)
      bb=hexp(b)
      colorh=unicode(rr.strip("0x").upper().rjust(2,"0")+gg.strip("0x").upper().rjust(2,"0")+bb.strip("0x").upper().rjust(2,"0")).encode('utf-8')
      return colorh

    def toqcolor(self,color): # color doit être un String au format hexa AABBCC !
      qcolor=QColor.fromRgb(int(str(color), 16))
      return qcolor

    def chbgfile(self): #OK QT4
      try :
        self.timeline.cellWidget(0,self.index).bgfile=self.bgfile.text()
        self.update_bg_pix()
      except :
        None

    def setBgfile(self): #OK QT4
      file=QFileDialog.getOpenFileName(self, "FileDialog",self.lastdir, "Images(*.jpg *.png *.gif *.xpm)")
      self.bgfile.setText(file)
      self.lastdir=os.path.split(unicode(file))[0]
      self.chbgfile()

    def chgopttransi(self,index): #OK QT4
      try :
        self.timeline.cellWidget(0,self.index).opttransi=index
      except :
        print "Erreur changement chgopttransi fonction ligne 808"
        None

    def choutputfile(self): #OK QT4
      self.updatexml(self.data,"outputfile",self.outputfile.text())

    def setOutputfile(self): #OK QT4
      file=QFileDialog.getSaveFileName(self, "FileDialog",self.home, "")
      self.outputfile.setText(file)
      self.updatexml(self.data,"outputfile",file)

    def choixoutputformat(self,txt): #OK QT4
      self.updatexml(self.data,"outputf",txt)

    def chsndfile(self): #OK QT4
      self.updatexml(self.data,"sndfile",self.soundfile.text())

    def sndfilea(self): #OK QT4
      file=QFileDialog.getOpenFileName(self, "FileDialog",self.lastdir, "Sound(*.wav *.mp3 *.ogg)")
      self.soundfile.setText(file)
      self.updatexml(self.data,"sndfile",file)
      self.lastdir=os.path.split(unicode(file))[0]

    ### Serie functions window section
    # Init function
    def serie(self) :
      self.winserie=Lot(self.lstT,self.lastdir,self)
      self.winserie.fromc.setMaximum(self.timeline.columnCount())
      self.winserie.toc.setMaximum(self.timeline.columnCount())
      self.winserie.show()
      self.connect(self.winserie.buttonBox,SIGNAL("accepted()"),self.processSerie)

    def processSerie(self) :
      if self.winserie.tableImage.rowCount() != 0 :
        i=0
        while i < self.winserie.tableImage.rowCount() :
          self.changeImageOption(self.winserie.tableImage.item(i,0).text(),self.winserie.tableImage.item(i,1).text(),self.winserie.tableImage.item(i,2).text())
          i += 1

    def changeImageOption(self,imF,imL,opt) :
      option=opt.split(":")
      i=int(imF)-1
      while i <= (int(imL)-1) :
        self.timeline.cellWidget(0,i).time=option[0]
        self.timeline.cellWidget(0,i).bgfile=option[1]
        self.timeline.cellWidget(0,i).bgcolor=int(str(option[2]),16)
        self.timeline.cellWidget(0,i).speedt=option[3]
        self.timeline.cellWidget(0,i).typet=option[4]
        self.timeline.cellWidget(0,i).opttransi=option[5]
        self.timeline.cellWidget(0,i).updatePix()
        self.timeline.setCurrentCell(0,i)
        self.selectionListe()
        i += 1
      self.displayLenght()

    ### GUI_Main - process section ###
    def process(self) :
      if self.pfilee==0 :
        self.projetfile=self.T+ os.sep +u"tmp.idv"
        self.pfilee=1
        self.saveprojet()
        self.pfilee=0
      else :
        self.saveprojet()
      k=0
      while k<self.timeline.columnCount() :
        self.timeline.cellWidget(0,k).export2ppm(self.T+ os.sep +u"img_"+unicode(k)+u".ppm",self.imgwidthF,self.imgheightF,self.imgwidth,self.imgheight)
        k+=1

      self.prc=process(self.data,self,self.verifsformats[5][self.outputfileformat.currentIndex()],self.imgformat,self.parent)

      if self.prc.err==0 :
        self.showprog=ShowProgress(self,self.prc.totimage)
        self.showprog.show()

        self.prc.start()
        self.connect(self.prc,SIGNAL("image"),self.displayProcessImg)
        self.connect(self.prc,SIGNAL("frame"),self.infoFrame)
        self.connect(self.prc,SIGNAL("text"),self.infoProgress)

    def displayProcessImg(self,img) :
      self.showprog.viewimg.setScene(self.timeline.cellWidget(0,img).Qscene())
      self.showprog.viewimg.fitInView(0,0,self.timeline.cellWidget(0,img).imgwidth,self.imgheight,Qt.KeepAspectRatio)

    def infoFrame(self,frame) :
      txt=self.tr("processing frame ")+str(frame)+self.tr(" from ")+str(self.prc.totimage)
      self.showprog.info.setText(txt)
      self.showprog.progressBar1.setValue(frame)

    def infoProgress(self,txt) :
      self.showprog.label1.setText(txt)

    ### Generic function to update DOM tree section ###
    def updatexml(self,dom,tag,txt,cf=0): #OK QT4
      doc = Document()
      node=doc.createTextNode(unicode(txt))
      try :
        of=dom.getElementsByTagName(tag)[0]
        of.replaceChild(node,of.childNodes[0])
      except :
        try :
          of=dom.getElementsByTagName(tag)[0]
          of.appendChild(node)
        except :
          if cf==0 :
            of2=dom.getElementsByTagName("options")[0]
          else :
            of2=dom.getElementsByTagName("configuration")[0]
          node2=doc.createElement(tag)
          node2.appendChild(node)
          of2.appendChild(node2)

