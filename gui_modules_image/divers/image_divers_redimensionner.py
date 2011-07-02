#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, Image, string, glob
from math import atan, cos, sin, pi, sqrt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_modules_image.image_base import Base, SpinSliders, SpinSlider

from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue

# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Nouvelle fenêtre d'aide
from gui_modules_common.EkdWidgets import EkdAide
# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class ElementLegende(QWidget):
	"Élément de la légende"
	def __init__(self, texte=": texte", couleurTrait=Qt.blue):
		QWidget.__init__(self)
		self.texte = texte
		self.couleurTrait = couleurTrait
		fm = QFontMetricsF(self.font())
		self.largeurFont = fm.width(self.texte)
		self.hauteurFont = fm.height()
		self.marge = 4
		self.largeurTrait = 30
		
	def sizeHint(self):
		return QSize(self.marge * 2 + self.largeurTrait + self.largeurFont, 4 / 3. * self.hauteurFont)

	def minimumSizeHint(self):
        	return QSize(self.marge * 2 + self.largeurTrait + self.largeurFont, 4 / 3. * self.hauteurFont)

	def paintEvent(self, event):
		paint = QPainter()
		paint.begin(self)
		yLigne = 3 / 4. * self.hauteurFont
		paint.drawText(self.largeurTrait + self.marge, self.hauteurFont, self.texte)
		paint.setPen(self.couleurTrait)
		paint.drawLine(self.marge, yLigne, self.largeurTrait, yLigne)
		paint.end()

class Apercu(QWidget):
	"""Apercu de la redimension d'images.
	Après instanciation de la classe, 3 variables doivent être définies (on les attribue
	depuis des méthodes set...()) pour que l'aperçu puisse s'afficher.
	"""
	def __init__(self, tailleCanevas=(400, 300), barreTaches=None):
		QWidget.__init__(self)
		# Taille du canevas
		self.tailleCanevas = tailleCanevas
		# Barre des tâches
		self.barreTaches = barreTaches
		# Facteur de redimensionnement des images par rapport au canevas
		self.facteur = 1.
		# Drapeau: Est-ce que l'aperçu vient d'être dessiné ?
		self.dessinApercu = 0
		# Tailles maximales (largeur, hauteur) des images source. La largeur et
		# la hauteur ne doivent pas obligatoirement appartenir à la même image
		self.maxSizeSourceImages = None, None
		
		#=== Variables à définir obligatoirement pour que l'aperçu soit tracé ===#
		# Taille (largeur, hauteur) des images à convertir
		self.sizeConvertImages = None
		# Liste des tailles d'images sources. Les élements de la liste sont
		# classés des tailles les plus fréquentes aux moins fréquentes
		self.listeTailleImage = None
		# Une image source de la taille la plus fréquente du lot
		self.image = QImage()
	
	def sizeHint(self):
		return QSize(self.tailleCanevas[0] + 5, self.tailleCanevas[1] + 5)

	def minimumSizeHint(self):
        	return QSize(self.tailleCanevas[0] + 5, self.tailleCanevas[1] + 5)
	
	def setImageTaillePlusFrequente(self, image=None):
		"Attribution de l'adresse d'une image source de la taille la plus fréquente du lot"
		self.image = QImage(image)
	
	def setListeTailleImage(self, liste):
		"""Modifie la liste des tailles d'images sources
		Les élements de la liste sont classés des tailles les plus fréquentes
		aux moins fréquentes
		"""
		self.listeTailleImage = liste
		self.__setMaxSizeSourceImages()
		# On attribue la hauteur des images converties si nécessaire
		self.setSizeConvertImages(self.sizeConvertImages[0])
		self.repaint()
		self.__setBarreTaches()
	
	def __setMaxSizeSourceImages(self):
		"""Calcul des tailles maximales de largeur et hauteur des images chargées
		(qui n'appartiennent pas forcément à la même image): (largeur, hauteur)
		Cette fonction ne peut être appelée de l'extérieur
		"""
		# tailles maximum par défaut
		tailleImgMax = [self.listeTailleImage[0][0], self.listeTailleImage[0][1]]
		for index, taille in enumerate(self.listeTailleImage):
			if taille[0] > tailleImgMax[0]:
				tailleImgMax[0] = taille[0]
			if taille[1] > tailleImgMax[1]:
				tailleImgMax[1] = taille[1]
		self.maxSizeSourceImages = tailleImgMax[0], tailleImgMax[1]
	
	def setSizeConvertImages(self, l=None, h=None):
		"Taille prévue pour les images converties: (largeur, hauteur)"
		if not h and self.listeTailleImage:
			taillePlusProbable = self.listeTailleImage[0]
			h = int(l * (float(taillePlusProbable[1]) / taillePlusProbable[0]))
		self.sizeConvertImages = l, h
		self.repaint()
		self.__setBarreTaches()
	
	def couleurContourSourceConvert(self):
		"""Renvoie les couleurs utilisés pour dessiner les contours des images sources
		et des images converties. On ne prend en compte qu'une couleur pour les images source,
		celle de l'image aux dimensions les plus présentes dans le lot.
		But: créer une légende en dehors de cette classe"""
		return QColor(Qt.black), QColor(Qt.darkGreen)
	
	def __setBarreTaches(self):
		"""On indique les tailles des images sources les plus probable et des images à convertir
		en barre des tâches (si elle existe et a été fournie)
		Cette fonction n'est pas appelable depuis l'extérieur
		"""
		if self.barreTaches and self.dessinApercu:
			txt = _(u"Images sources, Images converties")
			self.barreTaches.showMessage("%s : (%d ; %d) -> (%d ; %d)" %(txt,
				self.listeTailleImage[0][0], self.listeTailleImage[0][1],
				self.sizeConvertImages[0],self.sizeConvertImages[1]))
	
	def paintEvent(self, event):
		"""Dessin de l'apercu
		Retourne 1 si l'apercu a été dessiné, 0 sinon
		"""
		paint = QPainter()
		paint.begin(self)
		
		#=== Paramètres généraux ===#
		paint.setRenderHint(QPainter.Antialiasing)
				
		# Si on n'a pas suffisamment de paramètres pour tracer l'aperçu, alors on sort de la fonction
		if not self.sizeConvertImages[0] or not self.sizeConvertImages[1] \
			or not self.listeTailleImage or self.image.isNull():
			paint.end()
			self.dessinApercu = 0
			return
		
		#=== Paramètres numériques ===#
		# Calcul du facteur de redimensionnement des images sources et converties
		# par rapport au canevas
		# Largeur et hauteur maximales, images sources et futures images converties confondues
		lMax = max(self.maxSizeSourceImages[0], self.sizeConvertImages[0])
		hMax = max(self.maxSizeSourceImages[1], self.sizeConvertImages[1])
		marge = 4.
		fH = (self.tailleCanevas[1] - marge * 2) / hMax
		fL = (self.tailleCanevas[0] - marge * 2) / lMax
		# On choisit le facteur correspondant à la plus grande redimension pour rester
		# toujours dans les limites de notre canevas
		self.facteur = min(fH, fL)
		
		#=== Traçage ===#
		# Marge
		paint.translate(marge, marge)
		
		#---- Traçage des images sources
		tailleSourcePlusFreq = self.listeTailleImage[0][0], self.listeTailleImage[0][1]
		paint.drawImage(0, 0, self.image.scaled(self.facteur * tailleSourcePlusFreq[0],
					self.facteur * tailleSourcePlusFreq[1]))
		# Traçage des contours des images source
		paint.setBrush(Qt.NoBrush)
		couleur = [Qt.black, Qt.darkGray, Qt.gray, Qt.lightGray]
		for i, t in enumerate(self.listeTailleImage):
			# Plus le trait est foncé et plus la taille d'image source est probable
			if i < len(couleur):
				paint.setPen(couleur[i])
			else:
				# Au-délà de 4 tailles d'images, on ne joue plus sur le dégradé
				paint.setPen(couleur[len(couleur) - 1])
			paint.drawRect(0, 0, self.facteur * t[0], self.facteur * t[1])
		
		#---- Traçage des contours des images converties
		paint.setPen(Qt.darkGreen)
		paint.drawRect(0, 0, self.facteur * self.sizeConvertImages[0],
				self.facteur * self.sizeConvertImages[1])
		
		#---- Traçage de la flèche reliant les images sources de la taille la plus fréquente
		# aux  images à convertir
		pen = QPen(Qt.gray)
		pen.setStyle(Qt.DashLine)
		paint.setPen(pen)
		# Tuple (largeur, hauteur) des images sources les plus fréquentes
		tailleImgSourcePlusFreq = (self.facteur * self.listeTailleImage[0][0],
					self.facteur * self.listeTailleImage[0][1])
		# Tuple (largeur, hauteur) de l'image convertie
		tailleImgConvert = (self.facteur * self.sizeConvertImages[0],
					self.facteur * self.sizeConvertImages[1])
		
		#---- Traçage de la ligne de la flèche (mais pas les bouts)
		paint.drawLine(tailleImgSourcePlusFreq[0], tailleImgSourcePlusFreq[1],
				tailleImgConvert[0], tailleImgConvert[1])
		pen.setStyle(Qt.SolidLine)
		paint.setPen(pen)
		
		#---- Traçage des bouts des flèches quand on a la place
		# Taille de la ligne principale de la flèche
		tailleLigneFleche = sqrt((tailleImgConvert[0] - tailleImgSourcePlusFreq[0]) ** 2 +\
					(tailleImgConvert[1] - tailleImgSourcePlusFreq[1]) ** 2)
		# On ajoute pi à l'angle servant à tracer les bouts de flèche dans le cas où on
		# augmente la taille des images dans le sens de la hauteur (peu importe la largeur)
		decalAngle = 0
		if tailleImgConvert[1] > tailleImgSourcePlusFreq[1]:
			decalAngle = pi
		# Le bout de la flèche n'est pas affiché quand il n'y a pas la place
		# De plus cela évite évite d'avoir une erreur de division par zéro
		if tailleLigneFleche >= 15:
			# Angle servant à tracer les bouts de flèches (dans les coordonnées polaires)
			angleFleche = decalAngle + atan(float(tailleImgConvert[0] - tailleImgSourcePlusFreq[0]) /\
							(tailleImgConvert[1] - tailleImgSourcePlusFreq[1]))
			# Angle entre la direction de la flèche et ses bouts (en valeur absolue)
			angleBoutFleche = pi / 6
			angle1, angle2 = angleFleche - pi / 6, angleFleche + pi / 6
			# Taille des bouts de la flèche
			tailleBoutFleche = 10
			# On place le bout de la flèche au coin inférieur droit de l'image convertie
			paint.translate(tailleImgConvert[0],tailleImgConvert[1])
			# Utilisation des coordonnées polaires
			paint.drawLine(0, 0, sin(angle1) * tailleBoutFleche, cos(angle1) * tailleBoutFleche)
			paint.drawLine(0, 0, sin(angle2) * tailleBoutFleche, cos(angle2) * tailleBoutFleche)
	
		paint.end()
		self.dessinApercu = 1


class Image_Divers_Redimensionner(QWidget):
	"""# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Redimensionner
	# -----------------------------------"""
	def __init__(self, statusBar, geometry):

        	QWidget.__init__(self)
		
		# ----------------------------
		# Quelques paramètres de base
		# ----------------------------
		
		#=== Création des répertoires temporaires ===#
		# Gestion du repertoire tmp avec EkdConfig 
		self.repTampon = EkdConfig.getTempDir() + os.sep + "tampon" + os.sep + "image_divers_redimensionner" + os.sep


		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)
		if os.path.isdir(self.repTampon+'redim'+os.sep) is False:
        		os.makedirs(self.repTampon+'redim'+os.sep)	
		# Si le répertoire /tmp/ekd/tampon/image_divers_redimensionner/redim
		# n'est pas vide, il est expressément vidé de tout son contenu
		tempr=glob.glob(self.repTampon+'redim'+os.sep+'*.*')
		if len(tempr)>0:
			for parc in tempr: os.remove(parc)
		
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
		
		# Identifiant des filtres utilisant partiellement ou intégralement un module python durant 
		# la conversion
		self.filtresPython=['redim_avec_ratio', 'redim_sans_ratio']
		
		self.timer = QTimer()
		self.connect(self.timer, SIGNAL('timeout()'), self.sonderTempsActuel)
		
		self.process = QProcess()
		self.connect(self.process, SIGNAL('finished(int)'), self.finConversion)
		
		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()

		# Gestion de la configuration via EkdConfig

		# Paramètres de configuration
		self.config = EkdConfig
		# Identifiant du cadre
		self.idSection = "image_redimensionner"
		# Log du terminal
		self.base.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		self.listeImgSource = []
		self.listeImgDestin = []
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# ----------------------------------------
		# Bouton de sélection des images sources
		# ----------------------------------------
		
		self.tabwidget=QTabWidget()
		# Rq: le signal est placé à la fin de __init__ à cause d'une bizarrerie sous qt4.4
		
		#------------------
		# Onglet Réglages
		#------------------
		
		self.framReglage=QFrame()
		vboxReglage=QVBoxLayout(self.framReglage)
		
		# Gestion du nombre d'images à traiter
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel(_(u"Traitement à partir de l'image (numéro)")), 0, 0)
		self.spin1_ImTrait=SpinSlider(1, 100000, 1, '', self)
		self.grid.addWidget(self.spin1_ImTrait, 0, 1)
		self.connect(self.spin1_ImTrait, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		self.grid.addWidget(QLabel(_(u"Nombre de chiffres après le nom de l'image")), 1, 0)
		self.spin2_ImTrait=SpinSlider(3, 18, 6, '', self)
		self.grid.addWidget(self.spin2_ImTrait, 1, 1)
		self.connect(self.spin2_ImTrait, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		
		self.grid.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid)
		vboxReglage.addStretch()
		
		#=== Stacked ===#
		
		self.stacked = QStackedWidget()
		self.stacked.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
		
		#=== Instanciation des widgets du stacked  ===#
		
		# Widgets du stacked avec une seule boite de spin
		self.stacked_redim_avec_ratio = SpinSliders(self, 10,6000,640, _(u"nouvelle largeur"), 'largeur_ratio')
		
		# Widgets du stacked avec 2 boites de spin
		self.stacked_redim_sans_ratio = SpinSliders(self, 10,6000,640,_(u"nouvelle largeur"),'largeur_sans_ratio',
					10,6000,480, _(u"nouvelle hauteur"), 'longueur_sans_ratio')
		
		# Ajout des widgets aux stacked
		indexStacked_redim_avec_ratio = self.stacked.addWidget(self.stacked_redim_avec_ratio)
		indexStacked_redim_sans_ratio = self.stacked.addWidget(self.stacked_redim_sans_ratio)
		
		#=== Autres widgets de l'onglet réglagle ===#
		
		#---- boite de combo
		self.comboReglage=QComboBox()
		# Paramètres de la liste de combo: [(nom entrée, identifiant, index du stacked,
		# instance stacked),...]
		self.listeComboReglage=[\
			(_(u'Redimensionner en tenant compte des proportions'), 'redim_avec_ratio',
				indexStacked_redim_avec_ratio, self.stacked_redim_avec_ratio),
			(_(u'Redimensionner sans tenir compte des proportions'), 'redim_sans_ratio',
				indexStacked_redim_sans_ratio, self.stacked_redim_sans_ratio)]
		
		# Insertion des codecs de compression dans la boite de combo
		for i in self.listeComboReglage:
                	self.comboReglage.addItem(i[0], QVariant(i[1]))
		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		self.base.valeurComboIni(self.comboReglage, self.config, self.idSection, 'methode')
		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"),
				self.changerApercu)
		
		#---- Pseudo-aperçu de la redimension
		self.apercu = Apercu((400, 300), statusBar)
		
		self.connect(self.stacked_redim_avec_ratio.spin, SIGNAL("valueChanged(int)"),
				self.changerApercu)
		self.connect(self.stacked_redim_sans_ratio.spin1, SIGNAL("valueChanged(int)"),
				self.changerApercu)
		self.connect(self.stacked_redim_sans_ratio.spin2, SIGNAL("valueChanged(int)"),
				self.changerApercu)
		# On donne les valeurs de largeur et hauteur des images converties à l'aperçu
		self.changerApercu()
		
		# Légende de l'aperçu
		coulSource, coulConvert = self.apercu.couleurContourSourceConvert()
		self.legendeSource = ElementLegende(": " +\
			_(u"Contours des images sources (taille la plus fréquente en foncé)"), coulSource)
		self.legendeConvert = ElementLegende(": "+ _(u"Contours des images à convertir"), coulConvert)
		self.legendeSource.hide()
		self.legendeConvert.hide()
		
		#=== Mise-en-page ===#
		
		hbox = QHBoxLayout()
		hbox.addWidget(QLabel(_(u'Type')))
		hbox.addWidget(self.comboReglage)
		hbox.setAlignment(Qt.AlignHCenter)
		
		vboxReglage.addLayout(hbox)
		vboxReglage.addWidget(self.stacked)
		hboxApercu = QHBoxLayout()
		hboxApercu.addStretch()
		hboxApercu.addWidget(self.apercu)
		hboxApercu.addStretch()
		vboxReglage.addLayout(hboxApercu)
		vboxReglage.addWidget(self.legendeSource)
		vboxReglage.addWidget(self.legendeConvert)
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
		
		vbox.addWidget(self.tabwidget)

		self.indexTabImgSource = self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		self.indexTabReglage=self.tabwidget.addTab(self.framReglage, _(u'Réglages'))
		self.indexTabImgDestin = self.tabwidget.addTab(self.afficheurImgDestination, _(u'Image(s) après traitement'))
		self.indexTabInfo=self.tabwidget.addTab(self.framInfos, _(u'Infos'))
		
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
		# Bouton inactif au départ
		self.boutApPremImg.setEnabled(False)
		self.connect(self.boutApPremImg, SIGNAL("clicked()"), self.visu_1ere_derniere_img)
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
		
		#-----------------------------
		# Barre de progression
		#-----------------------------
		
		self.progress=QProgressDialog(_(u"Conversion en cours..."), _(u"Arrêter"), 0, 100)
		self.progress.setWindowTitle(_(u'EnKoDeur-Mixeur. Fenêtre de progression'))
		self.progress.setMinimumWidth(500)
		self.progress.setMinimumHeight(100)
		self.connect(self.progress, SIGNAL("canceled()"), self.arretProgression)
		
		# affichage de la boîte principale
		self.setLayout(vbox)

		self.connect(self.tabwidget, SIGNAL("currentChanged(int)"), self.fctTab)

		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
		#----------------------------------------------------------------------------------------------------
		
		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifImgSource)
		
		
	def changeValNbreImg_1(self):
		"""gestion du nombre d'images à traiter"""
		#print "Traitement a partir de l'image (numero):", self.spin1_ImTrait.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1_ImTrait.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2_ImTrait.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2_ImTrait.value())


	def modifImgSource(self, i):
		"""On active ou désactive les boutons d'action et on recharge le pseudo-aperçu de planche-contact
		en fonction du nombre d'images présentes dans le widget de sélection"""
		self.boutAppliquer.setEnabled(i)
		self.boutApPremImg.setEnabled(i)
		self.modifImageSource = 1
		if i :
			# Redessinage du canevas de peudo-aperçu
			self.stat_dim_img()
			liste = [i[1] for i in self.lStatDimSeq]
			self.apercu.setImageTaillePlusFrequente(self.imageTaillePlusFrequente)
			self.apercu.setListeTailleImage(liste)
			# Affichage de la légende
			self.legendeSource.show()
			self.legendeConvert.show()

	
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
		
	
	def changerComboReglage(self, i):
		"""L'entrée sélectionnée de la boîte de combo modifie le QFrame de réglage du codec associée"""
		self.stacked.setCurrentIndex(self.listeComboReglage[i][2])
		self.config.set(self.idSection, 'methode', self.listeComboReglage[i][1])
	
	
	def logFinal(self, titreFiltre):
		"""Affichage des informations de conversion"""
		a='#'*36
		# On ne récupère pas l'ancien % car il est arrondi
		pourCent=round(float(len(self.listeImgDestin))/len(self.listeImgSource)*100)
		pourCent = "%.0f" %pourCent
		b = a + '\n# ' + _(u'Filtre utilisé: ') + titreFiltre + '\n' + a + '\n'
		c = _(u"nombre d'images converties / nombre d'images sources")+" = "+str(len(self.listeImgDestin))+" / "\
		+str(len(self.listeImgSource))+" = " + pourCent +" %\n\n"
		
		# Affichage information de la nouvelle résolution des images
		# Pour les commentaires voir dans la fonction appliquer
		if self.listeComboReglage[self.i][1]=='redim_avec_ratio':
			spin=self.listeComboReglage[self.i][3].spin.value() # nouvelle largeur
			obImg=Image.open(self.listeImgSource[0])
			w, h=obImg.size
			ratio=float(w)/float(h)
			calcHaut=float(spin)/ratio
			d = a+'\n# '+_(u"Nouvelle résolution image(s): ")+'\n'+a+'\n'+str(spin)+' x '+str(int(calcHaut))
			
		elif self.listeComboReglage[self.i][1]=='redim_sans_ratio':
			spin1=self.listeComboReglage[self.i][3].spin1.value() # nouvelle largeur
			spin2=self.listeComboReglage[self.i][3].spin2.value() # nouvelle hauteur
			obImg=Image.open(self.listeImgSource[0])
			d=a+'\n# '+_(u"Nouvelle résolution image(s): ")+'\n'+a+'\n'+str(spin1)+' x '+str(spin2)
		
		# Le dernier '\n' est parfois nécessaire pour voir la dernière ligne!
		self.zoneAffichInfosImg.setText(b+c+self.infosImgTitre[0]+\
		"\n".join(self.listeImgSource)+'\n\n'+self.infosImgTitre[1]+"\n".join(self.listeImgDestin)+'\n\n'+d+'\n')
	

	def changerApercu(self, i=None):
		"Modification de l'aperçu quand une valeur de la nouvelle largeur ou hauteur est donnée"
		
		index = self.comboReglage.currentIndex()
		if self.comboReglage.itemData(index).toString() == "redim_sans_ratio":
			largeur = self.stacked_redim_sans_ratio.spin1.value()
			hauteur = self.stacked_redim_sans_ratio.spin2.value()
		elif self.comboReglage.itemData(index).toString() == "redim_avec_ratio":
			largeur = self.stacked_redim_avec_ratio.spin.value()
			hauteur = None
		
		self.apercu.setSizeConvertImages(largeur, hauteur)
	
	
	def stat_dim_img(self):
		"""Calcul statistique des dimensions des images les plus présentes dans le lot
		et récupération de l'adresse d'une image de la taille la plus fréquente du lot"""

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
		
		# On récupère l'adresse d'une image de la taille la plus fréquente du lot
		for index, taille in enumerate(listePrepaRedim):
			if taille == self.lStatDimSeq[0][1]:
				self.imageTaillePlusFrequente = self.listeImgSource[index]
				break
		
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

	
	def arretProgression(self):
		"""Si le filtre appliqué est 100 % shell, alors la conversion est immédiatement stoppée après un clic sur le bouton de la QProgessDialog. Pas la peine d'attendre la fin de la conversion de l'image en cours comme pour les autres types de filtres."""
		
		if self.listeComboReglage[self.i][1] in self.filtresPython: return
		self.process.kill()
		if len(self.listeImgDestin)!=0:
			self.conversionImg = 1
			self.logFinal(self.listeComboReglage[self.i][0])
			self.tabwidget.setCurrentIndex(self.indexTabInfo)
		else: # Onglet de log -> on remet les infos de départ
			self.zoneAffichInfosImg.setText(self.infosImgTitre[0]+"\n".join(self.listeImgSource))
	
	
	def finConversion(self, statutDeSortie):
		"""Choses à faire à la fin de l'encodage d'une image quand le filtre sélectionné est constitué d'une seule commande shell"""
		
		if statutDeSortie==1:
			#print "Problème lors de la conversion!"
			EkdPrint(u"Problème lors de la conversion !")
			messageAide=QMessageBox(self)
			messageAide.setText(_(u"Une erreur s'est produite durant la conversion"))
			messageAide.setWindowTitle(_(u"Aide"))
			messageAide.setIcon(QMessageBox.Warning)
			messageAide.exec_()
			self.logFinal(self.listeComboReglage[self.i][0])
			self.tabwidget.setCurrentIndex(self.indexTabInfo)
			return
		
		# On passe à l'image suivante s'il en reste
		elif self.opReccurApresApp():
			self.appliquer()
	
	
	def opReccurApresApp(self):
		"""Opérations à effectuer après chaque appel du moteur."""
		
		if self.listeComboReglage[self.i][1] in self.filtresPython:
			modulePython = 1 # conversion python (+ shell pour certains filtres)
		
		self.listeImgDestin.append(self.cheminCourantSauv)
		pourCent=int((float(self.j+1)/self.nbrImg)*100)
		
		self.progress.setValue(pourCent)
		#!!!Rafraichissement indispensable pour la transmission immédiate du signal QProgressDialog().wasCanceled
		if modulePython: QApplication.processEvents()
		
		# Opérations de fin de conversion
		if pourCent==100:
			# Condition à respecter pour qu'un affichage d'une nouvelle image ait lieu dans l'onglet "Images après traitement"
			self.conversionImg = 1
			# Boite de dialogue d'information
			messageAide=QMessageBox(self)
			messageAide.setText(_(u"Le traitement a été appliqué avec succès!"))
			messageAide.setWindowTitle(self.listeComboReglage[self.i][0])
			messageAide.setIcon(QMessageBox.Information)
			messageAide.exec_()
			# Mise-à-jour du log
			self.logFinal(self.listeComboReglage[self.i][0])
			# Changement d'onglet et fonctions associées
			self.metaFctTab(self.indexTabImgDestin)
			return 0
		
		# Opérations à faire lors de l'arrêt de la conversion suite au clic sur le bouton annuler de la barre de progression
		elif self.progress.wasCanceled():
			if modulePython:
				# Condition à respecter pour qu'un affichage d'une nouvelle image ait lieu dans l'onglet "Images après traitement"
				self.conversionImg = 1
				# Mise-à-jour du log
				self.logFinal(self.listeComboReglage[self.i][0])
				# Affichage de l'onglet d'infos
				self.tabwidget.setCurrentIndex(self.indexTabInfo)
			return 0
		
		return 1
	
	
	def sonderTempsActuel(self):
		"""x ms après l'apparition de la boite de dialogue, on lance la conversion. But: faire en sorte que la boite de dialogue ait le temps de s'afficher correctement"""
		self.timer.stop()
		self.appliquer()
	
	
	def appliquer0(self):
		"""Préparation de la conversion"""
		
		# Redimensionner les images de tailles différentes?
		self.redim_img()

		# Récupération de la liste des fichiers chargés
		self.listeChemin=self.afficheurImgSource.getFiles()
		
		# Utilisation de la nouvelle boîte de dialogue de sauvegarde
		suffix=""
                self.cheminSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.cheminSauv = self.cheminSauv.getFile()
		
		if not self.cheminSauv: return
		
		#print 'Chemin+nom de sauvegarde:', self.cheminSauv

		# Extension/format des images
		self.ext = os.path.splitext(self.listeChemin[0])[1]
		
		# Liste des indices des images [0,1,2,...,nombre d'images-1]
		self.listeIndex = range(len(self.listeChemin))
		
		# Nombre d'images sources
		self.nbrImg = len(self.listeChemin)
		
		# Récupération de l'identifiant du codec
		self.i = self.comboReglage.currentIndex()
		
		# Indice de l'image à convertir
		self.j = 0
		
		self.progress.reset() # wasCanceled est remis à 0 -> la conversion ne s'arrête pas à la 1ère img
		self.progress.show()
		self.progress.setValue(0)
		QApplication.processEvents()
		
		# Lancement de la conversion dans 250 ms
		self.timer.start(250)
		
		
	def visu_1ere_derniere_img(self):
		"""Conversion des images"""
		
		# Récupération de l'identifiant du codec
		i = self.comboReglage.currentIndex()
		
		# Récupération du fichier sélectionné par l'utilisateur (si pas de fichier
		# sélectionné par l'utilisateur, la 1ère image de la liste est prise)
		file = self.afficheurImgSource.getFile()
		if not file: return
		self.listeChemin = [file]
		
		if self.listeComboReglage[i][1]=='redim_avec_ratio':
			""" Redimensionnement des images avec ratio """

			# Récup réglage ci-dessous
			spin = self.listeComboReglage[i][3].spin.value() # nouvelle largeur
				
			# Chemin de sauvegarde
			self.cheminCourantSauv = self.repTampon+'image_visu_redim_'+string.zfill(1, 6)+'.jpg'
				
			# Ouverture des images. Conversion et sauvegarde
			obImg = Image.open(self.listeChemin[0])
			
			# Recup dimensions de l'image
			w, h = obImg.size
			# Calcul du ratio de chaque image chargee
			ratio=float(w)/float(h)
			# Calcul de future hauteur avec les dimensions donnees par l'utilisateur
			calcHaut=float(spin)/ratio
			# Redimensionnement et sauvegarde des images
			finRedimSansRatio=obImg.resize((int(spin), int(calcHaut)), Image.ANTIALIAS).save(self.cheminCourantSauv)
			
			# Affichage de l'image temporaire 
			# Ouverture d'une boite de dialogue affichant l'aperçu.
			#
			# Affichage par le bouton Voir le résultat
			visio = VisionneurEvolue(self.cheminCourantSauv)
			visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
			visio.exec_()
		
			return 0
			
		elif self.listeComboReglage[i][1]=='redim_sans_ratio':
			""" Redimensionnement des images sans ratio """

			# Récup réglages ci-dessous
			spin1 = self.listeComboReglage[i][3].spin1.value() # nouvelle largeur
			spin2 = self.listeComboReglage[i][3].spin2.value() # nouvelle hauteur
				
			# Chemin de sauvegarde
			self.cheminCourantSauv = self.repTampon+'image_visu_redim_'+string.zfill(1, 6)+'.jpg'
				
			# Ouverture des images. Conversion et sauvegarde
			obImg = Image.open(self.listeChemin[0])
			
			# Redimensionnement et sauvegarde des images
			finRedimSansRatio=obImg.resize((int(spin1), int(spin2)), Image.ANTIALIAS).save(self.cheminCourantSauv)
			
			# Affichage de l'image temporaire 
			# Ouverture d'une boite de dialogue affichant l'aperçu.
			#
			# Affichage par le bouton Voir le résultat
			visio = VisionneurEvolue(self.cheminCourantSauv)
			visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
			visio.exec_()
		
			return 0
		
	
	def appliquer(self):
		"""Conversion des images"""
		
		# La liste pour l'affichage des images ds l'interface est
		# vidée pour que les images affichées ne s'amoncellent pas
		# si plusieurs rendus à la suite
		self.listeImgDestin=[]

		#print "Indice de l'image à encoder :", self.j
		EkdPrint(u"Indice de l'image à encoder: %s" % self.j)
		
		if self.listeComboReglage[self.i][1]=='redim_avec_ratio':
			""" Redimensionnement des images avec ratio """
			for self.j in self.listeIndex:
				# Récup réglage ci-dessous
				spin = self.listeComboReglage[self.i][3].spin.value() # nouvelle largeur
				
				# Chemin de sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill(self.j+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+self.ext
				
				# Ouverture des images. Conversion et sauvegarde
				obImg = Image.open(self.listeImgSource[self.j])
				# Recup dimensions de l'image
				w, h = obImg.size
				# Calcul du ratio de chaque image chargee
				ratio=float(w)/float(h)
				# Calcul de future hauteur avec les dimensions donnees par l'utilisateur
				calcHaut=float(spin)/ratio
				# Redimensionnement et sauvegarde des images
				finRedimSansRatio=obImg.resize((int(spin), int(calcHaut))).save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return
				
		elif self.listeComboReglage[self.i][1]=='redim_sans_ratio':
			""" Redimensionnement des images sans ratio """
			for self.j in self.listeIndex:
				# Récup réglages ci-dessous
				spin1 = self.listeComboReglage[self.i][3].spin1.value() # nouvelle largeur
				spin2 = self.listeComboReglage[self.i][3].spin2.value() # nouvelle hauteur
				
				# Chemin de sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill(self.j+self.spin1_ImTrait.value(), self.spin2_ImTrait.value())+self.ext
				
				# Ouverture des images. Conversion et sauvegarde en niveaux de gris
				obImg = Image.open(self.listeImgSource[self.j])
				# Redimensionnement et sauvegarde des images
				finRedimSansRatio=obImg.resize((int(spin1), int(spin2))).save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return
				
		# Affichage des images après traitement
		#
		# Changement d'onglet et fonctions associées
		self.conversionImg = 1
		self.metaFctTab(self.indexTabImgDestin)
			
			
	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""
		
		# Nouvelle fenêtre d'aide
		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<p><b>Vous pouvez ici changer la résolution (c'est à dire la taille, plus précisément la largeur et la hauteur) des images.</b></p><p><b>Dans l'onglet 'Réglages' il est possible de redimensionner les images en tenant compte du ratio, c'est à dire des proportions de chaque image (là on ne donne que la largeur, EKD se changeant de calculer la hauteur ; cela permet de ne pas déformer les images lors du changement de résolution), mais aussi de définir soi-même la taille de chaque image (en changeant à la fois la largeur et la hauteur).</b></p><p>Dans l'onglet <b>'Image(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Dans l'onglet <b>'Réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b>, ensuite sélectionnez votre <b>'Type'</b> (<b>Redimensionner en tenant compte des proportions</b> ou <b>Redimensionner sans tenir compte des proportions</b>), faites les réglages par rapport au <b>'Type'</b> choisi (vous pouvez voir en temps réel la taille de la première image du lot changer à mesure que vous réglez la <b>nouvelle largeur</b> et/ou la <b>nouvelle hauteur</b>).</p><p>En complément, vous pouvez cliquer sur le bouton <b>'Voir le résultat'</b>, vous voyez à ce moment là le résultat de vos réglages s'afficher dans une nouvelle fenêtre (particulièrement utile pour voir les déformations dues au redimensionnement pour <b>Redimensionner sans tenir compte des proportions</b>).</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer et sauver'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>'Images après traitement'</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>'Infos'</b> vous permet de voir les image(s) chargée(s), les image(s) convertie(s) et la nouvelle résolution des images.</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'spin1_ImTrait', unicode(self.spin1_ImTrait.value()))
		EkdConfig.set(self.idSection, u'spin2_ImTrait', unicode(self.spin2_ImTrait.value()))
		EkdConfig.set(self.idSection, u'stacked_redim_avec_ratio', unicode(self.stacked_redim_avec_ratio.spin.value()))
		EkdConfig.set(self.idSection, u'stacked_redim_sans_ratio1', unicode(self.stacked_redim_sans_ratio.spin.value()))
		EkdConfig.set(self.idSection, u'stacked_redim_sans_ratio2', unicode(self.stacked_redim_sans_ratio.spin2.value()))
		EkdConfig.set(self.idSection, u'type_redim', unicode(self.comboReglage.currentIndex()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.spin1_ImTrait.setValue(int(EkdConfig.get(self.idSection, 'spin1_ImTrait')))
		self.spin2_ImTrait.setValue(int(EkdConfig.get(self.idSection, 'spin2_ImTrait')))
		self.stacked_redim_avec_ratio.spin.setValue(int(EkdConfig.get(self.idSection, 'stacked_redim_avec_ratio')))	
		self.stacked_redim_sans_ratio.spin.setValue(int(EkdConfig.get(self.idSection, 'stacked_redim_sans_ratio1')))	
		self.stacked_redim_sans_ratio.spin2.setValue(int(EkdConfig.get(self.idSection, 'stacked_redim_sans_ratio2')))	
		self.comboReglage.setCurrentIndex(int(EkdConfig.get(self.idSection, 'type_redim')))
