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

class MusiqueSon_normalize(Base):
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
		self.idSection = "son_normaliser_convertir_musique_ou_son"

		super(MusiqueSon_normalize, self).__init__(None, None, None, 'vbox') # Base module de animation
		self.setTitle(_(u"Normaliser et convertir un fichier audio"))
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
		niveau = QGroupBox(_(u"Choix du niveau"))
		self.choix1 = QRadioButton(_(u"- 3 dB"))
		self.choix2 = QRadioButton(_(u"- 6 dB"))
		self.choix3 = QRadioButton(_(u"- 9 dB"))
		self.choix1.setChecked(True)
		nivLayout = QHBoxLayout()
		nivLayout.addWidget(self.choix1)
		nivLayout.addWidget(self.choix2)
		nivLayout.addWidget(self.choix3)
		niveau.setLayout(nivLayout)
		regVLayout.addWidget(niveau)

		mode = QGroupBox(_(u"Choix du mode de normalisation"))
		self.choixm1 = QRadioButton(_(u"Standard"))
		self.choixm2 = QRadioButton(_(u"Individuel"))
		self.choixm3 = QRadioButton(_(u"Balancé"))
		self.choixm1.setChecked(True)
		modeLayout = QHBoxLayout()
		modeLayout.addWidget(self.choixm1)
		modeLayout.addWidget(self.choixm2)
		modeLayout.addWidget(self.choixm3)
		mode.setLayout(modeLayout)
		regVLayout.addWidget(mode)

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
		self.infoLog(None, None, self.selectionAudioFile.getFile(), sortie)

	def afficherAide(self):
		""" Boîte de dialogue de l'aide """
		self.aide = EkdAide(550,400,self)
		self.aide.setText(_(u"<p><b>Ici vous pouvez normaliser des fichiers audio, c'est à dire ajuster leur volume sonore. Voici une définition selon Wikipédia de la normalisation audio:<br>http://fr.wikipedia.org/wiki/Normalisation_audio</b></p><p>Dans l'onglet <b>Son(s) source</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les fichiers(s) audio. Si vous voulez sélectionner plusieurs fichiers audio d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos fichiers audio), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner un fichier audio dans la liste et le lire (par le bouton juste à la droite de cette liste). De même si vous le désirez, vous pouvez obtenir des informations complètes sur le fichier audio sélectionné, et ce par le bouton <b>Infos</b> (en bas).</p><p>Dans l'onglet <b>Réglages</b> sélectionnez le <b>Format du fichier de sortie</b>, et s'il le faut <b>Réglage expert</b> et faites éventuellement le réglage de la <b>Qualité d'encodage</b>, puis réglez le <b>Choix du niveau</b> et le <b>Choix du mode de normalisation</b>.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>Appliquer</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>Nom de fichier</b>, cliquez sur le bouton <b>Enregistrer</b> et attendez le temps de la conversion. A la fin du traitement cliquez sur le bouton <b>Fermer</b> de la fenêtre <b>Affichage de la progression</b>.</p><p>Dans l'onglet <b>Son créé</b> vous pouvez lire le résultat.</p><p>L'onglet <b>Infos</b> vous permet de voir les fichiers audio chargés (avec leurs chemins exacts) avant et après conversion.</p>"))
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

		# Définition des options
		if self.choix1.isChecked() :
			db = " -3 "
		if self.choix2.isChecked() :
			db = " -6 "
		if self.choix3.isChecked() :
			db = " -9 "
		if self.choixm1.isChecked() :
			mde = ""
		if self.choixm2.isChecked() :
			mde = "-i"
		if self.choixm3.isChecked() :
			mde = "-b"
		option = "norm "+mde+db

		if self.selectionFile.reglageExp.getExpertState() :
			regExp = self.selectionFile.reglageExp.getC()
		else :
			regExp = u""

		# Encodage
		self.process = SoxProcess(chemin, cheminAudioSorti, 1, u"", u""+regExp, option, self.parent)
		self.process.setSignal(u"Input",u"In:")
		self.process.show()
		self.process.run()
		self.connect(self.process,SIGNAL("endProcess"),self.endProcess)

	def load(self) :
		self.selectionAudioFile.loadFileLocation(self.idSection)
		self.selectionFile.reglageExp.loadConfig(self.idSection)
		self.choix1.setChecked(int(EkdConfig.get(self.idSection, 'choix1')))
		self.choix2.setChecked(int(EkdConfig.get(self.idSection, 'choix2')))
		self.choix3.setChecked(int(EkdConfig.get(self.idSection, 'choix3')))
		self.choixm1.setChecked(int(EkdConfig.get(self.idSection, 'choixm1')))
		self.choixm2.setChecked(int(EkdConfig.get(self.idSection, 'choixm2')))
		self.choixm3.setChecked(int(EkdConfig.get(self.idSection, 'choixm3')))

	def save(self) :
		self.selectionAudioFile.saveFileLocation(self.idSection)
		self.selectionFile.reglageExp.saveConfig(self.idSection)
		EkdConfig.set(self.idSection, u'choix1', unicode(int(self.choix1.isChecked())))
		EkdConfig.set(self.idSection, u'choix2', unicode(int(self.choix2.isChecked())))
		EkdConfig.set(self.idSection, u'choix3', unicode(int(self.choix3.isChecked())))
		EkdConfig.set(self.idSection, u'choixm1', unicode(int(self.choixm1.isChecked())))
		EkdConfig.set(self.idSection, u'choixm2', unicode(int(self.choixm2.isChecked())))
		EkdConfig.set(self.idSection, u'choixm3', unicode(int(self.choixm3.isChecked())))
		
