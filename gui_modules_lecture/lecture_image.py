#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurImagePourEKD
from gui_modules_common.EkdWidgets import EkdPreview, EkdTimePropertie
from moteur_modules_common.EkdConfig import EkdConfig

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Lecture_VisionImage(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Lecture >> Visionner des images
	# -----------------------------------

	# On ne passe pas tout le parent, mais juste ce dont on a besoin (ici la bar de status)
	def __init__(self, statusBar, boutParcourir=False, filer=False):
        	QWidget.__init__(self)
		
		self.sortie=[]
		# Boite d'alignement verticale
		vbox=QVBoxLayout(self)
		
		# On ne passe pas tout le parent, mais juste ce dont on a besoin (ici la bar de status)
		# Barre des tâches
		self.statusBar = statusBar

                #-------------------
		# Navigateur de répertoires
		#-------------------
		
		# arborescence des fichiers et dossiers permettant l'affichage
		self.listViewVisioImg = QListView()
		
		filtres_option = QDir.Dirs | QDir.Readable | QDir.Executable
		filtres = QStringList()
		filtres << "*"
                sorting = QDir.DirsFirst
                if int(EkdConfig.get("general", "ignore_case")):
                    sorting |= QDir.IgnoreCase
		self.model = QDirModel(filtres, filtres_option, sorting)
		
		try :
			index = self.model.index(EkdConfig.get('general', 'image_input_path'))
		except :
			index = self.model.index(QDir.homePath())
		self.listViewVisioImg.setModel(self.model)
		self.listViewVisioImg.setRootIndex(index)
		self.connect(self.listViewVisioImg, SIGNAL("doubleClicked(const QModelIndex &)"), self.naviguer)
		self.connect(self.listViewVisioImg,SIGNAL("clicked(QModelIndex)"), self.updateDir)
		# Ajout du navigateur à la VBox
		if filer : 
			vbox.addWidget(self.listViewVisioImg)
			self.listViewVisioImg.setMaximumHeight(100)
		
		#-------------------
		# Boite de commandes
		#-------------------

		# Création du visionneur
		self.afficheurImg=VisionneurImagePourEKD()

		#-Boite horizontale des boutons de commandes
		hbox2=QHBoxLayout()
		
		iconTaille=32
		flat=1
		
		#--Bouton début
		boutDebut=QPushButton()
		boutDebut.setIcon(QIcon("Icones" + os.sep +"player_start.png"))
		boutDebut.setIconSize(QSize(iconTaille, iconTaille))
		boutDebut.setToolTip(_(u"Première image"))
		boutDebut.setFlat(flat)
		hbox2.addWidget(boutDebut)
		self.connect(boutDebut, SIGNAL("clicked()"), self.debut)
		
		#--Bouton precedent
		boutPrecedent=QPushButton()
		boutPrecedent.setIcon(QIcon("Icones" + os.sep + "player_rew.png"))
		boutPrecedent.setIconSize(QSize(iconTaille, iconTaille))
		boutPrecedent.setToolTip(_(u"Image précédente"))
		boutPrecedent.setFlat(flat)
		hbox2.addWidget(boutPrecedent)
		self.connect(boutPrecedent, SIGNAL("clicked()"), self.precedent)
		
		#--Bouton de lecture
		boutLecture=QPushButton()
		boutLecture.setIcon(QIcon("Icones" + os.sep + "player_play.png"))
		boutLecture.setIconSize(QSize(iconTaille, iconTaille))
		boutLecture.setToolTip(_(u"Lancer le diaporama"))
		boutLecture.setFlat(flat)
		hbox2.addWidget(boutLecture)
		self.connect(boutLecture, SIGNAL("clicked()"), self.diaporama)
		
		#--Bouton pause
		boutArret=QPushButton()
		boutArret.setIcon(QIcon("Icones" + os.sep + "player_pause.png"))
		boutArret.setIconSize(QSize(iconTaille, iconTaille))
		boutArret.setToolTip(_(u"Mettre en pause le diaporama"))
		boutArret.setFlat(flat)
		hbox2.addWidget(boutArret)
		self.connect(boutArret, SIGNAL("clicked()"), self.pause)
		############################################################
		
		#--Bouton suivant
		boutSuivant=QPushButton()
		boutSuivant.setIcon(QIcon("Icones" + os.sep + "player_fwd.png"))
		boutSuivant.setIconSize(QSize(iconTaille, iconTaille))
		boutSuivant.setToolTip(_(u"Image suivante"))
		boutSuivant.setFlat(flat)
		hbox2.addWidget(boutSuivant)
		self.connect(boutSuivant, SIGNAL("clicked()"), self.suivant)

		#--Bouton fin
		boutFin=QPushButton()
		boutFin.setIcon(QIcon("Icones" + os.sep + "player_end.png"))
		boutFin.setIconSize(QSize(iconTaille, iconTaille))
		boutFin.setToolTip(_(u"Dernière image"))
		boutFin.setFlat(flat)
		hbox2.addWidget(boutFin)
		self.connect(boutFin, SIGNAL("clicked()"), self.fin)
		
		hbox2.addStretch()
		
		#--Bouton taille fenetre
		boutTailleFenetre=QPushButton()
		boutTailleFenetre.setIcon(QIcon("Icones" + os.sep + "fenetre.png"))
		boutTailleFenetre.setIconSize(QSize(iconTaille, iconTaille))
		boutTailleFenetre.setToolTip(_(u"Ajuster à la fenêtre"))
		boutTailleFenetre.setFlat(flat)
		hbox2.addWidget(boutTailleFenetre)
		self.connect(boutTailleFenetre, SIGNAL("clicked()"), self.afficheurImg.setTailleFenetre)
		
		#--Bouton taille reel
		boutTailleReelle=QPushButton()
		boutTailleReelle.setIcon(QIcon("Icones" + os.sep +"taillereelle.png"))
		boutTailleReelle.setIconSize(QSize(iconTaille, iconTaille))
		boutTailleReelle.setToolTip(_(u"Taille réelle"))
		boutTailleReelle.setFlat(flat)
		hbox2.addWidget(boutTailleReelle)
		self.connect(boutTailleReelle, SIGNAL("clicked()"), self.afficheurImg.setTailleReelle)
		
		#--Bouton zoom avant
		boutZoomAvant=QPushButton()
		boutZoomAvant.setIcon(QIcon("Icones" + os.sep + "zoomplus.png"))
		boutZoomAvant.setIconSize(QSize(iconTaille, iconTaille))
		boutZoomAvant.setToolTip(_(u"Zoom avant"))
		boutZoomAvant.setFlat(flat)
		hbox2.addWidget(boutZoomAvant)
		self.connect(boutZoomAvant, SIGNAL("clicked()"), self.afficheurImg.zoomAvant)
		
		#--Bouton zoom arrière
		boutZoomArriere=QPushButton()
		boutZoomArriere.setIcon(QIcon("Icones" + os.sep + "zoommoins.png"))
		boutZoomArriere.setIconSize(QSize(iconTaille, iconTaille))
		boutZoomArriere.setToolTip(_(u"Zoom arrière"))
		boutZoomArriere.setFlat(flat)
		hbox2.addWidget(boutZoomArriere)
		self.connect(boutZoomArriere, SIGNAL("clicked()"), self.afficheurImg.zoomArriere)

		#--Bouton zoom arrière
                prop = "interval_speed"
                allprops = EkdConfig.getAllProperties(EkdConfig.getConfigSection("general"))
		self.boutTimer = EkdTimePropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], section="general")
		self.boutTimer.widget.setToolTip(_(u"Vitesse de défilement"))
		hbox2.addWidget(self.boutTimer.widget)

		if boutParcourir:
			#--Bouton Configuration du diaporama
			# La variable suivante fait le lien entre le chemin sélectionné de l'arbre
			# et celui qui sera ouvert avec la boite de dialogue du bouton parcourir
			self.cheminImage = None
			boutSelectFich = QPushButton("...")
			boutSelectFich.setToolTip(_(u"Parcourir"))
			hbox2.addWidget(boutSelectFich)
			self.connect(boutSelectFich, SIGNAL("clicked()"), self.ouvrirImages)

		# Apercus
		self.listeApercus=QListWidget()
		self.listeApercus.setGridSize(QSize(85,64))
		self.listeApercus.setIconSize(QSize(64,64))
		self.listeApercus.setFlow(QListView.LeftToRight)
		
		if PYQT_VERSION_STR >= "4.1.0":
			self.listeApercus.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
		self.connect(self.listeApercus, SIGNAL("currentRowChanged(int)"), self.changerImage)
		
		# Ajout du viewer à la VBox
		vbox.addWidget(self.afficheurImg)
		
		# Ajout de l'apercu à la VBox
		vbox.addWidget(self.listeApercus)
		
		# Fonction de test et de lecture de l'image gif
		self.isGif = self.afficheurImg.isGif
		self.startPauseGif = self.afficheurImg.startPauseGif
		
		# Création du QTimer
		self.timer=QTimer()
                self.updateTimer()
		self.connect(self.timer, SIGNAL("timeout()"), self.diapo)
		
		# Ajout des commandes
		self.listeApercus.setMaximumSize(QSize(2000,100))
		vbox.addLayout(hbox2)
		
        def updateTimer(self):
                interval = float(EkdConfig.get("general", "interval_speed")) * 1000
                if interval > 100:
                        self.timer.setInterval(interval)
                else:
                        self.timer.setInterval(100)
                
	def ouvrirImages(self):
		"Récupération du chemin des images sélectionnées"
		
		# Ouvrir images
		formats = ["*.%s" %unicode(format).lower() \
			for format in QImageReader.supportedImageFormats()]
		if not self.cheminImage: self.cheminImage=os.path.expanduser('~')
		chemins=QFileDialog.getOpenFileNames(None, _(u"Ouvrir images"), self.cheminImage, ("(%s);;JPEG (*.jpg *.JPG *.jpeg *.JPEG);;PNG (*.png *.PNG);;GIF (*.gif *.GIF);;BMP (*.bmp *.BMP);;SGI (*.sgi *.SGI);;TIF (*.tif *.TIF);;TARGA (*.tga *.TGA);;PNM (*.pnm *.PNM);;PPM (*.ppm *.PPM)" %" ".join(formats)))
		
		# Si pas de fichier sélectionné -> sortir de la fonction
		if not chemins: return
		
		self.cheminImage = QFileInfo(chemins[0]).absolutePath()
		liste = [unicode(QFileInfo(chem).fileName()) for chem in chemins]
		
		# Pour l'affichage il n'y a que la 1ère image qui est sélectionnée,
		# les autres sont présentes en aperçu
		self.updateImages(liste)
	
	def diaporama(self):
		"Fonction de diaporama"
                # On récupère d'abord la valeur du timer
                self.updateTimer()
		# On active le timer
		self.timer.start()
		
	def diapo(self):
		"Routine du Timer du diaporama"
		# Si on est à la dernière image
		if self.listeApercus.currentRow()==len(self.sortie)-1:
			self.timer.stop()
		else:
			self.suivant()
			
	def pause(self):
		"Fonction pour mettre en pause le diaporama"
                # On récupère d'abord la valeur du timer
                self.updateTimer()
		# On active le timer
		self.timer.stop()
			
	def debut(self):
		"Fonction pour selectionner la première image"
		self.listeApercus.setCurrentRow(0)
	
	def fin(self):
		"Fonction pour selectionner la dernière image"
		self.listeApercus.setCurrentRow(len(self.sortie)-1)
		
	def suivant(self):
		"Fonction pour sélectionner l'image suivante"
		
		# Si ce n'est pas la dernière image
		if self.listeApercus.currentRow()!=len(self.sortie)-1:
			self.listeApercus.setCurrentRow(self.listeApercus.currentRow()+1)
		
	def precedent(self):
		"Fonction pour sélectionner l'image precedente"
		
		# Si ce n'est pas la première image
		if self.listeApercus.currentRow()!=0:
			self.listeApercus.setCurrentRow(self.listeApercus.currentRow()-1)
		
	def changerImage(self, item):
		"Fonction pour charger l'image selectionnée dans le listview"
		
		# Si il y a une image selectionnée
		if item!=-1:
			self.afficheurImg.setImage(self.sortie[item])
	
	def updateDir(self, item):
		"Fonction appelée par le treeview lors d'un changement de repertoire"
		
		# On récupère le QModel parent du QModelItem
		modele = item.model()
		
		# On crée le QDir
		rep=QDir(modele.filePath(item))
		rep.setFilter(QDir.Files)
		self.cheminImage = rep.absolutePath()
		self.statusBar.showMessage(self.cheminImage)
		
		# Récuperation des fichiers du dossier
		liste=rep.entryList()
		self.updateImages(liste)
	
	def updateImages(self, liste, cheminImage=None):
		"Cette fonction a été coupée en 2 pour bien implémenter la boite de dialogue associée au bouton parcourir"
		
		# Filtre des extensions (pas sensible à la casse)
		dicoExtension=["png","jpg", "jpeg", "bmp", "gif", "sgi", "tga", "tif", "tiff", "pnm", "ppm"]
		self.sortie=[]
		
		# On vide le ListWidget
		self.listeApercus.clear()
		
		# Sélection des fichiers
		for entree in liste:
			# Création du QFileInfo
			if not cheminImage:
				fichier=QFileInfo(self.cheminImage + os.sep + entree)
			else:
				fichier=QFileInfo(cheminImage + os.sep + entree)
				
			
			# Recuperation de l'extension
			extension=fichier.suffix()
			
			# Application du filtre
			for validExtension in dicoExtension:
				# Si l'extension est valide
				if extension.toLower()==validExtension:
					# On ajoute à la liste
					self.sortie.append(fichier.absoluteFilePath())
					### Gain de performance en utilisant des miniature prégénérées
					# On ajoute au LisView
					minipix = EkdPreview(fichier.absoluteFilePath()).get_preview()
					item = QListWidgetItem(QIcon(minipix),QString(""))
					##
					item.setToolTip(fichier.fileName())
					self.listeApercus.addItem(item)
		
		# Affichage de la première image
		if len(self.sortie)!=0:
			self.debut()
		# Si pas d'image
		else:
			self.afficheurImg.setImage()

	def naviguer(self, item):
		'''
		fonction permettant de naviguer dans la listes des répertoires
		'''
		
		modele = item.model()
		path=QDir(modele.filePath(item)).absolutePath()
		if os.listdir(path):
			#print unicode(path)
			EkdPrint(unicode(path))
			self.listViewVisioImg.setRootIndex(item)
			self.statusBar.showMessage(path)
		else :
			#print "Cannot access " , path
			EkdPrint(u"Cannot access %s" % str(path))


	def getFolder(self):
		'''
		fonction permettant de récupérer le widget contenant les répertoires
		Permet de déplcer la liste des répertoires dans l'interface
		'''
		return self.listViewVisioImg
