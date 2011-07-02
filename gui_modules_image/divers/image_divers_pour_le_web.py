#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, string, glob, ImageFilter
import Image
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import *

from gui_modules_image.image_base import Base, SpinSliders, SpinSlider

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


class Apercu(QWidget):
	"""Aperçu de la découpe/morcellement d'image.
	Concrêtement, dessine la première image d'un lot en traçant dessus des lignes.
	Ces dernières forment des rectangles symbolisant les morceaux qui vont être découpés
	"""
	
	def __init__(self, tailleCanevas=(None, None)):
		QWidget.__init__(self)
		
		# Taille du canevas
		self.tailleCanevas = tailleCanevas
		# Image nulle au départ (rien ne sera donc traçé à ce niveau)
		self.image = QImage()
		# Nombre de cases en horizontal pour la découpe
		self.nbrCaseHoriz = 0
		# Nombre de cases en vertical pour la découpe
		self.nbrCaseVert = 0
	
	def sizeHint(self):
		return QSize(self.tailleCanevas[0], self.tailleCanevas[1])

	def minimumSizeHint(self):
        	return QSize(self.tailleCanevas[0], self.tailleCanevas[1])
	
	def setImage(self, img):
		"Donne l'adresse d'une image à la classe pour ensuite l'afficher"
		image = QImage(img)
		
		largeurImg , hauteurImg = image.size().width(), image.size().height()
		largeurCanevas, hauteurCanevas = self.tailleCanevas
		
		if largeurImg - largeurCanevas > hauteurImg - hauteurCanevas:
			# La largeur est le facteur limitant -> redimension en largeur
			self.image = image.scaledToWidth(largeurCanevas)
		else:
			# La hauteur est le facteur limitant -> redimension en hauteur
			self.image = image.scaledToHeight(hauteurCanevas)
		
		self.repaint()
	
	def setNbrCase(self, nbrCaseHoriz=3, nbrCaseVert=2):
		"Spécifie les paramètres de morcellement de la zone rectangulaire"
		self.nbrCaseHoriz = nbrCaseHoriz
		self.nbrCaseVert = nbrCaseVert
		self.repaint()
	
	def paintEvent(self, event):
		"Trace la première image et les traits qui symboliseront la découpe"
		paint = QPainter()
		paint.begin(self)
		
		# Si aucune image n'a été chargée, on ne trace rien
		if self.image.isNull():
			paint.end()
			return
		
		# Traçage de l'image
		paint.drawImage(0, 0, self.image)
		# On vérifie que l'on découpe véritablement l'image
		if self.nbrCaseHoriz > 1 or self.nbrCaseVert > 1:
			# Largeur de l'image à l'écran
			largeurImgEcran = self.image.size().width()
			# Hauteur de l'image à l'écran
			hauteurImgEcran = self.image.size().height()
			
			# Traçage des lignes verticales
			if self.nbrCaseHoriz > 1:
				# Largeur d'une case
				largeurCase = largeurImgEcran / self.nbrCaseHoriz
				for i in range(self.nbrCaseHoriz):
					if i == 0:
						continue
					paint.drawLine(i * largeurCase, 0, i * largeurCase, hauteurImgEcran)
			
			# Traçage des lignes horizontales
			if self.nbrCaseVert > 1:
				# Hauteur d'une case
				hauteurCase = hauteurImgEcran / self.nbrCaseVert
				for i in range(self.nbrCaseVert):
					if i == 0:
						continue
					paint.drawLine(0, i * hauteurCase, largeurImgEcran, i * hauteurCase)
		
		paint.end()

class widget_Coin_et_Ombre(QWidget) :
	# -----------------------------------
	# Réglages pour coin et ombres + actions automatiques liées aux choix de l'utilisateur
	# -----------------------------------
	def __init__(self) :
		QWidget.__init__(self)
		self.updateColor = 1
		# Construction de l'interface
		Glayout = QGridLayout(self)
		# Choix de la représentation des couleurs
		self.couleurHexa = QRadioButton(QString(_(u"Couleur Hexadécimale")), self)
		self.couleurRGB = QRadioButton(QString(_(u"Couleur RGB")), self)
		self.couleurHexa.setChecked(True)
		Glayout.addWidget(self.couleurHexa, 0, 1)
		Glayout.addWidget(self.couleurRGB, 0, 2)
		# Choix ombre portée
		self.ombrePortee = QCheckBox(QString(_(u"Ombre portée")), self)
		self.ombrePortee.setChecked(True)
		Glayout.addWidget(self.ombrePortee, 1, 2)
		# Titre couleur Fond et couleur Ombre
		self.couleurFond = QLabel(QString(_(u"Couleur de fond")))
		self.couleurOmbre = QLabel(QString(_(u"Couleur de l'ombre portée")))
		Glayout.addWidget(self.couleurFond, 2, 1)
		Glayout.addWidget(self.couleurOmbre, 2, 2)
		# introduction couleurs HEXA et affichage couleur
		self.couleurFondHexa = QLineEdit(QString("#FFFFFF"),self)
		self.couleurFondHexa.setInputMask(QString("\#HHHHHH"))
		self.couleurOmbreHexa = QLineEdit("#000000",self)
		self.couleurOmbreHexa.setInputMask(QString("\#HHHHHH"))
		Glayout.addWidget(self.couleurFondHexa, 3, 1)
		Glayout.addWidget(self.couleurOmbreHexa, 3, 2)
		# Affichage texte 3 couleurs RGB
		self.coulR = QLabel(QString(_(u"Rouge")), self)
		self.coulG = QLabel(QString(_(u"Vert")), self)
		self.coulB = QLabel(QString(_(u"Bleu")), self)
		Glayout.addWidget(self.coulR, 4, 0)
		Glayout.addWidget(self.coulG, 5, 0)
		Glayout.addWidget(self.coulB, 6, 0)
		# Sélection des couleurs RGB Fond
		self.fondR = SpinSlider(debut=0, fin=255, defaut=255, optionConfig=None, parent=None)
		self.fondG = SpinSlider(debut=0, fin=255, defaut=255, optionConfig=None, parent=None)
		self.fondB = SpinSlider(debut=0, fin=255, defaut=255, optionConfig=None, parent=None)
		Glayout.addWidget(self.fondR, 4, 1)
		Glayout.addWidget(self.fondG, 5, 1)
		Glayout.addWidget(self.fondB, 6, 1)
		# Sélection des couleurs RGB Ombre
		self.ombreR = SpinSlider(debut=0, fin=255, defaut=0, optionConfig=None, parent=None)
		self.ombreG = SpinSlider(debut=0, fin=255, defaut=0, optionConfig=None, parent=None)
		self.ombreB = SpinSlider(debut=0, fin=255, defaut=0, optionConfig=None, parent=None)
		Glayout.addWidget(self.ombreR, 4, 2)
		Glayout.addWidget(self.ombreG, 5, 2)
		Glayout.addWidget(self.ombreB, 6, 2)
		# Rayon de l'arrondi
		self.labelArrondi = QLabel(QString(_(u"Rayon de l'arrondi")), self)
		self.arrondiR = SpinSlider(debut=2, fin=30, defaut=10, optionConfig=None, parent=None)
		Glayout.addWidget(self.labelArrondi, 7, 1)
		Glayout.addWidget(self.arrondiR, 8, 1)
		# Intensité du flou
		self.labelflou = QLabel(QString(_(u"Intensité du flou")), self)
		self.flouI = SpinSlider(debut=4, fin=10, defaut=8, optionConfig=None, parent=None)
		Glayout.addWidget(self.labelflou, 7, 2)
		Glayout.addWidget(self.flouI, 8, 2)
		# Décalage de l'ombre
		self.labelDecalage = QLabel(QString(_(u"Décalage de l'ombre")), self)
		self.decalageOmbre = SpinSlider(debut=10, fin=50, defaut=20, optionConfig=None, parent=None)
		Glayout.addWidget(self.labelDecalage, 9, 2)
		Glayout.addWidget(self.decalageOmbre, 10, 2)
		self.majInterface()
		self.showCouleurFond()
		self.showCouleurOmbre()
		# connections interWidgets
		self.connect(self.couleurHexa, SIGNAL("clicked(bool)"), self.majInterface)
		self.connect(self.couleurRGB, SIGNAL("clicked(bool)"), self.majInterface)
		self.connect(self.ombrePortee, SIGNAL("clicked(bool)"), self.majInterface)
		self.connect(self.couleurFondHexa, SIGNAL("editingFinished()"), self.showCouleurFond)
		self.connect(self.fondR, SIGNAL("valueChanged(int)"), self.showCouleurFond)
		self.connect(self.fondG, SIGNAL("valueChanged(int)"), self.showCouleurFond)
		self.connect(self.fondB, SIGNAL("valueChanged(int)"), self.showCouleurFond)
		self.connect(self.couleurOmbreHexa, SIGNAL("editingFinished()"), self.showCouleurOmbre)
		self.connect(self.ombreR, SIGNAL("valueChanged(int)"), self.showCouleurOmbre)
		self.connect(self.ombreG, SIGNAL("valueChanged(int)"), self.showCouleurOmbre)
		self.connect(self.ombreB, SIGNAL("valueChanged(int)"), self.showCouleurOmbre)
		
	def majInterface(self) :
		# Fonction à appeler pour gérer les activations ou désactivation de widgets suivant les choix de l'utilisateur
		# Points à vérifier :
		# Si self.couleurHexa est sélectionné -> Il faut désactiver les SpinSlider pour les couleurs de fond et ombre
		# et activer les QLineEdit pour introduire les couleurs de fond et ombre sous forme hexadécimale.
		# Si ombre portée est non sélectionné -> grisé tous les réglages de la partie droite relative à la partiee ombre.
		if self.couleurHexa.isChecked() :
			self.couleurFondHexa.setEnabled(True)
			self.couleurOmbreHexa.setEnabled(True)
			self.fondR.setDisabled(True)
			self.fondG.setDisabled(True)
			self.fondB.setDisabled(True)
			self.ombreR.setDisabled(True)
			self.ombreG.setDisabled(True)
			self.ombreB.setDisabled(True)
		else :
			#self.couleurFondHexa.setDisabled(True)
			#self.couleurOmbreHexa.setDisabled(True)
			self.fondR.setEnabled(True)
			self.fondG.setEnabled(True)
			self.fondB.setEnabled(True)
			self.ombreR.setEnabled(True)
			self.ombreG.setEnabled(True)
			self.ombreB.setEnabled(True)
		if self.ombrePortee.isChecked() :
			self.flouI.setEnabled(True)
			self.decalageOmbre.setEnabled(True)
		else :
			self.flouI.setDisabled(True)
			self.decalageOmbre.setDisabled(True)
			self.couleurOmbreHexa.setDisabled(True)
			self.ombreR.setDisabled(True)
			self.ombreG.setDisabled(True)
			self.ombreB.setDisabled(True)
		
	def showCouleurFond(self) :
		if self.updateColor :
			# Variable pour éviter des mises à jour successive liées aux signaux
			self.updateColor = 0
			if self.couleurHexa.isChecked() :
				if self.couleurFondHexa.text().startsWith("#") :
					couleurHexa = self.couleurFondHexa.text()
				else :
					couleurHexa = self.couleurFondHexa.text().prepend("#")
				#if QColor().isValidColor(couleurHexa) :
				coul = QColor(couleurHexa)
				self.fondR.setValue(coul.red())
				self.fondG.setValue(coul.green())
				self.fondB.setValue(coul.blue())
			else :
				coul = QColor(self.fondR.value(), self.fondG.value(), self.fondB.value())
				self.couleurFondHexa.setText(coul.name())

			palette = QPalette()
			palette.setColor(QPalette.Base, coul)
			# Défini la couleur du texte pour avoir un bon contraste
			if coul.value()<128 : coul2 = QColor(255,255,255)
			else : coul2 = QColor(0,0,0)
			palette.setColor(QPalette.Text, coul2)
			self.couleurFondHexa.setPalette(palette)
			self.updateColor = 1

	def showCouleurOmbre(self) :
		if self.updateColor :
			# Variable pour éviter des mises à jour successive liées aux signaux
			self.updateColor = 0
			if self.couleurHexa.isChecked() :
				if self.couleurOmbreHexa.text().startsWith("#") :
					couleurHexa = self.couleurOmbreHexa.text()
				else :
					couleurHexa = self.couleurOmbreHexa.text().prepend("#")
				#if QColor().isValidColor(couleurHexa) :
				coul = QColor(couleurHexa)
				self.ombreR.setValue(coul.red())
				self.ombreG.setValue(coul.green())
				self.ombreB.setValue(coul.blue())
			else :
				coul = QColor(self.ombreR.value(), self.ombreG.value(), self.ombreB.value())
				self.couleurOmbreHexa.setText(coul.name())

			palette = QPalette()
			palette.setColor(QPalette.Base, coul)
			# Défini la couleur du texte pour avoir un bon contraste
			if coul.value()<128 : coul2 = QColor(255,255,255)
			else : coul2 = QColor(0,0,0)
			palette.setColor(QPalette.Text, coul2)
			self.couleurOmbreHexa.setPalette(palette)
			self.updateColor = 1
	
	def getParametresCoin(self) :
		"""Fonction pour récupérer directement toutes les valeurs sélectionnées dans l'interface pour la partie coin. Les données sont retournées comme une liste de valeur'"""
		return self.fondR.value(), self.fondG.value(), self.fondB.value(), self.arrondiR.value()

	def getParametresOmbre(self) :
		"""Fonction pour récupérer directement toutes les valeurs sélectionnées dans l'interface pour la partie ombre. Les données sont retournées comme une liste de valeur'"""
		return self.ombrePortee.isChecked(), self.ombreR.value(), self.ombreG.value(), self.ombreB.value(), self.flouI.value(), self.decalageOmbre.value()
		

class Image_Divers_PourLeWeb(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Pour le web
	# -----------------------------------
	def __init__(self, statusBar, geometry):
        	QWidget.__init__(self)
		
		# ----------------------------
		# Quelques paramètres de base
		# ----------------------------
		
		#=== Création des répertoires temporaires ===#
		# Gestion du repertoire tmp avec EkdConfig 
		self.repTampon = EkdConfig.getTempDir() + os.sep + "tampon" + os.sep + "pour_le_web" + os.sep
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
		#############################################################################
		
		#=== Variable contenant les titres du log ===#
		self.infosImgTitre = []
		txt = _(u"Image(s) chargée(s)")
		a='#'*36
		b = a + '\n# ' + txt + '\n' + a + '\n'
		txt=_(u"Image(s) convertie(s)")
		c = a + '\n# ' + txt + '\n' + a + '\n'
		self.infosImgTitre.append(b)
		self.infosImgTitre.append(c)
		
		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)
		
		# Est-ce que des images ont été converties et qu'elles n'ont pas encore été montrées?
		# Marche aussi quand la conversion a été arrêté avant la fin de la 1ère image
		self.conversionImg = 0
		
		# Est-ce qu'une prévisualisation a été appelée?
		self.previsualImg = 0
		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0
		
		self.timer = QTimer()
		self.connect(self.timer, SIGNAL('timeout()'), self.sonderTempsActuel)
		
		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()

		# Gestion de la configuration via EkdConfig

		# Paramètres de configuration
		self.config = EkdConfig
		# Identifiant du cadre
		self.idSection = "image_pour_le_web"
		# Log du terminal
		self.base.printSection(self.idSection)
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
		
		self.framReglage=QFrame()
		vboxReglage=QVBoxLayout(self.framReglage)
		
		# Gestion du nombre d'images à traiter
		self.grid = QGridLayout()
		
		self.labTraitImgNum=QLabel(_(u"Traitement à partir de l'image (numéro)"))
		self.grid.addWidget(self.labTraitImgNum, 0, 0)
		# Label invisible par défaut
		self.labTraitImgNum.hide()
		self.spin1_ImTrait=SpinSlider(1, 100000, 1, '', self)
		self.grid.addWidget(self.spin1_ImTrait, 0, 1)
		# Spin invisible par défaut
		self.spin1_ImTrait.hide()
		self.connect(self.spin1_ImTrait, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.labNbreChifNIm=QLabel(_(u"Nombre de chiffres après le nom de l'image"))
		self.grid.addWidget(self.labNbreChifNIm, 1, 0)
		# Label invisible par défaut
		self.labNbreChifNIm.hide()
		self.spin2_ImTrait=SpinSlider(3, 18, 6, '', self)
		self.grid.addWidget(self.spin2_ImTrait, 1, 1)
		# Spin invisible par défaut
		self.spin2_ImTrait.hide()
		self.connect(self.spin2_ImTrait, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.grid.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid)
		vboxReglage.addStretch()
		
		#=== Stacked ===#
		
		self.stacked = QStackedWidget()
		self.stacked.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
		
		#=== Instanciation des widgets du stacked  ===#
		
		#---- Stacked de Gif
		stacked_gifAnime = QFrame()
		vboxStacked = QVBoxLayout(stacked_gifAnime)
		
		# Widget du stacked avec une seule boite de spin
		self.spinCouleursDelai = SpinSliders(self,
				8, 256, 128, _(u"Nombre de couleurs (Réduction)"), 'nombre_couleurs',
				1, 20000, 10, _(u"Temps de pause entre 2 trames (ms)"), 'delai')
		
		self.spinLargeur = SpinSliders(self, 10, 1024, 200, _(u"Nouvelle largeur (px)"), 'nouvelle_largeur')
		self.spinLargeur.setEnabled(False)
		
		self.checkModifLargeur = QCheckBox("Modifier la largeur de l'image gif")
		self.connect(self.checkModifLargeur, SIGNAL("stateChanged(int)"), self.checkModifLargeurChange)
		self.checkModifLargeur.setChecked(False)
		
		vboxStacked.addWidget(self.spinCouleursDelai, 0)
		vboxStacked.addWidget(QLabel())
		vboxStacked.addWidget(self.checkModifLargeur, 0, Qt.AlignHCenter)
		vboxStacked.addWidget(self.spinLargeur , 0)
		vboxStacked.addStretch()
		
		#---- Stacked de Découpe
		stacked_morcellementImg = QFrame()
		vboxStacked = QVBoxLayout(stacked_morcellementImg)
		self.spinMorcellement = SpinSliders(self,
			1,10,2, _(u"Nombre de morceaux (sens horizontal)"), 'nombre_morceaux_horizontal',
			1,10,2,_(u"Nombre de morceaux (sens vertical)"), 'nombre_morceaux_vertical')
		# Aperçu de la découpe d'image
		self.apercu = Apercu((400, 300))
		self.connect(self.spinMorcellement.spin1, SIGNAL("valueChanged(int)"), self.changeMorcellement)
		self.connect(self.spinMorcellement.spin2, SIGNAL("valueChanged(int)"), self.changeMorcellement)
		self.apercu.setNbrCase(self.spinMorcellement.spin1.value(), self.spinMorcellement.spin2.value())
		vboxStacked.addWidget(self.spinMorcellement)
		hboxMorcellement = QHBoxLayout()
		hboxMorcellement.addStretch()
		hboxMorcellement.addWidget(self.apercu)
		hboxMorcellement.addStretch()
		vboxStacked.addLayout(hboxMorcellement)
		
		# Widgets du stacked avec une seule boite de spin
		indexStacked_gif_anime = self.stacked.addWidget(stacked_gifAnime)
		# Widgets du stacked avec 2 boites de spin
		indexStacked_morcellementImg = self.stacked.addWidget(stacked_morcellementImg)
				
		#---- Stacked de coin et ombre
		stacked_coin_ombre = QFrame()
		vboxStacked = QVBoxLayout(stacked_coin_ombre)
		
		self.cow = widget_Coin_et_Ombre()
		vboxStacked.addWidget(self.cow, 0)
		indexStacked_coin_ombre = self.stacked.addWidget(stacked_coin_ombre)
		
		# boite de combo
		self.comboReglage=QComboBox()
		# Paramètres de la liste de combo: [(nom entrée, identifiant, index du stacked,
		# instance stacked),...]
		self.listeComboReglage=[(_(u'Gif animé'),    'gif_anime',    indexStacked_gif_anime,    self.spinCouleursDelai),\
		(_(u"Morcellement/découpe d'image"),    'morcellement_img',    indexStacked_morcellementImg,    self.spinMorcellement), (_(u'Coins arrondis et ombre portée'),    'coin_ombre',  indexStacked_coin_ombre, self.cow)]
		
		# Insertion des codecs de compression dans la boite de combo
		for i in self.listeComboReglage:
                	self.comboReglage.addItem(i[0], QVariant(i[1]))
		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		self.base.valeurComboIni(self.comboReglage, self.config, self.idSection, 'methode')
		
		hbox = QHBoxLayout()
		hbox.addWidget(QLabel(_(u'Type')))
		hbox.addWidget(self.comboReglage)
		hbox.setAlignment(Qt.AlignHCenter)
		
		vboxReglage.addLayout(hbox)
		vboxReglage.addWidget(self.stacked)
		vboxReglage.addStretch()
		
		#----------------
		# Onglet de log
		#----------------
		
		self.zoneAffichInfosImg = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneAffichInfosImg.setText = self.zoneAffichInfosImg.setPlainText
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
		
		vbox.addWidget(self.tabwidget)

		self.indexTabImgSource = self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		self.indexTabImgReglage=self.tabwidget.addTab(self.framReglage, _(u'Réglages'))
		self.indexTabImgDestin = self.tabwidget.addTab(self.afficheurImgDestination, _(u'Image(s) après traitement'))
		self.indexTabImgInfos=self.tabwidget.addTab(self.framInfos, _(u'Infos'))
		
		# -------------------------------------------
		# widgets du bas : curseur + ligne + boutons
		# -------------------------------------------
		
		# Boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones/icone_aide_128.png"))
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
		
		self.boutApPremImg = QPushButton(_(u" Voir le résultat"))
		self.boutApPremImg.setIcon(QIcon("Icones/icone_visionner_128.png"))
		self.boutApPremImg.setFocusPolicy(Qt.NoFocus)
		self.boutApPremImg.setEnabled(False)
		self.connect(self.boutApPremImg, SIGNAL("clicked()"), self.visu_1ere_img)
		
		self.boutAppliquer=QPushButton(_(u" Appliquer et sauver"))
		self.boutAppliquer.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		
		# Bouton inactif au départ
		self.boutAppliquer.setEnabled(False)

		self.connect(self.boutAppliquer, SIGNAL("clicked()"), self.appliquer0)

		# Ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons
		
		hbox=QHBoxLayout()
		hbox.addWidget(boutAide)
		hbox.addStretch()
		hbox.addWidget(self.boutApPremImg)
		hbox.addStretch()
		hbox.addWidget(self.boutAppliquer)
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
		self.connect(self.afficheurImgSource, SIGNAL("pictureSelected()"), self.modifImgSelect)
		
		
	def changeValNbreImg_1(self):
		"""Gestion du nombre d'images à traiter"""
		#print "Traitement a partir de l'image (numero):", self.spin1_ImTrait.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1_ImTrait.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2_ImTrait.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2_ImTrait.value())


	def modifImgSource(self, i):
		"""On active ou désactive les boutons d'action et on recharge le pseudo-aperçu en fonction du nombre d'images présentes dans le widget de sélection"""
		self.boutAppliquer.setEnabled(i)
		self.boutApPremImg.setEnabled(i)
		self.modifImageSource = 1
		self.apercu.setImage(self.afficheurImgSource.getFile())

	
	def modifImgSelect(self):
		"Une nouvelle image a été sélectionnée. On la donne à l'aperçu"
		self.apercu.setImage(self.afficheurImgSource.getFile())
	
	
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
				# Démarre le *.gif quand ce type d'image a été créée et ne fait rien sinon
				if self.afficheurImgDestination.isGif():
					self.afficheurImgDestination.startPauseGif()
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
	
	
	def changerComboReglage(self, i):
		"""Récup/affichage ds le terminal de l'index de self.comboReglage"""
		self.stacked.setCurrentIndex(self.listeComboReglage[i][2])
		
		self.config.set(self.idSection, 'methode', self.listeComboReglage[i][1])
		
		#print self.comboReglage.currentIndex()
		EkdPrint(u"%s" % self.comboReglage.currentIndex())
		
		# Si Gif animé est sélectionné, les labels et spins sont invisibles
		if self.comboReglage.currentIndex()==0:
			self.labTraitImgNum.hide()
			self.spin1_ImTrait.hide()
			self.labNbreChifNIm.hide()
			self.spin2_ImTrait.hide()
		# Si Découpe/morcellement est sélectionné, les labels et spins deviennent visibles
		elif self.comboReglage.currentIndex()==1 or self.comboReglage.currentIndex()==2 :
			self.labTraitImgNum.show()
			self.spin1_ImTrait.show()
			self.labNbreChifNIm.show()
			self.spin2_ImTrait.show()
		
	
	def changeMorcellement(self, i):
		"Une valeur de morcellement vient de changer. On transmet l'information à l'aperçu"
		self.apercu.setNbrCase(self.spinMorcellement.spin1.value(),
					self.spinMorcellement.spin2.value())
		
		if self.comboReglage.currentIndex()==1:
			self.spin1_ImTrait.show()
	
	
	def checkModifLargeurChange(self, boolean):
		"""La case à cocher change d'état
		-> la boite de spin redimension de la largeur s'active ou se désactive"""
		self.spinLargeur.setEnabled(boolean)
	
	
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
				sRedim=obImg.resize(self.dimStatImg, Image.ANTIALIAS)
				chemSortie = self.repTampon+'redim'+os.sep+os.path.basename(chemImg)
				sRedim.save(chemSortie)
				self.listeImgSource[index] = chemSortie
				index += 1
	
	
	def sonderTempsActuel(self):
		"""x ms après l'apparition de la boite de dialogue, on lance la conversion. But: faire en sorte que la boite de dialogue ait le temps de s'afficher correctement"""
		self.timer.stop()
		self.appliquer()
			
				
	def visu_1ere_img(self):
		"""Visionnement de la conversion en Gif animé et Morcellement/découpe avant application"""
		
		# Si Gif animé est sélectionné
		if self.comboReglage.currentIndex()==0:

			# Récupération de la liste des fichiers chargés car por la visu du gif
			# animé ce sont les 2 1ères images de  la liste qui sont selectionnées
			self.listeImgSource=self.afficheurImgSource.getFiles()

			# Chemin de sauvegarde
			self.cheminCourantSauv = self.repTampon+'gif_anim_visu.gif'
			
			nbreElem=len(self.listeImgSource)

			# Liste de travail pour le redimensionnement
			listeImgTemp=[]
			
			# nbreElem et elem: affectation du nombre d'image et occurence 
			# à utiliser. A ce propos pour la visualisation le nombre d'images
			# utilisées pour la visualisation du gif animé sera de 2 maximum
			# (pour voir le temps de pause entre 2 trames)
			#### Si l'utilisateur ne charge qu'une image ####
			if nbreElem==1:
				nbreElem=1
				elem=0
				ouvrirImag=Image.open(self.listeImgSource[0])
            			ouvrirImag.save(self.repTampon+'redim'+os.sep+'redim_gif_anim_'+string.zfill(1, 3)+'.png')
				listeImgTemp.append(self.repTampon+'redim'+os.sep+'redim_gif_anim_'+string.zfill(1, 3)+'.png')
			#### Si l'utilisateur charge plusieurs images ####
			elif nbreElem>1:
				nbreElem=2
				elem=2
				# ----- Redimensionnement des images --------------------------------------
    				# Ouverture de la 1ere image chargee
				imgOuvComp=Image.open(self.listeImgSource[0])
    				# Dimension de cette image (w--> largeur, h --> hauteur)
    				w, h=imgOuvComp.size
    				# Boucle pour le redimensionnement
    				n=0
				# Tant qu'on a pas atteint le nbre d'images
    				while n < len(self.listeImgSource[0:elem]):
        				for parcRedim in self.listeImgSource[0:elem]:
            					ouvrirImag=Image.open(parcRedim)
            					# Redimensionnement des images
            					sRedimComp=ouvrirImag.resize(imgOuvComp.size, Image.ANTIALIAS)
            					sRedimComp.save(self.repTampon+'redim'+os.sep+'redim_gif_anim_'+string.zfill(n, 3)+'.png')
						listeImgTemp.append(self.repTampon+'redim'+os.sep+'redim_gif_anim_'+string.zfill(n, 3)+'.png')
            					n=n+1	
				
			# Recup de la valeur de Nombre de couleurs (Réduction)
			spinCouleur = str(self.spinCouleursDelai.spin1.value())
			# Nouveau temps de pause entre 2 images
			spinDelai = str(self.spinCouleursDelai.spin2.value())
			if self.spinLargeur.isEnabled():
				# Nouvelle largeur
				spinLargeur = str(self.spinLargeur.spin.value())
			
			listeChemin = ["\"" + i + "\"" for i in listeImgTemp]
			
			commande = 'convert -quiet -delay '+spinDelai+' -loop 0 -colors '+spinCouleur+' '+' '.join(listeChemin)+' '+"\""+self.repTampon+'gif_anim_visu.gif'+"\""
			
			# On ne redimensionne que si la boite de spin associée est active
			if self.spinLargeur.isEnabled():
				commande = commande.replace('convert', 'convert -resize ' + spinLargeur)
					
			os.system(commande)

			# Affichage de l'image temporaire 
			# Ouverture d'une boite de dialogue affichant l'aperçu.
			#
			# Affichage par le bouton Voir le résultat
			visio = VisionneurEvolue(self.cheminCourantSauv)
			visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
			visio.startPauseGif()
			visio.exec_()
		
			return 0
			
		# Si Découpe/morcellement est sélectionné	
		elif self.comboReglage.currentIndex()==1:
			
			# Récupération du fichier sélectionné par l'utilisateur (si pas de fichier
			# sélectionné par l'utilisateur, la 1ère image de la liste est prise)
			file = self.afficheurImgSource.getFile()
			if not file: return
			self.listeImgSource = [file]
			
			# Récupération de l'identifiant du codec
			i = self.comboReglage.currentIndex()
			
			# Recup de la valeur de Nombre de morceaux (sens horizontal)
			spin_1 = self.listeComboReglage[i][3].spin1.value()
			# Recup de la valeur de Nombre de morceaux (sens vertical)
			spin_2 = self.listeComboReglage[i][3].spin2.value()
			
			# Ouverture de la 1ère image du lot pour extension
			im=Image.open(self.listeImgSource[0])
			# Chemin, extension
			f, ext=os.path.splitext(self.listeImgSource[0])
			
			# Résolution de l'image
			resLarg, resHaut=im.size
			
			# Comprehension-list pour calculer les coordonnées de découpe dans le sens horizontal
			l_1=[(totoX*(resLarg/spin_1), totoY*(resHaut/spin_2)) for totoY in range(spin_2) for totoX in range(spin_1)]
			# Comprehension-list pour calculer les coordonnées de découpe dans le sens vertical
			l_2=[(totoX*(resLarg/spin_1)+(resLarg/spin_1), totoY*(resHaut/spin_2)+(resHaut/spin_2)) for totoY in range(spin_2) for totoX in range(spin_1)]
			# Regroupement sens horizontal et vertical
			inter=zip(l_1, l_2)
			# Regroupement final des coordonnées horizontales et verticales pour la découpe.
			# Affiche par exemple: [(0, 0, 105, 144), (105, 0, 210, 144), (210, 0, 315, 144), ...]
			lF=[(x1[0], x1[1], y1[0], y1[1]) for x1, y1 in inter]
			
			# Marge (en pixels) pour l'affichage
			marge=6
			# Calcul des coordonnées pour affichage dans l'interface
			lCoAff=[(((tX+1)*marge)+(tX*(resLarg/spin_1)), ((tY+1)*marge)+(tY*(resHaut/spin_2))) for tY in range(spin_2) for tX in range(spin_1)]
			# Largeur de l'image de fond pour affichage ds l'interface
			largFondAffichage=resLarg+((spin_1+1)*marge)
			# Hauteur de l'image de fond pour affichage ds l'interface
			hautFondAffichage=resHaut+((spin_2+1)*marge)
			# Creation de l'image de fond pour acceuillir les morceaux de l'image (affichage
			# dans l'interface)
			imgFond=Image.new('RGB', (largFondAffichage, hautFondAffichage), (119, 119, 121))
			
			# Regroupement des coordonnées horizontales et verticales pour la découpe et des
			# coordonnées d'affichage des images découpées dans l'interface.
			lFinal=zip(lF, lCoAff)
			
			# Parcours pour la découpe de chaque image
			for a1 in enumerate(lFinal):
				
				# Index du morceau
				nb=a1[0]
				# Coordonnées de la découpe sous la forme (a, b, c, d)
				cDecoup=a1[1][0]
				# Coordonnées d'affichage ds l'interface (a, b)
				cAffInterfac=a1[1][1]
					
				# Ouverture de la 1ère image du lot
				im=Image.open(self.listeImgSource[0])
				
				# Voir doc: http://www.pythonware.com/library/pil/handbook/introduction.htm
				# Découpe ...
				c=im.crop(cDecoup)
				# Pour les commentaires de cette partie en particulier, voir dans la fonction appliquer
				c.save(self.repTampon+'_'+string.zfill(1, 3)+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+ext)
				
				# Ré-ouverture ...
				im2=Image.open(self.repTampon+'_'+string.zfill(1, 3)+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+ext)
				
				# Copie des images découpées dans l'image de fond
				imgFond.paste(im2, cAffInterfac)
				# Sauvegarde dans le rep. tampon pour affichage dans l'interface
				imgFond.save(self.repTampon+'dec_im_'+string.zfill(1, 3)+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+'.jpg')

			# Chemin de sauvegarde
			self.cheminCourantSauv=self.repTampon+'dec_im_'+string.zfill(1, 3)+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+'.jpg'

			# Affichage de l'image temporaire 
			# Ouverture d'une boite de dialogue affichant l'aperçu.
			#
			# Affichage par le bouton Voir le résultat
			visio = VisionneurEvolue(self.cheminCourantSauv)
			visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
			visio.exec_()
		
			return 0	

		# Si coin et ombre sélectionné
		elif self.comboReglage.currentIndex()==2 :
			self.progress.reset()
			self.progress.show()
			self.progress.setValue(0)
			QApplication.processEvents()
			# Lancement de la conversion dans 250 ms (seule solution trouvée pour éviter le grisage au début)
			#self.timer.start(250)
			# récupération des paramètres des réglages partie coin
			coin = self.cow.getParametresCoin()
			# récupération des paramètres des réglages  partie ombre
			ombre = self.cow.getParametresOmbre()
			# Fichier source = Fichier sélectionné par l'utilisateur dans le tab image(s) source
			fichierSource = [self.afficheurImgSource.getFile()]
			# Fichier de sortie
			self.cheminCourantSauv = EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep + u'preview_1.png'
			# Présence d'ombre portée ou pas (0 pour non, 1 pour oui)
			self.ombre_portee_oui_non = int(ombre[0])
			
			if self.ombre_portee_oui_non == 0:
				# -----------------------------------------------------------------------------
				# Pour le cas de la prévisualisation sans ombre portée
				# -----------------------------------------------------------------------------
				# Attribution de la variable ombre contenant ici des données spécifiques. Les 
				# données ici présentes n'ont pas les mêmes valeurs que pour la variable ombre
				# présente dans les cas du choix de coins arrondis avec ombre portée.
				# Pour coin[0], coin[1], coin[2]:
				# -------------------------------
				# Les valeurs des couleurs de l'ombre correspondent aux valeurs des couleurs
				# des coins arrondis.
				# Pour le zéro:
				# -------------
				# La valeur du flou de l'ombre est attribué à zéro.
				# Pour -18:
				# ---------
				# Pour cette valeur on affecte la valeur -18. Voici le détail:
				# --> (le -18 est obtenu comme cela)
				# * à l'origine valeur du décalage de l'ombre (on ajoute 10 à cette valeur)
				# * pour finir on doit prévoir 8 pixels en plus pour le floutage
				# En définitive pour éliminer cette ombre portée il faut une valeur de -18 
				# Pour plus d'éléments, voir dans la classe PCoinOmbre.
				ombre = (True, coin[0], coin[1], coin[2], 0, -18)
				# Initialisation de la classe de réalisation du travail :
				processCoinOmbre = PCoinOmbre(fichierSource, EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep + u'preview', 1, coin, ombre, self.progress)
				if processCoinOmbre.start() :
					# Affichage de l'image temporaire 
					# Ouverture d'une boite de dialogue affichant l'aperçu.
					#
					# Affichage par le bouton Voir le résultat
					visio = VisionneurEvolue(self.cheminCourantSauv)
					visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
					visio.exec_()
					#
					return 0
			
			elif self.ombre_portee_oui_non == 1:
				# Initialisation de la classe de réalisation du travail :
				processCoinOmbre = PCoinOmbre(fichierSource, EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep + u'preview', 1, coin, ombre, self.progress)
				if processCoinOmbre.start() :
					# Affichage de l'image temporaire 
					# Ouverture d'une boite de dialogue affichant l'aperçu.
					#
					# Affichage par le bouton Voir le résultat
					visio = VisionneurEvolue(self.cheminCourantSauv)
					visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
					visio.exec_()
					#
					return 0


	def appliquer0(self):
		'''Préparation de la conversion'''
		
		'''
		C'est quoi ce truc, c'est un bug ??
		
		On se met ds la situation où on charge (par exemple) 3 images et qu'on sélectionne:
		Image > Pour le web > Morcellement/découpe d'image, on clique sur Appliquer et sauver,
		la barre de  progression fonctionne bien, les images découpées sont bien affichées et
		enregistrées sur le disque. Maintenant on ds l'onglet Image(s) source et on supprime
		une image (bouton Retirer), on clique sur Appliquer et sauver ... EKD se ferme brutalement
		et on a ce message ds la console:
		
		ASSERT failure in QVector<T>::at: "index out of range", file ../../include/QtCore/../../src/corelib/tools/qvector.h, 
		line 316
		Abandon
		
		Cela ne se produit que si j'active self.listeImgDestin=[], si désactivé aucun souci mais ...
		
		Le problème est qu'il faut vider la liste self.listeImgDestin car si elle n'est pas vidée
		les images issues de la découpe (et les gifs animés) s'accumulent irrémédiablement ... et 
		ce ds le cas de plusieurs traitements successifs. Donc obligé de désactiver 
		self.listeImgDestin=[] pour l'instant.
		'''
		
		# Si l'utilisateur charge des images de taille différente, fait le traitement 
		# ...,  recharge de nouvelles images, il faut que les répertoires de redimen-
		# sionnement soient vidés
		
		listePresRedim_1=glob.glob(self.repTampon+'redim_1'+os.sep+'*.*')
		if len(listePresRedim_1)>0:
			for parcR_1 in listePresRedim_1: os.remove(parcR_1)

		# Récupération de la liste des fichiers chargés
		self.listeChemin=self.afficheurImgSource.getFiles()
		
		# Redimensionner les images de tailles différentes? -> Seulement pour les traitements gif animé et découpe image.
		if self.comboReglage.currentIndex() != 2 :
			self.redim_img()
		
		# Utilisation de la nouvelle boîte de dialogue de sauvegarde
		suffix=""
                self.chemDossierSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.chemDossierSauv = self.chemDossierSauv.getFile()
		
		if not self.chemDossierSauv: return
		
		# Récupération de l'identifiant du codec
		self.i = self.comboReglage.currentIndex()
		
		self.progress.reset()
		self.progress.show()
		self.progress.setValue(0)
		QApplication.processEvents()
		
		# Lancement de la conversion dans 250 ms (seule solution trouvée pour éviter le grisage au début)
		self.timer.start(250)
	
	
	def appliquer(self):
		"""Conversion des images"""
		
		# Liste pour affichage des images chargées (ds le tabwidget)
		listeAff_1=[]
		# Liste pour affichage des images sauvegardées (ds le tabwidget)
		listeAff_2=[]

		# Si Gif animé est sélectionné
		if self.comboReglage.currentIndex()==0:
			
			# La liste pour l'affichage des images ds l'interface est
			# vidée pour que les images affichées ne s'amoncellent pas
			# si plusieurs rendus à la suite
			if len(self.listeImgDestin)>0: del self.listeImgDestin[:]
			
			nbreElem=len(self.listeImgSource)
			
			# Recup de la valeur de Nombre de couleurs (Réduction)
			spinCouleur = str(self.spinCouleursDelai.spin1.value())
			# Nouveau temps de pause entre 2 images
			spinDelai = str(self.spinCouleursDelai.spin2.value())
			if self.spinLargeur.isEnabled():
				# Nouvelle largeur
				spinLargeur = str(self.spinLargeur.spin.value())
			
			listeChemin = ["\"" + i + "\"" for i in self.listeImgSource]
			
			commande = 'convert -quiet -delay '+spinDelai+' -loop 0 -colors '+spinCouleur+' '+' '.join(listeChemin)+' '+"\""+self.chemDossierSauv+'.gif'+"\""
			
			# On ne redimensionne que si la boite de spin associée est active
			if self.spinLargeur.isEnabled():
				commande = commande.replace('convert', 'convert -resize ' + spinLargeur)
			
			# Mise en place des conditions pour Linux et Windows
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				
				process = QProcess(self)
				process.start(commande)
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				
				# Attention (sous Windows !!!) si on appelle une commande exterieure
				# (c'est a dire une commande non Python [par PIL ou Numpy par
				# exemple]) par QProcess, la commande en question ne sera pas
				# executee ... et aucun warning ou message d'erreur ne sera fourni
				# !!!. Il faut obligatoirement passer par os.system (!)
				os.system(commande)
			
			for parc in range(nbreElem):
			
				# Remplissage de la liste pour les statistiques de rendu
				listeAff_1.append(self.listeImgSource[parc])
				
				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée .
				val_pourc=((parc+1)*100)/nbreElem

				# Bouton Cancel pour arrêter la progression donc le process
				if (self.progress.wasCanceled()): break

				self.progress.setValue(val_pourc)
			
				QApplication.processEvents()
				# --------------------------------------------

			# Ajout des images par la variable self.cheminCourantSauv dans la liste 
			# self.listeImgDestin. Cette liste sert à récupérer les images pour l'affichage 
			# des images ds l'inteface.
			self.listeImgDestin.append(self.chemDossierSauv+'.gif')
			
			# Affichage des images après traitement
			#
			# Changement d'onglet et fonctions associées
			self.conversionImg = 1
			self.metaFctTab(self.indexTabImgDestin)
			
			# Affichage des infos sur l'image -------------------------	
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte1=_(u" Image(s) chargée(s)")
			texte2=_(u" Gif animé final")
			a='#'*36
			
			self.infosImgProv_1=a+'\n#'+texte1+'\n'+a
			self.infosImgProv_2=a+'\n#'+texte2+'\n'+a
		
			# Images chargées
			for parcStatRendu_1 in listeAff_1:
				self.infosImgProv_1=self.infosImgProv_1+'\n'+parcStatRendu_1
			
			# Gif animé sauvegardé
			self.infosImgProv_2=self.infosImgProv_2+'\n'+self.chemDossierSauv+'.gif'
		
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv_1+'\n\n'+self.infosImgProv_2+'\n\n')
			self.framInfos.setEnabled(True)
			
			# remise à 0 de la variable provisoire de log
			self.infosImgProv_1=''
			self.infosImgProv_2=''
			# ---------------------------------------------------------

		# Si Morcellement/découpe d'image est sélectionné	
		elif self.comboReglage.currentIndex()==1:

			# La liste pour l'affichage des images ds l'interface est
			# vidée pour que les images affichées ne s'amoncellent pas
			# si plusieurs rendus à la suite
			if len(self.listeImgDestin)>0: del self.listeImgDestin[:]
			
			# Recup de la valeur de Nombre de morceaux (sens horizontal)
			spin_1 = self.listeComboReglage[self.i][3].spin1.value()
			# Recup de la valeur de Nombre de morceaux (sens vertical)
			spin_2 = self.listeComboReglage[self.i][3].spin2.value()
			
			# Ouverture de la 1ère image du lot pour extension
			im=Image.open(self.listeImgSource[0])
			# Chemin, extension
			f, ext=os.path.splitext(self.listeImgSource[0])
			
			# Résolution de l'image
			resLarg, resHaut=im.size
			
			# Comprehension-list pour calculer les coordonnées de découpe dans le sens horizontal
			l_1=[(totoX*(resLarg/spin_1), totoY*(resHaut/spin_2)) for totoY in range(spin_2) for totoX in range(spin_1)]
			# Comprehension-list pour calculer les coordonnées de découpe dans le sens vertical
			l_2=[(totoX*(resLarg/spin_1)+(resLarg/spin_1), totoY*(resHaut/spin_2)+(resHaut/spin_2)) for totoY in range(spin_2) for totoX in range(spin_1)]
			# Regroupement sens horizontal et vertical
			inter=zip(l_1, l_2)
			# Regroupement final des coordonnées horizontales et verticales pour la découpe.
			# Affiche par exemple: [(0, 0, 105, 144), (105, 0, 210, 144), (210, 0, 315, 144), ...]
			lF=[(x1[0], x1[1], y1[0], y1[1]) for x1, y1 in inter]
			
			# Marge (en pixels) pour l'affichage
			marge=6
			# Calcul des coordonnées pour affichage dans l'interface
			lCoAff=[(((tX+1)*marge)+(tX*(resLarg/spin_1)), ((tY+1)*marge)+(tY*(resHaut/spin_2))) for tY in range(spin_2) for tX in range(spin_1)]
			# Largeur de l'image de fond pour affichage ds l'interface
			largFondAffichage=resLarg+((spin_1+1)*marge)
			# Hauteur de l'image de fond pour affichage ds l'interface
			hautFondAffichage=resHaut+((spin_2+1)*marge)
			# Creation de l'image de fond pour acceuillir les morceaux de l'image (affichage
			# dans l'interface)
			imgFond=Image.new('RGB', (largFondAffichage, hautFondAffichage), (119, 119, 121))
			
			# Regroupement des coordonnées horizontales et verticales pour la découpe et des
			# coordonnées d'affichage des images découpées dans l'interface.
			lFinal=zip(lF, lCoAff)
			
			nbreElem_2=len(self.listeImgSource)
			
			# Parcours principal des images chargées par l'utilisateur
			for parcImg in range(nbreElem_2):
				# Parcours pour la découpe de chaque image
				for a1 in enumerate(lFinal):
				
					# Index du morceau
					nb=a1[0]
					# Coordonnées de la découpe sous la forme (a, b, c, d)
					cDecoup=a1[1][0]
					# Coordonnées d'affichage ds l'interface (a, b)
					cAffInterfac=a1[1][1]
				
					#print 'Index', nb, 'Coord decoupe', cDecoup, 'Coord affichage', cAffInterfac
					EkdPrint(u'Index: %s, Coord decoupe: %s, Coord affichage: %s' % (nb, cDecoup, cAffInterfac))
					
					# Ouverture de chaque image
					im=Image.open(self.listeImgSource[parcImg])
					
					# ---------------------------------------------------------
					# Sauvegarde de la découpe sur le disque dur
					# ---------------------------------------------------------
					
					cheminSauv=self.chemDossierSauv+'_'+string.zfill(parcImg+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+ext
				
					# Voir doc: http://www.pythonware.com/library/pil/handbook/introduction.htm
					# Découpe ...
					c=im.crop(cDecoup)
					# Attention (et ce pour chaque fichier qui sera sauvegardé --> utilisateur
					# ou rep. temporaire) le 1er chiffre correspondra à l'image en cours, le 
					# second chiffre correspondra au morceau découpé en cours, la dernière
					# partie correspond au nombre de morceaux sur chaque ligne ... le signe
					# multiplié ... le nombre de morceaux sur chaque colonne. Exemple:
					# /.../.../.../nom_image_003_006_3x2.jpg
					# --> il s'agit de la 3ème image et du 6ème morceau découpé ... et nous
					# avons 3 images sur chaque ligne et 2 sur chaque colonne.
					c.save(cheminSauv)
					
					# ---------------------------------------------------------
					# Sauvegarde pour affichage des images dans l'interface
					# ---------------------------------------------------------
					
					# Sauvegarde des images et construction des plaques reconstituées d'images 
					# pour l'affichage dans l'interface
					c.save(self.repTampon+'aff_img_decoup_'+string.zfill(parcImg+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+ext)
					# Ré-ouverture ...
					im2=Image.open(self.repTampon+'aff_img_decoup_'+string.zfill(parcImg+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+ext)
					# Copie des images découpées dans l'image de fond (la plaque)
					imgFond.paste(im2, cAffInterfac)
					# Sauvegarde dans le rep. tampon pour affichage dans l'interface
					imgFond.save(self.repTampon+'aff_img_decoup_'+string.zfill(parcImg+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+ext)
					
					# ---------------------------------------------------------
					# Infos
					# ---------------------------------------------------------
					
					# Remplissage de la liste pour les statistiques de rendu
					listeAff_1.append(self.listeImgSource[parcImg])
				
					# Remplissage de la liste des pages sauvegardées (Info)
					listeAff_2.append(cheminSauv)
				
					# La page Image résultat devient visible à la fin des conversions
					#self.tabwidget.setCurrentIndex(self.indexTabImgDestin)
					
					# --------------------------------------------
					# Affichage de la progression (avec
					# QProgressDialog) ds une fenêtre séparée .
					val_pourc=((parcImg+1)*100)/nbreElem_2
					#val_pourc=((parcImg+1)*100)/self.nbrImg

					# Bouton Cancel pour arrêter la progression donc le process
					if (self.progress.wasCanceled()): break

					self.progress.setValue(val_pourc)
			
					QApplication.processEvents()
					# --------------------------------------------

				# Ajout des images pour l'affichage dans la liste self.listeImgDestin.
				# Les images en question sont les morceaux découpés qui sont ensuite 
				# reconstitués sur la plaque (image de fond) et réaffichés dans l'interface
				self.listeImgDestin.append(self.repTampon+'aff_img_decoup_'+string.zfill(parcImg+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+'_'+string.zfill(nb+1, 3)+'_'+str(spin_1)+'x'+str(spin_2)+ext)

				# Affichage des images après traitement
				#
				# Changement d'onglet et fonctions associées
				self.conversionImg = 1
				self.metaFctTab(self.indexTabImgDestin)

			# Récupération du chemin + nom des fichiers
			# sauvegardés en ayant éliminé les doublons
			listeAff_1=list(set(listeAff_1))
			listeAff_1.sort()
			
			# Affichage des infos sur l'image -------------------------	
			# On implémente les chemins des fichiers dans une variable
			# pour préparer l'affichage des infos
			texte1=_(u" Image(s) chargée(s)")
			texte2=_(u" Image(s) et morceaux découpés")
			a='#'*36
			
			self.infosImgProv_1=a+'\n#'+texte1+'\n'+a
			self.infosImgProv_2=a+'\n#'+texte2+'\n'+a
		
			# Images chargées
			for parcStatRendu_1 in listeAff_1:
				self.infosImgProv_1=self.infosImgProv_1+'\n'+parcStatRendu_1
			
			# Pages sauvegardées
			for parcStatRendu_2 in listeAff_2:
				self.infosImgProv_2=self.infosImgProv_2+'\n'+parcStatRendu_2
		
			# affichage des infos dans l'onglet
			self.zoneAffichInfosImg.setText(self.infosImgProv_1+'\n\n'+self.infosImgProv_2+'\n\n')
			self.framInfos.setEnabled(True)
			
			# remise à 0 de la variable provisoire de log
			self.infosImgProv_1=''
			self.infosImgProv_2=''
			# ---------------------------------------------------------

		# Si coin et ombre sélectionné
		elif self.comboReglage.currentIndex()==2 :
			# récupération des paramètres des réglages partie coin
			coin = self.cow.getParametresCoin()
			# récupération des paramètres des réglages  partie ombre
			ombre = self.cow.getParametresOmbre()
			# Fichiers sources = self.listeChemin -> A limiter aux éléments à traiter (à partir de xxx)
			fichiersSource = self.listeChemin[self.spin1_ImTrait.value()-1:]
			# Nom fichier de sortie = self.chemDossierSauv et nombre de chiffre pour la numérotation : self.spin2_ImTrait
			# Initialisation de la classe de réalisation du travail :
			processCoinOmbre = PCoinOmbre(fichiersSource, self.chemDossierSauv, self.spin2_ImTrait.value(), coin, ombre, self.progress)
			if processCoinOmbre.start() :
				# Activation de l'onglet "visualisation des images créées" + Affichage des infos dans l'onglet "infos"
				self.listeImgDestin = processCoinOmbre.getResultFiles()
				# Changement d'onglet et fonctions associées
				self.conversionImg = 1
				self.metaFctTab(self.indexTabImgDestin)
				# Affichage des infos sur l'image -------------------------	
				# On implémente les chemins des fichiers dans une variable
				# pour préparer l'affichage des infos
				texte1=_(u" Image(s) chargée(s)")
				texte2=_(u" Image(s) après traitement")
				a='#'*36
			
				self.infosImgProv_1=a+'\n#'+texte1+'\n'+a
				self.infosImgProv_2=a+'\n#'+texte2+'\n'+a
				for img in fichiersSource :
					self.infosImgProv_1 += u"\n"+img
				for img in self.listeImgDestin :
					self.infosImgProv_2 += u"\n"+img

				# affichage des infos dans l'onglet
				self.zoneAffichInfosImg.setText(self.infosImgProv_1+'\n\n'+self.infosImgProv_2+'\n\n')
				self.framInfos.setEnabled(True)
			
				# remise à 0 de la variable provisoire de log
				self.infosImgProv_1=''
				self.infosImgProv_2=''
				
			else :
				# Message d'erreur
				# A compléter
				#print u"Erreur lors du traitement"
				EkdPrint(u"Erreur lors du traitement")
	
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""
		# Nouvelle fenêtre d'aide
		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<p><b>Vous pouvez ici faire quelques traitements concernant la publication d'images sur internet, spécifiquement: gif animé et morcellement/découpe d'image.</b></p><p>Dans l'onglet <b>'Image(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Dans l'onglet <b>'Réglages'</b> sélectionnez votre <b>'Type'</b> (<b>Gif animé</b> ou <b>Morcellement/découpe d'image</b>), faites le/les réglage(s) correspondant au <b>'Type'</b> choisi. Si vous avez choisi <b>Morcellement/découpe d'image</b> vous voyez apparaître <b>'Traitement à partir de l'image (numéro)'</b> et <b>'Nombre de chiffres après le nom de l'image'</b> changez en les valeurs si vous le désirez <b><font color='red'>(la plupart du temps celles par défaut suffisent)</font></b>.</p><p>Cliquez sur le bouton <b>'Voir le résultat'</b>, vous voyez à ce moment là le résultat de vos réglages s'afficher dans une nouvelle fenêtre. A ce sujet et concernant la transformation en <b>'Gif animé'</b>, le résultat de la conversion se fait uniquement sur les deux premières images du lot ... et cela pour (entre autre) voir en images ce que donne le réglage du <b>'Temps de pause entre 2 trames (ms)'</b>.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer et sauver'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>'Images après traitement'</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite) et ce dans le cas de <b>Morcellement/découpe d'image</b>, pour ce qui est de lancer l'animation pour un gif animé, faites un clic droit sur l'image dans la fenêtre de rendu et cliquez soit sur le petit bouton <b>Mettre en pause/démarrer l'animation</b>, soit sur <b>Arrêter l'animation</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les image(s) chargée(s) et les image(s) convertie(s).</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'spin1_ImTrait', unicode(self.spin1_ImTrait.value()))
		EkdConfig.set(self.idSection, u'spin2_ImTrait', unicode(self.spin2_ImTrait.value()))
		EkdConfig.set(self.idSection, u'spinCouleursDelai', unicode(self.spinCouleursDelai.value()))
		EkdConfig.set(self.idSection, u'spinLargeur1', unicode(self.spinLargeur.spin.value()))
		EkdConfig.set(self.idSection, u'spinLargeur2', unicode(self.spinLargeur.spin2.value()))
		EkdConfig.set(self.idSection, u'spinMorcellement1', unicode(self.spinMorcellement.spin.value()))
		EkdConfig.set(self.idSection, u'spinMorcellement2', unicode(self.spinMorcellement.spin2.value()))
		EkdConfig.set(self.idSection, u'checkModifLargeur', unicode(int(self.checkModifLargeur.isChecked())))
		EkdConfig.set(self.idSection, u'format_sortie', unicode(self.comboReglage.currentIndex()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.spin1_ImTrait.setValue(int(EkdConfig.get(self.idSection, 'spin1_ImTrait')))
		self.spin2_ImTrait.setValue(int(EkdConfig.get(self.idSection, 'spin2_ImTrait')))
		self.spinCouleursDelai.setValue(int(EkdConfig.get(self.idSection, 'spinCouleursDelai')))
		self.spinLargeur.spin.setValue(int(EkdConfig.get(self.idSection, 'spinLargeur1')))	
		self.spinLargeur.spin2.setValue(int(EkdConfig.get(self.idSection, 'spinLargeur2')))	
		self.spinMorcellement.spin.setValue(int(EkdConfig.get(self.idSection, 'spinMorcellement1')))	
		self.spinMorcellement.spin2.setValue(int(EkdConfig.get(self.idSection, 'spinMorcellement2')))	
		self.checkModifLargeur.setChecked(int(EkdConfig.get(self.idSection, 'checkModifLargeur')))
		self.comboReglage.setCurrentIndex(int(EkdConfig.get(self.idSection, 'format_sortie')))


# Classe pour le calcul (traitement sur lot d'images) 
# des coins arrondis et de l'ombre portée.
class PCoinOmbre :

	def __init__(self, liste_image_chargees, motifFichierSortie, nbrChiffreFichSortie, coin, ombre, progress) :
		
		self.liste_image_chargees = liste_image_chargees
		self.motifFichierSortie  = motifFichierSortie
		self.nbrChiffreFichSortie = int(nbrChiffreFichSortie)
		# Données partie coin
		self.fondR = coin[0]
		self.fondG = coin[1]
		self.fondB = coin[2]
		self.dimCoin = coin[3]
		# données partie ombre portée
		self.ombre_portee_oui_non = int(ombre[0])
		self.regCoulOmbPortR = ombre[1]
		self.regCoulOmbPortG = ombre[2]
		self.regCoulOmbPortB = ombre[3]
		self.decalOmbrPortee = ombre[5]
		self.intensFlouOmbrPortee = ombre[4]
		# fenêtre de progression
		self.progress = progress
		# Preview ou non

		# Vérification que le répertoire temporaire existe et est vide.
		if os.path.exists(EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep) :
			for tmpFile in os.listdir(EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep) :
				os.remove(EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep + tmpFile)
		else : os.mkdir(EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep)
		self.repTamponDeTravail = EkdConfig.getTempDir() + os.sep+ u'coins_arrondis' + os.sep
		
		# Définition du répertoire de référence des masques
		self.repTamponMasque = os.getcwd() + os.sep + u'masques' + os.sep + u'masques_coins_arrondis' + os.sep

		# Gestion de du décalage de l'ombre portée en rapport avec le rayon du coin arrondi
		if self.decalOmbrPortee < self.dimCoin+10:
			#print 
			EkdPrint(u'')
			#print "La valeur du décalage de l'ombre portée doit corresponde à au moins cette valeur plus 10"
			EkdPrint(u"La valeur du décalage de l'ombre portée doit corresponde à au moins cette valeur plus 10")
			#print "C'est le cas dans la situation présente, par conséquent la valeur du décalage de l'ombre"
			EkdPrint(u"C'est le cas dans la situation présente, par conséquent la valeur du décalage de l'ombre")
			#print "portée va être augmentée de dix pixels."
			EkdPrint(u"portée va être augmentée de dix pixels.")
			#print
			EkdPrint(u'')
			self.decalOmbrPortee = self.decalOmbrPortee + 10

		# Pour avoir les dimensions exactes de chaque coin
		# il faut bien sûr multiplier le rayon par 2
		self.dimCoin = self.dimCoin * 2

		# On doit prévoir quelques pixels en plus pour le floutage
		self.decalOmbrPortee = self.decalOmbrPortee + 8

		self.nbreElem = len(self.liste_image_chargees)
		# Initialisation de la barre de progression
		self.progress.setRange(0, self.nbreElem*2)
		self.progress.setValue(0)
		QApplication.processEvents()
		# debug 
		#print "Valeur du range du QProgress : ", self.nbreElem
		EkdPrint(u"Valeur du range du QProgress: %s" % self.nbreElem)

		# Liste des fichiers de sortie -> Pour compléter le tab info en fin de process 
		self.listeOutputFiles = []
		#print '---------------------------------------------------' # Fin de l'initialisation du process
		EkdPrint(u'---------------------------------------------------') # Fin de l'initialisation du process

	def start(self) :
		# Variable pour monitorer le process
		processOK = 1
		# Boucle principale de chargement des images .
		for parcPrincipal in range(self.nbreElem):

			#print "Traitement de l'image:", parcPrincipal+1
			EkdPrint(u"Traitement de l'image: %s" % str(parcPrincipal+1))
			#print '---------------------------------------------------'
			EkdPrint(u'---------------------------------------------------')
		
			# Ouverture de l'image dans le lot .
			img = Image.open(self.liste_image_chargees[parcPrincipal])

			# Conversion en RGB (car autrement cela pose problème avec
			# les images en niveaux de gris, c'est à dire avec un mode L)
			img = img.convert('RGB')

			dim_largeur_border = img.size[0]
			dim_hauteur_border = img.size[1]

			coin_haut_gauche = Image.open(self.repTamponMasque+'border_haut_gauche.png')
			coin_haut_droite = Image.open(self.repTamponMasque+'border_haut_droite.png')
			coin_bas_gauche = Image.open(self.repTamponMasque+'border_bas_gauche.png')  
			coin_bas_droite = Image.open(self.repTamponMasque+'border_bas_droite.png')

			coin_haut_gauche = coin_haut_gauche.resize((self.dimCoin, self.dimCoin), Image.ANTIALIAS)
			coin_haut_droite = coin_haut_droite.resize((self.dimCoin, self.dimCoin), Image.ANTIALIAS)
			coin_bas_gauche = coin_bas_gauche.resize((self.dimCoin, self.dimCoin), Image.ANTIALIAS)
			coin_bas_droite = coin_bas_droite.resize((self.dimCoin, self.dimCoin), Image.ANTIALIAS)

			source_1 = coin_haut_gauche.convert('RGBA')
			source_2 = coin_haut_droite.convert('RGBA')
			source_3 = coin_bas_gauche.convert('RGBA')
			source_4 = coin_bas_droite.convert('RGBA')

			# Récup des données du coin haut gauche
			source_1_data = source_1.getdata()

			# ----------- Numpy data 1 ---------------------------------------------
			imageDataSource_1 = array(source_1_data)

			# ... mais selon Gaël Varoquaux --> "C'est la même chose si imageDataSource_1 
			# est 2D, mais mon code marche pour un nombre de dimension arbitraire. Discussion
			# disponible ici: https://listes.aful.org/wws/arc/python/2010-10/msg00025.html
			# (lire la totalité des discussions).
			r_s1 = imageDataSource_1[..., 0].ravel()
			g_s1 = imageDataSource_1[..., 1].ravel()
			b_s1 = imageDataSource_1[..., 2].ravel()
			a_s1 = imageDataSource_1[..., 3].ravel()

			# Création d'une 1ère matrice remplie de 1 (laquelle sera ensuite
			# re-remplie par les canaux r, g, b, a et par concaténation).
			nouvell_coul_s1 = ones(((self.dimCoin * self.dimCoin),3), dtype=int16)
			nouvell_coul_s1[:,0] = self.fondR
			nouvell_coul_s1[:,1] = self.fondG
			nouvell_coul_s1[:,2] = self.fondB

			# Concaténation des canaux r, g, b et du canal alpha retraité avec 
			# Numpy --> Changement de couleur.
			# Cette syntaxe est beaucoup mieux adaptée et surtout elle ne génère
			# pas d'erreur. Par rapport à cela, merci à Gaël Varoquaux !
			concCoulAlpha_s1 = concatenate((nouvell_coul_s1, a_s1[..., None]), axis=1)
			# ----------- Fin Numpy data 1 -----------------------------------------

			# ----------- Traitement par PIL de l'image data 1 ---------------------
			dataFinal_s1 = concCoulAlpha_s1.tolist()
			# Transformation des sous-listes (listes ds les listes 
			# c'est à dire en 2 dimensions) en tuples
			dataFinal_s1 = [tuple(s1) for s1 in dataFinal_s1]
			# Creation d'une nouvelle image et integration des donnees recoltees .
			newImage_s1 = Image.new('RGBA', (self.dimCoin, self.dimCoin))
			newImage_s1.putdata(dataFinal_s1)
			a1_s1, a2_s1, a3_s1, a4_s1 = newImage_s1.split()
			imgMerge_s1 = Image.merge('RGBA', (a1_s1, a2_s1, a3_s1, a4_s1))
			# ----------- Fin du traitement par PIL de l'image data 1 --------------

			source_2_data = source_2.getdata()

			# ----------- Numpy data 2 ---------------------------------------------
			imageDataSource_2 = array(source_2_data)

			r_s2 = imageDataSource_2[..., 0].ravel()
			g_s2 = imageDataSource_2[..., 1].ravel()
			b_s2 = imageDataSource_2[..., 2].ravel()
			a_s2 = imageDataSource_2[..., 3].ravel()

			nouvell_coul_s2 = ones(((self.dimCoin * self.dimCoin),3), dtype=int16)
			nouvell_coul_s2[:,0] = self.fondR
			nouvell_coul_s2[:,1] = self.fondG
			nouvell_coul_s2[:,2] = self.fondB

			concCoulAlpha_s2 = concatenate((nouvell_coul_s2, a_s2[..., None]), axis=1)
			# ----------- Fin Numpy data 2 -----------------------------------------

			# ----------- Traitement par PIL de l'image data 2 ---------------------
			dataFinal_s2 = concCoulAlpha_s2.tolist()
			dataFinal_s2 = [tuple(s2) for s2 in dataFinal_s2]
			newImage_s2 = Image.new('RGBA', (self.dimCoin, self.dimCoin))
			newImage_s2.putdata(dataFinal_s2)
			a1_s2, a2_s2, a3_s2, a4_s2 = newImage_s2.split()
			imgMerge_s2 = Image.merge('RGBA', (a1_s2, a2_s2, a3_s2, a4_s2))
			# ----------- Fin du traitement par PIL de l'image data 2 --------------
	
			source_3_data = source_3.getdata()

			# ----------- Numpy data 3 ---------------------------------------------
			imageDataSource_3 = array(source_3_data)

			r_s3 = imageDataSource_3[..., 0].ravel()
			g_s3 = imageDataSource_3[..., 1].ravel()
			b_s3 = imageDataSource_3[..., 2].ravel()
			a_s3 = imageDataSource_3[..., 3].ravel()

			nouvell_coul_s3 = ones(((self.dimCoin * self.dimCoin),3), dtype=int16)
			nouvell_coul_s3[:,0] = self.fondR
			nouvell_coul_s3[:,1] = self.fondG
			nouvell_coul_s3[:,2] = self.fondB

			concCoulAlpha_s3 = concatenate((nouvell_coul_s3, a_s3[..., None]), axis=1)
			# ----------- Fin Numpy data 3 -----------------------------------------

			# ----------- Traitement par PIL de l'image data 3 ---------------------
			dataFinal_s3 = concCoulAlpha_s3.tolist()
			dataFinal_s3 = [tuple(s3) for s3 in dataFinal_s3]
			newImage_s3 = Image.new('RGBA', (self.dimCoin, self.dimCoin))
			newImage_s3.putdata(dataFinal_s3)
			a1_s3, a2_s3, a3_s3, a4_s3 = newImage_s3.split()
			imgMerge_s3 = Image.merge('RGBA', (a1_s3, a2_s3, a3_s3, a4_s3))
			# ----------- Fin du traitement par PIL de l'image data 3 --------------
	
			source_4_data = source_4.getdata()

			# ----------- Numpy data 4 ---------------------------------------------
			imageDataSource_4 = array(source_4_data)

			r_s4 = imageDataSource_4[..., 0].ravel()
			g_s4 = imageDataSource_4[..., 1].ravel()
			b_s4 = imageDataSource_4[..., 2].ravel()
			a_s4 = imageDataSource_4[..., 3].ravel()

			nouvell_coul_s4 = ones(((self.dimCoin * self.dimCoin),3), dtype=int16)
			nouvell_coul_s4[:,0] = self.fondR
			nouvell_coul_s4[:,1] = self.fondG
			nouvell_coul_s4[:,2] = self.fondB

			concCoulAlpha_s4 = concatenate((nouvell_coul_s4, a_s4[..., None]), axis=1)
			# ----------- Fin Numpy data 4 -----------------------------------------

			# ----------- Traitement par PIL de l'image data 4 ---------------------
			dataFinal_s4 = concCoulAlpha_s4.tolist()
			dataFinal_s4 = [tuple(s4) for s4 in dataFinal_s4]
			newImage_s4 = Image.new('RGBA', (self.dimCoin, self.dimCoin))
			newImage_s4.putdata(dataFinal_s4)
			a1_s4, a2_s4, a3_s4, a4_s4 = newImage_s4.split()
			imgMerge_s4 = Image.merge('RGBA', (a1_s4, a2_s4, a3_s4, a4_s4))
			# ----------- Fin du traitement par PIL de l'image data 4 --------------

			# Liste contenant les données des 4 images des coins
			liste_des_data = [imgMerge_s1, imgMerge_s2, imgMerge_s3, imgMerge_s4]
			# Liste contenant les coordonnées pour le placement des 4 images des coins dans l'image cible
			liste_coordonnees_coins = [(0, 0),  ((dim_largeur_border - coin_haut_droite.size[0]), 0), (0, (dim_hauteur_border - coin_bas_gauche.size[1])), ((dim_largeur_border - coin_haut_droite.size[0]), (dim_hauteur_border - coin_bas_droite.size[1]))]
			# Liste contenant les 4 images des coins elles-mêmes
			liste_des_masques = [coin_haut_gauche, coin_haut_droite, coin_bas_gauche, coin_bas_droite]
			# Concaténation, sous la forme [(data1, coord1, masque1), ..., (data4, coord4, masque4)]
			listeDataCoordMasque = zip(liste_des_data, liste_coordonnees_coins, liste_des_masques)
			# Boucle pour la copie des 4 images de coin sur l'image cible et sauvegarde
			for parcDCM_1 in listeDataCoordMasque:
				img.paste(parcDCM_1[0], parcDCM_1[1], mask=parcDCM_1[2])
			self.progress.setValue(parcPrincipal*2+1)
			QApplication.processEvents()
			# Si on décide de traiter uniquement les coins arrondis, la sauvegarde se fait dans le rep de sauvegarde
			if self.ombre_portee_oui_non == 0:
				img.save(self.motifFichierSortie+string.zfill(parcPrincipal+1, self.nbrChiffreFichSortie)+'.png', 'PNG')
				self.progress.setValue(parcPrincipal+1)
				QApplication.processEvents()
				# debug 
				#print "Valeur du QProgress : ", parcPrincipal+1
				EkdPrint(u"Valeur du QProgress: %s" % parcPrincipal+1)
				self.listeOutputFiles.append(self.motifFichierSortie+string.zfill(parcPrincipal+1, self.nbrChiffreFichSortie)+'.png')
				self.progress.setValue((parcPrincipal+1)*2)
				QApplication.processEvents()

			# SI L'UTILISATEUR CHOISIT D'UTILISER LES OMBRES PORTEES
			if self.ombre_portee_oui_non == 1:

				# Creation de la/des nouvelle(s) image(s) à la couleur de l'ombre portée choisie par l'utilisateur
				# En fait il s'agit de la création de l'ombre portée (avec les bords nets pour l'instant)
				nouvImgOmbre = Image.new('RGB', (dim_largeur_border, dim_hauteur_border), (self.regCoulOmbPortR, self.regCoulOmbPortG, self.regCoulOmbPortB))

				# Boucle pour la copie des 4 images de coin sur l'image pour l'ombre portée et sauvegarde		
				for parcDCM_2 in listeDataCoordMasque:
					nouvImgOmbre.paste(parcDCM_2[0], parcDCM_2[1], mask=parcDCM_2[2])

				# Conversion en RGBA pour que l'image puisse être collée
				nouvImgOmbre = nouvImgOmbre.convert('RGBA')
				# Creation du fond sur lequel va être copié l'ombre portée et ensuite l'image chargée par l'utilisateur
				nouvImgFond = Image.new('RGB', (dim_largeur_border + self.decalOmbrPortee, dim_hauteur_border + self.decalOmbrPortee), (self.fondR, self.fondG, self.fondB))
				# Conversion en RGBA pour que l'image puisse être collée
				nouvImgFond = nouvImgFond.convert('RGBA')
				# Collage de l'image
				nouvImgFond.paste(nouvImgOmbre, (self.decalOmbrPortee-8, self.decalOmbrPortee-8), mask=nouvImgOmbre)

				# Application d'un flou sur les bords de l'ombre portée (avec la valeur de l'intensité du flou
				# définie par l'utilisateur).
				for iFlouOmPort in range(self.intensFlouOmbrPortee): nouvImgFond = nouvImgFond.filter(ImageFilter.BLUR)

				# ----------------------------------------------------------------------
				# Traitement pour changer la couleur du coin bas droite et le mettre 
				# à la couleur de l'ombre portée (car ce coin là, contrairement aux
				# autres se trouve directement dans l'ombre portée
				# 
				# ---------- Traitement Numpy ------------------------------------------
				#
				imageDataSource_4 = array(imgMerge_s4)
				#
				r_s4_pour_omb_port = imageDataSource_4[..., 0].ravel()
				g_s4_pour_omb_port = imageDataSource_4[..., 1].ravel()
				b_s4_pour_omb_port = imageDataSource_4[..., 2].ravel()
				a_s4_pour_omb_port = imageDataSource_4[..., 3].ravel()
				#
				nouvell_coul_s4_pour_omb_port = ones(((self.dimCoin * self.dimCoin),3), dtype=int16)
				nouvell_coul_s4_pour_omb_port[:,0] = self.regCoulOmbPortR
				nouvell_coul_s4_pour_omb_port[:,1] = self.regCoulOmbPortG
				nouvell_coul_s4_pour_omb_port[:,2] = self.regCoulOmbPortB
				#
				concCoulAlpha_s4_pour_omb_port = concatenate((nouvell_coul_s4_pour_omb_port, a_s4[..., None]), axis=1)
				# 
				# ---------- Traitement Python Imaging Library -------------------------
				#
				dataFinal_s4_pour_omb_port = concCoulAlpha_s4_pour_omb_port.tolist()
				dataFinal_s4_pour_omb_port = [tuple(s4_pour_omb_port) for s4_pour_omb_port in dataFinal_s4_pour_omb_port]
				newImage_s4_pour_omb_port = Image.new('RGBA', (self.dimCoin, self.dimCoin))
				newImage_s4_pour_omb_port.putdata(dataFinal_s4_pour_omb_port)
				a1_s4_pour_omb_port, a2_s4_pour_omb_port, a3_s4_pour_omb_port, a4_s4_pour_omb_port = newImage_s4_pour_omb_port.split()
				imgMerge_s4_pour_omb_port = Image.merge('RGBA', (a1_s4_pour_omb_port, a2_s4_pour_omb_port, a3_s4_pour_omb_port, a4_s4_pour_omb_port))

				# --------- TRAITEMENT FINAL -------------------------------------------
				img.paste(imgMerge_s4_pour_omb_port, ((dim_largeur_border - coin_haut_droite.size[0]), (dim_hauteur_border - coin_bas_droite.size[1])), coin_bas_droite)
			
				# Collage final de l'image chargée par l'utilisateur à la position 0, 0
				nouvImgFond.paste(img, (0, 0))
				# Sauvegarde
				nouvImgFond.save(self.motifFichierSortie+'_'+string.zfill(parcPrincipal+1, self.nbrChiffreFichSortie)+'.png', 'PNG')
				self.progress.setValue(parcPrincipal+1)
				QApplication.processEvents()
				#print "Valeur du QProgress : ", parcPrincipal+1
				EkdPrint(u"Valeur du QProgress: %s" % str(parcPrincipal+1))
				self.listeOutputFiles.append(self.motifFichierSortie+'_'+string.zfill(parcPrincipal+1, self.nbrChiffreFichSortie)+'.png')
				self.progress.setValue((parcPrincipal+1)*2)
				QApplication.processEvents()

		#print "Traitement fini."
		EkdPrint(u"Traitement fini.")
		#print '---------------------------------------------------'
		EkdPrint(u'---------------------------------------------------')
		return processOK
		
	def getResultFiles(self) :
		return self.listeOutputFiles
