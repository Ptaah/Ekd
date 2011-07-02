#!/usr/bin/python
# -*- coding: Utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Sequentiel(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		
		# Boîte principale
		hbox=QHBoxLayout(self)
		
		# Boite verticale à gauche
		vbox=QVBoxLayout()
		hbox.addLayout(vbox)
		
		# Liste des actions à ajouter
		self.listeAjouter=QPushButton(_(u"Ajouter une action"))
		self.listeAjouter.setIcon(QIcon("Icones/action.png"))
		self.connect(self.listeAjouter, SIGNAL("clicked()"), self.showMenu)
		
		# Boutons de deplacement des items
		hbox2=QHBoxLayout()
		iconTaille=32
		# Haut
		self.haut=QPushButton()
		self.haut.setIcon(QIcon("Icones/haut.png"))
		self.haut.setFlat(1)
		self.haut.setIconSize(QSize(iconTaille, iconTaille))
		hbox2.addWidget(self.haut)
		self.connect(self.listeAjouter, SIGNAL("clicked()"), self.showMenu)
		
		# Bas
		self.haut=QPushButton()
		self.haut.setIcon(QIcon("Icones/bas.png"))
		self.haut.setFlat(1)
		self.haut.setIconSize(QSize(iconTaille, iconTaille))
		hbox2.addWidget(self.haut)
		self.connect(self.listeAjouter, SIGNAL("clicked()"), self.showMenu)
		
		# Gauche
		self.haut=QPushButton()
		self.haut.setIcon(QIcon("Icones/gauche.png"))
		self.haut.setFlat(1)
		self.haut.setIconSize(QSize(iconTaille, iconTaille))
		hbox2.addWidget(self.haut)
		self.connect(self.listeAjouter, SIGNAL("clicked()"), self.showMenu)
		
		# Droite
		self.haut=QPushButton()
		self.haut.setIcon(QIcon("Icones/droite.png"))
		self.haut.setFlat(1)
		self.haut.setIconSize(QSize(iconTaille, iconTaille))
		hbox2.addWidget(self.haut)
			
		# Menu déroulant
		self.menuActions=QMenu(_(u"Ajouter une action"))
		
		# Entrée filtre de selection
		self.menuSelection=self.menuActions.addAction(_(u'&Filtre de sélection'))
		self.menuSelection.setIcon(QIcon("Icones/fenetre.png"))
		self.connect(self.menuSelection, SIGNAL("triggered()"), self.addSelection)
		
		# Filtres
		self.menuFiltres=QMenu(_(u"&Filtres d'image"))
		self.menuActions.addMenu(self.menuFiltres)
		self.menuFiltres.setIcon(QIcon("Icones/icone_images_256.png"))
		#self.connect(self.menuSelection, SIGNAL("triggered()"), self.addSelection)	
		
		self.menuSepia=self.menuFiltres.addAction(_(u'&Sepia'))
		self.menuSepia.setIcon(QIcon("Icones/icone_images_256.png"))
		self.connect(self.menuSepia, SIGNAL("triggered()"), self.addSepia)
		
		self.menuGris=self.menuFiltres.addAction(_(u'&Niveaux de Gris'))
		self.menuGris.setIcon(QIcon("Icones/icone_images_256.png"))
		self.connect(self.menuGris, SIGNAL("triggered()"), self.addGris)
		
		self.menuBalance=self.menuFiltres.addAction(_(u'&Balances'))
		self.menuBalance.setIcon(QIcon("Icones/icone_images_256.png"))
		self.connect(self.menuBalance, SIGNAL("triggered()"), self.addBalance)
		
		self.menuBalance=self.menuFiltres.addAction(_(u'&Balances'))
		self.menuBalance.setIcon(QIcon("Icones/icone_images_256.png"))
		self.connect(self.menuBalance, SIGNAL("triggered()"), self.addBalance)
		
		# Liste des actions
		self.liste=QTreeView()
		self.liste.setMaximumSize(QSize(250, 2000))
		self.connect(self.liste, SIGNAL("clicked(const QModelIndex&)"), self.reglages)
		
		# Ajout du bouton et du TreeView
		vbox.addWidget(self.listeAjouter)
		vbox.addLayout(hbox2)
		vbox.addWidget(self.liste)
		
		# Modele du QTreeView
		self.model=QStandardItemModel()
		self.model.setHorizontalHeaderLabels(QStringList(_(u"Actions")))
		
		# Item racine
		self.root=self.model.invisibleRootItem()
		
		# Item racine visible
		self.item=QStandardItem(QIcon("Icones/projet.png") ,QString(_(u'Projet')))
		self.root.appendRow(self.item)
		
		# Mise en place du modele
		self.liste.setModel(self.model)
		
		# Boite de paramètres
		reglages=QGroupBox()#_(u"Paramètres de l'action"))
		box=QVBoxLayout(reglages)
		
		# création de stacked pour les QWidget
		self.stacked=QStackedWidget()
		stack=stackProjet()
		self.stacked.addWidget(stack)
		self.stacked.setCurrentIndex(0)
		
		box.addWidget(self.stacked)
		
		hbox.addWidget(reglages)
		
		
		self.setLayout(hbox)
		
	def reglages(self, index):
		"Fonction qui affiche les réglages de l'action sélectionnée"
		print index.internalId()
		print index.column(), index.row()
		print index.internalPointer()
		
	def showMenu(self):
		"Fonction qui affiche le menu"
		self.menuActions.popup(self.listeAjouter.mapToGlobal(QPoint(0, self.listeAjouter.height())))
	
	def addSelection(self):
		"Ajout d'un filtre de selection"
		item=QStandardItem(QIcon("Icones/fenetre.png"), QString(_(u"Selection")))
		self.model.itemFromIndex(self.liste.currentIndex()).appendRow(item)
		self.liste.expand(self.liste.currentIndex())
		stack=stackSelection()
		self.stacked.addWidget(stack)
		#self.stacked.setCurrentIndex(self.liste.currentIndex().row())
		
	def addSepia(self):
		"Ajout d'un filtre sepia"
		item=QStandardItem(QIcon("Icones/icone_images_256.png"), QString(_(u"Sepia")))
		self.model.itemFromIndex(self.liste.currentIndex()).appendRow(item)
		self.liste.expand(self.liste.currentIndex())
	
	
	def addGris(self):
		"Ajout d'un filtre niveaux de gris"
		item=QStandardItem(QIcon("Icones/icone_images_256.png"), QString(_(u"Niveaux de gris")))
		self.model.itemFromIndex(self.liste.currentIndex()).appendRow(item)
		self.liste.expand(self.liste.currentIndex())

	def addBalance(self):
		"Ajout d'un filtre balances"
		item=QStandardItem(QIcon("Icones/icone_images_256.png"), QString(_(u"Balances")))
		self.model.itemFromIndex(self.liste.currentIndex()).appendRow(item)
		self.liste.expand(self.liste.currentIndex())

class stackSelection(QWidget):
	"Widget de selection"
	def __init__(self):
		QWidget.__init__(self)
		
		# VBox
		vbox=QVBoxLayout()
		
		# Titre
		label=QLabel(_(u"<H2>Filtre de sélection</H2>"))
		label.setWordWrap(1)
		vbox.addWidget(label)
		
		self.setLayout(vbox)

class stackProjet(QWidget):
	"Widgets du projet"
	
	def __init__(self):
		QWidget.__init__(self)
		
		# VBox
		vbox=QVBoxLayout()
		
		# Titre
		label=QLabel(_(u"<H2><U><CENTER>Introduction</CENTER></H2></U><BR><BR>Le module séquentiel est dédié au traitement par lot. En effet, il permet d'appliquer les filtres et possibilités de <FONT COLOR=green><B>EKD</B></FONT> sur une serie de données sources avec des filtres de selection. Exemple : filtre sépia et incrustation d'image sur les images 1 à 78 d'une vidéo...les possibilités sont infinies.<BR><BR>Le principe de fonctionnement est simple : <B>Toute action s'applique sur la source parente et après l'action précedente</B><BR><FONT COLOR=red><B>Commencez par ajouter une source (vidéo ou image)</B></FONT><BR><H2><FONT COLOR=red><B>-- Attention le module séquentiel n'est pas encore utilisable --</B></FONT><H2>"))
		label.setWordWrap(1)
		vbox.addWidget(label)
		
		self.setLayout(vbox)
	
	
class Filtres(QWidget):
	"Widgets associés à la boite Filtre"
	def __init__(self,config):
		QWidget.__init__(self)
		pass