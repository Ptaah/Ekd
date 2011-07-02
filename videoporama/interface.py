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
from subprocess import *
from xml.dom import minidom
from xml.dom.minidom import Document
from lot import *

def colortohex(color): #OK QT4 !!!
  r=int(int(color)/65536)
  g=int((int(color)-r*65536)/256)
  b=int(int(color)-r*65536-g*256)
  rr=hexp(r)
  gg=hexp(g)
  bb=hexp(b)
  colorh=unicode(rr.strip("0x").upper().rjust(2,"0")+gg.strip("0x").upper().rjust(2,"0")+bb.strip("0x").upper().rjust(2,"0")).encode('utf-8')
  return colorh
    

class QComboTable(QComboBox) :
    def __init__(self,row=-1,parent=None) :
      super(QComboTable,self).__init__(parent)
      self.row=row
      self.connect(self,SIGNAL("currentIndexChanged(int)"),self.sigChanged)
      
    def setRow(self,row) :
      self.row=row
      
    def sigChanged(self) :
      self.index=self.currentIndex()
      self.emit(SIGNAL("QCBchanged"),self.index,self.row)

class Lot(QDialog,Ui_lot) :
    def __init__(self,lstTransi,lastdir,parent=None) :
      super(Lot, self).__init__(parent)
      self.setupUi(self)
      self.lastdir=lastdir
      # Fill transition and transition option list box
      self.index=-1
      self.typet.addItems(lstTransi)
      # Defaulf background color
      self.bgcolor.setText(colortohex(0))
      bckcol=QPalette()
      bckcol.setColor(QPalette.Base,QColor.fromRgb(0))
      self.bgcolor.setPalette(bckcol)
      self.transiopt.addItem(self.tr("No Option"))
      self.connect(self.typet,SIGNAL("currentIndexChanged(int)"),self.chgTrOption)
      self.connect(self.bgfilea,SIGNAL("clicked()"),self.bgfileact)
      self.connect(self.bgcolora,SIGNAL("clicked()"),self.bgcoloract)
      self.connect(self.updateLine,SIGNAL("clicked()"),self.updateLineA)
      self.connect(self.removeLine,SIGNAL("clicked()"),self.removeLineA)        
      self.connect(self.empty,SIGNAL("clicked()"),self.emptyTableA)
      self.connect(self.validLine,SIGNAL("clicked()"),self.validLineA)
      self.connect(self.buttonBox,SIGNAL("rejected()"),self,SLOT("close()"))
      self.connect(self.tableImage,SIGNAL("itemSelectionChanged()"),self.updateOption)
    
    def updateOption(self) :
      if self.tableImage.currentRow() != self.index :
        self.index=self.tableImage.currentRow()
        self.fromc.setValue(int(self.tableImage.item(self.index,0).text()))
        self.toc.setValue(int(self.tableImage.item(self.index,1).text()))
        option=self.tableImage.item(self.index,2).text().split(":")
        self.time.setValue(int(option[0]))
        self.bgfile.setText(option[1])
        self.bgcolor.setText(option[2])
        bckcol=QPalette()
        bckcol.setColor(QPalette.Base,QColor.fromRgb(int(str(option[2]),16)))
        self.bgcolor.setPalette(bckcol)
        self.speedt.setCurrentIndex(int(option[3]))
        self.typet.setCurrentIndex(int(option[4]))
        self.transiopt.setCurrentIndex(int(option[5]))
        
    def bgfileact(self): #OK QT4
      file=QFileDialog.getOpenFileName(self, "FileDialog",self.lastdir, "Images(*.jpg *.png *.gif *.xpm)")
      self.bgfile.setText(file)
      self.lastdir=os.path.split(unicode(file).encode('utf-8'))[0]
        
    def bgcoloract(self): # OK QT4 !!!
      colorb=QColorDialog.getColor(QColor(0),self)
      red=colorb.red()
      green=colorb.green()
      blue=colorb.blue()
      xcolor=red*65536+green*256+blue
      self.bgcolor.setText(colortohex(xcolor))
      bckcol=QPalette()
      bckcol.setColor(QPalette.Base,colorb)
      self.bgcolor.setPalette(bckcol)
    
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
          if not c.startswith(".") :
            d=os.path.splitext(c)
            LS.append(d[0])
      return LS

    def chgTrOption(self,index) : #OK QT4
      try :
        z=self.getTrOptionLst(index)
        self.transiopt.clear()
        self.transiopt.addItems(z)
      except :
        print "problème fonction chgTrOption - interface.py" #None

    def updateLineA(self) :
      if self.index != -1 :
        options=QString(str(self.time.value())+":"+self.bgfile.text()+":"+self.bgcolor.text()+":"+str(self.speedt.currentIndex())+":"+str(self.typet.currentIndex())+":"+str(self.transiopt.currentIndex()))
        self.tableImage.setItem(self.index,0,QTableWidgetItem(str(self.fromc.value())))
        self.tableImage.setItem(self.index,1,QTableWidgetItem(str(self.toc.value())))
        self.tableImage.setItem(self.index,2,QTableWidgetItem(options))
        self.tableImage.setCurrentCell(self.index,0)
      else :
	self.validLineA()

    def removeLineA(self) :
      if self.tableImage.currentRow() != -1 :
        self.tableImage.removeRow(self.tableImage.currentRow())
      
    def emptyTableA(self) :
      while self.tableImage.rowCount() > 0 :
        self.tableImage.removeRow(0)
      
    def validLineA(self) :
      self.tableImage.insertRow(self.tableImage.rowCount())
      self.index = self.tableImage.rowCount()-1
      self.updateLineA()


class myLabel(QLabel) :
    def __init__(self,urlim,scene=None,col=0,time=5,bgfile="essai",bgcolor=256,typet=0,opttransi=0,speedt=3,imgwide=0,zoom=0,hd=0,parent=None) :
      super(myLabel,self).__init__(parent)
      self.scene=scene
      self.imgwide=imgwide
      if imgwide == 1 :
        self.wpix=133
        if hd==3 :
          self.imgwidth=1280
          self.imgheight=720
          self.txtzoom=4.2
          self.txtwide=300
        elif hd==4 :
          self.imgwidth=1920
          self.imgheight=1080
          self.txtzoom=6.9
          self.txtwide=275
        elif hd==5 :
          self.imgwidth=512
          self.imgheight=288
          self.txtzoom=1.5
          self.txtwide=335
        elif hd==6 :
          self.imgwidth=640
          self.imgheight=360
          self.txtzoom=1.5
          self.txtwide=335
        else :
          self.imgwidth=1024
          self.imgheight=576
          self.txtzoom=3.1
          self.txtwide=330
      else :
        self.wpix=100
        if hd==3 :
          self.imgwidth=1280
          self.imgheight=960
          self.txtzoom=4.1
          self.txtwide=312
        elif hd==4 :
          self.imgwidth=1920
          self.imgheight=1440
          self.txtzoom=6.4
          self.txtwide=298
        elif hd==5 :
          self.imgwidth=384
          self.imgheight=288
          self.txtzoom=1.2
          self.txtwide=310
        elif hd==6 :
          self.imgwidth=640
          self.imgheight=480
          self.txtzoom=1.2
          self.txtwide=310
        else :
          self.imgwidth=768
          self.imgheight=576
          self.txtzoom=2.5
          self.txtwide=310
      self.hpix=75
      self.urlim=unicode(urlim)
      self.col=col
      self.time=time
      self.bgfile=bgfile
      self.bgcolor=bgcolor
      self.typet=typet
      self.opttransi=opttransi
      self.speedt=speedt
      self.zoom=zoom
      self.updatePix()
    
    def updatePix(self) :
      dessin=QImage(self.wpix,self.hpix,QImage.Format_RGB32)
      select=self.selectItem()
      self.scene.clearSelection()
      self.scene.render(QPainter(dessin)) 
      if select != None :
        select.setSelected(1)
      pix=QPixmap.fromImage(dessin)
      self.setPixmap(pix)
    
    def export2ppm(self,url,w=720,h=576,ws=768,hs=576) :
      if self.zoom==2 :
        self.strtStpZoom(url,w,h)
      else :  
        dessin=QImage(w,h,QImage.Format_RGB32)
        self.scene.clearSelection()
        self.scene.render(QPainter(dessin),QRectF(0,0,w,h),QRectF(0,0,ws,hs),Qt.IgnoreAspectRatio) 
        dessin.save(url,"PPM",100)
    
    def selectItem(self) :
        items=self.scene.selectedItems()
        if len(items)==1 :
          return items[0]
        return None
    
    def Qscene(self) :
      return self.scene

    def setQscene(self,scene) :
      self.scene=scene
      self.updatePix()
      
    def copy(self) :
      cp=myLabel(self.urlim,self.scene,self.col,self.time,self.bgfile,self.bgcolor,self.typet,self.opttransi,self.speedt,self.imgwide)
      return cp
    
    def imagetime(self,videof) :
      if videof==1 :
        imgpsec=30
      else:
        imgpsec=25
      if self.typet < 1 :
        framt=0
      else :
        dicspeed={"0":1,"1":2,"2":4,"3":5,"4":10,"5":20}
        speedtrans=dicspeed[str(self.speedt)]
        framt = 100 / speedtrans
      nbrframe=int(self.time) * imgpsec
      imgt=int(self.time) + (framt*imgpsec) 
      return (imgt,nbrframe,framt)

# Functions for zoom and travel
    def setZoom(self) :
      if self.zoom == 0 :
        self.composeZoom=QGraphicsScene()
        pix=QPixmap(self.urlim)
        self.composeZoom.setSceneRect(QRectF(pix.rect()))
        self.composeZoom.addPixmap(pix)
      return self.composeZoom
      
    def setChkZoom(self,chk) :
      self.zoom=chk

    def setZoomBox(self,x,y,w,h,se=1) :
      penW = int(self.composeZoom.width() * 0.01)
      if penW == 0 :
        penW = 1
      if se == 1 :
        col=QColor(255,0,0)
        dt="startZoom"
      else :
        col=QColor(0,0,255)
        dt="endZoom"
      pen=QPen(col)
      pen.setWidth(penW)
      cadre=self.composeZoom.addRect(x,y,w,h,pen)
      cadre.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
      cadre.setZValue(101)
      cadre.setAcceptDrops(1)
      data=QVariant(dt)
      cadre.setData(0,data)
      
    def selectZoomBox(self,se) :
      if se == 1 :
        idf="startZoom"
      else :
        idf="endZoom"
      for item in self.composeZoom.items() :
        if (item.data(0).toString() == idf) :
          return item
      return None
      
    def getZoomBoxInfo(self,se) :
      item=self.selectZoomBox(se)
      if item != None :
        X=item.sceneBoundingRect()
        coord=str(X.x())+":"+str(X.y())+":"+str(X.width())+":"+str(X.height())
        return coord
      return None
      
    def strtStpZoom(self,url,w,h) :
      item=self.selectZoomBox(1).sceneBoundingRect()
      item2=self.selectZoomBox(0).sceneBoundingRect()
      base=Image.open(self.urlim)
      img=base.crop((int(item.x()),int(item.y()),int(item.x()+item.width()),int(item.y()+item.height())))
      img2=base.crop((int(item2.x()),int(item2.y()),int(item2.x()+item2.width()),int(item2.y()+item2.height())))
      img=img.convert("RGBA")
      img2=img2.convert("RGBA")
      (img.resize((w,h))).save(url,"PPM")
      (img2.resize((w,h))).save(url+u"end.ppm","PPM")
