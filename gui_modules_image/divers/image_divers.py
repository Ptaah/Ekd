#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_modules_common.EkdWidgets import EkdLabel

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Image_Divers(QWidget):
	# -----------------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers
	# -----------------------------------------
	def __init__(self, parent):
        	QWidget.__init__(self)
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# Titre de la page
		txt = _(u"Image Divers:")
		self.titre_du_cadre=QLabel("<H2><center><u>%s</u></center></H2>" %txt)
		
		# Lien vers les sous-cadres
		self.labelPlancheContact = EkdLabel(_(u"Planche contact"))
		self.labelInformation = EkdLabel(_(u"Information"))
		self.labelChangerFormat = EkdLabel(_(u"Changer format"))
		self.labelRedimensionner = EkdLabel(_(u"Redimensionner"))
		self.labelTxtSurImg = EkdLabel(_(u"Ajout d'éléments"))
		self.labelImageComposite = EkdLabel(_(u"Image composite"))
		self.labelRenommerImg = EkdLabel(_(u"Renommer images"))
		self.labelPourLeWeb = EkdLabel(_(u"Pour le web"))
		self.labelMultiplicImg = EkdLabel(_(u"Multiplication d'image"))
		
		# Ajout du titre de la page a la boite verticale
		vbox.addWidget(self.titre_du_cadre)
		vbox.addSpacing(10)
		vbox.addWidget(self.labelPlancheContact)
		vbox.addWidget(self.labelInformation)
		vbox.addWidget(self.labelChangerFormat)
		vbox.addWidget(self.labelRedimensionner)
		vbox.addWidget(self.labelTxtSurImg)
		vbox.addWidget(self.labelImageComposite)
		vbox.addWidget(self.labelRenommerImg)
		vbox.addWidget(self.labelPourLeWeb)
		vbox.addWidget(self.labelMultiplicImg)
		
		vbox.addStretch()

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "none" # Défini le type de fichier source.
		self.typeSortie = "none" # Défini le type de fichier de sortie.
		self.sourceEntrees = None # Fait le lien avec le sélecteur de fichier source.

		''' Utilisation de signaux pour connecter les label à l'arbre de gauche plutôt que de devoir passer le parent complet au label. On ajoute les connection entre les objets '''

		self.connect(self.labelPlancheContact, SIGNAL("click"), self.majPlancheContact)
		self.connect(self.labelInformation, SIGNAL("click"), self.majInformation)
		self.connect(self.labelChangerFormat, SIGNAL("click"), self.majChangerFormat)
		self.connect(self.labelRedimensionner, SIGNAL("click"), self.majRedimensionner)
		self.connect(self.labelTxtSurImg, SIGNAL("click"), self.majTxtSurImg)
		self.connect(self.labelImageComposite, SIGNAL("click"), self.majImageComposite)
		self.connect(self.labelRenommerImg, SIGNAL("click"), self.majRenommerImg)
		self.connect(self.labelPourLeWeb, SIGNAL("click"), self.majPourLeWeb)
		self.connect(self.labelMultiplicImg, SIGNAL("click"), self.majMultiplicImg)

		self.parent=parent

		
	def majPlancheContact(self):
		''' Fonction qui sera connecté lors du click sur le menu PlancheContact '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_PlContact, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_PlContact)


	def majInformation(self):
		''' Fonction qui sera connecté lors du click sur le menu Information '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_Information, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_Information)


	def majChangerFormat(self):
		''' Fonction qui sera connecté lors du click sur le menu ChangerFormat '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_ChangFormat, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_ChangFormat)


	def majRedimensionner(self):
		''' Fonction qui sera connecté lors du click sur le menu Redimensionner '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_Redimens, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_Redimens)


	def majTxtSurImg(self):
		''' Fonction qui sera connecté lors du click sur le menu Texte sur Image '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_TxtSurImg, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_TxtSurImg)


	def majImageComposite(self):
		''' Fonction qui sera connecté lors du click sur le menu Image Composite '''
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_ImgComposit, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_Compositing)


	def majRenommerImg(self):
		''' Fonction qui sera connecté lors du click sur le menu Renommer Image '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_RenomImg, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_RenomImg)


	def majPourLeWeb(self):
		''' Fonction qui sera connecté lors du click sur le menu Pour le web '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_PourLeWeb, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_PourLeWeb)


	def majMultiplicImg(self):
		''' Fonction qui sera connecté lors du click sur le menu MultiplicImg '''

		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.treeWidgetDiversImage.currentItem(), 0)
		self.parent.treeWidgetDiversImage.setItemSelected(self.parent.itemTree_MultiplicImg, 1)
		self.parent.stacked_onglet_image.setCurrentIndex(self.parent.stacked_image_divers_MultiplicImg)


	def load(self) :
		#print "Section image - divers"
		EkdPrint(u"Section image - divers")


	def save(self) :
		#print "Section image - divers"
		EkdPrint(u"Section image - divers")
