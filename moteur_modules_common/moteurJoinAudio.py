# -*- coding: utf-8 -*-
# This file is part of ekd - Music and sound module
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

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import subprocess
from PyQt4.QtCore import QObject, SIGNAL, QString, QThread
from gui_modules_common.EkdWidgets import EkdProgress
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdProcess import EkdProcess

# Activation des traces de débug sur ce moteur -> mettre à 1 ou True.
debug = 1

class soxProcessMulti(EkdProgress) :

	def __init__(self, cheminAudioSource, cheminAudioSorti, regExp=u"", parent=None) :
		super(soxProcessMulti, self).__init__(parent, 100)
		if debug : print type(cheminAudioSource)
		self.processAudio = soxEngineMulti(cheminAudioSource, cheminAudioSorti, regExp, parent)
		self.connect(self.processAudio, SIGNAL("DisplayText"), self.addText)
		self.connect(self.processAudio, SIGNAL("Progress"), self.setProgress)
		self.connect(self.processAudio, SIGNAL("endProcess(QString)"), self.endAction)

	def setProgress(self, prg) :
		self.barProgress.setValue(prg)

	def endAction(self, msg) :
		self.barProgress.setValue(100)
		self.fermer.setEnabled(True)
		self.emit(SIGNAL("endProcess"), msg)

	def run(self) :
		self.processAudio.start()


class soxEngineMulti(QThread) :

	def __init__(self, cheminIn, cheminOut, regExp, parent=None) :
		super(soxEngineMulti, self).__init__(parent)
		self.cheminIn = cheminIn
		self.cheminOut = cheminOut
		self.regExp = regExp
		self.k=0
	
	def verifDetailsAudioFF(self) :
		k=0
		for fileA in self.cheminIn :
			#infoP = subprocess.Popen(u"ffmpeg -i \""+fileA+u"\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
			infoP = EkdProcess(u"ffmpeg -i \""+fileA+u"\"", outputerr=subprocess.STDOUT)
			info = infoP.stdout.read()
			infoP.wait()
			if debug : print info
			if k==0 :
				#créer le tuple de valeur à vérifier (Lignes)
				dataInfo =unicode(info,"utf-8").split(u"\n")
			else :
				i=0
				for lign in unicode(info,"utf-8").split(u"\n") :
					if i ==8 : # Control de la ligne critique : nbr canaux, fréquence et précision.
						if debug : print lign, i
						if lign != dataInfo[i] :
							print "Formats incompatibles, réencodage"
							self.emit(SIGNAL("DisplayText"), _(u"Formats incompatibles, réencodage"))
							return True #un réencodage est nécessaire avant concaténation
					i += 1
				# Vérifier dans les infos que ça correspond avec le fichier précédent. Si non -> Break + return False
			k += 1
		return False # Si tous les fichiers ont des caractéristiques similaires -> OK pour concaténation
		

	def verifDetailsAudio(self) :
		k=0
		for fileA in self.cheminIn :
			#infoP = subprocess.Popen(u"sox --i \""+fileA+u"\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
			infoP = EkdProcess(u"sox --i \""+fileA+u"\"", outputerr=subprocess.STDOUT)
			info = infoP.stdout.read()
			infoP.wait()
			if debug : print info
			if k==0 :
				#créer le tuple de valeur à vérifier (Lignes) 
				dataInfo =unicode(info,"utf-8").split(u"\n")
			else :
				i=0
				for lign in unicode(info,"utf-8").split(u"\n") :
					if "Failed:" in lign :
						if debug : print "sox --i non disponible, fonction backup avec ffmpeg utilisee"
						return self.verifDetailsAudioFF()
					if i ==2 or i==3 or i==4 : # Control des lignes critiques : nbr canaux, fréquence et précision.
						if debug : print lign, i
						if lign != dataInfo[i] :
							print "Formats incompatibles, réencodage"
							self.emit(SIGNAL("DisplayText"), _(u"Formats incompatibles, réencodage"))
							return True #un réencodage est nécessaire avant concaténation
					i += 1
				# Vérifier dans les infos que ça correspond avec le fichier précédent. Si non -> Break + return False
			k += 1
		return False # Si tous les fichiers ont des caractéristiques similaires -> OK pour concaténation
				
	def formatFileSox(self, fileA) :
		fileExt = os.path.splitext(fileA)[1].lower()
		if fileExt == ".wav" : return u" -t wav \""+fileA+"\""
		elif fileExt[1] == ".ogg" : return u" -t ogg \""+fileA+"\""
		elif fileExt[1] == ".mp3" : return u" -t mp3 \""+fileA+"\""
		elif fileExt[1] == ".flac" : return u" -t flac \""+fileA+"\""
		elif fileExt[1] == ".mp2" : return u" -t mp2 \""+fileA+"\""
		else : return u" \""+fileA+u"\""


	def run(self):
		if debug : print self.cheminIn
		# Vérification que le répertoire temporaire existe et est vide.
		if os.path.exists(EkdConfig.getTempDir() + os.sep+ u'concat_audio' + os.sep) :
			for tmpFile in os.listdir(EkdConfig.getTempDir() + os.sep+ u'concat_audio' + os.sep) :
				os.remove(EkdConfig.getTempDir() + os.sep+ u'concat_audio' + os.sep + tmpFile)
		else : os.mkdir(EkdConfig.getTempDir() + os.sep+ u'concat_audio' + os.sep)

		entree=u""
		if self.verifDetailsAudio() :
			self.k=0
			for fileA in self.cheminIn :
				### A modifier par un chemin temporaire -> ekdConfig
				com = u"sox -S "+self.formatFileSox(fileA)+" -c 2 -r 44100 \"%stmp_%i_.wav\"" % (unicode(EkdConfig.getTempDir() + os.sep+ u'concat_audio' + os.sep),self.k) 
				# Debug
				if debug : print com.encode('utf-8')
				#self.mesg2=subprocess.Popen(com.encode('utf-8'), shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
				self.mesg2 = EkdProcess(com.encode('utf-8'), outputerr = None)
				self.mesg2.wait()
				entree += u" -t wav \"%stmp_%i_.wav\"" % (unicode(EkdConfig.getTempDir() + os.sep+ u'concat_audio' + os.sep),self.k)
				self.emit(SIGNAL("DisplayText"),_(u"Réencodage du fichier %s terminé") % (fileA))
				self.k += 1
		else :
			for fileA in self.cheminIn :
				entree += self.formatFileSox(fileA)

			# Debug
			if debug : print entree
		commande = u"sox -S --combine concatenate "+entree+u" -c 2 -r 44100 "+self.regExp+" \""+self.cheminOut+u"\""
		### Debug*
		if debug : print commande.encode("utf-8")
		#self.mesg = subprocess.Popen(commande.encode("utf-8"), universal_newlines=True, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
		self.mesg = EkdProcess(commande.encode("utf-8"), stdinput = subprocess.PIPE,
                                                                outputerr=subprocess.STDOUT)
		avancement = 0
		nfile = -1
		while self.mesg.poll() == None :
			prog = self.mesg.stdout.readline()
			if prog.find("Input") != -1 :
				nfile += 1
				if debug : print "file : ", nfile
			if prog.startswith("In:") :
				perFile = float(prog.split("%")[0][3:])
				if debug : print prog.split("%")[0][3:]
				avancement = int(100.0*nfile/len(self.cheminIn))+int(perFile/len(self.cheminIn))
			#Debug
			if debug : print avancement
			self.emit(SIGNAL("Progress"),avancement)

		self.finEncodage(self.mesg.wait())

	def finEncodage(self, statutDeSortie):
		"""choses à faire à la fin de l'encodage audio"""
		if statutDeSortie==1:
			print "Crash de l'encodeur!"
			self.emit(SIGNAL("DisplayText"),_(u"Crash de l'encodeur !"))
			self.emit(SIGNAL("endProcess(QString)"), QString(u"None"))

		elif statutDeSortie==2 :
			print "Problème lors de l'encodage audio final : ", statutDeSortie
			self.emit(SIGNAL("endProcess(QString)"), None)
			self.emit(SIGNAL("DisplayText"),_(u"Le traitement ne s'est pas déroulé correctement."))

		else :
			print "Fin et statut : ", statutDeSortie
			self.emit(SIGNAL("endProcess(QString)"), self.cheminOut)
			self.emit(SIGNAL("DisplayText"),_(u"Encodage terminé avec succès"))
		for i in range(self.k) :
			os.remove(u"%stmp_%i_.wav" % (unicode(EkdConfig.getTempDir() + os.sep+ u'concat_audio' + os.sep),i))
			i += 1
