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
from gui_modules_animation.animation_montage_video_decoup_une_vid import *
from music_son_base_sox import SoxProcess, choixSonSortieWidget
from gui_modules_common.EkdWidgets import EkdAide

class MusiqueSon_decoupe(Animation_MontagVideoDecoupUneVideo):
	"""Class pour la découpe de fichier son. Class dérivée de celle permettant de découper une vidéo dans le module animation"""
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Musique-Son >> Encodage
	# -----------------------------------
	def __init__(self, parent):
		super(MusiqueSon_decoupe, self).__init__(parent)
		# Vérification des possibilités de Sox pour l'encodage
		self.setTitle(_(u"Découpe de musiques et de sons"))

		self.parent = parent
		# -------------------------------
		# Divergeances par rapport à la class Musique Son_decoupe
		# -------------------------------
		self.idSection = "son_decoupe_musiques_et_sons"
		# -------------------------------------------------------------------
		# Boîte de groupe : "Fichier audio source"
		# -------------------------------------------------------------------
		self.radioSource.setText(_(u"Fichier son source"))
		self.radioConvert.setText(_(u"Son final"))
		self.mplayer.cibleVideo.hide()
		self.mplayer.conf.hide()
		self.mplayer.setToolTip(_(u"La lecture du fichier audio est nécessaire pour achever la sélection d'une zone de la piste audio"))
		self.boutExtractionSon.hide()
		### Option de fade in / fade out sur le son decoupe
		hlbox = QHBoxLayout()
		self.fadeIn = QCheckBox(_(u"Fade in"))
		self.fadeIn.setDisabled(True)
		self.fadeInTime = QDoubleSpinBox()
		self.fadeInTime.setDecimals(3)
		self.fadeInTime.setRange(0.500, 5.000)
		self.fadeInTime.setValue(1.000)
		self.fadeInTime.setDisabled(True)
		self.fadeOut = QCheckBox(_(u"Fade out"))
		self.fadeOut.setDisabled(True)
		self.fadeOutTime = QDoubleSpinBox()
		self.fadeOutTime.setDecimals(3)
		self.fadeOutTime.setRange(0.500, 5.000)
		self.fadeOutTime.setValue(1.000)
		self.fadeOutTime.setDisabled(True)
		self.boutMarqFinSelect_max.setToolTip(_(u"Marquer la fin de la sélection au temps maximum (t=\"la durée de la piste audio\")"))
		hlbox.addStretch(100)
		hlbox.addWidget(self.fadeIn)
		hlbox.addWidget(self.fadeInTime)
		hlbox.addStretch(20)
		hlbox.addWidget(self.fadeOut)
		hlbox.addWidget(self.fadeOutTime)
		hlbox.addStretch(100)
		self.layoutReglage.insertLayout(3,hlbox)
		### Pour n'activer les QDoubleSpinBox que lorsque les QCheckBox correspondantes
		### sont activees.
		self.connect(self.fadeIn, SIGNAL("stateChanged(int)"), self.fadeInTime.setEnabled)
		self.connect(self.fadeOut, SIGNAL("stateChanged(int)"), self.fadeOutTime.setEnabled)

		### Zone de selection du format de sortie de fichier
		hbox = QHBoxLayout()
		# Utilisation du widget choixSonSortieWidget
		self.choixFormatAudio = choixSonSortieWidget(self.parent.soxSuppFormat, parent=self)
		extFormat=[]
		for fmt in self.parent.soxSuppFormat :
			extFormat.append("*."+fmt)
		hbox.addWidget(self.choixFormatAudio)
		self.layoutReglage.insertLayout(0,hbox)
		#-------------------------------------------------------------------
		# Modification de la nouvelle interface d'ajout des videos pour l'adapter aux fichiers son
		self.afficheurVideoSource=SelectWidget(extensions = extFormat, mode="texte", audio = True)
		# Onglets
		self.tab.removeTab(0)
		self.indexVideoSource = self.tab.insertTab(0,self.afficheurVideoSource, _(u'Son(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		#--------------------------------------------------------------------
		self.tab.setCurrentIndex(0)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "audio" # Défini le type de fichier source.
		self.typeSortie = "audio" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.


	def getFile(self):
		'''
		# Modifié par rapport à la fonction getFile de la class decoupe_video
		On utilise la nouvelle interface de récupération des fichiers sources slectionnés
		'''
		self.chemin = unicode(self.afficheurVideoSource.getFile())
		if not self.chemin:
			### Desactive les options si pas de fichier d'entree introduit.
			self.fadeIn.setDisabled(True)
			self.fadeInTime.setDisabled(True)
			self.fadeOut.setDisabled(True)
			self.fadeOutTime.setDisabled(True)
			return

		# Affichage du chemin + nom de fichier dans la ligne d'édition
		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = [self.chemin]
		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioConvert.setChecked(False)
		self.radioApercu.setChecked(False)
		self.fadeIn.setEnabled(True)
		self.fadeOut.setEnabled(True)
		self.miseAZeroSelect()
		# les boutons de marquage apparaissent
		self.frameMarque.setEnabled(True)


	def afficherAide(self):
		""" Boîte de dialogue de l'aide """
		self.aide = EkdAide(550,280,self)
		self.aide.setText(_(u"""<p><b>Vous pouvez ici découper un fichier audio et ainsi en garder uniquement la partie qui vous intéresse.</b></p><p><font color='green'>Ce cadre est assez différent des autres, vous avez tout d'abord la zone d'écoute audio, comprenant les boutons marche, arrêt et le compteur, la glissière de défilement, la zone d'affichage de la découpe (les parties découpées seront affichées en vert), les boutons début/fin de sélection, remise à zéro, à la doite de ce dernier bouton, vous avez trois minuscules boutons contenant +, = et - (ils servent à accélérer ou diminuer la vitesse de lecture du fichier audio), une première case à cocher <b>Fade in</b> (qui peut appliquer un effet de fondu au début de la découpe du son), juste à la droite, le réglage du fondu, une deuxième case à cocher <b>Fade out</b> (qui peut appliquer un effet de fondu à la fin de la découpe du son), le réglage du fondu correspondant, puis les choix d'écoute <b>Fichier son source</b>, <b>aperçu</b> et <b>Son final</b>.</font></p><p><b>Tout ce qui vient de vous être décrit se trouve dans l'onglet Réglages</b>.</p><p>Dans l'onglet <b>Son(s) source</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les fichier(s) audio. Si vous voulez sélectionner plusieurs fichiers audio d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos fichiers), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner un fichier audio dans la liste et l'écouter (par le bouton juste à la droite de cette liste). De même si vous le désirez, vous pouvez obtenir des informations complètes sur le fichier audio sélectionné, et ce par le bouton <b>Infos</b> (en bas).</p><p>Dans l'onglet <b>Réglages</b>, lancez l'écoute du fichier audio (par le bouton avec la flèche orientée vers la droite <b>La lecture du fichier audio est nécessaire ...</b>), pour la vitesse de lecture, profitez des boutons + ou - pour augmenter ou diminuer la vitesse de lecture <b>(plus vous diminuez la vitesse de lecture, plus la découpe pourra se faire de façon précise)</b>, cliquez ensuite sur le bouton <b>Marquer le début de la sélection</b> ou <b>Marquer le début de la sélection au temps minimum (t=0)</b> (pour sélectionner le fichier audio à son tout début), laissez jouer (écoutez la musique ou le son) et cliquez sur le bouton <b>Marquer la fin de la sélection</b> au moment propice (ou <b>Marquer la fin de la sélection au temps maximum t="la durée du fichier audio"</b> pour garder le dit fichier audio jusqu'à la fin).</p><p><font color='blue'>Sachez que vous pouvez revenir aux paramètres par défaut en cliquant sur le bouton <b>Remettre à zéro les paramètres</b> (les deux flèches vertes inversées), vous devrez alors rejouer le fichier audio et recommencer vos différentes sélections.</font></p><p>Cliquez sur le bouton <b>Appliquer</b>, sélectionnez le répertoire de sauvegarde de votre fichier audio, entrez le <b>Nom de Fichier</b> dans le champ de texte réservé à cet effet ... cliquez sur le bouton <b>Enregistrer</b> et attendez le temps de la conversion. A la fin du traitement cliquez sur le bouton <b>Fermer</b> de la fenêtre <b>Affichage de la progression</b>.</p><p>Vous pouvez visionner votre fichier audio (avant la conversion) en sélectionnant <b>Fichier son source</b>, après la conversion <b>Son final</b>.</p><p>L'onglet <b>Infos</b> vous permet de voir les fichiers audio chargés (avec leurs chemins exacts) avant et après conversion.</p>"""))
		self.aide.show()


	def tempsToHMSMS(self,sec) :
		"""Fonction de conversion du temps en seconde vers le temps en HH:MM:SS.MSE"""
		heure = int(sec/3600.0)
		minute = int((sec-heure*3600.0)/60.0)
		seconde = int(sec-heure*3600.0-minute*60.0)
		millisec = int((sec-heure*3600.0-minute*60.0-seconde)*1000.0)
		return u"%02d:%02d:%02d.%d" % (heure, minute, seconde, millisec)

	def appliquer(self):
		"""Découpage du fichier son"""

		# suffix du fichier actif
		suffix=os.path.splitext(self.chemin)[1]
		if suffix == u".mp3" or suffix == u".MP3" :
			chemin = u"-t mp3 \""+self.chemin+u"\""
		elif suffix == u".ogg" or suffix == u".OGG" :
			chemin = u"-t ogg \""+self.chemin+u"\""
		elif suffix == u".mp2" or suffix == u".MP2" :
			chemin = u"-t mp2 \""+self.chemin+u"\""
		elif suffix == u".flac" or suffix == u".FLAC" :
			chemin = u"-t flac \""+self.chemin+u"\""
		else :
			chemin = u"\""+self.chemin+u"\""

		suffixSortie = u".%s" % (self.parent.soxSuppFormat[self.choixFormatAudio.formatSound.currentIndex()])
		saveDialog = EkdSaveDialog(self, os.path.expanduser(self.repSortieProv()), suffixSortie, _(u"Sauver"))
		self.fichierSortie = saveDialog.getFile()

		if not self.fichierSortie: return

		tempsDebut = self.tempsToHMSMS(self.valeurDebut)
		dureeSelection = self.tempsToHMSMS(self.valeurFin - self.valeurDebut)

		if (self.fadeIn.isChecked() and self.fadeIn.isEnabled()) or \
				(self.fadeOut.isChecked() and self.fadeOut.isEnabled()):
			if self.fadeIn.isChecked() and self.fadeIn.isEnabled() :
				fadeIn = u"00:00:0%f" % (self.fadeInTime.value())
			else :
				fadeIn = u"00:00:00.000"
			if self.fadeOut.isChecked() and self.fadeOut.isEnabled() :
				fadeOut = u"00:00:0%f" % (self.fadeOutTime.value())
			else :
				fadeOut = u"00:00:00.000"

			fadeOption = u"fade %s %s %s" % (fadeIn, dureeSelection, fadeOut)
		else :
			fadeOption = u""
		### Pour le debugage
		print "extension :", suffix, type(suffix)
		print "début : ", self.valeurDebut
		print "fin : ", self.valeurFin
		print "temps début formaté : ", dureeSelection
		print "durée : ", dureeSelection
		print "Input file : ", chemin
		print "Fichier de sortie : ", self.fichierSortie
		print u"option : trim %s %s" %(tempsDebut, dureeSelection)
		if self.choixFormatAudio.reglageExp.getExpertState() :
			optSortie = self.choixFormatAudio.reglageExp.getC()
		else :
			optSortie = u""

		### Encodage avec le module soxProcess
		self.process = SoxProcess(chemin, self.fichierSortie, 1, u"", optSortie, u"trim %s %s %s" %(tempsDebut, dureeSelection, fadeOption))
		self.process.setSignal("Input","In:")
		self.process.show()
		self.process.run()
		self.connect(self.process,SIGNAL("endProcess"),self.endProcess)

	def endProcess(self, sortie) :
		"""Actions à réaliser lors de la fin du processus d'encodage si celui-ci se termine correctement"""
		self.radioSource.setEnabled(True)
		self.radioConvert.setEnabled(True)
		### Info sur le traitement effectué.
		self.infoLog(None, None, self.chemin, self.fichierSortie)

	def load(self) :
		self.loadFiles()
		self.choixFormatAudio.reglageExp.loadConfig(self.idSection)

	def save(self) :
		self.saveFiles()
		self.choixFormatAudio.reglageExp.saveConfig(self.idSection)
