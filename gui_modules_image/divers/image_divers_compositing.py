#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, string, Image, glob
import shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_image.image_base import Base, SpinSlider

from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue

# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Gestion de l'aide via EkdAide
from gui_modules_common.EkdWidgets import EkdAide

# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Image_Divers_Compositing(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Compositing
	# -----------------------------------
	def __init__(self, statusBar, geometry):
        	QWidget.__init__(self)
		
		# ----------------------------
		# Quelques paramètres de base
		# ----------------------------

		# Paramètres de configuration
		self.config = EkdConfig
		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()
		self.idSection = "image_image_composite"
		# Log du terminal
		self.base.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		# Création des répertoires temporaires. Utilisation de EkdConfig
		self.repTampon = EkdConfig.getTempDir() + os.sep + "tampon" + os.sep + "temp_duplication" + os.sep
		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)
			
		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			os.remove(toutRepCompo)
			
		# Répertoire tampon dans lequel est crée le compositing qui sera crée par le
		# bouton 'Voir le résultat'. Utilisation de EkdConfig
		self.repTamponVisuVoirRes = self.repTampon + "visu_voir_res_compo" + os.sep
		if os.path.isdir(self.repTamponVisuVoirRes) is False:
        		os.makedirs(self.repTamponVisuVoirRes)
		
		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompoVisu in glob.glob(self.repTamponVisuVoirRes+'*.*'):
			os.remove(toutRepCompoVisu)
		
		# Répertoire temporaire 1 pour les redimensionnement des images
		if os.path.isdir(self.repTampon+'redim_1/') is False:
        		os.makedirs(self.repTampon+'redim_1/')
		# Répertoire temporaire 2 pour les redimensionnement des images	
		if os.path.isdir(self.repTampon+'redim_2/') is False:
        		os.makedirs(self.repTampon+'redim_2/')
			
		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompoRedim in glob.glob(self.repTampon+'redim_1/'+'*.*'):
			if len(toutRepCompoRedim)>0:
				os.remove(toutRepCompoRedim)
		# ...
		for toutRepCompoRedim in glob.glob(self.repTampon+'redim_2/'+'*.*'):
			if len(toutRepCompoRedim)>0:
				os.remove(toutRepCompoRedim)
		
		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)
		
		# Est-ce que des images ont été converties et qu'elles n'ont pas encore été montrées?
		# Marche aussi quand la conversion a été arrêté avant la fin de la 1ère image
		self.conversionImg = 0
		
		# Est-ce qu'une prévisualisation a été appelée?
		self.previsualImg = 0
		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0

		# Liste de chemins de fichiers avec et sans canal alpha et du dossier de sauvegarde
		self.listeChemAVcanAlph=[]
		self.listeChemSANScanAlph=[]
		self.listeImgDestin = []
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# --------------------------------------------------
		# widgets du haut : titre + bouton de sélection
		# --------------------------------------------------
		
		hbox = QHBoxLayout()
		
		# Ajout du titre de la page et de l'aperçu à la boite verticale
		vbox.addLayout(hbox, 0)
		
		#=== Bouton de sélection des images alpha et sans alpha ===#
		hbox = QHBoxLayout()

		self.framReglage=QFrame()
		vboxReglage=QVBoxLayout(self.framReglage)

		# Pour la gestion du nombre d'images à traiter ##############
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel(_(u"Traitement à partir de l'image (numéro)")), 0, 0)
		self.spin1=SpinSlider(1, 100000, 1, '', self)
		self.grid.addWidget(self.spin1, 0, 1)
		self.connect(self.spin1, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		self.grid.addWidget(QLabel(_(u"Nombre de chiffres après le nom de l'image")), 1, 0)
		self.spin2=SpinSlider(3, 18, 6, '', self)
		self.grid.addWidget(self.spin2, 1, 1)
		self.connect(self.spin2, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.grid.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid)
		vboxReglage.addStretch()

		# -------------------------------------------------
		# Onglets d'affichage image source et destination
		# -------------------------------------------------
		
		# On peut sélectionner les extensions qui doivent être visibles comme ceci:
		#self.afficheurImgSource=SelectWidget(extensions=["*.jpg", "*.png"], geometrie = self.mainWindowFrameGeometry)
		# Là uniquement les fichiers png et gif apparaissent ds la fenêtre de chargement
		# Ne pas oublier de mettre * avant le point et l'extension

		# Là où s'afficheront les images
		# Avec canal alpha
		self.afficheurImgSourceAvecCanalAlpha=SelectWidget(extensions=["*.png", "*.gif"], geometrie = self.mainWindowFrameGeometry)
		# Sans canal alpha
		self.afficheurImgSourceSansCanalAlpha=SelectWidget(geometrie = self.mainWindowFrameGeometry)

		# Gestion de la configuration via EkdConfig
		# Résultat du compositing
		self.afficheurImgDestination=Lecture_VisionImage(statusBar)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSourceSansCanalAlpha # Fait le lien avec le sélecteur de fichier source.
		### Remarque : Le choix a été fait de ne pas mettre la boîte de sélection des images alpha dans le tampon.
		
		# infos - logs
		self.zoneAffichInfosImg = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneAffichInfosImg.setText = self.zoneAffichInfosImg.setPlainText
		self.zoneAffichInfosImg.setReadOnly(True)
		self.fram=QFrame()
		vboxInfIm=QVBoxLayout(self.fram)
		vboxInfIm.addWidget(self.zoneAffichInfosImg)
		self.fram.setEnabled(False)
		
		self.tabwidget=QTabWidget()
		
		self.indexTabImgSourceAvCanAlph = self.tabwidget.addTab(self.afficheurImgSourceAvecCanalAlpha, _(u'Image(s) avec canal alpha'))
		self.indexTabImgSourceSansCanAlph = self.tabwidget.addTab(self.afficheurImgSourceSansCanalAlpha, _(u'Image(s) sans canal alpha'))
		self.indexTabReglage=self.tabwidget.addTab(self.framReglage, _(u'Réglages'))
		self.indexTabImgDestin=self.tabwidget.addTab(self.afficheurImgDestination, _(u'Image(s) après traitement'))
		self.indexTabInfo=self.tabwidget.addTab(self.fram, _(u'Infos'))
		
		vbox.addWidget(self.tabwidget)
		
		# -------------------------------------------------------------------
		# widgets du bas : ligne + boutons
		# -------------------------------------------------------------------
		
		# boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones/icone_aide_128.png"))
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
		self.boutApPremImg = QPushButton(_(u" Voir le résultat"))
		self.boutApPremImg.setIcon(QIcon("Icones/icone_visionner_128.png"))
		self.boutApPremImg.setFocusPolicy(Qt.NoFocus)
		self.boutApPremImg.setEnabled(False)
		self.connect(self.boutApPremImg, SIGNAL("clicked()"), self.visu_1ere_derniere_img)
		self.boutAppliquer=QPushButton(_(u" Appliquer et sauver"))
		self.boutAppliquer.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		self.boutAppliquer.setEnabled(False)
		self.connect(self.boutAppliquer, SIGNAL("clicked()"), self.appliquer)
		
		# ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons
		
		hbox=QHBoxLayout()
		hbox.addWidget(boutAide)
		hbox.addStretch()	# espace entre les 2 boutons
		hbox.addWidget(self.boutApPremImg)
		hbox.addStretch()
		hbox.addWidget(self.boutAppliquer)
		vbox.addLayout(hbox)
		
		# affichage de la boîte principale
		self.setLayout(vbox)
		
		self.connect(self.tabwidget, SIGNAL("currentChanged(int)"), self.fctTab)
		
		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
		#----------------------------------------------------------------------------------------------------
		
		self.connect(self.afficheurImgSourceSansCanalAlpha, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)
		
		
	def modifBoutonsAction(self, i):
		"On active ou désactive les boutons d'action selon s'il y a des images ou pas dans le widget de sélection"
		self.boutAppliquer.setEnabled(i)
		self.boutApPremImg.setEnabled(i)
		self.modifImageSource = 1
	

	def changeValNbreImg_1(self):
		"""Gestion du nombre d'images à traiter"""
		#print "Traitement a partir de l'image (numero):", self.spin1.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2.value())


	def fctTab(self, i):
		"Affichage d'une ou plusieurs images converties"
		
		# Cela ne concerne que l'onglet de visualisation des images après leur conversion
		if i == self.indexTabImgDestin:
			if self.conversionImg:
				# Affichage si on sauvegarde par le bouton Appliquer et sauver
				#print "La conversion vient d'avoir lieu -> affichage des images du lot de destination"
				EkdPrint(u"La conversion vient d'avoir lieu -> affichage des images du lot de destination")
				cheminImages = os.path.dirname(self.listeImgDestin[0])
				liste = []
				for fichier in self.listeImgDestin:
					liste.append(os.path.basename(fichier))
				self.afficheurImgDestination.updateImages(liste, cheminImages)
			elif not self.boutAppliquer.isEnabled() or self.modifImageSource:
				# Si le bouton de conversion n'est pas actif, c'est qu'il n'y a plus d'image source
				# -> on n'a plus de raison de maintenir des images dans l'afficheur de résultat
				# Si les images sources ont été modifiées, on purge aussi l'afficheur de résultat
				self.afficheurImgDestination.updateImages([])
			self.conversionImg = 0
			self.modifImageSource = 0
	
	
	def metaFctTab(self, i):
		"""Changement d'onglet (conçu pour sélectionner les onglets "Images Source" après le chargement de nouvelles images sources ou "Images Après Traitement" après la conversion). But: s'assurer que la fonction associée au QTabWidget (affichage d'images, grisage/dégrisage du curseur...) sera bien appliquée même si on est déjà sur le bon onglet"""
		if self.tabwidget.currentIndex()!=i:
			self.tabwidget.setCurrentIndex(i)
		else: self.fctTab(i)


	def stat_dim_img_1(self):
		"""Calcul statistique des dimensions des images les plus présentes dans le lot"""
		
		# Récupération de la liste des fichiers chargés (avec canal alpha)
		self.listeChemAVcanAlph=self.afficheurImgSourceAvecCanalAlpha.getFiles()
		
		# Ouverture et mise ds une liste des dimensions des images
		listePrepaRedim=[Image.open(aA).size for aA in self.listeChemAVcanAlph]
		
		# Merci beaucoup à Marc Keller de la liste: python at aful.org de m'avoir
		# aidé pour cette partie (les 4 lignes en dessous)
		dictSeq={}.fromkeys(listePrepaRedim, 0)
		for cle in listePrepaRedim: dictSeq[cle]+=1
		self.lStatDimSeq=sorted(zip(dictSeq.itervalues(), dictSeq.iterkeys()), reverse=1)
		self.dimStatImg=self.lStatDimSeq[0][1]
		
		#print "Toutes les dimensions des images (avec le nbre d'images):", self.lStatDimSeq
		EkdPrint(u"Toutes les dimensions des images (avec le nbre d'images): " + str(self.lStatDimSeq))
		#print 'Dimension des images la plus presente dans la sequence:', self.dimStatImg
		EkdPrint(u'Dimension des images la plus presente dans la sequence: ' + str(self.dimStatImg))
		#print "Nombre de tailles d'images différentes dans le lot :", len(self.lStatDimSeq)
		EkdPrint(u"Nombre de tailles d'images différentes dans le lot: " + str(len(self.lStatDimSeq)))
		
		if len(self.lStatDimSeq)>1: return 0
		else: return 1
	
	
	def redim_img_1(self):
		"""Si l'utilisateur charge des images avec des tailles complètement différentes --> les images de la séquence  peuvent être redimensionnées"""
		
		if not self.stat_dim_img_1():
			reply = QMessageBox.warning(self, 'Message',
			_(u"Vos images ne sont pas toutes de la même taille. Voulez-vous redimensionner les images de sortie à la taille la plus répandue dans la séquence ?. Dans la plupart des cas il faut répondre oui."), QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.No:
				return
			
			# Les images de tailles différentes à la plus répandue sont redimensionnées
			# dans un répertoire temporaire.
			# Les images redimensionnées voient leur chemin modifié dans la liste des
			# chemins des images sources. Les autres chemins ne changent pas.
			index=0
			for chemImg in self.listeChemAVcanAlph:
				obImg=Image.open(chemImg)
				if obImg.size!=self.dimStatImg:
					pass
				sRedim=obImg.resize(self.dimStatImg, Image.ANTIALIAS)
				chemSortie = self.repTampon+'redim_1'+os.sep+os.path.basename(chemImg)
				sRedim.save(chemSortie)
				self.listeChemAVcanAlph[index] = chemSortie
				index += 1


	def stat_dim_img_2(self):
		"""Calcul statistique des dimensions des images les plus présentes dans le lot"""

		# Récupération de la liste des fichiers chargés (sans canal alpha)
		self.listeChemSANScanAlph=self.afficheurImgSourceSansCanalAlpha.getFiles()
		###########################################################################
		
		# Ouverture et mise ds une liste des dimensions des images
		listePrepaRedim=[Image.open(aA).size for aA in self.listeChemSANScanAlph]
		
		# Merci beaucoup à Marc Keller de la liste: python at aful.org de m'avoir
		# aidé pour cette partie (les 4 lignes en dessous)
		dictSeq={}.fromkeys(listePrepaRedim, 0)
		for cle in listePrepaRedim: dictSeq[cle]+=1
		self.lStatDimSeq=sorted(zip(dictSeq.itervalues(), dictSeq.iterkeys()), reverse=1)
		self.dimStatImg=self.lStatDimSeq[0][1]
		
		#print self.dimStatImg
		EkdPrint(self.dimStatImg)
		
		#print "Toutes les dimensions des images (avec le nbre d'images):", self.lStatDimSeq
		EkdPrint(u"Toutes les dimensions des images (avec le nbre d'images): " + str(self.lStatDimSeq))
		#print 'Dimension des images la plus presente dans la sequence:', self.dimStatImg
		EkdPrint(u'Dimension des images la plus presente dans la sequence: ' + str(self.dimStatImg))
		#print "Nombre de tailles d'images différentes dans le lot :", len(self.lStatDimSeq)
		EkdPrint(u"Nombre de tailles d'images différentes dans le lot: " + str(len(self.lStatDimSeq)))
		
		if len(self.lStatDimSeq)>1: return 0
		else: return 1
	
	
	def redim_img_2(self):
		"""Si l'utilisateur charge des images avec des tailles complètement différentes --> les images de la séquence  peuvent être redimensionnées"""
		
		if not self.stat_dim_img_2():
			reply = QMessageBox.warning(self, 'Message',
			_(u"Vos images ne sont pas toutes de la même taille. Voulez-vous redimensionner les images de sortie à la taille la plus répandue dans la séquence ?. Dans la plupart des cas il faut répondre oui."), QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.No:
				return
			
			# Les images de tailles différentes à la plus répandue sont redimensionnées
			# dans un répertoire temporaire.
			# Les images redimensionnées voient leur chemin modifié dans la liste des
			# chemins des images sources. Les autres chemins ne changent pas.
			index=0
			for chemImg in self.listeChemSANScanAlph:
				obImg=Image.open(chemImg)
				if obImg.size!=self.dimStatImg:
					pass
				sRedim=obImg.resize(self.dimStatImg, Image.ANTIALIAS)
				chemSortie = self.repTampon+'redim_2'+os.sep+os.path.basename(chemImg)
				sRedim.save(chemSortie)
				self.listeChemSANScanAlph[index] = chemSortie
				index += 1


	def visu_1ere_derniere_img(self):
		"""Visionnement du compositing avant application"""
		
		# Si l'utilisateur charge des images de taille différente, fait le traitement 
		# ...,  recharge de nouvelles images, il faut que les répertoires de redimen-
		# sionnement soient vidés
		
		listePresRedim_1=glob.glob(self.repTampon+'redim_1'+os.sep+'*.*')
		listePresRedim_1.sort()
		if len(listePresRedim_1)>0:
			for parcR_1 in listePresRedim_1: os.remove(parcR_1)
			
		listePresRedim_2=glob.glob(self.repTampon+'redim_2'+os.sep+'*.*')
		listePresRedim_2.sort()
		if len(listePresRedim_2)>0:
			for parcR_2 in listePresRedim_2: os.remove(parcR_2)
		

		# Récupération de la liste des fichiers chargés (avec canal alpha)
		self.listeChemAVcanAlph=self.afficheurImgSourceAvecCanalAlpha.getFiles()
		self.listeChemAVcanAlph.sort()
		
		# Récupération de la liste des fichiers chargés (sans canal alpha)
		self.listeChemSANScanAlph=self.afficheurImgSourceSansCanalAlpha.getFiles()
		self.listeChemSANScanAlph.sort()
		
		
		# Vérification du fait que les fichiers avec canal alpha chargés contiennent bien
		# un canal alpha (RGBA) ... sinon affichage d'une boîte de dialogue d'erreur et arrêt
		# du traitement des images
		for parcMode in self.listeChemAVcanAlph:
			imVerifCanAlph=Image.open(parcMode)
			if imVerifCanAlph.mode!='RGBA':
				messErr=QMessageBox(self)
				messErr.setText(_(u"<b>Vous avez chargé des images sans canal alpha</b> (c'est à dire sans transparence) et ce à partir de l'onglet <b>Image(s) avec canal alpha</b>. Sans transparence, vous ne pouvez, en aucun cas, appliquer un compositing (vos images doivent être en mode RGBA pour que cela réussisse) !."))
				messErr.setWindowTitle(_(u"Erreur"))
				messErr.setIcon(QMessageBox.Critical)
				messErr.exec_()
				return


		# ----- TRAVAIL PREPARATOIRE --- Redimensionnement des images -----------------
		try:
			
			nbreElem_1=len(self.listeChemAVcanAlph)
			nbreElem_2=len(self.listeChemSANScanAlph)
			# Appel des fonction de redimensionnement
			self.redim_img_1()
			self.redim_img_2()
			# Récup des listes contenant les fichiers
			repRedimTemp_1=glob.glob(self.repTampon+'redim_1'+os.sep+'*.*')
			repRedimTemp_1.sort()
			repRedimTemp_2=glob.glob(self.repTampon+'redim_2'+os.sep+'*.*')
			repRedimTemp_2.sort()
	
		except:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"<p>Vous n'avez pas chargé d'image(s) (bouton Ajouter) dans l'onglet <b>Image(s) avec canal aplpha</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) avec canal aplpha</b>, que dans <b>Image(s) sans canal aplpha</b>.</p>"))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()
			return
		# -----------------------------------------------------------------------------
		
		
		try:
			# tImgAVcanAlph --> taille des images avec canal alpha
			# tImgSANScanAlph --> taille des images avec canal alpha
			# =/= --> différent
			# == --> strictement ègal
		
			# Si tImgAVcanAlph == entre elles et tImgSANScanAlph == entre elles
			# mais tImgAVcanAlph =/= tImgSANScanAlph (tImgAVcanAlph == tImgSANScanAlph
			# est aussi valable)
			if len(repRedimTemp_1)==0 and len(repRedimTemp_2)==0:
				im01=Image.open(self.listeChemAVcanAlph[nbreElem_1-1])
				im02=Image.open(self.listeChemSANScanAlph[0])
				# Redimensionnement à la tImgAVcanAlph
				im02=im02.resize(Image.open(self.listeChemAVcanAlph[nbreElem_1-1]).size, Image.ANTIALIAS)
				imgCompoUndeChaque=Image.composite(im01, im02, im01)
			# Si tImgAVcanAlph == entre elles et tImgSANScanAlph =/= entre elles
			elif len(repRedimTemp_1)==0 and len(repRedimTemp_2)>1:
				im01=Image.open(self.listeChemAVcanAlph[nbreElem_1-1])
				im02=Image.open(repRedimTemp_2[0])
				# Redimensionnement à la tImgAVcanAlph
				im02=im02.resize(Image.open(self.listeChemAVcanAlph[nbreElem_1-1]).size, Image.ANTIALIAS)
				imgCompoUndeChaque=Image.composite(im01, im02, im01)
			# Si tImgAVcanAlph =/= entre elles et tImgSANScanAlph =/= entre elles
			# Plusieurs images avec can alpha et plusieurs images sans can alpha
			elif len(repRedimTemp_1)>1 and len(repRedimTemp_2)>1:
				im01=Image.open(repRedimTemp_1[nbreElem_1-1])
				im02=Image.open(repRedimTemp_2[0])
				# Redimensionnement à la tImgAVcanAlph
				im02=im02.resize(Image.open(repRedimTemp_1[nbreElem_1-1]).size, Image.ANTIALIAS)
				imgCompoUndeChaque=Image.composite(im01, im02, im01)
			# Si tImgAVcanAlph =/= entre elles et tImgSANScanAlph == ... là on a
			# qu'une image sans canal alpha	ce qui correspond à un arrière plan fixe
			elif len(repRedimTemp_1)>1 and len(repRedimTemp_2)==0:
				im01=Image.open(repRedimTemp_1[nbreElem_1-1])
				im02=Image.open(self.listeChemSANScanAlph[0])
				# Redimensionnement à la tImgAVcanAlph
				im02=im02.resize(Image.open(repRedimTemp_1[nbreElem_1-1]).size, Image.ANTIALIAS)
				imgCompoUndeChaque=Image.composite(im01, im02, im01)
		
		except:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"<p><b>Première situation d'erreur:</b> Vous n'avez pas chargé d'image(s) (bouton Ajouter) dans l'onglet <b>Image(s) avec canal aplpha</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) avec canal aplpha</b>, que dans <b>Image(s) sans canal aplpha</b>.</p><p><b>Seconde situation d'erreur:</b> la visualisation de l'image ne peut pas avoir lieu car vous avez répondu non au moins une fois au moment du redimensionnement des images. Recommencez et répondez oui aux deux boîtes de dialogue.</p>"))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()
			return
		
		# Sauvegarde des images resultant du Compositing
		self.cheminCourantSauv = self.repTamponVisuVoirRes+'visu_compositing_'+string.zfill((1), 6)+'.png'
		imgCompoUndeChaque.save(self.cheminCourantSauv, "PNG")

		# Affichage de l'image temporaire 
		# Ouverture d'une boite de dialogue affichant l'aperçu.
		#
		# Affichage par le bouton Voir le résultat
		visio = VisionneurEvolue(self.cheminCourantSauv)
		visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
		visio.exec_()
		
		return 0
	
	
	def appliquer(self):
		"""Appliquer le compositing"""

		# Si l'utilisateur charge des images de taille différente, fait le traitement 
		# ...,  recharge de nouvelles images, il faut que les répertoires de redimen-
		# sionnement soient vidés
		
		listePresRedim_1=glob.glob(self.repTampon+'redim_1'+os.sep+'*.*')
		listePresRedim_1.sort()
		if len(listePresRedim_1)>0:
			for parcR_1 in listePresRedim_1: os.remove(parcR_1)
			
		listePresRedim_2=glob.glob(self.repTampon+'redim_2'+os.sep+'*.*')
		listePresRedim_2.sort()
		if len(listePresRedim_2)>0:
			for parcR_2 in listePresRedim_2: os.remove(parcR_2)
		
		# La liste pour l'affichage des images ds l'interface est
		# vidée pour que les images affichées ne s'amoncellent pas
		# si plusieurs rendus à la suite
		self.listeImgDestin=[]

		# Récupération de la liste des fichiers chargés (avec canal alpha)
		self.listeChemAVcanAlph=self.afficheurImgSourceAvecCanalAlpha.getFiles()
		self.listeChemAVcanAlph.sort()
		# Récupération de la liste des fichiers chargés (sans canal alpha)
		self.listeChemSANScanAlph=self.afficheurImgSourceSansCanalAlpha.getFiles()
		self.listeChemSANScanAlph.sort()

		# Vérification du fait que les fichiers avec canal alpha chargés contiennent bien
		# un canal alpha (RGBA) ... sinon affichage d'une boîte de dialogue d'erreur et arrêt
		# du traitement des images
		for parcMode in self.listeChemAVcanAlph:
			imVerifCanAlph=Image.open(parcMode)
			if imVerifCanAlph.mode!='RGBA':
				messErr=QMessageBox(self)
				messErr.setText(_(u"<b>Vous avez chargé des images sans canal alpha</b> (c'est à dire sans transparence) et ce à partir de l'onglet <b>Image(s) avec canal alpha</b>. Sans transparence, vous ne pouvez, en aucun cas, appliquer un compositing (vos images doivent être en mode RGBA pour que cela réussisse) !."))
				messErr.setWindowTitle(_(u"Erreur"))
				messErr.setIcon(QMessageBox.Critical)
				messErr.exec_()
				return


		# ----- TRAVAIL PREPARATOIRE --- Redimensionnement des images -----------------
		try:
			
			nbreElem_1=len(self.listeChemAVcanAlph)
			nbreElem_2=len(self.listeChemSANScanAlph)
			# Appel des fonction de redimensionnement
			self.redim_img_1()
			self.redim_img_2()
			# Récup des listes contenant les fichiers
			### Le 18/09/09 ## ...+'redim_1/*.*' transformé en ...+'redim_1'+os.sep+'*.*'
			repRedimTemp_1=glob.glob(self.repTampon+'redim_1'+os.sep+'*.*')
			repRedimTemp_1.sort()
			### Le 18/09/09 ## ...+'redim_2/*.*' transformé en ...+'redim_2'+os.sep+'*.*'
			repRedimTemp_2=glob.glob(self.repTampon+'redim_2'+os.sep+'*.*')
			repRedimTemp_2.sort()
	
		except:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"<p>Vous n'avez pas chargé d'image(s) (bouton Ajouter) dans l'onglet <b>Image(s) avec canal aplpha</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) avec canal aplpha</b>, que dans <b>Image(s) sans canal aplpha</b>.</p>"))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()
			return
		# -----------------------------------------------------------------------------
		

    		# -----------------------------------------------------------------------------
		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
		#------------------------------------------------------------------------------

		# Utilisation de la nouvelle boîte de dialogue de sauvegarde
		suffix=""
                self.chemDossierSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.chemDossierSauv = self.chemDossierSauv.getFile()
		
		if not self.chemDossierSauv: return
		
		# Liste pour affichage (ds le tabwidget)
		listeAff_1=[]
		listeAff_2=[]
		listeAff_3=[]
		
		# Barre de progression dans une fenêtre séparée . Attention la fenêtre
		# de la barre se ferme dès que la progression est terminée . En cas de
		# process très court, la fenêtre peut n'apparaître que très brièvement
		# (voire pas du tout si le temps est très très court) .
		self.progress=QProgressDialog(_(u"Progression ..."), _(u"Arrêter le processus"), 0, 100)
		self.progress.setWindowTitle(_(u'EnKoDeur-Mixeur. Fenêtre de progression'))
		# Attribution des nouvelles dimensions 
		self.progress.setMinimumWidth(500)
		self.progress.setMinimumHeight(100)

		# On implémente les chemins des fichiers dans une variable
		# pour préparer l'affichage des infos
		texte1=_(u" Image(s) avec canal alpha chargée(s)")
		texte2=_(u" Image(s) sans canal alpha chargée(s)")
		texte3=_(u" Résultat image(s) composite")
		a='#'*36
		self.infosImgProv_1=a+'\n#'+texte1+'\n'+a
		self.infosImgProv_2=a+'\n#'+texte2+'\n'+a
		self.infosImgProv_3=a+'\n#'+texte3+'\n'+a
		
		# -------------------------------------------------------------------
		# Si le nbre d'images chargées avec canal alpha est égal à 1 ...
		# en fait si l'utilisateur ne charge qu'une image avec et sans canal
		# alpha ...
		# -------------------------------------------------------------------
		if nbreElem_1 == 1:
		
			try :
				
                		# Ouverture des images (im01 --> avec canal alpha et 
				# im02 --> sans canal alpha)
                		im01=Image.open(self.listeChemAVcanAlph[0])
                		im02=Image.open(self.listeChemSANScanAlph[0])
				
				# Récup de la dimension des l'image chargée avec canal alpha
				w_1, h_1=im01.size
				# Récup de la dimension des l'image chargée sans canal alpha
				w_2, h_2=im02.size
				# Redimensionnement de l'image sans canal alpha à la taille de l'image avec canal alpha
				if (int(w_1), int(h_1)) != (int(w_2), int(h_2)):
					im02=im02.resize(Image.open(self.listeChemAVcanAlph[0]).size, Image.ANTIALIAS)
				
                		# Application du compositing
                		imgCompoUndeChaque=Image.composite(im01, im02, im01)

                		# Sauvegarde des images resultant du Compositing
				self.cheminCourantSauv = self.chemDossierSauv+'_'+string.zfill(self.spin1.value(), self.spin2.value())+'.png'
				imgCompoUndeChaque.save(self.cheminCourantSauv, "PNG")

				# Ajout des images par la variable self.cheminCourantSauv dans la liste self.listeChemin
				# Cette liste sert à récupérer les images pour l'affichage des images ds l'inteface
				self.listeImgDestin.append(self.cheminCourantSauv)

				# Affichage des images après traitement
				#
				# Changement d'onglet et fonctions associées
				self.conversionImg = 1
				self.metaFctTab(self.indexTabImgDestin)
				
				# log
				listeAff_1.append(self.listeChemAVcanAlph[0])
				listeAff_2.append(self.listeChemSANScanAlph[0])
				listeAff_3.append(self.cheminCourantSauv)
				
			except: 
				messageErreur=QMessageBox(self)
				messageErreur.setText(_(u"<p>Vous n'avez pas chargé d'image(s) (bouton Ajouter) dans l'onglet <b>Image(s) avec canal aplpha</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) avec canal aplpha</b>, que dans <b>Image(s) sans canal aplpha</b>.</p>"))
				messageErreur.setWindowTitle(_(u"Erreur"))
				messageErreur.setIcon(QMessageBox.Critical)
				messageErreur.exec_()

		# -------------------------------------------------------------------
		# Si le nbre d'images chargées sans canal alpha est supérieur à 1 ...
		# ce qui correspond à un travail avec un fond animé
		# -------------------------------------------------------------------
		elif nbreElem_2 > 1:
		
			self.progress.show()
		
			nbre=min(nbreElem_1, nbreElem_2)
			
			try :
				for parcoursComposit_un in range(nbre):
					
                			# Ouverture des images (imm1 --> avec canal alpha et 
					# imm2 --> sans canal alpha)
                			imm1=Image.open(self.listeChemAVcanAlph[parcoursComposit_un])
                			imm2=Image.open(self.listeChemSANScanAlph[parcoursComposit_un])

					# ------------ Images exactement de même taille ---------------------
					# Récup des dimensions des images chargées avec canal alpha
					w_1, h_1=imm1.size
					# Récup des dimensions des images chargées sans canal alpha
					w_2, h_2=imm2.size
					# Si l'utilisateur à chargé des images ayant strictement la même taille
					if w_1==w_2 and h_1==h_2:
						# Redimensionnement des images sans canal alpha à la taille
						# des images avec canal alpha
						imm2=imm2.resize(Image.open(self.listeChemAVcanAlph[0]).size, Image.ANTIALIAS)
					# -------------------------------------------------------------------
					# ------------ Images de tailles différentes ------------------------
					# Si l'utilisateur à chargé des images avec canal alpha ayant la même
					# taille entre elles mais n'ayant pas la même taille que les images
					# sans canal alpha (qui ont la même taille entre elles)
					if w_1!=w_2 or h_1!=h_2:
						# Redimensionnement des images sans canal alpha à la taille
						# des images avec canal alpha
						imm2=imm2.resize(Image.open(self.listeChemAVcanAlph[0]).size, Image.ANTIALIAS)
					# Si l'utilisateur charge des images avec avec canal alpha de tailles
					# différentes entre elles et des images sans canal alpha aussi différentes
					# entre elles, les images sans canal alpha sont redimensionnées à la dimension
					# des images avec canal alpha
					if len(repRedimTemp_1)>0 and len(repRedimTemp_2)>0:
						if (int(w_1), int(h_1)) != (int(w_2), int(h_2)):
							imm2=imm2.resize(Image.open(repRedimTemp_1[0]).size, Image.ANTIALIAS)
					# Si l'utilisateur charge des images avec canal alpha toutes de même taille mais
					# aussi charge des images sans canal alpha de tailles complètement différentes,
					# les images sans canal alpha sont redimensionnées à la dimension des images
					# avec canal alpha
					if len(repRedimTemp_2)>0 and len(repRedimTemp_1)==0:
						if (int(w_1), int(h_1)) != (int(w_2), int(h_2)):
							imm2=imm2.resize(Image.open(self.listeChemAVcanAlph[0]).size, Image.ANTIALIAS)
					# Si l'utilisateur charge des images sans canal alpha toutes de même taille mais
					# aussi charge des images avec canal alpha de tailles complètement différentes,
					# les images avec canal alpha sont redimensionnées à la dimension de la 1ère
					# image avec canal alpha
					if len(repRedimTemp_1)>0 and len(repRedimTemp_2)==0:
						if (int(w_1), int(h_1)) != (int(w_2), int(h_2)):
							imm1=imm1.resize(Image.open(self.listeChemAVcanAlph[0]).size, Image.ANTIALIAS)

                			# Application du compositing
                			imgCompo_1=Image.composite(imm1, imm2, imm1)

					# Sauvegarde des images resultant du Compositing
					self.cheminCourantSauv = self.chemDossierSauv+'_'+string.zfill(parcoursComposit_un+self.spin1.value(), self.spin2.value())+'.png'
					imgCompo_1.save(self.cheminCourantSauv, "PNG")

					# Ajout des images par la variable self.cheminCourantSauv dans la liste self.listeChemin
					# Cette liste sert à récupérer les images pour l'affichage des images ds l'inteface
					self.listeImgDestin.append(self.cheminCourantSauv)
					
					# Affichage des images après traitement
					#
					# Changement d'onglet et fonctions associées
					self.conversionImg = 1
					self.metaFctTab(self.indexTabImgDestin)
				
					# log
					listeAff_1.append(self.listeChemAVcanAlph[parcoursComposit_un])
					listeAff_2.append(self.listeChemSANScanAlph[parcoursComposit_un])
					listeAff_3.append(self.cheminCourantSauv)
					
					# --------------------------------------------
					# Affichage de la progression (avec
					# QProgressDialog) ds une fenêtre séparée
					val_pourc_1=((parcoursComposit_un+1)*100)/nbre

					# Bouton Cancel pour arrêter la progression donc le process
					if (self.progress.wasCanceled()): break

					self.progress.setValue(val_pourc_1)
			
					QApplication.processEvents()
					# --------------------------------------------

			except:
				messageErreur=QMessageBox(self)
				messageErreur.setText(_(u"<p><b>Première situation d'erreur:</b> Vous n'avez pas chargé d'image(s) (bouton Ajouter) dans l'onglet <b>Image(s) avec canal aplpha</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) avec canal alpha</b>, que dans <b>Image(s) sans canal aplpha</b>.</p><p><b>Seconde situation d'erreur:</b> la visualisation et/ou le traitement image(s) ne peut pas avoir lieu car vous avez répondu non au moins une fois au moment du redimensionnement des images. Recommencez et répondez oui aux deux boîtes de dialogue.</p>"))
				messageErreur.setWindowTitle(_(u"Erreur"))
				messageErreur.setIcon(QMessageBox.Critical)
				messageErreur.exec_()
				
		# -------------------------------------------------------------------
		# Si le nbre d'images chargées sans canal alpha est égal à 1 ...
		# ce qui correspond à un travail avec un fond fixe (caméra fixe)
		# -------------------------------------------------------------------
		elif nbreElem_2 == 1:
			
			self.progress.show()
			
			listeTempCompo=[]
			
			try :
				for parcoursDupli in range(nbreElem_1):
					
					dupliString=self.listeChemSANScanAlph[0]
					
					# Ouverture de l'image 
					reS=Image.open(dupliString)
					
					# Sauvegarde de l'image après multiplication
					reS.save(str(self.repTampon+'d_'+string.zfill(parcoursDupli+self.spin1.value(), self.spin2.value())+'.png'), 'PNG')
					
					# Remplissage de la liste tampon
					listeTempCompo.append(self.repTampon+'d_'+string.zfill(parcoursDupli+self.spin1.value(), self.spin2.value())+'.png')
					
					# Copie de l'ensemble des images (avec canal alpha)
					# chargees par l'utilisateur, dans le sous-repertoire
					# temporaire --> /EkdConfig.getTempDir()/ekd/tampon/temp_duplication/ . Il est
					# indispensable que ces images se retrouvent dans le meme
					# repertoire que les images multipliées (sans canal alpha)
					for parCop in self.listeChemSANScanAlph: 
						cop=shutil.copy(parCop, self.repTampon)
						
					# Ouverture des images (imm3 --> avec canal alpha et 
					# imm4 --> sans canal alpha) 
					imm3=Image.open(self.listeChemAVcanAlph[parcoursDupli])
					imm4=Image.open(listeTempCompo[parcoursDupli])

					# ------------ Images de même taille --------------------------------
					# Récup des dimensions des images chargées avec canal alpha
					w_1, h_1=imm3.size
					# Récup des dimensions des images chargées sans canal alpha
					w_2, h_2=imm4.size
					# Si l'utilisateur à chargé des images ayant strictement la même taille
					if w_1==w_2 and h_1==h_2:
						# Redimensionnement des images sans canal alpha à la taille
						# des images avec canal alpha
						imm4=imm4.resize(Image.open(self.listeChemAVcanAlph[0]).size, Image.ANTIALIAS)
					# -------------------------------------------------------------------
					# ------------ Images de tailles différentes ------------------------
					# Si le rep /EkdConfig.getTempDir()/ekd/tampon/temp_duplication/redim_1 contient des fichiers ...
					if len(repRedimTemp_1)>0:
						# Ouverture de la dernière image dans:
						# /EkdConfig.getTempDir()/ekd/tampon/temp_duplication/redim_1
						imm3=Image.open(repRedimTemp_1[parcoursDupli])
						# Dimension (w_1 --> largeur, h_1 --> hauteur)
						w_1, h_1=imm3.size
					# Si le rep /EkdConfig.getTempDir()/ekd/tampon/temp_duplication/redim_2 contient des fichiers ...
					if len(repRedimTemp_2)>0:
						# Ouverture de la première image dans:
						# /EkdConfig.getTempDir()/ekd/tampon/temp_duplication/redim_2
						imm4=Image.open(repRedimTemp_2[parcoursDupli])
						# Dimension (w_2 --> largeur, h_2 --> hauteur)
						w_2, h_2=imm4.size
					# Si l'utilisateur charge des images avec canal alpha de taille complètement différentes 
					# (les images sont redimensionnées ds le rep tempo redim_1)de l'image sans canal alpha, 
					# l'image sans canal alpha est redimensionnée à la taille des images avec canal alpha du 
					# répertoire temporaire. Autrement l'image sans canal alpha est redimensionnée à la taille 
					# de la 1ère image avec canal alpha chargée
					if len(repRedimTemp_1)>0:
						if (int(w_1), int(h_1)) != (int(w_2), int(h_2)):
							imm4=imm4.resize(Image.open(repRedimTemp_1[0]).size, Image.ANTIALIAS)
					else:
						imm4=imm4.resize(Image.open(self.listeChemAVcanAlph[0]).size, Image.ANTIALIAS)
					
					# Application du compositing .
					imgCompo_2=Image.composite(imm3, imm4, imm3)
					
					# Sauvegarde des images resultant du Compositing
					self.cheminCourantSauv = self.chemDossierSauv+'_'+string.zfill(parcoursDupli+self.spin1.value(), self.spin2.value())+'.png'
					# ----------------------------------------------------------------------
					imgCompo_2.save(self.cheminCourantSauv, "PNG")

					# Ajout des images par la variable self.cheminCourantSauv dans la liste self.listeChemin
					# Cette liste sert à récupérer les images pour l'affichage des images ds l'inteface
					self.listeImgDestin.append(self.cheminCourantSauv)
					
					# Affichage des images après traitement
					#
					# Changement d'onglet et fonctions associées
					self.conversionImg = 1
					self.metaFctTab(self.indexTabImgDestin)
				
					# log
					listeAff_1.append(self.listeChemAVcanAlph[parcoursDupli])
					listeAff_2.append(listeTempCompo[parcoursDupli])
					listeAff_3.append(self.cheminCourantSauv)
					
					# --------------------------------------------
					# Affichage de la progression (avec
					# QProgressDialog) ds une fenêtre séparée .
					val_pourc_2=((parcoursDupli+1)*100)/nbreElem_1
	
					# Bouton Cancel pour arrêter la progression donc le process
					if (self.progress.wasCanceled()): break
	
					self.progress.setValue(val_pourc_2)
			
					QApplication.processEvents()
					# --------------------------------------------

			except:
				messageErreur=QMessageBox(self)
				messageErreur.setText(_(u"<p><b>Première situation d'erreur:</b> Vous n'avez pas chargé d'image(s) (bouton Ajouter) dans l'onglet <b>Image(s) avec canal aplpha</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) avec canal alpha</b>, que dans <b>Image(s) sans canal aplpha</b>.</p><p><b>Seconde situation d'erreur:</b> la visualisation et/ou le traitement image(s) ne peut pas avoir lieu car vous avez répondu non au moins une fois au moment du redimensionnement des images. Recommencez et répondez oui aux deux boîtes de dialogue.</p>"))
				messageErreur.setWindowTitle(_(u"Erreur"))
				messageErreur.setIcon(QMessageBox.Critical)
				messageErreur.exec_()

		# Images chargées avec canal alpha
		for parcStatRendu_1 in listeAff_1:
			self.infosImgProv_1=self.infosImgProv_1+'\n'+parcStatRendu_1
			
		# Pages sauvegardées
		for parcStatRendu_2 in listeAff_2:
			self.infosImgProv_2=self.infosImgProv_2+'\n'+parcStatRendu_2
			
		# Compositing
		for parcStatRendu_3 in listeAff_3:
			self.infosImgProv_3=self.infosImgProv_3+'\n'+parcStatRendu_3
		
		# affichage des infos dans l'onglet
		self.zoneAffichInfosImg.setText(self.infosImgProv_1+'\n\n'+self.infosImgProv_2+'\n\n'+self.infosImgProv_3+'\n\n')
		self.fram.setEnabled(True)
	
	
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""

		# Utilisation de EkdAide
		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<p><b>Vous allez ici superposer des images avec un canal alpha (transparence) sur d'autres images sans canal alpha (ces dernières sont en quelque sorte l'arrière-plan). Vous avez aussi ici la possibilité de travailler avec un arrière-plan composé d'une seule image, en cas de travail en plan fixe (le programme duplique lui-même les images).</b></p><p><b>Voilà la définition que donne Wikipédia du terme compositing (c'est le terme exact): 'La composition (en anglais compositing) est un ensemble de méthodes numériques consistant à mélanger plusieurs sources d’images pour en faire un plan unique qui sera intégré dans le montage. Pour un film d'animation, il s'agit de l'étape finale de fabrication qui consiste à assembler toutes les couches des décors, des personnages et à réaliser les effets de caméra, à animer certains déplacements, et effets spéciaux. En cinéma de prise de vue réel, il consiste surtout à réaliser des effets spéciaux et à truquer des vidéos. C'est l'un des derniers maillons de la chaîne de l'image dans la réalisation d'un film.<br>Les sources peuvent être des images numérisées de cinéma, de dessin, de vidéo, des images numériques (dessin, 3D, effets spéciaux).'<br>Source: http://fr.wikipedia.org/wiki/Compositing</b></p><p>Dans l'onglet <b>'Image(s) avec canal alpha'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Passez maintenant dans l'onglet <b>'Image(s) sans canal alpha'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images).</p><p>Dans <b>'Réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b>. Cliquez sur le bouton <b>'Voir le résultat'</b> vous voyez à ce moment là, le résultat du compositing entre la dernière image du lot de votre premier groupe d'image (images avec transparence) et la première image du lot de votre second groupe d'image (images sans transparence), s'afficher dans une nouvelle fenêtre.</p>Pour finir cliquez sur le bouton <b>'Appliquer et sauver'</b>, entrez le titre de votre futur compositing (après <b>'Nom de fichier'</b>) dans cette dernière boîte (vous aurez évidemment pris soin de sélectionner le répertoire de destination de votre compositing). Cliquez sur le bouton <b>'Enregistrer'</b>.<p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>Image(s) après traitement</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>'Infos'</b> vous permet de voir le filtre utilisé, les image(s) chargée(s) et les image(s) convertie(s).</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSourceAvecCanalAlpha.saveFileLocation(self.idSection, u'sourcesa')
		self.afficheurImgSourceSansCanalAlpha.saveFileLocation(self.idSection, u'sourcessa')
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2.value()))


	def load(self) :
		self.afficheurImgSourceAvecCanalAlpha.loadFileLocation(self.idSection, u'sourcesa')
		self.afficheurImgSourceSansCanalAlpha.loadFileLocation(self.idSection, u'sourcessa')
		self.spin1.setValue(int(EkdConfig.get(self.idSection, u'spin1')))
		self.spin2.setValue(int(EkdConfig.get(self.idSection, u'spin2')))	
