#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, string, glob
import Image
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_modules_image.image_base import Base, SpinSliders, SpinSlider

from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue

BaseImg = Base # pour différencier les 2 bases
from gui_modules_common.gui_base import Base
from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg

# Nouvelle fenêtre d'aide
from gui_modules_common.EkdWidgets import EkdAide
# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

debug = 1


class Image_Divers_MultiplicImg(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Multiplication d'images
	# -----------------------------------
	def __init__(self, statusBar, geometry):
        	QWidget.__init__(self)
		
		# ----------------------------
		# Quelques paramètres de base
		# ----------------------------
		
		#=== Création des répertoires temporaires ===#
		
		# Utilisation de EkdConfig pour les repertoires tmp
		self.repTampon = EkdConfig.getTempDir() + os.sep + "tampon" + os.sep + "multiplic_img" + os.sep

		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)
		if os.path.isdir(self.repTampon+'redim'+os.sep) is False:
        		os.makedirs(self.repTampon+'redim'+os.sep)

		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			if len(toutRepCompo)>0:
				os.remove(toutRepCompo)

		for toutRepCompoRedim in glob.glob(self.repTampon+'redim'+os.sep+'*.*'):
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

		# On joue avec l'éritage de Base
		self.baseImg = BaseImg() # module de image

		# Gestion de la configuration via EkdConfig
		# Paramètres de configuration
		self.config = EkdConfig
		# Identifiant du cadre
		self.idSection = "image_multiplication"
		# Log du terminal
		self.baseImg.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		self.listeImgSource = []
		self.listeImgDestin = []
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		self.tabwidget=QTabWidget()
		
		#------------------
		# Onglet Réglages
		#------------------
		
		# Réglages 1
		
		# boite de combo pour régler les extensions pour la sauvegarde des images
		self.comboReglageExt=QComboBox()
		self.listeComboReglageExt=[(_(u'JPEG (.jpg)'), '.jpg'), (_(u'JPEG (.jpeg)'), '.jpeg'), (_(u'PNG (.png)'), '.png'), (_(u'BMP (.bmp)'), '.bmp'), (_(u'PPM (.ppm)'), '.ppm')]
		
		# Insertion des formats (les extensions pour la sauvegarde des images) dans la combo box
		for i in self.listeComboReglageExt:
                	self.comboReglageExt.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboReglageExt, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		self.baseImg.valeurComboIni(self.comboReglageExt, self.config, self.idSection, 'mult_format_ext')

		self.framReglage=QFrame()
		vboxReglage=QVBoxLayout(self.framReglage)
		
		self.grid = QGridLayout()
		
		self.labTraitImgNum=QLabel(_(u"Traitement à partir de l'image (numéro)"))
		self.grid.addWidget(self.labTraitImgNum, 0, 0)
		self.spin1_ImTrait=SpinSlider(1, 100000, 1, '', self)
		self.grid.addWidget(self.spin1_ImTrait, 0, 1)
		self.connect(self.spin1_ImTrait, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.labNbreChifNIm=QLabel(_(u"Nombre de chiffres après le nom de l'image"))
		self.grid.addWidget(self.labNbreChifNIm, 1, 0)
		self.spin2_ImTrait=SpinSlider(3, 18, 6, '', self)
		self.grid.addWidget(self.spin2_ImTrait, 1, 1)
		self.connect(self.spin2_ImTrait, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.grid.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid)
		vboxReglage.addStretch()
		
		# Réglages 2
		
		self.grid2 = QGridLayout()
		self.grid2.addWidget(QLabel(_(u"Multiplication, durée en secondes")), 0, 0)
		# Méta-widget: boite de spin + curseur
		# arguments: valeur debut, fin, defaut, identifiant configuration, parent
		self.spin1=SpinSlider(1, 300, 4, 'mult_duree_sec', self)
		self.grid2.addWidget(self.spin1, 0, 1)
		self.connect(self.spin1, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.grid2.addWidget(QLabel(_(u"Multiplication, nombre d'images/sec")), 1, 0)
		self.spin2=SpinSlider(1, 30, 1, 'mult_nbre_img_sec', self)
		self.grid2.addWidget(self.spin2, 1, 1)
		self.connect(self.spin2, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.grid2.addWidget(QLabel(_(u'Type de format après traitement')), 2, 0)
		self.grid2.addWidget(self.comboReglageExt, 2, 1)
		
		# Label qualité pour la qualité (compression) lors de la sauvegarde en JPEG
		self.labQualite=QLabel(_(u"Qualité"))
		self.labQualite.hide()

		self.grid2.addWidget(self.labQualite, 3, 0)
		# Réglage de la qualité pour la qualité (compression) lors de la sauvegarde en JPEG
		self.spin3=SpinSlider(1, 100, 75, 'qualiteJpeg', self)
		self.spin3.hide()
		
		i = self.comboReglageExt.currentIndex()
		idCombo=str(self.comboReglageExt.itemData(i).toStringList()[0])
		if idCombo in ['.jpg', '.jpeg']:
			self.labQualite.show()
			self.spin3.show()
		else:
			self.labQualite.hide()
			self.spin3.hide()

		self.grid2.addWidget(self.spin3, 3, 1)
		self.connect(self.spin3, SIGNAL("valueChanged(int)"), self.changeQualitePourJPEG)
		
		self.grid2.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid2)
		vboxReglage.addStretch()
		
		
		#=== Widgets mplayer ===#
		widget = QWidget()
		vboxMplayer = QVBoxLayout(widget)
		vboxMplayer.addStretch()
		hbox = QHBoxLayout()
		vboxMplayer.addLayout(hbox)
		hbox.addStretch()

		self.mplayer=Mplayer(taille=(350,252), choixWidget=(Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_SUR_UNE_LIGNE,Mplayer.PAS_PARCOURIR, Mplayer.LIST))
		
		hbox.addWidget(self.mplayer)
		hbox.addStretch()
		vboxMplayer.addStretch()
		
		#----------------
		# Onglet de log
		#----------------
		
		self.zoneAffichInfosImg = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneAffichInfosImg.insertPlainText = self.zoneAffichInfosImg.insertPlainText
		self.zoneAffichInfosImg.setReadOnly(True)
		self.framInfos=QFrame()
		vboxInfIm=QVBoxLayout(self.framInfos)
		vboxInfIm.addWidget(self.zoneAffichInfosImg)
		self.framInfos.setEnabled(False)
		
		# -------------------------------------------------
		# Onglets d'affichage image source et destination
		# -------------------------------------------------
		
		# Là où s'afficheront les images
		self.afficheurImgSource=SelectWidget(geometrie = self.mainWindowFrameGeometry)
		self.afficheurImgDestination=Lecture_VisionImage(statusBar)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.
		
		self.indexTabImgSource = self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		self.indexTabImgReglage = self.tabwidget.addTab(self.framReglage, _(u'Réglages'))
		self.indexTabImgDestin = self.tabwidget.addTab(self.afficheurImgDestination, _(u'Image(s) après traitement'))
		self.indexTabVideoDestin = self.tabwidget.addTab(widget, _(u'Vidéo créé'))
		self.indexTabImgInfos = self.tabwidget.addTab(self.framInfos, _(u'Infos'))
		
		vbox.addWidget(self.tabwidget)
		
		# -------------------------------------------
		# widgets du bas : curseur + ligne + boutons
		# -------------------------------------------
		
		# Boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones/icone_aide_128.png"))
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
		
		self.boutTransfImgVideo=QPushButton(_(u" Appliquer et sauver la vidéo"))
		self.boutTransfImgVideo.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		self.boutTransfImgVideo.setToolTip(_(u'<b>Multiplication des images et conversion en vidéo (codec: Motion JPEG) (.avi)</b>'))
		# Bouton inactif au départ
		self.boutTransfImgVideo.setEnabled(False)
		self.connect(self.boutTransfImgVideo, SIGNAL("clicked()"), self.transformImgEnVideo)
		
		self.boutMultImgUniquement=QPushButton(_(u" Appliquer et sauver les images"))
		self.boutMultImgUniquement.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		self.boutMultImgUniquement.setToolTip(_(u'<b>Multiplication des images seulement</b>'))
		# Bouton inactif au départ
		self.boutMultImgUniquement.setEnabled(False)
		self.connect(self.boutMultImgUniquement, SIGNAL("clicked()"), self.multiplicImgUniq)
		
		# Si l'utilisateur n'a pas chargé d'image les 2 boutons restent désactivés
		if self.modifImageSource == 0:
			self.boutTransfImgVideo.setEnabled(False)
			self.boutMultImgUniquement.setEnabled(False)

		# Ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons
		
		hbox=QHBoxLayout()
		hbox.addWidget(boutAide)
		hbox.addStretch()
		hbox.addWidget(self.boutTransfImgVideo)
		hbox.addStretch()
		hbox.addWidget(self.boutMultImgUniquement)
		vbox.addLayout(hbox)
		
		self.setLayout(vbox)

		#-----------------------------
		# Barre de progression
		#-----------------------------
		
		self.progress=QProgressDialog(_(u"Conversion en cours..."), _(u"Arrêter"), 0, 100)
		self.progress.setWindowTitle(_(u'EnKoDeur-Mixeur. Fenêtre de progression'))
		self.progress.setMinimumWidth(500)
		self.progress.setMinimumHeight(100)

		self.connect(self.tabwidget, SIGNAL("currentChanged(int)"), self.fctTab)

		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
		#----------------------------------------------------------------------------------------------------
		
		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifImgSource)
		
		#----------------------------------------------------------------------------------------------------
		# Signal pour afficher ou ne pas afficher les widgets de changement de qualité pour les images
		#----------------------------------------------------------------------------------------------------
		
		self.connect(self.comboReglageExt, SIGNAL("currentIndexChanged(int)"), self.changerQualJPEG)
		
		
	def changeValNbreImg_1(self):
		#print "Traitement a partir de l'image (numero):", self.spin1_ImTrait.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1_ImTrait.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2_ImTrait.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2_ImTrait.value())
		#print "Multiplication, durée en secondes:", self.spin1.value()
		EkdPrint(u"Multiplication, durée en secondes: %s" % self.spin1.value())
		# Affichage de la valeur du nbre d'img/sec
		#print "Multiplication, nombre d'images/sec:", self.spin2.value()
		EkdPrint(u"Multiplication, nombre d'images/sec: %s" % self.spin2.value())
		
		
	def changerComboReglage(self, i):
		"""Récup/affichage ds le terminal de l'index de self.comboReglageExt"""
		#print self.comboReglageExt.currentText()
		EkdPrint(u"%s" % self.comboReglageExt.currentText())
		self.config.set(self.idSection, 'mult_format_ext', self.listeComboReglageExt[i][1])
		
		
	def changerQualJPEG(self):
		''' Changement de la qualité pour les images jpeg à l'enregistrement '''

		# Si on sélectionne le format JPEG (avec extension .jpg ou .jpeg) dans la liste
		# déroulante, on peut régler la qualité du JPEG pour la sauvegarde
		if self.comboReglageExt.currentIndex() in [0, 1]:
			self.labQualite.show()
			self.spin3.show()
		# Si on sélectionne tous les autres formats, les widgets n'apparaissent pas
		else:
			self.labQualite.hide()
			self.spin3.hide()
		
		
	def changeQualitePourJPEG(self):
		#print "Compression JPEG, qualité:", self.spin3.value()
		EkdPrint(u"Compression JPEG, qualité: %s" % self.spin3.value())
	
		
	def modifImgSource(self, i):
		"""On active ou désactive les boutons d'action et on recharge le pseudo-aperçu en fonction du nombre d'images présentes dans le widget de sélection"""
		
		# Ce bouton est désactivé par défaut car c'est 
		# l'utilisateur qui choisit quel bouton activer
		self.boutMultImgUniquement.setEnabled(i)
		self.boutTransfImgVideo.setEnabled(i)
		
		self.modifImageSource = 1
		
		
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
			elif not self.boutMultImgUniquement.isEnabled() or self.modifImageSource:
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
		
		
	def stat_dim_img(self):
		"""Calcul statistique des dimensions des images les plus présentes dans le lot"""

		# Récupération de la liste des fichiers chargés
		self.listeImgSource=self.afficheurImgSource.getFiles()
		
		# Ouverture et mise ds une liste des dimensions des images
		listePrepaRedim=[Image.open(aA).size for aA in self.listeImgSource]
		
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
	
	
	def redim_img(self):
		"""Si l'utilisateur charge des images avec des tailles complètement différentes --> les images de la séquence  peuvent être redimensionnées"""
		
		if not self.stat_dim_img():
			reply = QMessageBox.warning(self, 'Message',
			_(u"Vos images ne sont pas toutes de la même taille. Voulez-vous redimensionner les images de sortie à la taille la plus répandue dans la séquence ?. Si vous répondez non, le traitement ne sera pas effectué."), QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.No:
				return
			
			# Les images de tailles différentes à la plus répandue sont redimensionnées
			# dans un répertoire temporaire.
			# Les images redimensionnées voient leur chemin modifié dans la liste des
			# chemins des images sources. Les autres chemins ne changent pas.
			index=0
			for chemImg in self.listeImgSource:
				obImg=Image.open(chemImg)
				if obImg.size!=self.dimStatImg:
					pass
				sRedim=obImg.resize(self.dimStatImg)
				chemSortie = self.repTampon+'redim'+os.sep+os.path.basename(chemImg)
				sRedim.save(chemSortie)
				self.listeImgSource[index] = chemSortie
				index += 1
				
				
	def multiplicImgUniq(self):
		""" Multiplication d'image --> utile pour affichage du titrage (après conversion image - vidéo) """
		
		# Redimensionner les images de tailles différentes
		self.redim_img()
		
		# Liste pour affichage des images chargées
		listeAff_1=[]
		# Liste pour affichage des images sauvegardées
		listeAff_2=[]

		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
		suffix=""
                self.chemDossierSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.chemDossierSauv = self.chemDossierSauv.getFile()
		
		if not self.chemDossierSauv: return
		
		# La liste pour l'affichage des images ds l'interface est
		# vidée pour que les images affichées ne s'amoncellent pas
		# si plusieurs rendus à la suite
		self.listeImgDestin=[]
		
		# Récupération de la liste des fichiers chargés
		self.listeImgSource=self.afficheurImgSource.getFiles()
		self.listeImgSource.sort()
		
		# Récup du format sélectionné par l'utilisateur
		i = self.comboReglageExt.currentIndex()
		ext=self.comboReglageExt.itemData(i).toString()
		ext=unicode(ext).lower()
		#print "Format (extension) d'enregistrement:", ext
		EkdPrint(u"Format (extension) d'enregistrement: %s" % ext)
		
		# Nombre d'éléments présents dans la liste
		nbreElem=len(self.listeImgSource)
		
		for j in range(nbreElem):
			
			spin1 = self.spin1.value() # Multiplication, durée en secondes
			spin2 = self.spin2.value() # Multiplication, nombre d'images/sec 
			nbreTotal = spin1 * spin2 # Calcul du nbre exact d'images (après récup des données utilisateur) 
			
			# Image chargée
			imPourDupli = self.listeImgSource[j]
					
			# Remplissage de la liste pour images chargées (Info)
			listeAff_1.append(imPourDupli)
			
			# Multiplication (rendu)
			for parc in range(nbreTotal):
				
				# On sélectionne le 'Type de format après traitement' à JPEG (.jpg) ou JPEG (.jpeg)
				if i in [0, 1]:
			
					# Ouverture de l'image 
					dup = Image.open(imPourDupli)
					# Application
					dup.save(self.chemDossierSauv+u'_'+string.zfill(j+1, self.spin2_ImTrait.value())+u'_'+string.zfill(parc+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+ext, quality=self.spin3.value())
					
					# Ajout des images par la variable self.cheminCourantSauv dans la liste
					# self.listeChemin. Cette liste sert à récupérer les images pour l'affichage
					# des images ds l'inteface
					self.listeImgDestin.append(self.chemDossierSauv+u'_'+string.zfill(j+1, self.spin2_ImTrait.value())+u'_'+string.zfill(parc+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+ext)

					# Remplissage de la liste des pages sauvegardées (Info)
					listeAff_2.append(self.chemDossierSauv+u'_'+string.zfill(j+1, self.spin2_ImTrait.value())+u'_'+string.zfill(parc+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+ext)
				
					# --------------------------------------------
					# Affichage de la progression (avec
					# QProgressDialog) ds une fenêtre séparée .
					val_pourc=((parc+1)*100)/nbreTotal

					# Bouton Cancel pour arrêter la progression donc le process
					if (self.progress.wasCanceled()):
						break

					self.progress.setValue(val_pourc)
		
					QApplication.processEvents()
					# --------------------------------------------
					
				# Si on sélectionne les autres formats que JPEG (.jpg) ou JPEG (.jpeg) ...
				else:
					
					# Ouverture de l'image 
					dup = Image.open(imPourDupli)
					# Application
					dup.save(self.chemDossierSauv+u'_'+string.zfill(j+1, self.spin2_ImTrait.value())+u'_'+string.zfill(parc+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+ext)
				
					# Ajout des images par la variable self.cheminCourantSauv dans la liste
					# self.listeChemin. Cette liste sert à récupérer les images pour l'affichage
					# des images ds l'inteface
					self.listeImgDestin.append(self.chemDossierSauv+u'_'+string.zfill(j+1, self.spin2_ImTrait.value())+u'_'+string.zfill(parc+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+ext)
				
					# Remplissage de la liste des pages sauvegardées (Info)
					listeAff_2.append(self.chemDossierSauv+u'_'+string.zfill(j+1, self.spin2_ImTrait.value())+u'_'+string.zfill(parc+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+ext)
				
					# --------------------------------------------
					# Affichage de la progression (avec
					# QProgressDialog) ds une fenêtre séparée .
					val_pourc=((parc+1)*100)/nbreTotal

					# Bouton Cancel pour arrêter la progression donc le process
					if (self.progress.wasCanceled()):
						break

					self.progress.setValue(val_pourc)
		
					QApplication.processEvents()
					# --------------------------------------------
					
		# Affichage des images après traitement
		#
		# Changement d'onglet et fonctions associées
		self.conversionImg = 1
		self.metaFctTab(self.indexTabImgDestin)

		# Affichage des infos sur l'image -------------------------	
		# On implémente les chemins des fichiers dans une variable
		# pour préparer l'affichage des infos
		texte1=_(u" Image(s) chargée(s)")
		texte2=_(u" Image(s) après multiplication")
		texte3=_(u" Nombre d'images totales après multiplication: ")
		a='#'*36
			
		self.infosImgProv_1=a+'\n#'+texte1+'\n'+a
		self.infosImgProv_2=a+'\n#'+texte2+'\n'+a
		self.infosImgProv_3=a+'\n#'+texte3+str(nbreTotal)+'\n'+a
		
		# Images chargées
		for parcStatRendu_1 in listeAff_1:
			self.infosImgProv_1=self.infosImgProv_1+'\n'+parcStatRendu_1
			
		# Images sauvegardées
		for parcStatRendu_2 in listeAff_2:
			self.infosImgProv_2=self.infosImgProv_2+'\n'+parcStatRendu_2
		
		# affichage des infos dans l'onglet
		self.zoneAffichInfosImg.insertPlainText(self.infosImgProv_1+'\n\n'+self.infosImgProv_2+'\n\n'+self.infosImgProv_3+'\n\n')
		self.framInfos.setEnabled(True)
			
		# remise à 0 de la variable provisoire de log
		self.infosImgProv_1=''
		self.infosImgProv_2=''
		self.infosImgProv_3=''
		# ---------------------------------------------------------
		
		# Une fois que la multiplication des images a eu lieu, les 2 
		# boutons (multiplication des images uniquement,
		# multiplication des images et conversion en vidéo) deviennent
		# actifs
		self.boutTransfImgVideo.setEnabled(True)
		self.boutMultImgUniquement.setEnabled(True)

		
	def transformImgEnVideo(self, nomSortie=None, ouvert=1):
		""" Multiplication d'image et conversion en vidéo en une seule commande """
		
		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			if len(toutRepCompo)>0:
				os.remove(toutRepCompo)
		self.mplayer.listeVideos = [] # Réinitialise la liste des vidéos de sorties à visionner par Mplayer.
		# Liste pour affichage de l'image chargée
		listeAff_1=[]

		# Récupération du chemin de la vidéo de destination (à l'exception de l'extension)
		rep = self.baseImg.getRepSource(self.config)
		
		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
		suffix=""
		cheminVideoSorti = EkdSaveDialog(self, os.path.expanduser(rep), suffix, _(u"Sauver"), multiple=True)
		cheminVideoSorti = cheminVideoSorti.getFile()
		
		if not cheminVideoSorti: return
		
		# Récupération de la liste des fichiers chargés
		self.listeImgSource=self.afficheurImgSource.getFiles()
		#print self.listeImgSource # Debug !!!
		EkdPrint(u"%s" % self.listeImgSource) # Debug !!!
		
		# Si l'utilisateur charge plusieurs images, la boîte d'information apparait
		# Si l'utilisateur décide de répondre non, le traitement s'arrête.
		if len(self.listeImgSource) > 1:
			
			reponse = QMessageBox.information(self, 'Message',
			_(u"<p>Vous avez décidé de changer plusieurs images. Sachez que dans ce menu, <b>chaque image sera traitée séparément (!)</b>.</p><p>Si vous avez décidé de transformer directement vos images (préalablement multipliées durant le traitement) en vidéo, vous devez savoir que <b>chaque image produira une vidéo encodée en Motion JPEG (extension .avi)</b></p><p>Etes-vous d'accord pour continuer ?.</p>"), QMessageBox.Yes, QMessageBox.No)
			if reponse == QMessageBox.No:
				return
		
		# Traitement par lot -> boucle sur chaque image
		k=0
		for imPourDupli in self.listeImgSource :
			#print "valeur de k ", k
			EkdPrint(u"valeur de k: %s" % k)
			#print "Valeur de imPourDupli :", imPourDupli
			EkdPrint(u"Valeur de imPourDupli: %s" % imPourDupli)
			# Récup du format sélectionné par l'utilisateur
			i = self.comboReglageExt.currentIndex()
			ext=self.comboReglageExt.itemData(i).toString()
			ext=str(ext).lower()
			#print "Format (extension) d'enregistrement:", ext
			EkdPrint(u"Format (extension) d'enregistrement: %s" % ext)
		
			spin1 = self.spin1.value() # Multiplication, durée en secondes
			spin2 = self.spin2.value() # Multiplication, nombre d'images/sec 
			nbreTotal = spin1 * spin2 # Calcul du nbre exact d'images (après récup des données utilisateur)
		
			# Remplissage de la liste pour images chargées (Info)
			listeAff_1.append(imPourDupli)

			# ------------------------------------------------------------------------
			# Au moment de la conversion des images en vidéo (et après multiplication)
			# FFmpeg doit obligatoirement utiliser des images avec des dimensions
			# (largeur et hauteur) paires (!!!) ... si des images avec des dimensions
			# impaires sont traitées, ça va planter (FFmpeg plantera !). Il faut donc
			# redimensionner l'image chargée par l'utilisateur ... 
			# ------------------------------------------------------------------------
			# Chemin + nom de l'image après redimensionnement
			chemin = self.repTampon+'redim/'+os.path.basename(imPourDupli)
			# Ouverture de l'image chargée pour récup des dimensions
			ouvIm = Image.open(imPourDupli)
			#
			w = ouvIm.size[0] # largeur
			h = ouvIm.size[1] # hauteur
		
			# Si dimension largeur impaire
			if w % 2 == 1 and h % 2 == 0: 
				red = ouvIm.resize((w-1, h)).save(chemin)
				# L'image est redimensionnée et sauvegardée
				imPourDupli = chemin
			
			# Si dimension hauteur impaire
			if h % 2 == 1 and w % 2 == 0: 
				red = ouvIm.resize((w, h-1)).save(chemin)
				# L'image est redimensionnée et sauvegardée
				imPourDupli = chemin
			
			# Si les deux dimensions (largeur et hauteur) impaires
			if w % 2 == 1 and h % 2 == 1: 
				red = ouvIm.resize((w-1, h-1)).save(chemin)
				# L'image est redimensionnée et sauvegardée
				imPourDupli = chemin
			
			# Pour le reste (c'est à dire si l'image a des dimensions paires)
			# on prend directement l'image qui a été chargée par l'utilisateur
			else: pass

			# Remplissage de la liste pour images chargées (Info)
			listeAff_1.append(imPourDupli)

			# Calcul
			for parc in range(nbreTotal):
			
				# On sélectionne le 'Type de format après traitement' à JPEG (.jpg) ou JPEG (.jpeg)
				if i in [0, 1]:
		
					# Ouverture de l'image pour multiplication
					dup = Image.open(imPourDupli)
			
					# Récupération des dimensions après redimensionnement
					# (redimensionnement pour les images avec des 
					# dimensions impaires au départ)
					ww = dup.size[0] # largeur
					hh = dup.size[1] # hauteur
			
					# Application
					dup.save(str(self.repTampon+string.zfill(parc+1, 8)+ext), quality=self.spin3.value())

					# Pas d'affichages des images ds l'interface (libère des ressources)
				
					# --------------------------------------------
					# Affichage de la progression (avec
					# QProgressDialog) ds une fenêtre séparée .
					val_pourc=((parc+1)*100)/nbreTotal

					# Bouton Cancel pour arrêter la progression donc le process
					if (self.progress.wasCanceled()):
						break

					self.progress.setValue(val_pourc)
		
					QApplication.processEvents()
					# --------------------------------------------
			
				# Si on sélectionne les autres formats que JPEG (.jpg) ou JPEG (.jpeg) ...
				else:
				
					# Ouverture de l'image pour multiplication
					dup = Image.open(imPourDupli)
			
					# Récupération des dimensions après redimensionnement
					# (redimensionnement pour les images avec des 
					# dimensions impaires au départ)
					ww = dup.size[0] # largeur
					hh = dup.size[1] # hauteur
			
					# Application
					dup.save(str(self.repTampon+string.zfill(parc+1, 8)+ext))

					# Pas d'affichages des images ds l'interface (libère des ressources)
				
					# --------------------------------------------
					# Affichage de la progression (avec
					# QProgressDialog) ds une fenêtre séparée .
					val_pourc=((parc+1)*100)/nbreTotal

					# Bouton Cancel pour arrêter la progression donc le process
					if (self.progress.wasCanceled()):
						break

					self.progress.setValue(val_pourc)
		
					QApplication.processEvents()
					# --------------------------------------------
		
			# Codec d'encodage vidéo
			id_codec = 'mjpeg'
			# Chemin + extension
			cheminVideoSortif = cheminVideoSorti+'_'+unicode(string.zfill(k+1, self.spin2_ImTrait.value()))+'.avi'
		
			# Affichage des infos sur l'image et la vidéo sortie ------
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte1=_(u" Image chargée")
			texte2=_(u" Vidéo sortie")
			texte3=_(u" Durée de la vidéo en secondes: ")
			a='#'*36
			self.infosImgProv_0='# '+_(u"Traitement n° ")+unicode(k+1)+"\n"
			self.infosImgProv_1=a+'\n#'+texte1+'\n'+a
			self.infosImgProv_2=a+'\n#'+texte2+'\n'+a
			self.infosImgProv_3=a+'\n#'+texte3+str(spin1)+'\n'+a
		
			# Image chargée
			self.infosImgProv_1=self.infosImgProv_1+'\n'+listeAff_1[0]
			
			# Vidéo sauvegardée
			self.infosImgProv_2=self.infosImgProv_2+'\n'+cheminVideoSortif
		
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.insertPlainText(self.infosImgProv_0+self.infosImgProv_1+'\n\n'+self.infosImgProv_2+'\n\n'+self.infosImgProv_3+'\n\n')
			self.framInfos.setEnabled(True)
			
			# remise à 0 de la variable provisoire de log
			self.infosImgProv_1=''
			self.infosImgProv_2=''
			self.infosImgProv_3=''
			# ---------------------------------------------------------
		
			# Sélection de la taille de l'image pour l'encodage en Motion JPEG
			tailleIm = [str(ww), str(hh)]

			# Récupération du chemin
			cheminVideoEntre = self.repTampon+'%08d'+ext
		
			# Drapeau de bon déroulement des opérations
			drapReussi = 1
			if k == len(self.listeImgSource) : o = True
			else : o =False

			# La multiplication d'image est gérée par FFmpeg
			ffmpeg = WidgetFFmpeg(id_codec, cheminVideoEntre, cheminVideoSortif, valeurNum=str(spin2), laisserOuvert=o, tailleIm=tailleIm)
			if debug : 
				#print "DEBUG - Duree en secondes : ", self.spin1.value() 
				EkdPrint(u"DEBUG - Duree en secondes: %s" % self.spin1.value())
			ffmpeg.setVideoLen(self.spin1.value())
			ffmpeg.setWindowTitle(_(u"Conversion des images en vidéo"))
			ffmpeg.exec_()

			if drapReussi:
				self.mplayer.listeVideos.append(cheminVideoSortif)
				self.mplayer.setEnabled(True)
				self.tabwidget.setCurrentIndex(self.indexTabVideoDestin)
			k += 1

		# La liste pour l'affichage des images ds l'interface est
		# vidée pour que les images affichées ne s'amoncellent pas
		# si plusieurs rendus à la suite
		self.listeImgDestin=[]
		self.mplayer.setListeVideo()
		
		# Une fois que la multiplication des images a eu lieu, les 2 
		# boutons (multiplication des images uniquement,
		# multiplication des images et conversion en vidéo) deviennent
		# actifs
		self.boutTransfImgVideo.setEnabled(True)
		self.boutMultImgUniquement.setEnabled(True)
		
		
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""
		
		# Nouvelle fenêtre d'aide
		self.aide = EkdAide(550,690,parent=self)
		self.aide.setText(_(u"<p><b>Vous pouvez ici soit faire la multiplication des images et sans produire de vidéo, soit effectuer la multiplication et par la même occasion créer une vidéo du résultat.</b></p><p>Dans l'onglet <b>'Image(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Pour ce qui est de la simple multiplication des images: dans l'onglet <b>'Réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b>, ensuite faites les réglages de <b>'Multiplication, durée en secondes'</b>, <b>'Multiplication, nombre d'images/sec'</b> et <b>'Type de format après traitement'</b>, ... et cliquez sur le bouton <b>Appliquer et sauver les images</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>. Ce coup-ci pour ce qui est de la multiplication des images et la transformation de ces images en vidéo: toujours dans l'onglet <b>'Réglages'</b> faites les réglages de <b>'Multiplication, durée en secondes'</b>, <b>'Multiplication, nombre d'images/sec'</b> et <b>'Type de format après traitement'</b>, ... et cliquez sur le bouton <b>Appliquer et sauver la vidéo</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Dans le cas du traitement <b>Multiplication des images seulement</b>, si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>'Images après traitement'</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite). Dans le cas de la conversion des images en vidéo vous pouvez visualiser la vidéo produite dans l'onglet <b>Vidéo créé</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les image(s) chargée(s), les image(s) convertie(s) ou la vidéo produite.</p>"))
		self.aide.show()

		
	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'spin1_ImTrait', unicode(self.spin1_ImTrait.value()))
		EkdConfig.set(self.idSection, u'spin2_ImTrait', unicode(self.spin2_ImTrait.value()))
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2.value()))
		EkdConfig.set(self.idSection, u'spin3', unicode(self.spin3.value()))
		EkdConfig.set(self.idSection, u'extension', unicode(self.comboReglageExt.currentIndex()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.spin1_ImTrait.setValue(int(EkdConfig.get(self.idSection, 'spin1_ImTrait')))
		self.spin2_ImTrait.setValue(int(EkdConfig.get(self.idSection, 'spin2_ImTrait')))
		self.spin1.setValue(int(EkdConfig.get(self.idSection, 'spin1')))
		self.spin2.setValue(int(EkdConfig.get(self.idSection, 'spin2')))	
		self.spin3.setValue(int(EkdConfig.get(self.idSection, 'spin3')))	
		self.comboReglageExt.setCurrentIndex(int(EkdConfig.get(self.idSection, 'extension')))
