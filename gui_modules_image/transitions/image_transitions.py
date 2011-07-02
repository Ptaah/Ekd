#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_modules_common.EkdWidgets import EkdLabel

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Image_Transitions(QWidget):
	# -----------------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Transitions
	# -----------------------------------------
	def __init__(self, parent):
        	QWidget.__init__(self)
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# Titre de la page
		txt = _(u"Image Transitions:")
		self.titre_du_cadre=QLabel("<H2><center><u>%s</u></center></H2>" %txt)
		
		# Lien vers les sous-cadres
		self.labelFonduEnchaine = EkdLabel(_(u"Fondu enchaîné"))
		self.labelSpirale = EkdLabel(_(u"Spirale"))
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "none" # Défini le type de fichier source.
		self.typeSortie = "none" # Défini le type de fichier de sortie.
		self.sourceEntrees = None # Fait le lien avec le sélecteur de fichier source.
		
		# Ajout du titre de la page a la boite verticale
		vbox.addWidget(self.titre_du_cadre)
		vbox.addSpacing(10)
		vbox.addWidget(self.labelFonduEnchaine)
		vbox.addWidget(self.labelSpirale)
		
		vbox.addStretch()

		''' Utilisation de signaux pour connecter les label à l'arbre de gauche plutôt que de devoir passer le parent complet au label. On ajoute les connection entre les objets '''
		self.connect(self.labelFonduEnchaine, SIGNAL("click"), self.majFonduEnchaine)
		self.connect(self.labelSpirale, SIGNAL("click"), self.majSpirale)

		self.parent=parent

	def majFonduEnchaine(self):
		''' Fonction qui sera connecté lors du click sur le menu FonduEnchainé '''
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_FonduEnchaine, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_transitions_fondEnch)

	def majSpirale(self):
		''' Fonction qui sera connecté lors du click sur le menu Spirale '''
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_Spirale, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_transitions_Spirale)

	def load(self) :
		#print "Section image - transition"
		EkdPrint(u"Section image - transition")

	def save(self) :
		#print "Section image - transition"
		EkdPrint(u"Section image - transition")
