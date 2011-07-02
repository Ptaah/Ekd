#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of ekd - diaporama video module - This module is an integration of videoporama
# Videoporama is a program to make diaporama export in video file
# Copyright (C) 2007-2010  Olivier Ponchaut <opvg@edpnet.be>

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

import sys
import os
import subprocess
import Image
import StringIO
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from __builtin__ import hex as hexp
from videoporama_widget import *
from showprogress import *
from warning import *
from moteur_modules_common.EkdConfig import EkdConfig
#from moteur_modules_common.EkdProcess import EkdProcess

class ShowProgress(QDialog,Ui_showprogress) : #OK QT4
    def __init__(self, parent=None, totframe=0):
      super(ShowProgress, self).__init__(parent)
      self.setupUi(self)
      self.progressBar1.setMaximum(totframe)
      self.totframe=totframe
      self.connect(self.pushButton1,SIGNAL("clicked()"),self.tmpclose)

    def tmpclose(self) :
      self.emit(SIGNAL("cleantmp"))
      self.close()

class Warning(QDialog,Ui_warning) : #OK QT4
    def __init__(self, parent=None):
        super(Warning, self).__init__(parent)
        self.setupUi(self)

class process(QThread) :
  def __init__(self,dom,win,lstfmt,wide=0,parent=None) :
    super(process, self).__init__(parent)
    self.win=win
    self.listformat = lstfmt
    self.wide=wide
    if wide == 1 :
      self.aspect="3"
      self.wimage="16:9"
    else :
      self.aspect="2"
      self.wimage="4:3"
    self.img=[]
    self.err=0 # define if there's an error in initialisation phase
    self.msgerror=""
    self.sont=0
    try:
      self.t=EkdConfig.get("videoporamaconfig","speedt")
    except:
      self.t="3"
    try:
      self.n=dom.getElementsByTagName('videof')[0].childNodes[0].nodeValue
      if self.n=="0" : #PAL
        self.VIDEO_TYPE_LETTER="p"
        self.VIDEO_FORMAT="SIZE_720x576"
        self.IMGSEC="25:1"
        self.widthpict=720
        self.heightpict=576
        self.imgpsec=25
      elif self.n=="1" : #NTSC
        self.VIDEO_TYPE_LETTER="n"
        self.VIDEO_FORMAT="SIZE_720x480"
        self.IMGSEC="30000:1001"
        self.widthpict=720
        self.heightpict=480
        self.imgpsec=30
      elif self.n=="2" : #SECAM
        self.VIDEO_TYPE_LETTER="s"
        self.VIDEO_FORMAT="SIZE_720x576"
        self.IMGSEC="25:1"
        self.widthpict=720
        self.heightpict=576
        self.imgpsec=25
      elif self.n=="3" : #HDReady
        self.VIDEO_TYPE_LETTER="p"
        self.IMGSEC="25:1"
        self.widthpict=1280
        self.heightpict=720
        self.imgpsec=25
      elif self.n=="4" : #Full HD
        self.VIDEO_TYPE_LETTER="p"
        self.IMGSEC="25:1"
        self.widthpict=1920
        self.heightpict=1080
        self.imgpsec=25
      elif self.n=="5" : #Web flv
        self.VIDEO_TYPE_LETTER="p"
        self.IMGSEC="25:1"
        self.widthpict=384
        self.heightpict=288
        self.imgpsec=25
      elif self.n=="6" : #moyen xvid
        self.VIDEO_TYPE_LETTER="p"
        self.IMGSEC="25:1"
        self.widthpict=640
        if self.wide :
          self.heightpict=480
        else :
          self.heightpict=480
        self.imgpsec=25
    except:
      self.VIDEO_TYPE_LETTER="p"
      self.VIDEO_FORMAT="SIZE_720x576"
      self.widthpict=720
      self.heightpict=576
      self.imgpsec=25

    # Definition of total number of frame to process
    self.dicspeed={"0":1,"1":2,"2":4,"3":5,"4":10,"5":20}
    self.speedtrans=self.dicspeed[self.t]
    self.frametransition = 100 / self.speedtrans

    self.totimage=0
    # Images files
    if self.win.timeline.columnCount() == 0 :
      self.msgerror=self.msgerror+self.tr("There aren't picture to process \n")
      self.err=1
    else :
      k=0
      while k<self.win.timeline.columnCount() :
        self.img.append(self.win.timeline.cellWidget(0,k))
        self.totimage += self.win.timeline.cellWidget(0,k).imagetime(int(self.n))[1]+self.win.timeline.cellWidget(0,k).imagetime(int(self.n))[2]
        k+=1
      self.totimage+=self.frametransition
    # configurations elements
    # tmp directory
    self.T=self.win.T
    #ffmpeg directory
    if os.name != 'nt' :
      self.I=EkdConfig.get("videoporamaconfig","imgmgkdir")
    else :
      self.I=""
    #mjpegtools directory
    if os.name != 'nt' :
      self.MJ=EkdConfig.get("videoporamaconfig","mjpegtoolsdir")
    else:
      self.MJ=""
    # sox directory
    if os.name != 'nt' :
      self.S=EkdConfig.get("videoporamaconfig","soxdir")
    else:
      self.S=""
    try:
      self.w=dom.getElementsByTagName('sndfile')[0].childNodes[0].nodeValue
      if self.w=="" :
        self.w=os.getcwd()+os.sep+u"videoporama/template/nullsound.wav"
        self.sont=1
    except:
      self.w=os.getcwd()+os.sep+u"videoporama/template/nullsound.wav"
      self.sont=1
    try:
      self.f=dom.getElementsByTagName('outputf')[0].childNodes[0].nodeValue
    except:
      None
    try:
      self.mpgf=dom.getElementsByTagName('mpegformat')[0].childNodes[0].nodeValue
      self.formatmpg(self.mpgf)
    except:
      None
    try:
      self.o=dom.getElementsByTagName('outputfile')[0].childNodes[0].nodeValue
      if self.o=="" :
        self.msgerror=self.msgerror+self.tr("There isn't output file define \n")
        self.err=1
    except:
      self.msgerror=self.msgerror+self.tr("There isn't output file define \n")
      self.err=1
      None
    self.lumask={}
    z=0
    b=os.listdir(os.getcwd()+os.sep+u"videoporama/luma/")
    for c in b :
      # Ajouté le 23/11/2009 pour corriger le problème des .svn
      if not c.startswith(".") :
        self.lumask[z]=os.getcwd()+os.sep+u"videoporama/luma/"+c
        z+=1

    if self.err :
      self.error(self.msgerror)
    #else :

  def preview(self) :
    self.f=100
    self.widthpict=384
    self.heightpict=288


  def formatmpg(self,format):
    if format=="VCD" :
      self.y4m="420jpeg"
      if self.n == "1" :
        self.targetf="ntsc-vcd"
      else :
        self.targetf="vcd"
    elif format=="SVCD" :
      self.y4m="420mpeg2"
      if self.n == "1" :
        self.targetf="ntsc-svcd"
      else :
        self.targetf="svcd"
    elif format=="raw" :
      self.y4m="444"
      if self.n == "1" :
        self.targetf="ntsc-dv"
      else :
        self.targetf="dv"
    elif format=="DVD" :
      self.y4m="420mpeg2"
      if self.n == "1" :
        self.targetf="ntsc-dvd"
      else :
        self.targetf="dvd"
    else :
      self.y4m="444"


  def convertsound(self):
    # definition of sound lenght
    if self.VIDEO_TYPE_LETTER=="n" :
      sec=float(self.totimage) * 1001 / 30000
    else :
      sec=float(self.totimage) / 25
    seconde=str(sec % 60).split(".")
    minute=int(sec / 60)
    heure=int(minute / 60)
    timesnd="%s:%s:%s.%s" % (str(heure).rjust(2,'0'),str(minute).rjust(2,'0'),seconde[0].rjust(2,'0'),seconde[1].ljust(3,'0')[0:3])
    if QString(self.w).endsWith("mp3") | QString(self.w).endsWith("MP3") :
      st=u" -t mp3"
    else :
      st=u""

    # sound conversion
    self.ws=self.T + os.sep +u"audio.tmp.wav"
    if self.sont != 1 :
      if (subprocess.call(u"sox"+st+u" \""+self.w+u"\" -c 2 \""+self.T+ os.sep + u"audio.tmp.wav\" fade 00:00:00 "+timesnd+u" 00:00:00.500", shell=True)):
        print "bad sound file : "
        self.w=os.getcwd()+ os.sep +u"videoporama/template/nullsound.wav"
        self.sont=1
        self.convertsound()
    else :
      if (subprocess.call(u"sox -r 44100 -n -c 2 \""+self.T+ os.sep+ u"audio.tmp.wav\" trim 00:00:00.000 "+timesnd+u" ", shell=True)):
        print self.tr("Error with sound encoding process")
        self.emit(SIGNAL("text"), self.tr("Error with sound encoding process"))
        return 0
      ##

    # Test si le fichier son exist, si non, message d'erreur et arrêt de l'encodage
    if (not os.path.exists(self.T+os.sep+u"audio.tmp.wav")) :
      print self.T+os.sep+u"audio.tmp.wav"
      self.emit(SIGNAL("text"),self.tr("Error with sound encoding process \nEncoding process abort"))
      return 0
    else :
      return 1

  def fadepil(self,previouspil,impil,dissolve) :
    percent=float(dissolve)/100
    imf=Image.blend(previouspil,impil,percent)
    z=StringIO.StringIO()
    imf.save(z,"PPM")
    return z

  def slidepil(self,previouspil,impil,dissolve,opt=0) :
    if opt == 0 :
      box1=(int(self.widthpict-dissolve*self.widthpict/100),0,self.widthpict,self.heightpict)
      box2=(0,0,int(dissolve*self.widthpict/100),self.heightpict)
    elif opt == 1 :
      box1=(0,0,int(dissolve*self.widthpict/100),self.heightpict)
      box2=(int(self.widthpict-dissolve*self.widthpict/100),0,self.widthpict,self.heightpict)
    elif opt == 2 :
      box1=(0,int(self.heightpict-dissolve*self.heightpict/100),self.widthpict,self.heightpict)
      box2=(0,0,self.widthpict,int(dissolve*self.heightpict/100))
    elif opt == 3 :
      box1=(0,0,self.widthpict,int(dissolve*self.heightpict/100))
      box2=(0,int(self.heightpict-dissolve*self.heightpict/100),self.widthpict,self.heightpict)

    ima=impil.crop(box1)
    previouspil.paste(ima,box2)
    z=StringIO.StringIO()
    previouspil.save(z,"PPM")
    return z

  def appearpil(self,previouspil,impil,dissolve) :
    wt = int(self.widthpict*dissolve/100)
    ht = int(self.heightpict*dissolve/100)
    box = (int((self.widthpict-wt)/2),int((self.heightpict-ht)/2),int((self.widthpict+wt)/2),int((self.heightpict+ht)/2))
    imz = impil.resize((wt,ht))
    previouspil.paste(imz,box)
    z=StringIO.StringIO()
    previouspil.save(z,"PPM")
    return z

  def disappearpil(self,previouspil,impil,dissolve) :
    impil2=impil.copy()
    prce = 100-dissolve
    wt = int(self.widthpict*prce/100)
    ht = int(self.heightpict*prce/100)
    box = (int((self.widthpict-wt)/2),int((self.heightpict-ht)/2),int((self.widthpict+wt)/2),int((self.heightpict+ht)/2))
    imz = previouspil.resize((wt,ht))
    impil2.paste(imz,box)
    z=StringIO.StringIO()
    impil2.save(z,"PPM")
    return z

  def cubepil(self,previouspil,impil,dissolve,opt=0) :
    base = Image.new("RGB",(self.widthpict,self.heightpict))
    if opt == 0 :
      w1=int(self.widthpict*dissolve/100)
      box1=(0,0,w1,self.heightpict)
      part1 = impil.resize((w1,self.heightpict))
      w2=self.widthpict-w1
      box2=(w1,0,self.widthpict,self.heightpict)
      part2 = previouspil.resize((w2,self.heightpict))
      base.paste(part1,box1)
      base.paste(part2,box2)
    elif opt == 1 :
      w1=int(self.widthpict*dissolve/100)
      part1 = impil.resize((w1,self.heightpict))
      w2=self.widthpict-w1
      box1=(w2,0,self.widthpict,self.heightpict)
      box2=(0,0,w2,self.heightpict)
      part2 = previouspil.resize((w2,self.heightpict))
      base.paste(part1,box1)
      base.paste(part2,box2)
    elif opt == 2 :
      h1=int(self.heightpict*dissolve/100)
      box1=(0,0,self.widthpict,h1)
      part1 = impil.resize((self.widthpict,h1))
      h2=self.heightpict-h1
      box2=(0,h1,self.widthpict,self.heightpict)
      part2 = previouspil.resize((self.widthpict,h2))
      base.paste(part1,box1)
      base.paste(part2,box2)
    elif opt == 3 :
      h1=int(self.heightpict*dissolve/100)
      part1 = impil.resize((self.widthpict,h1))
      h2=self.heightpict-h1
      box1=(0,h2,self.widthpict,self.heightpict)
      box2=(0,0,self.widthpict,h2)
      part2 = previouspil.resize((self.widthpict,h2))
      base.paste(part1,box1)
      base.paste(part2,box2)

    z=StringIO.StringIO()
    base.save(z,"PPM")
    return z

  def pushpil(self,previouspil,impil,dissolve,opt=0) :
    if opt == 0 :
      base = Image.new("RGB",(self.widthpict*2,self.heightpict))
      base.paste(impil,(0,0,self.widthpict,self.heightpict))
      base.paste(previouspil,(self.widthpict,0,self.widthpict*2,self.heightpict))
      imz=base.crop((int(self.widthpict-dissolve*self.widthpict/100),0,int(self.widthpict*2-(dissolve*self.widthpict/100)),self.heightpict))
    elif opt == 1 :
      base = Image.new("RGB",(self.widthpict*2,self.heightpict))
      base.paste(previouspil,(0,0,self.widthpict,self.heightpict))
      base.paste(impil,(self.widthpict,0,self.widthpict*2,self.heightpict))
      imz=base.crop((int(dissolve*self.widthpict/100),0,int(self.widthpict+(dissolve*self.widthpict/100)),self.heightpict))
    elif opt == 2 :
      base = Image.new("RGB",(self.widthpict,self.heightpict*2))
      base.paste(impil,(0,0,self.widthpict,self.heightpict))
      base.paste(previouspil,(0,self.heightpict,self.widthpict,self.heightpict*2))
      imz=base.crop((0,int(self.heightpict-dissolve*self.heightpict/100),self.widthpict,int(self.heightpict*2-(dissolve*self.heightpict/100))))
    elif opt == 3 :
      base = Image.new("RGB",(self.widthpict,self.heightpict*2))
      base.paste(previouspil,(0,0,self.widthpict,self.heightpict))
      base.paste(impil,(0,self.heightpict,self.widthpict,self.heightpict*2))
      imz=base.crop((0,int(dissolve*self.heightpict/100),self.widthpict,int(self.heightpict+(dissolve*self.heightpict/100))))

    z=StringIO.StringIO()
    imz.save(z,"PPM")
    return z

  def map(self,i) :
    if i < limit :
      return 0
    return 255

  def lumapil(self,previouspil,impil,dissolve,mask) :
    global limit
    limit = int(dissolve*255/100)+1
    luma = Image.open(mask)
    msk = luma.point(lambda i : self.map(i),"1")
    mskl = msk.resize((self.widthpict,self.heightpict))
    lumaout = Image.composite(previouspil,impil,mskl)
    z=StringIO.StringIO()
    lumaout.save(z,"PPM")
    return z

  def choiceTransition(self,transitype,previous,image,dissolve,optionTr):
    if int(transitype)==0 :
      z=StringIO.StringIO()
      image.save(z,"PPM")
      return z

    elif int(transitype)==1 :
      resu=self.fadepil(previous,image,dissolve)
      # Debug
      if self.debug==1 :
        print "Transition = fade - image="+str(image)+" Precedente="+str(previous)+" percent transi="+str(dissolve)+" option Tr="+str(optionTr)
      return resu

    elif int(transitype)==2 :
      resu=self.appearpil(previous,image,dissolve)
      # Debug
      if self.debug==1 :
        print "Transition = Appear - image="+str(image)+" Precedente="+str(previous)+" percent transi="+str(dissolve)+" option Tr="+str(optionTr)
      return resu

    elif int(transitype)==3 :
      resu=self.disappearpil(previous,image,dissolve)
      # Debug
      if self.debug==1 :
        print "Transition = Disappear - image="+str(image)+" Precedente="+str(previous)+" percent transi="+str(dissolve)+" option Tr="+str(optionTr)
      return resu

    elif int(transitype)==4 :
      # Debug
      if self.debug==1 :
        print "Transition = Slide - image="+str(image)+" Precedente="+str(previous)+" percent transi="+str(dissolve)+" option Tr="+str(optionTr)
      resu=self.slidepil(previous,image,dissolve,int(optionTr))
      return resu

    elif int(transitype)==5 :
      # Debug
      if self.debug==1 :
        print "Transition = Cube - image="+str(image)+" Precedente="+str(previous)+" percent transi="+str(dissolve)+" option Tr="+str(optionTr)
      resu=self.cubepil(previous,image,dissolve,int(optionTr))
      return resu

    elif int(transitype)==6 :
      # Debug
      if self.debug==1 :
        print "Transition = Push - image="+str(image)+" Precedente="+str(previous)+" percent transi="+str(dissolve)+" option Tr="+str(optionTr)
      resu=self.pushpil(previous,image,dissolve,int(optionTr))
      return resu

    elif int(transitype)==7 :
      # Debug
      if self.debug==1 :
        print "Transition = Luma - image="+str(image)+" Precedente="+str(previous)+" percent transi="+str(dissolve)+" option Tr="+str(optionTr)

      resu=self.lumapil(previous,image,dissolve,self.lumask[int(optionTr)])
      return resu

  def zoomTravelImage(self,base,im,i,l=0) :
    nim=im.imagetime(self.n)
    progress=float(float(i-nim[2])/nim[1])
    imStart=im.selectZoomBox(1).sceneBoundingRect()
    imEnd=im.selectZoomBox(0).sceneBoundingRect()
    x1 = int((imEnd.x()-imStart.x())*progress+imStart.x())
    y1 = int((imEnd.y()-imStart.y())*progress+imStart.y())
    x2 = int(x1 + (imEnd.width()-imStart.width())*progress+imStart.width())
    y2 = int(y1 + (imEnd.height()-imStart.height())*progress+imStart.height())
    box = (x1, y1, x2, y2)
    imageZ=base.crop(box)
    imz=imageZ.resize((self.widthpict,self.heightpict)).convert("RGBA")
    z=StringIO.StringIO()
    imz.save(z,"PPM")
    if l == 1 :
      try:
        os.remove(self.T+ os.sep +"previmagetmp.ppm")
      except:
        None
      imz.save(self.T+ os.sep +"previmagetmp.ppm","PPM")
    return z

  def run(self):

    self.debug=0

    # Debug
    if self.debug==1 :
      print "Nombre total de frame="+str(self.totimage)

    # Sound check and abord if no sound file
    if not self.convertsound() :
      return None

    # First frame (black)
    black=Image.new("RGB",(self.widthpict,self.heightpict))
    black.save(self.T+ os.sep +u"black.ppm","PPM")

    self.formatmpg(self.listformat[1])
    if self.listformat[0]==0 :
      ext=u".dv"
      if QString(self.o).endsWith(ext) :
        ext=u""
      # Encoding process in DV
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S 444 | "+self.I+"ffmpeg -y -f yuv4mpegpipe -i - -i \""+self.ws+"\" -aspect "+self.wimage+" -target "+self.targetf+" \""+self.o+ext+"\"", shell=True, stdin=subprocess.PIPE)

    elif self.listformat[0] > 0 and self.listformat[0] < 4 : # Encoding mpeg 1 & 2
      ext=u".mpg"
      if QString(self.o).endsWith(ext) :
        ext=u""
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S "+self.y4m+" | "+self.I+"ffmpeg -y -f yuv4mpegpipe -i - -i \""+self.ws+"\" -aspect "+self.wimage+" -target "+self.targetf+" \""+self.o+ext+"\"", shell=True, stdin=subprocess.PIPE)

    elif self.listformat[0] == 4 : # Encoding Flash
      ext=u".flv"
      if QString(self.o).endsWith(ext) :
        ext=u""
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S "+self.y4m+" | "+self.I+"ffmpeg -y -f yuv4mpegpipe -i - -i \""+self.ws+"\" -s "+str(self.widthpict)+"x"+str(self.heightpict)+" -aspect "+self.wimage+" -qscale 20 -vcodec flv -ab 96000 -ar 22050 \""+self.o+ext+"\"", shell=True, stdin=subprocess.PIPE)

    elif self.listformat[0] == 8 : # Encoding h264
      ext=u".avi"
      if QString(self.o).endsWith(ext) :
        ext=u""
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S "+self.y4m+" | ffmpeg -y -f yuv4mpegpipe -i - -i \""+self.ws+"\" -s "+str(self.widthpict)+"x"+str(self.heightpict)+" -aspect "+self.wimage+" -qscale 12 -b 2000000 -vcodec libx264 -acodec libmp3lame -ab 128000 -ar 44100 \""+self.o+ext+"\"", shell=True, stdin=subprocess.PIPE)

    elif self.listformat[0] == 7 : #Encoding Xvid
      ext=u".avi"
      if QString(self.o).endsWith(ext) :
        ext=u""
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S "+self.y4m+" | ffmpeg -y -f yuv4mpegpipe -i - -i \""+self.ws+"\" -s "+str(self.widthpict)+"x"+str(self.heightpict)+" -aspect "+self.wimage+" -qscale 4 -vcodec libxvid -acodec libmp3lame -ab 128000 -ar 44100 \""+self.o+ext+"\"", shell=True, stdin=subprocess.PIPE)

    elif self.listformat[0] == 5 : #Encoding Theora ogg
      ext=u".ogg"
      if QString(self.o).endsWith(ext) :
        ext=u""
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S "+self.y4m+" | ffmpeg -y -f yuv4mpegpipe -i - -i \""+self.ws+"\" -s "+str(self.widthpict)+"x"+str(self.heightpict)+" -aspect "+self.wimage+" -b 2000000 -vcodec libtheora -qcomp 4.0 -acodec vorbis -ab 128000 -ar 44100 \""+self.o+ext+"\"", shell=True, stdin=subprocess.PIPE)

    elif self.listformat[0] == 6 : #Encoding mjpeg
      ext=u".avi"
      if QString(self.o).endsWith(ext) :
        ext=u""
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S "+self.y4m+" | ffmpeg -y -f yuv4mpegpipe -i - -i \""+self.ws+"\" -s "+str(self.widthpict)+"x"+str(self.heightpict)+" -aspect "+self.wimage+" -qscale 4 -vcodec mjpeg -acodec pcm_s16le -ar 44100 \""+self.o+ext+"\"", shell=True, stdin=subprocess.PIPE)

    elif int(self.f)==100 :
      self.formatmpg("VCD")
      #ext=u".mpg"
      encodedv_pipe = subprocess.Popen(self.MJ+"ppmtoy4m -v 0 -n "+str(self.totimage)+" -A "+self.wimage+" -F "+self.IMGSEC+" -S "+self.y4m+" | ffmpeg -f yuv4mpegpipe -i - -i \""+self.ws+"\" -s "+str(self.widthpict)+"x"+str(self.heightpict)+" -aspect "+self.wimage+" - | "+self.MP+"mplayer - ", shell=True, stdin=subprocess.PIPE)
    # Standard input to convert process
    encodedv_stdin = encodedv_pipe.stdin

    z=0 # z = current frame
    a=1 # a = current image
    optTr=0
    n=0
    self.imgsources=[]
    for im in self.img :
      self.imgsources.append(unicode(im.urlim))
      self.emit(SIGNAL("image"),n)
      # Debug
      if self.debug==1 :
        print "URL Image "+str(im.urlim)+" - devient="+self.T+ os.sep +"imagetmp.ppm"

      imf=Image.open(self.T+ os.sep +u"img_".encode('utf-8')+unicode(n).encode('utf-8')+u".ppm".encode('utf-8'))
      imfp=StringIO.StringIO()
      imf.save(imfp,"PPM")

      if im.zoom==2 :
        baseIm = Image.open(im.urlim)

      i=0 # current frame on current image
      dissolve=0

      if a == 1 :
        ftransi=self.frametransition
        previous=self.T+ os.sep +u"black.ppm"
        transitype=1

      nbrframe=im.imagetime(int(self.n))[1] + ftransi
      zoom=im.zoom
      # Debug
      if self.debug==1 :
        print "Image "+str(a)+" - Nbr frame = "+str(im.imagetime(int(self.n))[1])
      if ftransi != 0 :
        speedt = 100 / ftransi
      while i < nbrframe : # Process current image
        image=self.T+ os.sep +u"img_".encode('utf-8')+unicode(n).encode('utf-8')+u".ppm".encode('utf-8')
        #tFirst ransition
        if i < ftransi : # Process transition with previous image
          if dissolve == 0 :
            im1=Image.open(previous)
            im2=Image.open(image)
          famg=self.choiceTransition(transitype,im1,im2,dissolve,optTr)
          encodedv_stdin.write(famg.getvalue())

          dissolve=dissolve+speedt

        else :
          if zoom==2 :
            if (i == (nbrframe-1)):
              convert_pipe = self.zoomTravelImage(baseIm,im,i,1)
            else :
              convert_pipe = self.zoomTravelImage(baseIm,im,i)
            encodedv_stdin.write(convert_pipe.getvalue())

          else :
            encodedv_stdin.write(imfp.getvalue())

        # Debug
        if self.debug==1 :
          print "Frame="+str(z)+" - Image envoyee encodage "+str(image)

        i+=1
        z+=1
        self.emit(SIGNAL("frame"),z)
      a+=1
      transitype=int(im.typet)
      optTr=im.opttransi
      ftransi=im.imagetime(int(self.n))[2]
      if im.zoom != 2 :
        try:
          os.remove(self.T+ os.sep +u"previmagetmp.ppm")
        except :
          None
        os.rename(image,self.T+ os.sep +u"previmagetmp.ppm")
      previous=self.T+ os.sep +u"previmagetmp.ppm"
      n+=1

    dissolve=0
    speedt = 100 / ftransi
    while z < self.totimage :
      if dissolve == 0 :
        im1=Image.open(previous)
        im2=Image.open(self.T+ os.sep +u"black.ppm")
      famg=self.choiceTransition(transitype,im1,im2,dissolve,optTr)
      encodedv_stdin.write(famg.getvalue())
      dissolve=dissolve+int(speedt)
      z+=1
      self.emit(SIGNAL("frame"),z)

    encodedv_stdin.close() # Send signal End of file to encoding process
    encodedv_pipe.wait() # Wait until encoding is finished

    self.emit(SIGNAL("text"),self.tr("Encoding finished"))
    self.emit(SIGNAL("resProcess"),self.o+ext, self.imgsources, None, None, self.o+ext)
    self.cleantmp()

  def error(self,texte):
    self.war=Warning(self.win)
    self.war.texte.setText(texte)
    self.war.show()
    self.war.connect(self.war.closeb,SIGNAL("clicked()"),self.war,SLOT("close()"))

  def cleantmp(self) : # cleaning temporary files
    for file in os.listdir(self.T) :
      if file.endswith(u".ppm") and file.startswith(u"img_") :
        os.remove(self.T+ os.sep +file)
    try:
      os.remove(self.T+ os.sep +u"black.ppm")
    except:
      None
    try:
      os.remove(self.T+ os.sep +u"previmagetmp.ppm")
    except:
      None
    try:
      os.remove(self.T+ os.sep +u"audio.tmp.wav")
    except:
      None
