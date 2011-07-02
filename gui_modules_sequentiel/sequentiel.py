#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base

class Sequentiel(QWidget):
	# Modifié le 22/06/2009 : Inutile
	#def __init__(self, parent):
	def __init__(self):
		QWidget.__init__(self)
		
		largeur = 200
		hauteur = 200		
		
		# Variable d'index du QStackedWidget pour connaitre l'index du
		self.id = 0
		
		# Boîte principale
		hbox=QHBoxLayout(self)
		
		# Boite verticale à gauche
		vbox=QVBoxLayout()
		hbox.addLayout(vbox)
		
		# Liste des actions à ajouter
		self.listeAjouter = QPushButton(_(u"Ajouter une action"))
		self.listeAjouter.setIcon(QIcon("Icones/add_sub_task.png"))
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
		self.liste.setEditTriggers(QAbstractItemView.NoEditTriggers)
		#self.liste.setDragDropMode(QAbstractItemView.InternalMove)
		self.connect(self.liste, SIGNAL("clicked(const QModelIndex&)"), self.reglages)
		
		# Ajout du bouton et du TreeView
		vbox.addWidget(self.listeAjouter)
		vbox.addLayout(hbox2)
		vbox.addWidget(self.liste)
		
		# Modele du QTreeView
		self.model=QStandardItemModel()
		self.model.setHorizontalHeaderLabels(QStringList(_(u"Actions")))
		
		# Item racine
		self.root = self.model.invisibleRootItem()
		
		# Item racine visible
		self.item = QStandardItem(QIcon("Icones/projet.png") ,QString(_(u'Projet')))
		#print self.item.data(Qt.UserRole).toInt()
		self.item.setData(QVariant(self.id), Qt.UserRole)
		#print self.item.data(Qt.UserRole).toInt()
		self.root.appendRow(self.item)
		
		# Mise en place du modele
		self.liste.setModel(self.model)
		
		# Boite de paramètres
		reglages = QGroupBox()
		box = QVBoxLayout(reglages)
		
		# Création de stacked pour les QWidget
		self.stacked = QStackedWidget()
		
		# Stack de départ
		self.stack = stackProjet(self)
		self.stacked.addWidget(self.stack)
		self.stacked.setCurrentIndex(self.id)
		
		# Ajout du QStacked au QGroupBox
		box.addWidget(self.stacked)
		hbox.addWidget(reglages)
				
		self.setLayout(hbox)
		
		# Fenetre popup
		self.popup = Popup(self)
		self.popup.setParent(self)
		
	def reglages(self, index):
		"Fonction qui affiche les réglages de l'action sélectionnée"
		print index.internalId() + index.column() + index.row(), index.data(Qt.UserRole).toInt()
		self.stacked.setCurrentIndex(index.data(Qt.UserRole).toInt()[0])
		print self.liste.indexAbove(index).data(Qt.UserRole).toInt()
		#self.popup.showInfo(_(u"Vous ne pouvez pas ajouter un filtre sur autre chose qu'une source ou une selection d'une source."), "fenetre.png", _(u"Mauvaise manipulation"))
				
	def showMenu(self):
		"Fonction qui affiche le menu"
		self.menuActions.popup(self.listeAjouter.mapToGlobal(QPoint(0, self.listeAjouter.height())))
	
	def addSelection(self):
		"Ajout d'un filtre de selection"
		self.id = self.id + 1
		
		# Création de l'item avec son ID
		self.item = QStandardItem(QIcon("Icones/fenetre.png"), QString(_(u"Selection")))
		self.item.setData(QVariant(self.id), Qt.UserRole)
		
		print "-", self.item.data(Qt.UserRole).toInt()[0]
		
		# Ajout de l'item à celui selectionné
		self.model.itemFromIndex(self.liste.currentIndex()).appendRow(self.item)
		self.liste.expand(self.liste.currentIndex())
		
		# Création du stack
		stack = stackSelection(self.id)
		self.stacked.addWidget(stack)		
		self.stacked.setCurrentIndex(1)		

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
		
	def addVideo(self):
		"Ajout d'une vidéo"
		
		# Ajout de l'action
		self.addAction("video.png", _(u"Vidéo"), 1, stackVideo())	
		
	def addAction(self, icon, label, genre, stack):
		"Ajout d'une action"
				
		print "- ID :", self.item.data(Qt.UserRole).toInt()[0], "Genre :", genre
		
		# Création et ajout de l'item à celui selectionné si il n'y a pas de problème de type
		if(incompatible(self.model.itemFromIndex(self.liste.currentIndex()).data(Qt.UserRole + 1).toInt(), genre) == 0):
		
			# Incrémentation de la variable de l'identifiant de l'index du stack
			self.id = self.id + 1
			
			# Création de l'item avec son ID et son type
			self.item = QStandardItem(QIcon("Icones/" + icon), QString(label))
			self.item.setData(QVariant(self.id), Qt.UserRole)
			self.item.setData(QVariant(genre), Qt.UserRole + 1)
			
			# Ajout 
			self.model.itemFromIndex(self.liste.currentIndex()).appendRow(self.item)
			self.liste.expand(self.liste.currentIndex())
		
			# Création du stack
			self.stack = stack
			self.stacked.addWidget(self.stack)		
			self.stacked.setCurrentIndex(self.id)

class Popup(QFrame):
	"Popup temporisée pour affcher des messages"
		
	def __init__(self, main):
		QFrame.__init__(self)
				
		# Référence au module séquentiel
		self.main = main
		
		# Activation du tracking pour capter le MouseMoveEvent
		self.setMouseTracking(1)
		
		# Dimensions
		largeur = 300
		hauteur = 120
			
		# QFrame popup
		#self.popup = QFrame(self)
		#self.popup.setAutoFillBackground(1)
		#self.popup.setFrameShape(QFrame.StyledPanel)
		#self.popup.setFrameShadow(QFrame.Plain)
		#self.connect(self.popup, SIGNAL("mouseMoveEvent()"), self.hidePopup)
		#popup.setFrameStyle(QFrame.Box)
		
		self.setAutoFillBackground(1)
		self.setFrameShape(QFrame.StyledPanel)
		self.setFrameShadow(QFrame.Plain)
		
		# Palette de la frame		
		palette = QPalette()
		palette.setColor(QPalette.Window, QColor(255, 255, 255, 255))
		self.setPalette(palette)
		
		#print self.mapToGlobal(QPoint(self.width()/2,self.height()/2)).x(), self.mapToGlobal(QPoint(self.width()/2,self.height()/2)).y()
		#print "Largeur :", self.width(), "| Hauteur :", self.height()
		#print "X :", self.width()/2 - largeur/2, "| Y :", self.height()/2 - hauteur/2
		
		# Positionnement au centre de l'ecran
		#self.setGeometry(QDesktopWidget().screenGeometry().width()/2 - largeur/2, QDesktopWidget().screenGeometry().height()/2 - hauteur/2, largeur, hauteur)
		
		# Titre
		self.labelTitre = QLabel()
		
		# Ligne
		self.ligne = QFrame(self)
		self.ligne.setFrameShape(QFrame.HLine)
		
		# Message avec l'icone
		self.labelIcone = QLabel()
		self.labelMessage = QLabel()
		self.labelMessage.setWordWrap(1)
		
		# Boites
		vbox = QVBoxLayout(self)
		hbox = QHBoxLayout()
		hbox.addWidget(self.labelIcone)
		hbox.addWidget(self.labelMessage)
		vbox.addWidget(self.labelTitre)
		vbox.addWidget(self.ligne)
		vbox.addStretch()
		vbox.addLayout(hbox)		
		
		self.hide()
		
		# On fait apparaitre
		#alpha = 0
		
		#while alpha < 255:
		#	alpha = alpha + 15
		#	palette.setColor(QPalette.Window, QColor(255, 255, 255, alpha))
		#	palette.setColor(QPalette.WindowText, QColor(0, 0, 0, alpha))
		#	popup.setPalette(palette)
		#	labelMessage.setPalette(palette)
		#	labelTitre.setPalette(palette)
		#	popup.repaint()
		#	time.sleep(0.15)
			
		# On fait disparaitre		
		#while alpha > 0:
		#	alpha = alpha - 15
		#	palette.setColor(QPalette.Window, QColor(255, 255, 255, alpha))
		#	palette.setColor(QPalette.WindowText, QColor(0, 0, 0, alpha))
		#	popup.setPalette(palette)
		#	labelMessage.setPalette(palette)
		#	labelTitre.setPalette(palette)
		#	popup.repaint()
		#	time.sleep(0.05)
	
	def showInfo(self, message, icone, titre):
		"Affichage avec un titre, une icone et un texte"
		# On modifie les valeurs
		largeur = 300
		hauteur = 120
		
		# Titre
		self.labelTitre.setText(QString("<CENTER><H3><FONT COLOR=green>" + str(titre) + "</FONT></H3></CENTER>"))
		
		# Message avec l'icone
		self.labelIcone.setText(QString("<img src='Icones/" + str(icone) + "' style='vertical-align:middle;' width=32px height=32px>&nbsp;&nbsp;"))
		self.labelMessage.setText(QString(str(message)))
		self.labelMessage.setWordWrap(1)
		
		# Positionnement au centre de l'écran
		self.setGeometry(self.main.width()/2 - largeur/2, self.main.height()/2 - hauteur/2, largeur, hauteur)
		
		# On montre
		self.show()
		
		# Temps d'attente
		QTimer.singleShot(5000, self.hide);
	
	def mouseMoveEvent(self, event):
		self.hide()
		
#############################
# Compatibilité des actions
# - Source vidéo ou images s'ajoute qu'à la racine
# - Sorties vidéo ou images s'ajoutent qu'à la suite d'une source
def incompatible(type1, type2):
	"Fonction qui vérifie la compatibilité entre 2 items pour savoir si l'un peut être fils de l'autre"
	
	print "Compatibilité entre", type1, "et", type2
	return 0
	
			

class stackSelection(QWidget):
	"Widget de selection"
	def __init__(self, i):
		QWidget.__init__(self)
	
		# VBox
		vbox = QVBoxLayout()
		vbox.setSizeConstraint(QLayout.SetMinimumSize)
		
		# Titre
		label=QLabel(_(u"<CENTER><H2><img src='Icones/fenetre.png' style='vertical-align:middle;'>&nbsp;&nbsp;&nbsp;<U>Filtre de sélection</U>&nbsp;&nbsp;&nbsp;<img src='Icones/fenetre.png' style='vertical-align:middle;'></H2></CENTER><BR>"))
		label.setWordWrap(1)
		vbox.addWidget(label)
		
		source = QGroupBox(QString(_(u"Source")))
		sourceBox = QHBoxLayout(source)
		labelSource = QLabel(_(u"<img src='Icones/video.png' style='vertical-align:middle;' width=32 height=32>&nbsp;&nbsp;&nbsp;Vidéo : /home/jrbleboss/test.mpg "))
		sourceBox.addWidget(labelSource)
		
		source = QGroupBox(QString(_(u"Source")))
		sourceBox = QHBoxLayout(source)
		labelSource = QLabel(_(u"<img src='Icones/video.png' style='vertical-align:middle;' width=32 height=32>&nbsp;&nbsp;&nbsp;Vidéo : /home/jrbleboss/test.mpg "))
		sourceBox.addWidget(labelSource)
		
		vbox.addWidget(source)
	
		self.setLayout(vbox)

class stackVideo(QWidget):
	"Widget de source vidéo"
	def __init__(self):
		QWidget.__init__(self)

		# VBox
		vbox = QVBoxLayout()
		vbox.setSizeConstraint(QLayout.SetMinimumSize)
		vbox.addStretch()

		# Titre
		label=QLabel(_(u"<CENTER><H2><img src='Icones/video.png' style='vertical-align:middle;' width=32 height=32>&nbsp;&nbsp;&nbsp;<U>Source vidéo</U>&nbsp;&nbsp;&nbsp;<img src='Icones/video.png' style='vertical-align:middle;' width=32 height=32></H2></CENTER><BR>"))
		label.setWordWrap(1)
		vbox.addWidget(label)
		

		source = QGroupBox(QString("Source"))
		sourceBox = QHBoxLayout(source)
		self.sourceLine = QLineEdit()
		self.sourceLine.setReadOnly(True)
		#labelSource = QLabel(_(u"<img src='Icones/ouvrir.png' style='vertical-align:middle;' width=32 height=32>&nbsp;&nbsp;&nbsp; Choisissez une vidéo"))
		#sourceLine.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.LineEdit)
		sourceBox.addWidget(self.sourceLine)
		
		ouvrir = QPushButton(_(u"Parcourir"))
		ouvrir.setIcon(QIcon("Icones/ouvrir.png"))
		self.connect(ouvrir, SIGNAL("clicked()"), self.selectVideo)
		sourceBox.addWidget(ouvrir)
		vbox.addWidget(source)
		vbox.addStretch()

		self.setLayout(vbox)

	def selectVideo(self):
		"QFileDialog pour choisir la vidéo"
		
		chemin = QFileDialog.getOpenFileName(None, _(u"Ouvrir"), os.path.expanduser("~"), "Vidéos (*.avi *.mpg *.mpeg *.mjpeg *.flv *.mp4 *.ogg)\n*")
		
		# Si pas de fichier sélectionné -> sortir de la fonction
		if not chemin: return
		
		self.sourceLine.setText(QString(chemin))

class stackProjet(QWidget):
	"Widgets du projet"
	
	def __init__(self, main):
		QWidget.__init__(self)
	
		# VBox
		vbox=QVBoxLayout()
	
		# Texte
		label=QLabel(tr(u"<H2><CENTER><img src='Icones/projet.png' style='vertical-align:middle;'>&nbsp;&nbsp;&nbsp;<U>Module Séquentiel</U>&nbsp;&nbsp;&nbsp;<img src='Icones/projet.png' style='vertical-align:middle;'></CENTER></H2><BR><BR> \
		<H3><U>Introduction</U></H3> \
		<p style='text-indent:20px;'>Le module séquentiel est dédié au traitement par lot. En effet, il permet d'utiliser les \
		filtres et possibilités de <FONT COLOR=green><B>EKD</B></FONT> sur une serie de données sources avec des filtres de selection. <BR>Exemple : filtre sépia et \
		incrustation d'image sur les images 1 à 78 d'une vidéo...les possibilités sont infinies.</p><BR> \
		<p style='text-indent:20px;'>Le principe de fonctionnement est simple : \
		<B>Toute action s'applique sur la source parente et après l'action précedente</B></p><BR><BR> \
		<HL><CENTER><FONT COLOR=green>Commencez par ajouter une source</FONT></CENTER><HL>"))
		label.setWordWrap(1)
	
		hbox = QHBoxLayout()

		videoAjouter = QToolButton()
		videoAjouter.setIcon(QIcon("Icones/video.png"))
		videoAjouter.setIconSize(QSize(64, 64))
		videoAjouter.setText(QString(_(u"Ajouter une vidéo")))
		videoAjouter.setAutoRaise(1)
		videoAjouter.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		self.connect(videoAjouter, SIGNAL("clicked()"), main.addVideo)
		hbox.addWidget(videoAjouter)

		imageAjouter = QToolButton()
		imageAjouter.setIcon(QIcon("Icones/image.png"))
		imageAjouter.setIconSize(QSize(64, 64))
		imageAjouter.setText(QString(_(u"Ajouter des images")))
		imageAjouter.setAutoRaise(1);
		imageAjouter.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		#self.connect(imageAjouter, SIGNAL("clicked()"), addVideo)
		hbox.addWidget(imageAjouter)

		vbox.addWidget(label)
		vbox.addLayout(hbox)

		self.setLayout(vbox)
	
	
class Filtres(QWidget):
	"Widgets associés à la boite Filtre"
	def __init__(self,config):
		QWidget.__init__(self)
		pass
