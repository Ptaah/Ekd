#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.EkdWidgets import EkdLabel
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

class Animation_Encodage(QWidget):
	# -----------------------------------------
	# Cadre accueillant les widgets de :
	# Animation >> Encodage
	# -----------------------------------------
	def __init__(self, parent):
        	QWidget.__init__(self)
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# Titre de la page
		txt = _(u"Transcodage:")
		self.titre_du_cadre=QLabel("<H2><center><u>%s</u></center></H2>" %txt)

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "none" # Défini le type de fichier source.
		self.typeSortie = "none" # Défini le type de fichier de sortie.
		self.sourceEntrees = None # Fait le lien avec le sélecteur de fichier source.

		# Lien vers les sous-cadres
		self.labelGeneral = EkdLabel(_(u"Transcodage: Général"))
		self.labelPourLeWeb = EkdLabel(_(u"Transcodage: Pour le web"))
		self.labelHauteDefinition = EkdLabel(_(u"Transcodage: Haute définition"))
		self.labelAVCHD = EkdLabel(_(u"Transcodage: Gestion de l'AVCHD"))
		
		# Ajout du titre de la page a la boite verticale
		vbox.addWidget(self.titre_du_cadre)
		vbox.addSpacing(10)
		vbox.addWidget(self.labelGeneral)
		vbox.addWidget(self.labelPourLeWeb)
		vbox.addWidget(self.labelHauteDefinition)
		vbox.addWidget(self.labelAVCHD)
		
		vbox.addStretch()

		self.connect(self.labelGeneral, SIGNAL("click"), self.majGeneral)
		self.connect(self.labelPourLeWeb, SIGNAL("click"), self.majPourLeWeb)
		self.connect(self.labelHauteDefinition, SIGNAL("click"), self.majHauteDefinition)
		self.connect(self.labelAVCHD, SIGNAL("click"), self.majAVCHD)
		self.parent=parent

	def majGeneral(self):
		'''
		Fonction qui sera connecté lors du click sur le menu Général
		'''
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.treeWidgetAnimation.currentItem(), 0)
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.itemTree_Encodage_General, 1)
		self.parent.stacked_onglet_animation.setCurrentIndex(self.parent.stacked_animation_encodage_general)

	def majPourLeWeb(self):
		'''
		Fonction qui sera connecté lors du click sur le menu Pour le web
		'''
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.treeWidgetAnimation.currentItem(), 0)
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.itemTree_Encodage_Web, 1)
		self.parent.stacked_onglet_animation.setCurrentIndex(self.parent.stacked_animation_encodage_web)

	def majHauteDefinition(self):
		'''
		Fonction qui sera connecté lors du click sur le menu Haute Définition
		'''
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.treeWidgetAnimation.currentItem(), 0)
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.itemTree_Encodage_HD, 1)
		self.parent.stacked_onglet_animation.setCurrentIndex(self.parent.stacked_animation_encodage_hd)

	def majAVCHD(self):
		'''
		Fonction qui sera connecté lors du click sur le menu Haute Définition
		'''
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.treeWidgetAnimation.currentItem(), 0)
		self.parent.treeWidgetAnimation.setItemSelected(self.parent.itemTree_Encodage_AVCHD, 1)
		self.parent.stacked_onglet_animation.setCurrentIndex(self.parent.stacked_animation_encodage_avchd)

	def load(self) :
		#print "Section transcodage"
		EkdPrint(u"Section transcodage")

	def save(self) :
		#print "Section transcodage"
		EkdPrint(u"Section transcodage")
