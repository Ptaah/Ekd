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
# Nouvelle fenêtre d'aide ######
from gui_modules_common.EkdWidgets import EkdAide

# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Image_Transitions_Spirale(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Transitions >> Spirale
	# -----------------------------------
	def __init__(self, statusBar, geometry):
        	QWidget.__init__(self)
		
		# ----------------------------
		# quelques paramètres de base
		# ----------------------------
		self.idSection = u"image_transition_spirale"
		
		# Répertoires tampon
		# Gestion du repertoire tmp avec EkdConfig 
		self.repTampon = EkdConfig.getTempDir() + os.sep + "tampon" + os.sep + "transitions" + os.sep + "spirale"

		self.repTamponRedimSeqA = self.repTampon + os.sep + 'redimSeqA' + os.sep
		self.repTamponRedimSeqB = self.repTampon + os.sep + 'redimSeqB' + os.sep

		self.repTampon_spir_1 = self.repTampon + os.sep + 'spirale_tempo_A' + os.sep
		self.repTampon_pas_spir_1 = self.repTampon + os.sep + 'pas_spirale_tempo_A' + os.sep
		self.repTampon_spir_2 = self.repTampon + os.sep + 'spirale_tempo_B' + os.sep
		self.repTampon_pas_spir_2 = self.repTampon + os.sep + 'pas_spirale_tempo_B' + os.sep
		self.repTampon_Visu = self.repTampon + os.sep + 'voir_le_resultat'

		# Supression de tous les répertoires et fichiers dans /tmp/ekd/tampon/transitions
		if os.path.isdir(os.path.dirname(self.repTampon_spir_1[:-1])) is True: 
			shutil.rmtree(os.path.dirname(self.repTampon_spir_1[:-1]))
		
		#=== Création des répertoires temporaires ===#

		if os.path.isdir(self.repTamponRedimSeqA) is False:
        		os.makedirs(self.repTamponRedimSeqA)

		if os.path.isdir(self.repTamponRedimSeqB) is False:
        		os.makedirs(self.repTamponRedimSeqB)
				
		if os.path.isdir(self.repTampon_spir_1) is False:
        		os.makedirs(self.repTampon_spir_1)

		if os.path.isdir(self.repTampon_spir_1+'redim'+os.sep) is False:
        		os.makedirs(self.repTampon_spir_1+'redim'+os.sep)
		
		if os.path.isdir(self.repTampon_pas_spir_1) is False:
        		os.makedirs(self.repTampon_pas_spir_1)

		if os.path.isdir(self.repTampon_pas_spir_1+'redim'+os.sep) is False:
        		os.makedirs(self.repTampon_pas_spir_1+'redim'+os.sep)
			
		if os.path.isdir(self.repTampon_spir_2) is False:
        		os.makedirs(self.repTampon_spir_2)

		if os.path.isdir(self.repTampon_spir_2+'redim'+os.sep) is False:
        		os.makedirs(self.repTampon_spir_2+'redim'+os.sep)

		if os.path.isdir(self.repTampon_pas_spir_2) is False:
        		os.makedirs(self.repTampon_pas_spir_2)

		if os.path.isdir(self.repTampon_pas_spir_2+'redim'+os.sep) is False:
        		os.makedirs(self.repTampon_pas_spir_2+'redim'+os.sep)
			
		if os.path.isdir(self.repTampon_Visu) is False:
        		os.makedirs(self.repTampon_Visu)
			
		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()

		# Gestion de la configuration via EkdConfig
		# Paramètres de configuration
		self.config = EkdConfig
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry
		
		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)
		
		# Est-ce que des images ont été converties et qu'elles n'ont pas encore été montrées?
		# Marche aussi quand la conversion a été arrêté avant la fin de la 1ère image
		self.conversionImg = 0
		
		# Est-ce qu'une prévisualisation a été appelée?
		self.previsualImg = 0
		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0
		
		# Liste de chemins de fichiers sequence A, sequence B  
		# et du dossier de sauvegarde
		self.listeChemSequenceA=[]
		self.listeChemSequenceB=[]
		self.listeImgDestin = []
		
		# Variable provisoire contenant le texte des infos de chargement et sauvegarde
		self.infosImgProv = ''
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# --------------------------------------------------
		# widgets du haut : titre + bouton de sélection
		# --------------------------------------------------
		
		hbox = QHBoxLayout()
		#hbox.addWidget(titre_du_cadre,1) # étirement: centré
		
		# Ajout du titre de la page et de l'aperçu à la boite verticale
		vbox.addLayout(hbox, 0)
		
		#=== 1er onglet ===#
		self.framReglage=QFrame()
		vboxReglage=QVBoxLayout(self.framReglage)
		
		# Gestion du nombre d'images à traiter
		# Se trouve maintenant directement dans l'onglet Réglages
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
		
		'''
		# -----------------------------------------------------------------------
		# Widgets de réglage contenus dans la page Réglage du TabWidget-- choix 
		# du nombre d'images pour la spirale
		# -----------------------------------------------------------------------
		# boite de spin
		self.choixNbreImagesSpirale=QSpinBox()
		self.choixNbreImagesSpirale.setMinimum(1)
		self.choixNbreImagesSpirale.setMaximum(5000)
		self.choixNbreImagesSpirale.setValue(2)
		
		self.connect(self.choixNbreImagesSpirale,SIGNAL("valueChanged(int)"),self.reglag)
		
		# label d'info du choix par l'utilisateur du nombre d'images qui
		# devront constituer la spirale entre les deux séquences d'images
		txt1, txt2=_(u"Choix du nombre d'images pour la spirale -->"),_(u'Entre 1 et 5000')
		infoImagesSpirale=QLabel('<font color="green">%s</font> <font color="red">%s</font>' %(txt1,txt2), self)
		
		widget=QWidget()
		layout=QGridLayout()
		layout.addWidget(self.choixNbreImagesSpirale, 0, 0)
		layout.addWidget(infoImagesSpirale, 0, 1)
		widget.setLayout(layout)
		'''
		
		# -------------------------------------------------
		# Onglets d'affichage image source et destination
		# -------------------------------------------------

		# Là où s'afficheront les images
		# Séquence A
		self.afficheurImgSourceSeqA=SelectWidget(geometrie = self.mainWindowFrameGeometry)
		# Séquence B
		self.afficheurImgSourceSeqB=SelectWidget(geometrie = self.mainWindowFrameGeometry)

		# Résultat de la transition
		self.afficheurImgDestination=Lecture_VisionImage(statusBar)
		
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
		
		self.indexTabImgSourceSeqA = self.tabwidget.addTab(self.afficheurImgSourceSeqA, _(u'Image(s) séquence A'))
		self.indexTabImgSourceSeqB = self.tabwidget.addTab(self.afficheurImgSourceSeqB, _(u'Image(s) séquence B'))
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
		self.connect(self.boutApPremImg, SIGNAL("clicked()"), self.visu_1ere_img)
		self.boutAppliquer=QPushButton(_(u" Appliquer et sauver"))
		# Appliquer et sauver
		self.boutAppliquer.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		# Bouton inactif au départ
		self.boutAppliquer.setEnabled(False)
		self.connect(self.boutAppliquer, SIGNAL("clicked()"), self.final_moteur)
		
		# Ligne de séparation juste au dessus des boutons
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
		
		# Affichage de la boîte principale
		self.setLayout(vbox)
		
		self.connect(self.tabwidget, SIGNAL("currentChanged(int)"), self.fctTab)
		
		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
		#----------------------------------------------------------------------------------------------------
		
		#self.connect(self.afficheurImgSourceSeqA, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)
		self.connect(self.afficheurImgSourceSeqB, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)
		
		
	def changeValNbreImg_1(self):
		"""Gestion du nombre d'images à traiter"""
		#print "Traitement a partir de l'image (numero):", self.spin1.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2.value())


	def modifBoutonsAction(self, i):
		"On active ou désactive les boutons d'action selon s'il y a des images ou pas dans le widget de sélection"
		self.boutApPremImg.setEnabled(i)
		self.boutAppliquer.setEnabled(i)
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
		
		
	'''	
	def reglag(self):
		self.valChoixFonduPourSpirale=int(self.choixNbreImagesFondu.value())
	'''
	
	
	def stat_dim_img(self):
		"""Calcul statistique des dimensions des images les plus présentes dans les deux lots (seq A et seq B)."""

		# Récupération de la liste des fichiers chargés (séquence A)
		self.listeChemSequenceA=self.afficheurImgSourceSeqA.getFiles()
		
		# Ouverture et mise ds une liste des dimensions des images seq A. List
		# comprehension.
		listePrepaRedimA=[Image.open(aA).size for aA in self.listeChemSequenceA]
		
		# Merci beaucoup à Marc Keller de la liste: python at aful.org de m'avoir 
		# aidé pour cette partie (les 4 lignes en dessous) pour statistiquement 
		# découvrir les dimensions des images les plus présentes dans le lot 
		# chargé par l'utilisateur. J'avais trouvé une solution qui fonctionnait 
		# bien, mais celle de Marc est bien plus efficace car elle utilise un
		# dictionnaire (elle est donc plus rapide).
		dictSeqA={}.fromkeys(listePrepaRedimA, 0)
		for cleA in listePrepaRedimA: dictSeqA[cleA]+=1
		self.lStatDimSeqA=sorted(zip(dictSeqA.itervalues(), dictSeqA.iterkeys()), reverse=1)
		self.dimStatImgA=self.lStatDimSeqA[0][1]

		#print "Toutes les dimensions des images seq A (avec le nbre d'images):", self.lStatDimSeqA
		EkdPrint(u"Toutes les dimensions des images seq A (avec le nbre d'images): %s" % self.lStatDimSeqA)
		#print 'Dimension des images la plus presente dans la sequence A:', self.dimStatImgA
		EkdPrint(u'Dimension des images la plus presente dans la sequence A: %s' % self.dimStatImgA)
		#print "Nombre de tailles d'images différentes dans le lot :", len(self.lStatDimSeqA)
		EkdPrint(u"Nombre de tailles d'images différentes dans le lot: " % len(self.lStatDimSeqA))

		# Récupération de la liste des fichiers chargés (séquence B)
		self.listeChemSequenceB=self.afficheurImgSourceSeqB.getFiles()
		
		# Ouverture et mise ds une liste des dimensions des images seq B. List
		# comprehension.
		listePrepaRedimB=[Image.open(bB).size for bB in self.listeChemSequenceB]
		
		dictSeqB={}.fromkeys(listePrepaRedimB, 0)
		for cleB in listePrepaRedimB: dictSeqB[cleB]+=1
		self.lStatDimSeqB=sorted(zip(dictSeqB.itervalues(), dictSeqB.iterkeys()), reverse=1)
		self.dimStatImgB=self.lStatDimSeqB[0][1]

		#print "Toutes les dimensions des images seq B (avec le nbre d'images):", self.lStatDimSeqB
		EkdPrint(u"Toutes les dimensions des images seq B (avec le nbre d'images): %s" % self.lStatDimSeqB)
		#print 'Dimension des images la plus presente dans la sequence B:', self.dimStatImgB
		EkdPrint(u'Dimension des images la plus presente dans la sequence B: %s' % self.dimStatImgB)
		#print "Nombre de tailles d'images différentes dans le lot :", len(self.lStatDimSeqB)
		EkdPrint(u"Nombre de tailles d'images différentes dans le lot: %s" % len(self.lStatDimSeqB))
		
		# On libere la memoire
		del listePrepaRedimA, dictSeqA, listePrepaRedimB, dictSeqB
	
	
	def redim_img(self):
		"""Si l'utilisateur charge des images avec des tailles complètement différentes --> les images de la séquence A et B sont redimensionnées"""

		self.stat_dim_img()

		# ------------------------------------------------
		# Quand l'utilisateur charge des images de taille complètement différentes
		# dans la séquence A, elles doivent être redimensionnées pour la suite du traitement
		# ------------------------------------------------
		if len(self.lStatDimSeqA) > 1:

			listeImgRedimA=[]
			index_Redim_seqA=0
			for chemOrig1 in self.listeChemSequenceA:
				ouvrirPourRedimA=Image.open(chemOrig1)
				ssRedim1=ouvrirPourRedimA.resize(self.dimStatImgA, Image.ANTIALIAS)
				chemTempRedimSeqA = self.repTamponRedimSeqA+os.path.basename(chemOrig1)
				ssRedim1.save(chemTempRedimSeqA)
				self.listeChemSequenceA[index_Redim_seqA] = chemTempRedimSeqA
				# Remplissage de la liste provisoire
				listeImgRedimA.append(chemTempRedimSeqA)
				index_Redim_seqA += 1

			# On vide la liste
			self.listeChemSequenceA = []

			# Renommage par ordre alpha-numérique des éléments de la liste et enregistrement dans le rep. tampon dévolu à cela
			self.listeChemSequenceA = [os.rename(listeImgRedimA[parc_1], self.repTamponRedimSeqA+'image_'+string.zfill(parc_1+1, 10)+'.jpg') for parc_1 in range(len(listeImgRedimA))]

			# On va chercher les images dans le rep. tampon dévolu, mais comme glob utilise
			# un dictionnaire, les éléments de la liste se classent de façon aléatoire
			self.listeChemSequenceA = glob.glob(self.repTamponRedimSeqA+os.sep+'*.*')
			# On remet en ordre la liste (et comme nous avons auparavant classé
			# les éléments par ordre alpha-numérique ... pas de problème)
			self.listeChemSequenceA.sort()

		# ------------------------------------------------
		# Quand l'utilisateur charge des images de taille complètement différentes
		# dans la séquence B, elles doivent être redimensionnées pour la suite du traitement
		# ------------------------------------------------
		if len(self.lStatDimSeqB) > 1:

			listeImgRedimB=[]
			index_Redim_seqB=0
			for chemOrig2 in self.listeChemSequenceB:
				ouvrirPourRedimB=Image.open(chemOrig2)
				ssRedim2=ouvrirPourRedimB.resize(self.dimStatImgB, Image.ANTIALIAS)
				chemTempRedimSeqB = self.repTamponRedimSeqB+os.path.basename(chemOrig2)
				ssRedim2.save(chemTempRedimSeqB)
				self.listeChemSequenceB[index_Redim_seqB] = chemTempRedimSeqB
				# Remplissage de la liste provisoire
				listeImgRedimB.append(chemTempRedimSeqB)
				index_Redim_seqB += 1

			# On vide la liste
			self.listeChemSequenceB = []

			# Renommage par ordre alpha-numérique des éléments de la liste et enregistrement dans le rep. tampon dévolu à cela
			self.listeChemSequenceB = [os.rename(listeImgRedimB[parc_2], self.repTamponRedimSeqB+'image_'+string.zfill(parc_2+1, 10)+'.jpg') for parc_2 in range(len(listeImgRedimB))]

			# On va chercher les images dans le rep. tampon dévolu, mais comme glob utilise
			# un dictionnaire, les éléments de la liste se classent de façon aléatoire
			self.listeChemSequenceB = glob.glob(self.repTamponRedimSeqB+os.sep+'*.*')
			# On remet en ordre la liste (et comme nous avons auparavant classé
			# les éléments par ordre alpha-numérique ... pas de problème)
			self.listeChemSequenceB.sort()
			
		# Les images de tailles différentes à la plus répandue sont redimensionnées
		# dans un répertoire temporaire.
		# Les images redimensionnées voient leur chemin modifié dans la liste des
		# chemins des images sources. Les autres chemins ne changent pas.
		# --------------------------------------------------------------------------
		# Après coup:
		# -----------
		# Les images de la séquence A ont (maintenant) la même taille entre elles.
		# Les images de la séquence B ont (maintenant) la même taille entre elles.
		# Les images de la séquence A n'ont pas nécessairement la taille des images
		# de la séquence B.
		# --------------------------------------------------------------------------
		# On prend pour référence la taille des images de la séquence A:
		# ** Le redimensionnement dans la séquence A se fait à la taille des images
		# la plus répandue dans la séquence A (!)
		# ** Le redimensionnement dans la séquence B se fait à la taille des images
		# la plus répandue dans la séquence A (!!! très important --> comme ça les 
		# images dans la seq. A et dans la seq. B on toutes la même taille !)
		
		index_1=0
		for chemImg1 in self.listeChemSequenceA:
			ouvrirImagA=Image.open(chemImg1)
			if ouvrirImagA.size!=self.dimStatImgA:
				pass
			sRedim1=ouvrirImagA.resize(self.dimStatImgA, Image.ANTIALIAS)
			#
			chemSortie_1 = self.repTampon_spir_1+'redim'+os.sep+os.path.basename(chemImg1)
			#
			sRedim1.save(chemSortie_1)
			self.listeChemSequenceA[index_1] = chemSortie_1
			index_1 += 1
				
		index_2=0
		for chemImg2 in self.listeChemSequenceB:
			ouvrirImagB=Image.open(chemImg2)
			if ouvrirImagB.size!=self.dimStatImgB:
				pass
			sRedim2=ouvrirImagB.resize(self.dimStatImgA, Image.ANTIALIAS)
			#
			chemSortie_2 = self.repTampon_spir_2+'redim'+os.sep+os.path.basename(chemImg2)
			#
			sRedim2.save(chemSortie_2)
			self.listeChemSequenceB[index_2] = chemSortie_2
			index_2 += 1
			
		# On libere la memoire
		#del index_1, chemImg1, ouvrirImagA, sRedim1, chemSortie_1, index_2, chemImg2, ouvrirImagB, sRedim2, chemSortie_2
			
				
	def etape_pre_preparatoire(self):
		
		# Récupération de la liste des fichiers chargés (séquence A)
		self.listeChemSequenceA=self.afficheurImgSourceSeqA.getFiles()
		# Récupération de la liste des fichiers chargés (séquence B)
		self.listeChemSequenceB=self.afficheurImgSourceSeqB.getFiles()
		
		# On implémente les chemins des fichiers dans une variable
		# pour préparer l'affichage des infos pour les images 
		# chargées de la séquence A
		textSeqA=_(u"Image(s) séquence A chargée(s)")
		a1='#'*36
		self.infosImgProvAffSeqA = a1 + '\n# ' + textSeqA + '\n' + a1
			
		for cheminA in self.listeChemSequenceA:
			self.infosImgProvAffSeqA=self.infosImgProvAffSeqA+'\n'+cheminA
		self.infosImgProvAffSeqA = self.infosImgProvAffSeqA + '\n\n'
		
		# Pareil pour les images chargées de la séquence B ...
		textSeqB=_(u"Image(s) séquence B chargée(s)")
		a2='#'*36
		self.infosImgProvAffSeqB = a2 + '\n# ' + textSeqB + '\n' + a2
			
		for cheminB in self.listeChemSequenceB:
			self.infosImgProvAffSeqB=self.infosImgProvAffSeqB+'\n'+cheminB
		self.infosImgProvAffSeqB = self.infosImgProvAffSeqB + '\n\n'
		
		# On libere la memoire
		del textSeqA, a1, cheminA, textSeqB, a2, cheminB
	
	
	def etape_preparatoire(self):
		"""Etape préparatoire avant l'application de la transition spirale"""
		
		# Appel de la fonction d'affichage des images chargées 
		# des séquences A et B pour l'onglet Infos
		self.etape_pre_preparatoire()
			
		# Appel de la fonction pour le redimensionnement
		self.stat_dim_img()
			
		# Si la largeur des images la plus presente dans la sequence A est égale à la largeur des 
		# images la plus presente dans la sequence B et si la hauteur des images la plus presente 
		# dans la sequence A est égale à la hauteur des images la plus presente dans la sequence B
		# ... et si on n'a qu'un lot d'images dont les dimensions sont strictement identiques pour
		# la seq A et la seq B ...rien ne se passe ...
		if (self.dimStatImgA[0]==self.dimStatImgB[0] and self.dimStatImgA[1]==self.dimStatImgB[1]) and (len(self.lStatDimSeqA)==1 and len(self.lStatDimSeqB)==1):

			pass

		# Autrement les images sont redimensionnées ...
		else:
			reply = QMessageBox.warning(self, 'Message',
			_(u"Vos images ne sont pas toutes de la même taille. Ceci dit la création de la transition fondu enchaîné peut quand même avoir lieu. Les images vont être redimensionnées à la résolution (statistiquement parlant) la plus présente dans vos images. Les opérations supplémentaires allongeront le processus. Voulez-vous quand même continuer ?."), QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.No:
				return False
			# Redimensionnement des images
			self.redim_img()
			
		# Application (sans réglage possible de la part de l'utilisateur ...
		# pour éviter des erreurs du genre: l'utilisateur règle le taux d'images
		# comprises dans la spirale plus élevé que le nbre d'images chargées pour
		# la séquence A ou B) du taux d'images incluses dans la spirale
		mini=min(len(self.listeChemSequenceA), len(self.listeChemSequenceB))
		
		if mini==1: 
			self.valChoixFonduPourSpirale=1
			self.valChoixEnroulement=1
		elif 1<mini<=5: 
			self.valChoixFonduPourSpirale=2
			self.valChoixEnroulement=2
		elif 5<mini<=10: 
			self.valChoixFonduPourSpirale=4
			self.valChoixEnroulement=4
		elif 10<mini<=25: 
			self.valChoixFonduPourSpirale=8
			self.valChoixEnroulement=8
		elif 25<mini<=50: 
			self.valChoixFonduPourSpirale=13
			self.valChoixEnroulement=13
		elif 50<mini<=100: 
			self.valChoixFonduPourSpirale=20
			self.valChoixEnroulement=20
		elif 100<mini<=250: 
			self.valChoixFonduPourSpirale=27
			self.valChoixEnroulement=27
		elif 250<mini<=1500: 
			self.valChoixFonduPourSpirale=52
			self.valChoixEnroulement=52
		elif mini>1500: 
			self.valChoixFonduPourSpirale=52
			self.valChoixEnroulement=52
		
		#print "Nombre d'image(s) incluses dans la spirale: entre ", str(self.valChoixEnroulement-2), ' et ', str(self.valChoixEnroulement)
		EkdPrint(u"Nombre d'image(s) incluses dans la spirale: entre %s et %s" % (self.valChoixEnroulement-2, self.valChoixEnroulement))

		#self.valChoixSpirale=int(self.choixNbreImagesFondu.value())

		# -------------------------------------------------------------------------
		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
		#--------------------------------------------------------------------------

		# Utilisation de la nouvelle boîte de dialogue de sauvegarde
		suffix=""
                self.chemDossierSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.chemDossierSauv = self.chemDossierSauv.getFile()
		
		if not self.chemDossierSauv: return False
		
		#print 'Chemin+nom de sauvegarde:', self.chemDossierSauv
		
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
		textSeqFinal=_(u"Résultat Spirale")
		a='#'*36
		self.infosImgProv = self.infosImgProv + a + '\n# ' + textSeqFinal + '\n' + a
		
		
		# -------- TRAITEMENT DE LA SEQUENCE A ----- IMAGES POUR LA SPIRALE -
		# Recup du chemin et nom de la 1ere image chargee sequence A
		chNomChargSeqA=self.listeChemSequenceA[0]
	
		# Recup de l'extension des images sequence A chargees par l'utilisateur
		extImSeqA=string.split(chNomChargSeqA, '.')[-1:]	
	
		# Mise dans l'ordre croissant des images
		self.listeChemSequenceA.sort()
		# Inversion de l'ordre (ordre decroissant)
		self.listeChemSequenceA.reverse()
	
		# On ne selectionne (ds cette liste) que les images qui vont subir
		# la spirale et ce pour les images de la sequence A
		self.imgCoupeesSeqA=self.listeChemSequenceA[0:self.valChoixEnroulement]
		# On remet les images de la liste self.imgCoupeesSeqA ds l'orde croissant
		self.imgCoupeesSeqA.sort()
		
		####### Le module sets a été remplacé par cette syntaxe ##########################
		####### Attention ca risque de ne pas fonctionner sous Python 3.0 ################
		# --------------------------------------------------------------------------------
		# Sous Python 3.0:
		# a = {0, 1, 2, 3, 4}
		# b = {1, 127, 4, 7, 12}
		# c = a.symmetric_difference(b)
		# d = [p for p in c]
		# d.sort()
		# print(d)
		# [0, 2, 3, 7, 12, 127]
		# --------------------------------------------------------------------------------
		# On fait ressortir les elements differents entre les images sequence A 
		# selectionnes par l'utilisateur (seq A spirale) et les images sequence A  
		# qui ont ete chargees par l'utilisateur
		interChargUtilisSeqA=set(self.imgCoupeesSeqA) 
		interExisteSeqA=set(self.listeChemSequenceA) 
		interInterSeqA=interChargUtilisSeqA.symmetric_difference(interExisteSeqA)
		listeInterInterSeqA=[t1 for t1 in interInterSeqA]
		listeInterInterSeqA.sort()
		##################################################################################
		
			
		# Creation liste vide pour images spirale sequence A
		listeChemFichSeqA_SPI_Temp=[]
		
		# Copie des images de la sequence A qui doivent faire partie de la spirale 
		# dans le rep. /tmp/ekd/tampon/transitions/spirale/spirale_tempo_A
		for parcSeqA_Temp in self.imgCoupeesSeqA:
			shutil.copy("".join(parcSeqA_Temp), os.path.dirname(self.repTampon_spir_1))
			# Remplissage de la liste .
			listeChemFichSeqA_SPI_Temp.append(parcSeqA_Temp)
		
		# Application de la spirale (a proprement parler) sur les images . Boucle pour
		# la commande ImageMagick . Le depart de la spirale est fixee a 50 spirale 
		# naissante), la fin a 2000 (spirale bien enroulee) et le pas se fait par la
		# valeur croissante 2000 divise par la valeur self.valChoixFonduPourSpirale 
		# choisie par l'utilisateur. Dans la sequence A la spirale est croissante, c'est 
		# a dire qu'elle s'enroule ...
		
		# Compatibilité entre linux et windows
		# Dans la version windows ce n'est pas traité par un QProcess (comme sous
		# Linux) mais directement avec os.system (car le QProcess avec la commande
		# convert d'ImageMagick génère une erreur)
			
		# Uniquement pour Linux et MacOSX
		if os.name in ['posix', 'mac']:
			process = QProcess(self)
		
		for yy1_SPI, io1_SPI in zip(range(len(listeChemFichSeqA_SPI_Temp)*2), range(self.valChoixEnroulement, 2000, 2000/self.valChoixEnroulement)):
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				# Commande ImageMagick dans la boucle .
				process.start('convert '+listeChemFichSeqA_SPI_Temp[yy1_SPI]+' -swirl '+str(io1_SPI)+' '+listeChemFichSeqA_SPI_Temp[yy1_SPI])

				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				os.system('convert '+"\""+listeChemFichSeqA_SPI_Temp[yy1_SPI]+"\""+' -swirl '+str(io1_SPI)+' '+"\""+listeChemFichSeqA_SPI_Temp[yy1_SPI]+"\"")
		# -------------------------------------------------------------------------
	
		# ----- TRAITEMENT DE LA SEQUENCE A --- IMAGES AUTRES QUE POUR LA SPIRALE -
		
		# Copie des images de la sequence A qui ne servent pas à la spirale 
		# dans le rep. /tmp/ekd/tampon/transitions/spirale/pas_spirale_tempo_A
		for parcSeqA_PasSPI in listeInterInterSeqA:
			shutil.copy("".join(parcSeqA_PasSPI), os.path.dirname(self.repTampon_pas_spir_1[:-1]))
		
		# Chemin complet vers le rep. /tmp/ekd/tampon/transitions/spirale/pas_spirale_tempo_A
		chemRepSauvSeqA_PasSPI=os.path.dirname(self.repTampon_pas_spir_1[:-1])
	
		# Recup du chemin+nom des images sequence A copiees ds le rep. pas_spirale_tempo_A
		rChRepSauvSeqA_PasSPI=glob.glob(chemRepSauvSeqA_PasSPI+os.sep+'*.'+"".join(extImSeqA))
		rChRepSauvSeqA_PasSPI.sort()
	
		# Pour le renommage des images selectionnees pour la spirale, Exemple:
		# Affiche '000039' ... '000058' (si choix : 20 img. pour la spirale)
		# List comprehension. Je sais c'est moins lisible, mais c'est plus rapide !.
		self.liste_1_RISPSPI=[string.zfill(int(parcRISPSPI)+len(listeInterInterSeqA)+1, 6) for parcRISPSPI in range(len(self.imgCoupeesSeqA))]
			
		# Pour le renommage des images se trouvant juste avant celles pour la spirale
		# Les images copiees ds le rep. pas_spirale_tempo_A vont ensuite etre renommees et 
		# (recopiees) --> à la fin, ds le rep. de sauvegarde choisi par l'utilisateur.
		# Exemple : Affichage '000001' ... '000038'.
		liste_2_RITJACPFseqA=[string.zfill(parcRITJACPF_seqA+1, 6) for parcRITJACPF_seqA in range(len(listeInterInterSeqA))]
		
		# Renommage des images sequence A de la liste liste_2_RITJACPFseqA. Ces
		# images sont renommees en fonction de la numerotation des images qui n'ont
		# pas ete selectionnes par le reglage des images faisant partie de la spirale.

		# listeSeqAaff aussi utilisé dans la fonction final_moteur
		self.listeSeqAaff=[]
		
		aSeqA=0
		while aSeqA < len(rChRepSauvSeqA_PasSPI):
			os.rename(rChRepSauvSeqA_PasSPI[aSeqA], os.path.dirname(self.repTampon_pas_spir_1)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(liste_2_RITJACPFseqA[aSeqA])+'.jpg')
			
			# Copie des fichiers ne servant pas pour le fondu dans le rep. de sauvegarde
			shutil.copy(self.repTampon_pas_spir_1+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(liste_2_RITJACPFseqA[aSeqA])+'.jpg', os.path.dirname(self.chemDossierSauv))
			
			# Liste Séquence B Affichage --> affichage des infos
			self.listeSeqAaff.append(os.path.dirname(self.chemDossierSauv)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(liste_2_RITJACPFseqA[aSeqA])+'.jpg')
			
			aSeqA=aSeqA+1
		# ---------------------------------------------------------------------------
	
	
		# -------- TRAITEMENT DE LA SEQUENCE B ----- IMAGES POUR LA SPIRALE -
		# Recup du chemin et nom de la 1ere image chargee sequence B
		chNomChargSeqB=self.listeChemSequenceB[0]
	
		# Recup de l'extension des images sequence B chargees par l'utilisateur
		extImSeqB=string.split(chNomChargSeqB, '.')[-1:]	
	
		# Mise dans l'ordre croissant des images
		self.listeChemSequenceB.sort()
	
		# On ne selectionne (ds cette liste) que les images qui vont subir
		# la spirale et ce pour les images de la sequence B .
		self.imgCoupeesSeqB=self.listeChemSequenceB[0:self.valChoixEnroulement]
		
		####### Le module sets a été remplacé par cette syntaxe ##########################
		####### Attention ca risque de ne pas fonctionner sous Python 3.0 ################
		# --------------------------------------------------------------------------------
		# Sous Python 3.0:
		# a = {0, 1, 2, 3, 4}
		# b = {1, 127, 4, 7, 12}
		# c = a.symmetric_difference(b)
		# d = [p for p in c]
		# d.sort()
		# print(d)
		# [0, 2, 3, 7, 12, 127]
		# --------------------------------------------------------------------------------
		# On fait ressortir les elements differents entre les images sequence B 
		# selectionnes par l'utilisateur (seq B spirale) et les images sequence B  
		# qui ont ete chargees par l'utilisateur.
		interChargUtilisSeqB=set(self.imgCoupeesSeqB) 
		interExisteSeqB=set(self.listeChemSequenceB) 
		interInterSeqB=interChargUtilisSeqB.symmetric_difference(interExisteSeqB)
		listeInterInterSeqB=[t2 for t2 in interInterSeqB]
		listeInterInterSeqB.sort()
		##################################################################################
		
			
		# Creation liste vide pour images spirale sequence B
		listeChemFichSeqB_SPI_Temp=[]
		
		# Copie des images de la sequence A qui doivent faire partie de la spirale 
		# dans le rep. /tmp/ekd/tampon/transitions/spirale/spirale_tempo_B
		for parcSeqB_Temp in self.imgCoupeesSeqB:
			copRepSeqB_Temp=shutil.copy("".join(parcSeqB_Temp), os.path.dirname(self.repTampon_spir_2))
			# Remplissage de la liste .
			listeChemFichSeqB_SPI_Temp.append(parcSeqB_Temp)
		
		# Application de la spirale (a proprement parler) sur les images. Boucle pour
		# la commande ImageMagick . Le depart de la spirale est fixee a 50 spirale 
		# naissante), la fin a 2000 (spirale bien enroulee) et le pas se fait par la
		# valeur croissante 2000 divise par la valeur self.valChoixFonduPourSpirale 
		# choisie par l'utilisateur. Dans la sequence A la spirale est croissante, 
		# c'est a dire qu'elle s'enroule ...
		
		# Compatibilité entre linux et windows
		# Dans la version windows ce n'est pas traité par un QProcess (comme sous
		# Linux) mais directement avec os.system (car le QProcess avec la commande
		# convert d'ImageMagick génère une erreur)
		
		for yy2_SPI, io2_SPI in zip(range(len(listeChemFichSeqB_SPI_Temp)*2), range(2000, self.valChoixEnroulement, -2000/self.valChoixEnroulement)):
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				# Commande ImageMagick dans la boucle .
				process.start('convert '+listeChemFichSeqB_SPI_Temp[yy2_SPI]+' -swirl '+str(io2_SPI)+' '+listeChemFichSeqB_SPI_Temp[yy2_SPI])
			
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				os.system('convert '+"\""+listeChemFichSeqB_SPI_Temp[yy2_SPI]+"\""+' -swirl '+str(io2_SPI)+' '+"\""+listeChemFichSeqB_SPI_Temp[yy2_SPI]+"\"")
		# ---------------------------------------------------------------------------
		
		# ----- TRAITEMENT DE LA SEQUENCE B --- IMAGES AUTRES QUE POUR LA SPIRALE -
		# Creation d'un repertoire tampon pour accueillir les images ne servant pas
		# à la spirale, mais ces images sont tres utiles pour le montage final
		# ==> images_spirale_seq_A_et_B_melangees + images_seq_B_pas_spirale .
		
		# Copie des images de la sequence B qui ne servent pas à la spirale 
		# dans le rep. /tmp/ekd/tampon/transitions/spirale/pas_spirale_tempo_B
		for parcSeqB_PasSPI in listeInterInterSeqB:
			shutil.copy("".join(parcSeqB_PasSPI), os.path.dirname(self.repTampon_pas_spir_2[:-1]))
		
		# Chemin complet vers le rep. /tmp/ekd/tampon/transitions/spirale/pas_spirale_tempo_B
		chemRepSauvSeqB_PasSPI=os.path.dirname(self.repTampon_pas_spir_2[:-1])
	
		# Recup du chemin+nom des images sequence A copiees ds le rep. pas_spirale_tempo_B
		rChRepSauvSeqB_PasSPI=glob.glob(chemRepSauvSeqB_PasSPI+os.sep+'*.'+"".join(extImSeqB))
		rChRepSauvSeqB_PasSPI.sort()
	
		# Pour le renommage des images selectionnees pour la spirale
		##### Exemple : Affichage '000059' ... '000088'
		liste_2_RITJACPFseqB=[string.zfill(parcRITJACPF_seqB+len(self.imgCoupeesSeqB)+len(listeInterInterSeqA)+1, 6) for parcRITJACPF_seqB in range(len(listeInterInterSeqB))]
		
		# Renommage des images sequence B de la liste liste_2_RITJACPFseqB .
		# Attention : le renommage s'effectue avec la numerotation suivante ====> 
		# indice parcRITJACPF_seqB sequence B (c'est a dire 0, 1, 2, 3, 4, 5, 6, 7
		# ...) + nbre d'images selectionnees pour la decoupe sequence B + nbre
		# d'images n'ayant pas ete selectionnees pour la spirale de la séquence A (ce
		# coup-ci ce sont des images de la sequence A !!! et pas sequence B) + 1.
		self.listeSeqBaff=[]
		
		aSeqB=0
		while aSeqB < len(rChRepSauvSeqB_PasSPI):
			os.rename(rChRepSauvSeqB_PasSPI[aSeqB], os.path.dirname(self.repTampon_pas_spir_2)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(liste_2_RITJACPFseqB[aSeqB])+'.jpg')
			
			# Copie des fichiers ne servant pas pour le fondu dans le rep. de sauvegarde
			shutil.copy(self.repTampon_pas_spir_2+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(liste_2_RITJACPFseqB[aSeqB])+'.jpg', os.path.dirname(self.chemDossierSauv))
			
			# Liste Séquence B Affichage --> affichage des infos
			self.listeSeqBaff.append(os.path.dirname(self.chemDossierSauv)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(liste_2_RITJACPFseqB[aSeqB])+'.jpg')
			
			aSeqB=aSeqB+1
		# ---------------------------------------------------------------------------
		return True
		
		# On libere la memoire
		del mini, textSeqFinal, a, chNomChargSeqA, extImSeqA, interChargUtilisSeqA, interExisteSeqA, interInterSeqA, listeInterInterSeqA, t1,parcSeqA_Temp, parcSeqA_PasSPI, chemRepSauvSeqA_PasSPI, rChRepSauvSeqA_PasSPI, parcRISPSPI, liste_2_RITJACPFseqA, parcRITJACPF_seqA, aSeqA, chNomChargSeqB, extImSeqB, interChargUtilisSeqB, interExisteSeqB, interInterSeqB, listeInterInterSeqB, t2, parcSeqB_Temp, copRepSeqB_Temp, parcSeqB_PasSPI, chemRepSauvSeqB_PasSPI, rChRepSauvSeqB_PasSPI, liste_2_RITJACPFseqB, parcRITJACPF_seqB, aSeqB
		
		
	def visu_1ere_img(self):
		"""Fonction pour faire une simulation de rendu et ce à partir du bouton Voir le résultat"""
		
		try:
		
			# Attention après un 1er process (application d'une spirale,
			# le répertoire tampon pour la visualisation du fondu peut avoir
			# été eliminé ... et si on veut 'Voir le résultat' et bien le chemin
			# n'existera pas, il faut donc le recréer ... donc création du rep. 
			# tampon pour la visualisation de la spirale
			if os.path.isdir(self.repTampon_Visu) is False: os.makedirs(self.repTampon_Visu)

			# Récupération de la liste des fichiers chargés (séquence A)
			self.listeChemSequenceA=self.afficheurImgSourceSeqA.getFiles()
		
			# Récupération de la liste des fichiers chargés (séquence B)
			self.listeChemSequenceB=self.afficheurImgSourceSeqB.getFiles()
		
			listeResultatChem=[]
			nbreElem_1=len(self.listeChemSequenceA)
			
			# Ouverture des images pour visualisation.
			imgOpSPI1=Image.open("".join(self.listeChemSequenceA[nbreElem_1-1]))
			imgOpSPI2=Image.open("".join(self.listeChemSequenceB[0]))
		
			chemSortie = self.repTampon_Visu+os.sep+'spirale_visu.jpg'
		
			# Si les images de la seq. A et de la seq. B ont une taille différente ...
			if imgOpSPI1.size!=imgOpSPI2.size:
				# Redimensionnement de la dernière iamge de la seq. A
				# à la taille de la première image de la seq. B
				sRedim=imgOpSPI1.resize(imgOpSPI2.size, Image.ANTIALIAS)
				sRedim.save(chemSortie)
			
				# Ré-ouverture
				imgOpSPI1=Image.open(self.repTampon_Visu+os.sep+'spirale_visu.jpg')
			
				# Application de blend (superposition et transparence) pour affichage
				# et remplissage de la liste
				imgSPI=Image.blend(imgOpSPI1, imgOpSPI2, 0.5)
				imgSPI.save(chemSortie)
				# Commande ImageMagick, application de la spirale. Valeur à 680.
				os.system('convert '+"\""+chemSortie+"\""+' -swirl 680 '+"\""+chemSortie+"\"")
				listeResultatChem.append(chemSortie)
			
			# Si les images de la seq. A et de la seq. B ont toutes la même taille ...
			else:
				# Autrement si les images de la seq. A et de la seq. B ont la même taille ...
				# et remplissage de la liste
				imgSPI=Image.blend(imgOpSPI1, imgOpSPI2, 0.5)
				imgSPI.save(chemSortie)
				# Commande ImageMagick, application de la spirale. Valeur à 680.
				os.system('convert '+"\""+chemSortie+"\""+' -swirl 680 '+"\""+chemSortie+"\"")
				listeResultatChem.append(chemSortie)
			
			# Affichage de l'image temporaire 
			# Ouverture d'une boite de dialogue affichant l'aperçu.
			#
			# Affichage par le bouton Voir le résultat
			visio = VisionneurEvolue(listeResultatChem[0])
			visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
			visio.exec_()
		
			return 0
			
			# On libere la memoire
			del listeResultatChem, nbreElem_1, imgOpSPI1, imgOpSPI2, chemSortie, sRedim, imgSPI, visio
			
		except:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"<p><b>Première situation d'erreur:</b> vous n'avez pas chargé d'image(s) (bouton <b>Ajouter</b>) dans l'onglet <b>Image(s) séquence A</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) séquence A</b>, que dans <b>Image(s) séquence B</b>.</p><p><b>Deuxième situation d'erreur:</b> une (ou plusieurs) des images que vous avez chargé n'a pas le bon mode, en effet, pour la création de transitions, EKD ne peut pas travailler avec les images dont le mode est <b>L</b> (il s'agit d'images en niveaux de gris), <b>P</b> (images GIF) ou <b>RGBA</b> (images avec un canal alpha, c'est à dire des images avec un canal de transparence) . Vérifiez le mode de chacune de vos images (et ce dans les onglets <b>Image(s) séquence A</b> et <b>Image(s) séquence B</b>), pour ce faire sélectionnez une image et cliquez sur le bouton <b>Infos</b> (dans la fenêtre qui s'ouvre, chacune des images fautives devrait avoir soit <b>L</b>, soit <b>P</b> ou soit <b>RGBA</b> indiqué en face du champ <b>Mode</b>). Eliminez chacune de ces images (par le bouton <b>Retirer</b>) et relancez le traitement (par les boutons <b>Voir le résultat</b> ou <b>Appliquer et sauver</b>).</p>"))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()
			return

		
	def final_moteur(self):
		"""appliquer la transition spirale"""
			
		try:
				
			# FINAL MOTEUR (APPLICATION DE LA SPIRALE)
			if not self.etape_preparatoire(): return
		
			listeResultatChem=[]
		
			nbreElem=len(self.imgCoupeesSeqA)
		
			for parc in range(nbreElem):
			
				# Ouverture des images en cours dans la boucle .
				imgOpSPI1=Image.open("".join(self.imgCoupeesSeqA[parc]))
				imgOpSPI2=Image.open("".join(self.imgCoupeesSeqB[parc]))
			
				# Calcul du taux de blend (taux de melange de l'image 
				# sequence A et sequence B en cours).
				calcCHANGblend=round(float(parc+1)/len(self.imgCoupeesSeqA), 8)
		
				# Application de la spirale (en fait le fondu) et sauvegarde (avec
				# numerotation des images).
				imgSPI=Image.blend(imgOpSPI1, imgOpSPI2, calcCHANGblend)
				imgSPI.save(os.path.dirname(self.chemDossierSauv)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(self.liste_1_RISPSPI[parc])+'.jpg')
				listeResultatChem.append(os.path.dirname(self.chemDossierSauv)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+"".join(self.liste_1_RISPSPI[parc])+'.jpg')
		
				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée .
				val_pourc=((parc+1)*100)/nbreElem
	
				# Bouton Cancel pour arrêter la progression donc le process
				if (self.progress.wasCanceled()):
					break
	
				self.progress.setValue(val_pourc)
			
				QApplication.processEvents()
				# --------------------------------------------
				
			# Concaténation des 3 listes (avant superposition, images superposées 
			# et après superposition) en une seule liste.
			conc3L=list(self.listeSeqAaff+listeResultatChem+self.listeSeqBaff)
			
			lRenomAff=[]

			for parcC3L in range(len(conc3L)):
				# Renommage des fichiers en tenant compte du Traitement a partir de l'image 
				# (numero) et du Nombre de chiffres apres le nom de l'image
				os.rename(conc3L[parcC3L], os.path.dirname(self.chemDossierSauv)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+string.zfill(parcC3L+self.spin1.value(), self.spin2.value())+'.jpg')
				lRenomAff.append(os.path.dirname(self.chemDossierSauv)+os.sep+os.path.basename(self.chemDossierSauv)+'_'+string.zfill(parcC3L+self.spin1.value(), self.spin2.value())+'.jpg')
				
				# Ajout des images dans la liste self.listeImgDestin. Cette liste
				# sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(lRenomAff[parcC3L])
				
				# --------------------------------------------
				# Barre de progression très utile si de très
				# nombreuses images à renommer.
				
				nbreElemRenom=len(lRenomAff)
				
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée .
				val_pourc_renom=((parcC3L+1)*100)/nbreElemRenom
	
				# Bouton Cancel pour arrêter la progression donc le process
				if (self.progress.wasCanceled()):
					break
	
				self.progress.setValue(val_pourc_renom)
			
				QApplication.processEvents()
				# --------------------------------------------

			# Affichage des images après traitement
			#
			# Changement d'onglet et fonctions associées
			self.conversionImg = 1
			self.metaFctTab(self.indexTabImgDestin)

			# La liste pour l'affichage des images ds l'interface est
			# vidée pour que les images affichées ne s'amoncellent pas
			# si plusieurs rendus à la suite
			self.listeImgDestin=[]
			
			# Affichage des infos de sauvegarde des images de la transition spirale
			for chemin in lRenomAff:
				self.infosImgProv=self.infosImgProv+'\n'+chemin
			self.infosImgProv = self.infosImgProv + '\n\n'
				
			# Affichage des infos du nbre d'images ayant servi dans le fondu
			textNbre=_(u"Nombre d'image(s) incluses dans la spirale: entre ")
			a_nbre='#'*46
			self.infosImgProv = self.infosImgProvAffSeqA+self.infosImgProvAffSeqB+self.infosImgProv+a_nbre+'\n# '+textNbre+str(self.valChoixFonduPourSpirale-2)+_(' et ')+str(self.valChoixFonduPourSpirale)+'\n'+a_nbre+'\n'
		
			# Affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv)
			self.fram.setEnabled(True)
		
			# remise à 0 de la variable provisoire de log
			self.infosImgProv = ''

			# -------------------------------------
			# On vide tous les répertoires temporaires pour la fin du traitement. Ainsi
			# on peut éliminer/rajouter des images pour relancer un autre traitement.
			# -------------------------------------

			lRedimSeqA = glob.glob(self.repTamponRedimSeqA+os.sep+'*.*')
			if len(lRedimSeqA) > 0:
				for a1 in lRedimSeqA: os.remove(a1)

			lRedimSeqB = glob.glob(self.repTamponRedimSeqB+os.sep+'*.*')
			if len(lRedimSeqB) > 0:
				for a2 in lRedimSeqB: os.remove(a2)
		
			lRepTamponRedimSpir1 = glob.glob(self.repTampon_spir_1+'redim'+os.sep+'*.*')
			if len(lRepTamponRedimSpir1) > 0:
				for a3 in lRepTamponRedimSpir1: os.remove(a3)

			lRepTamponRedimSpir2 = glob.glob(self.repTampon_spir_2+'redim'+os.sep+'*.*')
			if len(lRepTamponRedimSpir2) > 0:
				for a4 in lRepTamponRedimSpir2: os.remove(a4)

			lRepTamponSpir1 = glob.glob(self.repTampon_spir_1+os.sep+'*.*')
			if len(lRepTamponSpir1) > 0:
				for a5 in lRepTamponSpir1: os.remove(a5)

			lRepTamponSpir2 = glob.glob(self.repTampon_spir_2+os.sep+'*.*')
			if len(lRepTamponSpir2) > 0:
				for a6 in lRepTamponSpir2: os.remove(a6)

			lRepTamponRedimPasSpir1 = glob.glob(self.repTampon_pas_spir_1+'redim'+os.sep+'*.*')
			if len(lRepTamponRedimPasSpir1) > 0:
				for a7 in lRepTamponRedimPasSpir1: os.remove(a7)

			lRepTamponRedimPasSpir2 = glob.glob(self.repTampon_pas_spir_2+'redim'+os.sep+'*.*')
			if len(lRepTamponRedimPasSpir2) > 0:
				for a8 in lRepTamponRedimPasSpir2: os.remove(a8)

			lRepTamponPasSpir1 = glob.glob(self.repTampon_pas_spir_1+os.sep+'*.*')
			if len(lRepTamponPasSpir1) > 0:
				for a9 in lRepTamponPasSpir1: os.remove(a9)

			lRepTamponPasSpir2 = glob.glob(self.repTampon_pas_spir_2+os.sep+'*.*')
			if len(lRepTamponPasSpir2) > 0:
				for a10 in lRepTamponPasSpir2: os.remove(a10)

			# On libere la memoire
			del listeResultatChem, nbreElem, parc, imgOpSPI1, imgOpSPI2, calcCHANGblend, imgSPI, val_pourc, conc3L, lRenomAff, parcC3L, nbreElemRenom, val_pourc_renom, chemin, textNbre, a_nbre

		except:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"<p><b>Première situation d'erreur:</b> vous n'avez pas chargé d'image(s) (bouton <b>Ajouter</b>) dans l'onglet <b>Image(s) séquence A</b>. Recommencez et chargez des images aussi bien dans <b>Image(s) séquence A</b>, que dans <b>Image(s) séquence B</b>.</p><p><b>Deuxième situation d'erreur:</b> une (ou plusieurs) des images que vous avez chargé n'a pas le bon mode, en effet, pour la création de transitions, EKD ne peut pas travailler avec les images dont le mode est <b>L</b> (il s'agit d'images en niveaux de gris), <b>P</b> (images GIF) ou <b>RGBA</b> (images avec un canal alpha, c'est à dire des images avec un canal de transparence) . Vérifiez le mode de chacune de vos images (et ce dans les onglets <b>Image(s) séquence A</b> et <b>Image(s) séquence B</b>), pour ce faire sélectionnez une image et cliquez sur le bouton <b>Infos</b> (dans la fenêtre qui s'ouvre, chacune des images fautives devrait avoir soit <b>L</b>, soit <b>P</b> ou soit <b>RGBA</b> indiqué en face du champ <b>Mode</b>). Eliminez chacune de ces images (par le bouton <b>Retirer</b>) et relancez le traitement (par les boutons <b>Voir le résultat</b> ou <b>Appliquer et sauver</b>).</p>"))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()
			return

	
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""
		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<p><b>Vous pouvez ici apposer une transition fondu enchaîné tout en mélangeant le tout avec une transition spirale et ce entre deux lots d'images.</b></p><p><b>Selon Wikipédia, voilà une définition de fondu enchaîné: '... pour l'image: une transition entre deux plans (c'est-à-dire deux points de vue différents), deux images différentes: on remplace progressivement une image par une autre.<br>On l'utilise souvent pour faire la transition entre deux scènes d'une durée allant de plusieurs images à plusieurs secondes.'</b></p><p><b>En ce qui nous concerne ici il s'agit principalement d'une transition spirale ; dans la première moitié du passage de la première scène à la seconde, les images des deux scènes se mélangent (fondu enchaîné) et en même temps une spirale se met en route dans le sens des aiguilles d'une montre, puis dans la seconde moitié la spirale tourne dans le sens inverse.</b></p><p>Dans l'onglet <b>'Image(s) séquence A'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Passez maintenant dans l'onglet <b>'Image(s) séquence B'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images).</p><p>Dans <b>'Réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b>.</p><p> Cliquez sur le bouton <b>'Voir le résultat'</b> vous voyez à ce moment là le résultat de la transition <b>Spirale</b> entre la dernière image du lot de la séquence A et la première image du lot de la séquence B, s'afficher dans une nouvelle fenêtre.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer et sauver'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>Image(s) après traitement</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>'Infos'</b> vous permet de voir les image(s) de la séquence A chargée(s), les image(s) de la séquence B chargée(s), le résultat de la transition spirale et le nombre d'image(s) incluses dans la spirale.</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSourceSeqA.saveFileLocation(self.idSection, u'sourcesa')
		self.afficheurImgSourceSeqB.saveFileLocation(self.idSection, u'sourcesb')
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2.value()))


	def load(self) :
		self.afficheurImgSourceSeqA.loadFileLocation(self.idSection, u'sourcesa')
		self.afficheurImgSourceSeqB.loadFileLocation(self.idSection, u'sourcesb')
		self.spin1.setValue(int(EkdConfig.get(self.idSection, u'spin1')))
		self.spin2.setValue(int(EkdConfig.get(self.idSection, u'spin2')))	
