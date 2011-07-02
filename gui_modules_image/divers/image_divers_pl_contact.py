#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, glob, string, Image, ImageDraw, ImageFont
# Le module itertools (voir à partir de la ligne 752)
from itertools import cycle, islice, izip
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_image.image_base import Base, SpinSlider

from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue

#  Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Nouvelle fenêtre d'aide
from gui_modules_common.EkdWidgets import EkdAide
# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Apercu(QWidget):
	"Apercu de la dernière planche-contact"
	def __init__(self, parent):
		QWidget.__init__(self)
		self.parent = parent
		# Facteur A4 (format A4: 210 x 297 mm) en partant de 1mm <-> 1px
		self.fA4 = 0.70
	
	def taille(self):
		"renvoie la taille de la dernière planche-contact"
		i = self.parent.comboPorPay.currentIndex()
		orientation=str(self.parent.comboPorPay.itemData(i).toString())
		if orientation=='form_port': l, h = int(self.fA4*210), int(self.fA4*297)
		else: h, l = int(self.fA4*210), int(self.fA4*297)
		return l, h
	
	def paintEvent(self, event):
		"Dessin de l'apercu de la dernière planche-contact"
		paint = QPainter()
		paint.begin(self)
		
		#=== Paramètres cosmétiques ===#
		paint.setRenderHint(QPainter.Antialiasing)
		# Couleur de fond
		i = self.parent.comboVal.currentIndex()
		couleur=str(self.parent.comboVal.itemData(i).toStringList()[0])
		palette = {	'noir': QColor(0, 0, 0),
				'gris': QColor(120, 120, 120),
				'blanc': QColor(255, 255, 255)}
		qcolor = palette[couleur]
		qcolor.setAlpha(240) # petite atténuation de la couleur
		paint.setBrush(qcolor)
		if couleur != 'noir':
			paint.setPen(QColor(0,0,0))
		else:
			paint.setPen(QColor(120,120,120))
		
		#=== Paramètres numériques ===#
		# Nombre de lignes et de colonnes
		nbrColonne = self.parent.spin2.value()
		nbrLigne = self.parent.spin3.value()
		# Nombre de cases par planche
		nbrCase = nbrLigne*nbrColonne
		
		# Largeur et hauteur de l'aperçu planche-contact
		l, h = self.taille()
		# Décalage pour centrer la planche horizontalement
		offset = (self.parent.tabwidget.size().width() - l)/2
		# Largeur et hauteur d'une case
		largeurCase, hauteurCase = l/nbrColonne, h/nbrLigne
		
		# Fréquence de sélection (passage d'une image à l'autre)
		frequenceSelection = self.parent.spin1.value()
		# Nombre d'images sélectionnées
		nbrImgTotale = len(self.parent.afficheurImgSource.getLength())
		# Nombre d'images qui apparaîtront dans les planches
		if nbrImgTotale==1: nbrImgPlanche = 1
		else: nbrImgPlanche = nbrImgTotale/frequenceSelection
		
		# Nombre d'img de la dernière planche et nombre de planches
		nbrImgDernierePlanche = nbrImgPlanche
		nbrPlanche = 1
		while nbrCase < nbrImgDernierePlanche:
			nbrImgDernierePlanche -= nbrCase
			nbrPlanche += 1
		else:
			if nbrImgTotale == 0 or frequenceSelection>nbrImgTotale:
				nbrPlanche = 0
		
		#=== Traçage ===#
		# Tracé du rectangle de la planche-contact
		paint.drawRect(offset+0, 0, l, h)
		
		# Tracé des colonnes
		for x in range(nbrColonne):
			paint.drawLine(offset+x*largeurCase, 0, offset+x*largeurCase, h)
		# Tracé des lignes
		for y in range(nbrLigne):
			paint.drawLine(offset+0, y*hauteurCase, offset+l, y*hauteurCase)
		
		# On raye les cases qui n'accueilleront pas d'images
		if nbrImgDernierePlanche == nbrCase: return
		indiceColonne1ereImgVide = nbrImgDernierePlanche
		indiceLigne1ereImgVide = 0
		while indiceColonne1ereImgVide >= nbrColonne:
			indiceColonne1ereImgVide -= nbrColonne
			indiceLigne1ereImgVide += 1
		for y in range(indiceLigne1ereImgVide, nbrLigne):
			if y == indiceLigne1ereImgVide:
				indiceColonneDepart = indiceColonne1ereImgVide
			else: indiceColonneDepart = 0
			for x in range(indiceColonneDepart, nbrColonne):
				paint.drawLine(offset+x*largeurCase, y*hauteurCase,
					offset+(x+1)*largeurCase, (y+1)*hauteurCase)
				paint.drawLine(offset+(x+1)*largeurCase, y*hauteurCase,
					offset+x*largeurCase, (y+1)*hauteurCase)
		
		self.parent.apercuGroup.setTitle(_(u"Pseudo-aperçu de la dernière planche-contact (%s planche(s)-contact au total)" %nbrPlanche))
		
		paint.end()


class Image_Divers_PlContact(QWidget):
	"""# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Planche-contact
	# -----------------------------------"""
	def __init__(self, statusBar, geometry):
        	QWidget.__init__(self)
		
		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------
		#=== Tout sera mis dans une boîte verticale ===#
		vbox=QVBoxLayout(self)
		
		#=== Création des répertoires temporaires ===#
		# Utilisation de EkdConfig pour les repertoire tmp
		self.repTampon = EkdConfig.getTempDir() + os.sep + 'tampon' + os.sep + 'image_divers_planche_contact' + os.sep
		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)
		if os.path.isdir(self.repTampon + 'redim') is False:
        		os.makedirs(self.repTampon + 'redim')
			
		# Répertoires temporaires de gestion des 2 formats possibles des images:
		# format paysage ou format portrait. Ces 2 répertoires servent pour la
		# rotation des images (très utile pour les images en format portrait)
		if os.path.isdir(self.repTampon + 'resolution_tmp_larg_haut') is False:
        		os.makedirs(self.repTampon + 'resolution_tmp_larg_haut')
			
		if os.path.isdir(self.repTampon + 'resolution_larg_haut') is False:
        		os.makedirs(self.repTampon + 'resolution_larg_haut')
		
		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon + '*.*'):
			os.remove(toutRepCompo)
	
		# Si des images sont redimensionnées dans un traitement 
		# précédent le répertoire redim est vidé de son contenu	
		if len(glob.glob(self.repTampon+'redim' + os.sep + '*.*'))>0:
			# Epuration/elimination des fichiers tampon dans le rep redim
			for repTemp in glob.glob(self.repTampon+'redim' + os.sep + '*.*'):
				os.remove(repTemp)
				
		# Le répertoire est vidé de son contenu	
		if len(glob.glob(self.repTampon+'resolution_tmp_larg_haut' + os.sep + '*.*'))>0:
			# Epuration/elimination des fichiers
			for repTempLargHaut in glob.glob(self.repTampon+'resolution_tmp_larg_haut' + os.sep + '*.*'):
				os.remove(repTempLargHaut)
				
		# Le répertoire est vidé de son contenu	
		if len(glob.glob(self.repTampon+'resolution_larg_haut' + os.sep + '*.*'))>0:
			# Epuration/elimination des fichiers
			for repLargHaut in glob.glob(self.repTampon+'resolution_larg_haut' + os.sep + '*.*'):
				os.remove(repLargHaut)

		# Délai avant conversion
		self.timer = QTimer()
		self.connect(self.timer, SIGNAL('timeout()'), self.sonderTempsActuel)
		
		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)
		
		# Est-ce que des images ont été converties et qu'elles n'ont pas encore été montrées?
		# Marche aussi quand la conversion a été arrêté avant la fin de la 1ère image
		self.conversionImg = 0
		
		# Est-ce qu'une prévisualisation a été appelée?
		self.previsualImg = 0
		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0
		
		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()

		# Gestion de la configuration via EkdConfig

		# Paramètres de configuration
		self.config = EkdConfig
		# Identifiant du cadre
		self.idSection = "image_planche-contact"
		# Log du terminal
		self.base.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		self.listeImgSource = []
		self.listeImgDestin = []
		
		#------------------------
		# Onglets et stacked
		#------------------------

		self.tabwidget=QTabWidget()
		
		#=== 1er onglet ===#
		self.framReglage=QFrame()
		vboxReglage=QVBoxLayout(self.framReglage)

		# Boîte de combo
		self.comboReglage=QComboBox()
		self.listeComboReglage=[(_(u'JPEG (.jpg)'), '.jpg'),\
					(_(u'JPEG (.jpeg)'), '.jpeg'),\
					(_(u'PNG (.png)'), '.png'),\
					(_(u'GIF (.gif)'), '.gif'),\
					(_(u'BMP (.bmp)'), '.bmp'),\
					(_(u'PPM (.ppm)'), '.ppm'),\
					(_(u'TIFF (.tiff)'), '.tiff'),\
					(_(u'TIF (.tif)'), '.tif')]

		# Insertion des formats dans la combo box
		for i in self.listeComboReglage:
                	self.comboReglage.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		
		# Boîte de combo
		self.comboPorPay=QComboBox()
		self.listeComboPorPay=[(_(u'Format portrait'), 'form_port'),\
					(_(u'Format paysage'), 'form_pay')]
		# Insertion des formats portrait ou paysage dans la combo box
		for i in self.listeComboPorPay:
                	self.comboPorPay.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboPorPay, SIGNAL("currentIndexChanged(int)"), self.changerComboPorPay)
		self.comboPorPay.setToolTip(_(u"Inverse la valeur des nombres d'images par ligne et par colonne"))
		
		##################################### Ajouté le 12/11/10 #############
		# Boîte de combo
		self.comboTailPl=QComboBox()
		self.listecomboTailPl=[(_(u'Standard: 842x595 (pixels)'), 'taille_planche_842x595'),\
				       (_(u'Moyenne: 1684x1190 (pixels)'), 'taille_planche_1684x1190'),\
				       (_(u'Bonne: 2526x1785 (pixels)'), 'taille_planche_2526x1785'),\
				       (_(u'Excellente: 3368x2380 (pixels)'), 'taille_planche_3368x2380')]
		# Insertion de la taille de la planche dans la combo box
		for i in self.listecomboTailPl:
                	self.comboTailPl.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboTailPl, SIGNAL("currentIndexChanged(int)"), self.changerComboTailPl)
		self.comboTailPl.setToolTip(_(u"Change la taille de la planche (attention au temps de rendu !)"))
		##################################### Fin de Ajouté le 12/11/10 ######
		
		# Boîte de combo
		self.comboVal=QComboBox()
		self.listeComboVal=[(_(u'Blanc'), 'blanc'),\
				    (_(u'Noir'),  'noir'),\
				    (_(u'Gris'),  'gris')]
		# Insertion des valeurs (ce ne sont pas des couleurs) dans la combo box
		for i in self.listeComboVal:
                	self.comboVal.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboVal, SIGNAL("currentIndexChanged(int)"), self.changerComboVal)

		self.grid = QGridLayout()
		self.grid.addWidget(QLabel(_(u"Passage d'une image à l'autre")), 0, 0)
		# Méta-widget: boite de spin + curseur
		# arguments: valeur debut, fin, defaut, identifiant configuration, parent
		self.spin1=SpinSlider(1, 1000, 1, 'passage_image', self)
		self.grid.addWidget(self.spin1, 0, 1)
		self.grid.addWidget(QLabel(_(u'Orientation de la page de fond')), 1, 0)
		self.grid.addWidget(self.comboPorPay, 1, 1)
		##################################### Ajouté le 12/11/10 #############
		self.labelTailPl=QLabel(_(u'Qualité (taille de la page de fond)'))
		self.labelTailPl.hide()
		self.comboTailPl.hide()
		self.grid.addWidget(self.labelTailPl, 2, 0)
		self.grid.addWidget(self.comboTailPl, 2, 1)
		##################################### Fin de Ajouté le 12/11/10 ######
		self.grid.addWidget(QLabel(_(u'Valeur du fond')), 3, 0)
		self.grid.addWidget(self.comboVal, 3, 1)
		self.grid.addWidget(QLabel(_(u"Nombre d'images par ligne")), 4, 0)
		self.spin2=SpinSlider(1, 12, 4, 'nombre_images_largeur', self)
		self.grid.addWidget(self.spin2, 4, 1)
		self.grid.addWidget(QLabel(_(u"Nombre d'images par colonne")), 5, 0)
		self.spin3=SpinSlider(1, 14, 6, 'nombre_images_longueur', self)
		self.grid.addWidget(self.spin3, 5, 1)
		self.grid.addWidget(QLabel(_(u"Largeur de la marge en pixels (entre les images)")), 6, 0)
		self.spin4=SpinSlider(1, 100, 10, 'largeur_marge', self)
		self.grid.addWidget(self.spin4, 6, 1)
		self.grid.addWidget(QLabel(_(u'Format de sortie de la planche-contact')), 7, 0)
		self.grid.addWidget(self.comboReglage, 7, 1)
		
		self.grid.setAlignment(Qt.AlignHCenter)
		
		vboxReglage.addLayout(self.grid)
		
		# Pseudo-aperçu de la planche-contact (sans les images)
		self.apercu = Apercu(self)
		self.connect(self.spin2, SIGNAL("valueChanged(int)"), self.rechargePlanche)
		self.connect(self.spin3, SIGNAL("valueChanged(int)"), self.rechargePlanche)
		self.connect(self.comboVal, SIGNAL("currentIndexChanged(int)"), self.rechargePlanche)
		self.connect(self.spin1, SIGNAL("valueChanged(int)"), self.rechargePlanche)
		self.connect(self.comboPorPay, SIGNAL("currentIndexChanged(int)"), self.rechargePlanche)
		
		# Boîte de groupe d'aperçu
		self.apercuGroup = QGroupBox(_(u"Pseudo-aperçu de la dernière planche-contact (0 planche-contact au total)"))
		self.hboxApercu = QHBoxLayout(self.apercuGroup)
		# Remplissage de la boite par l'aperçu
		self.rechargePlanche()
		vboxReglage.addStretch()
		vboxReglage.addWidget(self.apercuGroup)

		#=== onglet supplémentaire ===#
		self.framNbreImg=QFrame() ##
		vboxReglage=QVBoxLayout(self.framNbreImg)
		
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel(_(u"Traitement à partir de l'image (numéro)")), 0, 0)
		self.spin1valNombres=SpinSlider(1, 10000, 1, '', self)
		self.grid.addWidget(self.spin1valNombres, 0, 1)
		self.connect(self.spin1valNombres, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		self.grid.addWidget(QLabel(_(u"Nombre de chiffres après le nom de l'image")), 1, 0)
		self.spin2valNombres=SpinSlider(3, 6, 3, '', self)
		self.grid.addWidget(self.spin2valNombres, 1, 1)
		self.connect(self.spin2valNombres, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.grid.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid)
		vboxReglage.addStretch()
		
		# Mise par défaut de la résolution de l'image de fond ------
		# Résolution en largeur de l'image de base (le fond)
		self.resLarg=595
		# Résolution en hauteur de l'image de base (le fond)
		self.resHaut=842
		# Mise par défaut de la valeur de l'image de fond ----------
		# Par défaut le fond est blanc
		self.val=(255, 255, 255)
		# Couleur de la police de numérotation des pages
		self.coulPolice=(0, 0, 0)
		# ----------------------------------------------------------
		
		#=== 2ème onglet ===#
		# infos - logs
		self.zoneAffichInfosImg = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneAffichInfosImg.setText = self.zoneAffichInfosImg.setPlainText
		self.zoneAffichInfosImg.setReadOnly(True)
		self.framImg=QFrame()
		vboxReglage=QVBoxLayout(self.framImg)
		vboxReglage.addWidget(self.zoneAffichInfosImg)
		self.framImg.setEnabled(False)

		# -------------------------------------------------
		# Onglets d'affichage image source et destination
		# -------------------------------------------------

		# Là où s'afficheront les images
		self.afficheurImgSource=SelectWidget(geometrie = self.mainWindowFrameGeometry)
		# Gestion de la configuration via EkdConfig
		self.afficheurImgDestination=Lecture_VisionImage(statusBar)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.

		self.indexTabImgSource = self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		self.indexTabReglage=self.tabwidget.addTab(self.framReglage, _(u'Mise en page'))
		self.indexTabNbreImg=self.tabwidget.addTab(self.framNbreImg, _(u"Autres réglages"))
		self.indexTabImgDestin = self.tabwidget.addTab(self.afficheurImgDestination, _(u'Image(s) après traitement'))
		self.indexTabInfo=self.tabwidget.addTab(self.framImg, _(u'Infos'))
	
                self.scroll = QScrollArea()
                self.scroll.setWidget(self.tabwidget)
                self.scroll.setWidgetResizable(True)
		vbox.addWidget(self.scroll)
		
		#------------------
		# Widgets du bas
		#------------------
		
		# Boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones" + os.sep + "icone_aide_128.png"))
		boutAide.setFocusPolicy(Qt.NoFocus)
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
		self.info=QPushButton(_(u" Information"))
		self.info.setIcon(QIcon("Icones" + os.sep + "icone_info_128.png"))
		self.info.setFocusPolicy(Qt.NoFocus)
		self.connect(self.info, SIGNAL("clicked()"), self.information)

		self.boutApPremPl = QPushButton(_(u" Voir le résultat"))
		self.boutApPremPl.setIcon(QIcon("Icones" + os.sep + "icone_visionner_128.png"))
		self.boutApPremPl.setFocusPolicy(Qt.NoFocus)
		self.boutApPremPl.setEnabled(False)
		self.connect(self.boutApPremPl, SIGNAL("clicked()"), self.visu_1ere_planche)

		self.boutApp=QPushButton(_(u" Appliquer"))
		self.boutApp.setIcon(QIcon("Icones"+ os.sep +"icone_appliquer_128.png"))
		self.boutApp.setFocusPolicy(Qt.NoFocus)
		self.boutApp.setEnabled(False)
		self.connect(self.boutApp, SIGNAL("clicked()"), self.appliquer0)
		
		# Ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons
		hbox=QHBoxLayout()
		hbox.addWidget(boutAide)
		hbox.addStretch()	# espace entre les 2 boutons
		hbox.addWidget(self.info)
		hbox.addStretch()
		hbox.addWidget(self.boutApPremPl)
		hbox.addStretch()
		hbox.addWidget(self.boutApp)
		vbox.addLayout(hbox)
		
		self.setLayout(vbox)
		
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		self.base.valeurComboIni(self.comboReglage, self.config, self.idSection, 'format')
		self.base.valeurComboIni(self.comboVal, self.config, self.idSection, 'couleur_fond')
		self.base.valeurComboIni(self.comboPorPay, self.config, self.idSection, 'orientation')
		
		#------------------------------------------------
		# Barre de progression dans une fenêtre séparée
		#------------------------------------------------
		
		self.progress=QProgressDialog(_(u"Progression ..."), _(u"Arrêter le processus"), 0, 100)
		self.progress.setWindowTitle(_(u'EnKoDeur-Mixeur. Fenêtre de progression'))
		# Attribution des nouvelles dimensions
		self.progress.setMinimumWidth(500)
		self.progress.setMinimumHeight(100)
		
		self.connect(self.tabwidget, SIGNAL("currentChanged(int)"), self.fctTab)

		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
		#----------------------------------------------------------------------------------------------------
		
		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifImgSource)
	
	
	def modifImgSource(self, i):
		"""On active ou désactive les boutons d'action et on recharge le pseudo-aperçu de planche-contact
		en fonction du nombre d'images présentes dans le widget de sélection"""
		self.boutApp.setEnabled(i)
		self.boutApPremPl.setEnabled(i)
		self.modifImageSource = 1
		# Mise à jour de l'aperçu
		self.rechargePlanche()
		
	
	def rechargePlanche(self):
		"On recharge le contenu de la boite de groupe contenant la planche-contact à chaque fois qu'un paramètre est modifiée pour celle-ci"
		self.apercu.repaint()
		l, h = self.apercu.taille()
		margeGroup = self.apercuGroup.getContentsMargins()
		if PYQT_VERSION_STR >= "4.3.0":
			margeHBox = self.hboxApercu.getContentsMargins()
		else:
			margeHBox = [self.hboxApercu.margin()]*4
		margeLargeur=margeGroup[0]+margeGroup[2]+margeHBox[0]+margeHBox[2]
		margeHauteur=margeGroup[1]+margeGroup[3]+margeHBox[1]+margeHBox[3]
		tailleL = l + margeLargeur
		tailleH = h + margeHauteur
		self.apercuGroup.setMinimumSize(tailleL, tailleH)
		self.hboxApercu.addWidget(self.apercu)
		
		
	def changeValNbreImg_1(self): ##
		"""Gestion du nombre d'images à traiter"""
		#print "Traitement a partir de l'image (numero):", self.spin1valNombres.value()
		EkdPrint(u"Traitement a partir de l'image (numero): " + str(self.spin1valNombres.value()))
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2valNombres.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: " + str(self.spin2valNombres.value()))
	
	
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
			elif not self.boutApp.isEnabled() or self.modifImageSource:
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
	
	
	def changerComboReglage(self, i):
		"""Récup/affichage ds le terminal de l'index de self.comboReglage"""
		#print self.comboReglage.currentIndex()
		#print self.comboReglage.currentText()
		EkdPrint(self.comboReglage.currentText())
		idCombo=str(self.comboReglage.itemData(i).toString())
		self.config.set(self.idSection, 'format', idCombo)
		
		
	def changerComboPorPay(self, i):
		"""Récup/affichage ds le terminal de l'index de self.comboPorPay"""
		#print self.comboPorPay.currentText()
		
		idCombo=str(self.comboPorPay.itemData(i).toString())
	
		##################################### Adapté le 12/11/10 #############
		# Pour le format portrait la taille est standard, c'est à dire 595x842 ... et les
		# widgets deviennent invisibles ... 
		if self.comboPorPay.currentIndex()==0:
			self.labelTailPl.hide()
			self.comboTailPl.hide()
			# Résolution en largeur de l'image de base (le fond)
			self.resLarg=595
			# Résolution en hauteur de l'image de base (le fond)
			self.resHaut=842
			#print "La taille de la planche est %sx%s" % (self.resLarg, self.resHaut)
			EkdPrint(u"La taille de la planche est %sx%s" % (self.resLarg, self.resHaut))
		# ... par contre si l'utilisateur choisit le format portrait, les widgets se révèlent 
		if self.comboPorPay.currentIndex()==1:
			self.labelTailPl.show()
			self.comboTailPl.show()
		##################################### Fin de Adapté le 12/11/10 ######
		
		# On inverse les valeurs du nombre d'images/ligne et colonne
		nbrImgLigne = self.spin2.value()
		nbrImgColonne = self.spin3.value()
		self.spin2.setValue(nbrImgColonne)
		self.spin3.setValue(nbrImgLigne)
		
		self.config.set(self.idSection, 'orientation', idCombo)
			
		
	##################################### Ajouté le 12/11/10 #############
	def changerComboTailPl(self, i):
	 
		idCombo=str(self.comboTailPl.itemData(i).toString())

		if self.comboPorPay.currentIndex()==1:
		        # -------------------------------------------------------------------
			# Réservé uniquement au choix du format paysage
			# -------------------------------------------------------------------
			# Différentes valeurs selon la taille de la planche choisie
			# (résolution en largeur et en hauteur de l'image de base [le fond])
			if idCombo=='taille_planche_842x595':
				self.resLarg, self.resHaut = 842, 595
			elif idCombo=='taille_planche_1684x1190': 
				self.resLarg, self.resHaut = 1684, 1190
			elif idCombo=='taille_planche_2526x1785':
				self.resLarg, self.resHaut = 2526, 1785
			elif idCombo=='taille_planche_3368x2380':
				self.resLarg, self.resHaut = 3368, 2380
			#print "La taille de la planche est %sx%s" % (self.resLarg, self.resHaut)
			EkdPrint(u"La taille de la planche est %sx%s" % (self.resLarg, self.resHaut))
			
		self.config.set(self.idSection, 'taille', idCombo)
	##################################### Fin de Ajouté le 12/11/10 ######
	
	
	def changerComboVal(self, i):
		"""Récup/affichage ds le terminal de l'index de self.comboVal"""
		#print self.comboVal.currentText()
		idCombo=str(self.comboVal.itemData(i).toStringList()[0])
		if idCombo=='blanc':
			#print "L'image de fond est blanche"
			EkdPrint(u"L'image de fond est blanche")
			self.val=(255, 255, 255)
			self.coulPolice=(0, 0, 0)
		elif idCombo=='noir':
			#print "L'image de fond est noire"
			EkdPrint(u"L'image de fond est noire")
			self.val=(0, 0, 0)
			self.coulPolice=(255, 255, 255)
		elif idCombo=='gris':
			#print "L'image de fond est grise"
			EkdPrint(u"L'image de fond est grise")
			self.val=(127, 127, 127)
			self.coulPolice=(255, 255, 255)
		self.config.set(self.idSection, 'couleur_fond', idCombo)
	
		
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
		
		if len(self.lStatDimSeq)>1:
			return 0
		else:
			return 1
	
	
	def redim_img(self):
		"""Si l'utilisateur charge des images avec des tailles complètement différentes --> les images de la séquence  peuvent être redimensionnées"""
		
		if not self.stat_dim_img():
			reply = QMessageBox.warning(self, 'Message',
			_(u"Vos images ne sont pas toutes de la même taille. Voulez-vous redimensionner les images de sortie à la taille la plus répandue dans la séquence?"), QMessageBox.Yes, QMessageBox.No)
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
				sRedim=obImg.resize(self.dimStatImg, Image.ANTIALIAS)
				chemSortie = self.repTampon+'redim/'+os.path.basename(chemImg)
				sRedim.save(chemSortie)
				self.listeImgSource[index] = chemSortie
				index += 1
		
	
	def information(self):
		""" Information(s) concernant la planche-contact """
		
		# Calcul du nombre d'images sur la page
		nb=(self.spin2.value()*self.spin3.value())*20
		
		info=QMessageBox(self)
		info.setText(_(u"Le nombre maximum d'images (miniatures) pouvant être affichées dans les différentes pages de la planche-contact est de <b>%s</b>, en fait le nombre d'images par ligne multiplié par le nombre d'images par colonne, tout ceci multiplé par 20 (il s'agit du nombre de pages possibles pour la planche-contact).") % nb)
		info.setWindowTitle(_(u"Information"))
		info.setIcon(QMessageBox.Information)
		info.exec_()
		
		
	def visu_1ere_planche(self):
		""" Visualisation de la planche-contact avant la sauvegarde finale. Pour voir les commentaires
		des lignes dans cette fonction, se reporter à la fonction planche_contact juste en dessous """

		# Récupération de la liste des fichiers chargés
		self.listeChemin=self.afficheurImgSource.getFiles()

		listeRes = []
		
		for nb, parcImg in enumerate(self.listeChemin):
			obImg = Image.open(parcImg)
			w = obImg.size[0]
			h = obImg.size[1]
			extMode = os.path.splitext(parcImg)[1]
			chemin = self.repTampon+'resolution_tmp_larg_haut'+os.sep+'res_'+string.zfill(1+nb, 6)+extMode
			if h > w: 
				obImg.rotate(90).save(chemin)
				listeRes.append(chemin)
			else:
				obImg.save(chemin)
				listeRes.append(chemin)

		nbMax=self.spin2.value()*self.spin3.value()
		
		nbreImgLargeur, nbreImgHauteur = self.spin2.value(), self.spin3.value()
		
		largMiniature=(self.resLarg-(nbreImgLargeur+1)*self.spin4.value())/nbreImgLargeur
		
		ratio=float(self.resLarg)/float(self.resHaut)
		
		if self.resLarg<=self.resHaut:
			hautMiniature=int(float(largMiniature)*ratio)
		elif self.resLarg>self.resHaut:
			hautMiniature=int(float(largMiniature)/ratio)
			if nbreImgHauteur>nbreImgLargeur:
				self.tabwidget.setCurrentIndex(self.indexTabReglage)
				if QMessageBox.question(self,_(u"Planche-Contact"),_(u"Vous avez effectué les réglages afin que le nombre d'images par colonne soit plus important que nombre d'images par ligne. Vous allez en conséquence obtenir d'assez mauvais résultats (chevauchement d'images). Pour un format paysage, le nombre d'images par ligne doit être supérieur au nombre d'images par colonne.\n\nVoulez-vous continuer?"),QMessageBox.Yes|QMessageBox.No) == QMessageBox.No: return
		
		hautMarge=(self.resHaut-(nbreImgHauteur*hautMiniature))/(nbreImgHauteur+1)
		
		lCoordPlanche=[(((totoX+1)*self.spin4.value())+(totoX*largMiniature), ((totoY+1)*hautMarge)+(totoY*hautMiniature)) for totoY in range(nbreImgHauteur) for totoX in range(nbreImgLargeur)]
		
		nbreImg=len(listeRes)

		listeImCo=[listeRes[parc_1] for parc_1 in range(0, len(listeRes), self.spin1.value())]

		lImCoordFinal=list(islice(izip(cycle(listeImCo), cycle(lCoordPlanche)), max(len(lCoordPlanche[0:len(listeImCo)]), len(listeImCo))))
		
		posXFonte=lCoordPlanche[len(lCoordPlanche)-1][0]
		posYFonte=lCoordPlanche[len(lCoordPlanche)-1][1]+hautMiniature+10

		if posYFonte<(self.resHaut-10):
			posYFonte=posYFonte
		elif posYFonte>=(self.resHaut-10):
			posYFonte=lCoordPlanche[len(lCoordPlanche)-1][1]+hautMiniature+1
		
		fonte=ImageFont.load_default()

		img2=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img2).text((posXFonte, posYFonte), '-- 1 --', font=fonte, fill=self.coulPolice)
		
		listeOcc=[]
		for images, coorXY in lImCoordFinal:
		
			listeOcc.append(images)
			img1=Image.open(images)
			redim=img1.resize((largMiniature, hautMiniature), Image.ANTIALIAS)
			
			if (len(listeOcc)*100/nbMax)<=100:
				self.cheminCourantSauv=self.repTampon+'img_visu_pl_c_'+string.zfill(1, 3)+'.jpg'
				img2.paste(redim, coorXY)
				img2.save(self.cheminCourantSauv)
		
		# Affichage de l'image temporaire 
		# Ouverture d'une boite de dialogue affichant l'aperçu.
		#
		# Affichage par le bouton Voir le résultat
		visio = VisionneurEvolue(self.cheminCourantSauv)
		visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
		visio.exec_()
		
		return 0

	
	def planche_contact(self):
		""" Planche-contact """

		# Récupération de la liste des fichiers chargés
		self.listeChemin=self.afficheurImgSource.getFiles()

		# Cette partie du code est extrêmement utile quand l'utilisateur charge des
		# images en format paysage ou des images en format portrait, le sens/direction
		# d'affichage des miniatures sera respecté dans la planche-contact finale 
		# (--> format paysage ou portrait)
		listeRes = []
		
		for nb, parcImg in enumerate(self.listeChemin):
			obImg = Image.open(parcImg)
			# Résolution largeur
			w = obImg.size[0]
			# Résolution hauteur
			h = obImg.size[1]
			# Collecte de l'extension des images
			extMode = os.path.splitext(parcImg)[1]
			# Chemin de copie ou de rotation des images (on passe par un rep. temporaire)
			chemin = self.repTampon+'resolution_larg_haut'+os.sep+'res_'+string.zfill(1+nb, 6)+extMode
			# Si la résolution hauteur est supérieure à la résolution largeur
			if h > w: 
				obImg.rotate(90).save(chemin)
				listeRes.append(chemin)
			else:
				obImg.save(chemin)
				listeRes.append(chemin)
		
		# Calcul du nombre maximum d'images autorisées sur une page planche-contact
		# En fait le nombre max d'images autorisées correspond au nbre d'images par
		# ligne mutiplié par le nbre d'images par colonne
		nbMax=self.spin2.value()*self.spin3.value()
		
		nbreImgLargeur, nbreImgHauteur = self.spin2.value(), self.spin3.value()
		
		# Calcul de la résolution (la largeur) des images miniatures sur la planche-contact
		largMiniature=(self.resLarg-(nbreImgLargeur+1)*self.spin4.value())/nbreImgLargeur
		
		# Calcul du ratio de l'image de base
		ratio=float(self.resLarg)/float(self.resHaut)
		
		# Si la résolution de l'image est en format portrait (comme par défaut)
		if self.resLarg<=self.resHaut:
			# Calcul de la résolution (la hauteur) des images
			hautMiniature=int(float(largMiniature)*ratio)
		# Si la résolution de l'image est en format paysage
		elif self.resLarg>self.resHaut:
			# Calcul de la résolution (la hauteur) des images
			hautMiniature=int(float(largMiniature)/ratio)
			# Information pour l'utilisateur
			if nbreImgHauteur>nbreImgLargeur:
				self.tabwidget.setCurrentIndex(self.indexTabReglage)
				if QMessageBox.question(self,_(u"Planche-Contact"),_(u"Vous avez effectué les réglages afin que le nombre d'images par colonne soit plus important que nombre d'images par ligne. Vous allez en conséquence obtenir d'assez mauvais résultats (chevauchement d'images). Pour un format paysage, le nombre d'images par ligne doit être supérieur au nombre d'images par colonne.\n\nVoulez-vous continuer?"),QMessageBox.Yes|QMessageBox.No) == QMessageBox.No: return
		
		# Calcul de la taille de la marge haute
		hautMarge=(self.resHaut-(nbreImgHauteur*hautMiniature))/(nbreImgHauteur+1)
		
		# Comprehension-list pour calculer l'emplacement exact des images sur la planche
		# La taille de la marge haute est automatiquement adaptée (par le calcul de hautMarge)
		# Affiche (par exemple):
		# [(10, 38), (156, 38), (302, 38), ...]
		lCoordPlanche=[(((totoX+1)*self.spin4.value())+(totoX*largMiniature), ((totoY+1)*hautMarge)+(totoY*hautMiniature)) for totoY in range(nbreImgHauteur) for totoX in range(nbreImgLargeur)]
		
		# Récup du format sélectionné par l'utilisateur
		format=self.comboReglage.currentText()
		# Définition de l'extension pour la conversion
		if format=='JPEG (.jpg)': ext='.jpg'
		elif format=='JPEG (.jpeg)': ext='.jpeg'
		elif format=='PNG (.png)': ext='.png'
		elif format=='GIF (.gif)': ext='.gif'
		elif format=='BMP (.bmp)': ext='.bmp'
		elif format=='PPM (.ppm)': ext='.ppm'
		elif format=='TIFF (.tiff)': ext='.tiff'
		elif format=='TIF (.tif)': ext='.tif'

		nbreImg=len(listeRes)
		
		# Comprehension-list pour sélection des images
		listeImCo=[listeRes[parc_1] for parc_1 in range(0, len(listeRes), self.spin1.value())]
		
		# Mise en relation des images sélectionnées par la liste listeImCo et
		# les coordonnées calculées dans la liste lCoordPlanche. Un très très 
		# grand merci à Kent Johnson de la liste tutor at python.org pour avoir
		# trouvé cette solution. Les messages sont consultables ici:
		# http://mail.python.org/pipermail/tutor/2008-March/060701.html
		# http://mail.python.org/pipermail/tutor/2008-March/060702.html
		# http://mail.python.org/pipermail/tutor/2008-March/060703.html
		# Par exemple cette liste affiche:
		# [('/chemin/image_000001.png', (10, 38)), 
		#  ('/chemin/image_000002.png', (156, 38)), 
		#  ('/chemin/image_000003.png', (302, 38)),
		# ...]
		lImCoordFinal=list(islice(izip(cycle(listeImCo), cycle(lCoordPlanche)), max(len(lCoordPlanche[0:len(listeImCo)]), len(listeImCo))))
		
		# Coordonnées d'affichage de la police (numérotation des pages)
		posXFonte=lCoordPlanche[len(lCoordPlanche)-1][0]
		posYFonte=lCoordPlanche[len(lCoordPlanche)-1][1]+hautMiniature+10
		
		# Conditions d'affichage de la police ...
		if posYFonte<(self.resHaut-10):
			posYFonte=posYFonte
		elif posYFonte>=(self.resHaut-10):
			posYFonte=lCoordPlanche[len(lCoordPlanche)-1][1]+hautMiniature+1
		
		# Fonte truetype utilisée (celle par défaut)
		fonte=ImageFont.load_default()
		
		# Création de l'image de fond (1ère page) sur laquelle viendront 
		# se greffer les miniatures
		img2=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		# Ecriture du numéro de page
		ImageDraw.Draw(img2).text((posXFonte, posYFonte), '-- 1 --', font=fonte, fill=self.coulPolice)
		# Création des autres pages (20 en tout)
		img3=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img3).text((posXFonte, posYFonte), '-- 2 --', font=fonte, fill=self.coulPolice)
		img4=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img4).text((posXFonte, posYFonte), '-- 3 --', font=fonte, fill=self.coulPolice)
		img5=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img5).text((posXFonte, posYFonte), '-- 4 --', font=fonte, fill=self.coulPolice)
		img6=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img6).text((posXFonte, posYFonte), '-- 5 --', font=fonte, fill=self.coulPolice)
		img7=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img7).text((posXFonte, posYFonte), '-- 6 --', font=fonte, fill=self.coulPolice)
		img8=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img8).text((posXFonte, posYFonte), '-- 7 --', font=fonte, fill=self.coulPolice)
		img9=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img9).text((posXFonte, posYFonte), '-- 8 --', font=fonte, fill=self.coulPolice)
		img10=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img10).text((posXFonte, posYFonte), '-- 9 --', font=fonte, fill=self.coulPolice)
		img11=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img11).text((posXFonte, posYFonte), '-- 10 --', font=fonte, fill=self.coulPolice)
		img12=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img12).text((posXFonte, posYFonte), '-- 11 --', font=fonte, fill=self.coulPolice)
		img13=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img13).text((posXFonte, posYFonte), '-- 12 --', font=fonte, fill=self.coulPolice)
		img14=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img14).text((posXFonte, posYFonte), '-- 13 --', font=fonte, fill=self.coulPolice)
		img15=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img15).text((posXFonte, posYFonte), '-- 14 --', font=fonte, fill=self.coulPolice)
		img16=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img16).text((posXFonte, posYFonte), '-- 15 --', font=fonte, fill=self.coulPolice)
		img17=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img17).text((posXFonte, posYFonte), '-- 16 --', font=fonte, fill=self.coulPolice)
		img18=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img18).text((posXFonte, posYFonte), '-- 17 --', font=fonte, fill=self.coulPolice)
		img19=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img19).text((posXFonte, posYFonte), '-- 18 --', font=fonte, fill=self.coulPolice)
		img20=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img20).text((posXFonte, posYFonte), '-- 19 --', font=fonte, fill=self.coulPolice)
		img21=Image.new('RGB', (self.resLarg, self.resHaut), self.val)
		ImageDraw.Draw(img21).text((posXFonte, posYFonte), '-- 20 --', font=fonte, fill=self.coulPolice)

		# Liste pour affichage des pages sauvegardées (ds le tabwidget)
		listeAff_2=[]
		
		listeOcc=[]
		# Boucle principale
		for images, coorXY in lImCoordFinal:
		
			# Remplissage de la liste pour le calcul du pourcentage
			listeOcc.append(images)
			# Ouverture images
			img1=Image.open(images)
			# Redimensionnement des futures miniatures pour affichage ds la planche
			redim=img1.resize((largMiniature, hautMiniature), Image.ANTIALIAS)
			
			# Conditions d'affichage sur la 1ère page, sauvegarde et affichage
			if (len(listeOcc)*100/nbMax)<=100:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value(), self.spin2valNombres.value())+ext
				img2.paste(redim, coorXY)
				img2.save(self.cheminCourantSauv)
				# Ajout des images par la variable self.cheminCourantSauv dans la liste self.listeImgDestin
				# Cette liste sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(self.cheminCourantSauv)
				# Remplissage de la liste des pages sauvegardées (Info)
				listeAff_2.append(self.cheminCourantSauv)

			# -------------------------------------------------------------
			# Conditions d'affichage sur la 2ème page, sauvegarde et affichage
			elif 101<=(len(listeOcc)*100/nbMax)<=200:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+1, self.spin2valNombres.value())+ext
				img3.paste(redim, coorXY)
				img3.save(self.cheminCourantSauv)
				# Ajout des images par la variable self.cheminCourantSauv dans la liste self.listeImgDestin
				# Cette liste sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(self.cheminCourantSauv)
				# Remplissage de la liste des pages sauvegardées (Info)
				listeAff_2.append(self.cheminCourantSauv)
				
			# Conditions d'affichage sur la 3ème page, sauvegarde et affichage
			elif 201<=(len(listeOcc)*100/nbMax)<=300:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+2, self.spin2valNombres.value())+ext
				img4.paste(redim, coorXY)
				img4.save(self.cheminCourantSauv)
				# Ajout des images par la variable self.cheminCourantSauv dans la liste self.listeImgDestin
				# Cette liste sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(self.cheminCourantSauv)
				# Remplissage de la liste des pages sauvegardées (Info)
				listeAff_2.append(self.cheminCourantSauv)
				
			# ...
			elif 301<=(len(listeOcc)*100/nbMax)<=400:
				# Les commentaires sont retirés à partir de  là
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+3, self.spin2valNombres.value())+ext
				img5.paste(redim, coorXY)
				img5.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 401<=(len(listeOcc)*100/nbMax)<=500:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+4, self.spin2valNombres.value())+ext
				img6.paste(redim, coorXY)
				img6.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 501<=(len(listeOcc)*100/nbMax)<=600:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+5, self.spin2valNombres.value())+ext
				img7.paste(redim, coorXY)
				img7.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 601<=(len(listeOcc)*100/nbMax)<=700:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+6, self.spin2valNombres.value())+ext
				img8.paste(redim, coorXY)
				img8.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 701<=(len(listeOcc)*100/nbMax)<=800:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+7, self.spin2valNombres.value())+ext
				img9.paste(redim, coorXY)
				img9.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)	
				
			elif 801<=(len(listeOcc)*100/nbMax)<=900:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+8, self.spin2valNombres.value())+ext
				img10.paste(redim, coorXY)
				img10.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)	
				
			elif 901<=(len(listeOcc)*100/nbMax)<=1000:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+9, self.spin2valNombres.value())+ext
				img11.paste(redim, coorXY)
				img11.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1001<=(len(listeOcc)*100/nbMax)<=1100:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+10, self.spin2valNombres.value())+ext
				img12.paste(redim, coorXY)
				img12.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1101<=(len(listeOcc)*100/nbMax)<=1200:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+11, self.spin2valNombres.value())+ext
				img13.paste(redim, coorXY)
				img13.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1201<=(len(listeOcc)*100/nbMax)<=1300:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+12, self.spin2valNombres.value())+ext
				img14.paste(redim, coorXY)
				img14.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1301<=(len(listeOcc)*100/nbMax)<=1400:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+13, self.spin2valNombres.value())+ext
				img15.paste(redim, coorXY)
				img15.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1401<=(len(listeOcc)*100/nbMax)<=1500:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+14, self.spin2valNombres.value())+ext
				img16.paste(redim, coorXY)
				img16.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)	
				
			elif 1501<=(len(listeOcc)*100/nbMax)<=1600:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+15, self.spin2valNombres.value())+ext
				img17.paste(redim, coorXY)
				img17.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1601<=(len(listeOcc)*100/nbMax)<=1700:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+16, self.spin2valNombres.value())+ext
				img18.paste(redim, coorXY)
				img18.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1701<=(len(listeOcc)*100/nbMax)<=1800:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+17, self.spin2valNombres.value())+ext
				img19.paste(redim, coorXY)
				img19.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1801<=(len(listeOcc)*100/nbMax)<=1900:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+18, self.spin2valNombres.value())+ext
				img20.paste(redim, coorXY)
				img20.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)
				
			elif 1901<=(len(listeOcc)*100/nbMax)<=2000:
				self.cheminCourantSauv=self.cheminCourantSauv=self.chemDossierSauv+'_'+string.zfill(self.spin1valNombres.value()+19, self.spin2valNombres.value())+ext
				img21.paste(redim, coorXY)
				img21.save(self.cheminCourantSauv)
				self.listeImgDestin.append(self.cheminCourantSauv)
				listeAff_2.append(self.cheminCourantSauv)

			# Elimination des doublons dans la liste (qui peuvent être nombreux)
			self.listeImgDestin=list(set(self.listeImgDestin))
			# Mise en ordre de  la liste
			self.listeImgDestin.sort()
			
			# ================================================================== #
			# Calcule le pourcentage effectue a chaque passage et ce pour la 
			# barre de progression .
			# ---------------------------------------------
			val_pourc=((len(listeOcc)*100)/(nbreImg/self.spin1.value()))
			# Si le pourcentage dépasse les 100% il est remis à 100
			if val_pourc>=100: val_pourc=100
			
			# --------------------------------------------
			# Affichage de la progression (avec
			# QProgressDialog) ds une fenêtre séparée
			self.progress.setValue(val_pourc)
			QApplication.processEvents()
			# Bouton Cancel pour arrêter la progression donc le process
			if (self.progress.wasCanceled()): break
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
		
		# Récupération du chemin + nom des fichiers
		# sauvegardés en ayant éliminé les doublons
		listeAff_2=list(set(listeAff_2))
		listeAff_2.sort()
			
		# Affichage des infos sur l'image -------------------------	
		# On implémente les chemins des fichiers dans une variable
		# pour préparer l'affichage des infos
		texte1=_(u" Image(s) chargée(s)")
		texte2=_(u" Pages des planches-contact sauvegardées")
		a='#'*36
			
		self.infosImgProv_1=a+'\n#'+texte1+'\n'+a
		self.infosImgProv_2=a+'\n#'+texte2+'\n'+a
		
		# Images chargées
		for parcStatRendu_1 in self.listeChemin:
			self.infosImgProv_1=self.infosImgProv_1+'\n'+parcStatRendu_1
			
		# Pages sauvegardées
		for parcStatRendu_2 in listeAff_2:
			self.infosImgProv_2=self.infosImgProv_2+'\n'+parcStatRendu_2
		
		# affichage des infos dans l'onglet
		self.zoneAffichInfosImg.setText(self.infosImgProv_1+'\n\n'+self.infosImgProv_2+'\n\n')
		self.framImg.setEnabled(True)
			
		# remise à 0 de la variable provisoire de log
		self.infosImgProv=''
		# ---------------------------------------------------------

		# Epuration/elimination des fichiers tampon
		for toutRepTemp in glob.glob(self.repTampon+'*.*'):
			os.remove(toutRepTemp)

	
	def sonderTempsActuel(self):
		"""x ms après l'apparition de la boite de dialogue, on lance la conversion. But: faire en sorte que la boite de dialogue ait le temps de s'afficher correctement"""
		self.timer.stop()
		self.appliquer()
	
	
	def appliquer(self):
		"""On lance le type de conversion correspondant aux items sélectionnés des 2 boites de combo """
		# Si on a sélectionné masque alpha et la méthode 1 
		
		self.planche_contact()
		
	
	def appliquer0(self):
		"""Préparation de la conversion"""
		
		# Redimensionner les images de tailles différentes?
		self.redim_img()

		# Récupération de la liste des fichiers chargés
		self.listeChemin=self.afficheurImgSource.getFiles()
		
		# Si la valeur de Passage d'une image à l'autre est supérieure au nbre d'images
		# chargées par l'utilisateur ...
		if self.spin1.value()>len(self.listeChemin):
			self.tabwidget.setCurrentIndex(self.indexTabReglage)
			warn=QMessageBox(self)
			warn.setText(_(u"La valeur de 'Passage d'une image à l'autre' est supérieure au nombre d'images que vous avez chargé, cela ne convient pas (la valeur de 'Passage ...' doit obligatoirement être inférieure au nombre d'images chargées pour que l'opération puisse se poursuivre)"))
			warn.setWindowTitle(_(u"Attention !"))
			warn.setIcon(QMessageBox.Warning)
			warn.exec_()
   			return
		
		# Autrement si tout va bien ...

		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
		suffix=""
                self.chemDossierSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.chemDossierSauv = self.chemDossierSauv.getFile()
		
		if not self.chemDossierSauv: return
		
		self.progress.reset()
		self.progress.show()
		self.progress.setValue(0)
		QApplication.processEvents()
		
		# Lancement de la conversion dans 250 ms (seule solution trouvée pour éviter 
		# le grisage au début)
		self.timer.start(250)

		
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""

		messageAide=EkdAide(parent=self)
		messageAide.setText(_(u"<p><b>Vous pouvez réaliser ici une planche-contact à partir d'un nombre plus ou moins important d'images. D'assez nombreux réglages vous donnent l'opportunité (dans l'onglet 'Mise en page') de présenter et d'orienter votre planche-contact comme bon vous semble.</b></p><p><b>La planche-contact était/est bien souvent utilisée dans le monde de la photographie, par exemple avec les techniques de la photo argentique (la photographie au sens traditionnel du terme, c'est à dire la prise de vue, l'exposition d'une pellicule sensible à la lumière puis son développement et, éventuellement, son tirage sur papier). Dans le domaine de la photographie numérique, la planche-contact peut aussi (sans aucun problème) être utilisée pour voir et présenter un ensemble de clichés (c'est ce que se propose de faire pour vous EKD).</b></p><p><b>Voilà la définition que donne Wikipédia du terme planche-contact (il s'agit là d'une définition faisant référence à la photo argentique): 'Une planche-contact est la représentation de toutes les poses d'un film de la même taille que le négatif.<br>Pour obtenir une planche contact, après avoir développé le film négatif, on va couper le film en plusieurs bandes que l'on aligne ensuite les unes sous les autres sur un papier photosensible. On expose alors le tout, sans insérer le film dans l'appareil.<br>Ce procédé a de particulier qu'il est simple et rapide. Mais surtout, il offre une vue d'ensemble des photos d'un film, ce qui est très pratique.<br>Ainsi, la planche contact offre la possibilité de jeter un rapide coup d'oeil sur les photos d'un film. Ensuite, on peut aller plus avant, et s'intéresser aux images que l'on veut agrandir...'.<br>Source: http://fr.wikipedia.org/wiki/Planche-contact</b></p><p>Dans l'onglet <b>'Images sources'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher votre/vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Dans l'onglet <b>'Autre réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b>.</p><p>Dans l'onglet <b>'Mise en page'</b>, réglez les valeurs qui vous intéressent (vous pouvez voir le nombre maximum d'images affichables en cliquant sur le bouton <b>'Information'</b>). Cliquez sur le bouton <b>'Voir le résultat'</b> (vous voyez à ce moment le résultat de vos réglages sur la première page de la planche-contact s'afficher dans une nouvelle fenêtre).</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer et sauver'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>Image(s) après traitement</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>'Infos'</b> vous permet de voir le filtre utilisé, les image(s) chargée(s) et les image(s) convertie(s).</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'spin1valNombres', unicode(self.spin1valNombres.value()))
		EkdConfig.set(self.idSection, u'spin2valNombres', unicode(self.spin2valNombres.value()))
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2.value()))
		EkdConfig.set(self.idSection, u'spin3', unicode(self.spin3.value()))
		EkdConfig.set(self.idSection, u'spin4', unicode(self.spin4.value()))
		EkdConfig.set(self.idSection, u'format_sortie', unicode(self.comboReglage.currentIndex()))
		EkdConfig.set(self.idSection, u'comboPorPay', unicode(self.comboPorPay.currentIndex()))
		EkdConfig.set(self.idSection, u'comboVal', unicode(self.comboVal.currentIndex()))
		# Ajouté le 12/11/10 #####################################################
		EkdConfig.set(self.idSection, u'comboTailPl', unicode(self.comboTailPl.currentIndex()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.spin1valNombres.setValue(int(EkdConfig.get(self.idSection, 'spin1valNombres')))
		self.spin2valNombres.setValue(int(EkdConfig.get(self.idSection, 'spin2valNombres')))
		self.spin1.setValue(int(EkdConfig.get(self.idSection, 'spin1')))
		self.spin2.setValue(int(EkdConfig.get(self.idSection, 'spin2')))	
		self.spin3.setValue(int(EkdConfig.get(self.idSection, 'spin3')))	
		self.spin4.setValue(int(EkdConfig.get(self.idSection, 'spin4')))	
		self.comboReglage.setCurrentIndex(int(EkdConfig.get(self.idSection, 'format_sortie')))
		self.comboPorPay.setCurrentIndex(int(EkdConfig.get(self.idSection, 'comboPorPay')))
		self.comboVal.setCurrentIndex(int(EkdConfig.get(self.idSection, 'comboVal')))
		# Ajouté le 12/11/10 #####################################################
		self.comboTailPl.setCurrentIndex(int(EkdConfig.get(self.idSection, 'comboTailPl')))
		

