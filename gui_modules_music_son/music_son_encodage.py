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
from moteur_modules_animation.mplayer import *
from gui_modules_common.gui_base import Base
from music_son_base_sox import SoxProcess, choixSonSortieWidget
from gui_modules_common.EkdWidgets import EkdSaveDialog, EkdAide
from gui_modules_image.selectWidget import SelectWidget
from moteur_modules_common.EkdConfig import EkdConfig

class MusiqueSon_Encodage(Base):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Musique-Son >> Encodage
	# -----------------------------------
	def __init__(self, parent):
		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------
		self.config=EkdConfig

		self.parent = parent
		#=== Identifiant de la classe ===#
		self.idSection = "son_musique_encodage"

		super(MusiqueSon_Encodage, self).__init__(None, None, None, 'vbox') # Base module de animation
		self.setTitle(_(u"Convertir un fichier audio"))
		self.printSection()

		#------------------------------------------------------------------------
		# TabWidget pour les réglages et pour l'écoute du résultat
		#------------------------------------------------------------------------
		extFormat=[]
		for fmt in self.parent.soxSuppFormat :
			extFormat.append("*."+fmt)

		# Widget standard de sélection de fichier audio dans le tab standard
		self.selectionAudioFile = SelectWidget(extensions = extFormat, mode="texte", audio = True)
		# Onglets
		self.tab.insertTab(0,self.selectionAudioFile, _(u'Son(s) source'))
		self.connect(self.selectionAudioFile,SIGNAL("fileSelected"),self.synchroFiles)
		self.connect(self.selectionAudioFile, SIGNAL("pictureChanged(int)"), self.synchroFiles)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "audio" # Défini le type de fichier source.
		self.typeSortie = "audio" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.selectionAudioFile # Fait le lien avec le sélecteur de fichier source.

		# -------------------------------------------------------------------
		# Sélection et affichage des fichiers à joindre : "Fichiers audio source"
		# -------------------------------------------------------------------
		reglage = QWidget()
		regVLayout = QVBoxLayout(reglage)
		self.selectionFile = choixSonSortieWidget(self.parent.soxSuppFormat, parent=self)
		regVLayout.addWidget(self.selectionFile)
		

		regVLayout.addStretch()
		self.tab.addTab(reglage,_(u"Réglage"))

		#------------------------------------------------------------------------
		# Ecoute du résultat
		#------------------------------------------------------------------------
		#=== Widgets mplayer ===#
		widget = QWidget()
		vboxMplayer = QVBoxLayout(widget)
		vboxMplayer.addStretch()
		hbox = QHBoxLayout()
		vboxMplayer.addLayout(hbox)
		hbox.addStretch()

		self.mplayer=Mplayer(taille=(300,270), facteurLimitant=Mplayer.LARGEUR,
			choixWidget=(Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_A_PART))
		self.mplayer.setAudio(True)
		hbox.addWidget(self.mplayer)
		hbox.addStretch()
		vboxMplayer.addStretch()

		self.mplayer.setEnabled(False)
		self.tab.addTab(widget, _(u"Son créé"))

		### pour les infos supplémentaires
		self.addLog()
		# -------------------------------------------------------------------
		# widgets du bas : ligne + boutons Aide et Appliquer
		# -------------------------------------------------------------------

	def synchroFiles(self):
		if len(self.selectionAudioFile.getFiles()) > 0 :
			self.boutApp.setEnabled(True)
		else :
			self.boutApp.setEnabled(False)

	def endProcess(self, sortie) :
		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = [sortie]
		self.tab.setCurrentIndex(1)
		### Info sur le traitement effectué.
		self.infoLog(None, None, self.selectionAudioFile.getFile(), sortie)

	def afficherAide(self):
		""" Boîte de dialogue de l'aide """
		self.aide = EkdAide(550,400,self)
		self.aide.setText(_(u"<p><b>Ici vous pouvez transcoder des fichiers audio (avec extension .ogg, .mp3, .wav, .ac3, .wmv et .mp2) en un fichier audio d'un type différent.</b></p><p>Dans l'onglet <b>Son(s) source</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les fichiers(s) audio. Si vous voulez sélectionner plusieurs fichiers audio d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos fichiers audio), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner un fichier audio dans la liste et le lire (par le bouton juste à la droite de cette liste). De même si vous le désirez, vous pouvez obtenir des informations complètes sur le fichier audio sélectionné, et ce par le bouton <b>Infos</b> (en bas).</p><p>Dans l'onglet <b>Réglages</b> sélectionnez le <b>Format du fichier de sortie</b>, et s'il le faut <b>Réglage expert</b> et faites éventuellement le réglage de la <b>Qualité d'encodage</b>.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>Appliquer</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>Nom de fichier</b>, cliquez sur le bouton <b>Enregistrer</b> et attendez le temps de la conversion. A la fin du traitement cliquez sur le bouton <b>Fermer</b> de la fenêtre <b>Affichage de la progression</b>.</p><p>Dans l'onglet <b>Son créé</b> vous pouvez lire le résultat.</p><p>L'onglet <b>Infos</b> vous permet de voir les fichiers audio chargés (avec leurs chemins exacts) avant et après conversion.</p>"))
		self.aide.show()

	def appliquer(self):
		""" appelle la boite de dialogue de sélection de fichier à sauver """

		suffixSortie = u"."+self.selectionFile.getFileExt()
		saveDialog = EkdSaveDialog(self, mode="audio", suffix=suffixSortie, title=_(u"Sauver"))
		cheminAudioSorti = saveDialog.getFile()


		if not cheminAudioSorti: return

		# récupération du chemin des fichiers audio source
		cheminAudioSource=self.selectionAudioFile.getFile()
		# suffix du fichier actif
		suffix=os.path.splitext(cheminAudioSource)[1]
		if suffix == u".mp3" or suffix == u".MP3" :
			chemin = u"-t mp3 \""+cheminAudioSource+u"\""
		elif suffix == u".ogg" or suffix == u".OGG" :
			chemin = u"-t ogg \""+cheminAudioSource+u"\""
		elif suffix == u".mp2" or suffix == u".MP2" :
			chemin = u"-t mp2 \""+cheminAudioSource+u"\""
		elif suffix == u".flac" or suffix == u".FLAC" :
			chemin = u"-t flac \""+cheminAudioSource+u"\""
		else :
			chemin = u"\""+cheminAudioSource+u"\""


		if self.selectionFile.reglageExp.getExpertState() :
			regExp = self.selectionFile.reglageExp.getC()
		else :
			regExp = u""

		# Encodage
		self.process = SoxProcess(chemin, cheminAudioSorti, 1, u"", u""+regExp, u"", self.parent)
		self.process.setSignal(u"Input",u"In:")
		self.process.show()
		self.process.run()
		self.connect(self.process,SIGNAL("endProcess"),self.endProcess)

	def load(self) :
		self.selectionAudioFile.loadFileLocation(self.idSection)
		self.selectionFile.reglageExp.loadConfig(self.idSection)

	def save(self) :
		self.selectionAudioFile.saveFileLocation(self.idSection)
		self.selectionFile.reglageExp.saveConfig(self.idSection)
