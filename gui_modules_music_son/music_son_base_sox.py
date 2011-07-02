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
from PyQt4.QtCore import QObject, SIGNAL, QProcess, QByteArray, QString, QThread
from PyQt4.QtGui import QWidget, QHBoxLayout, QLabel, QComboBox, QCheckBox, QGroupBox, QSpacerItem, QSizePolicy
from gui_modules_common.EkdWidgets import EkdProgress
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdProcess import EkdProcess

if os.name in ['posix', 'mac']:
	coding = "utf-8"
else :
	coding = "cp1252"


class reglageExpert(QWidget) :
	"""Class pour créer les widgets spécifiques pour les réglages plus fin sur la qualité d'encodage, sur le débit binaire des fichiers, ... """
	def __init__(self, listeFormat, comboFormat, parent=None) :
		super(reglageExpert, self).__init__(parent)
		self.listeFormat = listeFormat
		self.comboFormat = comboFormat
		self.format = self.comboFormat.currentIndex()
		self.parent = parent
		layout = QHBoxLayout(self)
		self.textLabel = QLabel(self)
		self.textLabel.hide()
		self.expert = QCheckBox(_(u"Réglage expert : "), self)
		self.qualite = QComboBox(self)
		layout.addWidget(self.expert)
		layout.addWidget(self.textLabel)
		layout.addWidget(self.qualite)
		layout.addStretch()
		i=1
		while i<9 :
			self.qualite.addItem(str(i))
			i	+=	1
		self.qualite.hide()
		self.changeFormat(self.comboFormat.currentIndex())
		self.connect(self.expert, SIGNAL("stateChanged(int)"), self.setExpert)
		self.connect(self.comboFormat, SIGNAL("currentIndexChanged(int)"), self.changeFormat)
		self.connect(self.qualite, SIGNAL("currentIndexChanged(int)"), self.changeQualite)

	def setExpert(self, state) :
		if state :
			self.qualite.show()
			self.textLabel.show()
		else :
			self.qualite.hide()
			self.textLabel.hide()

	def changeQualite(self,qualite) :
		self.changeFormat(self.comboFormat.currentIndex())

	def changeFormat(self, format) :
		if len(self.listeFormat) == 0 :
			return
		else :
			if self.listeFormat[format] == "mp3" or self.listeFormat[format] == "mp2" or self.listeFormat[format] == "ogg" :
				self.textLabel.setText(_(u"Qualité d'encodage"))
				self.qualite.setEnabled(True)
				self.C = u" -C %f " % (10.0*float(self.qualite.currentIndex()+1)/8.0)
			elif self.listeFormat[format] == "flac" :
				self.textLabel.setText(_(u"Taux de compression"))
				self.qualite.setEnabled(True)
				self.C = u" -C %d " % (self.qualite.currentIndex()+1)
			else :
				self.textLabel.setText(_(u"Non applicable, format non compressé"))
				self.qualite.setDisabled(True)
				self.C = u""

	def getExpertState(self) :
		return self.expert.isChecked()

	def getC(self) :
		return self.C

	def saveConfig(self, idsection="") :
		if idsection == "" :
			return 
		EkdConfig.set(idsection, u'format', unicode(self.comboFormat.currentIndex()))
		EkdConfig.set(idsection, u'expert', unicode(int(self.getExpertState())))
		EkdConfig.set(idsection, u'qualite', unicode(self.qualite.currentIndex()))


	def loadConfig(self, idsection="") :
		if idsection == "" :
			return 
		self.comboFormat.setCurrentIndex(int(EkdConfig.get(idsection, 'format')))
		self.expert.setChecked(int(EkdConfig.get(idsection, 'expert')))
		self.qualite.setCurrentIndex(int(EkdConfig.get(idsection, 'qualite')))


class checkSoxEncoding(QObject) :
	"""checkSoxEncoding est une class pour vérifier les possibilités de Sox pour l'encodage du format mp2/mp3. Si ce n'est pas le cas, retourne 0 -> adaptation de l'interface pour supprimer ces possibilités"""
	def __init__(self, listeformat, parent=None) :
		super(checkSoxEncoding, self).__init__(parent)
		#self.hide()
		self.listeFormat = listeformat
		self.parent = parent
		self.index = 0
		self.checkListeFormat = []

	def run(self) :
		self.soxP = QProcess(self.parent)
		self.connect(self.soxP, SIGNAL('finished(int)'), self.finProcess)
		self.write = 0
		commande = u"sox -n -t %s \"%s\" trim 00:00:00.000 00:00:01.000" % (self.listeFormat[self.index], os.path.expanduser("~")+os.sep+u"checkSoxEssai."+self.listeFormat[self.index])
		### Debug
		print commande
		self.soxP.setProcessChannelMode(QProcess.MergedChannels)
		self.soxP.start(commande)

	def finProcess(self,statut) :
		# Test si la commande a été exécutée correctement
		print "statut de sortie : %d" % (statut)
		if not statut :
			# Si OK -> Ajout de l'extension dans la liste des formats supportés par Sox en encodage
			self.checkListeFormat.append((self.listeFormat[self.index],True))
			os.remove(os.path.expanduser("~")+os.sep+u"checkSoxEssai."+self.listeFormat[self.index])
		else :
			# Sinon, déclaré le format comme non utilisable et donc pas présent dans la liste des formats supportés
			self.checkListeFormat.append((self.listeFormat[self.index],False))
		# Incrémentation du compteur pour explorer tous les formats à tester
		self.index += 1
		### Debug
		print "index = %d" % (self.index)
		print "longueur liste = %d" % (len(self.listeFormat))
		# Si l'index est égal au nombre de format à tester, la class émet le signal de fin de vérification + liste des formats avec info sur le support
		if self.index == len(self.listeFormat) :
			### Debug : print self.checkListeFormat
			self.emit(SIGNAL("checkSox"), self.checkListeFormat)
		else :
			self.run()

class choixSonSortieWidget(QGroupBox) :
    """Class pour faire le widget standard de sélection du format de sortie son + réglages experts"""
    def __init__(self, soxSuppFormat, parent=None) :
      super(choixSonSortieWidget, self).__init__(parent)
      self.setObjectName("groupBox")
      self.horizontalLayout = QHBoxLayout(self)
      self.horizontalLayout.setObjectName("horizontalLayout")
      self.label = QLabel(self)
      self.label.setObjectName("label")
      self.horizontalLayout.addWidget(self.label)
      self.formatSound = QComboBox(self)
      for x in soxSuppFormat :
        self.formatSound.addItem(QString(x))
      self.formatSound.setObjectName("formatSound")
      self.horizontalLayout.addWidget(self.formatSound)
      spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
      self.horizontalLayout.addItem(spacerItem)
      self.reglageExp = reglageExpert(soxSuppFormat, self.formatSound)
      self.horizontalLayout.addWidget(self.reglageExp)
      self.setTitle(_(u"Réglage du format de sortie"))
      self.label.setText(_(u"Format du fichier de sortie :"))
      self.formatSound.setToolTip(_(u"Format du fichier son de sortie"))

    def getFileExt(self) :
      return unicode(self.formatSound.currentText())

### progression avec la class de traitement.
class SoxProcess(EkdProgress) :
	"""Class pour effectuer les traitements audio avec Sox et afficher la progression dans
		une boîte de dialogue standard.
		La class nécessite le ou les url des fichiers en entrée à traiter, l'url du fichier de sortie et les options à passer à SoX.
		Le process génère 2 signaux (Données disponibles pour lire + données, fin de process + statut de sortie du process). Les critères pour définir l'avancement du process ainsi que les informations à afficher à l'utilisateurs doivent être définie au moyen des critères "critereFile" et "critereProgress"
	"""
	def __init__(self, cheminAudioSource, cheminAudioSorti, nfile, globalOptions=u"", outputFileOptions=u"", effects=u"", parent=None) :
		super(SoxProcess, self).__init__(parent, 100)
		self.processAudio = soxEngine(cheminAudioSource, cheminAudioSorti, nfile, globalOptions, outputFileOptions, effects, parent)


	def retranslateUi(self, showprogress):
		showprogress.setWindowTitle(_(u"Affichage de la progression"))
		self.barProgress.setToolTip(_(u"Progression de l\'encodage"))
		self.infoText.setToolTip(_(u"Messages de SoX"))
		self.fermer.setToolTip(_(u"Fermer la fenêtre"))
		self.fermer.setText(_(u"Fermer"))
		self.fermer.setShortcut(_(u"Alt+S"))

	def setSignal(self, critereFile, critereProgress) :
		self.processAudio.critereFile = critereFile
		self.processAudio.critereProgress = critereProgress

	def run(self) :
		self.connect(self.processAudio, SIGNAL("progress(int)"), self.setProgress)
		self.connect(self.processAudio, SIGNAL("endProcess(QString)"), self.endAction)
		self.connect(self.processAudio, SIGNAL("DisplayText"), self.addText)
		self.processAudio.start()

	def setProgress(self, prg) :
		self.barProgress.setValue(prg)

	def endAction(self, msg) :
		self.barProgress.setValue(100)
		self.fermer.setEnabled(True)
		self.emit(SIGNAL("endProcess"), msg)

class soxEngine(QThread) :

	def __init__(self, cheminAudioSource, cheminAudioSorti, nfile, globalOptions=u"", outputFileOptions=u"", effects=u"", parent=None) :
		super(soxEngine, self).__init__(parent)
		self.cheminAudioSource = unicode(cheminAudioSource)
		self.cheminAudioSorti = unicode(cheminAudioSorti)
		self.effects = unicode(effects)
		self.globalOptions = unicode(globalOptions)
		self.outputFileOptions = unicode(outputFileOptions)
		self.critereFile = u""
		self.critereProgress = u""
		self.nfile = nfile
		self.avancement = 0
		self.avancementFile = 0
		self.fileT = -1


	def run(self):
		commande = u"sox -S "+self.globalOptions+u" "+self.cheminAudioSource+u" "+self.outputFileOptions+u" \""+self.cheminAudioSorti+u"\" "+self.effects
		### Debug
		#print commande
		try :
			#self.mesg = subprocess.Popen(commande.encode(EkdConfig.coding), universal_newlines=True, bufsize=0, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
			self.mesg = EkdProcess(commande.encode(EkdConfig.coding), outputerr=subprocess.STDOUT)
		except Exception, e:
			print u"Erreur dans le lancement de %s\n(%s)" % (commande, e)
			raise
		self.retCode = None
		while self.retCode == None :
			self.progression()
			self.retCode = self.mesg.poll()
			#self.usleep(10)
		self.finEncodage(self.retCode)

	def progression(self):
		"""
		Recupération de la progression du process en cours
		"""
		tampon = self.mesg.stdout.readline()
		### Debug
		#print tampon
		progre = 0
		# on récupère les lignes de Sox
		if self.critereFile != u"" and tampon.find(str(self.critereFile))!= -1 :
			self.emit(SIGNAL("DisplayText"),QString(tampon))
			self.fileT += 1
			avInst = float(self.fileT*100/self.nfile)
			if self.avancementFile < avInst : 
				self.avancementFile = avInst
				self.emit(SIGNAL("progress(int)"),int(self.avancementFile))

		if self.critereProgress != u"" and tampon.find(str(self.critereProgress))!= -1 :
			try :
				pr1 = tampon.split(":")
				pr2 = pr1[1].split("%")
				progre = int(float(pr2[0]))
			except :
				None
			avInst = self.avancementFile + float(progre/self.nfile)
			if self.avancement < avInst : 
				self.avancement = avInst
				self.emit(SIGNAL("progress(int)"),int(self.avancement))

		elif self.critereProgress != u"" and tampon.find("Time:")!=-1 :
			try :
				pr1 = tampon.split("(")
				pr2 = pr1[1].split("%")
				progre = int(float(pr2[0]))
			except :
				None
			avInst = self.avancementFile + float(progre/self.nfile)
			if self.avancement < avInst : 
				self.avancement = avInst
				self.emit(SIGNAL("progress(int)"),int(self.avancement))

	def finEncodage(self, statutDeSortie):
		"""choses à faire à la fin de l'encodage audio"""
		if statutDeSortie==1:
			print "Crash de l'encodeur!"
			self.emit(SIGNAL("DisplayText"),u"Crash de l'encodeur !")
			self.fermer.setEnabled(True)
			return

		else :
			self.emit(SIGNAL("endProcess(QString)"), self.cheminAudioSorti)
			print self.cheminAudioSorti
			self.emit(SIGNAL("DisplayText"),u"Encodage terminé avec succès")
