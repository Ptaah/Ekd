#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, glob, string, shutil, Image, ImageChops, ImageDraw, ImageFilter, time
from math import pi
from numpy import *
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


try: 
	# Importation de Psyco s'il est installé
	import psycho
	psycho.full()
except ImportError:
	pass


class Camembert(QWidget):
	"Camembert de couleur"
	def __init__(self, rayon=100):
		QWidget.__init__(self)
		self.rayon = rayon
		# Bornes des teintes de couleur sélectionnées
		self.startColor = 0
		self.endColor = 360
		self.font = QFont(self.font())
		self.font.setPointSize(8)

	def sizeHint(self):
		#return QSize(2*self.rayon+10, 2*self.rayon+15)
		return QSize(2.5*self.rayon+10, 2.5*self.rayon+15)

	def minimumSizeHint(self):
        	#return QSize(2*self.rayon+10, 2*self.rayon+15)
		return QSize(2.5*self.rayon+10, 2.5*self.rayon+15)

	def setColors(self, startColor=0, endColor=360):
		"Sélection des couleurs de début et de fin"
		self.startColor = min(startColor, endColor)
		self.endColor = max(startColor, endColor)
		self.repaint()

	def paintEvent(self, event):
		"Traçage du camembert de couleur"
		painter = QPainter()
		painter.begin(self)
		painter.setRenderHint(QPainter.Antialiasing)
		# Pour que les axes et le texte ne soient pas tronqués
		painter.translate(10, 10)
		gradient = QConicalGradient(self.rayon, self.rayon, 0)
		color = [Qt.red, Qt.yellow, Qt.green, Qt.cyan, Qt.blue, Qt.magenta, Qt.red]
		for i in range(7):
			gradient.setColorAt(i/6., color[i])
		painter.setBrush(gradient)
		painter.setPen(Qt.NoPen)
		rect = QRect(0, 0, 2*self.rayon, 2*self.rayon)
		# Tracé du disque
		painter.drawEllipse(rect)
		painter.setPen(QPen(QColor(120, 120, 120), 1, Qt.DashLine))
		r = self.rayon
		# Pour que les axes et le texte sortent du disque
		coeff = 1.1
		painter.setFont(self.font)
		# Traçage des axes et des coordonnées
		for i in range(6):
			angle = i*pi/3 - pi/2
			if angle < 1.01*pi:
				# Coordonnées polaires
				painter.drawLine(coeff * r * sin(angle) + r, coeff * r * cos(angle) + r,
					coeff * -r * sin(angle) + r, coeff * -r * cos(angle) + r)
			painter.drawText(coeff * -r * sin(angle) + r, coeff * -r * cos(angle) + r, str(i*60))
		painter.setPen(QPen(QColor(10, 10, 10), 2, Qt.SolidLine))
		painter.setBrush(QBrush(Qt.NoBrush))
		# Sélection d'une plage de couleur
		painter.drawPie(rect, 16 * self.startColor, 16 * abs(self.endColor - self.startColor))
		painter.end()


class SaturValeur(QLabel):
	"""Rectangle de saturation-valeur
	Saturation en hauteur. Valeur en largeur.
	On utilise un QLabel pour y ajouter une image. L'image permet l'utilisation du mode Multiply.
	Ce mode est nécessaire à l'application du dégradé «valeur» (du noir au blanc),
	une fois que le dégradé «saturation» (de la "couleur pure" au blanc) a été appliqué en
	mode normal"""
	def __init__(self, taille=(125, 125), teinte=120, saturation=(0, 100), valeur=(0, 100)):
		QLabel.__init__(self)
		self.taille = taille
		self.teinte = teinte
		self.startSatur = saturation[0]
		self.endSatur = saturation[1]
		self.startValeur = valeur[0]
		self.endValeur = valeur[1]
		# Bornes des saturation sélectionnées
		self.startSatur = 0
		self.endSatur = 100
		self.update()

	def sizeHint(self):
		return QSize(self.taille[0], self.taille[1])

	def minimumSizeHint(self):
        	return QSize(self.taille[0], self.taille[1])

	def setTeinte(self, teinte):
		"Sélection de la teinte"
		self.teinte = teinte
		self.update()

	def setTeinteSaturValeur(self, teinte=120, saturation=(0, 100), valeur=(0, 100)):
		"Sélection des saturations et des valeurs"
		self.teinte = teinte
		self.startSatur = min(saturation[0], saturation[1])
		self.endSatur = max(saturation[0], saturation[1])
		self.startValeur = min(valeur[0], valeur[1])
		self.endValeur = max(valeur[0], valeur[1])
		self.update()

	def setSatur(self, startSatur=0, endSatur=100):
		"Sélection des saturations de début et de fin"
		self.startSatur = min(startSatur, endSatur)
		self.endSatur = max(startSatur, endSatur)
		self.update()

	def setValeur(self, startValeur=0, endValeur=100):
		"Sélection des valeurs de début et de fin"
		self.startValeur = min(startValeur, endValeur)
		self.endValeur = max(startValeur, endValeur)
		self.update()

	def update(self):
		"""Traçage du rectangle de saturation-valeur"""
		
		painter = QPainter()
		img = QImage(self.taille[0], self.taille[1], QImage.Format_ARGB32)
		painter.begin(img)
		# painter.setRenderHint(QPainter.Antialiasing)
		if self.teinte == 360:
			teinte = 0
		else:
			teinte = self.teinte/360.
		rect = QRect(0, 0, self.taille[0], self.taille[1])
		#=== Gradient de saturation en hauteur ===#
		painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
		gradient = QLinearGradient(0, 0, 0, self.taille[1])
		startColor, endColor = QColor(), QColor()
		startColor.setHsvF(teinte, 1., 1.)
		endColor.setHsvF(teinte, 0., 1.)
		gradient.setColorAt(0.0, startColor)
		gradient.setColorAt(1.0, endColor)
		painter.setBrush(gradient)
		painter.setPen(Qt.NoPen)
		# Traçage de la bande
		painter.drawRect(rect)
		#=== Gradient de valeur en largeur ===#
		painter.setCompositionMode(QPainter.CompositionMode_Multiply)
		gradient = QLinearGradient(0, 0, self.taille[0], 0)
		startColor, endColor = QColor(0, 0, 0), QColor(255, 255, 255)
		gradient.setColorAt(0.0, startColor)
		gradient.setColorAt(1.0, endColor)
		painter.setBrush(gradient)
		painter.drawRect(rect)
		#=== Rectangle délimitant le domaine de saturation-valeur ===#
		painter.setPen(QPen(QColor(120, 120, 120), 2, Qt.SolidLine))
		xa = self.startValeur / 100. * self.taille[0]
		xb = self.endValeur / 100. * self.taille[0]
		ya = self.taille[1] - self.startSatur / 100. * self.taille[1]
		yb = self.taille[1] - self.endSatur / 100. * self.taille[1]
		painter.drawLine(xa, 0, xa, self.taille[1])
		painter.drawLine(xb, 0, xb, self.taille[1])
		painter.drawLine(0, ya, self.taille[0], ya)
		painter.drawLine(0, yb, self.taille[0], yb)
		painter.end()
		self.setPixmap(QPixmap.fromImage(img))


class Image_MasqueAlpha3D(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Masque alpha/3D
	# -----------------------------------
	def __init__(self, statusBar, geometry):
        	QWidget.__init__(self)
		
		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------
		#=== tout sera mis dans une boîte verticale ===#
		vbox=QVBoxLayout(self)
		
		# Création des répertoires temporaires

		# Gestion du repertoire tmp avec EkdConfig 
		self.repTampon = EkdConfig.getTempDir() + os.sep +'tampon' + os.sep + 'temp_image_masque_alpha_3d' + os.sep
		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)
		
		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			os.remove(toutRepCompo)
		
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
		self.idSection = "image_masque_alpha_3d"
		# Log du terminal
		self.base.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		self.listeImgSource = []
		self.listeImgDestin = []
		
		#-------------------------------------------------
		# Sélection images, type de méthode et de masque
		#-------------------------------------------------
		
		grid = QGridLayout()
		grid.addWidget(QLabel(_(u"Méthode :")), 0, 0)
		
		# Boite de combo
		self.comboMethode=QComboBox()
		listeCombo=[	(_(u'Méthode 1') ,'methode1'),\
				(_(u'Méthode 2') ,'methode2')]
		
		# Insertion des codecs de compression dans la combo box
		for i in listeCombo:
                	self.comboMethode.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboMethode, SIGNAL("currentIndexChanged(int)"), self.changerComboMethode)
		
		grid.addWidget(self.comboMethode, 0, 1)
		
		grid.addWidget(QLabel(_(u"Type de masque :")), 1, 0)
		
		# Boite de combo pour le choix du masque
		self.comboMasque=QComboBox()
		listeCombo=[	(_(u'Masque alpha') ,'masque_alpha'),\
				(_(u'Masque 3D') ,'masque_3D')]
		
		# Insertion des codecs de compression dans la combo box
		for i in listeCombo:
                	self.comboMasque.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboMasque, SIGNAL("currentIndexChanged(int)"), self.changerComboMasque)
		
		grid.addWidget(self.comboMasque, 1, 1)
		
		grid.setAlignment(Qt.AlignHCenter)
		vbox.addLayout(grid)
		
		#------------------------
		# Onglets et stacked
		#------------------------
		self.tabwidget=QTabWidget()
		
		#=== 1er onglet ===#
		self.framReglage=QFrame()
		vboxInfIm=QVBoxLayout(self.framReglage)
		
		# Boite de combo
		self.comboReglage=QComboBox()
		listeCombo=[	(_(u'Personnalisé') ,'personnalise'),\
				(_(u'Fond Bleu') ,'fond_bleu'),\
				(_(u'Fond Vert') ,'fond_vert')]
		# Insertion des codecs de compression dans la combo box
		for i in listeCombo:
                	self.comboReglage.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		
		# Boite de combo pour Qualité 
		self.comboQualite=QComboBox() 
		listeComboQual=[	(_(u'Moyenne') ,'moyenne'),\
					(_(u'Bonne') ,'bonne'),\
					(_(u'Très bonne') ,'tres_bonne'),\
					(_(u'Excellente') ,'excellente')] 
		# Insertion des codecs de compression dans la combo box
		for i in listeComboQual:
                	self.comboQualite.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboQualite, SIGNAL("currentIndexChanged(int)"), self.changerComboQualite)
		
		# Boite de combo pour la netteté masque alpha méthode 2
		self.comboNettete=QComboBox() 
		listecomboNettete=[	(_(u"Par défaut") ,'par_defaut'),\
					(_(u'Formes plus nettes') ,'formes_nettes')]
		# Insertion des codecs de compression dans la combo box
		for i in listecomboNettete:
                	self.comboNettete.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboNettete, SIGNAL("currentIndexChanged(int)"), self.changerNettete)
		
		# Boite de combo pour pixels noirs ou blancs masque 3D méthode 2
		self.comboFondForme=QComboBox() 
		listeComboFondForme=[	(_(u'Fond noir forme(s) blanche(s)') ,'fon_noir_for_blanch'),\
					(_(u'Fond blanc forme(s) noire(s)') ,'fon_blanc_for_noir')]
		# Insertion des codecs de compression dans la combo box
		for i in listeComboFondForme:
                	self.comboFondForme.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboFondForme, SIGNAL("currentIndexChanged(int)"), self.changerFondForme)
		
		hbox = QHBoxLayout()
		hbox.addWidget(QLabel(_(u'Type de fond uni :')))
		hbox.addWidget(self.comboReglage)
		hbox.setAlignment(Qt.AlignHCenter)
		
		grid = QGridLayout()
		grid.addWidget(QLabel(_(u"Teinte (début) :")), 0, 0)
		self.spinTeinteDebut = SpinSlider(0,360,0) # Degrés de 0 à 360
		grid.addWidget(self.spinTeinteDebut, 0, 1)
		grid.addWidget(QLabel(_(u"Teinte (fin) :")), 0, 2)
		self.spinTeinteFin = SpinSlider(0,360,360)
		grid.addWidget(self.spinTeinteFin, 0, 3)
		grid.addWidget(QLabel(_(u"Saturation (début) :")), 1, 0)
		self.spinSaturationDebut = SpinSlider(0,100,0)
		grid.addWidget(self.spinSaturationDebut, 1, 1)
		grid.addWidget(QLabel(_(u"Saturation (fin) :")), 1, 2)
		self.spinSaturationFin = SpinSlider(0,100,100)
		grid.addWidget(self.spinSaturationFin, 1, 3)
		grid.addWidget(QLabel(_(u"Luminosité (début) :")), 2, 0)
		self.spinLuminosite = SpinSlider(0,100,0)
		grid.addWidget(self.spinLuminosite, 2, 1)
		# ---------

		grid.setAlignment(Qt.AlignHCenter)
		
		# -----------------
		grid2 = QGridLayout()
		
		self.labelFondForme=QLabel(_(u"Choix du fond et de la forme :"))
		
		i = self.comboMasque.currentIndex()
		idCombo=str(self.comboMasque.itemData(i).toStringList()[0])
		if idCombo=='masque_alpha':
			self.labelFondForme.hide()
			self.comboFondForme.hide()
		grid2.addWidget(self.labelFondForme, 0, 0)
		grid2.addWidget(self.comboFondForme, 0, 1)
		
		self.labelQualite=QLabel(_(u"Qualité :"))
		
		i = self.comboMethode.currentIndex()
		idCombo=str(self.comboMethode.itemData(i).toStringList()[0])
		if idCombo=='methode1':
			self.labelQualite.hide()
			self.comboQualite.hide()
		grid2.addWidget(self.labelQualite, 1, 0)
		grid2.addWidget(self.comboQualite, 1, 1)
		
		self.labelNettete=QLabel(_(u"Choix de la netteté :"))

		i = self.comboMethode.currentIndex()
		idCombo=str(self.comboMethode.itemData(i).toStringList()[0])
		if idCombo=='methode1':
			self.labelNettete.show()
			self.comboNettete.show()
		grid2.addWidget(self.labelNettete, 2, 0)
		grid2.addWidget(self.comboNettete, 2, 1)
		
		grid2.setAlignment(Qt.AlignHCenter)
		
		# -----------------
		
		hboxApercus = QHBoxLayout()
		# Au départ: self.camembert = Camembert(100)
		self.camembert = Camembert(94)
		self.camembert.setColors(self.spinTeinteDebut.value(), self.spinTeinteFin.value())
		self.connect(self.spinTeinteDebut, SIGNAL("valueChanged(int)"), self.teinteChange)
		self.connect(self.spinTeinteFin, SIGNAL("valueChanged(int)"), self.teinteChange)
		hboxApercus.addWidget(self.camembert, 1)
		
		# Au départ: 
		# self.saturValeur1 = SaturValeur((125,125), ...)
		# self.saturValeur2 = SaturValeur((125,125), ...)
		self.saturValeur1 = SaturValeur((180,180), self.spinTeinteDebut.value(),
			(self.spinSaturationDebut.value(), self.spinSaturationFin.value()),
			(self.spinLuminosite.value(), 100))
		self.saturValeur2 = SaturValeur((180,180), self.spinTeinteFin.value(),
			(self.spinSaturationDebut.value(), self.spinSaturationFin.value()),
			(self.spinLuminosite.value(), 100))
		
		self.connect(self.spinSaturationDebut, SIGNAL("valueChanged(int)"), self.saturValeurChange)
		self.connect(self.spinSaturationFin, SIGNAL("valueChanged(int)"), self.saturValeurChange)
		self.connect(self.spinLuminosite, SIGNAL("valueChanged(int)"), self.saturValeurChange)
		hboxApercus.addWidget(self.saturValeur1, 0, Qt.AlignRight)
		hboxApercus.addWidget(self.saturValeur2, 0, Qt.AlignRight)
		
		# -----------------
		
		vboxInfIm.addLayout(hbox)
		vboxInfIm.addSpacing(10)
		vboxInfIm.addLayout(grid)
		vboxInfIm.addLayout(grid2)
		vboxInfIm.addStretch()
		vboxInfIm.addLayout(hboxApercus)
		
		# Gestion du nombre d'images à traiter
		#=== onglet supplémentaire ===#
		self.framNbreImg=QFrame()
		vboxReglage=QVBoxLayout(self.framNbreImg)
		
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
		
		#=== 2ème onglet ===#
		# infos - logs
		self.zoneAffichInfosImg = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneAffichInfosImg.setText = self.zoneAffichInfosImg.setPlainText
		self.zoneAffichInfosImg.setReadOnly(True)
		self.framImg=QFrame()
		vboxInfIm=QVBoxLayout(self.framImg)
		vboxInfIm.addWidget(self.zoneAffichInfosImg)
		self.framImg.setEnabled(False)

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
		self.indexTabReglage=self.tabwidget.addTab(self.framReglage, _(u'Réglages du masque'))
		# Onglet de la gestion du nombre d'images à traiter
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
		
		# boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones/icone_aide_128.png"))
		boutAide.setFocusPolicy(Qt.NoFocus)
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)

		self.boutReglage = QPushButton(_(u" Voir le résultat"))
		self.boutReglage.setIcon(QIcon("Icones/icone_visionner_128.png"))
		self.boutReglage.setFocusPolicy(Qt.NoFocus)
		self.boutReglage.setEnabled(False)
		self.connect(self.boutReglage, SIGNAL("clicked()"), self.apercuReglages)
		
		self.boutApp=QPushButton(_(u" Appliquer"))
		self.boutApp.setIcon(QIcon("Icones/icone_appliquer_128.png"))
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
		hbox.addWidget(self.boutReglage)
		hbox.addStretch()
		hbox.addWidget(self.boutApp)
		vbox.addLayout(hbox)
		
		self.setLayout(vbox)
		
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		self.base.valeurComboIni(self.comboMethode, self.config, self.idSection, 'methode')
		self.base.valeurComboIni(self.comboMasque, self.config, self.idSection, 'masque')
		self.base.valeurComboIni(self.comboReglage, self.config, self.idSection, 'reglage')
		self.base.valeurComboIni(self.comboQualite, self.config, self.idSection, 'qualite')
		self.base.valeurComboIni(self.comboNettete, self.config, self.idSection, 'nettete')
		self.base.valeurComboIni(self.comboFondForme, self.config, self.idSection, 'forme_fond')
		
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
		self.boutReglage.setEnabled(i)
		self.modifImageSource = 1
		# Mise à jour de l'aperçu
		
		
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
	
	
	def teinteChange(self, i):
		"Change la teinte du début sur le camembert de couleur"
		self.camembert.setColors(self.spinTeinteDebut.value(), self.spinTeinteFin.value())
		self.saturValeurChange()
	
	def saturValeurChange(self, i=None):
		"Change la saturation et la luminosité sur les rectangles d'aperçus"
		sat1, sat2 = self.spinSaturationDebut.value(), self.spinSaturationFin.value()
		val1, val2 = self.spinLuminosite.value(), 100
		teinte1, teinte2 = self.spinTeinteDebut.value(), self.spinTeinteFin.value()
		self.saturValeur1.setTeinteSaturValeur(teinte1, (sat1, sat2), (val1, val2))
		self.saturValeur2.setTeinteSaturValeur(teinte2, (sat1, sat2), (val1, val2))
	
	def changerComboMethode(self, i):
		""" Conditions de disparition/réapparition des labels self.labelQualite, self.labelNettete et combos self.comboQualite, self.comboNettete """
		idCombo=str(self.comboMethode.itemData(i).toStringList()[0])
		
		if idCombo=='methode1':
			self.labelQualite.hide()
			self.comboQualite.hide()
			if self.comboMasque.currentIndex()==0:
				self.labelNettete.show()
				self.comboNettete.show()
			else:
				self.labelNettete.hide()
				self.comboNettete.hide()
		elif idCombo=='methode2':
			self.labelQualite.show()
			self.comboQualite.show()
			self.labelNettete.hide()
			self.comboNettete.hide()
		self.config.set(self.idSection, 'methode', idCombo)
	
	
	def changerComboMasque(self, i):
		""" Conditions de disparition/réapparition des labels self.labelFondForme, self.labelNettete et combos self.comboFondForme, self.comboNettete """
		idCombo=str(self.comboMasque.itemData(i).toStringList()[0])

		if idCombo=='masque_alpha':
			self.labelFondForme.hide()
			self.comboFondForme.hide()
			self.labelNettete.hide()
			self.comboNettete.hide()
			if self.comboMethode.currentIndex()==0:
				self.labelNettete.show()
				self.comboNettete.show()
			else:
				self.labelNettete.hide()
				self.comboNettete.hide()
		elif idCombo=='masque_3D':
			self.labelFondForme.show()
			self.comboFondForme.show()
			self.labelNettete.hide()
			self.comboNettete.hide()
		
		self.config.set(self.idSection, 'masque', idCombo)
	
	
	def changerComboQualite(self, i):
		"""Grisage/dégrisage du combo 'qualité' quand l'entrée de la boite de combo de méthode change (non grisé quand méthode 2 est sélectionné) ... humhum récup de l'index de self.comboQualite. Bon c'est pas terrible mon histoire là. Ya certainement moyen de faire mieux !"""
		#print self.comboQualite.currentIndex()
		EkdPrint(u"%s" % str(self.comboQualite.currentIndex()))
		idCombo=str(self.comboQualite.itemData(i).toString())
		self.config.set(self.idSection, 'qualite', idCombo)
		'''
		idCombo=str(self.comboMethode.itemData(i).toStringList()[0])
		if idCombo=='methode1':
			self.comboQualite.setEnabled(False)
		elif idCombo=='methode2':
			self.comboQualite.setEnabled(True)
		'''
		
		
	def changerFondForme(self, i):
		"""Grisage/dégrisage du combo 'qualité' quand l'entrée de la boite de combo de méthode change (non grisé quand méthode 2 est sélectionné) ... humhum récup de l'index de self.comboQualite. Bon c'est pas terrible mon histoire là. Ya certainement moyen de faire mieux !"""
		#print self.comboFondForme.currentIndex()
		EkdPrint(u"%s" % str(self.comboFondForme.currentIndex()))
		idCombo=str(self.comboFondForme.itemData(i).toString())
		self.config.set(self.idSection, 'forme_fond', idCombo)
		'''
		idCombo=str(self.comboMethode.itemData(i).toStringList()[0])
		if idCombo=='methode1':
			self.comboQualite.setEnabled(False)
		elif idCombo=='methode2':
			self.comboQualite.setEnabled(True)
		'''
		
		
	def changerNettete(self, i):
		"""Grisage/dégrisage du combo 'qualité' quand l'entrée de la boite de combo de méthode change (non grisé quand méthode 2 est sélectionné) ... humhum récup de l'index de self.comboQualite. Bon c'est pas terrible mon histoire là. Ya certainement moyen de faire mieux !"""
		#print self.comboNettete.currentIndex()
		EkdPrint(u"%s" % str(self.comboNettete.currentIndex()))
		idCombo=str(self.comboNettete.itemData(i).toString())
		self.config.set(self.idSection, 'nettete', idCombo)
		'''
		idCombo=str(self.comboMethode.itemData(i).toStringList()[0])
		if idCombo=='methode1':
			self.comboQualite.setEnabled(False)
		elif idCombo=='methode2':
			self.comboQualite.setEnabled(True)
		'''
	
	
	def changerComboReglage(self, i):
		"""Modification des valeurs des spins de la boite de réglage quand l'entrée de la boite de combo de réglage change"""
		idCombo=str(self.comboReglage.itemData(i).toString())
		# Si c'est une image avec fond autre que bleu ou vert ...
		if idCombo=='personnalise':
			#print 'Vous avez chargé une image avec fond autre que bleu ou vert'
			EkdPrint(u'Vous avez chargé une image avec fond autre que bleu ou vert')
			# Teinte (début)
			self.spinTeinteDebut.setValue(0)
			# Teinte (début)
			self.spinTeinteFin.setValue(360)
			# Saturation (début)
			self.spinSaturationDebut.setValue(0)
			# Saturation (fin)
			self.spinSaturationFin.setValue(100)
			# Luminosité
			self.spinLuminosite.setValue(0)
		# Si c'est une image avec fond bleu ...
		elif idCombo=='fond_bleu':
			#print 'Vous avez chargé une image avec fond bleu'
			EkdPrint(u'Vous avez chargé une image avec fond bleu')
			# Teinte (début)
			self.spinTeinteDebut.setValue(176)
			# Teinte (début)
			self.spinTeinteFin.setValue(298)
			# Saturation (début)
			self.spinSaturationDebut.setValue(16)
			# Saturation (fin)
			self.spinSaturationFin.setValue(100)
			# Luminosité
			self.spinLuminosite.setValue(39)
		# Si c'est une image avec fond vert ...
		elif idCombo=='fond_vert':
			#print 'Vous avez chargé une image avec fond vert'
			EkdPrint(u'Vous avez chargé une image avec fond vert')
			# Teinte (début)
			self.spinTeinteDebut.setValue(76)
			# Teinte (début)
			self.spinTeinteFin.setValue(175)
			# Saturation (début)
			self.spinSaturationDebut.setValue(25)
			# Saturation (fin)
			self.spinSaturationFin.setValue(100)
			# Luminosité
			self.spinLuminosite.setValue(22)
		self.config.set(self.idSection, 'reglage', idCombo)
	
	
	def operationReussie(self):
		""" Boîte de d'avertissement réussite """
		
		message=QMessageBox(self)
		message.setText(_(u"Rendu terminé !"))
		message.setWindowTitle(_(u"EnKoDeur-Mixeur"))
		message.setIcon(QMessageBox.Information)
		message.exec_()
		
	
	def messageErreur(self):
		""" Boîte d'avertissement si erreur """
		
		erreur=QMessageBox(self)
		erreur.setText(_(u"Il s'est produit une erreur !"))
		erreur.setWindowTitle(_(u"Erreur"))
		erreur.setIcon(QMessageBox.Critical)
		erreur.exec_()	


	def meth_1_ReglagPrevis(self):
		""" Réglage des différents paramètres et prévisualisation pour la méthode 1 """

		try :

			# Récupération du fichier sélectionné par l'utilisateur (si pas de fichier
			# sélectionné par l'utilisateur, la 1ère image de la liste est prise)
			file = self.afficheurImgSource.getFile()
			if not file: return
			self.listeChemin = [file]
			
			# Compteur départ pour le temps de rendu
			t0=time.time()
			
			# Liste pour affichage image découpée (ds le tabwidget)
			listeAff_1=[]
			
			# Ouverture de la 1ère image du lot pour résultat 
			# des réglages et prévisualisation
			imageDepart=Image.open(self.listeChemin[0])
			
			# On recupere la taille de l'image
			widthDepart, heightDepart=imageDepart.size

			# On recupere le nombre de pixels totaux
			nbPixelsTotal=widthDepart*heightDepart
			
			#print 'Nbre total de pixels', nbPixelsTotal
			EkdPrint(u'Nbre total de pixels %s' % nbPixelsTotal)
		
			# On recupere le tableau de pixels
			imageData=imageDepart.getdata()

			#-------------------------------------------------------
			# Algorithme de detection du fond uni bleu/vert ou autre
			#-------------------------------------------------------	
	
			# On boucle sur l'image RVB -> on cree une nouvelle image RVBA, le fond 
			# bleu/vert est supprime . De plus on va stocker les pixels de bord .
			newImageRGBA=[]

			for parcRGB_1 in range(nbPixelsTotal) :
				
    				# On recupere les valeurs R,G et B
				val_R_rgb=imageData[parcRGB_1][0]
    				val_G_rgb=imageData[parcRGB_1][1]
    				val_B_rgb=imageData[parcRGB_1][2]
				
				"""
				# --------------------------------------------------------
				# Utilisation de la syntaxe PyQt4. Le code est plus concis
				# mais gros problème le traitement est beaucoup plus long
				# que l'algo en dessous (pour une image en 800 x 600 avec 
				# fond uni bleu, avec la syntaxe PyQt4 --> 1 mn 05 sec, avec
				# l'algo --> 45 secondes
				# --------------------------------------------------------
				# Conversion des couleurs en couleurs Qt
				couleurQt=QColor(val_R_rgb, val_G_rgb, val_B_rgb)

				# Calcul des valeurs HSV
				h_HSV=couleurQt.toHsv().hue()
				s_HSV=couleurQt.toHsv().saturation()
				v_HSV=couleurQt.toHsv().value()
				
				# On teste si le pixel appartient au fond ou non
    				if self.spinTeinteDebut.value()<=h_HSV<=self.spinTeinteFin.value() and self.spinSaturationDebut.value()<=s_HSV<=self.spinSaturationFin.value() and self.spinLuminosite.value()<=v_HSV<=256:
        				# Si oui, on affecte du noir (0, 0, 0, a) et de la 
					# transparence (a=0) au pixel
        				newImageRGBA.append((0, 0, 0, 0))
    				else :
        				# Si non, on conserve la valeur RVB avec une 
					# transparence a 100%, c'est à dire complètement opaque
					newImageRGBA.append((val_R_rgb, val_G_rgb, val_B_rgb, 255))
				"""
				
    				# ------------------------------- #
    				# On calcule les valeurs de H,S,V #
    				# ------------------------------- #
    				# On detecte le max et le min
    				maxRGB=float(max(imageData[parcRGB_1]))
    				minRGB=float(min(imageData[parcRGB_1]))
    				# Calcule de la difference entre min et max
    				deltaRGB=maxRGB-minRGB
    				# Calcul de la Saturation
    				if maxRGB>0: s_HSV=(deltaRGB/maxRGB)*100
    				else: s_HSV=0
    				# Calcul de Hue (Teinte)
    				if deltaRGB==0: h_HSV=-1
    				elif val_R_rgb==maxRGB: h_HSV=(val_G_rgb-val_B_rgb)/deltaRGB
    				elif val_G_rgb==maxRGB: h_HSV=2+(val_B_rgb-val_R_rgb)/deltaRGB
    				else: h_HSV=4+(val_R_rgb-val_G_rgb)/deltaRGB
				# Conversion en degres de Hue
    				h_HSV=h_HSV*60
    				if h_HSV<0: h_HSV=h_HSV+360
    				# Calcul de Value (Luminosite)
    				v_HSV=maxRGB
				# Pourcentage de 0 à 100 de Value (il est beaucoup plus
				# pratique de travailler avec une valeur entre 0 et 100)
				v_HSV=v_HSV*100/256 
    		
				# On teste si le pixel appartient au fond ou non
    				if self.spinTeinteDebut.value()<=h_HSV<=self.spinTeinteFin.value() and self.spinSaturationDebut.value()<=s_HSV<=self.spinSaturationFin.value() and self.spinLuminosite.value()<=v_HSV<=100:
        				# Si oui, on affecte du noir et de la transparence 
					# (A=0) au pixel
        				newImageRGBA.append((0, 0, 0, 0))
    				else :
        				# Si non, on conserve la valeur RVB avec une 
					# transparence a 100%, c'est à dire complètement opaque
        				newImageRGBA.append((val_R_rgb, val_G_rgb, val_B_rgb, 255))
			
			#-----------------------------------------------------
			# Fin algo de detection du fond uni bleu/vert ou autre
			#-----------------------------------------------------
			
			# On sauvegarde l'image avant anti-aliasing
			imgDecoup=Image.new('RGBA', imageDepart.size)
			imgDecoup.putdata(newImageRGBA)
			
			# Ouverture de l'image avec le fond en damier (avec EKD marque en bas a droite)
			imQuad=Image.open("gui_modules_lecture"+os.sep+"affichage_image"+os.sep+"ekd_quadrillage_canal_alpha.png")
			# Redimensionnement de l'image du damier (quadrillage) aux dimensions de la
			# premiere image chargee .
			RedimQuad=imQuad.resize(imageDepart.size, Image.ANTIALIAS)
			
			# Copie de l'image quadrillage dans le répertoire tampon
			shutil.copy('gui_modules_lecture'+os.sep+'affichage_image'+os.sep+'ekd_quadrillage_canal_alpha.png', self.repTampon)
		
			# On libère de la memoire
			del imageData
			
			#---------------------------------------------------------------------------
			# On supprimme la premiere ligne bleue (si fond bleu) 
			# restante autour du personnage. Début d'anti-aliasing
			antialiasing=[]

			for parcSupprimeLigne in range(nbPixelsTotal):
    			# Si le pixel detecte n'est pas transparent
				if newImageRGBA[parcSupprimeLigne][3]>0 :
					y_ligne=math.ceil((parcSupprimeLigne-1)/widthDepart)
        				x_ligne=parcSupprimeLigne-(y_ligne*widthDepart)
        				# Detection des bords
        				if (x_ligne==0 or x_ligne>=widthDepart-1 or y_ligne==0 or y_ligne>=heightDepart-1) :
						antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
        				else :
            					# Si on a 1 voisin transparent bord
            					# Sinon -> pas bord
            					# On teste (x-1,y),(x+1,y),(x,y-1),(x,y+1)
						if (newImageRGBA[parcSupprimeLigne-1][3]==0 or newImageRGBA[parcSupprimeLigne+1][3]==0 or newImageRGBA[parcSupprimeLigne-widthDepart][3]==0 or newImageRGBA[parcSupprimeLigne+widthDepart][3]==0) :
                					# Si bord existe -> on efface . Le bord en 
							# question est transforme en R, G, B --> 
							# noir et A --> transparent .
							antialiasing.append((0, 0, 0, 0))
						else :
							antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
    				else :
        				antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], 0))

			newImageRGBA=antialiasing
			#---------------------------------------------------------------------------

			# Creation d'une nouvelle image et integration des donnees recoltees .
			newImageAntialias=Image.new('RGBA', imgDecoup.size)
			newImageAntialias.putdata(antialiasing)
			a1, a2, a3, a4=newImageAntialias.split()
			imgMerge=Image.merge('RGBA', (a1, a2, a3, a4))
			# Sauvegarde de la nouvelle image (image tampon)
			imgMerge.save(self.repTampon+'decoupe_fond_tmp58g7e1gdf4g.png', 'PNG')
			
			# Condition (au choix de l'utilisateur) de réglage du combo de netteté 
			if self.comboNettete.currentIndex()==0:
				pass
			else:
				# Ouverture de l'image pour application du kernel (matrice)
				imk=Image.open(self.repTampon+'decoupe_fond_tmp58g7e1gdf4g.png')
				# Kernel 3x3 pour amélioration des bords. L'image devient plus nette.
				sizeKern3x3=(3, 3)
				# Matrice trouvee ici:
				# http://blogs.codes-sources.com/tkfe/archive/2005/04/15/6004.aspx
				kernAmBords=(-1, -2, -1, -2, 16, -2, -1, -2, -1)
				# Application de la matrice
				imKernelAmBords=imk.filter(ImageFilter.Kernel(sizeKern3x3, kernAmBords)).save(self.repTampon+'decoupe_fond_tmp58g7e1gdf4g.png', 'PNG')
			
			# Ouverture de l'image pour application du kernel (matrice)
			ouvIm=Image.open(self.repTampon+'decoupe_fond_tmp58g7e1gdf4g.png')
				
			# Kernel 3x3 anti-crénelage
			sizeKern3x3=(3, 3)
			# Type de kernel utilisé
			kernAntiAlias=(1, 2, 3, 4, 5, 6, 7, 8, 9)
			# Application d'un anti-aliasing sur l'image (et donc sur les contours) par cette matrice.
			# Cette excellente matrice a été trouvée ici: http://www.photo-lovers.org/mosaic.shtml.fr
			# (voir à partir de Méthode du vecteur médian)
			ouvIm.filter(ImageFilter.Kernel(sizeKern3x3, kernAntiAlias)).save(self.repTampon+'decoupe_fond_tmp58g7e1gdf4g.png', 'PNG')
			
			imgFinal=Image.open(self.repTampon+'decoupe_fond_tmp58g7e1gdf4g.png')
		
			# Compositing entre l'image avec le damier et l'image du fond vert/bleu decoupe
			ImageChops.composite(imgFinal, RedimQuad, imgFinal).save(self.repTampon+'aff_decoup_fond__tmp58g7y411eeya7.png', 'PNG')
			
			# Remplissage de listeAff_1 pour affichage (ds le tabwidget)
			listeAff_1.append(self.repTampon+'aff_decoup_fond__tmp58g7y411eeya7.png')
			
			# On libere la memoire
			del antialiasing, newImageRGBA, imQuad, RedimQuad, newImageAntialias, imgDecoup, val_R_rgb, val_G_rgb, val_B_rgb, h_HSV, s_HSV, v_HSV, parcRGB_1, parcSupprimeLigne, a1, a2, a3, a4, imageDepart
			# x_ligne et y_ligne ne sont pas libérés car cela peut produire une erreur ds 
			# certaines circonstances
			
			# --------------------------------------------------------------------
			# CALCUL ET AFFICHAGE DE LA DATE ET DU TEMPS DE RENDU
			# --------------------------------------------------------------------
			# Temps local (annee, mois, jour, heure, minute, seconde ...)
			tLocal=time.localtime()
			# Pour affichage de facon comprehensible de la date et l'heure
			datHeurEcr=_(u"Le ")+str(tLocal[2])+"/"+str(tLocal[1])+"/"+str(tLocal[0])+_(u" a ")+str(tLocal[3])+":"+str(tLocal[4])+":"+str(tLocal[5])
			# Positionnement au temps 2 pour le temps de rendu de l'image .
			t1=time.time()
			# Si le temps de rendu est inferieur a la minute ... .
			if int(t1-t0)<60 :
				# Pour affichage dans le terminal .
				affTerm=_("Temps de rendu : %s secondes") % (int(round(t1-t0)))
				#print
				#print datHeurEcr
				#print "=================================================="
				#print affTerm
				#print "=================================================="
				#print
				EkdPrint(u'')
				EkdPrint(u"%s" % datHeurEcr)
				EkdPrint(u"==================================================")
				EkdPrint(u"%s" % affTerm)
				EkdPrint(u"==================================================")
				EkdPrint('')
				# Pour affichage dans l'interface (variable) .
				affTempsInterface=_("%s secondes") % (int(round(t1-t0)))
			# Si le temps de rendu est superieur a la minute ... calcul des 
			# minutes et des secondes .
			elif int(t1-t0)>=60 : 
				# Pour affichage dans le terminal .
				affTerm=_(u"Temps de rendu : ")+str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
				#print
				#print datHeurEcr
				#print "=================================================="
				#print affTerm
				#print "=================================================="
				#print
				EkdPrint(u'')
				EkdPrint(u"%s" % datHeurEcr)
				EkdPrint(u"==================================================")
				EkdPrint(u"%s" % affTerm)
				EkdPrint(u"==================================================")
				EkdPrint(u'')
				# Pour affichage dans l'interface
				affTempsInterface=str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
			# --------------------------------------------------------------------

			# Affichage de l'image temporaire 
			# Ouverture d'une boite de dialogue affichant l'aperçu.
			#
			# Affichage par le bouton Voir le résultat
			visio = VisionneurEvolue(self.repTampon+'aff_decoup_fond__tmp58g7y411eeya7.png')
			visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
			visio.exec_()
		
			return 0
			
			# Affichage des infos sur l'image --------------------	
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte=_(u" Image avant découpage du fond uni ")
			texte_2=_(u" Réglages(s)")
			texte_3=_(u" Résolution de l'image")
			texte_4=_(u" Temps de calcul de la découpe")
			a='#'*36
			
			self.infosImgProv=a+'\n# '+texte+'\n'+a+'\n'
			self.infosImgProv=self.infosImgProv+'\n'+self.listeChemin[0]+'\n\n'
			
			self.infosImgProv_2=a+'\n# '+texte_2+'\n'+a+'\n'
			self.infosImgProv_2=self.infosImgProv_2+'\n'+_(u'Valeur teinte (début) : ')+str(self.spinTeinteDebut.value())+'\n'+_(u'Valeur teinte (fin) : ')+str(self.spinTeinteFin.value())+'\n'+_(u'Valeur saturation (début) : ')+str(self.spinSaturationDebut.value())+'\n'+_(u'Valeur saturation (fin) : ')+str(self.spinSaturationFin.value())+'\n'+_(u'Valeur luminosité : ')+str(self.spinLuminosite.value())+'\n\n'
			
			self.infosImgProv_3=a+'\n# '+texte_3+'\n'+a+'\n'
			self.infosImgProv_3=self.infosImgProv_3+'\n'+str(widthDepart)+' x '+str(heightDepart)+_(u' pix')+'\n'+_(u"Nombre de pixels dans l'image : ")+str(nbPixelsTotal)+'\n\n'
			
			self.infosImgProv_4=a+'\n# '+texte_4+'\n'+a+'\n'
			self.infosImgProv_4=self.infosImgProv_4+'\n'+affTempsInterface+'\n\n'
			
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv+self.infosImgProv_2+self.infosImgProv_3+self.infosImgProv_4)
			self.framImg.setEnabled(True)
		
			# remise à 0 de la variable provisoire de log
			self.infosImgProv, self.infosImgProv_2, self.infosImgProv_3, self.infosImgProv_4='', '', '', ''
			# ----------------------------------------------------
			
			# Epuration/elimination des fichiers tampon
			for toutRepTemp in glob.glob(self.repTampon+'*.*'):
				os.remove(toutRepTemp)
				
			self.operationReussie()
			
		except :
			#print "ERREUR !"
			EkdPrint(u"ERREUR !")
			self.messageErreur()

			
	def meth_1_ReglagMasqueAlpha(self):
		""" Masque alpha (découpe) pour la méthode 1 """
		
		# Cette fonction gere les chemins avec trous .
	
		try :

			# Epuration/elimination des fichiers tampon
			l_RepTemp=glob.glob(self.repTampon+'*.*')
			if len(l_RepTemp)>0: 
				for toutRepTemp in l_RepTemp: os.remove(toutRepTemp)

			# Récupération de la liste des fichiers chargés
			self.listeChemin=self.afficheurImgSource.getFiles()
			
			# Liste pour affichage image découpée (ds le tabwidget)
			listeAff_1=[]
			# Liste pour affichage dans la page Info
			listeAff_2=[]
	
			# Nbre d'images charges par l'utilisateur
			nbreElem=len(self.listeChemin)	

			# Compteur pour le calcul du temps de rendu cumule.
			som_t_renduCumul=0 
	
			# Compteur pour le 1er temps de rendu (exactement la meme variable
			# que pour ==> Positionnement au temps 1 pour le temps de rendu de 
			# l'image, juste en-dessous) .
			t0=0 

			# Positionnement au temps 1 pour le temps de rendu de l'image .
			temps1=time.localtime(time.time())	
	
			# Boucle principale de chargement des images .
			for parcPrincipal in range(nbreElem):
		
				# Ouverture de l'image dans le lot .
				imageDepart=Image.open(self.listeChemin[parcPrincipal])
		
				# Compteur pour le 1er temps de rendu .
				t0=time.time()

				# On recupere la taille de l'image
				widthDepart, heightDepart=imageDepart.size

				# On recupere le nombre de pixels totaux
				nbPixelsTotal=widthDepart*heightDepart
		
				# On recupere le tableau de pixels
				imageData=imageDepart.getdata()
 
				#-----------------------------------------------
				# Algorithme de detection du fond bleu/vert
				#-----------------------------------------------

				# On boucle sur l'image RVB -> on cree une nouvelle image RVBA, 
				# le fond bleu/vert est supprime . De plus on va stocker les 
				# pixels de bord .
				newImageRGBA=[]

				for parcRGB_1 in range(nbPixelsTotal) :
    					# On recupere les valeurs R,G et B
					val_R_rgb=imageData[parcRGB_1][0]
    					val_G_rgb=imageData[parcRGB_1][1]
    					val_B_rgb=imageData[parcRGB_1][2]
    
    					# ------------------------------- #
    					# On calcule les valeurs de H,S,V #
    					# ------------------------------- #
    					# On detecte le max et le min
    					maxRGB=float(max(imageData[parcRGB_1]))
    					minRGB=float(min(imageData[parcRGB_1]))
    					# Calcule de la difference entre min et max
    					deltaRGB=maxRGB-minRGB
    					# Calcul de la Saturation
    					if maxRGB>0: s_HSV=(deltaRGB/maxRGB)*100
    					else: s_HSV=0
    					# Calcul de Hue (Teinte)
    					if deltaRGB==0: h_HSV=-1
    					elif val_R_rgb==maxRGB: h_HSV=(val_G_rgb-val_B_rgb)/deltaRGB
    					elif val_G_rgb==maxRGB: h_HSV=2+(val_B_rgb-val_R_rgb)/deltaRGB
    					else: h_HSV=4+(val_R_rgb-val_G_rgb)/deltaRGB
					# Conversion en degres de Hue
    					h_HSV=h_HSV*60
    					if h_HSV<0: h_HSV=h_HSV+360
    					# Calcul de Value (Luminosite)
    					v_HSV=maxRGB
					# Pourcentage de 0 à 100 de Value (il est beaucoup plus
					# pratique de travailler avec une valeur entre 0 et 100)
					v_HSV=v_HSV*100/256
			
					# On teste si le pixel appartient au fond ou non
    					if self.spinTeinteDebut.value()<=h_HSV<=self.spinTeinteFin.value() and self.spinSaturationDebut.value()<=s_HSV<=self.spinSaturationFin.value() and self.spinLuminosite.value()<=v_HSV<=100:
        					# Si oui, on affecte du blanc et de la 
						# transparence (A=0) au pixel
        					newImageRGBA.append((0, 0, 0, 0))
    					else :
        					# Si non, on conserve la valeur RVB avec une 
						# transparence a 100% .
        					newImageRGBA.append((val_R_rgb, val_G_rgb, val_B_rgb, 255))	
			
					#-----------------------------------------------
					# Fin algo detection fond bleu/vert
					#-----------------------------------------------

				# On sauvegarde l'image avant anti-aliasing
				imgDecoup=Image.new('RGBA', imageDepart.size)
				imgDecoup.putdata(newImageRGBA)
				
				# Ouverture de l'image avec le fond en damier
				imQuad=Image.open("gui_modules_lecture"+os.sep+"affichage_image"+os.sep+"ekd_quadrillage_canal_alpha.png")
				# Redimensionnement de l'image du damier (quadrillage) aux 
				# dimensions de la premiere image chargee.
				RedimQuad=imQuad.resize(imageDepart.size, Image.ANTIALIAS)
			
				# Copie de l'image quadrillage dans le répertoire tampon
				shutil.copy('gui_modules_lecture'+os.sep+'affichage_image'+os.sep+'ekd_quadrillage_canal_alpha.png', self.repTampon)
		
				# On libere de la memoire
				del imageData

				#---------------------------------------------------------------------------
				# On supprimme la premiere ligne bleue (si fond bleu) 
				# restante autour du personnage. Début d'anti-aliasing
				antialiasing=[]

				for parcSupprimeLigne in range(nbPixelsTotal) :
    					# Si le pixel detecte n'est pas transparent
    					if newImageRGBA[parcSupprimeLigne][3]>0 :
        					y_ligne=math.ceil((parcSupprimeLigne-1)/widthDepart)
        					x_ligne=parcSupprimeLigne-(y_ligne*widthDepart)
        					# Detection des bords
        					if (x_ligne==0 or x_ligne>=widthDepart-1 or y_ligne==0 or y_ligne>=heightDepart-1) :
							antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
        					else :
            						# Si on a 1 voisin transparent bord
            						# Sinon -> pas bord
            						# On teste (x-1,y),(x+1,y),(x,y-1),(x,y+1)
            						if (newImageRGBA[parcSupprimeLigne-1][3]==0 or newImageRGBA[parcSupprimeLigne+1][3]==0 or newImageRGBA[parcSupprimeLigne-widthDepart][3]==0 or newImageRGBA[parcSupprimeLigne+widthDepart][3]==0) :
                						# Si bord existe -> on efface . Le 
								# bord en question est transforme en R,
								# G, B --> blanc et A --> transparent
                						antialiasing.append((255, 255, 255, 0))
            						else :
                						antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
    					else :
        					antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], 0))

				newImageRGBA=antialiasing
				#---------------------------------------------------------------------------
				
				# Creation d'une nouvelle image et integration des donnees recoltees.
				newImageAntialias=Image.new('RGBA', imgDecoup.size)
				newImageAntialias.putdata(antialiasing)
				a1, a2, a3, a4=newImageAntialias.split()
				imgMerge=Image.merge('RGBA', (a1, a2, a3, a4))
				# Sauvegarde de la nouvelle image (image tampon)
				imgMerge.save(self.repTampon+'decoupe_fond_tmpf1f84o824qz7.png', 'PNG')
			
				# Condition (au choix de l'utilisateur) de réglage du combo de netteté
				if self.comboNettete.currentIndex()==0:
					pass
				else:
					# Ouverture de l'image pour application du kernel (matrice)
					imk=Image.open(self.repTampon+'decoupe_fond_tmpf1f84o824qz7.png')
					# Kernel 3x3 pour amélioration des bords. L'image devient plus nette.
					sizeKern3x3=(3, 3)
					# Matrice trouvee ici:
					# http://blogs.codes-sources.com/tkfe/archive/2005/04/15/6004.aspx
					kernAmBords=(-1, -2, -1, -2, 16, -2, -1, -2, -1)
					# Application de la matrice
					imKernelAmBords=imk.filter(ImageFilter.Kernel(sizeKern3x3, kernAmBords)).save(self.repTampon+'decoupe_fond_tmpf1f84o824qz7.png', 'PNG')
			
				# Ouverture de l'image pour application du kernel (matrice)
				ouvIm=Image.open(self.repTampon+'decoupe_fond_tmpf1f84o824qz7.png')
				
				# Kernel 3x3 anti-crénelage
				sizeKern3x3=(3, 3)
				# Type de kernel utilisé
				kernAntiAlias=(1, 2, 3, 4, 5, 6, 7, 8, 9)
				# Application d'un anti-aliasing sur l'image (et donc sur les contours) par 
				# cette matrice. Cette excelllente matrice a été trouvée ici:
				# http://www.photo-lovers.org/mosaic.shtml.fr 
				# (voir à partir de Méthode du vecteur médian)
				#
				# Sauvegarde de l'image --> utilisateur
				vraiCheminSauv = self.chemDossierSauv+'_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'
				ouvIm.filter(ImageFilter.Kernel(sizeKern3x3, kernAntiAlias)).save(vraiCheminSauv, 'PNG')
				
				# Sauvegarde de l'image pour compositing
				ouvIm.filter(ImageFilter.Kernel(sizeKern3x3, kernAntiAlias)).save(self.repTampon+'decoupe_fond_tmpf1f84o824qz7_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
				
				# Ouverture de l'image pour compositing
				imgFinal=Image.open(self.repTampon+'decoupe_fond_tmpf1f84o824qz7_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
				
				# Compositing entre l'image avec le damier et l'image du fond vert/bleu decoupe et
				# enregistrement dans le rep temporaire (et ce pour l'affichage dans l'interface)
				ImageChops.composite(imgFinal, RedimQuad, imgFinal).save(self.repTampon+'decoupe_fond_tmpf1f84o824qz7_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png', 'PNG')
				
				# Remplissage de listeAff_1 pour affichage (ds le tabwidget)
				listeAff_1.append(self.repTampon+'decoupe_fond_tmpf1f84o824qz7_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
				
				# Ajout des images dans la liste self.listeImgDestin. Cette liste
				# sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(listeAff_1[parcPrincipal])
				
				# On libere la memoire
				del antialiasing, newImageRGBA, imQuad, RedimQuad, newImageAntialias, imgDecoup, val_R_rgb, val_G_rgb, val_B_rgb, h_HSV, s_HSV, v_HSV, parcRGB_1, parcSupprimeLigne, a1, a2, a3, a4, imageDepart
				# x_ligne et y_ligne ne sont pas libérés car cela peut produire une erreur ds 
				# certaines circonstances
				
				# ------------------------------------------------------------------ #
				# STATS DE RENDU (AFFICHAGE ET SAUVEGARDE) .
				# ------------------------------------------------------------------ #
				# Calcule le pourcentage effectue a chaque passage
				val_pourc=((parcPrincipal+1)*100)/nbreElem
				# Affichage du pourcentage du rendu dans le terminal
				# sous Linux ou la fenetre MS-DOS sous Windows
				#print _("Progression du rendu :"), val_pourc # pas de unicode pour un print
				EkdPrint(_(u"Progression du rendu: %s") % val_pourc)
				# Positionnement au temps 2 pour le temps de rendu de l'image
				t1=time.time()
				# Temps local (annee, mois, jour, heure, minute, seconde ...)
				tLocal=time.localtime()
				# Calcul avec le compteur pour le calcul du temps de rendu cumule
				som_t_renduCumul=som_t_renduCumul+(t1-t0)
				# Calcul pour la moyenne du temps de rendu .
				MoyRendu=som_t_renduCumul/(parcPrincipal+1) 
				# Calcul pour le temps de rendu restant .
				tempRestant=((MoyRendu*nbreElem)-(MoyRendu*parcPrincipal+1))-MoyRendu 
				# Mise en ordre du temps local pour ecriture dans fichier
				datHeurEcr=_(u"Le ")+str(tLocal[2])+"/"+str(tLocal[1])+"/"+str(tLocal[0])+_(u" a ")+str(tLocal[3])+":"+str(tLocal[4])+":"+str(tLocal[5])
			
				# Pour ecriture dans fichier
				progImg=_(u"Image ")+str(parcPrincipal+1)+"/"+str(nbreElem)
			
				# Si le temps de rendu est inferieur a la minute ... .
				if int(t1-t0)<60:
					affTemps=_(u"Temps de rendu : %s secondes") % (int(round(t1-t0)))
				# Si le temps de rendu est superieur a la minute ... calcul des 
				# minutes et des secondes
				elif int(t1-t0)>=60:
					affTemps=_(u"Temps de rendu : ")+str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
				# Si la moyenne du temps de rendu est inferieur a la minute ... .	
				if MoyRendu<60:
					moyTemps=_(u"Moyenne du temps de rendu : %s secondes") % (int(round(MoyRendu))) 
				# Si la moyenne du temps de rendu est superieur a la minute ...  
				# calcul des minutes et des secondes .
				elif MoyRendu>=60:
					moyTemps=_(u"Moyenne du temps de rendu : ")+str(int(round(MoyRendu/60)))+_(u" min ")+str(int(round(MoyRendu%60)))+_(u" sec")
				# Si le temps de rendu est inferieur a la minute ... .
				if som_t_renduCumul<60:
					tRenduCumul=_(u"Temps de rendu cumule : %s secondes") % (int(round(som_t_renduCumul)))
				# Si le temps de rendu est superieur ou egal a la minute ... calcul des 
				# heures et des minutes .
				elif som_t_renduCumul>=60:
					tRenduInfMinut=int(round(som_t_renduCumul/60))
					tRenduCumul=_(u"Temps de rendu cumule : ")+str(tRenduInfMinut/60)+_(u" h ")+str(tRenduInfMinut%60)+_(u" min")
					
				# Pour le temps de rendu restant ...
				# Si le temps de rendu restant est superieur a 0 secondes .
				if tempRestant>0:
					# Si le temps de rendu restant est inferieur a la minute et le
					# calcul du pourcentage est inferieur a 100 % .
					if tempRestant<60 and val_pourc<100:
						tRestant=_(u"Temps de rendu restant (estimation) : %s secondes") % (int(round(tempRestant)))
					# Si le temps de rendu restant est superieur a la minute et le
					# calcul du pourcentage est inferieur a 100 % .
					elif tempRestant>=60 and val_pourc<100:
						tRestantInfMinut=int(round(tempRestant/60))
						tRestant=_(u"Temps de rendu restant (estimation) : ")+str(tRestantInfMinut/60)+_(u" h ")+str(tRestantInfMinut%60)+_(u" min")
				
				# Des que le rendu est arrive a 100%, affichage de dans le
				# terminal sous Linux ou la fenetre MS-DOS sous Windows
				if val_pourc==100 :
					#print
					EkdPrint(u'')
					#print _("Fini !")
					EkdPrint(_(u"Fini !"))

				# Ecriture des statistiques (cumul de l'ecriture) dans un fichier texte	
				ecrStatRendu=open(self.chemDossierSauv+_("_image_masque_alpha_meth_1.txt"), 'a')
				ecrStatRendu.write("=================================================\n"+str(datHeurEcr)+"\n"+"-------------------------------------------------\n"+str(progImg)+"\n"+str(affTemps)+"\n"+str(moyTemps)+"\n"+str(tRenduCumul)+"\n\n")
				ecrStatRendu.close()
				
				# Remplissage de la liste pour les statistiques de rendu
				listeAff_2.append((_(u"Image chargée : ")+self.listeChemin[parcPrincipal], _(u"Image finale : ")+vraiCheminSauv, progImg, affTemps, moyTemps, tRenduCumul, _(u"Nombre total de pixels : ")+str(nbPixelsTotal), _("Dimension : ")+str(widthDepart)+' x '+str(heightDepart)))

				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée
				self.progress.setValue(val_pourc)
				QApplication.processEvents()
				# Bouton Cancel pour arrêter la progression donc le process
				if (self.progress.wasCanceled()): break
				# Quand l'utilisateur charge au moins 2 images ...
				if len(self.listeChemin)>1:
					self.progress.setLabel(QLabel(QString(tRestant)))
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
			
			# Affichage des infos sur l'image -------------------------	
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte=_(u" Statistiques de rendu")
			a='#'*36
			b="-"*36
			
			self.infosImgProv=a+'\n#'+texte+'\n'+a+'\n'
			for parcStatRendu in listeAff_2:
				self.infosImgProv=self.infosImgProv+'\n'+parcStatRendu[0]+'\n'+parcStatRendu[1]+'\n'+parcStatRendu[2]+'\n'+parcStatRendu[3]+'\n'+parcStatRendu[4]+'\n'+parcStatRendu[5]+'\n'+parcStatRendu[6]+'\n'+parcStatRendu[7]+'\n'+b+'\n'
				
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv)
			self.framImg.setEnabled(True)
			
			# remise à 0 de la variable provisoire de log
			self.infosImgProv=''
			# ---------------------------------------------------------
				
			self.operationReussie()

		except :
			#print "ERREUR !"
			EkdPrint(u"ERREUR !")
			self.messageErreur()

			
	def meth_1_ReglagMasque3D(self):
		""" Masque 3D pour la méthode 1 """
		
		# Cette fonction gere les chemins avec trous
	
		try :

			# Epuration/elimination des fichiers tampon
			l_RepTemp=glob.glob(self.repTampon+'*.*')
			if len(l_RepTemp)>0: 
				for toutRepTemp in l_RepTemp: os.remove(toutRepTemp)

			# Récupération de la liste des fichiers chargés
			self.listeChemin=self.afficheurImgSource.getFiles()
			
			# Liste pour affichage image découpée (ds le tabwidget)
			listeAff_1=[]
			# Liste pour affichage dans la page Info
			listeAff_2=[]
		
			# Nbre d'images charges par l'utilisateur
			nbreElem=len(self.listeChemin) 

			# Compteur pour le calcul du temps de rendu cumule.
			som_t_renduCumul=0 
	
			# Compteur pour le 1er temps de rendu (exactement la meme variable
			# que pour ==> Positionnement au temps 1 pour le temps de rendu de 
			# l'image, juste en-dessous) .
			t0=0 

			# Positionnement au temps 1 pour le temps de rendu de l'image .
			temps1=time.localtime(time.time())	
	
			# Boucle principale de chargement des images .
			for parcPrincipal in range(nbreElem):
		
				# Ouverture de l'image dans le lot .
				imageDepart=Image.open(self.listeChemin[parcPrincipal])
		
				# Compteur pour le 1er temps de rendu .
				t0=time.time()

				# On recupere la taille de l'image
				widthDepart, heightDepart=imageDepart.size

				# On recupere le nombre de pixels totaux
				nbPixelsTotal=widthDepart*heightDepart
		
				# On recupere le tableau de pixels
				imageData=imageDepart.getdata()
 
				#-----------------------------------------------
				# Algorithme de detection du fond bleu/vert
				#-----------------------------------------------

				# On boucle sur l'image RVB -> on cree une nouvelle image RVBA, 
				# le fond bleu/vert est supprime . De plus on va stocker les 
				# pixels de bord .
				newImageRGBA=[]

				for parcRGB_1 in range(nbPixelsTotal):
    					# On recupere les valeurs R,G et B
					val_R_rgb=imageData[parcRGB_1][0]
    					val_G_rgb=imageData[parcRGB_1][1]
    					val_B_rgb=imageData[parcRGB_1][2]
    
    					# ------------------------------- #
    					# On calcule les valeurs de H,S,V #
    					# ------------------------------- #
    					# On detecte le max et le min
    					maxRGB=float(max(imageData[parcRGB_1]))
    					minRGB=float(min(imageData[parcRGB_1]))
    					# Calcule de la difference entre min et max
    					deltaRGB=maxRGB-minRGB
    					# Calcul de la Saturation
    					if maxRGB>0: s_HSV=(deltaRGB/maxRGB)*100
    					else: s_HSV=0
    					# Calcul de Hue (Teinte)
    					if deltaRGB==0: h_HSV=-1
    					elif val_R_rgb==maxRGB: h_HSV=(val_G_rgb-val_B_rgb)/deltaRGB
    					elif val_G_rgb==maxRGB: h_HSV=2+(val_B_rgb-val_R_rgb)/deltaRGB
    					else: h_HSV=4+(val_R_rgb-val_G_rgb)/deltaRGB
					# Conversion en degres de Hue
    					h_HSV=h_HSV*60
    					if h_HSV<0: h_HSV=h_HSV+360
    					# Calcul de Value (Luminosite)
    					v_HSV=maxRGB
					# Pourcentage de 0 à 100 de Value (il est beaucoup plus
					# pratique de travailler avec une valeur entre 0 et 100)
					v_HSV=v_HSV*100/256

					# ----------------------------------------------------------- #
					# Attention conditions d'affichage du fond et de la forme !.
					# ----------------------------------------------------------- #
					# Ici si on a sélectionné un fond noir et une/des formes blanches
					if self.comboFondForme.currentIndex()==0:
						# On teste si le pixel appartient au fond ou non
    						if self.spinTeinteDebut.value()<=h_HSV<=self.spinTeinteFin.value() and self.spinSaturationDebut.value()<=s_HSV<=self.spinSaturationFin.value() and self.spinLuminosite.value()<=v_HSV<=100:
							
        						# Si oui, on affecte du noir et de la 
							# transparence (A=0) au pixel
        						newImageRGBA.append((0, 0, 0, 0))
    						else :
        						# Si non, on affecte du blanc avec une transparence a 100%
        						newImageRGBA.append((255, 255, 255, 255))
					# Là si on a sélectionné un fond blanc et une/des formes noires
					elif self.comboFondForme.currentIndex()==1:
						# On teste si le pixel appartient au fond ou non
    						if self.spinTeinteDebut.value()<=h_HSV<=self.spinTeinteFin.value() and self.spinSaturationDebut.value()<=s_HSV<=self.spinSaturationFin.value() and self.spinLuminosite.value()<=v_HSV<=100:
							
        						# Si oui, on affecte du blanc et de la 
							# transparence (A=0) au pixel
        						newImageRGBA.append((255, 255, 255, 0))
    						else :
        						# Si non, on affecte du noir avec une transparence a 100%
        						newImageRGBA.append((0, 0, 0, 255))
			
				#-----------------------------------------------
				# Fin algo detection fond bleu/vert
				#-----------------------------------------------

				# On sauvegarde l'image avant anti-aliasing
				imgDecoup=Image.new('RGBA', imageDepart.size)
				imgDecoup.putdata(newImageRGBA)
		
				# On libere de la memoire
				del imageData

				#---------------------------------------------------------------------------
				# On supprimme la premiere ligne bleue (si fond bleu) 
				# restante autour du personnage. Début d'anti-aliasing
				antialiasing=[]

				for parcSupprimeLigne in range(nbPixelsTotal):
    					# Si le pixel detecte n'est pas transparent
    					if newImageRGBA[parcSupprimeLigne][3]>0:
        					y_ligne=math.ceil((parcSupprimeLigne-1)/widthDepart)
        					x_ligne=parcSupprimeLigne-(y_ligne*widthDepart)
        					# Detection des bords
        					if (x_ligne==0 or x_ligne>=widthDepart-1 or y_ligne==0 or y_ligne>=heightDepart-1):
							antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
        					else:
            						# Si on a 1 voisin transparent bord
            						# Sinon -> pas bord
            						# On teste (x-1,y),(x+1,y),(x,y-1),(x,y+1)
            						if (newImageRGBA[parcSupprimeLigne-1][3]==0 or newImageRGBA[parcSupprimeLigne+1][3]==0 or newImageRGBA[parcSupprimeLigne-widthDepart][3]==0 or newImageRGBA[parcSupprimeLigne+widthDepart][3]==0):
                						# Si bord existe -> on efface . Le bord en
								# question est transforme en R, G, B -->
								# noir et A --> transparent .
                						antialiasing.append((0, 0, 0, 0))
            						else :
                						antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
    					else :
        					antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], 0))

				newImageRGBA=antialiasing
				#---------------------------------------------------------------------------
				
				# Creation d'une nouvelle image et integration des donnees recoltees .
				newImageAntialias=Image.new('RGBA', imgDecoup.size)
				newImageAntialias.putdata(antialiasing)
				a1, a2, a3, a4=newImageAntialias.split()
				imgMerge=Image.merge('RGBA', (a1, a2, a3, a4))
				# Sauvegarde de la nouvelle image (image tampon)
				imgMerge.save(self.repTampon+'masque3d_tmpg5dgf54dqk1oy8f.png', 'PNG')
				
				# Transformation du fond noir (ou fond blanc) transparent en fond noir (ou blanc) opaque 
				imgMerge.putalpha(255)
				
				# Sauvegarde de la nouvelle image (image tampon)
				imgMerge.save(self.repTampon+'masque3d_tmpg5dgf54dqk1oy8f.png', 'PNG')
				
				# Ouverture de l'image tampon
				ouvIm=Image.open(self.repTampon+'masque3d_tmpg5dgf54dqk1oy8f.png')
			
				# Kernel 5x5 Floutage
				sizeKern5x5=(5, 5)
				# Type de kernel utilisé
				kernFlou=(0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0)
				# Application d'un leger flou a l'image et enregistrement dans le
				# chemin (et avec le nom donné) et ce par/pour l'utilisateur
				vraiCheminSauv=self.chemDossierSauv+'_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'
				ouvIm.filter(ImageFilter.Kernel(sizeKern5x5, kernFlou)).save(vraiCheminSauv, 'PNG')

				# Application d'un leger flou a l'image et enregistrement dans le rep
				# temporaire (... et donc l'affichage dans l'interface)
				imKerFlou=ouvIm.filter(ImageFilter.Kernel(sizeKern5x5, kernFlou)).save(self.repTampon+'masque3d_tmpg5dgf54dqk1oy8f_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png', 'PNG')
				
				# Remplissage de listeAff_1 pour affichage (ds le tabwidget)
				listeAff_1.append(self.repTampon+'masque3d_tmpg5dgf54dqk1oy8f_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
				
				# Ajout des images dans la liste self.listeImgDestin. Cette liste
				# sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(listeAff_1[parcPrincipal])
				#################################################################################
				
				# On libere la memoire
				del antialiasing, newImageRGBA, newImageAntialias, imgDecoup, val_R_rgb, val_G_rgb, val_B_rgb, h_HSV, s_HSV, v_HSV, parcRGB_1, parcSupprimeLigne, a1, a2, a3, a4, imageDepart
				# x_ligne et y_ligne ne sont pas libérés car cela peut produire une erreur ds 
				# certaines circonstances
				
				# ------------------------------------------------------------------ #
				# STATS DE RENDU (AFFICHAGE ET SAUVEGARDE) .
				# ------------------------------------------------------------------ #
				# Calcule le pourcentage effectue a chaque passage
				val_pourc=((parcPrincipal+1)*100)/nbreElem
				# Affichage du pourcentage du rendu dans le terminal
				# sous Linux ou la fenetre MS-DOS sous Windows
				#print _("Progression du rendu :"), val_pourc
				EkdPrint(_(u"Progression du rendu: %s") % val_pourc)
				# Positionnement au temps 2 pour le temps de rendu de l'image
				t1=time.time()
				# Temps local (annee, mois, jour, heure, minute, seconde ...)
				tLocal=time.localtime()
				# Calcul avec le compteur pour le calcul du temps de rendu cumule
				som_t_renduCumul=som_t_renduCumul+(t1-t0)
				# Calcul pour la moyenne du temps de rendu .
				MoyRendu=som_t_renduCumul/(parcPrincipal+1) 
				# Calcul pour le temps de rendu restant .
				tempRestant=((MoyRendu*nbreElem)-(MoyRendu*parcPrincipal+1))-MoyRendu 
				# Mise en ordre du temps local pour ecriture dans fichier
				datHeurEcr=_(u"Le ")+str(tLocal[2])+"/"+str(tLocal[1])+"/"+str(tLocal[0])+_(u" a ")+str(tLocal[3])+":"+str(tLocal[4])+":"+str(tLocal[5])
			
				# Pour ecriture dans fichier
				progImg=_(u"Image ")+str(parcPrincipal+1)+"/"+str(nbreElem)
			
				# Si le temps de rendu est inferieur a la minute ... .
				if int(t1-t0)<60:
					affTemps=_(u"Temps de rendu : %s secondes") % (int(round(t1-t0)))
				# Si le temps de rendu est superieur a la minute ... calcul des 
				# minutes et des secondes
				elif int(t1-t0)>=60:
					affTemps=_(u"Temps de rendu : ")+str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
				# Si la moyenne du temps de rendu est inferieur a la minute ... .	
				if MoyRendu<60:
					moyTemps=_(u"Moyenne du temps de rendu : %s secondes") % (int(round(MoyRendu))) 
				# Si la moyenne du temps de rendu est superieur a la minute ...  
				# calcul des minutes et des secondes .
				elif MoyRendu>=60:
					moyTemps=_(u"Moyenne du temps de rendu : ")+str(int(round(MoyRendu/60)))+_(u" min ")+str(int(round(MoyRendu%60)))+_(u" sec")
				# Si le temps de rendu est inferieur a la minute ... .
				if som_t_renduCumul<60:
					tRenduCumul=_(u"Temps de rendu cumule : %s secondes") % (int(round(som_t_renduCumul)))
				# Si le temps de rendu est superieur ou egal a la minute ... calcul des 
				# heures et des minutes .
				elif som_t_renduCumul>=60:
					tRenduInfMinut=int(round(som_t_renduCumul/60))
					tRenduCumul=_(u"Temps de rendu cumule : ")+str(tRenduInfMinut/60)+_(u" h ")+str(tRenduInfMinut%60)+_(u" min")
					
				# Pour le temps de rendu restant ...
				# Si le temps de rendu restant est superieur a 0 secondes .
				if tempRestant>0:
					# Si le temps de rendu restant est inferieur a la minute et le
					# calcul du pourcentage est inferieur a 100 % .
					if tempRestant<60 and val_pourc<100:
						tRestant=_(u"Temps de rendu restant (estimation) : %s secondes") % (int(round(tempRestant)))
					# Si le temps de rendu restant est superieur a la minute et le
					# calcul du pourcentage est inferieur a 100 % .
					elif tempRestant>=60 and val_pourc<100:
						tRestantInfMinut=int(round(tempRestant/60))
						tRestant=_(u"Temps de rendu restant (estimation) : ")+str(tRestantInfMinut/60)+_(u" h ")+str(tRestantInfMinut%60)+_(u" min")
						
				# Des que le rendu est arrive a 100%, affichage de dans le
				# terminal sous Linux ou la fenetre MS-DOS sous Windows .
				if val_pourc==100 :
					#print
					EkdPrint(u'')
					#print _("Fini !")
					EkdPrint(_(u"Fini !"))
				
				# Ecriture des statistiques (cumul de l'ecriture) dans un fichier texte	
				ecrStatRendu=open(self.chemDossierSauv+_("_image_masque_3d_meth_1.txt"), 'a')
				ecrStatRendu.write("=================================================\n"+datHeurEcr+"\n"+"-------------------------------------------------\n"+progImg+"\n"+str(affTemps)+"\n"+str(moyTemps)+"\n"+str(tRenduCumul)+"\n\n")
				ecrStatRendu.close()
				
				# Remplissage de la liste pour les statistiques de rendu
				listeAff_2.append((_(u"Image chargée : ")+self.listeChemin[parcPrincipal], _(u"Image finale : ")+vraiCheminSauv, progImg, affTemps, moyTemps, tRenduCumul, _(u"Nombre total de pixels : ")+str(nbPixelsTotal), _("Dimension : ")+str(widthDepart)+' x '+str(heightDepart)))
				
				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée
				self.progress.setValue(val_pourc)
				# Quand l'utilisateur charge au moins 2 images ...
				QApplication.processEvents()
				# Bouton Cancel pour arrêter la progression donc le process
				if (self.progress.wasCanceled()): break
				if len(self.listeChemin)>1:
					self.progress.setLabel(QLabel(QString(tRestant)))
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
			
			# Affichage des infos sur l'image -------------------------
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte=_(u" Statistiques de rendu")
			a='#'*36
			b="-"*36
			
			self.infosImgProv=a+'\n#'+texte+'\n'+a+'\n'
			for parcStatRendu in listeAff_2:
				self.infosImgProv=self.infosImgProv+'\n'+parcStatRendu[0]+'\n'+parcStatRendu[1]+'\n'+parcStatRendu[2]+'\n'+parcStatRendu[3]+'\n'+parcStatRendu[4]+'\n'+parcStatRendu[5]+'\n'+parcStatRendu[6]+'\n'+parcStatRendu[7]+'\n'+b+'\n'
				
			# Affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv)
			self.framImg.setEnabled(True)
			
			# Remise à 0 de la variable provisoire de log
			self.infosImgProv=''
			# ---------------------------------------------------------
			
			self.operationReussie()
				
		except :
			#print "ERREUR !"
			EkdPrint(u"ERREUR !")
			self.messageErreur()
				
			
	def meth_2_ReglagPrevis(self):
		""" Réglage des différents paramètres et prévisualisation pour la méthode 2 """

		try :

			# Récupération du fichier sélectionné par l'utilisateur (si pas de fichier
			# sélectionné par l'utilisateur, la 1ère image de la liste est prise)
			file = self.afficheurImgSource.getFile()
			if not file: return
			self.listeChemin = [file]
			
			# Compteur départ pour le temps de rendu
			t0=time.time()
			
			# Liste pour affichage image découpée (ds le tabwidget)
			listeAff_1=[]
	
			# Ouverture utile pour connaitre notamment la resolution de l'image .
			imageDepart=Image.open(self.listeChemin[0])
			
			# On recupere la taille de l'image
			widthDepart, heightDepart=imageDepart.size

			# On recupere le nombre de pixels totaux
			nbPixelsTotal=widthDepart*heightDepart
			
			#print 'Nbre total de pixels', nbPixelsTotal
			EkdPrint(u'Nbre total de pixels %s' % nbPixelsTotal)
			
			# Pour compatibilité entre linux et windows
			# Dans la version windows ce n'est pas traité par un QProcess (comme sous 
			# Linux) mais directement avec os.system (car le QProcess avec la commande 
			# convert d'ImageMagick génère une erreur)
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				process = QProcess(self)
			
			# Si on a sélectionné Qualité Moyenne
			if self.comboQualite.currentIndex()==0:
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					process.start('convert -resize '+str(round(imageDepart.size[0]*1.4))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(round(imageDepart.size[0]*1.4))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
				
			# Si on a sélectionné Qualité Bonne
			elif self.comboQualite.currentIndex()==1:
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					process.start('convert -resize '+str(round(imageDepart.size[0]*1.6))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(round(imageDepart.size[0]*1.6))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
					
			# Si on a sélectionné Qualité Tres bonne
			elif self.comboQualite.currentIndex()==2:
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					process.start('convert -resize '+str(round(imageDepart.size[0]*1.8))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(round(imageDepart.size[0]*1.8))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
					
			# Si on a sélectionné Qualité Excellente
			elif self.comboQualite.currentIndex()==3:
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					process.start('convert -resize '+str(round(imageDepart.size[0]*2))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(round(imageDepart.size[0]*2))+'x '+"\""+"".join(self.listeChemin[0])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
			
			imgOuv_1_tmp=Image.open(self.repTampon+"decoupe_fond_tmp5ghy46s3y53k77w4.png")
			
			# Creation de l'array avec les donnees de l'image chargee .
			imageData=array(imgOuv_1_tmp.getdata())
		
			# Collecte des coordonnees x (methode tout avec Numpy --> modulo)
			coord_X_1=remainder(arange(imageData.shape[0]), imgOuv_1_tmp.size[0]) 
			# Collecte des coordonnees y (methode tout avec Numpy --> division)
			coord_Y_1=divide(arange(imageData.shape[0]), imgOuv_1_tmp.size[0])
			# Autre facon de proceder :
			#coord_X_1=arange(len(imageData))%imgOuv_1_tmp.size[0] # collecte
			# coordonnees x
			#coord_Y_1=arange(len(imageData))/imgOuv_1_tmp.size[0] # collecte
			# coordonnees y
			
			# Remplissage d'un array (tableau) avec toutes les coordonnes de 
			# la grille, comme ceci :
			# array([[0, 0],
			#	 [1, 0],
			#	 [2, 0], ..., [0, 1], [1, 1], [2, 1], ..., [500, 50], ...]
			coord_XY=column_stack((coord_X_1, coord_Y_1))
			
			# Calcul de la valeur max . Exemple : [..., [12, 789, 1], [89, 567, 7],
			# ...] donne comme resultat : [[..., 789, 567, ...]] .
			maxRGB=imageData.max(axis=1)
		
			# Conversion en float
			maxRGB=maxRGB.astype(float)
		
			# ------------------------------------------------------------------
			# REMERCIEMENT SPECIAL A Gael Varoquaux (du forum python@aful.org), qui
			# m'a fait decouvrir Numpy et a trouve la formule pour le calcul de Hue
			# (h_HSV)
			# ------------------------------------------------------------------
			# CALCUL DE Hue (avec des valeurs arrondies a 2 chiffres apres la
			# virgule) .
			# TEINTE
			# ------------------------------------------------------------------
			h_HSV=(angle(inner(imageData, c_[1,exp(2j*pi/3.),exp(-2j*pi/3.)]))*180/pi)%360

			# ------------------------------------------------------------------
			# CALCUL DE Saturation	(imageData.ptp(axis=1) ==>
			# maxRGB-minRGB)
			# On obtient a la fin un pourcentage (*100). SATURATION
			# ------------------------------------------------------------------
			s_HSV=round_(imageData.ptp(axis=1)/maxRGB, decimals=2)*100
		
			# ------------------------------------------------------------------
			# CALCUL DE Value. Calcul du pourcentage. LUMINOSITE
			# ------------------------------------------------------------------
			#V_ADFBV=imageData.max(axis=1) # Sans pourcentage
			v_HSV=(imageData.max(axis=1))*100/256 # Avec pourcentage
		
			# Concatenation des colonnes . Exemple :
			# [[0, 1],
			#  [2, 3],
			#  [4, 5]] donne comme resultat : [[0, 2, 4], [1, 3, 5]]
			hsv=column_stack((h_HSV, s_HSV, v_HSV)).astype(int)
			
			# Concatenation des valeurs entre elles . Le tableau genere est
			# sous la forme [[x1 y1 h1 s1 v1] [x2 y2 h2 s2 v2] ... ]
			conc_XY_RGB=c_[coord_XY, hsv]
		
			# --------------------------------------------------------------
			# Collecte/selection des coordonnes x et y, valeurs de Hue, valeurs de
			# Saturation, valeurs de Value selon les reglages faits par 
			# l'utilisateur .
			# Collecte non dans une boucle, mais avec la syntaxe de Numpy .	
			condition_1=((conc_XY_RGB.take([0], axis=1).ravel()>=0) & (conc_XY_RGB.take([1], axis=1).ravel()>=0) & (conc_XY_RGB.take([2], axis=1).ravel()>self.spinTeinteDebut.value()) & (conc_XY_RGB.take([2], axis=1).ravel()<self.spinTeinteFin.value()) & (conc_XY_RGB.take([3], axis=1).ravel()>self.spinSaturationDebut.value()+4) & (conc_XY_RGB.take([3], axis=1).ravel()<self.spinSaturationFin.value()+4) & (conc_XY_RGB.take([4], axis=1).ravel()>self.spinLuminosite.value()-4) & (conc_XY_RGB.take([4], axis=1).ravel()<100))
		
			# Resultat de la condition juste au-dessus .
			selection_1=conc_XY_RGB[condition_1]
		
			# Collecte des coordonnes x et y exactes des pixels bleus/verts dans 
			# l'image. Les autres donnees ne sont pas prises en compte . Selection 
			# des coordonnees x et y avec la syntaxe de Numpy.
			a1=selection_1[:,0]
			a2=selection_1[:,1]
		
			# Mise en forme des cordonnes x et y dans le tableau
			listePrecisCoordonnees=column_stack((a1, a2))
			
			# Collecte de la couleur RGB a la position x=0, y=0 .
			data_1er_pixel=imgOuv_1_tmp.getpixel((0, 0))
		
			# Conversion en RGBA de l'image. RGB+Canal Alpha
			if imgOuv_1_tmp.mode!="RGBA": imagAlpha=imgOuv_1_tmp.convert("RGBA")
			else: imagAlpha=imgOuv_1_tmp
			
			# Ouverture de l'image avec le fond en damier
			imQuad=Image.open("gui_modules_lecture"+os.sep+"affichage_image"+os.sep+"ekd_quadrillage_canal_alpha.png")
			# Redimensionnement de l'image du damier (quadrillage) aux 
			# dimensions de la premiere image chargee .
			RedimQuad=imQuad.resize(imageDepart.size, Image.ANTIALIAS)
			
			# Copie de l'image quadrillage dans le répertoire tampon
			shutil.copy('gui_modules_lecture'+os.sep+'affichage_image'+os.sep+'ekd_quadrillage_canal_alpha.png', self.repTampon)
		
			# Transformation des pixels bleus ou verts du fond
			# en pixels transparents (RGBA --> A=0)
			ecrPix_1=ImageDraw.Draw(imagAlpha)	
			for parcoursXY in listePrecisCoordonnees:
				# Decoupe du fond (enfin le fond devient completement
				# transparent)
				leFondDevTransp=ecrPix_1.point(parcoursXY, (data_1er_pixel[0], data_1er_pixel[1], data_1er_pixel[2], 0))
						
			# -------------------------------------------------------------------
			# Sélection des pixels contigus autour du perso/forme (ceux les +
			# proches) --
			# -------------------------------------------------------------------
			# Selection des pixels contigus (c'est a dire ceux qui touchent le
			# personnage/la forme qui sera decoupe(e)).
			# -------------------------------------------------------------------
			# Calcul des coordonnees cote gauche -->* (pixels de gauche)
			condit_2=where(listePrecisCoordonnees[1:].take([0], axis=1).ravel()>(listePrecisCoordonnees[:-1]+1).take([0], axis=1).ravel())
			# Resultat de la condition juste au-dessus .
			koko_1=listePrecisCoordonnees[condit_2]
			# -------------------------------------------------------------------
			# Inversion du tableau pour calcul des pix de droite ; Exemple : 
			# [[3, 127], [81, 127], [3, 3], [95, 3], [47, 3], [347, 3]] devient
			# [[347, 3], [47, 3], [95, 3], [3, 3], [81, 127], [3, 127]] .
			inversionPourCond_3=listePrecisCoordonnees[::-1]
			# Calcul des coordonnees cote droit *<-- (pixels de droite)
			conditInvers=where(inversionPourCond_3[1:].take([0], axis=1).ravel()<(inversionPourCond_3[:-1]-1).take([0], axis=1).ravel())
			# Resultat de la condition juste au-dessus. Et de nouveau inversion.
			koko_2=inversionPourCond_3[conditInvers][::-1]
			# Mise en forme des cordonnes x et y dans le tableau .
			l_coordXYcontigues=vstack((koko_1, koko_2))
			# -------------------------------------------------------------------
			# De nouveau merci a Gael Varoquaux pour cette methode de classement
			# juste en dessous (methode par une fonction) .
			def foncRemisEnOrdre(k_a, k_b) :
				if k_a[1] > k_b[1] : return 1
				elif k_a[1] < k_b[1] : return -1
				elif k_a[0] > k_b[0] : return 1
				elif k_a[0] < k_b[0] : return -1
				else : return 0
			# Creation d'une liste avec les données du tableu 
			# crée precedemment .
			listeXYcoordContig=l_coordXYcontigues.tolist()
			# Remise en ordre suivant le calcul dans la fonction 
			# foncRemisEnOrdreDFVA .
			listeXYcoordContig.sort(cmp=foncRemisEnOrdre)
			# Creation d'un tableau a partir de la liste .
			l_coordXYcontigues=array(listeXYcoordContig)
			# -------------------------------------------------------------------
		
			# -------------------------------------------------------------------
			# Sélection pour découpe des pixels (les pixels du contour du
			# perso/forme) --
			# -------------------------------------------------------------------
			# Compteur
			conptD_1=0
			# Decoupe des pixels contigus (niveau 1 ==> liste l_Decoup_1)
			l_Decoup_1=[]
			# Decoupe des pixels contigus (niveau 2 ==> liste l_Decoup_2)
			l_Decoup_2=[]
			# Decoupe des pixels contigus (niveau 3 ==> liste l_Decoup_3)
			l_Decoup_3=[]
		
			for parcDecoup_X, parcDecoup_Y in l_coordXYcontigues:
			
				# Si l'id du compteur est pair ca se decale sur la droite .
				if conptD_1%2==0:
					# Incrementation niv 1 de la valeur de x --> (x, y) 
					# a +1
					parcDecoup_X=parcDecoup_X+1
					l_Decoup_1.append((parcDecoup_X, parcDecoup_Y))	
					# Incrementation niv 2 de la valeur de x --> (x, y) 
					# a +1
					parcDecoup_X=parcDecoup_X+1 
					l_Decoup_2.append((parcDecoup_X, parcDecoup_Y)) 
					# Incrementation niv 3 de la valeur de x --> (x, y) 
					# a +1
					parcDecoup_X=parcDecoup_X+1 
					l_Decoup_3.append((parcDecoup_X, parcDecoup_Y)) 
				
				# Si l'id du compteur est impair ca se decale sur la gauche
				elif conptD_1%2==1:
					# Incrementation niv 1 de la valeur de x --> (x, y) 
					# a -1
					parcDecoup_X=parcDecoup_X-1
					l_Decoup_1.append((parcDecoup_X, parcDecoup_Y))	
					# Incrementation niv 2 de la valeur de x --> (x, y) 
					# a -1
					parcDecoup_X=parcDecoup_X-1 
					l_Decoup_2.append((parcDecoup_X, parcDecoup_Y)) 
					# Incrementation niv 3 de la valeur de x --> (x, y) 
					# a -1
					parcDecoup_X=parcDecoup_X-1 
					l_Decoup_3.append((parcDecoup_X, parcDecoup_Y)) 
												
				conptD_1=conptD_1+1
			# -------------------------------------------------------------------
	
			# -------------------------------------------------------------------
			# Selection et mise en relation ds une liste des couleurs aux
			# coordonnes x et y definies juste au dessus . A la fin les listes
			# sont sous cette forme : [..., ((x, y), (R, G, B, A)), ...]
			# -------------------------------------------------------------------
			############ Retiré le 12/04/09 #####################################
			'''
			lll_1=zip(l_Decoup_1, [imagAlpha.getpixel(bbb_1) for bbb_1 in l_Decoup_1])
			lll_2=zip(l_Decoup_2, [imagAlpha.getpixel(bbb_2) for bbb_2 in l_Decoup_2])
			lll_3=zip(l_Decoup_3, [imagAlpha.getpixel(bbb_3) for bbb_3 in l_Decoup_3])
			'''
			#####################################################################
			lll_1=zip(l_Decoup_1, [imagAlpha.getpixel((int(bbb_1[0]), int(bbb_1[1]))) for bbb_1 in l_Decoup_1])
			lll_2=zip(l_Decoup_2, [imagAlpha.getpixel((int(bbb_2[0]), int(bbb_2[1]))) for bbb_2 in l_Decoup_2])
			lll_3=zip(l_Decoup_3, [imagAlpha.getpixel((int(bbb_3[0]), int(bbb_3[1]))) for bbb_3 in l_Decoup_3])
			# -------------------------------------------------------------------
								
			# -------------------------------------------------------------------
			# Traitement de l'image ... decoupe/application du fond transparent
			# (du liseret 1) immediatement autour du perso ou forme .
			ecrPixBordur1=ImageDraw.Draw(imagAlpha)
			for parcBordurXY_1, parcBordurCoul_1 in lll_1 :
				# Découpe du liseret (enfin le liseret devient + ou -
				# transparent)
				ecrPixBordur1.point(parcBordurXY_1, (parcBordurCoul_1[0], parcBordurCoul_1[1], parcBordurCoul_1[2], 10))
			
			# Traitement de l'image ... decoupe/application du fond transparent
			# (du liseret 2) immediatement autour du perso ou forme .	
			ecrPixBordur2=ImageDraw.Draw(imagAlpha)
			for parcBordurXY_2, parcBordurCoul_2 in lll_2 : 
				# Découpe du liseret (enfin le liseret devient + ou -
				# transparent)
				ecrPixBordur2.point(parcBordurXY_2, (parcBordurCoul_2[0], parcBordurCoul_2[1], parcBordurCoul_2[2], 100)) 
			
			# Traitement de l'image ... decoupe/application du fond transparent
			# (du liseret 3) immediatement autour du perso ou forme .	
			ecrPixBordur3=ImageDraw.Draw(imagAlpha)
			for parcBordurXY_3, parcBordurCoul_3 in lll_3 : 
				# Découpe du liseret (enfin le liseret devient + ou -
				# transparent)
				ecrPixBordur3.point(parcBordurXY_3, (parcBordurCoul_3[0], parcBordurCoul_3[1], parcBordurCoul_3[2], 200)) 
			# -------------------------------------------------------------------
			
			# On libere la memoire
			del coord_X_1, coord_Y_1, coord_XY, maxRGB, h_HSV, s_HSV, v_HSV, hsv, conc_XY_RGB, condition_1, selection_1, a1, a2, listePrecisCoordonnees, data_1er_pixel, leFondDevTransp, condit_2, koko_1, inversionPourCond_3, conditInvers, koko_2, l_coordXYcontigues, l_Decoup_1, l_Decoup_2, l_Decoup_3, lll_1, lll_2, lll_3, ecrPixBordur1, ecrPixBordur2, ecrPixBordur3
			
			# -------------------------------------------------------------------
			# PARTIE FINALE DU RENDU
			# -------------------------------------------------------------------
			# Application d'un leger lissage de l'image
			imFILTsmooth=imagAlpha.filter(ImageFilter.SMOOTH)	
			# Compositing entre l'image avec lissage et l'image tampon
			ImageChops.composite(imFILTsmooth, imagAlpha, imagAlpha).save(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png', 'PNG')
				
			# Ouverture de l'image pour application du kernel (matrice)
			imk=Image.open(self.repTampon+"decoupe_fond_tmp5ghy46s3y53k77w4.png")
			# Kernel 3x3 pour amélioration des bords. L'image devient plus nette.
			sizeKern3x3=(3, 3) 
			# Matrice trouvee ici: http://blogs.codes-sources.com/tkfe/archive/2005/04/15/6004.aspx
			kernAmBords=(-1, -2, -1, -2, 16, -2, -1, -2, -1)
			imKernelAmBords=imk.filter(ImageFilter.Kernel(sizeKern3x3, kernAmBords)).save(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png', 'PNG')
				
			# Ouverture de l'image pour application du kernel (matrice)
			ouvIm=Image.open(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png')
				
			# Kernel 3x3 anti-crénelage
			sizeKern3x3=(3, 3)
			# Type de kernel utilisé
			kernAntiAlias=(1, 2, 3, 4, 5, 6, 7, 8, 9)
			# Application d'un anti-aliasing sur l'image (et donc sur les contours) par 
			# cette matrice. Cette excelllente matrice a été trouvée ici:
			# http://www.photo-lovers.org/mosaic.shtml.fr 
			# (voir à partir de Méthode du vecteur médian)
			#
			# Sauvegarde de l'image pour compositing
			ouvIm.filter(ImageFilter.Kernel(sizeKern3x3, kernAntiAlias)).save(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png')
			
			# Compatibilité entre linux et windows 
			# Dans la version windows ce n'est pas traité par un QProcess (comme sous 
			# Linux) mais directement avec os.system (car le QProcess avec la commande 
			# convert d'ImageMagick génère une erreur)
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				# Retour aux dimensions d'origine de l'image et enregistrement dans 
				# le rep temporaire (et ce pour le compositing ... et donc l'affichage
				# dans l'interface)
				process.start('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
			
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				os.system('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png'+"\"")
			
			imgFinal=Image.open(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png')
		
			# Compositing entre l'image avec le damier et l'image du fond 
			# vert/bleu decoupe
			ImageChops.composite(imgFinal, RedimQuad, imgFinal).save(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png')
			
			# Remplissage de listeAff_1 pour affichage (ds le tabwidget)
			listeAff_1.append(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png')
			# -------------------------------------------------------------------
			
			# On re-libere la memoire
			del imFILTsmooth, imgFinal
				
			# Remplissage de listeAff_1 pour affichage (ds le tabwidget)
			listeAff_1.append(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png')
			
			# --------------------------------------------------------------------
			# CALCUL ET AFFICHAGE DE LA DATE ET DU TEMPS DE RENDU
			# --------------------------------------------------------------------
			# Temps local (annee, mois, jour, heure, minute, seconde ...)
			tLocal=time.localtime()
			# Pour affichage de facon comprehensible de la date et l'heure
			datHeurEcr=_(u"Le ")+str(tLocal[2])+"/"+str(tLocal[1])+"/"+str(tLocal[0])+_(u" a ")+str(tLocal[3])+":"+str(tLocal[4])+":"+str(tLocal[5])
			# Positionnement au temps 2 pour le temps de rendu de l'image .
			t1=time.time()
			# Si le temps de rendu est inferieur a la minute ... .
			if int(t1-t0)<60 :
				# Pour affichage dans le terminal .
				affTerm=_("Temps de rendu : %s secondes") % (int(round(t1-t0)))
				#print
				#print datHeurEcr
				#print "=================================================="
				#print affTerm
				#print "=================================================="
				#print
				EkdPrint(u'')
				EkdPrint(u"%s" % datHeurEcr)
				EkdPrint(u"==================================================")
				EkdPrint(u"%s" % affTerm)
				EkdPrint(u"==================================================")
				EkdPrint(u'')
				# Pour affichage dans l'interface (variable)
				affTempsInterface=_("%s secondes") % (int(round(t1-t0)))
			# Si le temps de rendu est superieur a la minute ... calcul des 
			# minutes et des secondes .
			elif int(t1-t0)>=60 : 
				# Pour affichage dans le terminal
				affTerm=_(u"Temps de rendu : ")+str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
				#print
				#print datHeurEcr
				#print "=================================================="
				#print affTerm
				#print "=================================================="
				#print
				EkdPrint(u'')
				EkdPrint(u"%s" % datHeurEcr)
				EkdPrint(u"==================================================")
				EkdPrint(u"%s" % affTerm)
				EkdPrint(u"==================================================")
				EkdPrint(u'')
				# Pour affichage dans l'interface
				affTempsInterface=str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
			
			# Affichage de l'image temporaire 
			# Ouverture d'une boite de dialogue affichant l'aperçu.
			#
			# Affichage par le bouton Voir le résultat
			visio = VisionneurEvolue(self.repTampon+'decoupe_fond_tmp5ghy46s3y53k77w4.png')
			visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
			visio.exec_()
		
			return 0
			
			# Affichage des infos sur l'image --------------------	
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte=_(u" Image avant découpage du fond uni ")
			texte_2=_(u" Réglages(s)")
			texte_3=_(u" Résolution de l'image")
			texte_4=_(u" Temps de calcul de la découpe")
			a='#'*36
			
			self.infosImgProv=a+'\n# '+texte+'\n'+a+'\n'
			self.infosImgProv=self.infosImgProv+'\n'+self.listeChemin[0]+'\n\n'
			
			self.infosImgProv_2=a+'\n# '+texte_2+'\n'+a+'\n'
			self.infosImgProv_2=self.infosImgProv_2+'\n'+_(u'Valeur teinte (début) : ')+str(self.spinTeinteDebut.value())+'\n'+_(u'Valeur teinte (fin) : ')+str(self.spinTeinteFin.value())+'\n'+_(u'Valeur saturation (début) : ')+str(self.spinSaturationDebut.value())+'\n'+_(u'Valeur saturation (fin) : ')+str(self.spinSaturationFin.value())+'\n'+_(u'Valeur luminosité : ')+str(self.spinLuminosite.value())+'\n\n'
			
			self.infosImgProv_3=a+'\n# '+texte_3+'\n'+a+'\n'
			self.infosImgProv_3=self.infosImgProv_3+'\n'+str(widthDepart)+' x '+str(heightDepart)+_(u' pix')+'\n'+_(u"Nombre de pixels dans l'image : ")+str(nbPixelsTotal)+'\n\n'
			
			self.infosImgProv_4=a+'\n# '+texte_4+'\n'+a+'\n'
			self.infosImgProv_4=self.infosImgProv_4+'\n'+affTempsInterface+'\n\n'
			
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv+self.infosImgProv_2+self.infosImgProv_3+self.infosImgProv_4)
			self.framImg.setEnabled(True)
		
			# remise à 0 de la variable provisoire de log
			self.infosImgProv, self.infosImgProv_2, self.infosImgProv_3, self.infosImgProv_4='', '', '', ''
			# ----------------------------------------------------
			
			# On re-re-libere la memoire
			del tLocal, datHeurEcr, t0, t1, affTerm, affTempsInterface, texte, texte_2, texte_3, texte_4, a, self.infosImgProv, self.infosImgProv_2, self.infosImgProv_3, self.infosImgProv_4, nbPixelsTotal, listeAff_1, imageDepart, widthDepart, heightDepart, imagAlpha
			
			# Epuration/elimination des fichiers tampon
			for toutRepTemp in glob.glob(self.repTampon+'*.*'):
				os.remove(toutRepTemp)
				
			self.operationReussie()
			
		except:
			#print "ERREUR !"
			EkdPrint(u"ERREUR !")
			QMessageBox.warning(None, _(u"Erreur"), _(u"<p><b>Attention opération annulée pour la visualisation de la découpe du Masque alpha (méthode 2):</b> modifiez les valeurs de <font color=blue><b>Teinte (début)</b></font> et/ou <font color=blue><b>Teinte (fin)</b></font>, </font><font color=blue><b>Saturation (début)</b></font> et/ou <font color=blue><b>Luminosité</b></font> dans l'onglet <b>Réglages du masque</b>.<p>Cliquez sur le bouton '<b>OK</b>' juste en dessous, changez les valeurs comme dit juste avant, et relancez la visualisation par le bouton <b>'Voir le résultat'</b>.</p>"))
	
	
	def meth_2_ReglagMasqueAlpha(self):
		""" Masque alpha (découpe) pour la méthode 2 """
		
		# Cette fonction gere les chemins avec trous .
	
		try :

			# Epuration/elimination des fichiers tampon
			l_RepTemp=glob.glob(self.repTampon+'*.*')
			if len(l_RepTemp)>0: 
				for toutRepTemp in l_RepTemp: os.remove(toutRepTemp)

			# Récupération de la liste des fichiers chargés
			self.listeChemin=self.afficheurImgSource.getFiles()
		
			# Liste pour affichage image découpée (ds le tabwidget)
			listeAff_1=[]
			# Liste pour affichage dans la page Info
			listeAff_2=[]

			# Nbre d'images charges par l'utilisateur
			nbreElem=len(self.listeChemin)	

			# Compteur pour le calcul du temps de rendu cumule.
			som_t_renduCumul=0 

			# Compteur pour le 1er temps de rendu (exactement la meme variable
			# que pour ==> Positionnement au temps 1 pour le temps de rendu de 
			# l'image, juste en-dessous) .
			t0=0 

			# Positionnement au temps 1 pour le temps de rendu de l'image .
			temps1=time.localtime(time.time())	

			# Boucle principale de chargement des images .
			for parcPrincipal in range(nbreElem):
			
				# Ouverture de l'image dans le lot
				imageDepart=Image.open(self.listeChemin[parcPrincipal])
	
				# Compteur pour le 1er temps de rendu .
				t0=time.time()
			
				# On recupere la taille de l'image
				widthDepart, heightDepart=imageDepart.size
				# On recupere le nombre de pixels totaux
				nbPixelsTotal=widthDepart*heightDepart
				
				# Compatibilité entre linux et windows
				# Dans la version windows ce n'est pas traité par un QProcess (comme sous 
				# Linux) mais directement avec os.system (car le QProcess avec la commande 
				# convert d'ImageMagick génère une erreur)
			
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					process = QProcess(self)
			
				# Si on a sélectionné Qualité Moyenne
				if self.comboQualite.currentIndex()==0:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*1.4))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*1.4))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
						
				# Si on a sélectionné Qualité Bonne
				elif self.comboQualite.currentIndex()==1:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*1.6))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*1.6))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
						
				# Si on a sélectionné Qualité Tres bonne
				elif self.comboQualite.currentIndex()==2:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*1.8))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*1.8))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
						
				# Si on a sélectionné Qualité Excellente
				elif self.comboQualite.currentIndex()==3:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*2))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*2))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\"")
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					if not process.waitForStarted(3000):
						QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
					process.waitForFinished(-1)
			
				imgOuv_1_tmp=Image.open(self.repTampon+"decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png")
		
				# Creation de l'array avec les donnees de l'image chargee
				imageData=array(imgOuv_1_tmp.getdata())

				# Collecte des coordonnees x (methode tout avec Numpy --> modulo)
				coord_X_1=remainder(arange(imageData.shape[0]), imgOuv_1_tmp.size[0]) 
				# Collecte des coordonnees y (methode tout avec Numpy --> division)
				coord_Y_1=divide(arange(imageData.shape[0]), imgOuv_1_tmp.size[0])
		
				# Remplissage d'un array (tableau) avec toutes les coordonnes de 
				# la grille, comme ceci :
				# array([[0, 0],
				#	 [1, 0],
				#	 [2, 0], ..., [0, 1], [1, 1], [2, 1], ..., [500, 50], ...]
				coord_XY=column_stack((coord_X_1, coord_Y_1))
		
				# Calcul de la valeur max . Exemple : [..., [12, 789, 1], [89, 567, 7],
				# ...] donne comme resultat : [[..., 789, 567, ...]] .
				maxRGB=imageData.max(axis=1)
	
				# Conversion en float
				maxRGB=maxRGB.astype(float)
	
				# ------------------------------------------------------------------
				# CALCUL DE Hue (avec des valeurs arrondies a 2 chiffres apres la
				# virgule) .
				# TEINTE
				# ------------------------------------------------------------------
				h_HSV=(angle(inner(imageData, c_[1,exp(2j*pi/3.),exp(-2j*pi/3.)]))*180/pi)%360

				# ------------------------------------------------------------------
				# CALCUL DE Saturation	(imageData.ptp(axis=1) ==>
				# maxRGB-minRGB)
				# On obtient a la fin un pourcentage (*100). SATURATION
				# ------------------------------------------------------------------
				s_HSV=round_(imageData.ptp(axis=1)/maxRGB, decimals=2)*100
	
				# ------------------------------------------------------------------
				# CALCUL DE Value. Calcul du pourcentage. LUMINOSITE
				# ------------------------------------------------------------------
				v_HSV=(imageData.max(axis=1))*100/256 # Avec pourcentage
	
				# Concatenation des colonnes . Exemple :
				# [[0, 1],
				#  [2, 3],
				#  [4, 5]] donne comme resultat : [[0, 2, 4], [1, 3, 5]]
				hsv=column_stack((h_HSV, s_HSV, v_HSV)).astype(int)
		
				# Concatenation des valeurs entre elles . Le tableau genere est
				# sous la forme [[x1 y1 h1 s1 v1] [x2 y2 h2 s2 v2] ... ]
				conc_XY_RGB=c_[coord_XY, hsv]
	
				# --------------------------------------------------------------
				# Collecte/selection des coordonnes x et y, valeurs de Hue, valeurs de
				# Saturation, valeurs de Value selon les reglages faits par 
				# l'utilisateur .
				# Collecte non dans une boucle, mais avec la syntaxe de Numpy .	
				condition_1=((conc_XY_RGB.take([0], axis=1).ravel()>=0) & (conc_XY_RGB.take([1], axis=1).ravel()>=0) & (conc_XY_RGB.take([2], axis=1).ravel()>self.spinTeinteDebut.value()) & (conc_XY_RGB.take([2], axis=1).ravel()<self.spinTeinteFin.value()) & (conc_XY_RGB.take([3], axis=1).ravel()>self.spinSaturationDebut.value()+4) & (conc_XY_RGB.take([3], axis=1).ravel()<self.spinSaturationFin.value()+4) & (conc_XY_RGB.take([4], axis=1).ravel()>self.spinLuminosite.value()-4) & (conc_XY_RGB.take([4], axis=1).ravel()<100))
	
				# Resultat de la condition juste au-dessus .
				selection_1=conc_XY_RGB[condition_1]
	
				# Collecte des coordonnes x et y exactes des pixels bleus/verts dans 
				# l'image. Les autres donnees ne sont pas prises en compte . Selection 
				# des coordonnees x et y avec la syntaxe de Numpy.
				a1=selection_1[:,0]
				a2=selection_1[:,1]
	
				# Mise en forme des cordonnes x et y dans le tableau
				listePrecisCoordonnees=column_stack((a1, a2))
		
				# Collecte de la couleur RGB a la position x=0, y=0 .
				data_1er_pixel=imgOuv_1_tmp.getpixel((0, 0))
	
				# Conversion en RGBA de l'image. RGB+Canal Alpha
				if imgOuv_1_tmp.mode!="RGBA": imagAlpha=imgOuv_1_tmp.convert("RGBA")
				else: imagAlpha=imgOuv_1_tmp
			
				# Ouverture de l'image avec le fond en damier
				imQuad=Image.open("gui_modules_lecture"+os.sep+"affichage_image"+os.sep+"ekd_quadrillage_canal_alpha.png")
				# Redimensionnement de l'image du damier (quadrillage) aux 
				# dimensions de la premiere image chargee .
				RedimQuad=imQuad.resize(imageDepart.size, Image.ANTIALIAS)
		
				# Copie de l'image quadrillage dans le répertoire tampon
				shutil.copy('gui_modules_lecture'+os.sep+'affichage_image'+os.sep+'ekd_quadrillage_canal_alpha.png', self.repTampon)
			
				# Transformation des pixels bleus ou verts du fond
				# en pixels transparents (RGBA --> A=0)
				ecrPix_1=ImageDraw.Draw(imagAlpha)	
				for parcoursXY in listePrecisCoordonnees:
					# Decoupe du fond (enfin le fond devient completement
					# transparent)
					leFondDevTransp=ecrPix_1.point(parcoursXY, (data_1er_pixel[0], data_1er_pixel[1], data_1er_pixel[2], 0))

				# -------------------------------------------------------------------
				# Sélection des pixels contigus autour du perso/forme (ceux les +
				# proches) --
				# -------------------------------------------------------------------
				# Selection des pixels contigus (c'est a dire ceux qui touchent le
				# personnage/la forme qui sera decoupe(e)) .
				# -------------------------------------------------------------------
				# Calcul des coordonnees cote gauche -->* (pixels de gauche)
				condit_2=where(listePrecisCoordonnees[1:].take([0], axis=1).ravel()>(listePrecisCoordonnees[:-1]+1).take([0], axis=1).ravel())
				# Resultat de la condition juste au-dessus .
				koko_1=listePrecisCoordonnees[condit_2]
				# -------------------------------------------------------------------
				# Inversion du tableau pour calcul des pix de droite ; Exemple : 
				# [[3, 127], [81, 127], [3, 3], [95, 3], [47, 3], [347, 3]] devient
				# [[347, 3], [47, 3], [95, 3], [3, 3], [81, 127], [3, 127]] .
				inversionPourCond_3=listePrecisCoordonnees[::-1]
				# Calcul des coordonnees cote droit *<-- (pixels de droite)
				conditInvers=where(inversionPourCond_3[1:].take([0], axis=1).ravel()<(inversionPourCond_3[:-1]-1).take([0], axis=1).ravel())
				# Resultat de la condition juste au-dessus. Et de nouveau inversion.
				koko_2=inversionPourCond_3[conditInvers][::-1]
				# Mise en forme des cordonnes x et y dans le tableau .
				l_coordXYcontigues=vstack((koko_1, koko_2))
				# -------------------------------------------------------------------
				# De nouveau merci a Gael Varoquaux pour cette methode de classement
				# juste en dessous (methode par une fonction) .
				def foncRemisEnOrdre(k_a, k_b) :
					if k_a[1] > k_b[1] : return 1
					elif k_a[1] < k_b[1] : return -1
					elif k_a[0] > k_b[0] : return 1
					elif k_a[0] < k_b[0] : return -1
					else : return 0
				# Creation d'une liste avec les donnes du tableu 
				# cree precedemment .
				listeXYcoordContig=l_coordXYcontigues.tolist()
				# Remise en ordre suivant le calcul dans la fonction 
				# foncRemisEnOrdreDFVA .
				listeXYcoordContig.sort(cmp=foncRemisEnOrdre)
				# Creation d'un tableau a partir de la liste .
				l_coordXYcontigues=array(listeXYcoordContig)
				# -------------------------------------------------------------------
	
				# -------------------------------------------------------------------
				# Sélection pour découpe des pixels (les pixels du contour du
				# perso/forme) --
				# -------------------------------------------------------------------
				# Compteur
				conptD_1=0
				# Decoupe des pixels contigus (niveau 1 ==> liste l_Decoup_1)
				l_Decoup_1=[]
				# Decoupe des pixels contigus (niveau 2 ==> liste l_Decoup_2)
				l_Decoup_2=[]
				# Decoupe des pixels contigus (niveau 3 ==> liste l_Decoup_3)
				l_Decoup_3=[]
	
				for parcDecoup_X, parcDecoup_Y in l_coordXYcontigues:
		
					# Si l'id du compteur est pair ca se decale sur la droite .
					if conptD_1%2==0 :
						# Incrementation niv 1 de la valeur de x --> (x, y) 
						# a +1
						parcDecoup_X=parcDecoup_X+1
						l_Decoup_1.append((parcDecoup_X, parcDecoup_Y))
						# Incrementation niv 2 de la valeur de x --> (x, y) 
						# a +1
						parcDecoup_X=parcDecoup_X+1 
						l_Decoup_2.append((parcDecoup_X, parcDecoup_Y)) 
						# Incrementation niv 3 de la valeur de x --> (x, y) 
						# a +1
						parcDecoup_X=parcDecoup_X+1 
						l_Decoup_3.append((parcDecoup_X, parcDecoup_Y)) 
			
					# Si l'id du compteur est impair ca se decale sur la gauche
					elif conptD_1%2==1 :
						# Incrementation niv 1 de la valeur de x --> (x, y) 
						# a -1
						parcDecoup_X=parcDecoup_X-1
						l_Decoup_1.append((parcDecoup_X, parcDecoup_Y))	
						# Incrementation niv 2 de la valeur de x --> (x, y) 
						# a -1
						parcDecoup_X=parcDecoup_X-1 
						l_Decoup_2.append((parcDecoup_X, parcDecoup_Y)) 
						# Incrementation niv 3 de la valeur de x --> (x, y) 
						# a -1
						parcDecoup_X=parcDecoup_X-1 
						l_Decoup_3.append((parcDecoup_X, parcDecoup_Y)) 
											
					conptD_1=conptD_1+1
				# -------------------------------------------------------------------

				# -------------------------------------------------------------------
				# Selection et mise en relation ds une liste des couleurs aux
				# coordonnes x et y definies juste au dessus . A la fin les listes
				# sont sous cette forme : [..., ((x, y), (R, G, B, A)), ...]
				# -------------------------------------------------------------------
				############ Retiré le 12/04/09 #####################################
				'''
				lll_1=zip(l_Decoup_1, [imagAlpha.getpixel(bbb_1) for bbb_1 in l_Decoup_1])
				lll_2=zip(l_Decoup_2, [imagAlpha.getpixel(bbb_2) for bbb_2 in l_Decoup_2])
				lll_3=zip(l_Decoup_3, [imagAlpha.getpixel(bbb_3) for bbb_3 in l_Decoup_3])
				'''
				#####################################################################
				lll_1=zip(l_Decoup_1, [imagAlpha.getpixel((int(bbb_1[0]), int(bbb_1[1]))) for bbb_1 in l_Decoup_1])
				lll_2=zip(l_Decoup_2, [imagAlpha.getpixel((int(bbb_2[0]), int(bbb_2[1]))) for bbb_2 in l_Decoup_2])
				lll_3=zip(l_Decoup_3, [imagAlpha.getpixel((int(bbb_3[0]), int(bbb_3[1]))) for bbb_3 in l_Decoup_3])
				# -------------------------------------------------------------------
							
				# -------------------------------------------------------------------
				# Traitement de l'image ... decoupe/application du fond transparent
				# (du liseret 1) immediatement autour du perso ou forme .
				ecrPixBordur1=ImageDraw.Draw(imagAlpha)
				for parcBordurXY_1, parcBordurCoul_1 in lll_1 :
					# Découpe du liseret (enfin le liseret devient + ou -
					# transparent)
					ecrPixBordur1.point(parcBordurXY_1, (parcBordurCoul_1[0], parcBordurCoul_1[1], parcBordurCoul_1[2], 10))
		
				# Traitement de l'image ... decoupe/application du fond transparent
				# (du liseret 2) immediatement autour du perso ou forme.	
				ecrPixBordur2=ImageDraw.Draw(imagAlpha)
				for parcBordurXY_2, parcBordurCoul_2 in lll_2 : 
					# Découpe du liseret (enfin le liseret devient + ou -
					# transparent)
					ecrPixBordur2.point(parcBordurXY_2, (parcBordurCoul_2[0], parcBordurCoul_2[1], parcBordurCoul_2[2], 100)) 
		
				# Traitement de l'image ... decoupe/application du fond transparent
				# (du liseret 3) immediatement autour du perso ou forme .	
				ecrPixBordur3=ImageDraw.Draw(imagAlpha)
				for parcBordurXY_3, parcBordurCoul_3 in lll_3 : 
					# Découpe du liseret (enfin le liseret devient + ou -
					# transparent)
					ecrPixBordur3.point(parcBordurXY_3, (parcBordurCoul_3[0], parcBordurCoul_3[1], parcBordurCoul_3[2], 200)) 
				# -------------------------------------------------------------------
		
				# On libere la memoire
				del coord_X_1, coord_Y_1, coord_XY, maxRGB, h_HSV, s_HSV, v_HSV, hsv, conc_XY_RGB, condition_1, selection_1, a1, a2, listePrecisCoordonnees, data_1er_pixel, leFondDevTransp, condit_2, koko_1, inversionPourCond_3, conditInvers, koko_2, l_coordXYcontigues, l_Decoup_1, l_Decoup_2, l_Decoup_3, lll_1, lll_2, lll_3, ecrPixBordur1, ecrPixBordur2, ecrPixBordur3

				# -------------------------------------------------------------------
				# PARTIE FINALE DU RENDU
				# -------------------------------------------------------------------
				# Application d'un leger lissage de l'image
				imFILTsmooth=imagAlpha.filter(ImageFilter.SMOOTH)	
				# Compositing entre l'image avec lissage et l'image tampon
				ImageChops.composite(imFILTsmooth, imagAlpha, imagAlpha).save(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png', 'PNG')
			
				# Ouverture de l'image pour application du kernel (matrice)
				imk=Image.open(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png')
				# Kernel 3x3 pour amélioration des bords. L'image devient plus nette.
				sizeKern3x3=(3, 3) 
				# Matrice trouvee ici: http://blogs.codes-sources.com/tkfe/archive/2005/04/15/6004.aspx
				kernAmBords=(-1, -2, -1, -2, 16, -2, -1, -2, -1)
				imKernelAmBords=imk.filter(ImageFilter.Kernel(sizeKern3x3, kernAmBords)).save(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png', 'PNG')
			
				# Ouverture de l'image pour application du kernel (matrice)
				ouvIm=Image.open(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png')
			
				# Kernel 3x3 anti-crénelage
				sizeKern3x3=(3, 3)
				# Type de kernel utilisé
				kernAntiAlias=(1, 2, 3, 4, 5, 6, 7, 8, 9)
				# Application d'un anti-aliasing sur l'image (et donc sur les contours) par 
				# cette matrice. Cette excelllente matrice a été trouvée ici:
				# http://www.photo-lovers.org/mosaic.shtml.fr 
				# (voir à partir de Méthode du vecteur médian)
				#
				# Sauvegarde de l'image pour compositing
				ouvIm.filter(ImageFilter.Kernel(sizeKern3x3, kernAntiAlias)).save(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png', 'PNG')
			
				# Chemin de sauvegarde
				vraiCheminSauv=self.chemDossierSauv+'_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'
				
				# Compatibilité entre linux et windows
				# Dans la version windows ce n'est pas traité par un QProcess (comme sous 
				# Linux) mais directement avec os.system (car le QProcess avec la commande 
				# convert d'ImageMagick génère une erreur)
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					# Retour aux dimensions d'origine de l'image et enregistrement 
					# dans le rep temporaire (et ce pour la sauvegarde de l'image 
					# --> utilisateur)
					process.start('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\""+' '+"\""+vraiCheminSauv+"\"")
			
					if not process.waitForStarted(3000):
						QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
					process.waitForFinished(-1)
					
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\""+' '+"\""+vraiCheminSauv+"\"")
				
				# Compatibilité entre linux et windows
				# Dans la version windows ce n'est pas traité par un QProcess (comme sous 
				# Linux) mais directement avec os.system (car le QProcess avec la commande 
				# convert d'ImageMagick génère une erreur)
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:	
					# Retour aux dimensions d'origine de l'image et enregistrement dans 
					# le rep temporaire (et ce pour le compositing ... et donc l'affichage
					# dans l'interface)
					process.start('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'+"\"")
			
					if not process.waitForStarted(3000):
						QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
					process.waitForFinished(-1)
					
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx.png'+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'+"\"")
				
				imgFinal=Image.open(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
	
				# Compositing entre l'image avec le damier et l'image du fond 
				# vert/bleu decoupe
				ImageChops.composite(imgFinal, RedimQuad, imgFinal).save(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
		
				# Remplissage de listeAff_1 pour affichage (ds le tabwidget)
				listeAff_1.append(self.repTampon+'decoupe_fond_tmpt6x5q56fvw9qf6q6qx_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
				
				# Ajout des images dans la liste self.listeImgDestin. Cette liste
				# sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(listeAff_1[parcPrincipal])
				# -------------------------------------------------------------------
		
				# On re-libere la memoire
				del imFILTsmooth, imgFinal
			
				# ------------------------------------------------------------------ #
				# STATS DE RENDU (AFFICHAGE ET SAUVEGARDE) .
				# ------------------------------------------------------------------ #
				# Calcule le pourcentage effectue a chaque passage
				val_pourc=((parcPrincipal+1)*100)/nbreElem
				# Affichage du pourcentage du rendu dans le terminal
				# sous Linux ou la fenetre MS-DOS sous Windows
				#print _("Progression du rendu :"), val_pourc
				EkdPrint(_(u"Progression du rendu: %s") % val_pourc)
				# Positionnement au temps 2 pour le temps de rendu de l'image
				t1=time.time()
				# Temps local (annee, mois, jour, heure, minute, seconde ...)
				tLocal=time.localtime()
				# Calcul avec le compteur pour le calcul du temps de rendu cumule
				som_t_renduCumul=som_t_renduCumul+(t1-t0)
				# Calcul pour la moyenne du temps de rendu .
				MoyRendu=som_t_renduCumul/(parcPrincipal+1) 
				# Calcul pour le temps de rendu restant .
				tempRestant=((MoyRendu*nbreElem)-(MoyRendu*parcPrincipal+1))-MoyRendu 
				# Mise en ordre du temps local pour ecriture dans fichier
				datHeurEcr=_(u"Le ")+str(tLocal[2])+"/"+str(tLocal[1])+"/"+str(tLocal[0])+_(u" a ")+str(tLocal[3])+":"+str(tLocal[4])+":"+str(tLocal[5])
		
				# Pour ecriture dans fichier
				progImg=_(u"Image ")+str(parcPrincipal+1)+"/"+str(nbreElem)
		
				# Si le temps de rendu est inferieur a la minute ... .
				if int(t1-t0)<60:
					affTemps=_(u"Temps de rendu : %s secondes") % (int(round(t1-t0)))
				# Si le temps de rendu est superieur a la minute ... calcul des 
				# minutes et des secondes
				elif int(t1-t0)>=60:
					affTemps=_(u"Temps de rendu : ")+str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
				# Si la moyenne du temps de rendu est inferieur a la minute ... .	
				if MoyRendu<60:
					moyTemps=_(u"Moyenne du temps de rendu : %s secondes") % (int(round(MoyRendu))) 
				# Si la moyenne du temps de rendu est superieur a la minute ...  
				# calcul des minutes et des secondes .
				elif MoyRendu>=60:
					moyTemps=_(u"Moyenne du temps de rendu : ")+str(int(round(MoyRendu/60)))+_(u" min ")+str(int(round(MoyRendu%60)))+_(u" sec")
				# Si le temps de rendu est inferieur a la minute ... .
				if som_t_renduCumul<60:
					tRenduCumul=_(u"Temps de rendu cumule : %s secondes") % (int(round(som_t_renduCumul)))
				# Si le temps de rendu est superieur ou egal a la minute ... calcul des 
				# heures et des minutes .
				elif som_t_renduCumul>=60:
					tRenduInfMinut=int(round(som_t_renduCumul/60)) 
					tRenduCumul=_(u"Temps de rendu cumule : ")+str(tRenduInfMinut/60)+_(u" h ")+str(tRenduInfMinut%60)+_(u" min")
				
				# Pour le temps de rendu restant ...
				# Si le temps de rendu restant est superieur a 0 secondes .
				if tempRestant>0:
					# Si le temps de rendu restant est inferieur a la minute et le
					# calcul du pourcentage est inferieur a 100 %.
					if tempRestant<60 and val_pourc<100:
						tRestant=_(u"Temps de rendu restant (estimation) : %s secondes") % (int(round(tempRestant)))
					# Si le temps de rendu restant est superieur a la minute et le
					# calcul du pourcentage est inferieur a 100 % .
					elif tempRestant>=60 and val_pourc<100:
						tRestantInfMinut=int(round(tempRestant/60))
						tRestant=_(u"Temps de rendu restant (estimation) : ")+str(tRestantInfMinut/60)+_(u" h ")+str(tRestantInfMinut%60)+_(u" min")
			
				# Des que le rendu est arrive a 100%, affichage de dans le
				# terminal sous Linux ou la fenetre MS-DOS sous Windows
				if val_pourc==100 :
					#print
					EkdPrint(u'')
					#print _("Fini !")
					EkdPrint(_(u"Fini !"))

				# Ecriture des statistiques (cumul de l'ecriture) dans un fichier texte	
				ecrStatRendu=open(self.chemDossierSauv+_("_image_masque_alpha_meth_2.txt"), 'a')
				ecrStatRendu.write("=================================================\n"+str(datHeurEcr)+"\n"+"-------------------------------------------------\n"+str(progImg)+"\n"+str(affTemps)+"\n"+str(moyTemps)+"\n"+str(tRenduCumul)+"\n\n")
				ecrStatRendu.close()
			
				# Remplissage de la liste pour les statistiques de rendu
				listeAff_2.append((_(u"Image chargée : ")+self.listeChemin[parcPrincipal], _(u"Image finale : ")+vraiCheminSauv, progImg, affTemps, moyTemps, tRenduCumul, _(u"Nombre total de pixels : ")+str(nbPixelsTotal), _("Dimension : ")+str(widthDepart)+' x '+str(heightDepart)))

				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée
				# Bouton Cancel pour arrêter la progression donc le process
				self.progress.setValue(val_pourc)
				QApplication.processEvents()
				if (self.progress.wasCanceled()): break
				# Quand l'utilisateur charge au moins 2 images ...
				if len(self.listeChemin)>1:
					self.progress.setLabel(QLabel(QString(tRestant)))
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
		
			# Affichage des infos sur l'image -------------------------	
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte=_(u" Statistiques de rendu")
			a='#'*36
			b="-"*36
		
			self.infosImgProv=a+'\n#'+texte+'\n'+a+'\n'
			for parcStatRendu in listeAff_2:
				self.infosImgProv=self.infosImgProv+'\n'+parcStatRendu[0]+'\n'+parcStatRendu[1]+'\n'+parcStatRendu[2]+'\n'+parcStatRendu[3]+'\n'+parcStatRendu[4]+'\n'+parcStatRendu[5]+'\n'+parcStatRendu[6]+'\n'+parcStatRendu[7]+'\n'+b+'\n'
			
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv)
			self.framImg.setEnabled(True)
		
			# remise à 0 de la variable provisoire de log
			self.infosImgProv=''
			# ---------------------------------------------------------
			
			self.operationReussie()

		except :
			#print "ERREUR !"
			EkdPrint(u"ERREUR !")
			QMessageBox.warning(None, _(u"Erreur"), _(u"<p><b>Attention opération annulée pour Masque alpha (méthode 2):</b> modifiez les valeurs de <font color=blue><b>Saturation (début)</b></font> et de <font color=blue><b>Luminosité</b></font> dans l'onglet <b>Réglages du masque</b>.<p>Cliquez sur le bouton '<b>OK</b>' juste en dessous, puis sur '<b>Arrêter le processus</b>' de la fenêtre de progression.</p><p>Une solution possible est de charger l'image qui pose problème, changer les valeurs de 'Saturation (début)' et de 'Luminosité' et voir le résultat avec le bouton 'Voir le résultat'. Une fois que cela est fait, chargez le lot d'images et faites le traitement (avec les bons réglages).</p>"))

	
	def meth_2_ReglagMasque3D(self):
		
		""" Masque 3D pour la méthode 2. On utilise les méthodes de calcul de la méthode 1 et 
		avec quelques principes de la méthode 2 (sélection de la qualité --> self.comboQualite)"""

		# Cette fonction gere les chemins avec trous
	
		try :
			
			# Epuration/elimination des fichiers tampon
			l_RepTemp=glob.glob(self.repTampon+'*.*')
			if len(l_RepTemp)>0: 
				for toutRepTemp in l_RepTemp: os.remove(toutRepTemp)

			# Récupération de la liste des fichiers chargés
			self.listeChemin=self.afficheurImgSource.getFiles()
			
			# Liste pour affichage image découpée (ds le tabwidget)
			listeAff_1=[]
			# Liste pour affichage dans la page Info
			listeAff_2=[]
		
			# Nbre d'images charges par l'utilisateur
			nbreElem=len(self.listeChemin)

			# Compteur pour le calcul du temps de rendu cumule.
			som_t_renduCumul=0 
	
			# Compteur pour le 1er temps de rendu (exactement la meme variable
			# que pour ==> Positionnement au temps 1 pour le temps de rendu de 
			# l'image, juste en-dessous) .
			t0=0 

			# Positionnement au temps 1 pour le temps de rendu de l'image .
			temps1=time.localtime(time.time())	
	
			# Boucle principale de chargement des images .
			for parcPrincipal in range(nbreElem):
				
				# Ouverture de l'image dans le lot
				imageDepart=Image.open(self.listeChemin[parcPrincipal])
		
				# Compteur pour le 1er temps de rendu .
				t0=time.time()

				# On recupere la taille de l'image originelle
				widthDepart, heightDepart=imageDepart.size
				# On recupere le nombre de pixels totaux
				nbPixelsTotal=widthDepart*heightDepart
				
				# Compatibilité entre linux et windows
				# Dans la version windows ce n'est pas traité par un QProcess (comme sous
				# Linux) mais directement avec os.system (car le QProcess avec la commande
				# convert d'ImageMagick génère une erreur)
			
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					process = QProcess(self)
				
				# Si on a sélectionné Qualité Moyenne
				if self.comboQualite.currentIndex()==0:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*1.4))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*1.4))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
					
				# Si on a sélectionné Qualité Bonne
				elif self.comboQualite.currentIndex()==1:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*1.6))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*1.6))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
						
				# Si on a sélectionné Qualité Tres bonne
				elif self.comboQualite.currentIndex()==2:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*1.8))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*1.8))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
					
				# Si on a sélectionné Qualité Excellente
				elif self.comboQualite.currentIndex()==3:
					
					# Uniquement pour Linux et MacOSX
					if os.name in ['posix', 'mac']:
						process.start('convert -resize '+str(round(imageDepart.size[0]*2))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
					# Uniquement pour windows
					elif os.name == 'nt':
						os.system('convert -resize '+str(round(imageDepart.size[0]*2))+'x '+"\""+"".join(self.listeChemin[parcPrincipal])+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\"")
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					if not process.waitForStarted(3000):
						QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
					process.waitForFinished(-1)
				
				imgOuv_1_tmp=Image.open(self.repTampon+"decoupe_fond_tmpds56682qd35az2d8u9hl.png")
				
				# On recupere le tableau de pixels (image aggrandie)
				imageData=imgOuv_1_tmp.getdata()
				
				# On recupere la taille de l'image (image aggrandie)
				width_2, height_2=imgOuv_1_tmp.size
				# On recupere le nombre de pixels totaux (image aggrandie)
				nbPixelsTotal_2=width_2*height_2
 
				#-----------------------------------------------
				# Algorithme de detection du fond bleu/vert
				#-----------------------------------------------

				# On boucle sur l'image RVB -> on cree une nouvelle image RVBA, 
				# le fond bleu/vert est supprime . De plus on va stocker les 
				# pixels de bord .
				newImageRGBA=[]

				for parcRGB in range(nbPixelsTotal_2):
    					# On recupere les valeurs R,G et B
					val_R_rgb=imageData[parcRGB][0]
    					val_G_rgb=imageData[parcRGB][1]
    					val_B_rgb=imageData[parcRGB][2]
    
    					# ------------------------------- #
    					# On calcule les valeurs de H,S,V #
    					# ------------------------------- #
    					# On detecte le max et le min
    					maxRGB=float(max(imageData[parcRGB]))
    					minRGB=float(min(imageData[parcRGB]))
    					# Calcule de la difference entre min et max
    					deltaRGB=maxRGB-minRGB
    					# Calcul de la Saturation
    					if maxRGB>0: s_HSV=(deltaRGB/maxRGB)*100
    					else: s_HSV=0
    					# Calcul de Hue (Teinte)
    					if deltaRGB==0: h_HSV=-1
    					elif val_R_rgb==maxRGB: h_HSV=(val_G_rgb-val_B_rgb)/deltaRGB
    					elif val_G_rgb==maxRGB: h_HSV=2+(val_B_rgb-val_R_rgb)/deltaRGB
    					else: h_HSV=4+(val_R_rgb-val_G_rgb)/deltaRGB
					# Conversion en degres de Hue
    					h_HSV=h_HSV*60
    					if h_HSV<0: h_HSV=h_HSV+360
    					# Calcul de Value (Luminosite)
    					v_HSV=maxRGB
					# Pourcentage de 0 à 100 de Value (il est beaucoup plus
					# pratique de travailler avec une valeur entre 0 et 100)
					v_HSV=v_HSV*100/256
					
					# ----------------------------------------------------------- #
					# Attentions conditions d'affichage du fond et de la forme !.
					# ----------------------------------------------------------- #
					# Ici si on a sélectionné un fond noir et une/des formes blanches
					if self.comboFondForme.currentIndex()==0:
						# On teste si le pixel appartient au fond ou non
    						if self.spinTeinteDebut.value()<=h_HSV<=self.spinTeinteFin.value() and self.spinSaturationDebut.value()<=s_HSV<=self.spinSaturationFin.value() and self.spinLuminosite.value()<=v_HSV<=100:
							
        						# Si oui, on affecte du noir et de la 
							# transparence (A=0) au pixel
        						newImageRGBA.append((0, 0, 0, 0))
    						else :
        						# Si non, on affecte du blanc avec une transparence a 100%
        						newImageRGBA.append((255, 255, 255, 255))
					# Là si on a sélectionné un fond blanc et une/des formes noires
					elif self.comboFondForme.currentIndex()==1:
						# On teste si le pixel appartient au fond ou non
    						if self.spinTeinteDebut.value()<=h_HSV<=self.spinTeinteFin.value() and self.spinSaturationDebut.value()<=s_HSV<=self.spinSaturationFin.value() and self.spinLuminosite.value()<=v_HSV<=100:
							
        						# Si oui, on affecte du blanc et de la 
							# transparence (A=0) au pixel
        						newImageRGBA.append((255, 255, 255, 0))
    						else :
        						# Si non, on affecte du noir avec une transparence a 100%
        						newImageRGBA.append((0, 0, 0, 255))
					
				#-----------------------------------------------
				# Fin algo detection fond bleu/vert
				#-----------------------------------------------

				# On sauvegarde l'image avant anti-aliasing
				imgDecoup=Image.new('RGBA', imgOuv_1_tmp.size)
				imgDecoup.putdata(newImageRGBA)
		
				# On libere de la memoire
				del imageData

				#---------------------------------------------------------------------------
				# On supprimme la premiere ligne bleue (si fond bleu) 
				# restante autour du personnage. Début d'anti-aliasing
				antialiasing=[]

				for parcSupprimeLigne in range(nbPixelsTotal_2):
    					# Si le pixel detecte n'est pas transparent
    					if newImageRGBA[parcSupprimeLigne][3]>0:
        					y_ligne=math.ceil((parcSupprimeLigne-1)/width_2)
        					x_ligne=parcSupprimeLigne-(y_ligne*width_2)
        					# Detection des bords
        					if (x_ligne==0 or x_ligne>=width_2-1 or y_ligne==0 or y_ligne>=height_2-1):
							antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
        					else:
            						# Si on a 1 voisin transparent bord
            						# Sinon -> pas bord
            						# On teste (x-1,y),(x+1,y),(x,y-1),(x,y+1)
            						if (newImageRGBA[parcSupprimeLigne-1][3]==0 or newImageRGBA[parcSupprimeLigne+1][3]==0 or newImageRGBA[parcSupprimeLigne-width_2][3]==0 or newImageRGBA[parcSupprimeLigne+width_2][3]==0):
                						# Si bord existe -> on efface . Le bord en
								# question est transforme en R, G, B -->
								# noir et A --> transparent .
                						antialiasing.append((0, 0, 0, 0))
            						else :
                						antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], newImageRGBA[parcSupprimeLigne][3]))
    					else :
        					antialiasing.append((newImageRGBA[parcSupprimeLigne][0], newImageRGBA[parcSupprimeLigne][1], newImageRGBA[parcSupprimeLigne][2], 0))

				newImageRGBA=antialiasing
				#---------------------------------------------------------------------------
				
				# Creation d'une nouvelle image et integration des donnees recoltees .
				newImageAntialias=Image.new('RGBA', imgDecoup.size)
				newImageAntialias.putdata(antialiasing)
				a1, a2, a3, a4=newImageAntialias.split()
				imgMerge=Image.merge('RGBA', (a1, a2, a3, a4))
		
				# Transformation du fond noir transparent en fond noir opaque 
				imgMerge.putalpha(255)
		
				# Sauvegarde de la nouvelle image (image tampon)
				imgMerge.save(self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png', 'PNG')
				
				# Ouverture de l'image tampon
				ouvIm=Image.open(self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png')
			
				# Kernel 5x5 Floutage
				sizeKern5x5=(5, 5)
				# Type de kernel utilisé
				kernFlou=(0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0)
				# Application d'un leger flou a l'image et enregistrement dans le
				# chemin (et avec le nom donné) et ce par/pour l'utilisateur
				vraiCheminSauv=self.chemDossierSauv+'_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'
				ouvIm.filter(ImageFilter.Kernel(sizeKern5x5, kernFlou)).save(vraiCheminSauv, 'PNG')
				# Application d'un leger flou a l'image et enregistrement dans le rep
				# temporaire (... et donc l'affichage dans l'interface)
				imKerFlou=ouvIm.filter(ImageFilter.Kernel(sizeKern5x5, kernFlou)).save(self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png', 'PNG')
				
				# Compatibilité entre linux et windows
				# Dans la version windows ce n'est pas traité par un QProcess (comme sous 
				# Linux) mais directement avec os.system (car le QProcess avec la commande 
				# convert d'ImageMagick génère une erreur)
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					# Retour aux dimensions d'origine de l'image et enregistrement dans le
					# rep temporaire (et ce pour la sauvegarde de l'image --> utilisateur)
					process.start('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\""+' '+"\""+vraiCheminSauv+"\"")
				
					if not process.waitForStarted(3000):
						QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
					process.waitForFinished(-1)
					
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\""+' '+"\""+vraiCheminSauv+"\"")
				
				# Compatibilité entre linux et windows
				# Dans la version windows ce n'est pas traité par un QProcess (comme sous 
				# Linux) mais directement avec os.system (car le QProcess avec la commande 
				# convert d'ImageMagick génère une erreur)
				
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					# Retour aux dimensions d'origine de l'image et enregistrement dans 
					# le rep temporaire (et ce pour le compositing ... et donc l'affichage
					# dans l'interface)
					process.start('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'+"\"")
				
					if not process.waitForStarted(3000):
						QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
					process.waitForFinished(-1)
					
				# Uniquement pour windows
				elif os.name == 'nt':
					os.system('convert -resize '+str(imageDepart.size[0])+'x '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl.png'+"\""+' '+"\""+self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png'+"\"")
				
				# Remplissage de listeAff_1 pour affichage (ds le tabwidget)
				listeAff_1.append(self.repTampon+'decoupe_fond_tmpds56682qd35az2d8u9hl_'+string.zfill(parcPrincipal+self.spin1.value(), self.spin2.value())+'.png')
				
				# Ajout des images dans la liste self.listeImgDestin. Cette liste
				# sert à récupérer les images pour l'affichage des images ds l'interface
				self.listeImgDestin.append(listeAff_1[parcPrincipal])
				
				# On libere la memoire
				del antialiasing, newImageRGBA, newImageAntialias, imgDecoup, val_R_rgb, val_G_rgb, val_B_rgb, h_HSV, s_HSV, v_HSV, parcRGB, parcSupprimeLigne, a1, a2, a3, a4, imageDepart
				# x_ligne et y_ligne ne sont pas libérés car cela peut produire une erreur ds 
				# certaines circonstances
		
				# ------------------------------------------------------------------ #
				# STATS DE RENDU (AFFICHAGE ET SAUVEGARDE) .
				# ------------------------------------------------------------------ #
				# Calcule le pourcentage effectue a chaque passage
				val_pourc=((parcPrincipal+1)*100)/nbreElem
				# Affichage du pourcentage du rendu dans le terminal
				# sous Linux ou la fenetre MS-DOS sous Windows
				#print _("Progression du rendu :"), val_pourc
				EkdPrint(_(u"Progression du rendu: %s") % val_pourc)
				# Positionnement au temps 2 pour le temps de rendu de l'image
				t1=time.time()
				# Temps local (annee, mois, jour, heure, minute, seconde ...)
				tLocal=time.localtime()
				# Calcul avec le compteur pour le calcul du temps de rendu cumule
				som_t_renduCumul=som_t_renduCumul+(t1-t0)
				# Calcul pour la moyenne du temps de rendu .
				MoyRendu=som_t_renduCumul/(parcPrincipal+1) 
				# Calcul pour le temps de rendu restant .
				tempRestant=((MoyRendu*nbreElem)-(MoyRendu*parcPrincipal+1))-MoyRendu 
				# Mise en ordre du temps local pour ecriture dans fichier
				datHeurEcr=_(u"Le ")+str(tLocal[2])+"/"+str(tLocal[1])+"/"+str(tLocal[0])+_(u" a ")+str(tLocal[3])+":"+str(tLocal[4])+":"+str(tLocal[5])
			
				# Pour ecriture dans fichier
				progImg=_(u"Image ")+str(parcPrincipal+1)+"/"+str(nbreElem)
			
				# Si le temps de rendu est inferieur a la minute ... .
				if int(t1-t0)<60:
					affTemps=_(u"Temps de rendu : %s secondes") % (int(round(t1-t0)))
				# Si le temps de rendu est superieur a la minute ... calcul des 
				# minutes et des secondes
				elif int(t1-t0)>=60:
					affTemps=_(u"Temps de rendu : ")+str(int(round(t1-t0))/60)+_(u" min ")+str(int(round(t1-t0))%60)+_(u" sec")
				# Si la moyenne du temps de rendu est inferieur a la minute ... .	
				if MoyRendu<60:
					moyTemps=_(u"Moyenne du temps de rendu : %s secondes") % (int(round(MoyRendu))) 
				# Si la moyenne du temps de rendu est superieur a la minute ...  
				# calcul des minutes et des secondes .
				elif MoyRendu>=60:
					moyTemps=_(u"Moyenne du temps de rendu : ")+str(int(round(MoyRendu/60)))+_(u" min ")+str(int(round(MoyRendu%60)))+_(u" sec")
				# Si le temps de rendu est inferieur a la minute ... .
				if som_t_renduCumul<60:
					tRenduCumul=_(u"Temps de rendu cumule : %s secondes") % (int(round(som_t_renduCumul)))
				# Si le temps de rendu est superieur ou egal a la minute ... calcul des 
				# heures et des minutes .
				elif som_t_renduCumul>=60:
					tRenduInfMinut=int(round(som_t_renduCumul/60)) 
					tRenduCumul=_(u"Temps de rendu cumule : ")+str(tRenduInfMinut/60)+_(u" h ")+str(tRenduInfMinut%60)+_(u" min") 
					
				# Pour le temps de rendu restant ...
				# Si le temps de rendu restant est superieur a 0 secondes .
				if tempRestant>0:
					# Si le temps de rendu restant est inferieur a la minute et le
					# calcul du pourcentage est inferieur a 100 % .
					if tempRestant<60 and val_pourc<100:
						tRestant=_(u"Temps de rendu restant (estimation) : %s secondes") % (int(round(tempRestant)))
					# Si le temps de rendu restant est superieur a la minute et le
					# calcul du pourcentage est inferieur a 100 % .
					elif tempRestant>=60 and val_pourc<100:
						tRestantInfMinut=int(round(tempRestant/60))
						tRestant=_(u"Temps de rendu restant (estimation) : ")+str(tRestantInfMinut/60)+_(u" h ")+str(tRestantInfMinut%60)+_(u" min")
						
				# Des que le rendu est arrive a 100%, affichage de dans le
				# terminal sous Linux ou la fenetre MS-DOS sous Windows .
				if val_pourc==100 :
					#print
					EkdPrint(u'')
					#print _("Fini !")
					EkdPrint(_(u"Fini !"))
				
				# Ecriture des statistiques (cumul de l'ecriture) dans un fichier texte	
				ecrStatRendu=open(self.chemDossierSauv+_("_image_masque_3d_meth_2.txt"), 'a')
				ecrStatRendu.write("=================================================\n"+datHeurEcr+"\n"+"-------------------------------------------------\n"+progImg+"\n"+str(affTemps)+"\n"+str(moyTemps)+"\n"+str(tRenduCumul)+"\n\n")
				ecrStatRendu.close()
				
				# Remplissage de la liste pour les statistiques de rendu
				listeAff_2.append((_(u"Image chargée : ")+self.listeChemin[parcPrincipal], _(u"Image finale : ")+vraiCheminSauv, progImg, affTemps, moyTemps, tRenduCumul, _(u"Nombre total de pixels : ")+str(nbPixelsTotal), _(u"Dimension : ")+str(widthDepart)+' x '+str(heightDepart)))
				
				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée
				# Bouton Cancel pour arrêter la progression donc le process
				self.progress.setValue(val_pourc)
				QApplication.processEvents()
				if (self.progress.wasCanceled()): break
				# Quand l'utilisateur charge au moins 2 images ...
				if len(self.listeChemin)>1:
					self.progress.setLabel(QLabel(QString(tRestant)))
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
			
			# Affichage des infos sur l'image -------------------------
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte=_(u" Statistiques de rendu")
			a='#'*36
			b="-"*36
			
			self.infosImgProv=a+'\n#'+texte+'\n'+a+'\n'
			for parcStatRendu in listeAff_2:
				self.infosImgProv=self.infosImgProv+'\n'+parcStatRendu[0]+'\n'+parcStatRendu[1]+'\n'+parcStatRendu[2]+'\n'+parcStatRendu[3]+'\n'+parcStatRendu[4]+'\n'+parcStatRendu[5]+'\n'+parcStatRendu[6]+'\n'+parcStatRendu[7]+'\n'+b+'\n'
				
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv)
			self.framImg.setEnabled(True)
			
			# remise à 0 de la variable provisoire de log
			self.infosImgProv=''
			# ---------------------------------------------------------
			
			self.operationReussie()
				
		except :
			#print "ERREUR !"
			EkdPrint(u"ERREUR !")
			QMessageBox.warning(None, _(u"Erreur"), _(u"<p><b>Attention opération annulée pour Masque 3D (méthode 2):</b> modifiez les valeurs de <font color=blue><b>Saturation (début)</b></font> et de <font color=blue><b>Luminosité</b></font> dans l'onglet <b>Réglages du masque</b>.<p>Cliquez sur le bouton '<b>OK</b>' juste en dessous, puis sur '<b>Arrêter le processus</b>' de la fenêtre de progression.</p><p>Une solution possible est de charger l'image qui pose problème, changer les valeurs de 'Saturation (début)' et de 'Luminosité' et voir le résultat avec le bouton 'Voir le résultat'. Une fois que cela est fait, chargez le lot d'images et faites le traitement (avec les bons réglages).</p>"))
	
	
	def apercuReglages(self): 
		""" Aperçu du résultat sur la 1ère image du lot des réglages et ce juste avant d'appliquer soit masque alpha, soit masque 3D (pour méthode 1 ou 2) """
		
		#print _('valeur de Teinte (debut)'), self.spinTeinteDebut.value()
		EkdPrint(_(u'valeur de Teinte (debut) %s') % self.spinTeinteDebut.value())
		#print _('valeur de Teinte (fin)'), self.spinTeinteFin.value()
		EkdPrint(_(u'valeur de Teinte (fin) %s') % self.spinTeinteFin.value())
		#print _('valeur de Saturation (debut)'), self.spinSaturationDebut.value()
		EkdPrint(_(u'valeur de Saturation (debut) %s') % self.spinSaturationDebut.value())
		#print _('valeur de Saturation (fin)'), self.spinSaturationFin.value()
		EkdPrint(_(u'valeur de Saturation (fin) %s') % self.spinSaturationFin.value())
		#print _('valeur de Luminosite'), self.spinLuminosite.value()
		EkdPrint(_(u'valeur de Luminosite %s') % self.spinLuminosite.value())
		
		# Si on a sélectionné la méthode 1
		if self.comboMethode.currentIndex()==0: self.meth_1_ReglagPrevis()
		# Si on a sélectionné la méthode 2
		elif self.comboMethode.currentIndex()==1: self.meth_2_ReglagPrevis()
	
	
	def sonderTempsActuel(self):
		"""x ms après l'apparition de la boite de dialogue, on lance la conversion. But: faire en sorte que la boite de dialogue ait le temps de s'afficher correctement"""
		self.timer.stop()
		self.appliquer()
	
	
	def appliquer(self):
		"""On lance le type de conversion correspondant aux items sélectionnés des 2 boites de combo """
		# Si on a sélectionné masque alpha et la méthode 1 
		if self.comboMasque.currentIndex()==0 and self.comboMethode.currentIndex()==0:
			self.meth_1_ReglagMasqueAlpha()
		# Si on a sélectionné masque 3D et la méthode 1 
		elif self.comboMasque.currentIndex()==1 and self.comboMethode.currentIndex()==0:
			self.meth_1_ReglagMasque3D()
		# Si on a sélectionné masque alpha et la méthode 2 
		elif self.comboMasque.currentIndex()==0 and self.comboMethode.currentIndex()==1:
			self.meth_2_ReglagMasqueAlpha()
		# Si on a sélectionné masque 3D et la méthode 2 
		elif self.comboMasque.currentIndex()==1 and self.comboMethode.currentIndex()==1:
			self.meth_2_ReglagMasque3D()
	
	
	def appliquer0(self):
		"""Préparation de la conversion"""
		
		#print _(u'valeur de Teinte (debut)'), self.spinTeinteDebut.value()
		EkdPrint(_(u'valeur de Teinte (debut) %s') % self.spinTeinteDebut.value())
		#print _(u'valeur de Teinte (fin)'), self.spinTeinteFin.value()
		EkdPrint(_(u'valeur de Teinte (fin) %s') % self.spinTeinteFin.value())
		#print _(u'valeur de Saturation (debut)'), self.spinSaturationDebut.value()
		EkdPrint(_(u'valeur de Saturation (debut) %s') % self.spinSaturationDebut.value())
		#print _(u'valeur de Saturation (fin)'), self.spinSaturationFin.value()
		EkdPrint(_(u'valeur de Saturation (fin) %s') % self.spinSaturationFin.value())
		#print _(u'valeur de Luminosite'), self.spinLuminosite.value()
		EkdPrint(_(u'valeur de Luminosite %s') % self.spinLuminosite.value())

		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
		suffix=""
                self.chemDossierSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.chemDossierSauv = self.chemDossierSauv.getFile()
		
		if not self.chemDossierSauv: return
		
		self.progress.reset()
		self.progress.show()
		self.progress.setValue(0)
		QApplication.processEvents()
		
		# Lancement de la conversion dans 250 ms (seule solution trouvée pour éviter le grisage au début)
		self.timer.start(250)
		
		
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""
		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<p><h3><center>Découpe de fond uni bleu ou vert (chroma key)</center></h3></p><p><b>Vous pouvez ici découper (retirer) le fond bleu ou vert sur un lot d'images. Ce procédé de découpe de fond est utilisé dans divers domaines pour par exemple faire de l'incrustation d'un sujet découpé sur un autre fond (effets spéciaux au cinéma).</b></p><p><b>A ce sujet, voilà une petite définition venant de Wikipédia: 'L'incrustation est un effet spécial de cinéma consistant à intégrer des objets filmés séparément. ... Ce principe est notamment utilisé pour faire apparaître les cartes de la météo derrière le présentateur. Le bleu et le vert sont utilisés, car ces couleurs sont peu présentes dans la peau humaine. ... Les bords de l'objet filmé sur fond bleu posent parfois problème, notamment dans le cas de cheveux, on a alors un artefact appelé « tache bleue » (blue spill). ... En fonction du type de technique de tournage (vidéo ou film chimique), on utilise un fond bleu ou vert. Source: http://fr.wikipedia.org/wiki/Incrustation.</b></p><p><b>Voici un exemple de mise en place et tournage sur fond bleu ou vert:<br>http://www.lunerouge.org/spip/article.php3?id_article=592</b></p><p><b>Dans notre cas, EKD utilise deux méthodes pour faire la découpe de fond uni bleu ou vert (à voir dans l'onglet 'Réglages du masque'). La seconde méthode est plus précise que la première, mais elle plus lente. Dans cet onglet tout un tas de réglages vous sont proposés.</b></p><p>Dans l'onglet <b>'Images sources'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Dans l'onglet <b>'Autres réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b>.</p><p>Ensuite choisissez votre <b>Méthode</b> et votre <b>Type de masque</b>.</p><p>Dans l'onglet <b>Réglages du masque</b> sélectionnez d'abord le <b>Type de fond uni</b>, faites les réglages de <b>Teinte</b>, <b>Saturation</b> et <b>Luminosité</b>, puis selon les cas réglez <b>Choix de la netteté</b>, <b>Qualité</b> ou <b>Choix du fond et de la forme</b>, cliquez sur le bouton <b>Voir le résultat</b> (<b><font color='green'>il s'agit d'une prévue vous montrant le résultat de la découpe après réglages</font></b>), si vous n'êtes pas satisfaits, refaites les réglages, ... si les réglages vous conviennent, cliquez sur le bouton <b>Appliquer</b>, entrez le <b>Nom de fichier</b> dans cette dernière boîte (vous aurez évidemment pris soin de sélectionner le répertoire de destination de votre découpe). Cliquez sur le bouton <b>Enregistrer</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>Image(s) après traitement</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>Infos</b> vous permet de voir les <b>Statistiques de rendu</b>.</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'comboMethode', unicode(self.comboMethode.currentIndex()))
		EkdConfig.set(self.idSection, u'comboMasque', unicode(self.comboMasque.currentIndex()))
		EkdConfig.set(self.idSection, u'comboReglage', unicode(self.comboReglage.currentIndex()))
		EkdConfig.set(self.idSection, u'comboQualite', unicode(self.comboQualite.currentIndex()))
		EkdConfig.set(self.idSection, u'comboNettete', unicode(self.comboNettete.currentIndex()))
		EkdConfig.set(self.idSection, u'comboFondForme', unicode(self.comboFondForme.currentIndex()))
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2.value()))
		EkdConfig.set(self.idSection, u'spinTeinteDebut', unicode(self.spinTeinteDebut.value()))
		EkdConfig.set(self.idSection, u'spinTeinteFin', unicode(self.spinTeinteFin.value()))
		EkdConfig.set(self.idSection, u'spinSaturationDebut', unicode(self.spinSaturationDebut.value()))
		EkdConfig.set(self.idSection, u'spinSaturationFin', unicode(self.spinSaturationFin.value()))
		EkdConfig.set(self.idSection, u'spinLuminosite', unicode(self.spinLuminosite.value()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.comboMethode.setCurrentIndex(int(EkdConfig.get(self.idSection, u'comboMethode')))
		self.comboMasque.setCurrentIndex(int(EkdConfig.get(self.idSection, u'comboMasque')))
		self.comboReglage.setCurrentIndex(int(EkdConfig.get(self.idSection, u'comboReglage')))
		self.comboQualite.setCurrentIndex(int(EkdConfig.get(self.idSection, u'comboQualite')))
		self.comboNettete.setCurrentIndex(int(EkdConfig.get(self.idSection, u'comboNettete')))
		self.comboFondForme.setCurrentIndex(int(EkdConfig.get(self.idSection, u'comboFondForme')))
		self.spin1.setValue(int(EkdConfig.get(self.idSection, u'spin1')))
		self.spin2.setValue(int(EkdConfig.get(self.idSection, u'spin2')))	
		self.spinTeinteDebut.setValue(int(EkdConfig.get(self.idSection, u'spinTeinteDebut')))
		self.spinTeinteFin.setValue(int(EkdConfig.get(self.idSection, u'spinTeinteFin')))
		self.spinSaturationDebut.setValue(int(EkdConfig.get(self.idSection, u'spinSaturationDebut')))
		self.spinSaturationFin.setValue(int(EkdConfig.get(self.idSection, u'spinSaturationFin')))
		self.spinLuminosite.setValue(int(EkdConfig.get(self.idSection, u'spinLuminosite')))
