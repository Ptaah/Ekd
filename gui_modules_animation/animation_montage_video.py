#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.EkdWidgets import EkdLabel
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Animation_MontagVideo(QWidget):
	# -----------------------------------------
	# Cadre accueillant les widgets de :
	# Animation >> Montage vidéo
	# -----------------------------------------
	def __init__(self, parent):
        	QWidget.__init__(self)
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "none" # Défini le type de fichier source.
		self.typeSortie = "none" # Défini le type de fichier de sortie.
		self.sourceEntrees = None # Fait le lien avec le sélecteur de fichier source.


		# Titre de la page
		txt = _(u"Montage Vidéo:")
		self.titre_du_cadre=QLabel("<H2><center><u>%s</u></center></H2>" %txt)
		
		# Lien vers les sous-cadres
		self.labelVideoSeul = EkdLabel(_(u"Montage: Vidéo Seul"))
		self.labelVideoAudio = EkdLabel(_(u"Montage: Vidéo et Audio"))
		self.labelDecouperVideo = EkdLabel(_(u"Montage: Découper une Vidéo"))
		
		# Ajout du titre de la page a la boite verticale
		vbox.addWidget(self.titre_du_cadre)
		vbox.addSpacing(10)
		vbox.addWidget(self.labelVideoSeul)
		vbox.addWidget(self.labelVideoAudio)
		vbox.addWidget(self.labelDecouperVideo)
		
		vbox.addStretch()
		self.connect(self.labelVideoSeul, SIGNAL("click"), self.majVideoSeul)
		self.connect(self.labelVideoAudio, SIGNAL("click"), self.majVideoAudio)
		self.connect(self.labelDecouperVideo, SIGNAL("click"), self.majDecouperVideo)
		self.parent=parent

	def majVideoSeul(self):
		''' 
		Fonction qui sera connecté lors du click sur le menu Vidéo Seul
		'''
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.treeWidgetAnimation.currentItem(), 0)
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.itemTree_SVideo, 1)
		self.parent.stacked_onglet_animation.setCurrentIndex(self.parent.stacked_animation_MontagVideoVidSeul)

	def majVideoAudio(self):
		''' 
		Fonction qui sera connecté lors du click sur le menu Vidéo Audio
		'''
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.treeWidgetAnimation.currentItem(), 0)
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.itemTree_SVideoAudio, 1)
		self.parent.stacked_onglet_animation.setCurrentIndex(self.parent.stacked_animation_MontagVideoVidPlusAudio)

	def majDecouperVideo(self):
		''' 
		Fonction qui sera connecté lors du click sur le menu Découper une vidéo
		'''
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.treeWidgetAnimation.currentItem(), 0)
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.itemTree_SDecouperVideo, 1)
		self.parent.stacked_onglet_animation.setCurrentIndex(self.parent.stacked_animation_MontagVideoDecoupUneVideo)

	def load(self) :
		#print "Section montage video"
		EkdPrint(u"Section montage video")

	def save(self) :
		#print "Section montage video"
		EkdPrint(u"Section montage video")

