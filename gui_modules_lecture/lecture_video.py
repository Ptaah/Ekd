#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from moteur_modules_animation.mplayer import Mplayer
import os
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_common.EkdWidgets import EkdAide

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Lecture_VisionVideo(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Lecture >> Visionner des images
	# -----------------------------------

	# On ne passe pas tout le parent, mais juste ce dont on a besoin (ici la bar de status)
	def __init__(self, statusBar, filer=False):
        	QWidget.__init__(self)
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# On ne passe pas tout le parent, mais juste ce dont on a besoin (ici la bar de status)
		# Barre des tâches
		self.statusBar = statusBar

                #-------------------
		# Navigateur de répertoires
		#-------------------
		
		# arborescence des fichiers et dossiers permettant l'affichage
		self.listViewVisioVideo = QListView()

		filtres_option = QDir.AllDirs | QDir.Files | QDir.Readable
		filtres = QStringList()
		filtres << "*.avi" << "*.mpg" << "*.mpeg" << "*.mjpeg" << "*.flv" << "*.mp4" << "*.ogg" << "*.vob" << "*.mov" << "*.h264" << "*.wmv" << "*.3gp"
                sorting = QDir.DirsFirst
                if int(EkdConfig.get("general", "ignore_case")):
                    sorting |= QDir.IgnoreCase
		self.model = QDirModel(filtres, filtres_option, sorting)
		
		try :
			index = self.model.index(EkdConfig.get('general', 'video_input_path'))
		except Exception, e:
			index = self.model.index(QDir.homePath())

		self.listViewVisioVideo.setModel(self.model)
		self.listViewVisioVideo.setRootIndex(index)

		self.connect(self.listViewVisioVideo, SIGNAL("doubleClicked(const QModelIndex &)"), self.naviguer)
		self.connect(self.listViewVisioVideo,SIGNAL("clicked(QModelIndex)"), self.updateDir)

		# Ajout du navigateur à la VBox
		if filer : 
			vbox.addWidget(self.listViewVisioVideo)
			self.listViewVisioVideo.setMaximumHeight(100)

		self.afficheurVideo=Mplayer([], (400, 400*3/4),
			(Mplayer.PRECEDENT_SUIVANT,Mplayer.CURSEUR_A_PART,Mplayer.PARCOURIR),
			barreTaches=self.statusBar, facteurLimitant=Mplayer.LARGEUR)
		
		group=QGroupBox("")
		layout=QHBoxLayout(group)
		layout.addWidget(self.afficheurVideo)
		
		hbox = QHBoxLayout()
		hbox.addStretch()
		hbox.addWidget(group)
		hbox.addStretch()
		vbox.addLayout(hbox)
		
		vbox.addStretch()
		
		# -------------------------------------------------------------------
		# widgets du bas : ligne + boutons
		# -------------------------------------------------------------------
		
		# boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones" + os.sep + "icone_aide_128.png"))
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
		
		# ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons
		
		hbox=QHBoxLayout()
		hbox.addWidget(boutAide)
		hbox.addStretch()	# espace entre les 2 boutons
		vbox.addLayout(hbox)
		
		# affichage de la boîte principale
		self.setLayout(vbox)
	
	
	def updateDir(self, index):
		"Fonction appelée par le treeview lors d'un changement de repertoire. Chemin(s) fourni(s) à mplayer."
		modele = index.model()
		
		# chemin sélectionné (QString)
		cheminSelect = modele.filePath(index)
		
		#=== Le chemin sélectionné est un fichier ===#
		if not modele.isDir(index) :
			self.afficheurVideo.listeVideos = [unicode(cheminSelect)]
			return
		
		#=== Le chemin sélectionné est un répertoire ===#
		# On crée le QDir
		rep=QDir(cheminSelect)
		rep.setFilter(QDir.Files)
		self.statusBar.showMessage(rep.absolutePath())
		# Lien entre le chemin sélectionné de l'arbre et celui qui sera ouvert
		# avec la boite de dialogue du bouton parcourir
		self.afficheurVideo.cheminPourBoutonParcourir = rep.absolutePath()
		
		# Filtre des extensions (pas sensible à la casse)
		listeExtension=["avi", "mpg", "mpeg", "mjpeg", "flv", "mp4", "ogg"]
		# Liste des vidéos qui sera fournie à mplayer
		listeVideo=[]
		
		# Récuperation des fichiers du dossier
		liste=rep.entryList()
		
		# Sélection des fichiers
		for entree in liste:
			# Création du QFileInfo
			fichier=QFileInfo(rep.absolutePath() + os.sep + entree)
			
			# Recuperation de l'extension
			extension=fichier.suffix()
			
			# Application du filtre
			for validExtension in listeExtension:
				# Si l'extension est valide
				if extension.toLower()==validExtension:
					# On ajoute à la liste
					listeVideo.append(fichier.absoluteFilePath())
		
		
		# On communique les vidéos à mplayer
		self.afficheurVideo.listeVideos = listeVideo
	
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""
		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<h3><center>Lire des vidéos</center></h3><p>Vous allez ici pouvoir lire une ou plusieurs vidéo(s).</p><p>Cliquez sur le bouton 'Parcourir...', dans la boîte de dialogue allez chercher votre (ou vos) vidéo(s) ... et cliquez sur le bouton juste à droite (la flèche blanche vers la droite).</p><p>Pour sélectionner plusieurs vidéos (dans la boîte de dialogue), maintenez la touche CTRL du clavier enfoncée (pour une sélection individuelle) ou bien SHIFT (pour une sélection groupée) ... tout en sélectionnant vos fichiers.</p><p>Pour certaines opérations précises, vous pouvez utiliser les raccourcis claviers suivants (pour que ces raccourcis soient opérationnels, n'oubliez pas de mettre le pointeur de votre souris sur la fenêtre de lecture):</p><h4><ul>** Les touches Alt Gr avec [ et Alt Gr avec ] diminuent/accélèrent la vitesse courante de lecture de 10% (avec la touche backspace, on revient à une vitesse de lecture normale).</ul></h4><h4><ul>** Les touches Shift avec 0 augmentent le volume et les touches Shift avec 9 diminuent le volume (pour le son). Attention pour le 0 et le 9, ce sont les chiffres à gauche du clavier (pas les touches du pavé numérique).</ul></h4><h4><ul>** Avec la touche q (ou Echap) on arrête la lecture.</ul></h4>"))
		messageAide.show()

	def naviguer(self, item):
		'''
		fonction permettant de naviguer dans la listes des répertoires
		seulement si l'item doublecliké est un répertoire
		'''
			
		modele = item.model()
		rep=QDir(modele.filePath(item))
		
		if rep.exists():
			path = rep.absolutePath()
			if os.listdir(path):
				#print unicode(path)
				EkdPrint(unicode(path))
				self.listViewVisioVideo.setRootIndex(item)
				self.statusBar.showMessage(path)
			else :
				#print "Cannot access " , path
				EkdPrint(u"Cannot access %s" % str(path))
		else:
			self.afficheurVideo.arretMPlayer()
			self.afficheurVideo.demarrerMPlayer()

	def getFolder(self):
		'''
		fonction permettant de récupérer le widget contenant les répertoires
		Permet de déplacer la liste des répertoires dans l'interface
		'''
		return self.listViewVisioVideo
