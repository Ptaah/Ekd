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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from moteur_modules_animation.mplayer import *
from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from videoporama_widget import *
from gui_modules_common.EkdWidgets import EkdSaveDialog, EkdAide

class Videoporama_Main(Base) : #OK QT4
		def __init__(self, verifsformats, parent=None):
			super(Videoporama_Main, self).__init__(boite='vbox', titre=_(u"Diaporama d'images en vidéo"))
			#=== Drapeaux ===#
			# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)

			# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
			self.modifImageSource = 0

			# Fonction appelant la fenêtre principale
			self.mainWindowFrameGeometry = parent.frameGeometry

			layout = QVBoxLayout()
			self.tabW=QTabWidget()

			self.afficheurImgSource=SelectWidget(geometrie = self.mainWindowFrameGeometry)

			self.dicoTab = {}

			self.dicoTab['images']=self.add(self.afficheurImgSource, _(u'Image(s) source(s)'))
			self.idSection = 'videoporama'
			## ---------------------------------------------------------------------
			# Variables pour la fonction tampon
			## ---------------------------------------------------------------------
			self.typeEntree = "image" # Défini le type de fichier source.
			self.typeSortie = "video" # Défini le type de fichier de sortie.
			self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.

			#=== Widget réglages videoporama ===#
			self.vid_widg=vid_widg(verifsformats, parent) # Class vid_widg est dans videoporama_widget.py
			self.add(self.vid_widg,_(u"Réglages"))

			self.addPreview(light=True)
			self.addLog()
			#----------------------------------------------------------------------------------------------------
			# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
			#----------------------------------------------------------------------------------------------------
			self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)

		def saveprj(self, url) :
			self.vid_widg.saveprojet(url)

		def loadprj(self,url) :
			self.vid_widg.affichedata(url,n=1,disp=self.afficheurImgSource)
			if self.vid_widg.timeline.columnCount() > 0 :
				self.boutApp.setEnabled(1)

		def load(self) :
			print "Diaporama"

		def save(self) :
			print "Diaporama"

		def empty(self) :
			self.afficheurImgSource.toutSupprimer()

		def modifBoutonsAction(self, i):
			"""On active ou désactive les boutons d'action selon s'il y a des images ou pas dans le widget de sélection
			Transfert et synchronisation des images vers la timeline de videoporama"""
			self.boutApp.setEnabled(i)
			if i :
				self.modifImageSource = 1
				lfiles=self.afficheurImgSource.getFiles()
				tlfiles=self.vid_widg.getFilesList()
				z=0
				for F in tlfiles :
					if F in lfiles :
						lfiles.remove(F)
						z+=1
					else :
						self.vid_widg.delete(z)
				self.vid_widg.add2(lfiles)
			else :
				self.modifImageSource = 0
				self.vid_widg.empty()

		def appliquer(self) :
			""" Démarrage du processus d'encodage des images en diaporama vidéo"""

			format=self.vid_widg.data.getElementsByTagName('outputf')[0].childNodes[0].nodeValue
			filter=u"."+self.vid_widg.verifsformats[5][int(format)][2]
			print "DEBUG : Format du fichier : ", format, "Filter : ", filter
                        # XXX Check that the output directory is correctly set.
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=filter, title=_(u"Sauver"))
			self.outputfile = saveDialog.getFile()

			if not self.outputfile : return
			self.vid_widg.updatexml(self.vid_widg.data,"outputfile",self.outputfile)
			self.vid_widg.process()
			self.connect(self.vid_widg.prc, SIGNAL("resProcess"), self.activideo)

		def activideo(self,ofile, image=None, video=None, audio=None, sortie=None) :
			""" visualisation de la video finalisée """
			self.mplayer.listeVideos = [ofile]
			self.mplayer.setEnabled(True)
			self.tabW.setCurrentIndex(2)
			self.infoLog(image, video, audio, sortie)

		def afficherAide(self) :
			""" Boîte de dialogue d'aide """
			self.aide = EkdAide(600,700,self)
			self.aide.setText(_(u"<p><b>Le module diaporama permet de créer des fichiers vidéo de diaporama à partir d'images fixes. Selon la définition de Wikipédia: 'Un diaporama est un spectacle de projection de diapositives ; par extension on entend par ce terme toute suite d'images ou de documents reliés par des effets et, sur lesquels il est possible de mettre du son.'. Source:<br>http://fr.wikipedia.org/wiki/Diaporama</b></p>\
				<p>La composition d'un diaporama se passe en 5 étapes principales : \
				<ol> \
					<li>Sélection des images sources : Ceci est réalisé dans l'onglet \"Image(s) source(s))\".</li> \
					<li>Définition de l'ordre d'apparition des images dans le diaporama : Cette opération se fait dans l'onglet \"réglages\". L'ordre d'apparition des images est celui de la ligne du temps dans laquelle se retrouve les miniatures des images à traiter. Pour changer l'ordre, il suffit de sélectionner l'image à déplacer et de la déplacer au moyen des icônes avec les flèches gauche ou droite.</li> \
					<li>Réglages sur le montage : Cette étape est réalisée dans le premier onglet de la zone d'option (onglet \"Options du montage\"). Il faut alors définir le format d'image, la résolution de la vidéo de sortie, le format et l'éventuelle bande son (fichier) à ajouter au montage.</li> \
					<li>Réglages spécifiques par image : Ces réglages sont réalisés dans les 3 derniers onglets de la zone de réglage (\"Image\", \"Texte\" et \"Zoom et survol\"). Pour changer les réglages d'une image, il faut d'abord la sélectionner dans la ligne du temps. L'image sélectionnée est alors affichée dans la zone de prévisualisation. Dans l'onglet \"Image\" il est possible de définir le temps d'affichage de l'image dans le diaporama (en seconde), d'ajouter une couleur ou une image de fond (pour les images orientées en portrait) et de défini l'effet de transition qui sera effectué entre l'image sélectionnée et l'image suivante. Dans l'onglet \"Texte\", il est possible d'ajouter un ou plusieurs texte(s) sur l'image et enfin dans l'onglet \"Zoom et survol\" il est possible de définir les caractéristiques d'un survol de l'image de départ entre une sélection dans l'image (appelée image de départ) et une autre sélection (appelée image de fin).</li> \
					<li>Pour réaliser le montage, il reste à appuyer sur le bouton \"Appliquer\" et attendre la fin e l'encodage. Le résultat peut ensuite être visualisé dans l'onglet \"Vidéo créée\".</li></ol><\p> \
				<p>Une aide plus détaillée sur ce module est également disponible dans le répertoire ekd/videoporama/help</p>"))
			self.aide.show()

