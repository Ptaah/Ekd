#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, glob, string, shutil, Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw
from random import randrange
from numpy import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Module SpinSliders20Possibles rajouté le 16/07/10
from gui_modules_image.image_base import Base, SpinSlider, SpinSliders, SpinSliders20Possibles 
from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue

# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Nouvelle fenêtre d'aide
from gui_modules_common.EkdWidgets import EkdAide
# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

from moteur_modules_common.EkdProcess import EkdProcess

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class FiltresAvec9Spin(QFrame):
	"""Widget de réglage à 9 boites de spin"""
	def __init__(self, txt1='', txt2=None, parent=None):
        	QFrame.__init__(self)

		grid = QGridLayout(self)
		self.vColor = []
		self.spin = [[0]*3,[0]*3,[0]*3]
		for k in range(3):
			x = QLineEdit()
			x.setMinimumHeight(25)
			self.vColor.append(x)
			grid.addWidget(self.vColor[k], 1, k+1)
			for l in range(3):
				self.spin[k][l]=SpinSlider(0, 99, 50, 'couleur_'+str(k+1)+str(l+1), parent)
				self.connect(self.spin[k][l], SIGNAL("valueChanged(int)"), self.updateColor)
				grid.addWidget(self.spin[k][l], k+2, l+1)
		self.updateColor(50)
		grid.addWidget(QLabel(_(u"Couleur n°1")), 0, 1)
		grid.addWidget(QLabel(_(u"Couleur n°2")), 0, 2)
		grid.addWidget(QLabel(_(u"Couleur n°3")), 0, 3)
		grid.addWidget(QLabel(_(u"Rouge")), 2, 0)
		grid.addWidget(QLabel(_(u"Vert")), 3, 0)
		grid.addWidget(QLabel(_(u"Bleu")), 4, 0)
		grid.setAlignment(Qt.AlignCenter)

	def updateColor(self, val) :
		for i in range(3) :
			bckcol=QPalette()
			bckcol.setColor(QPalette.Base,QColor(int(self.spin[0][i].value()*2.55),int(self.spin[1][i].value()*2.55),int(self.spin[2][i].value()*2.55)))
			#self.vColor[i].setBackgroundRole(QPalette.Base)
			self.vColor[i].setPalette(bckcol)


class FiltresAvec13Spin(QFrame):
	"""Widget de réglage à 13 boites de spin"""
	def __init__(self, txt1='', txt2=None, parent=None):
        	QFrame.__init__(self)

		grid = QGridLayout(self)
		grid.addWidget(QLabel(_(u"Intensite du trait")), 0, 0)
		self.spinTrait = SpinSlider(10,40, 25, 'coul_contour_couleur_00', parent=parent)
		grid.addWidget(self.spinTrait, 0, 1, 1, -1)
		grid.addWidget(QLabel(_(u"Couleur du trait de contour")), 1, 0)
		# Ajout de self.spinTrait à la fin de la liste self.spin pour une meilleure
		# récupération de la valeur de l'intensité du trait dans les fonctions
		# visu_1ere_img et appliquerContourEtCouleur
		self.spin = [[0]*3,[0]*3,[0]*3,[0]*3,self.spinTrait]
		self.vColor = []
		colorTrait = QLineEdit()
		grid.addWidget(colorTrait, 1, 1, 1, -1)
		grid.addWidget(QLabel(_(u"Rouge")), 2, 0)
		grid.addWidget(QLabel(_(u"Vert")), 3, 0)
		grid.addWidget(QLabel(_(u"Bleu")), 4, 0)
		grid.addWidget(QLabel(_(u"Transparence")), 5, 0)

		for p in range(4) :
			if p == 3 : coul = 255
			else : coul = 20
			self.spin[p][2]=SpinSlider(0, 255, coul, 'coul_contour_couleur_'+str(p+1)+'3', parent=parent)
			self.connect(self.spin[p][2], SIGNAL("valueChanged(int)"), self.updateColor)
			grid.addWidget(self.spin[p][2], p+2, 1, 1, -1)

		for z in range(2) :
			x = QLineEdit()
			x.setMinimumHeight(25)
			self.vColor.append(x)
			grid.addWidget(self.vColor[z], 7, z+1)

		self.vColor.append(colorTrait)

		for k1 in range(4):			
			for l1 in range(2):
				incrementation=str(k1)+'_'+str(l1)
				# -- Orange avec canal alpha opaque --
				if incrementation=='0_0': coul=92
				elif incrementation=='1_0': coul=125
				elif incrementation=='2_0': coul=188
				elif incrementation=='3_0': coul=255
				# -- Bleu avec canal alpha opaque ----
				elif incrementation=='0_1': coul=201
				elif incrementation=='1_1': coul=157
				elif incrementation=='2_1': coul=205
				elif incrementation=='3_1': coul=255
				self.spin[k1][l1]=SpinSlider(0, 255, coul, 'coul_contour_couleur_'+str(k1+1)+str(l1+1), parent)
				self.connect(self.spin[k1][l1], SIGNAL("valueChanged(int)"), self.updateColor)
				grid.addWidget(self.spin[k1][l1], k1+8, l1+1)
		

		self.updateColor(1)
		grid.addWidget(QLabel(_(u"Couleur pour l'ombre")), 6, 1)
		grid.addWidget(QLabel(_(u"Couleur pour la lumière")), 6, 2)
		grid.addWidget(QLabel(_(u"Rouge")), 8, 0)
		grid.addWidget(QLabel(_(u"Vert")), 9, 0)
		grid.addWidget(QLabel(_(u"Bleu")), 10, 0)
		grid.addWidget(QLabel(_(u"Transparence")), 11, 0)
		grid.setAlignment(Qt.AlignCenter)

	def updateColor(self, val) :
		for i in range(3) :
			bckcol=QPalette()
			bckcol.setColor(QPalette.Base,QColor(self.spin[0][i].value(),self.spin[1][i].value(),self.spin[2][i].value(),self.spin[3][i].value()))
			self.vColor[i].setPalette(bckcol)


class FiltresAvec8Spin(QFrame):
	"""Widget de réglage à 6 boites de spin"""
	def __init__(self, txt1='', txt2=None, parent=None):
        	QFrame.__init__(self)

		grid = QGridLayout(self)
		self.spin = [[0]*2,[0]*2,[0]*2,[0]*2]
		self.vColor = []
		for z in range(2) :
			x = QLineEdit()
			x.setMinimumHeight(25)
			self.vColor.append(x)
			grid.addWidget(self.vColor[z], 1, z+1)

		for k1 in range(4):			
			for l1 in range(2):
				incrementation=str(k1)+'_'+str(l1)
				# -- Orange avec canal alpha opaque --
				if incrementation=='0_0': coul=253
				elif incrementation=='1_0': coul=145
				elif incrementation=='2_0': coul=5
				elif incrementation=='3_0': coul=255
				# -- Bleu avec canal alpha opaque ----
				elif incrementation=='0_1': coul=35
				elif incrementation=='1_1': coul=85
				elif incrementation=='2_1': coul=136
				elif incrementation=='3_1': coul=255
				self.spin[k1][l1]=SpinSlider(0, 255, coul, 'coul_omb_lum_a_la_coul_'+str(k1+1)+str(l1+1), parent)
				self.connect(self.spin[k1][l1], SIGNAL("valueChanged(int)"), self.updateColor)
				grid.addWidget(self.spin[k1][l1], k1+2, l1+1)

		self.updateColor(1)
		grid.addWidget(QLabel(_(u"Couleur pour l'ombre")), 0, 1)
		grid.addWidget(QLabel(_(u"Couleur pour la lumière")), 0, 2)
		grid.addWidget(QLabel(_(u"Rouge")), 2, 0)
		grid.addWidget(QLabel(_(u"Vert")), 3, 0)
		grid.addWidget(QLabel(_(u"Bleu")), 4, 0)
		grid.addWidget(QLabel(_(u"Transparence")), 5, 0)
		grid.setAlignment(Qt.AlignCenter)

	def updateColor(self, val) :
		for i in range(2) :
			bckcol=QPalette()
			bckcol.setColor(QPalette.Base,QColor(self.spin[0][i].value(),self.spin[1][i].value(),self.spin[2][i].value(),self.spin[3][i].value()))
			self.vColor[i].setPalette(bckcol)


class FiltresAvecCombo(QFrame):
	"""Widget de réglage contenant une boite de combo"""
	def __init__(self, txt, liste, identifiant, parent):
        	QFrame.__init__(self)

		self.parent = parent
		self.identifiant = identifiant

		hbox = QHBoxLayout(self)
		hbox.addWidget(QLabel(txt))
		self.combo = QComboBox()

		font =QFont()
		fm = QFontMetricsF(font)
		hauteurIcone = fm.height() - 2 # icones espacées de 2 pixels

		for i in liste:
			if len(i)!=3: self.combo.addItem(i[0],QVariant(i[1]))
			else:
				pixmap = QPixmap(hauteurIcone, hauteurIcone)
				color = QColor(i[2][0],i[2][1],i[2][2])
				pixmap.fill(color)
				self.combo.addItem(QIcon(pixmap),i[0],QVariant(i[1]))
		self.connect(self.combo, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		parent.base.valeurComboIni(self.combo, parent.config, parent.idSection, identifiant)
		hbox.addWidget(self.combo)
		hbox.setAlignment(Qt.AlignCenter)

	def changerComboReglage(self, i):
		self.parent.config.set(self.parent.idSection, self.identifiant,self.combo.itemData(i).toString())


class Image_FiltresImage(QWidget):
	"""# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Filtres image
	# -----------------------------------"""
	def __init__(self, statusBar, geometry):

        	QWidget.__init__(self)

		# ----------------------------
		# Quelques paramètres de base
		# ----------------------------

		# Gestion de la configuration via EkdConfig
		self.config=EkdConfig
		# Identifiant du cadre
		self.idSection = "image_filtres_image"
		self.base = Base()
		# Log du terminal
		self.base.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry
		
		#== Sélection du répertoire annexe --> là où se trouve ce script de gestion ==#
		#== des filtres image, c'est à dire: image_filtres_image.py (pour certains  ==#
		#== filtres de G'MIC)                                                       ==#
		#
		# Uniquement pour Linux et MacOSX
		if os.name in ['posix', 'mac']:
                        # Répertoire courant
                        rep_cour = os.getcwd()
			# Chemin exact du répertoire annexe
			self.rep_annexe = rep_cour + os.sep + "gui_modules_image" + os.sep + "filtres_images" + os.sep + "annexe" + os.sep

		#=== Création des répertoires temporaires ===#
		# Gestion du repertoire tmp avec EkdConfig
		self.repTampon = EkdConfig.getTempDir() + os.sep + 'tampon' + os.sep + 'image_filtres_image' + os.sep

		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)
		if os.path.isdir(self.repTampon+'redim' + os.sep) is False:
        		os.makedirs(self.repTampon+'redim' + os.sep)

		# Scan du répertoire tampon /tmp/ekd/tampon/image_filtres_image
		listeRepTemp=glob.glob(self.repTampon+'*.*')

		# Epuration/elimination des fichiers tampon contenus
		# dans /tmp/ekd/tampon/image_filtres_image
		if len(listeRepTemp)>0:
			for toutRepTempE in listeRepTemp:
				os.remove(toutRepTempE)

		# Scan du répertoire tampon /tmp/ekd/tampon/conv_img_en_video/redim
		listeRepTempRedim=glob.glob(self.repTampon+'redim' + os.sep + '*.*')

		# Epuration/elimination des fichiers tampon contenus
		# dans /tmp/ekd/tampon/conv_img_en_video/redim
		if len(listeRepTempRedim)>0:
			for toutRepTempE_Redim in listeRepTempRedim:
				os.remove(toutRepTempE_Redim)

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
		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0

		# Identifiant des filtres utilisant partiellement ou intégralement un module python durant la conversion
		self.filtresPython=['illustration_niveau_gris','traits_fins_et_couleur','emboss','sharpen','niveau_gris','couleurs_personnalisees','vieux_films','couleurs_predefinies', 'amelior_des_bords', 'debruitage', 'seuillage', 'evanescence', 'imitation_bd_1', 'negatif', 'encadre_photo', 'separ_en_modules', 'omb_lum_a_la_coul', 'rotation_image', 'imitation_bd_2', 'laplacien_1', 'contour_et_couleur', 'peintur_degrade_de_coul']

		# Fonctions communes à plusieurs cadres du module Image
		# Paramètres de configuration
		self.listeImgSource = []
		self.listeImgDestin = []

		self.process = QProcess()
		self.connect(self.process, SIGNAL('finished(int)'), self.finConversion)

		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)

		self.tabwidget=QTabWidget()

		#------------------
		# Onglet Réglages
		#------------------

		self.framReglage=QFrame()
		vboxReglage=QVBoxLayout(self.framReglage)

		#=== Stacked ===#

		self.stacked = QStackedWidget()
		self.stacked.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))

		#=== Instanciation des widgets du stacked  ===#

		# Widgets du stacked sans réglage
		stacked_sansReglage = QFrame()
		vboxStacked = QVBoxLayout(stacked_sansReglage)
		txt=_(u"Pas de réglages ici")
		vboxStacked.addWidget(QLabel("<center>%s</center>" %txt))

		# Widgets du stacked avec un combo
		liste = [	(_(u"Impulse"),		"impulse"),\
				(_(u"Laplacian"),	"laplacian"),\
				(_(u"Poisson"),		"poisson")]
		stacked_pointillisme = FiltresAvecCombo(_(u"Sélection des couleurs"), liste, 'pointillisme', self)
		liste = [	(_(u"Rouge vif"),		"rouge_vif",		(198,0,0)),\
				(_(u"Rouge primaire"),		"rouge_primaire",	(199,0,101)),\
				(_(u"Vert perroquet"),		"vert_perroquet",	(0,199,0)),\
				(_(u"Vert acide et clair"),	"vert_acide_clair",	(146,198,1)),\
				(_(u"Bleu roi"),		"bleu_roi",		(0,145,254)),\
				(_(u"Bleu indigo"),		"bleu_indigo",		(145,145,255)),\
				(_(u"Bleu turquoise"),		"bleu_turquoise",	(145,255,255)),\
				(_(u"Jaune or"),		"jaune_or",		(234,198,0)),\
				(_(u"Jaune orange"),		"jaune_orange",		(255,197,0)),\
				(_(u"Saumon"),			"saumon",		(234,163,145)),\
				(_(u"Marron très clair"),	"marron_tres_clair",	(205,158,116)),\
				(_(u"Terre argileuse"),		"terre argileuse",	(243,159,123)),\
				(_(u"Gris colore rouge"),	"gris_colore_rouge",	(220,162,161)),\
				(_(u"Gris colore vert"),	"gris_colore_vert",	(162,200,161)),\
				(_(u"Gris colore bleu"),	"gris_colore_bleu",	(161,162,206)),\
				(_(u"Gris colore jaune"),	"gris_colore_jaune",	(200,200,162))]
		stacked_couleursPredef = FiltresAvecCombo(_(u"Type"), liste, 'couleurs_predefinies', self)
		liste = [	(_(u"Fond blanc, lignes noires"),	"fond_blanc_lignes_noires"),\
				(_(u"Fond noir, lignes blanches"),	"fond_noir_lignes_blanches")]
		stacked_evanescence = FiltresAvecCombo(_(u"Fond, forme"), liste, 'evanescence', self)
		liste = [	(_(u"Négatif couleur"),	"negatif_couleur"),\
				(_(u"Négatif noir et blanc"),	"negatif_n_et_b")]
		stacked_negatif = FiltresAvecCombo(_(u"Type de négatif"), liste, 'negatif', self)
		liste = [       (_(u"90 degrés vers la gauche"), 'rot_img_90_gauche'),\
				(_(u"180 degrés vers la gauche"), 'rot_img_180_gauche'),\
				(_(u"270 degrés vers la gauche"), 'rot_img_270_gauche')]
		stacked_retournement_img = FiltresAvecCombo(_(u"Type de rotation"), liste, 'rotation_image', self)
		liste = [       (_(u"Noir et blanc"), 'laplacien_1_noir_et_blanc'),\
				(_(u"Couleur"), 'laplacien_1_couleur')]
		stacked_laplacien_1 = FiltresAvecCombo(_(u"Type"), liste, 'laplacien_1', self)
		# Mélange de Couleurs prédéfinies, Dessin 13: en couleur (donc géré par G'MIC) et 
		# Réduction du bruit (débruitage)
		liste = [	(_(u"Bleu roi"),		"bleu_roi",		(0,145,254)),\
				(_(u"Bleu indigo"),		"bleu_indigo",		(145,145,255)),\
				(_(u"Jaune or"),		"jaune_or",		(234,198,0)),\
				(_(u"Jaune orange"),		"jaune_orange",		(255,197,0)),\
				(_(u"Saumon"),			"saumon",		(234,163,145)),\
				(_(u"Marron très clair"),	"marron_tres_clair",	(205,158,116)),\
				(_(u"Terre argileuse"),		"terre argileuse",	(243,159,123))]
		stacked_PeintDegradDeCoul = FiltresAvecCombo(_(u"Type"), liste, 'peintur_degrade_de_coul', self)

		# Widgets du stacked avec un ou plusieurs combos et boite(s) de spin
		liste = [	(_(u"Noir"),		"noir"),\
				(_(u"Gris"),		"gris"),\
				(_(u"Blanc"),		"blanc"),\
				(_(u"Rouge"),	        "rouge"),\
				(_(u"Vert"),		"vert"),\
				(_(u"Bleu"),		"bleu"),\
				(_(u"Jaune"),		"jaune")]
		stacked_encadrePhoto = FiltresAvecCombo(_(u"Couleur du cadre"), liste, 'encadre_photo', self)

		# Widgets du stacked avec une seule boite de spin
		stacked_sepia = SpinSliders(self, 50,99,60,_(u"% de sepia"), 'sepia')
		stacked_traitsNoirs = SpinSliders(self, 1,70,1,_(u"valeur de charcoal"), 'charcoal_traits_noirs')
		stacked_peuCouleurs = SpinSliders(self, 30,90,40, _(u"valeur de edge"), 'edge')
		stacked_peintHuile = SpinSliders(self, 1,20,1, _(u"valeur de la peinture à l'huile"), 'peinture_huile')
		stacked_gamma = SpinSliders(self, 0,20,1, _(u"valeur de gamma"), 'gamma')
		stacked_fonceClair = SpinSliders(self, 1,400,100, _(u"1: Noir; 100: Normal; 400: Surexposé"), 'fonce_clair')
		stacked_peintEau = SpinSliders(self, 4,16,6, _(u"valeur de la liquidité"), 'liquidite')
		stacked_basRelief = SpinSliders(self, 1,16,1, _(u"Netteté du bas-relief"), 'bas_relief')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_dessin_13_coul = SpinSliders(self, 1,7000,1874, _(u"Amplitude"), 'dessin_13_amplitude')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_dessin_14_crayPapier_2 = SpinSliders(self, 1,50,3, _(u"Taille"), 'dessin_14_taille')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_erosion = SpinSliders(self, 1,100,5, _(u"Valeur d'érosion"), 'erosion')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_dilatation = SpinSliders(self, 1,100,5, _(u"Valeur de dilatation"), 'dilatation')
		# ----------------------------------------------------------------------

		# Widgets du stacked avec 2 boites de spin
		stacked_crayonPapier_1 = SpinSliders(self,
			1,70,1, _(u"valeur de charcoal"),'charcoal_crayon_1',
			1,10,1, _(u"valeur de spread"), 'spread_crayon_1')
		stacked_blur = SpinSliders(self,
			1,16,1, _(u"radius"), 'radius',
			1,16,1, _("sigma"), 'sigma')
		stacked_traitCoulFond = SpinSliders(self,
			1,20,1, _(u"précision du trait (1: Net; 20: Flou)"), 'precision_trait',
			1,20,1, _(u"largeur du trait (1 : Fin; 20 : Gras)"), 'largeur_trait')
		stacked_seuillage = SpinSliders(self,
			1,255,1, _(u"seuillage bas"), 'seuillage_bas',
			1,255,128, _(u"seuillage haut"), 'seuillage_haut')
		stacked_imitationBd_2 = SpinSliders(self,
			10,40,28, _(u"intensité du trait"), 'intensite_du_trait_bd_2',
			2,16,4, _(u"flou des couleurs"), 'flou_couleurs')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		########Rajout le 28/11/2010 par LUCAS Thomas et CABANA Antoine#########
		stacked_visionThermique = SpinSliders(self,
			1,255,1, _(u"Minimum de luminance"), 'vision_thermique_min',
			1,255,255, _(u"Maximum de luminance"), 'vision_thermique_max')
		########################################################################
		# ----------------------------------------------------------------------

		# Widgets du stacked avec 3 boites de spin
		stacked_imitationBd_1 = SpinSliders(self,
			10,40,28, _(u"intensité du trait"), 'intensite_du_trait_bd_1',
			1,4,2, _(u"réduction des couleurs"), 'reduction_couleur',
			1,8,6, _(u"contraste des couleurs"), 'contraste_couleur')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_cubismeAnalytique = SpinSliders(self, 
			1,1000,240, _(u"Itérations"), 'iterations_cubisme_analytique',
			1,100,8, _(u"Taille de bloc"), 'taille_bloc_cubisme_analytique',
			1,360,114, _(u"Angle"), 'angle_cubisme_analytique')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_correctionYeuxRouges = SpinSliders(self,
			1,100,80, _(u"Seuil des couleurs"), 'seuil_coul_correct_yeux_rouges',
			1,100,1, _(u"Lissage"), 'lissage_correct_yeux_rouges',
			1,100,1, _(u"Atténuation"), 'attenuation_correct_yeux_rouges')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_expressionnisme = SpinSliders(self,
			1,10,2, _(u"Abstraction"), 'abstraction_expressionnisme',
			1,500,180, _(u"Lissage"), 'lissage_expressionnisme',
			1,400,340, _(u"Couleur"), 'couleur_expressionnisme')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_vieille_photo = SpinSliders(self,
			1,10,4, _(u"Taille en largeur de l'ombre"), 'taill_larg_ombre_vieil_photo',
			1,10,4, _(u"Taille en hauteur de l'ombre"), 'taill_haut_ombre_vieil_photo',
			1,90,10, _(u"Rotation (en degrés) de la photo"), 'rot_photo_vieil_photo')
		# ----------------------------------------------------------------------

		# Widgets du stacked avec 20 boites de spin possibles (classe SpinSliders20Possibles de gui_modules_image.image_base)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_polaroid = SpinSliders20Possibles(self, 
			5,50,10, _(u"Taille de la bordure"), 'taill_bord_polaroid',
			1,10,4, _(u"Taille en largeur de l'ombre"), 'taill_larg_ombre_polaroid',
			1,10,4, _(u"Taille en hauteur de l'ombre"), 'taill_haut_ombre_polaroid',
			1,90,10, _(u"Rotation (en degrés) de la photo"), 'rot_photo_polaroid')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_oeilleton = SpinSliders20Possibles(self, 
			1,100,50, _(u"Position sur la largeur"), 'pos_larg_oeilleton',
			1,100,50, _(u"Position sur la hauteur"), 'pos_haut_oeilleton',
			1,100,50, _(u"Rayon"), 'rayon_oeilleton',
			1,10,1, _(u"Amplitude"), 'amplitude_oeilleton')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_andyWarhol = SpinSliders20Possibles(self, 
			1,20,3, _(u"Nombre d'images par ligne"), 'nbre_img_ligne_andy_warhol',
			1,20,3, _(u"Nombre d'images par colonne"), 'nbre_img_colonne_andy_warhol',
			1,10,1, _(u"Lissage"), 'lissage_andy_warhol',
			1,256,40, _(u"Couleur"), 'couleur_andy_warhol')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_bull_en_tableau = SpinSliders20Possibles(self, 
			100,2048,1024, _(u"Résolution en X"), 'resol_x_bull_en_tableau',
			100,2048,1024, _(u"Résolution en Y"), 'resol_y_bull_en_tableau',
			5,300,70, _(u"Rayon de la bulle"), 'rayon_bull_en_tableau',
			1,20,3, _(u"Bulles par ligne"), 'nbre_par_ligne_bull_en_tableau',
			1,20,3, _(u"Bulles par colonne"), 'nbre_par_ligne_bull_en_tableau',
			5,200,25, _(u"Largeur de la bordure"), 'larg_bordur_bull_en_tableau',
			5,200,25, _(u"Hauteur de la bordure"), 'haut_bordur_bull_en_tableau',
			100,3584,800, _(u"Largeur finale de l'image"), 'larg_final_img_bull_en_tableau',
			100,3584,800, _(u"Hauteur finale de l'image"), 'haut_final_img_bull_en_tableau')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_la_planete_1 = SpinSliders20Possibles(self, 
			1,6,2, _(u"Position des doubles"), 'pos_doubles_planete_1',
			10,1000,100, _(u"Rayon de la planète"), 'rayon_planete_1',
			1,500,60, _(u"Dilatation"), 'dilatation_planete_1',
			100,3584,800, _(u"Largeur finale de l'image"), 'larg_final_img_planete_1',
			100,3584,800, _(u"Hauteur finale de l'image"), 'haut_final_img_planete_1')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_bord_tendu = SpinSliders20Possibles(self, 
			1,10,1, _(u"Netteté du trait"), 'nett_trait_bord_tendu',
			1,10,1, _(u"Fluctuation de couleurs"), 'fluct_coul_bord_tendu',
			1,10,1, _(u"Transparence du trait"), 'transp_trait_bord_tendu',
			1,10,1, _(u"Floutage"), 'floutage_bord_tendu',
			1,128,1, _(u"Couleurs, début"), 'coul_debut_bord_tendu',
			128,255,255, _(u"Couleurs, fin"), 'coul_fin_img_bord_tendu')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_figuration_libre = SpinSliders20Possibles(self, 
			1,7000,1238, _(u"Amplitude"), 'amplitude_figuration_libre',
			1,10,1, _(u"Abstraction"), 'abstraction_figuration_libre',
			1,500,150, _(u"Douceur de la peinture"), 'douc_peint_figuration_libre',
			1,400,200, _(u"Couleur"), 'couleur_figuration_libre',
			1,500,310, _(u"Seuil du bord (segmentation)"), 'seuil_bord_figuration_libre',
			1,500,1, _(u"Douceur de la segmentation"), 'douc_seg_figuration_libre')
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		stacked_peint_aquarelle = SpinSliders20Possibles(self, 
			10,40,22, _(u"Intensité du trait"), 'intensite_du_trait_peint_aguarelle',
			2,16,7, _(u"Flou des couleurs"), 'flou_couleurs_peint_aguarelle',
			1,7000,80, _(u"Amplitude"), 'amplitude_peint_aguarelle',
			1,10,4, _(u"Abstraction"), 'abstraction_peint_aguarelle',
			1,500,202, _(u"Douceur de la peinture"), 'douc_peint_peint_aguarelle',
			1,400,254, _(u"Couleur"), 'couleur_peint_aguarelle',
			1,500,310, _(u"Seuil du bord (segmentation)"), 'seuil_bord_peint_aguarelle',
			1,500,102, _(u"Douceur de la segmentation"), 'douc_seg_peint_aguarelle',
			1,100,100, _(u"Opacité de l'ombre"), 'opacite_ombre_peint_aguarelle',
			1,99,20, _(u"Taille bordure horizontale"), 'tail_bord_horiz_peint_aguarelle',
			1,99,20, _(u"Taille bordure verticale"), 'tail_bord_vertic_peint_aguarelle',
			1,40,30, _(u"Distorsion de la bordure"), 'distors_bord_peint_aguarelle',
			1,5,3, _(u"Douceur de la bordure"), 'douceur_bord_peint_aguarelle')	
                # ----------------------------------------------------------------------
                # Géré par G'MIC
                ######## Rajout le 4/02/2011 par LUCAS Thomas et CABANA Antoine #########
                stacked_effet_flamme = SpinSliders20Possibles(self,
                        1,8,4, _(u"Palette de couleur"), 'palette_coul_effet_flamme',
                        1,4000,478, _(u"Amplitude"), 'amplitude_effet_flamme',
                        100,1000,145, _(u"Echantillonnage"), 'echantillonnage_effet_flamme',
                        1,1000,43, _(u"Lissage"), 'lissage_effet_flamme',
                        1,100,2, _(u"Opacité"), 'opacite_effet_flamme',
                        1,100,15, _(u"Bord"), 'bord_effet_flamme',
                        1,1000,594, _(u"Amplitude du lissage anisotropique"), 'amplitude_liss_anisotropique_effet_flamme',
                        1,200,83, _(u"Netteté"), 'nettete_effet_flamme',
                        1,100,92, _(u"Anisotropie"), 'anisotropie_effet_flamme',
                        1,1000,50, _(u"Gradiant de lissage"), 'gradiant_lissage_effet_flamme',
                        1,1000,360, _(u"Tenseur de lissage"), 'tenseur_lissage_effet_flamme',
                        10,200,57, _(u"Précision spatiale"), 'precision_spatiale_effet_flamme',
                        1,180,33, _(u"Précision angulaire"), 'precision_angulaire_effet_flamme',
                        10,500,200, _(u"Valeur de la précision"), 'valeur_precision_effet_flamme',
                        1,10,2, _(u"Répétitions"), 'repetitions_effet_flamme')
                #########################################################################

		# Widgets du stacked avec 9 boites de spins
		stacked_couleursPersonnal = FiltresAvec9Spin(parent=self)
		
		# Widgets du stacked avec 3 combos et 2 boites de spins ==> Non car pas réussi donc ...
		# _(u"Taille mini de la forme"), 'taille_mini_forme'
		# _(u"Taille maxi de la forme"), 'taille_maxi_forme'
		# Synonymes de modulation (ton, hauteur, fréquence...)
		stacked_separ_en_modules = SpinSliders(self,
			8,60,14, _(u"Taille mini de la forme"), 'taille_mini_forme',
			8,60,18, _(u"Taille maxi de la forme"), 'taille_maxi_forme')

		# Widgets du stacked avec 8 boites de spins
		stacked_ombrEtLumALaCouleur = FiltresAvec8Spin(parent=self)	
		stacked_contourEtCouleur = FiltresAvec13Spin(parent=self)

		#=== Ajout de widgets au stacked ===#

		# Widgets du stacked sans réglage
		indexStacked_sansReglage = self.stacked.addWidget(stacked_sansReglage)

		# Widgets du stacked avec un combo
		indexStacked_pointillisme = self.stacked.addWidget(stacked_pointillisme)
		indexStacked_couleursPredef = self.stacked.addWidget(stacked_couleursPredef)
		indexStacked_evanescence = self.stacked.addWidget(stacked_evanescence)
		indexStacked_negatif = self.stacked.addWidget(stacked_negatif)
		indexStacked_retournement_img = self.stacked.addWidget(stacked_retournement_img)
		indexStacked_laplacien_1 = self.stacked.addWidget(stacked_laplacien_1)
		# Mélange de Couleurs prédéfinies, Dessin 13: en couleur (donc géré par G'MIC) et 
		# Réduction du bruit (débruitage)
		indexStacked_peintDegradDeCoul = self.stacked.addWidget(stacked_PeintDegradDeCoul)
		#
		indexStacked_erosion = self.stacked.addWidget(stacked_erosion)
		indexStacked_dilatation = self.stacked.addWidget(stacked_dilatation)

		# Widgets du stacked avec un/plusieurs combo(s) + boite(s) de spin
		indexStacked_encadrePhoto = self.stacked.addWidget(stacked_encadrePhoto)

		# Widgets du stacked avec une seule boite de spin
		indexStacked_sepia = self.stacked.addWidget(stacked_sepia)
		indexStacked_traitsNoirs = self.stacked.addWidget(stacked_traitsNoirs)
		indexStacked_peuCouleurs = self.stacked.addWidget(stacked_peuCouleurs)
		indexStacked_peintHuile = self.stacked.addWidget(stacked_peintHuile)
		indexStacked_gamma = self.stacked.addWidget(stacked_gamma)
		indexStacked_fonceClair = self.stacked.addWidget(stacked_fonceClair)
		indexStacked_peintEau = self.stacked.addWidget(stacked_peintEau)
		indexStacked_basRelief = self.stacked.addWidget(stacked_basRelief)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_dessin_13_coul = self.stacked.addWidget(stacked_dessin_13_coul)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_dessin_14_crayPapier_2 = self.stacked.addWidget(stacked_dessin_14_crayPapier_2)
		# ----------------------------------------------------------------------

		# Widgets du stacked avec 2 boites de spin
		indexStacked_crayonPapier_1 = self.stacked.addWidget(stacked_crayonPapier_1)
		indexStacked_blur = self.stacked.addWidget(stacked_blur)
		indexStacked_traitCoulFond = self.stacked.addWidget(stacked_traitCoulFond)
		indexStacked_seuillage = self.stacked.addWidget(stacked_seuillage)
		indexStacked_imitationBd_2 = self.stacked.addWidget(stacked_imitationBd_2)
		indexStacked_separ_en_modules = self.stacked.addWidget(stacked_separ_en_modules)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_correctYeuxRouges = self.stacked.addWidget(stacked_correctionYeuxRouges)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		########Rajout le 28/11/2010 par LUCAS Thomas et CABANA Antoine#################
		indexStacked_visionThermique = self.stacked.addWidget(stacked_visionThermique)
		################################################################################
		# ----------------------------------------------------------------------

		# Widgets du stacked avec 3 boites de spin
		indexStacked_imitationBd_1 = self.stacked.addWidget(stacked_imitationBd_1)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_cubismeAnalytique = self.stacked.addWidget(stacked_cubismeAnalytique)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_expressionnisme = self.stacked.addWidget(stacked_expressionnisme)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_vieille_photo = self.stacked.addWidget(stacked_vieille_photo)
		# ----------------------------------------------------------------------

		# Widgets du stacked avec 20 boites de spin possibles (classe SpinSliders20Possibles de gui_modules_image.image_base)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_polaroid = self.stacked.addWidget(stacked_polaroid)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_oeilleton = self.stacked.addWidget(stacked_oeilleton)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_andyWarhol = self.stacked.addWidget(stacked_andyWarhol)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_bullEnTableau = self.stacked.addWidget(stacked_bull_en_tableau)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_laPlanete_1 = self.stacked.addWidget(stacked_la_planete_1)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_bordTendu = self.stacked.addWidget(stacked_bord_tendu)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_figurationLibre = self.stacked.addWidget(stacked_figuration_libre)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
		indexStacked_peintureAquarelle = self.stacked.addWidget(stacked_peint_aquarelle)
		# ----------------------------------------------------------------------
		# Géré par G'MIC
                ######## Rajout le 4/02/2011 par LUCAS Thomas et CABANA Antoine #################
                indexStacked_effet_flamme = self.stacked.addWidget(stacked_effet_flamme)
                #################################################################################

		# Widgets du stacked avec 9 boites de spins
		indexStacked_couleursPersonnal = self.stacked.addWidget(stacked_couleursPersonnal)

		# Widgets du stacked avec 8 boites de spins
		indexStacked_ombrEtLumALaCouleur = self.stacked.addWidget(stacked_ombrEtLumALaCouleur)

		# Widgets du stacked avec 13 boites de spins
		indexStacked_contourEtCouleur = self.stacked.addWidget(stacked_contourEtCouleur)

		# Boîte de combo
		self.comboReglage=QComboBox()
		# Paramètres de la liste de combo: [(nom entrée, identifiant, index du stacked,
		# instance stacked),...]
		self.listeComboReglage=[\
		(_(u'Vieux Films (bandes + poussières)'),	'vieux_films',		indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Sepia'),					'sepia',		indexStacked_sepia,\
				stacked_sepia),\
		(_(u'Dessin 1: traits noirs'),			'traits_noirs',		indexStacked_traitsNoirs,\
				stacked_traitsNoirs),\
		(_(u'Dessin 2: crayon à papier 1'),		'crayon_papier_1',	indexStacked_crayonPapier_1,\
				stacked_crayonPapier_1),\
		(_(u'Dessin 3: monochrome'),			'monochrome',		indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Dessin 4: avec un peu de couleur'),	'peu_couleur',		indexStacked_peuCouleurs,\
				stacked_peuCouleurs),\
		(_(u"Peinture à l'Huile"),			'peinture_huile',	indexStacked_peintHuile,\
				stacked_peintHuile),\
		(_(u'Blur - Floutage'),				'floutage',		indexStacked_blur,\
				stacked_blur),\
		(_(u'Gamma'),					'gamma',		indexStacked_gamma,\
				stacked_gamma),\
		(_(u'Dessin 5: traits de couleurs + fond noir'),'trait_couleur_fond_noir',indexStacked_traitCoulFond,\
				stacked_traitCoulFond),\
		(_(u'Pointillisme'),				'pointillisme',		indexStacked_pointillisme,\
				stacked_pointillisme),\
		(_(u'Foncé-Clair'),				'fonce_clair',		indexStacked_fonceClair,\
				stacked_fonceClair),\
		(_(u"Peinture à l'eau"),			'peinture_eau',		indexStacked_peintEau,\
				stacked_peintEau),\
		(_(u'Dessin 6: illustration en niveaux de gris'),'illustration_niveau_gris',indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Dessin 7: traits très fins + couleur'),	'traits_fins_et_couleur',	indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Emboss'),					'emboss',		indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Sharpen (détails)'),			'sharpen',		indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Niveaux de Gris'),				'niveau_gris',		indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Couleurs prédéfinies'),			'couleurs_predefinies',	indexStacked_couleursPredef,\
				stacked_couleursPredef),\
		(_(u'Création de couleurs personnalisées'),	'couleurs_personnalisees',indexStacked_couleursPersonnal,\
				stacked_couleursPersonnal),\
		(_(u'Bas-relief ou pierre sculptée'),		'bas_relief',		indexStacked_basRelief,\
				stacked_basRelief),\
		(_(u'Amélioration des bords (image plus nette)'),'amelior_des_bords',	indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Réduction du bruit (débruitage)'),		'debruitage',		indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Dessin 8: seuillage des images'),		'seuillage',		indexStacked_seuillage,\
				stacked_seuillage),\
		(_(u'Dessin 9: evanescence'),			'evanescence',		indexStacked_evanescence,\
				stacked_evanescence),\
		(_(u'Dessin 10: imitation bande dessinée 1'),	'imitation_bd_1',	indexStacked_imitationBd_1,\
				stacked_imitationBd_1),\
		(_(u'Négatif (inverse les couleurs/valeurs)'),	'negatif',		indexStacked_negatif,\
				stacked_negatif),\
		(_(u'Encadrement photographique'),		'encadre_photo',	indexStacked_encadrePhoto,\
				stacked_encadrePhoto),\
		(_(u'Séparation en modules'),			'separ_en_modules',	indexStacked_separ_en_modules,\
				stacked_separ_en_modules),\
		(_(u'Ombre et lumière à la couleur'),		'omb_lum_a_la_coul',	indexStacked_ombrEtLumALaCouleur,\
				stacked_ombrEtLumALaCouleur),\
		(_(u'Rotation image'),		                'rotation_image',	indexStacked_retournement_img,\
				stacked_retournement_img),\
		(_(u'Dessin 11: imitation bande dessinée 2'),	'imitation_bd_2',	indexStacked_imitationBd_2,\
				stacked_imitationBd_2),\
		(_(u'Dessin 12: laplacien'),	                'laplacien_1',	        indexStacked_laplacien_1,\
				stacked_laplacien_1),\
		(_(u'Contour et couleur'),		        'contour_et_couleur',	indexStacked_contourEtCouleur,\
				stacked_contourEtCouleur),\
		(_(u'Dessin 13: en couleur'),		        'dessin_13_couleur',	indexStacked_dessin_13_coul,\
				stacked_dessin_13_coul),\
		(_(u'Dessin 14: crayon à papier 2'),		'crayon_papier_2',	indexStacked_dessin_14_crayPapier_2,\
				stacked_dessin_14_crayPapier_2),\
		(_(u'Atténuation des yeux rouges'),		'correct_yeux_rouges',	indexStacked_correctYeuxRouges,\
				stacked_correctionYeuxRouges),\
		(_(u'Solarisation'),	                        'solarisation',		indexStacked_sansReglage,\
				stacked_sansReglage),\
		(_(u'Oeilleton'),		                'oeilleton',	        indexStacked_oeilleton,\
				stacked_oeilleton),\
		(_(u'Polaroïd'),		                'polaroid',	        indexStacked_polaroid,\
				stacked_polaroid),\
		(_(u'Vieille photo'),		                'vieille_photo',	indexStacked_vieille_photo,\
				stacked_vieille_photo),\
		(_(u'Cubisme analytique'),		        'cubisme_analytique',	indexStacked_cubismeAnalytique,\
				stacked_cubismeAnalytique),\
		(_(u'Andy Warhol'),		                'andy_warhol',	        indexStacked_andyWarhol,\
				stacked_andyWarhol),\
		(_(u'Expressionnisme'),		                'expressionnisme',	indexStacked_expressionnisme,\
				stacked_expressionnisme),\
		(_(u'Bulles en tableau'),	                'bull_en_tableau',      indexStacked_bullEnTableau,\
				stacked_bull_en_tableau),\
		(_(u'La planète 1'),	                        'la_planete_1',         indexStacked_laPlanete_1,\
				stacked_la_planete_1),\
		(_(u'Vision thermique'),	                'vision_thermique',	indexStacked_visionThermique,\
				stacked_visionThermique),\
		(_(u'Peinture monochrome en dégradé'),	        'peintur_degrade_de_coul', indexStacked_peintDegradDeCoul,\
				stacked_PeintDegradDeCoul),\
		(_(u'Bord tendu'),	                        'bord_tendu',           indexStacked_bordTendu,\
				stacked_bord_tendu),\
		(_(u'Erosion'),	                                'erosion',              indexStacked_erosion,\
				stacked_erosion),\
		(_(u'Dilatation'),	                        'dilatation',           indexStacked_dilatation,\
				stacked_dilatation),\
		(_(u'Figuration libre'),	                'figuration_libre',     indexStacked_figurationLibre,\
				stacked_figuration_libre),\
		(_(u'Peinture aquarelle 1'),	                'peinture_aquarelle_1', indexStacked_peintureAquarelle,\
				stacked_peint_aquarelle),\
		(_(u'Effet flamme'),	                        'effet_flamme',         indexStacked_effet_flamme,\
				stacked_effet_flamme),\
		]

		###########################
		# Conversion en CMYK retiré le 30/11/08
		# (_(u'Conversion en CMYK'),			'cmyk',			indexStacked_sansReglage,\
		#	stacked_sansReglage),\
		###########################

		# Insertion des codecs de compression dans la boite de combo
		for i in self.listeComboReglage:
			self.comboReglage.addItem(QIcon("Icones" + os.sep + "Exemples" + os.sep +  str(i[1]) + ".jpg"), i[0], QVariant(i[1]))

		self.comboReglage.setIconSize(QSize(48, 36))
		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		self.base.valeurComboIni(self.comboReglage, self.config, self.idSection, 'filtre')

		# Gestion du nombre d'images à traiter
		# Se trouve maintenant directement dans l'onglet Réglages
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel(_(u"Traitement à partir de l'image (numéro)")), 0, 0)
		self.spin1valNombres=SpinSlider(1, 100000, 1, '', self)
		self.grid.addWidget(self.spin1valNombres, 0, 1)
		self.connect(self.spin1valNombres, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		self.grid.addWidget(QLabel(_(u"Nombre de chiffres après le nom de l'image")), 1, 0)
		self.spin2valNombres=SpinSlider(3, 18, 6, '', self)
		self.grid.addWidget(self.spin2valNombres, 1, 1)
		self.connect(self.spin2valNombres, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)

		self.grid.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid)
		vboxReglage.addStretch()

		hbox = QHBoxLayout()
		hbox.addWidget(QLabel(_(u'Type')))
		hbox.addWidget(self.comboReglage)
		hbox.setAlignment(Qt.AlignHCenter)

                self.scroll = QScrollArea()
                self.scroll.setWidget(self.stacked)

		vboxReglage.addLayout(hbox)
		vboxReglage.addWidget(self.scroll)
		#vboxReglage.addWidget(self.stacked)
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
		self.afficheurImgSource=SelectWidget(mode="icone", geometrie = self.mainWindowFrameGeometry)
		self.afficheurImgDestination=Lecture_VisionImage(statusBar)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.


		# Curseur de parcours des images source ou destination
		# Déclaré ici à cause d'un bogue pas très logique sous MAC (bilbon)
		#self.curseur = QSlider(Qt.Horizontal)
		#self.curseur.setEnabled(False)

		vbox.addWidget(self.tabwidget)

		self.indexTabImgSource = self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		self.indexTabImgReglage = self.tabwidget.addTab(self.framReglage, _(u'Réglages'))
		self.indexTabImgDestin = self.tabwidget.addTab(self.afficheurImgDestination, _(u'Images après traitement'))
		self.indexTabImgInfos = self.tabwidget.addTab(self.framInfos, _(u'Infos'))

		# -------------------------------------------
		# widgets du bas : curseur + ligne + boutons
		# -------------------------------------------

		# Boutons
		self.boutAide=QPushButton(_(u" Aide"))
		self.boutAide.setIcon(QIcon("Icones" + os.sep + "icone_aide_128.png"))
		self.connect(self.boutAide, SIGNAL("clicked()"), self.afficherAide)
		self.boutApPremImg = QPushButton(_(u" Voir le résultat"))
		self.boutApPremImg.setIcon(QIcon("Icones" + os.sep + "icone_visionner_128.png"))
		self.boutApPremImg.setFocusPolicy(Qt.NoFocus)
		self.boutApPremImg.setEnabled(False)
		self.connect(self.boutApPremImg, SIGNAL("clicked()"), self.visu_1ere_img)
		self.boutAppliquer=QPushButton(_(u" Appliquer et sauver"))
		self.boutAppliquer.setIcon(QIcon("Icones" + os.sep + "icone_appliquer_128.png"))
		self.boutAppliquer.setEnabled(False)

		self.connect(self.boutAppliquer, SIGNAL("clicked()"), self.appliquer0)

		# Ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons

		hbox=QHBoxLayout()
		hbox.addWidget(self.boutAide)
		hbox.addStretch()
		hbox.addWidget(self.boutApPremImg)
		hbox.addStretch()
		hbox.addWidget(self.boutAppliquer)
		vbox.addLayout(hbox)

		#-----------------------------
		# Barre de progression
		#-----------------------------

		self.progress=QProgressDialog(_(u"Filtrage en cours..."), _(u"Arrêter"), 0, 100)
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

		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)


	def modifBoutonsAction(self, i):
		"On active ou désactive les boutons d'action selon s'il y a des images ou pas dans le widget de sélection"
		self.boutAppliquer.setEnabled(i)
		self.boutApPremImg.setEnabled(i)
		self.modifImageSource = 1


	def changerComboReglage(self, i):
		"""L'entrée sélectionnée de la boîte de combo modifie le QFrame de réglage du codec associée"""
		self.stacked.setCurrentIndex(self.listeComboReglage[i][2])
		self.config.set(self.idSection, 'filtre',self.listeComboReglage[i][1])


	def changeValNbreImg_1(self):
		"""gestion du nombre d'images à traiter"""
		#print "Traitement a partir de l'image (numero):", self.spin1valNombres.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1valNombres.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2valNombres.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2valNombres.value())


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


	def logFinal(self, titreFiltre):
		"""Affichage des informations de conversion"""
		a='#'*36
		# On ne récupère pas l'ancien % car il est arrondi
		pourCent=round(float(len(self.listeImgDestin))/len(self.listeImgSource)*100)
		pourCent = "%.0f" %pourCent
		b = a + '\n# ' + _(u'Filtre utilisé: ') + titreFiltre + '\n' + a + '\n'
		c = _(u"nombre d'images converties / nombre d'images sources")+" = "+str(len(self.listeImgDestin))+" / "\
		+str(len(self.listeImgSource))+" = " + pourCent +" %\n\n"

		# Le dernier '\n' est parfois nécessaire pour voir la dernière ligne!
		self.zoneAffichInfosImg.setText(b+c+self.infosImgTitre[0]+\
		"\n".join(self.listeImgSource)+'\n\n'+self.infosImgTitre[1]+"\n".join(self.listeImgDestin)+'\n')


	def stat_dim_img(self):
		"""Calcul statistique des dimensions des images les plus présentes dans le lot"""

		# Ouverture et mise ds une liste des dimensions des images
		listePrepaRedim=[Image.open(aA).size for aA in self.listeImgSource]

		# Merci beaucoup à Marc Keller de la liste: python at aful.org de m'avoir
		# aidé pour cette partie (les 4 lignes en dessous)
		dictSeq={}.fromkeys(listePrepaRedim, 0)
		for cle in listePrepaRedim: dictSeq[cle]+=1
		self.lStatDimSeq=sorted(zip(dictSeq.itervalues(), dictSeq.iterkeys()), reverse=1)
		self.dimStatImg=self.lStatDimSeq[0][1]
		
		#print "Toutes les dimensions des images (avec le nbre d'images):", self.lStatDimSeq
		EkdPrint(u"Toutes les dimensions des images (avec le nbre d'images): %s" % self.lStatDimSeq)
		#print 'Dimension des images la plus presente dans la sequence:', self.dimStatImg
		EkdPrint(u'Dimension des images la plus presente dans la sequence: %s' % str(self.dimStatImg))
		#print "Nombre de tailles d'images différentes dans le lot :", len(self.lStatDimSeq)
		EkdPrint(u"Nombre de tailles d'images différentes dans le lot: %s" % len(self.lStatDimSeq))

		if len(self.lStatDimSeq)>1: return 0
		else: return 1


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
				chemSortie = self.repTampon+'redim'+os.sep+os.path.basename(chemImg)
				sRedim.save(chemSortie)
				self.listeImgSource[index] = chemSortie
				index += 1


	def appliquerCouleursPredef(self):
		"""Conversion des images pour le filtre: Couleurs Prédéfinies"""
		indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
		entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])

		if entreeCombo=="rouge_vif":
			couleur_Img_Predef=(
			1.0, 0.3, 0.0, 0,
			0.0, 0.0, 0.0, 0,
			0.0, 0.0, 0.0, 0)
		elif entreeCombo=="rouge_primaire":
			couleur_Img_Predef=(
			1.0, 0.3, 0.0, 0,
			0.0, 0.0, 0.0, 0,
			0.7, 0.0, 0.0, 0)
		elif entreeCombo=="vert_perroquet":
			couleur_Img_Predef=(
			0.0, 0.0, 0.0, 0,
			1.0, 0.3, 0.0, 0,
			0.0, 0.0, 0.0, 0)
		elif entreeCombo=="vert_acide_clair":
			couleur_Img_Predef=(
			1.0, 0.0, 0.0, 0,
			1.0, 0.3, 0.0, 0,
			0.0, 0.0, 0.0, 0)
		elif entreeCombo=="bleu_roi":
			couleur_Img_Predef=(
			0.0, 0.0, 0.0, 0,
			1.0, 0.0, 0.0, 0,
			1.0, 1.0, 0.0, 0)
		elif entreeCombo=="bleu_indigo":
			couleur_Img_Predef=(
			1.0, 0.0, 0.0, 0,
			1.0, 0.0, 0.0, 0,
			1.0, 1.0, 0.0, 0)
		elif entreeCombo=="bleu_turquoise":
			couleur_Img_Predef=(
			1.0, 0.0, 0.0, 0,
			1.0, 1.0, 0.0, 0,
			1.0, 1.0, 0.0, 0)
		elif entreeCombo=="jaune_or":
			couleur_Img_Predef=(
			0.64, 0.64, 0.10, 0,
			0.56, 0.56, 0.10, 0,
			0.0, 0.0, 0.0, 0)
		elif entreeCombo=="jaune_orange":
			couleur_Img_Predef=(
			1.0, 0.5, 0.5, 0,
			1.0, 0.3, 0.0, 0,
			0.0, 0.0, 0.0, 0)
		elif entreeCombo=="saumon":
			couleur_Img_Predef=(
			1.0, 0.5, 0.0, 0,
			1.0, 0.1, 0.0, 0,
			1.0, 0.0, 0.0, 0)
		elif entreeCombo=="marron_tres_clair":
			couleur_Img_Predef=(
			0.95, 0.38, 0.0, 0,
			0.90, 0.15, 0.0, 0,
			0.48, 0.26, 0.0, 0)
		elif entreeCombo=="terre argileuse":
			couleur_Img_Predef=(
			0.96, 0.58, 0.0, 0,
			0.56, 0.44, 0.0, 0,
			0.46, 0.32, 0.0, 0)
		elif entreeCombo=="gris_colore_rouge":
			couleur_Img_Predef=(
			0.68, 0.68, 0.0, 0,
			0.50, 0.50, 0.0, 0,
			0.50, 0.50, 0.0, 0)
		elif entreeCombo=="gris_colore_vert":
			couleur_Img_Predef=(
			0.50, 0.50, 0.0, 0,
			0.62, 0.62, 0.0, 0,
			0.50, 0.50, 0.0, 0)
		elif entreeCombo=="gris_colore_bleu":
			couleur_Img_Predef=(
			0.50, 0.50, 0.0, 0,
			0.50, 0.50, 0.0, 0,
			0.64, 0.64, 0.0, 0)
		elif entreeCombo=="gris_colore_jaune":
			couleur_Img_Predef=(
			0.62, 0.62, 0.0, 0,
			0.62, 0.62, 0.0, 0,
			0.50, 0.50, 0.0, 0)

		for self.j in self.listeIndex:
			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			obImg = Image.open(self.listeImgSource[self.j])
			convert = obImg.convert("RGB").convert("RGB", couleur_Img_Predef)
			convert.save(self.cheminCourantSauv)
			if not self.opReccurApresApp(): return


	def appliquerVieuxFilms(self):
		"""Conversion des images pour le filtre: Vieux Films"""
		listePous=[
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_001.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_002.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_003.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_004.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_005.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_006.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_007.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_008.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_009.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_010.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_011.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_012.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_013.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_014.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_015.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_016.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_017.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_018.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_019.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_020.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_021.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_022.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_023.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_024.png',
		'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_025.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_026.png']

		for self.j in self.listeIndex:
			
			process = QProcess(self)
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				
				process.start("convert -blur 1%x1% -fx intensity ""\""+self.listeImgSource[self.j]+"\" "+self.repTampon+"vf_vieux_films1")
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				
				# Attention ici dans la version windows ce n'est pas traité par un 
				# QProcess (comme sous Linux) mais directement avec os.system (car le
				# QProcess avec la commande convert d'ImageMagick génère une erreur)
				os.system("convert -blur 1%x1% -fx intensity "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.repTampon+"vf_vieux_films1"+"\"")

			img0=Image.open(self.listeImgSource[self.j])
			taille=img0.size
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:

				process.start("convert "+listePous[randrange(len(listePous))]+" -resize "+ str(taille[0])+'x'+str(taille[1])+"! "+self.repTampon+"vf_vieux_films2")
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				
				# Attention ici dans la version windows ce n'est pas traité par un 
				# QProcess (comme sous Linux) mais directement avec os.system (car le
				# QProcess avec la commande convert d'ImageMagick génère une erreur)
				os.system("convert "+"\""+listePous[randrange(len(listePous))]+"\""+" -resize "+ str(taille[0])+'x'+str(taille[1])+"! "+"\""+self.repTampon+"vf_vieux_films2"+"\"")

			img1 = Image.open(self.repTampon+"vf_vieux_films2")
			img2 = Image.open(self.repTampon+"vf_vieux_films1")
			compos = Image.composite(img1,img2,img1)

			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			compos.save(self.cheminCourantSauv)

			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerSeuillage(self):
		""" Dessin 8: seuillage (avec intégration de syntaxe Numpy) """
		for self.j in self.listeIndex:
			# Ouverture des images
			obImg = Image.open(self.listeImgSource[self.j])
			# Récup réglages de seuillage bas et seuillage haut
			spin1 = self.listeComboReglage[self.i][3].spin1.value() # seuil bas
			spin2 = self.listeComboReglage[self.i][3].spin2.value() # seuil haut
			# La valeur de seuil bas ne doit jamais être supérieure ou égale à la valeur de
			# seuil haut (produirait des images sans interêt) --> dans ce cas le processus
			# s'arrête et un message avertit l'utilisateur.
			if spin1>=spin2:
				erreur=QMessageBox(self)
				erreur.setText(_(u"Attention, <b>la valeur de seuillage bas doit obligatoirement être inférieure à la valeur de seuillage haut</b>. La conversion demandée ne sera pas effectuée. Refaites vos réglages correctement et recommencez l'opération."))
				erreur.setWindowTitle(_(u"Erreur de réglage"))
				erreur.setIcon(QMessageBox.Warning)
				erreur.exec_()
				break
			else: pass
			# Conversion et sauvegarde en niveaux de gris
			imageNDG = obImg.convert("L")
			# Recup dimensions de l'image
			wSeuil, hSeuil = imageNDG.size
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egaliseNDG_Seuil = ImageOps.equalize(imageNDG)
			# Creation d'une nouvelle image
			nouvImgNDG_Seuil = Image.new("L", (wSeuil, hSeuil))
			# Insertion data ds nouvImgNDG_Seuil
			nouvImgNDG_Seuil.putdata(egaliseNDG_Seuil.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			dataNDG_Seuil=array(nouvImgNDG_Seuil)
			# Aplatissement du tableau pour traitement
			aplatNDG_Seuil=dataNDG_Seuil.flat
			# Condition: (apres parcours de chaque element du tableau)
			# ==> correspond en python classique a :
			# if aplatNDG_Seuil>=spin1 and aplatNDG_Seuil<=spin2:
			# Les pixels blancs seront placés ici.
			condSeuil=(aplatNDG_Seuil>=spin1)&(aplatNDG_Seuil<=spin2)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 0 --> noir, soit par 255 --> blanc .
			idSeuil=where(condSeuil, 0, 255)
			# Creation d'une nouvelle image
			nouvImgBinaire=Image.new("L", (wSeuil, hSeuil))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImgBinaire.putdata(idSeuil.tolist())
			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			nouvImgBinaire.save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerEvanescence(self):
		""" Dessin 9: traits noirs, fond blanc (avec intégration de syntaxe Numpy) """
		for self.j in self.listeIndex:
			# Récupération de l'index et l'entrée du combo de sélection
			indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])
			# Ouverture des images. Conversion et sauvegarde en niveaux de gris
			obImg = Image.open(self.listeImgSource[self.j]).convert("L")
			# Recup dimensions de l'image
			w, h = obImg.size
			# Kernel 5x5 Réduction du Bruit
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'_tmp_g546gf546ezr53ww7i.png', 'PNG')
			# Ouverture de l'image temporaire
			ouvImg = Image.open(self.repTampon+'_tmp_g546gf546ezr53ww7i.png')
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egalise = ImageOps.equalize(ouvImg)
			# Creation d'une nouvelle image
			nouvImg = Image.new("L", (w, h))
			# Insertion data ds nouvImg
			nouvImg.putdata(egalise.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			data = array(nouvImg)
			# Aplatissement du tableau pour traitement
			aplat = data.flat
			# Condition: (apres parcours de chaque element du tableau)
			condition=(aplat>=1)&(aplat<=255)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 255 --> blanc, soit par 0 --> noir
			if entreeCombo=='fond_blanc_lignes_noires': idCond = where(condition, 255, 0)
			elif entreeCombo=='fond_noir_lignes_blanches': idCond = where(condition, 0, 255)
			# Creation d'une nouvelle image
			nouvImgBinaire=Image.new("L", (w, h))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImgBinaire.putdata(idCond.tolist())
			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext ##
			nouvImgBinaire.save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1
			# Purge du répertoire tampon
			os.remove(self.repTampon+'_tmp_g546gf546ezr53ww7i.png')


	def appliquerImitationBd_1(self):
		""" Dessin 10: imitation bande dessinée (avec intégration [un peu] de syntaxe Numpy) """
		for self.j in self.listeIndex:
		# Récup réglages ci-dessous
			spin1 = self.listeComboReglage[self.i][3].spin1.value() # intensité des traits
			spin2 = self.listeComboReglage[self.i][3].spin2.value() # réduction des couleurs
			spin3 = self.listeComboReglage[self.i][3].spin3.value() # contraste de couleurs
			# Ouverture des images. Conversion et sauvegarde en niveaux de gris
			obImg = Image.open(self.listeImgSource[self.j]).convert("L")
			# Recup dimensions de l'image
			w, h = obImg.size

			# Partie 1 ------ Détection du contour des formes et traçage des futurs traits noirs ----
			# Kernel 5x5 Réduction du Bruit + ajout de la valeur de spin1 au centre de la matrice
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, spin1, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png', 'PNG')
			# Ouverture de l'image temporaire
			ouvImg = Image.open(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png')
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egalise = ImageOps.equalize(ouvImg)
			# Creation d'une nouvelle image
			nouvImg = Image.new("L", (w, h))
			# Insertion data ds nouvImg
			nouvImg.putdata(egalise.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			data = array(nouvImg)
			# Aplatissement du tableau pour traitement
			aplat = data.flat
			# Condition: (apres parcours de chaque element du tableau)
			condition = (aplat>=1)&(aplat<=255)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 255 --> blanc, soit par 0 --> noir
			idCond = where(condition, 255, 0)
			# Creation d'une nouvelle image
			nouvImgBinaire = Image.new("L", (w, h))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImgBinaire.putdata(idCond.tolist())
			# Recup des donnees
			listeAlpha_1=list(nouvImgBinaire.getdata())
			# Creation de la liste newListRGBAbin
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				# Si on a des pixels blancs et transparents dans listeAlpha_1 alors on injecte
				# des pixels blancs transparents mais ce  coup-ci en mode RGBA .
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				# (Autre) si on a des pixels noirs et opaques dans listeAlpha_1
				# alors on injecte des pixels noirs opaques mais ce coup-ci en
				# mode RGBA .
				else: newListRGBAbin.append((0, 0, 0, 255))

			# Creation d'une nouvelle image
			nouvImgRGBA=Image.new("RGBA", (w, h))
			# Insertion data ds nouvImgRGBA
			nouvImgRGBA.putdata(newListRGBAbin)
			# Sauvegarde image temporaire
			nouvImgRGBA.save(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png', 'PNG')
			# Attention il faut diviser par 10.0 la valeur de spin3 (c'est à dire contraste
			# de couleurs). On divise par 10.0 et pas 10 !.
			spin3=float(spin3/10.0)

			# Partie 2 ------ Réduction/postérisation/contraste des couleurs du fond de l'image -----
			# Ouverture de l'image principale dans le lot
			imPrinc=Image.open(self.listeImgSource[self.j])
			# Application du filtre pour la reduction des couleurs
			imPosterize=ImageOps.posterize(imPrinc, spin2)
			# Conversion en RGBA pour pouvoir compositer ...
			imPosterize.convert('RGBA')
			imPosterize.save(self.repTampon+'tmp_gds89gfdt39xfg6d9qxx1f.png', 'PNG')
			# Ouverture de l'image posterizee pour poursuite du traitement (application contraste)
			imPostTraitC=Image.open(self.repTampon+'tmp_gds89gfdt39xfg6d9qxx1f.png')
			# Application du filtre contraste et sauvegarde du fichier temporaire
			imContraste=ImageEnhance.Contrast(imPostTraitC)
			imContraste.enhance(spin3).save(self.repTampon+'tmp_gds486fsf68q2wx5k7u1oop.png', 'PNG')
			# Ouverture de l'image posterizee ensuite contrastée poursuite du traitement ...
			imOpc=Image.open(self.repTampon+'tmp_gds486fsf68q2wx5k7u1oop.png')
			# Conversion en RGBA pour pouvoir compositer ...
			imOpc.convert('RGBA')

			# Partie finale --- Compositing entre les traits de la partie 1 et couleurs de partie 2 -
			# Attention il s'agit bien de l'image tampon: tmp_gds568ec4u5hg53g7s9m4rt.png
			# C'est l'image qui contient les traits noirs (contours des objets)
			# Traits noirs + le fond blanc a été remplacé par un fond transparent
			imFondTransp=Image.open(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png')
			# Compositing (traitement final)
			compoContCoul=Image.composite(imFondTransp, imOpc, imFondTransp)

			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			compoContCoul.save(self.cheminCourantSauv)

			# Purge des fichiers dans le rep tampon
			os.remove(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png')
			os.remove(self.repTampon+'tmp_gds89gfdt39xfg6d9qxx1f.png')
			os.remove(self.repTampon+'tmp_gds486fsf68q2wx5k7u1oop.png')

			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerNegatif(self):
		""" Negatif: inverse les couleurs (ou les valeurs en cas de conversion en noir et blanc) """
		for self.j in self.listeIndex:
			# Récupération de l'index et l'entrée du combo de sélection
			indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])
			# Ouverture des images
			obImg = Image.open(self.listeImgSource[self.j])
			if entreeCombo=='negatif_couleur':
				negatif = ImageOps.invert(obImg)
			elif entreeCombo=='negatif_n_et_b':
				obImg = obImg.convert("L")
				negatif = ImageOps.invert(obImg)
			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext ##
			negatif.save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerEncadrePhoto(self):
		""" Encadrement photographique: appose un cadre autour des images """
		for self.j in self.listeIndex:
			# Récupération de l'index et l'entrée du combo de sélection
			indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])
			# Ouverture des images
			obImg = Image.open(self.listeImgSource[self.j])
			if entreeCombo=='noir': couleur = (0, 0, 0)
			elif entreeCombo=='gris': couleur = (128, 128, 128)
			elif entreeCombo=='blanc': couleur = (255, 255, 255)
			elif entreeCombo=='rouge': couleur = (255, 0, 0)
			elif entreeCombo=='vert': couleur = (0, 255, 0)
			elif entreeCombo=='bleu': couleur = (0, 0, 255)
			elif entreeCombo=='jaune': couleur = (255, 255, 0)
			# Application du filtre
			cadre = ImageOps.expand(obImg, 40, couleur)
			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			cadre.save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerOmbreEtLumALaCouleur(self):
		""" Ombre et lumière à la couleur (un espèce de seuillage mais avec des couleurs) """
		# Récup de l'index du filtre
		i=self.comboReglage.currentIndex()
		ll=[]
		for k in range(4):
			for l in range(2):
				ll.append(self.listeComboReglage[i][3].spin[k][l].value())
		lValCoul=[ll[0], ll[2], ll[4], ll[6], ll[1], ll[3], ll[5], ll[7]]
		# Boucle principale
		for self.j in self.listeIndex:
			# Ouverture des images
			obImg = Image.open(self.listeImgSource[self.j])
			# Conversion et sauvegarde en niveaux de gris
			imageNDG = obImg.convert("L")
			# Recup dimensions de l'image
			wSeuil, hSeuil = imageNDG.size
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egaliseNDG_Seuil = ImageOps.equalize(imageNDG)
			# Creation d'une nouvelle image
			nouvImgNDG_Seuil = Image.new("L", (wSeuil, hSeuil))
			# Insertion data ds nouvImgNDG_Seuil
			nouvImgNDG_Seuil.putdata(egaliseNDG_Seuil.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			dataNDG_Seuil=array(nouvImgNDG_Seuil)#.reshape(wSeuil*hSeuil, 3)
			# Aplatissement du tableau pour traitement
			aplatNDG_Seuil=dataNDG_Seuil.flat
			# Condition: (apres parcours de chaque element du tableau)
			# ==> correspond en python classique a :
			# if aplatNDG_Seuil>=spin1 and aplatNDG_Seuil<=spin2:
			# Les pixels blancs seront placés ici.
			condSeuil=(aplatNDG_Seuil>=128)&(aplatNDG_Seuil<=255)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 0 --> noir, soit par 255 --> blanc .
			idSeuil=where(condSeuil, 0, 255)
			# Insertion data et conversion en liste classique
			transListe=idSeuil.tolist()
			# Multiplication des données en 4 canaux et insertion en une liste de listes
			# comme ceci: [[255, 255, 255, 255], [255, 255, 255, 255], [0, 0, 0, 0], ...]
			# Le fait qu'il y ait 4 canaux est fait pour la gestion du canal alpha
			quatreCanaux=[[parcTrans]*4 for parcTrans in transListe]
			# Transformation de la liste de listes en liste de tuples
			transTuple=[tuple(parcTuple) for parcTuple in quatreCanaux]
			# Insertion des données (les blancs sont transformés en une couleur, les
			# noir en une autre, couleurs choisies par l'utilisateur)
			listeDonnees=[]
			for parcDonnees in transTuple:
				if parcDonnees==(255, 255, 255, 255):
					parcDonnees=(lValCoul[0], lValCoul[1], lValCoul[2], lValCoul[3])
					listeDonnees.append(parcDonnees)
				elif parcDonnees==(0, 0, 0, 0):
					parcDonnees=(lValCoul[4], lValCoul[5], lValCoul[6], lValCoul[7])
					listeDonnees.append(parcDonnees)
			# Creation d'une nouvelle image
			nouvImg=Image.new("RGBA", (wSeuil, hSeuil))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImg.putdata(listeDonnees)
			# Comme un canal alpha peut être appliqué à l'image sauvegardée, il vaut
			# mieux sauvegarder avec une extension qui supporte la transparence
			if self.ext not in ['.png', '.gif', '.tga']:
				self.ext='.png'
			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			nouvImg.save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerRotationImage(self):
		""" Rotation des images (90, 180 et 270 vers la gauche) """
		for self.j in self.listeIndex:
			# Récupération de l'index et l'entrée du combo de sélection
			indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])
			# Ouverture des images
			obImg = Image.open(self.listeImgSource[self.j])
			#
			if entreeCombo=='rot_img_90_gauche': rot = 90
			elif entreeCombo=='rot_img_180_gauche': rot = 180
			elif entreeCombo=='rot_img_270_gauche': rot = 270
			# Application du filtre
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			obImg.rotate(rot).save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerImitationBd_2(self):
		""" Dessin 11: imitation bande dessinée (avec intégration [un peu] de syntaxe Numpy) """
		for self.j in self.listeIndex:
			# Récup réglages ci-dessous
			spin1 = self.listeComboReglage[self.i][3].spin.value() # intensité des traits
			spin2 = str(self.listeComboReglage[self.i][3].spin2.value()) # flou des couleurs

			# Partie 1 --- Travail avec l'image de fond (couleurs floutées) ------------------------- #

			process = QProcess(self)

			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				
				process.start("convert -noise "+spin2+" -gamma 1.4 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.repTampon+'tmp_gtyj58h6fdh2fyyw478105tu.png'+"\"")
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				
				# Attention ici dans la version windows ce n'est pas traité par un 
				# QProcess (comme sous Linux) mais directement avec os.system (car le
				# QProcess avec la commande convert d'ImageMagick génère une erreur)
				os.system(("convert -noise "+spin2+" -gamma 1.4 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.repTampon+'tmp_gtyj58h6fdh2fyyw478105tu.png'+"\"").encode(locale.getdefaultlocale()[1]))

			# --------------------------------------------------------------------------------------- #

			# Partie 2 ------ Détection du contour des formes et traçage des futurs traits noirs ---- #

			# Ouverture des images. Conversion et sauvegarde en niveaux de gris
			obImg = Image.open(self.listeImgSource[self.j]).convert("L")
			# Recup dimensions de l'image
			w, h = obImg.size

			# Kernel 5x5 Réduction du Bruit + ajout de la valeur de spin1 au centre de la matrice
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, spin1, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_g9wxgfdg55t864vs156gmox4wse156sf.png', 'PNG')
			# Ouverture de l'image temporaire
			ouvImg = Image.open(self.repTampon+'tmp_g9wxgfdg55t864vs156gmox4wse156sf.png')
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egalise = ImageOps.equalize(ouvImg)
			# Creation d'une nouvelle image
			nouvImg = Image.new("L", (w, h))
			# Insertion data ds nouvImg
			nouvImg.putdata(egalise.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			data = array(nouvImg)
			# Aplatissement du tableau pour traitement
			aplat = data.flat
			# Condition: (apres parcours de chaque element du tableau)
			condition = (aplat>=1)&(aplat<=255)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 255 --> blanc, soit par 0 --> noir
			idCond = where(condition, 255, 0)
			# Creation d'une nouvelle image
			nouvImgBinaire = Image.new("L", (w, h))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImgBinaire.putdata(idCond.tolist())
			# Recup des donnees
			listeAlpha_1=list(nouvImgBinaire.getdata())
			# Creation de la liste newListRGBAbin
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				# Si on a des pixels blancs et transparents dans listeAlpha_1 alors on injecte
				# des pixels blancs transparents mais ce  coup-ci en mode RGBA .
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				# (Autre) si on a des pixels noirs et opaques dans listeAlpha_1
				# alors on injecte des pixels noirs opaques mais ce coup-ci en
				# mode RGBA .
				else: newListRGBAbin.append((0, 0, 0, 255))

			# Creation d'une nouvelle image
			nouvImgRGBA=Image.new("RGBA", (w, h))
			# Insertion data ds nouvImgRGBA
			nouvImgRGBA.putdata(newListRGBAbin)
			# Sauvegarde image temporaire
			nouvImgRGBA.save(self.repTampon+'tmp_g9wxgfdg55t864vs156gmox4wse156sf.png', 'PNG')

			# --------------------------------------------------------------------------------------- #

			# Partie finale --- Compositing entre les traits de la partie 1 et couleurs de partie 2 - #

			# Ouverture de l'image de fond (couleurs floutées) et conversion en RGBA
			imOpc=Image.open(self.repTampon+'tmp_gtyj58h6fdh2fyyw478105tu.png')
			imOpc.convert('RGBA')
			# Attention il s'agit bien de l'image tampon: tmp_g9wxgfdg55t864vs156gmox4wse156sf.png
			# C'est l'image qui contient les traits noirs (contours des objets)
			# Traits noirs + le fond blanc a été remplacé par un fond transparent
			imFondTransp=Image.open(self.repTampon+'tmp_g9wxgfdg55t864vs156gmox4wse156sf.png')
			# Compositing (traitement final)
			compoContCoul=Image.composite(imFondTransp, imOpc, imFondTransp)

			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			compoContCoul.save(self.cheminCourantSauv)

			# Purge des fichiers dans le rep tampon
			os.remove(self.repTampon+'tmp_gtyj58h6fdh2fyyw478105tu.png')
			os.remove(self.repTampon+'tmp_g9wxgfdg55t864vs156gmox4wse156sf.png')

			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerLaplacien_1(self):
		""" Dessin 12: laplacien """
		for self.j in self.listeIndex:
			# Récupération de l'index et l'entrée du combo de sélection
			indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])
			# Application du filtre
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			if entreeCombo=="laplacien_1_noir_et_blanc":
				# Conversion de l'image en niveaux de gris
				obImg = Image.open(self.listeImgSource[self.j]).convert('L')
			elif entreeCombo=="laplacien_1_couleur":
				# Conversion de l'image en RGB
				obImg = Image.open(self.listeImgSource[self.j]).convert('RGB')
			sizeKern5x5=(5, 5)
			kernLaplacien_1 = (-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 24, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1)
			imKernelLaplacien_1 = obImg.filter(ImageFilter.Kernel(sizeKern5x5, kernLaplacien_1)).save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def appliquerContourEtCouleur(self):
		""" Ce filtre est le mélange d'une partie (pour les traits de contour) du filtre 
		Dessin 10: imitation bande dessinée et du filtre Ombre et lumière à la couleur """

		for self.j in self.listeIndex:

			# Récup réglages ci-dessous
			#
			#spin1 = self.listeComboReglage[self.i][3].spin1.value() # intensité des traits
			#
			# Récup de l'index du filtre
			i=self.comboReglage.currentIndex()
			# Récup des données --> couleurs pour l'ombre, couleurs pour la lumière
			ll=[]
			for k in range(4):
				for l in range(2):
					ll.append(self.listeComboReglage[i][3].spin[k][l].value())
			lValCoul=[ll[0], ll[2], ll[4], ll[6], ll[1], ll[3], ll[5], ll[7]]
			#
			# Récuperération de la couleur du trait de contour
			coul_rouge_trait = self.listeComboReglage[i][3].spin[0][2].value() # rouge
			coul_vert_trait = self.listeComboReglage[i][3].spin[1][2].value() # vert
			coul_bleu_trait = self.listeComboReglage[i][3].spin[2][2].value() # bleu
			transparence_trait = self.listeComboReglage[i][3].spin[3][2].value() # transparence
			# Valeur de l'intensité du trait
			val_intens_trait = self.listeComboReglage[i][3].spin[len(self.listeComboReglage[i][3].spin)-1].value()
			
			# -------------------------------------------------------------------
			# Partie trait/contour
			# -------------------------------------------------------------------
			# Ouverture des images. Conversion et sauvegarde en niveaux de gris
			obImg_1 = Image.open(self.listeImgSource[self.j]).convert("L")
			# Recup dimensions de l'image
			w, h = obImg_1.size

			# Détection du contour des formes et traçage des futurs traits noirs -
			# Kernel 5x5 Réduction du Bruit + ajout de la valeur de spin1 au centre de la matrice
			imKernel = obImg_1.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, val_intens_trait, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_df7f684qf466wrt84fk8ffs74doqsf48g.png', 'PNG')
			# Ouverture de l'image temporaire
			ouvImg = Image.open(self.repTampon+'tmp_df7f684qf466wrt84fk8ffs74doqsf48g.png')
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egalise = ImageOps.equalize(ouvImg)
			# Creation d'une nouvelle image
			nouvImg = Image.new("L", (w, h))
			# Insertion data ds nouvImg
			nouvImg.putdata(egalise.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			data = array(nouvImg)
			# Aplatissement du tableau pour traitement
			aplat = data.flat
			# Condition: (apres parcours de chaque element du tableau)
			condition = (aplat>=1)&(aplat<=255)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 255 --> blanc, soit par 0 --> noir
			idCond = where(condition, 255, 0)
			# Creation d'une nouvelle image
			nouvImgBinaire = Image.new("L", (w, h))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImgBinaire.putdata(idCond.tolist())
			# Recup des donnees
			listeAlpha_1=list(nouvImgBinaire.getdata())
			# Creation de la liste newListRGBAbin
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				# Si on a des pixels blancs et transparents dans listeAlpha_1 alors on injecte
				# des pixels blancs transparents mais ce  coup-ci en mode RGBA .
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				# (Autre) si on a des pixels noirs et opaques dans listeAlpha_1
				# alors on injecte des pixels noirs opaques mais ce coup-ci en
				# mode RGBA.
				else: newListRGBAbin.append((coul_rouge_trait, coul_vert_trait, coul_bleu_trait, transparence_trait))

			# Creation d'une nouvelle image
			nouvImgRGBA=Image.new("RGBA", (w, h))
			# Insertion data ds nouvImgRGBA
			nouvImgRGBA.putdata(newListRGBAbin)
			# Sauvegarde image temporaire
			nouvImgRGBA.save(self.repTampon+'tmp_df7f684qf466wrt84fk8ffs74doqsf48g.png', 'PNG')
			# -------------------------------------------------------------------

			# -------------------------------------------------------------------
			# Partie couleur (ombre et lumière)
			# -------------------------------------------------------------------
			# Ouverture des images
			obImg_2 = Image.open(self.listeImgSource[self.j])
			# Conversion et sauvegarde en niveaux de gris
			imageNDG = obImg_2.convert("L")
			# Recup dimensions de l'image
			wSeuil, hSeuil = imageNDG.size
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egaliseNDG_Seuil = ImageOps.equalize(imageNDG)
			# Creation d'une nouvelle image
			nouvImgNDG_Seuil = Image.new("L", (wSeuil, hSeuil))
			# Insertion data ds nouvImgNDG_Seuil
			nouvImgNDG_Seuil.putdata(egaliseNDG_Seuil.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			dataNDG_Seuil=array(nouvImgNDG_Seuil)#.reshape(wSeuil*hSeuil, 3)
			# Aplatissement du tableau pour traitement
			aplatNDG_Seuil=dataNDG_Seuil.flat
			# Condition: (apres parcours de chaque element du tableau)
			# ==> correspond en python classique a :
			# if aplatNDG_Seuil>=spin1 and aplatNDG_Seuil<=spin2:
			# Les pixels blancs seront placés ici.
			condSeuil=(aplatNDG_Seuil>=128)&(aplatNDG_Seuil<=255)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 0 --> noir, soit par 255 --> blanc .
			idSeuil=where(condSeuil, 0, 255)
			# Insertion data et conversion en liste classique
			transListe=idSeuil.tolist()
			# Multiplication des données en 4 canaux et insertion en une liste de listes
			# comme ceci: [[255, 255, 255, 255], [255, 255, 255, 255], [0, 0, 0, 0], ...]
			# Le fait qu'il y ait 4 canaux est fait pour la gestion du canal alpha
			quatreCanaux=[[parcTrans]*4 for parcTrans in transListe]
			# Transformation de la liste de listes en liste de tuples
			transTuple=[tuple(parcTuple) for parcTuple in quatreCanaux]
			# Insertion des données (les blancs sont transformés en une couleur, les
			# noir en une autre, couleurs choisies par l'utilisateur)
			listeDonnees=[]
			for parcDonnees in transTuple:
				if parcDonnees==(255, 255, 255, 255):
					parcDonnees=(lValCoul[0], lValCoul[1], lValCoul[2], lValCoul[3])
					listeDonnees.append(parcDonnees)
				elif parcDonnees==(0, 0, 0, 0):
					parcDonnees=(lValCoul[4], lValCoul[5], lValCoul[6], lValCoul[7])
					listeDonnees.append(parcDonnees)
			# Creation d'une nouvelle image
			nouvImg=Image.new("RGBA", (wSeuil, hSeuil))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImg.putdata(listeDonnees)
			nouvImg.save(self.repTampon+'tmp_gg48rg68aaafgabw686u8sdv8s8f5w9d.png', 'PNG')
			# Comme un canal alpha peut être appliqué à l'image sauvegardée, il vaut
			# mieux sauvegarder avec une extension qui supporte la transparence
			if self.ext not in ['.png', '.gif', '.tga']:
				self.ext='.png'
			# -------------------------------------------------------------------

			# -------------------------------------------------------------------
			# Compositing
			# -------------------------------------------------------------------
			imFondTransp=Image.open(self.repTampon+'tmp_df7f684qf466wrt84fk8ffs74doqsf48g.png')
			compoContCoul=Image.composite(imFondTransp, nouvImg, imFondTransp)
			# -------------------------------------------------------------------

			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			compoContCoul.save(self.cheminCourantSauv)

			os.remove(self.repTampon+'tmp_df7f684qf466wrt84fk8ffs74doqsf48g.png')
			os.remove(self.repTampon+'tmp_gg48rg68aaafgabw686u8sdv8s8f5w9d.png')

			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1
			
		
	def appliquerPeintureMonochromEnDegrade(self):
		""" Filtre utilisant notamment un module python (ex. PIL) et une commande G'MIC.
		Ce filtre est un mélange de Couleurs prédéfinies, Dessin 13: en couleur et
		Réduction du bruit (débruitage). """
		
		# locale est importé ici
		import locale
		
		indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
		entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])
		
		if entreeCombo=="bleu_roi":
			coul_Img_PeintDegCoul=(
			0.0, 0.0, 0.0, 0,
			1.0, 0.0, 0.0, 0,
			1.0, 1.0, 0.0, 0)
		elif entreeCombo=="bleu_indigo":
			coul_Img_PeintDegCoul=(
			1.0, 0.0, 0.0, 0,
			1.0, 0.0, 0.0, 0,
			1.0, 1.0, 0.0, 0)
		elif entreeCombo=="jaune_or":
			coul_Img_PeintDegCoul=(
			0.64, 0.64, 0.10, 0,
			0.56, 0.56, 0.10, 0,
			0.0, 0.0, 0.0, 0)
		elif entreeCombo=="jaune_orange":
			coul_Img_PeintDegCoul=(
			1.0, 0.5, 0.5, 0,
			1.0, 0.3, 0.0, 0,
			0.0, 0.0, 0.0, 0)
		elif entreeCombo=="saumon":
			coul_Img_PeintDegCoul=(
			1.0, 0.5, 0.0, 0,
			1.0, 0.1, 0.0, 0,
			1.0, 0.0, 0.0, 0)
		elif entreeCombo=="marron_tres_clair":
			coul_Img_PeintDegCoul=(
			0.95, 0.38, 0.0, 0,
			0.90, 0.15, 0.0, 0,
			0.48, 0.26, 0.0, 0)
		elif entreeCombo=="terre argileuse":
			coul_Img_PeintDegCoul=(
			0.96, 0.58, 0.0, 0,
			0.56, 0.44, 0.0, 0,
			0.46, 0.32, 0.0, 0)
		
		for self.j in self.listeIndex:
			obImg_1 = Image.open(self.listeImgSource[self.j])
			convert_1 = obImg_1.convert("RGB").convert("RGB", coul_Img_PeintDegCoul)
			convert_1.save(self.repTampon+'tmp_f4781297g41ze7gw5ty5k6ggu7y7ybg147tf.png', 'PNG')
			# Partie --> Dessin 13: en couleur
			#
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				###############################################################################
				## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
				### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
				### traitement).                                                             ##
				os.system(("gmic "+"\\\""+self.repTampon+'tmp_f4781297g41ze7gw5ty5k6ggu7y7ybg147tf.png'+"\\\""+" -drawing 6288 -o "+"\\\""+self.repTampon+'tmp_wzert75fsdf98vf8yu2v1g47gexm4y7yp9b.png'+"\\\"").encode(locale.getdefaultlocale()[1]))
				###############################################################################
				# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -drawing 6288 -o "+"\\\""+self.repTampon+'tmp_wzert75fsdf98vf8yu2v1g47gexm4y7yp9b.png'+"\\\"")
			# Uniquement pour windows
			elif os.name == 'nt':
				os.system(("gmic "+"\\\""+self.repTampon+'tmp_f4781297g41ze7gw5ty5k6ggu7y7ybg147tf.png'+"\\\""+" -drawing 6288 -o "+"\\\""+self.repTampon+'tmp_wzert75fsdf98vf8yu2v1g47gexm4y7yp9b.png'+"\\\"").encode(locale.getdefaultlocale()[1]))
			# Partie --> Réduction du bruit (débruitage)
			obImg_2 = Image.open(self.repTampon+'tmp_wzert75fsdf98vf8yu2v1g47gexm4y7yp9b.png')
			convert_2 = obImg_2.filter(ImageFilter.Kernel((5, 5), (2, 4, 5, 4, 2, 4, 9, 12, 9, 4, 5, 12, 15, 12, 5, 4, 9, 12, 9, 4, 2, 4, 5, 4, 2)))
			# Supression des images tampon
			os.remove(self.repTampon+'tmp_f4781297g41ze7gw5ty5k6ggu7y7ybg147tf.png')
			os.remove(self.repTampon+'tmp_wzert75fsdf98vf8yu2v1g47gexm4y7yp9b.png')
			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			convert_2.save(self.cheminCourantSauv)
			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1
			
			
	def appliquerPeintureAquarelle_1(self):
		""" Filtre utilisant notamment un module python (ex. PIL et Numpy) et quatre commandes G'MIC. 
		Ce filtre est un mélange de Dessin 11: imitation bande dessinée 2 et (G'MIC): Gimp painting 
		+ Segmentation + Shadow patch + Fuzzy frame """
		
		# locale est importé ici
		import locale
		
		#################################################
		# Pour Peinture aquarelle:
		# --------------------------------
		# spin1 --> Intensité des traits
		# spin2 --> Flou des couleurs
		# spin3 --> Amplitude
		# spin4 --> Abstraction
		# spin5 --> Douceur de la peinture
		# spin6 --> Couleur
		# spin7 --> Seuil du bord (segmentation)
		# spin8 --> Douceur de la segmentation
		# spin9 --> Opacité de l'ombre
		# spin10 --> Taille bordure horizontale
		# spin11 --> Taille bordure verticale
		# spin12 --> Distorsion de la bordure
		# spin13 --> Douceur de la bordure
		#################################################
		spin1 = self.listeComboReglage[self.i][3].spin.value()
		spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
		spin3 = self.listeComboReglage[self.i][3].spin3.value()
		spin3 = str(spin3/100)
		spin4 = str(self.listeComboReglage[self.i][3].spin4.value())
		spin5 = self.listeComboReglage[self.i][3].spin5.value()
		spin5 = str(spin5/100)
		spin6 = self.listeComboReglage[self.i][3].spin6.value()
		spin6 = str(spin6/100)
		spin7 = self.listeComboReglage[self.i][3].spin7.value()
		spin7 = str(spin7/100)
		spin8 = self.listeComboReglage[self.i][3].spin8.value()
		spin8 = str(spin8/100)
		spin9 = self.listeComboReglage[self.i][3].spin9.value()
		spin9 = str(spin9/100)
		spin10 = str(self.listeComboReglage[self.i][3].spin10.value())
		spin11 = str(self.listeComboReglage[self.i][3].spin11.value())
		spin12 = str(self.listeComboReglage[self.i][3].spin12.value())
		spin13 = str(self.listeComboReglage[self.i][3].spin13.value())
		
		for self.j in self.listeIndex:
			
			######################################################
			# Partie --> Dessin 11: imitation bande dessinée 2
			######################################################

			# Travail avec l'image de fond (couleurs floutées) -------------------------------------- #

			process = QProcess(self)

			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				
				process.start("convert -noise "+spin2+" -gamma 1.4 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.repTampon+'tmp_grt8u49ret89vdsr49tgw4tyhb6e5dd1k58v.png'+"\"")
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				
			# Uniquement pour windows
			elif os.name == 'nt':
				
				# Attention ici dans la version windows ce n'est pas traité par un 
				# QProcess (comme sous Linux) mais directement avec os.system (car le
				# QProcess avec la commande convert d'ImageMagick génère une erreur)
				os.system(("convert -noise "+spin2+" -gamma 1.4 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.repTampon+'tmp_grt8u49ret89vdsr49tgw4tyhb6e5dd1k58v.png'+"\"").encode(locale.getdefaultlocale()[1]))

			# --------------------------------------------------------------------------------------- #

			# Détection du contour des formes et traçage des futurs traits noirs -------------------- #

			# Ouverture des images. Conversion et sauvegarde en niveaux de gris
			obImg = Image.open(self.listeImgSource[self.j]).convert("L")
			# Recup dimensions de l'image
			w, h = obImg.size

			# Kernel 5x5 Réduction du Bruit + ajout de la valeur de spin1 au centre de la matrice
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, spin1, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_g84gfgs2d3hvl7op8sq4v0yer4w4z1g97f.png', 'PNG') 
			# Ouverture de l'image temporaire
			ouvImg = Image.open(self.repTampon+'tmp_g84gfgs2d3hvl7op8sq4v0yer4w4z1g97f.png')
			# Filtre egalisateur pour renforcer les zones claires et les zones foncées
			egalise = ImageOps.equalize(ouvImg)
			# Creation d'une nouvelle image
			nouvImg = Image.new("L", (w, h))
			# Insertion data ds nouvImg
			nouvImg.putdata(egalise.getdata())
			# Récup des données contenues ds l'image et mises dans un tableau par Numpy
			data = array(nouvImg)
			# Aplatissement du tableau pour traitement
			aplat = data.flat
			# Condition: (apres parcours de chaque element du tableau)
			condition = (aplat>=1)&(aplat<=255)
			# Selon la condition, remplacement de chaque element/pixel
			# soit par 255 --> blanc, soit par 0 --> noir
			idCond = where(condition, 255, 0)
			# Creation d'une nouvelle image
			nouvImgBinaire = Image.new("L", (w, h))
			# Insertion data ds nouvImgBinaire et conversion en liste classique
			nouvImgBinaire.putdata(idCond.tolist())
			# Recup des donnees
			listeAlpha_1=list(nouvImgBinaire.getdata())
			# Creation de la liste newListRGBAbin
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				# Si on a des pixels blancs et transparents dans listeAlpha_1 alors on injecte
				# des pixels blancs transparents mais ce  coup-ci en mode RGBA .
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				# (Autre) si on a des pixels noirs et opaques dans listeAlpha_1
				# alors on injecte des pixels noirs opaques mais ce coup-ci en
				# mode RGBA .
				else: newListRGBAbin.append((0, 0, 0, 255))

			# Creation d'une nouvelle image
			nouvImgRGBA=Image.new("RGBA", (w, h))
			# Insertion data ds nouvImgRGBA
			nouvImgRGBA.putdata(newListRGBAbin)
			# Sauvegarde image temporaire
			nouvImgRGBA.save(self.repTampon+'tmp_g84gfgs2d3hvl7op8sq4v0yer4w4z1g97f.png', 'PNG')

			# --------------------------------------------------------------------------------------- #

			# Compositing entre les traits et couleurs ---------------------------------------------- #

			# Ouverture de l'image de fond (couleurs floutées) et conversion en RGBA
			imOpc=Image.open(self.repTampon+'tmp_grt8u49ret89vdsr49tgw4tyhb6e5dd1k58v.png')
			imOpc.convert('RGBA')
			# Attention il s'agit bien de l'image tampon: tmp_g84gfgs2d3hvl7op8sq4v0yer4w4z1g97f.png
			# C'est l'image qui contient les traits noirs (contours des objets)
			# Traits noirs + le fond blanc a été remplacé par un fond transparent
			imFondTransp=Image.open(self.repTampon+'tmp_g84gfgs2d3hvl7op8sq4v0yer4w4z1g97f.png')
			# Compositing (traitement final)
			compoContCoul=Image.composite(imFondTransp, imOpc, imFondTransp)
			compoContCoul.save(self.repTampon+'tmp_gfg84s9ef8f8ser8v8ghiqz516azd99qsw51k8y.png', 'PNG')
			
			# Purge des fichiers dans le rep tampon
			os.remove(self.repTampon+'tmp_grt8u49ret89vdsr49tgw4tyhb6e5dd1k58v.png')
			os.remove(self.repTampon+'tmp_g84gfgs2d3hvl7op8sq4v0yer4w4z1g97f.png')

			# Sauvegarde
			self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
			
			######################################################
			# Partie --> G'MIC ==> Gimp painting + Segmentation + Shadow patch + Fuzzy frame
			######################################################
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				###############################################################################
				## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
				### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
				### traitement).                                                             ##
				os.system(("gmic "+"\\\""+self.repTampon+'tmp_gfg84s9ef8f8ser8v8ghiqz516azd99qsw51k8y.png'+"\\\""+"  -drawing  "+spin3+" -gimp_painting "+spin4+','+spin5+','+spin6+" -gimp_segment_watershed_preview "+spin7+','+spin8+',0,0'+" -gimp_shadow_patch "+spin9+",0"+" -gimp_frame_fuzzy "+spin10+','+spin11+','+spin12+','+spin13+",255,255,255,255 "+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
				###############################################################################
				# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				#self.process.start("gmic "+"\\\""+self.repTampon+'tmp_gfg84s9ef8f8ser8v8ghiqz516azd99qsw51k8y.png'+"\\\""+"  -drawing  "+spin3+" -gimp_painting "+spin4+','+spin5+','+spin6+" -gimp_segment_watershed_preview "+spin7+','+spin8+',0,0'+" -gimp_shadow_patch "+spin9+",0"+" -gimp_frame_fuzzy "+spin10+','+spin11+','+spin12+','+spin13+",255,255,255,255 "+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
			# Uniquement pour windows
			elif os.name == 'nt':
				os.system(("gmic "+"\\\""+self.repTampon+'tmp_gfg84s9ef8f8ser8v8ghiqz516azd99qsw51k8y.png'+"\\\""+"  -drawing  "+spin3+" -gimp_painting "+spin4+','+spin5+','+spin6+" -gimp_segment_watershed_preview "+spin7+','+spin8+',0,0'+" -gimp_shadow_patch "+spin9+",0"+" -gimp_frame_fuzzy "+spin10+','+spin11+','+spin12+','+spin13+",255,255,255,255 "+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))

			# Purge du dernier fichier dans le rep tampon
			os.remove(self.repTampon+'tmp_gfg84s9ef8f8ser8v8ghiqz516azd99qsw51k8y.png')

			# Fin
			if not self.opReccurApresApp(): return
			self.j += 1


	def arretProgression(self):
		"""Si le filtre appliqué est 100 % shell, alors la conversion est immédiatement stoppée après un clic sur le bouton de la QProgessDialog. Pas la peine d'attendre la fin de la conversion de l'image en cours comme pour les autres types de filtres."""
		if self.listeComboReglage[self.i][1] in self.filtresPython: return
		self.terminerFiltreShell = 1
		self.process.kill()
		if len(self.listeImgDestin)!=0:
			self.conversionImg = 1
			self.logFinal(self.listeComboReglage[self.i][0])
			self.tabwidget.setCurrentIndex(self.indexTabImgInfos)
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
			self.tabwidget.setCurrentIndex(self.indexTabImgInfos)
			return

		# On ne continue pas si l'utilisateur l'a décidé
		elif self.terminerFiltreShell: return

		# On passe à l'image suivante s'il en reste
		elif self.opReccurApresApp():
			self.appliquer()


	def opReccurApresApp(self):
		"""Opérations à effectuer après chaque appel du moteur."""
		if self.listeComboReglage[self.i][1] in self.filtresPython:
			modulePython = 1 # conversion python (+ shell pour certains filtres)
		else: modulePython = 0 # conversion 100% shell

		self.listeImgDestin.append(self.cheminCourantSauv)
		pourCent=int((float(self.j+1)/self.nbrImg)*100)

		self.progress.setValue(pourCent)
		#!!!Rafraichissement indispensable pour la transmission immédiate du signal QProgressDialog().wasCanceled
		if modulePython: QApplication.processEvents()

		# Incrémentation de l'indice du fichier source pour une conversion 100% commande shell
		if not modulePython: self.j += 1

		# Opérations de fin de conversion
		if pourCent==100:
			# Condition à respecter pour qu'un affichage d'une nouvelle image ait lieu dans l'onglet "Images après traitement"
			self.conversionImg = 1
			# Boite de dialogue d'information
			messageAide=QMessageBox(self)
			messageAide.setText(_(u"Le filtre a été appliqué avec succès!"))
			messageAide.setWindowTitle(self.listeComboReglage[self.i][0])
			messageAide.setIcon(QMessageBox.Information)
			messageAide.exec_()
			# Uniquement pour windows
			if os.name == 'nt':
				# Les 3 lignes du dessous sont pour l'élimination du répertoire ekd_gmic_filtres_image
				# servant pour le filtre image Effet flamme (sous windows uniquement), pour plus de
				# précisions, voir dans la fonction appliquer.
				lecteur = os.environ['HOMEDRIVE']
				rep_annexe = lecteur + os.sep + 'ekd_gmic_filtres_image' + os.sep
				if os.path.isdir(rep_annexe) is True: shutil.rmtree(rep_annexe)
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
				self.tabwidget.setCurrentIndex(self.indexTabImgInfos)
			return 0

		return 1


	def visu_1ere_img(self):
		"""Fonction pour faire une simulation de rendu (avec les réglages opérés dans l'onglet Réglages)
		et ce à partir du bouton Aperçu à partir de la première image, toujours dans l'onglet Réglages"""

		file = self.afficheurImgSource.getFile()
		if not file:
			return

		self.listeImgSource=[file] # changer la suite
		# et virer les crochets de cette liste

		# Récup de l'index du filtre
		i=self.comboReglage.currentIndex()

		self.cheminCourantSauv = self.repTampon+'image_visu_'+string.zfill(1, 6)+'.png'

		#------------------------------
		# Filtres 100% commande shell
		#------------------------------

		#------------------------------
		# Gestion par ImagMagick
		#------------------------------

		# locale est importé ici
		import locale

		if self.listeComboReglage[i][1] in ['sepia','traits_noirs','peu_couleur','peinture_huile',\
					'gamma','fonce_clair','peinture_eau','bas_relief']:
			spin = str(self.listeComboReglage[i][3].spin.value())
			if self.listeComboReglage[i][1]=='sepia':
				os.system(("convert -sepia-tone "+spin+"% -monitor "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='traits_noirs':
				os.system(("convert -charcoal "+spin+" -monochrome "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='peu_couleur':
				os.system(("convert -enhance -equalize -edge "+spin+" -colorize 6,12,20 "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='peinture_huile':
				os.system(("convert -paint "+spin+' '+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='gamma':
				os.system(("convert -gamma "+spin+' '+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='fonce_clair':
				os.system(("convert -modulate "+spin+' '+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='peinture_eau':
				os.system(("convert -noise "+spin+" -gamma 1.4 "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='bas_relief':
				os.system(("convert -paint "+spin+" -shade 120x45 "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))

		elif self.listeComboReglage[i][1] in ['crayon_papier_1','floutage','trait_couleur_fond_noir']:
			spin1 = str(self.listeComboReglage[i][3].spin1.value())
			spin2 = str(self.listeComboReglage[i][3].spin2.value())
			if self.listeComboReglage[i][1]=='crayon_papier_1':
				os.system(("convert -spread "+spin2+" -charcoal "+spin1+' '+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='floutage':
				os.system(("convert -blur "+spin1+'%'+'x'+spin2+"% "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='trait_couleur_fond_noir':
				os.system(("convert -median "+spin1+" -edge "+spin2+' '+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))

		elif self.listeComboReglage[i][1]=='monochrome':
			os.system(("convert -monochrome "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))

		elif self.listeComboReglage[i][1]=='pointillisme':
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			os.system(("convert +noise "+entreeCombo+' '+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
			'''
			elif self.listeComboReglage[i][1]=='craie_blanche':
			os.system("convert -blur 2x2 -fx 'log(r*60*pi)' -edge 0.1 -blur 2x2 "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
			'''

		#------------------------------
		# Gestion par G'MIC
		#------------------------------

		### ATTENTION ######################################################################
		# "\"" a été remplacé par "\\\"" car G'MIC demande une syntaxe du style: 
		# gmic \"mon nom de fichier avec espace.jpg\" ... pour pouvoir traiter des fichiers
		# avec des espaces dans son nom
		####################################################################################

		if self.listeComboReglage[i][1] in ['dessin_13_couleur', 'crayon_papier_2', 'polaroid', 'vieille_photo', 'oeilleton', 'cubisme_analytique', 'andy_warhol', 'expressionnisme', 'correct_yeux_rouges', 'solarisation', 'bull_en_tableau', 'la_planete_1', 'vision_thermique', 'bord_tendu', 'erosion', 'dilatation', 'figuration_libre', 'effet_flamme']:
			if self.listeComboReglage[i][1]=='dessin_13_couleur':
				#################################################
				# Pour Dessin 13: couleur:
				# ------------------------
				# spin1 --> Amplitude
				#################################################
				spin1 = self.listeComboReglage[i][3].spin1.value()
				spin1 = str(spin1/100)
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -drawing "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='crayon_papier_2':
				#################################################
				# Pour Dessin 14: crayon à papier 2:
				# ----------------------------------
				# spin1 --> Taille
				#################################################
				spin1 = self.listeComboReglage[i][3].spin1.value()
				spin1 = str(spin1/10)
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -pencilbw "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='correct_yeux_rouges':
				#################################################
				# Pour Correction des yeux rouges:
				# --------------------------------
				# spin1 --> Seuil des couleurs
				# spin2 --> Lissage
				# spin3 --> Atténuation
				#################################################
				spin1 = self.listeComboReglage[i][3].spin1.value()
				# Si spin1 réglé sur 1 en fait spin vaut 0
				if spin1 == 1: spin1 = 0
				# Si la valeur de spin1 est supérieure à 1 on retranche 1
				if spin1 > 1: spin1 = spin1 - 1
				spin1 = str(spin1)
				spin2 = self.listeComboReglage[i][3].spin2.value()
				spin2 = str(spin2/10.0)
				spin3 = self.listeComboReglage[i][3].spin3.value()
				spin3 = str(spin3/10.0)
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -red_eye "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='solarisation':
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -solarize -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='oeilleton':
				#################################################
				# Pour Oeilleton:
				# ---------------
				# spin1 --> Position sur la largeur
				# spin2 --> Position sur la hauteur
				# spin3 --> Rayon
				# spin4 --> Amplitude
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = str(self.listeComboReglage[i][3].spin3.value())
				spin4 = str(self.listeComboReglage[i][3].spin4.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -fish_eye "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='polaroid':
				#################################################
				# Pour Polaroïd:
				# --------------
				# spin1 --> Taille de la bordure
				# spin2 --> Taille en largeur pour l'ombre
				# spin3 --> Taille en hauteur pour l'ombre
				# spin4 --> Rotation (en degrés) de  la photo
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = str(self.listeComboReglage[i][3].spin3.value())
				spin4 = str(self.listeComboReglage[i][3].spin4.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -polaroid "+spin1+" -drop_shadow "+spin2+','+spin3+" -rotate "+spin4+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='vieille_photo':
				#################################################
				# Pour Vieille photo:
				# -------------------
				# spin1 --> Taille en largeur pour l'ombre
				# spin2 --> Taille en hauteur pour l'ombre
				# spin3 --> Rotation (en degrés) de  la photo
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = str(self.listeComboReglage[i][3].spin3.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -old_photo -drop_shadow "+spin1+','+spin2+" -rotate "+spin3+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='cubisme_analytique':
				#################################################
				# Pour Cubisme analytique:
				# ------------------------
				# spin1 --> Itération
				# spin2 --> Taille de bloc
				# spin3 --> Angle
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = str(self.listeComboReglage[i][3].spin3.value())
				#self.process = EkdProcess(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -cubism "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]), output = None, stdinput = None)
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -cubism "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='andy_warhol':
				#################################################
				# Pour Andy Warhol:
				# -----------------
				# spin1 --> Nombre d'images par ligne
				# spin2 --> Nombre d'images par colonne
				# spin3 --> Lissage
				# spin4 --> Couleur
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = str(self.listeComboReglage[i][3].spin3.value())
				spin4 = str(self.listeComboReglage[i][3].spin4.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -warhol "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='expressionnisme':
				#################################################
				# Pour Expressionnisme:
				# ---------------------
				# spin1 --> Abstraction
				# spin2 --> Lissage
				# spin3 --> Couleur
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = self.listeComboReglage[i][3].spin2.value()
				spin2 = str(spin2/100)
				spin3 = self.listeComboReglage[i][3].spin3.value()
				spin3 = str(spin3/100)
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -gimp_painting "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='bull_en_tableau':
				#################################################
				# Pour Bulles en tableau:
				# -----------------------
				# spin1 --> Résolution en X
				# spin2 --> Résolution en Y
				# spin3 --> Rayon de la bulle
				# spin4 --> Bulles par ligne
				# spin5 --> Bulles par colonne
				# spin6 --> Largeur de la bordure
				# spin7 --> Hauteur de la bordure
				# spin8 --> Largeur finale de l'image
				# spin9 --> Hauteur finale de l'image
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = str(self.listeComboReglage[i][3].spin3.value())
				spin4 = str(self.listeComboReglage[i][3].spin4.value())
				spin5 = str(self.listeComboReglage[i][3].spin5.value())
				spin6 = str(self.listeComboReglage[i][3].spin6.value())
				spin7 = str(self.listeComboReglage[i][3].spin7.value())
				spin8 = str(self.listeComboReglage[i][3].spin8.value())
				spin9 = str(self.listeComboReglage[i][3].spin9.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -mirror z -map_sphere "+spin1+','+spin2+','+spin3+" -array_fade "+spin4+','+spin5+" -frame_fuzzy "+spin6+','+spin7+" -resize "+spin8+','+spin9+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
				# gmic in.jpg -mirror z -map_sphere 1024,1024,70 -array_fade 3,3 -frame_fuzzy 25,25 -resize 600,450 -o out.jpg
			elif self.listeComboReglage[i][1]=='la_planete_1':
				#################################################
				# Pour Bulles en tableau:
				# -----------------------
				# spin1 --> Position des doubles
				# spin2 --> Rayon de la planète
				# spin3 --> Dilatation
				# spin4 --> Largeur finale de l'image
				# spin5 --> Hauteur finale de l'image
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = self.listeComboReglage[i][3].spin3.value()
				spin3 = str(spin3/100.0)
				spin4 = str(self.listeComboReglage[i][3].spin4.value())
				spin5 = str(self.listeComboReglage[i][3].spin5.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -repeat "+spin1+ " --mirror x -a x -done -map_sphere "+spin4+','+spin5+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
				# gmic in.jpg -repeat 2 --mirror x -a x -done -map_sphere 400,400,100,0.9 -o out.jpg
			######## Rajout le 28/11/2010 par LUCAS Thomas et CABANA Antoine ##################
			elif self.listeComboReglage[i][1]=='vision_thermique':
				#################################################
				# Pour Vision Thermique :
				# -----------------------
				# spin1 --> Minimum de Luminance
				# spin2 --> Maximum de Luminance
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				'''
				if spin1 >= spin2:
					erreur=QMessageBox(self)
					erreur.setText(_(u"Attention, <b>la valeur du mini ne doit jamais être supérieure ou égale à la valeur du maxi de la luminance</b>. L'opération demandée ne sera pas effectuée. Refaites vos réglages correctement et recommencez l'opération."))
					erreur.setWindowTitle(_(u"Erreur de réglage"))
					erreur.setIcon(QMessageBox.Warning)
					erreur.exec_()
					sys.exit
				else:
				#spin1 = str(self.listeComboReglage[i][3].spin1.value()) # Ce réglage est déjà définis plus haut ds le code
				#spin2 = str(self.listeComboReglage[i][3].spin2.value()) # Ce réglage est déjà définis plus haut ds le code
				'''
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+ " -luminance -n "+spin1+','+spin2+" -negative -map 1 -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='bord_tendu':
				#################################################
				# Pour Bord tendu:
				# --------------------------------
				# spin1 --> Netteté du trait
				# spin2 --> Fluctuation de couleurs
				# spin3 --> Transparence du trait
				# spin4 --> Floutage
				# spin5 --> Couleurs, début
				# spin6 --> Couleurs, fin
				#################################################
				spin1 = self.listeComboReglage[i][3].spin1.value()
				spin1 = str(spin1/10.0)
				spin2 = self.listeComboReglage[i][3].spin2.value()
				spin2 = str(spin2/10.0)
				spin3 = str(self.listeComboReglage[i][3].spin3.value())
				spin4 = str(self.listeComboReglage[i][3].spin4.value())
				spin5 = str(self.listeComboReglage[i][3].spin5.value())
				spin6 = str(self.listeComboReglage[i][3].spin6.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -edgetensors "+spin1+','+spin2+','+spin3+','+spin4+" -n "+spin5+','+spin6+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='erosion':
				#################################################
				# Pour Erosion:
				# --------------------------------
				# spin1 --> Valeur d'érosion
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -erode "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='dilatation':
				#################################################
				# Pour Dilatation:
				# --------------------------------
				# spin1 --> Valeur de dilatation
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value())
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -dilate "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			elif self.listeComboReglage[i][1]=='figuration_libre':
				#################################################
				# Pour Figuration libre:
				# --------------------------------
				# spin1 --> Amplitude
				# spin2 --> Abstraction
				# spin3 --> Douceur de la peinture
				# spin4 --> Couleur
				# spin5 --> Seuil du bord (segmentation)
				# spin6 --> Douceur de la segmentation
				#################################################
				spin1 = self.listeComboReglage[i][3].spin1.value()
				spin1 = str(spin1/100)
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = self.listeComboReglage[i][3].spin3.value()
				spin3 = str(spin3/100)
				spin4 = self.listeComboReglage[i][3].spin4.value()
				spin4 = str(spin4/100)
				spin5 = self.listeComboReglage[i][3].spin5.value()
				spin5 = str(spin5/100)
				spin6 = self.listeComboReglage[i][3].spin6.value()
				spin6 = str(spin6/100)
				os.system(("gmic "+"\\\""+self.listeImgSource[0]+"\\\""+"  -drawing  "+spin1+" -gimp_painting "+spin2+','+spin3+','+spin4+" -gimp_segment_watershed_preview "+spin5+','+spin6+',0,0'+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			######## Rajout le 4/02/2011 par LUCAS Thomas et CABANA Antoine ##################
			elif self.listeComboReglage[i][1]=='effet_flamme':
				#################################################
				# Pour Effet flamme :
				# -----------------------
				# spin1 --> Palette
				# spin2 --> Amplitude
				# spin3 --> Echantillonnage
				# spin4 --> Lissage
				# spin5 --> Opacité
				# spin6 --> Bord
				# spin7 --> Amplitude du lissage anisotropique
				# spin8 --> Netteté
				# spin9 --> Anisotropie
				# spin10 --> Gradiant de lissage
				# spin11 --> Tenseur de lissage
				# spin12 --> Précision spaciale
				# spin13 --> Précision angulaire
				# spin14 --> Valeur de la précision
				# spin15 --> Iterations
				#################################################
				spin1 = str(self.listeComboReglage[i][3].spin1.value()-1)
				spin2 = str(self.listeComboReglage[i][3].spin2.value())
				spin3 = str(self.listeComboReglage[i][3].spin3.value()/100.0)
				spin4 = str(self.listeComboReglage[i][3].spin4.value()/100.0)
				spin5 = str(self.listeComboReglage[i][3].spin5.value()/100.0)
				spin6 = str(self.listeComboReglage[i][3].spin6.value())
				spin7 = str(self.listeComboReglage[i][3].spin7.value())
				spin8 = str(self.listeComboReglage[i][3].spin8.value()/100.0)
				spin9 = str(self.listeComboReglage[i][3].spin9.value()/100.0)
				spin10 = str(self.listeComboReglage[i][3].spin10.value()/100.0)
				spin11 = str(self.listeComboReglage[i][3].spin11.value()/100.0)
				spin12 = str(self.listeComboReglage[i][3].spin12.value()/100.0)
				spin13 = str(self.listeComboReglage[i][3].spin13.value())
				spin14 = str(self.listeComboReglage[i][3].spin14.value()/100.0)
				spin15 = str(self.listeComboReglage[i][3].spin15.value())
				# Uniquement pour windows
                                if os.name == 'nt':
					# Sous windows (comme la plupart du temps EKD est installé dans Program Files), une
					# erreur est générée et le filtre Effet flamme ne peut pas être mis en oeuvre car
					# G'MIC ne peut pas aller chercher le fichier fire2.gmic dans un chemin comportant
					# des espace (des trous) ... il faut donc créer un chemin sous windows et copier
					# ce fichier pour qu'on puisse aller le chercher.
					# Répertoire courant
					rep_cour = os.getcwd()
					# Chemin exact du répertoire annexe en local dans l'arborescence d'EKD
					rep_chem_annex_local = rep_cour + os.sep + "gui_modules_image" + os.sep + "filtres_images" + os.sep + "annexe" + os.sep
					# Scan pour récupérer le fichier fire2.gmic en local (filtre image Effet flamme)
					fich_gmic_filtre_effet_flam = rep_chem_annex_local + 'fire2.gmic'
					# Là ou se trouve le lecteur par défaut sous windows (souvent C:)
					lecteur = os.environ['HOMEDRIVE']
					self.rep_annexe = lecteur + os.sep + 'ekd_gmic_filtres_image' + os.sep
					# Si le répertoire n'existe pas, il est crée
					if os.path.isdir(self.rep_annexe) is False: os.makedirs(self.rep_annexe)
					if os.path.isfile(fich_gmic_filtre_effet_flam) is True:
						shutil.copy(rep_chem_annex_local+os.sep+'fire2.gmic', self.rep_annexe[:-1])
				# Traitement
				os.system(("gmic "+" -m "+self.rep_annexe+"fire2.gmic "+"\\\""+self.listeImgSource[0]+"\\\""+" -fire "+spin1+','+spin2+','+spin3+','+spin4+','+spin5+','+spin6+','+spin7+','+spin8+','+spin9+','+spin10+','+spin11+','+spin12+','+spin13+','+spin14+','+spin15+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
				# Sous windows, le répertoire (crée pour l'occasion) et contenant
				# le fichier fire2.gmic est éliminé pour laisser l'arborescence de
				# windows propre.
				if os.name == 'nt': shutil.rmtree(self.rep_annexe)

		#--------------------------------------------------------
		# Filtres utilisant notamment un module python (ex. PIL)
		#--------------------------------------------------------

		elif self.listeComboReglage[i][1]=='vieux_films':
			"""Conversion de la 1ère image en Vieux Film"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerVieuxFilms
			###################################################################
			listePous=[
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_001.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_002.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_003.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_004.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_005.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_006.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_007.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_008.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_009.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_010.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_011.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_012.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_013.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_014.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_015.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_016.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_017.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_018.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_019.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_020.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_021.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_022.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_023.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_024.png',
			'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_025.png', 'masques'+os.sep+'filtre_vf'+os.sep+'poussiere'+os.sep+'pous_026.png']

			os.system(("convert -blur 1%x1% -fx intensity "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.repTampon+"vf_vieux_films1"+"\"").encode(locale.getdefaultlocale()[1]))

			img0=Image.open(self.listeImgSource[0])
			taille=img0.size
			# Pas besoin d'utiliser encode ici.
			os.system("convert "+"\""+listePous[0]+"\""+" -resize "+ str(taille[0])+'x'+str(taille[1])+"! "+"\""+self.repTampon+"vf_vieux_films2"+"\"")
			img1 = Image.open(self.repTampon+"vf_vieux_films2")
			img2 = Image.open(self.repTampon+"vf_vieux_films1")
			compos = Image.composite(img1,img2,img1)
			compos.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='illustration_niveau_gris':
			"""Conversion de la 1ère image en niveaux de gris"""
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.convert("1")
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='traits_fins_et_couleur':
			"""Conversion de la 1ère image en traits fins et couleur"""
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.filter(ImageFilter.EDGE_ENHANCE_MORE)
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='emboss':
			"""Conversion de la 1ère image en emboss"""
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.filter(ImageFilter.EMBOSS)
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='sharpen':
			"""Conversion de la 1ère image en sharpen"""
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.filter(ImageFilter.SHARPEN)
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='niveau_gris':
			"""Conversion de la 1ère image en niveau de gris"""
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.convert("L")
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='amelior_des_bords':
			"""Conversion de la 1ère image en ameliorant les bords"""
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.filter(ImageFilter.Kernel((3, 3), (-1, -2, -1, -2, 16, -2, -1, -2, -1)))
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='debruitage':
			"""Conversion de la 1ère image en debruitant"""
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.filter(ImageFilter.Kernel((5, 5), (2, 4, 5, 4, 2, 4, 9, 12, 9, 4, 5, 12, 15, 12, 5, 4, 9, 12, 9, 4, 2, 4, 5, 4, 2)))
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='evanescence':
			"""Conversion de la 1ère image en Dessin 9: traits noirs, fond blanc"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerEvanescence
			###################################################################
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			obImg = Image.open(self.listeImgSource[0]).convert("L")
			w, h = obImg.size
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'_tmp_g546gf546ezr53ww7i.png', 'PNG')
			ouvImg = Image.open(self.repTampon+'_tmp_g546gf546ezr53ww7i.png')
			egalise = ImageOps.equalize(ouvImg)
			nouvImg = Image.new("L", (w, h))
			nouvImg.putdata(egalise.getdata())
			data = array(nouvImg)
			aplat = data.flat
			condition=(aplat>=1)&(aplat<=255)
			if entreeCombo=='fond_blanc_lignes_noires': idCond = where(condition, 255, 0)
			elif entreeCombo=='fond_noir_lignes_blanches': idCond = where(condition, 0, 255)
			nouvImgBinaire=Image.new("L", (w, h))
			nouvImgBinaire.putdata(idCond.tolist())
			nouvImgBinaire.save(self.cheminCourantSauv)
			os.remove(self.repTampon+'_tmp_g546gf546ezr53ww7i.png')

		elif self.listeComboReglage[i][1]=='seuillage':
			"""Conversion de la 1ère image en Dessin 8: seuillage"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerSeuillage
			###################################################################
			obImg = Image.open(self.listeImgSource[0])
			spin1 = self.listeComboReglage[i][3].spin1.value() # seuil bas
			spin2 = self.listeComboReglage[i][3].spin2.value() # seuil haut
			if spin1>=spin2:
				erreur=QMessageBox(self)
				erreur.setText(_(u"Attention, <b>la valeur de seuillage bas doit obligatoirement être inférieure à la valeur de seuillage haut</b>. La conversion demandée ne sera pas effectuée. Refaites vos réglages correctement et recommencez l'opération."))
				erreur.setWindowTitle(_(u"Erreur de réglage"))
				erreur.setIcon(QMessageBox.Warning)
				erreur.exec_()
				sys.exit
			else: pass
			imageNDG = obImg.convert("L")
			wSeuil, hSeuil = imageNDG.size
			egaliseNDG_Seuil = ImageOps.equalize(imageNDG)
			nouvImgNDG_Seuil = Image.new("L", (wSeuil, hSeuil))
			nouvImgNDG_Seuil.putdata(egaliseNDG_Seuil.getdata())
			dataNDG_Seuil=array(nouvImgNDG_Seuil)
			aplatNDG_Seuil=dataNDG_Seuil.flat
			condSeuil=(aplatNDG_Seuil>=spin1)&(aplatNDG_Seuil<=spin2)
			idSeuil=where(condSeuil, 0, 255)
			nouvImgBinaire=Image.new("L", (wSeuil, hSeuil))
			nouvImgBinaire.putdata(idSeuil.tolist())
			nouvImgBinaire.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='imitation_bd_1':
			"""Conversion de la 1ère image en Dessin 10: imitation bande dessinée"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerImitationBd
			###################################################################
			spin1 = self.listeComboReglage[i][3].spin1.value() # intensité des traits
			spin2 = self.listeComboReglage[i][3].spin2.value() # réduction des couleurs
			spin3 = self.listeComboReglage[i][3].spin3.value() # contraste de couleurs
			obImg = Image.open(self.listeImgSource[0]).convert("L")
			w, h = obImg.size
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, spin1, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png', 'PNG')
			ouvImg = Image.open(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png')
			egalise = ImageOps.equalize(ouvImg)
			nouvImg = Image.new("L", (w, h))
			nouvImg.putdata(egalise.getdata())
			data = array(nouvImg)
			aplat = data.flat
			condition = (aplat>=1)&(aplat<=255)
			idCond = where(condition, 255, 0)
			nouvImgBinaire = Image.new("L", (w, h))
			nouvImgBinaire.putdata(idCond.tolist())
			listeAlpha_1=list(nouvImgBinaire.getdata())
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				else: newListRGBAbin.append((0, 0, 0, 255))
			nouvImgRGBA=Image.new("RGBA", (w, h))
			nouvImgRGBA.putdata(newListRGBAbin)
			nouvImgRGBA.save(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png', 'PNG')
			spin3=float(spin3/10.0)
			imPrinc=Image.open(self.listeImgSource[0])
			imPosterize=ImageOps.posterize(imPrinc, spin2)
			imPosterize.convert('RGBA')
			imPosterize.save(self.repTampon+'tmp_gds89gfdt39xfg6d9qxx1f.png', 'PNG')
			imPostTraitC=Image.open(self.repTampon+'tmp_gds89gfdt39xfg6d9qxx1f.png')
			imContraste=ImageEnhance.Contrast(imPostTraitC)
			imContraste.enhance(spin3).save(self.repTampon+'tmp_gds486fsf68q2wx5k7u1oop.png', 'PNG')
			imOpc=Image.open(self.repTampon+'tmp_gds486fsf68q2wx5k7u1oop.png')
			imOpc.convert('RGBA')
			imFondTransp=Image.open(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png')
			compoContCoul=Image.composite(imFondTransp, imOpc, imFondTransp)
			compoContCoul.save(self.cheminCourantSauv)
			os.remove(self.repTampon+'tmp_gds568ec4u5hg53g7s9m4rt.png')
			os.remove(self.repTampon+'tmp_gds89gfdt39xfg6d9qxx1f.png')
			os.remove(self.repTampon+'tmp_gds486fsf68q2wx5k7u1oop.png')

		elif self.listeComboReglage[i][1]=='negatif':
			"""Conversion de la 1ère image en Negatif: inverse les couleurs"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerNegatif
			###################################################################
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			obImg = Image.open(self.listeImgSource[0])
			if entreeCombo=='negatif_couleur':
				negatif = ImageOps.invert(obImg)
			elif entreeCombo=='negatif_n_et_b':
				obImg = obImg.convert("L")
				negatif = ImageOps.invert(obImg)
			negatif.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='encadre_photo':
			"""Conversion de la 1ère image en Encadrement photographique"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerEncadrePhoto
			###################################################################
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			obImg = Image.open(self.listeImgSource[0])
			if entreeCombo=='noir': couleur = (0, 0, 0)
			elif entreeCombo=='gris': couleur = (128, 128, 128)
			elif entreeCombo=='blanc': couleur = (255, 255, 255)
			elif entreeCombo=='rouge': couleur = (255, 0, 0)
			elif entreeCombo=='vert': couleur = (0, 255, 0)
			elif entreeCombo=='bleu': couleur = (0, 0, 255)
			elif entreeCombo=='jaune': couleur = (255, 255, 0)
			cadre = ImageOps.expand(obImg, 40, couleur)
			cadre.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='couleurs_predefinies':
			"""Conversion de la 1ère image en Couleurs Prédéfinies"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerCouleursPredef
			###################################################################
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			if entreeCombo=="rouge_vif":
				couleur_Img_Predef=(
				1.0, 0.3, 0.0, 0,
				0.0, 0.0, 0.0, 0,
				0.0, 0.0, 0.0, 0)
			elif entreeCombo=="rouge_primaire":
				couleur_Img_Predef=(
				1.0, 0.3, 0.0, 0,
				0.0, 0.0, 0.0, 0,
				0.7, 0.0, 0.0, 0)
			elif entreeCombo=="vert_perroquet":
				couleur_Img_Predef=(
				0.0, 0.0, 0.0, 0,
				1.0, 0.3, 0.0, 0,
				0.0, 0.0, 0.0, 0)
			elif entreeCombo=="vert_acide_clair":
				couleur_Img_Predef=(
				1.0, 0.0, 0.0, 0,
				1.0, 0.3, 0.0, 0,
				0.0, 0.0, 0.0, 0)
			elif entreeCombo=="bleu_roi":
				couleur_Img_Predef=(
				0.0, 0.0, 0.0, 0,
				1.0, 0.0, 0.0, 0,
				1.0, 1.0, 0.0, 0)
			elif entreeCombo=="bleu_indigo":
				couleur_Img_Predef=(
				1.0, 0.0, 0.0, 0,
				1.0, 0.0, 0.0, 0,
				1.0, 1.0, 0.0, 0)
			elif entreeCombo=="bleu_turquoise":
				couleur_Img_Predef=(
				1.0, 0.0, 0.0, 0,
				1.0, 1.0, 0.0, 0,
				1.0, 1.0, 0.0, 0)
			elif entreeCombo=="jaune_or":
				couleur_Img_Predef=(
				0.64, 0.64, 0.10, 0,
				0.56, 0.56, 0.10, 0,
				0.0, 0.0, 0.0, 0)
			elif entreeCombo=="jaune_orange":
				couleur_Img_Predef=(
				1.0, 0.5, 0.5, 0,
				1.0, 0.3, 0.0, 0,
				0.0, 0.0, 0.0, 0)
			elif entreeCombo=="saumon":
				couleur_Img_Predef=(
				1.0, 0.5, 0.0, 0,
				1.0, 0.1, 0.0, 0,
				1.0, 0.0, 0.0, 0)
			elif entreeCombo=="marron_tres_clair":
				couleur_Img_Predef=(
				0.95, 0.38, 0.0, 0,
				0.90, 0.15, 0.0, 0,
				0.48, 0.26, 0.0, 0)
			elif entreeCombo=="terre argileuse":
				couleur_Img_Predef=(
				0.96, 0.58, 0.0, 0,
				0.56, 0.44, 0.0, 0,
				0.46, 0.32, 0.0, 0)
			elif entreeCombo=="gris_colore_rouge":
				couleur_Img_Predef=(
				0.68, 0.68, 0.0, 0,
				0.50, 0.50, 0.0, 0,
				0.50, 0.50, 0.0, 0)
			elif entreeCombo=="gris_colore_vert":
				couleur_Img_Predef=(
				0.50, 0.50, 0.0, 0,
				0.62, 0.62, 0.0, 0,
				0.50, 0.50, 0.0, 0)
			elif entreeCombo=="gris_colore_bleu":
				couleur_Img_Predef=(
				0.50, 0.50, 0.0, 0,
				0.50, 0.50, 0.0, 0,
				0.64, 0.64, 0.0, 0)
			elif entreeCombo=="gris_colore_jaune":
				couleur_Img_Predef=(
				0.62, 0.62, 0.0, 0,
				0.62, 0.62, 0.0, 0,
				0.50, 0.50, 0.0, 0)
			obImg = Image.open(self.listeImgSource[0])
			convert = obImg.convert("RGB").convert("RGB", couleur_Img_Predef)
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='couleurs_personnalisees':
			"""Conversion de la 1ère image en Couleurs Personnalisees"""
			listeCouleurImgPerso=[]
			for k in range(3):
				for l in range(3):
					listeCouleurImgPerso.append(float('0.'+str(self.listeComboReglage[i][3].spin[k][l].value())))
				listeCouleurImgPerso.append(0)
			#print listeCouleurImgPerso
			EkdPrint(u"%s" % listeCouleurImgPerso)
			obImg=Image.open(self.listeImgSource[0])
			convert = obImg.convert("RGB").convert("RGB", listeCouleurImgPerso)
			convert.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='separ_en_modules':
			"""Conversion de la 1ère image en Séparation et modules"""
			spin1 = self.listeComboReglage[i][3].spin1.value()
			spin2 = self.listeComboReglage[i][3].spin2.value()
			if spin1>=spin2:
				erreur=QMessageBox(self)
				erreur.setText(_(u"Attention, <b>la valeur de taille mini de la forme ne doit jamais être supérieure ou égale à la valeur de la taille maxi de la forme</b>. La conversion demandée ne sera pas effectuée. Refaites vos réglages correctement et recommencez l'opération."))
				erreur.setWindowTitle(_(u"Erreur de réglage"))
				erreur.setIcon(QMessageBox.Warning)
				erreur.exec_()
				sys.exit
			else:
				try:
					obImg=Image.open(self.listeImgSource[0])
					width, height=obImg.size
					drawImage = ImageDraw.Draw(obImg)
					pixels = list(obImg.getdata())
					# Travail avec les pixels
					for y in range(0, height, spin1):
						yp = y * width
						for x in range(0, width, spin1):
							xyp = yp + x
							p = pixels[xyp]
							rndSize = random.randint(spin1, spin2)
							x1 = x - rndSize
							y1 = y - rndSize
							x2 = x + rndSize
							y2 = y + rndSize
							drawImage.rectangle((x1, y1, x2, y2), fill=p, outline=(0,0,0))
					obImg.save(self.cheminCourantSauv)

				except:
					erreur=QMessageBox(self)
					erreur.setText(_(u"<p>EKD ne peut pas travailler avec les images dont le mode est <b>L</b> (il s'agit d'images en niveaux de gris), <b>P</b> (images GIF). Vérifiez le mode de l'image que vous avez sélectionné (et ce dans l'onglet <b>Image(s) source</b>), pour ce faire cliquez sur le bouton <b>Infos</b> (dans la fenêtre qui s'ouvre, l'image fautive devrait avoir soit <b>L</b> ou soit <b>P</b> indiqué en face du champ <b>Mode</b>). Eliminez cette image (par le bouton <b>Retirer</b>) et relancez la visualisation en sélectionnant une autre image (et ensuite en cliquant sur <b>Voir le résultat</b>).</p>"))
					erreur.setWindowTitle(_(u"Erreur"))
					erreur.setIcon(QMessageBox.Critical)
					erreur.exec_()
					return 0

		elif self.listeComboReglage[i][1]=='omb_lum_a_la_coul':
			"""Conversion de la 1ère image en Ombre et lumière à la couleur"""
			ll=[]
			for k in range(4):
				for l in range(2):
					ll.append(self.listeComboReglage[i][3].spin[k][l].value())
			self.lValCoul=[ll[0], ll[2], ll[4], ll[6], ll[1], ll[3], ll[5], ll[7]]
			obImg=Image.open(self.listeImgSource[0])
			imageNDG = obImg.convert("L")
			wSeuil, hSeuil = imageNDG.size
			egaliseNDG_Seuil = ImageOps.equalize(imageNDG)
			nouvImgNDG_Seuil = Image.new("L", (wSeuil, hSeuil))
			nouvImgNDG_Seuil.putdata(egaliseNDG_Seuil.getdata())
			dataNDG_Seuil=array(nouvImgNDG_Seuil)
			aplatNDG_Seuil=dataNDG_Seuil.flat
			condSeuil=(aplatNDG_Seuil>=128)&(aplatNDG_Seuil<=255)
			idSeuil=where(condSeuil, 0, 255)
			transListe=idSeuil.tolist()
			quatreCanaux=[[parcTrans]*4 for parcTrans in transListe]
			transTuple=[tuple(parcTuple) for parcTuple in quatreCanaux]
			listeDonnees=[]
			for parcDonnees in transTuple:
				if parcDonnees==(255, 255, 255, 255):
					parcDonnees=(self.lValCoul[0], self.lValCoul[1], self.lValCoul[2], self.lValCoul[3])
					listeDonnees.append(parcDonnees)
				elif parcDonnees==(0, 0, 0, 0):
					parcDonnees=(self.lValCoul[4], self.lValCoul[5], self.lValCoul[6], self.lValCoul[7])
					listeDonnees.append(parcDonnees)
			nouvImg=Image.new("RGBA", (wSeuil, hSeuil))
			nouvImg.putdata(listeDonnees)
			nouvImg.save(self.cheminCourantSauv)

		elif self.listeComboReglage[i][1]=='rotation_image':
			# Récupération de l'index et l'entrée du combo de sélection
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			# Ouverture de l'image
			obImg = Image.open(self.listeImgSource[0])
			#
			if entreeCombo=='rot_img_90_gauche': rot = 90
			elif entreeCombo=='rot_img_180_gauche': rot = 180
			elif entreeCombo=='rot_img_270_gauche': rot = 270
			# Application du filtre
			obImg.rotate(rot).save(self.cheminCourantSauv)
		
		elif self.listeComboReglage[i][1]=='imitation_bd_2':
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerImitationBd
			###################################################################
			spin1 = self.listeComboReglage[i][3].spin.value() # intensité des traits
			spin2 = str(self.listeComboReglage[i][3].spin2.value()) # flou des couleurs
		
			os.system(("convert -noise "+spin2+" -gamma 1.4 "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.repTampon+'tmp_colf84dv556tdf65gu.png'+"\"").encode(locale.getdefaultlocale()[1]))
			
			obImg = Image.open(self.listeImgSource[0]).convert("L")
			w, h = obImg.size
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, spin1, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_tfgt6gr99yc9terff4.png', 'PNG')
			ouvImg = Image.open(self.repTampon+'tmp_tfgt6gr99yc9terff4.png')
			egalise = ImageOps.equalize(ouvImg)
			nouvImg = Image.new("L", (w, h))
			nouvImg.putdata(egalise.getdata())
			data = array(nouvImg)
			aplat = data.flat
			condition = (aplat>=1)&(aplat<=255)
			idCond = where(condition, 255, 0)
			nouvImgBinaire = Image.new("L", (w, h))
			nouvImgBinaire.putdata(idCond.tolist())
			listeAlpha_1=list(nouvImgBinaire.getdata())
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				else: newListRGBAbin.append((0, 0, 0, 255))
			nouvImgRGBA=Image.new("RGBA", (w, h))
			nouvImgRGBA.putdata(newListRGBAbin)
			nouvImgRGBA.save(self.repTampon+'tmp_tfgt6gr99yc9terff4.png', 'PNG')
			
			imOpc=Image.open(self.repTampon+'tmp_colf84dv556tdf65gu.png')
			imOpc.convert('RGBA')
			imFondTransp=Image.open(self.repTampon+'tmp_tfgt6gr99yc9terff4.png')
			compoContCoul=Image.composite(imFondTransp, imOpc, imFondTransp)
			compoContCoul.save(self.cheminCourantSauv)
			os.remove(self.repTampon+'tmp_colf84dv556tdf65gu.png')
			os.remove(self.repTampon+'tmp_tfgt6gr99yc9terff4.png')

		elif self.listeComboReglage[i][1]=='laplacien_1':
			# Récupération de l'index et l'entrée du combo de sélection
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			# Ouverture de l'image avec conditions
			if entreeCombo=="laplacien_1_noir_et_blanc":
				obImg = Image.open(self.listeImgSource[0]).convert('L')
			elif entreeCombo=="laplacien_1_couleur":
				obImg = Image.open(self.listeImgSource[0]).convert('RGB')
			sizeKern5x5=(5, 5)
			kernLaplacien_1 = (-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 24, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1)
			imKernelLaplacien_1 = obImg.filter(ImageFilter.Kernel(sizeKern5x5, kernLaplacien_1)).save(self.cheminCourantSauv)
			
		elif self.listeComboReglage[i][1]=='contour_et_couleur':
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerContourEtCouleur
			###################################################################
			# Partie trait/contour
			###################################################################
			coul_rouge_trait = self.listeComboReglage[i][3].spin[0][2].value() # rouge
			coul_vert_trait = self.listeComboReglage[i][3].spin[1][2].value() # vert
			coul_bleu_trait = self.listeComboReglage[i][3].spin[2][2].value() # bleu
			transparence_trait = self.listeComboReglage[i][3].spin[3][2].value() # transparence
			# Valeur de l'intensité du trait
			val_intens_trait = self.listeComboReglage[i][3].spin[len(self.listeComboReglage[i][3].spin)-1].value()

			obImg = Image.open(self.listeImgSource[0]).convert("L")
			w, h = obImg.size
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, val_intens_trait, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_gdf5t4n158w61816qf78f5fd599q.png', 'PNG')
			ouvImg = Image.open(self.repTampon+'tmp_gdf5t4n158w61816qf78f5fd599q.png')
			egalise = ImageOps.equalize(ouvImg)
			nouvImg = Image.new("L", (w, h))
			nouvImg.putdata(egalise.getdata())
			data = array(nouvImg)
			aplat = data.flat
			condition = (aplat>=1)&(aplat<=255)
			idCond = where(condition, 255, 0)
			nouvImgBinaire = Image.new("L", (w, h))
			nouvImgBinaire.putdata(idCond.tolist())
			listeAlpha_1=list(nouvImgBinaire.getdata())
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				else: newListRGBAbin.append((coul_rouge_trait, coul_vert_trait, coul_bleu_trait, transparence_trait))
			nouvImgRGBA=Image.new("RGBA", (w, h))
			nouvImgRGBA.putdata(newListRGBAbin)
			nouvImgRGBA.save(self.repTampon+'tmp_gdf5t4n158w61816qf78f5fd599q.png', 'PNG')
			###################################################################
			# Partie couleur (ombre et lumière)
			###################################################################
			ll=[]
			for k in range(4):
				for l in range(2):
					ll.append(self.listeComboReglage[i][3].spin[k][l].value())
			self.lValCoul=[ll[0], ll[2], ll[4], ll[6], ll[1], ll[3], ll[5], ll[7]]
			obImg=Image.open(self.listeImgSource[0])
			imageNDG = obImg.convert("L")
			wSeuil, hSeuil = imageNDG.size
			egaliseNDG_Seuil = ImageOps.equalize(imageNDG)
			nouvImgNDG_Seuil = Image.new("L", (wSeuil, hSeuil))
			nouvImgNDG_Seuil.putdata(egaliseNDG_Seuil.getdata())
			dataNDG_Seuil=array(nouvImgNDG_Seuil)
			aplatNDG_Seuil=dataNDG_Seuil.flat
			condSeuil=(aplatNDG_Seuil>=128)&(aplatNDG_Seuil<=255)
			idSeuil=where(condSeuil, 0, 255)
			transListe=idSeuil.tolist()
			quatreCanaux=[[parcTrans]*4 for parcTrans in transListe]
			transTuple=[tuple(parcTuple) for parcTuple in quatreCanaux]
			listeDonnees=[]
			for parcDonnees in transTuple:
				if parcDonnees==(255, 255, 255, 255):
					parcDonnees=(self.lValCoul[0], self.lValCoul[1], self.lValCoul[2], self.lValCoul[3])
					listeDonnees.append(parcDonnees)
				elif parcDonnees==(0, 0, 0, 0):
					parcDonnees=(self.lValCoul[4], self.lValCoul[5], self.lValCoul[6], self.lValCoul[7])
					listeDonnees.append(parcDonnees)
			nouvImg=Image.new("RGBA", (wSeuil, hSeuil))
			nouvImg.putdata(listeDonnees)
			#nouvImg.save(self.cheminCourantSauv)
			nouvImg.save(self.repTampon+'tmp_gdfg586re65fg86r68efez8erz535.png', 'PNG')
			##################################################
			# Compositing
			##################################################
			imFondTransp=Image.open(self.repTampon+'tmp_gdf5t4n158w61816qf78f5fd599q.png')
			compoContCoul=Image.composite(imFondTransp, nouvImg, imFondTransp)
			compoContCoul.save(self.cheminCourantSauv)
			os.remove(self.repTampon+'tmp_gdf5t4n158w61816qf78f5fd599q.png')
			os.remove(self.repTampon+'tmp_gdfg586re65fg86r68efez8erz535.png')
			##################################################
			
		# Filtre utilisant notamment un module python (ex. PIL) et une commande G'MIC.
		# Ce filtre est un mélange de Couleurs prédéfinies, Dessin 13: en couleur et
		# Réduction du bruit (débruitage)
		elif self.listeComboReglage[i][1]=='peintur_degrade_de_coul':
			"""Conversion de la 1ère image en Peinture monochrome en dégradé"""
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerPeinturDegradDeCouleur
			###################################################################
			# Partie --> Couleurs prédéfinies
			indexCombo = self.listeComboReglage[i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[i][3].combo.itemData(indexCombo).toStringList()[0])
			if entreeCombo=="bleu_roi":
				coul_Img_PeintDegCoul=(
				0.0, 0.0, 0.0, 0,
				1.0, 0.0, 0.0, 0,
				1.0, 1.0, 0.0, 0)
			elif entreeCombo=="bleu_indigo":
				coul_Img_PeintDegCoul=(
				1.0, 0.0, 0.0, 0,
				1.0, 0.0, 0.0, 0,
				1.0, 1.0, 0.0, 0)
			elif entreeCombo=="jaune_or":
				coul_Img_PeintDegCoul=(
				0.64, 0.64, 0.10, 0,
				0.56, 0.56, 0.10, 0,
				0.0, 0.0, 0.0, 0)
			elif entreeCombo=="jaune_orange":
				coul_Img_PeintDegCoul=(
				1.0, 0.5, 0.5, 0,
				1.0, 0.3, 0.0, 0,
				0.0, 0.0, 0.0, 0)
			elif entreeCombo=="saumon":
				coul_Img_PeintDegCoul=(
				1.0, 0.5, 0.0, 0,
				1.0, 0.1, 0.0, 0,
				1.0, 0.0, 0.0, 0)
			elif entreeCombo=="marron_tres_clair":
				coul_Img_PeintDegCoul=(
				0.95, 0.38, 0.0, 0,
				0.90, 0.15, 0.0, 0,
				0.48, 0.26, 0.0, 0)
			elif entreeCombo=="terre argileuse":
				coul_Img_PeintDegCoul=(
				0.96, 0.58, 0.0, 0,
				0.56, 0.44, 0.0, 0,
				0.46, 0.32, 0.0, 0)
			obImg_1 = Image.open(self.listeImgSource[0])
			convert = obImg_1.convert("RGB").convert("RGB", coul_Img_PeintDegCoul)
			convert.save(self.repTampon+'tmp_gf457rxwf510ht75hl4gs7tyt3xww7e.png', 'PNG')
			# Partie --> Dessin 13: en couleur
			os.system(("gmic "+"\\\""+self.repTampon+'tmp_gf457rxwf510ht75hl4gs7tyt3xww7e.png'+"\\\""+" -drawing 6288 -o "+"\\\""+self.repTampon+'tmp_fkkkl541ry87v165rv7f3iu8r9cfdjj147y5.png'+"\\\"").encode(locale.getdefaultlocale()[1]))
			# Partie --> Réduction du bruit (débruitage)
			obImg_2 = Image.open(self.repTampon+'tmp_fkkkl541ry87v165rv7f3iu8r9cfdjj147y5.png')
			convert = obImg_2.filter(ImageFilter.Kernel((5, 5), (2, 4, 5, 4, 2, 4, 9, 12, 9, 4, 5, 12, 15, 12, 5, 4, 9, 12, 9, 4, 2, 4, 5, 4, 2)))
			convert.save(self.cheminCourantSauv)
			os.remove(self.repTampon+'tmp_gf457rxwf510ht75hl4gs7tyt3xww7e.png')
			os.remove(self.repTampon+'tmp_fkkkl541ry87v165rv7f3iu8r9cfdjj147y5.png')
		
		# Filtre utilisant notamment un module python (ex. PIL et Numpy) et quatre 
		# commandes G'MIC. Ce filtre est un mélange de Dessin 11: imitation bande 
		# dessinée 2 et (G'MIC): Gimp painting + Segmentation + Shadow patch 
		# + Fuzzy frame
		elif self.listeComboReglage[i][1]=='peinture_aquarelle_1':
			###################################################################
			# Les commentaires n'ont pas été gardés ici, pour savoir de quoi
			# il en retourne voir dans la fonction appliquerPeintAquarelle
			###################################################################
			# Pour Figuration libre:
			# --------------------------------
			# spin1 --> Intensité des traits
			# spin2 --> Flou des couleurs
			# spin3 --> Amplitude
			# spin4 --> Abstraction
			# spin5 --> Douceur de la peinture
			# spin6 --> Couleur
			# spin7 --> Seuil du bord (segmentation)
			# spin8 --> Douceur de la segmentation
			# spin9 --> Opacité de l'ombre
			# spin10 --> Taille bordure horizontale
			# spin11 --> Taille bordure verticale
			# spin12 --> Distorsion de la bordure
			# spin13 --> Douceur de la bordure
			#################################################
			spin1 = self.listeComboReglage[i][3].spin.value()
			spin2 = str(self.listeComboReglage[i][3].spin2.value())
			spin3 = self.listeComboReglage[i][3].spin3.value()
			spin3 = str(spin3/100)
			spin4 = str(self.listeComboReglage[i][3].spin4.value())
			spin5 = self.listeComboReglage[i][3].spin5.value()
			spin5 = str(spin5/100)
			spin6 = self.listeComboReglage[i][3].spin6.value()
			spin6 = str(spin6/100)
			spin7 = self.listeComboReglage[i][3].spin7.value()
			spin7 = str(spin7/100)
			spin8 = self.listeComboReglage[i][3].spin8.value()
			spin8 = str(spin8/100)
			spin9 = self.listeComboReglage[i][3].spin9.value()
			spin9 = str(spin9/100)
			spin10 = str(self.listeComboReglage[i][3].spin10.value())
			spin11 = str(self.listeComboReglage[i][3].spin11.value())
			spin12 = str(self.listeComboReglage[i][3].spin12.value())
			spin13 = str(self.listeComboReglage[i][3].spin13.value())
		
			# Partie --> Dessin 11: imitation bande dessinée 2
		
			os.system(("convert -noise "+spin2+" -gamma 1.4 "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.repTampon+'tmp_f54rt2hk47125ghlt7f25fer147y7y6df.png'+"\"").encode(locale.getdefaultlocale()[1]))
			
			obImg = Image.open(self.listeImgSource[0]).convert("L")
			w, h = obImg.size
			imKernel = obImg.filter(ImageFilter.Kernel((5, 5), (-2, -2, -2, -2, -2, -1, -1, 0, 0, 0, 0, 0, spin1, 0, 0, 0, 0, 0, -1, -1, -2, -2, -2, -2, -2)))
			imKernel.save(self.repTampon+'tmp_f48era57ezerc4w4aqe711dd6o4db169p.png', 'PNG')
			ouvImg = Image.open(self.repTampon+'tmp_f48era57ezerc4w4aqe711dd6o4db169p.png')
			egalise = ImageOps.equalize(ouvImg)
			nouvImg = Image.new("L", (w, h))
			nouvImg.putdata(egalise.getdata())
			data = array(nouvImg)
			aplat = data.flat
			condition = (aplat>=1)&(aplat<=255)
			idCond = where(condition, 255, 0)
			nouvImgBinaire = Image.new("L", (w, h))
			nouvImgBinaire.putdata(idCond.tolist())
			listeAlpha_1=list(nouvImgBinaire.getdata())
			newListRGBAbin=[]
			for parcListe in listeAlpha_1:
				if parcListe==255: newListRGBAbin.append((255, 255, 255, 0))
				else: newListRGBAbin.append((0, 0, 0, 255))
			nouvImgRGBA=Image.new("RGBA", (w, h))
			nouvImgRGBA.putdata(newListRGBAbin)
			nouvImgRGBA.save(self.repTampon+'tmp_f48era57ezerc4w4aqe711dd6o4db169p.png', 'PNG')
			
			imOpc=Image.open(self.repTampon+'tmp_f54rt2hk47125ghlt7f25fer147y7y6df.png')
			imOpc.convert('RGBA')
			imFondTransp=Image.open(self.repTampon+'tmp_f48era57ezerc4w4aqe711dd6o4db169p.png')
			compoContCoul=Image.composite(imFondTransp, imOpc, imFondTransp)
			compoContCoul.save(self.repTampon+'tmp_g57fa5f6ez65r9o5k14z663fde1456dl.png', 'PNG')
			
			# Partie --> G'MIC ==> Gimp painting + Segmentation + Shadow patch + Fuzzy frame
			
			os.system(("gmic "+"\\\""+self.repTampon+'tmp_g57fa5f6ez65r9o5k14z663fde1456dl.png'+"\\\""+"  -drawing  "+spin3+" -gimp_painting "+spin4+','+spin5+','+spin6+" -gimp_segment_watershed_preview "+spin7+','+spin8+',0,0'+" -gimp_shadow_patch "+spin9+",0"+" -gimp_frame_fuzzy "+spin10+','+spin11+','+spin12+','+spin13+",255,255,255,255 "+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
			
			os.remove(self.repTampon+'tmp_f54rt2hk47125ghlt7f25fer147y7y6df.png')
			os.remove(self.repTampon+'tmp_f48era57ezerc4w4aqe711dd6o4db169p.png')
			os.remove(self.repTampon+'tmp_g57fa5f6ez65r9o5k14z663fde1456dl.png')
			
			
		# Affichage de l'image temporaire dans l'onglet
		# Images après traitement
		#
		# Ouverture d'une boite de dialogue affichant l'aperçu.

		# Affichage par le bouton Voir le résultat
		visio = VisionneurEvolue(self.cheminCourantSauv)
		visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
		visio.exec_()

		return 0


	def appliquer0(self):
		"""Préparation de la conversion"""

		self.listeImgSource=self.afficheurImgSource.getFiles()

		# Onglet de log
		self.zoneAffichInfosImg.setText(self.infosImgTitre[0]+"\n".join(self.listeImgSource))

		# Redimensionner les images de tailles différentes
		self.redim_img()

		# Utilisation de la nouvelle boîte de dialogue de sauvegarde
		suffix=""
                self.cheminSauv = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		self.cheminSauv = self.cheminSauv.getFile()

		if not self.cheminSauv: return

		#print 'Chemin+nom de sauvegarde:', self.cheminSauv

		# Condition à respecter pour qu'une redimension ait lieu
		self.conversionImg = 0

		# Liste des fichiers de destination
		self.listeImgDestin = []

		# Extension/format des images
		self.ext = os.path.splitext(self.listeImgSource[0])[1].encode("UTF8")

		# Liste des indices des images [0,1,2,...,nombre d'images-1]
		self.listeIndex = range(len(self.listeImgSource))

		# Nombre d'images sources
		self.nbrImg = len(self.listeImgSource)

		# Récupération de l'identifiant du codec
		self.i = self.comboReglage.currentIndex()

		# Indice de l'image à convertir
		self.j = 0

		# Drapeau (réinitialisation): terminer le filtre avec commande 100% shell
		self.terminerFiltreShell = 0

		self.progress.reset() # wasCanceled est remis à 0 -> la conversion ne s'arrête pas à la 1ère img
		self.progress.show()
		self.progress.setValue(0)
		QApplication.processEvents()

		# Faire en sorte que la boite de dialogue ait le temps de s'afficher correctement
		QTimer.singleShot(0, self.appliquer)


	def appliquer(self):
		"""Conversion des images"""

		# L'incrémentation de l'indice de l'image source se fait dans cette fonction si le 
		# filtre est choisi
		# contient un moteur module python, ou dans opReccurApresApp() pour 1 filtre 100% 
		# commande shell

		# Sauvegarde
		self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext

		#------------------------------
		# Filtres 100% commande shell
		#------------------------------
		
		# Mise en place de conditions pour linux et windows
		# Attention dans la version windows ce n'est pas traité par un QProcess (comme sous
		# Linux) mais directement avec os.system (car le QProcess avec la commande convert
		# d'ImageMagick génère une erreur)
		
		# Sous windows process.start(...) est désactivé car cela ne fonctionne pas avec les 
		# commandes ImageMagick, os.system(...) est utilisé à la place. Changement du code pour
                # s'accorder avec os.system(...)
		
		# Le code est plus long que dans la version Linux --> la boucle a été rajoutée ds 
		# chaque choix pour les filtres dépendant d'ImageMagick.

		if self.listeComboReglage[self.i][1] in ['sepia','traits_noirs','peu_couleur','peinture_huile',\
					'gamma','fonce_clair','peinture_eau','bas_relief']:
			
			spin = str(self.listeComboReglage[self.i][3].spin.value())
			
			if self.listeComboReglage[self.i][1]=='sepia':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -sepia-tone "+spin+"% "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -sepia-tone "+spin+"% "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
						
			elif self.listeComboReglage[self.i][1]=='traits_noirs':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -charcoal "+spin+" -monochrome "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -charcoal "+spin+" -monochrome "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
					
			elif self.listeComboReglage[self.i][1]=='peu_couleur':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -enhance -equalize -edge "+spin+" -colorize 6,12,20 "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -enhance -equalize -edge "+spin+" -colorize 6,12,20 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
						
			elif self.listeComboReglage[self.i][1]=='peinture_huile':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -paint "+spin+" \""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -paint "+spin+' '+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
					
			elif self.listeComboReglage[self.i][1]=='gamma':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -gamma "+spin+" \""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -gamma "+spin+' '+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
				
			elif self.listeComboReglage[self.i][1]=='fonce_clair':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -modulate "+spin+" \""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -modulate "+spin+" \""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
				
			elif self.listeComboReglage[self.i][1]=='peinture_eau':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -noise "+spin+" -gamma 1.4 "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -noise "+spin+" -gamma 1.4 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
				
			elif self.listeComboReglage[self.i][1]=='bas_relief':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -paint "+spin+" -shade 120x45 "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -paint "+spin+" -shade 120x45 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1] in ['crayon_papier','floutage','trait_couleur_fond_noir']:
			
			spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
			spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
			
			if self.listeComboReglage[self.i][1]=='crayon_papier':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -spread "+spin2+" -charcoal "+spin1+" \""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -spread "+spin2+" -charcoal "+spin1+' '+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
					
			elif self.listeComboReglage[self.i][1]=='floutage':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -blur "+spin1+'%'+'x'+spin2+"% "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -blur "+spin1+'%'+'x'+spin2+"% "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return
					
			elif self.listeComboReglage[self.i][1]=='trait_couleur_fond_noir':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					self.process.start("convert -median "+spin1+" -edge "+spin2+" \""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system("convert -median "+spin1+" -edge "+spin2+' '+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
						if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='monochrome':
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				self.process.start("convert -monochrome "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
			# Uniquement pour windows
			elif os.name == 'nt':
				for self.j in self.listeIndex:
					self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
					os.system("convert -monochrome "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
					if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='pointillisme':
			
			indexCombo = self.listeComboReglage[self.i][3].combo.currentIndex()
			entreeCombo = str(self.listeComboReglage[self.i][3].combo.itemData(indexCombo).toStringList()[0])
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				self.process.start("convert +noise "+entreeCombo+" "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
			# Uniquement pour windows
			elif os.name == 'nt':
				for self.j in self.listeIndex:
					self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
					os.system("convert +noise "+entreeCombo+' '+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
					if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='craie_blanche':
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				self.process.start("convert -blur 2x2 -fx 'log(r*60*pi)' -edge 0.1 -blur 2x2 "+"\""+self.listeImgSource[self.j]+"\" "+"\""+self.cheminCourantSauv+"\"")
			# Uniquement pour windows
			elif os.name == 'nt':
				for self.j in self.listeIndex:
					self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
					os.system("convert -blur 2x2 -fx 'log(r*60*pi)' -edge 0.1 -blur 2x2 "+"\""+self.listeImgSource[self.j]+"\""+' '+"\""+self.cheminCourantSauv+"\"")
					if not self.opReccurApresApp(): return

		#------------------------------
		# Gestion par G'MIC
		#------------------------------

		# Mise en place de conditions pour linux et windows
		# Attention dans la version windows ce n'est pas traité par un QProcess (comme sous
		# Linux) mais directement avec os.system (pour l'instant, test pas encore fait pour
		# savoir si ça fonctionne bien avec QProcess --> A FAIRE)
		
		# Sous windows process.start(...) est désactivé POUR L'INSTANT, os.system(...) est
		# utilisé à la place.
		
		# Le code est plus long que dans la version Linux --> la boucle a été rajoutée ds 
		# chaque choix pour les filtres dépendant de G'MIC.

		### ATTENTION ######################################################################
		# "\"" a été remplacé par "\\\"" car G'MIC demande une syntaxe du style: 
		# gmic \"mon nom de fichier avec espace.jpg\" ... pour pouvoir traiter des fichiers
		# avec des espaces dans son nom
		####################################################################################

		####################################################################################
		# Momentanément importé (bug d'affichage)
		import locale
		####################################################################################

		if self.listeComboReglage[self.i][1] in ['dessin_13_couleur', 'crayon_papier_2', 'oeilleton', 'polaroid', 'vieille_photo', 'cubisme_analytique', 'andy_warhol', 'expressionnisme', 'correct_yeux_rouges', 'solarisation', 'bull_en_tableau', 'la_planete_1', 'vision_thermique', 'bord_tendu', 'erosion', 'dilatation', 'figuration_libre', 'effet_flamme']:

			if self.listeComboReglage[self.i][1]=='dessin_13_couleur':
				#################################################
				# Pour Dessin 13: couleur:
				# ------------------------
				# spin1 --> Amplitude
				#################################################
				spin1 = self.listeComboReglage[self.i][3].spin1.value()
				spin1 = str(spin1/100)
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -drawing "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -drawing "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -drawing "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='crayon_papier_2':
				#################################################
				# Pour Dessin 14: crayon à papier 2:
				# ----------------------------------
				# spin1 --> Amplitude
				#################################################
				spin1 = self.listeComboReglage[self.i][3].spin1.value()
				spin1 = str(spin1/10)
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -pencilbw "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -pencilbw "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -pencilbw "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='correct_yeux_rouges':
				# Il faut passer par if au lieu de elif ici pour que cela fonctionne bien
				#elif self.listeComboReglage[self.i][1]=='correct_yeux_rouges':
				#################################################
				# Pour Correction des yeux rouges:
				# --------------------------------
				# spin1 --> Seuil des couleurs
				# spin2 --> Lissage
				# spin3 --> Atténuation
				#################################################
				spin1 = self.listeComboReglage[self.i][3].spin1.value()
				# Si spin1 réglé sur 1 en fait spin vaut 0
				if spin1 == 1: spin1 = 0
				# Si la valeur de spin1 est supérieure à 1 on retranche 1
				if spin1 > 1: spin1 = spin1 - 1
				spin1 = str(spin1)
				spin2 = self.listeComboReglage[self.i][3].spin2.value()
				spin2 = str(spin2/10.0)
				spin3 = self.listeComboReglage[self.i][3].spin3.value()
				spin3 = str(spin3/10.0)
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -red_eye "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -red_eye "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -red_eye "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='solarisation':
				# Il faut passer par if au lieu de elif ici pour que cela fonctionne bien
				#elif self.listeComboReglage[self.i][1]=='solarisation':
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -solarize -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -solarize -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -solarize -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='oeilleton':
				#################################################
				# Pour Oeilleton:
				# ---------------
				# spin1 --> Position sur la largeur
				# spin2 --> Position sur la hauteur
				# spin3 --> Rayon
				# spin4 --> Amplitude
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value())
				spin4 = str(self.listeComboReglage[self.i][3].spin4.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -fish_eye "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -fish_eye "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -fish_eye "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='polaroid':
				#################################################
				# Pour Polaroïd:
				# --------------
				# spin1 --> Taille de la bordure
				# spin2 --> Taille en largeur pour l'ombre
				# spin3 --> Taille en hauteur pour l'ombre
				# spin4 --> Rotation (en degrés) de  la photo
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value())
				spin4 = str(self.listeComboReglage[self.i][3].spin4.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -polaroid "+spin1+" -drop_shadow "+spin2+','+spin3+" -rotate "+spin4+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -polaroid "+spin1+" -drop_shadow "+spin2+','+spin3+" -rotate "+spin4+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -polaroid "+spin1+" -drop_shadow "+spin2+','+spin3+" -rotate "+spin4+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='vieille_photo':
				#################################################
				# Pour Vieille photo:
				# -------------------
				# spin1 --> Taille en largeur pour l'ombre
				# spin2 --> Taille en hauteur pour l'ombre
				# spin3 --> Rotation (en degrés) de  la photo
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -old_photo -drop_shadow "+spin1+','+spin2+" -rotate "+spin3+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -old_photo -drop_shadow "+spin1+','+spin2+" -rotate "+spin3+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -old_photo -drop_shadow "+spin1+','+spin2+" -rotate "+spin3+",1 -drgba -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))

			if self.listeComboReglage[self.i][1]=='cubisme_analytique':
				#################################################
				# Pour Cubisme analytique:
				# ------------------------
				# spin1 --> Itération
				# spin2 --> Taille de bloc
				# spin3 --> Angle
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						#self.process = EkdProcess(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -cubism "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]), output = None, stdinput = None)
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -cubism "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -cubism "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -cubism "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='andy_warhol':
				# Il faut passer par if au lieu de elif ici pour que cela fonctionne bien
				#elif self.listeComboReglage[self.i][1]=='andy_warhol':
				#################################################
				# Pour Andy Warhol:
				# -----------------
				# spin1 --> Nombre d'images par ligne
				# spin2 --> Nombre d'images par colonne
				# spin3 --> Lissage
				# spin4 --> Couleur
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value())
				spin4 = str(self.listeComboReglage[self.i][3].spin4.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -warhol "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -warhol "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -warhol "+spin1+','+spin2+','+spin3+','+spin4+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='expressionnisme':
				# Il faut passer par if au lieu de elif ici pour que cela fonctionne bien
				#elif self.listeComboReglage[self.i][1]=='expressionnisme':
				#################################################
				# Pour Expressionnisme:
				# ---------------------
				# spin1 --> Abstraction
				# spin2 --> Lissage
				# spin3 --> Couleur
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = self.listeComboReglage[self.i][3].spin2.value()
				spin2 = str(spin2/100)
				spin3 = self.listeComboReglage[self.i][3].spin3.value()
				spin3 = str(spin3/100)
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -gimp_painting "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -gimp_painting "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -gimp_painting "+spin1+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			if self.listeComboReglage[self.i][1]=='bull_en_tableau':
				# Il faut passer par if au lieu de elif ici pour que cela fonctionne bien
				#elif self.listeComboReglage[self.i][1]=='bull_en_tableau':
				#################################################
				# Pour Bulles en tableau:
				# -----------------------
				# spin1 --> Résolution en X
				# spin2 --> Résolution en Y
				# spin3 --> Rayon de la bulle
				# spin4 --> Bulles par ligne
				# spin5 --> Bulles par colonne
				# spin6 --> Largeur de la bordure
				# spin7 --> Hauteur de la bordure
				# spin8 --> Largeur finale de l'image
				# spin9 --> Hauteur finale de l'image
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value())
				spin4 = str(self.listeComboReglage[self.i][3].spin4.value())
				spin5 = str(self.listeComboReglage[self.i][3].spin5.value())
				spin6 = str(self.listeComboReglage[self.i][3].spin6.value())
				spin7 = str(self.listeComboReglage[self.i][3].spin7.value())
				spin8 = str(self.listeComboReglage[self.i][3].spin8.value())
				spin9 = str(self.listeComboReglage[self.i][3].spin9.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -mirror z -map_sphere "+spin1+','+spin2+','+spin3+" -array_fade "+spin4+','+spin5+" -frame_fuzzy "+spin6+','+spin7+" -resize "+spin8+','+spin9+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -mirror z -map_sphere "+spin1+','+spin2+','+spin3+" -array_fade "+spin4+','+spin5+" -frame_fuzzy "+spin6+','+spin7+" -resize "+spin8+','+spin9+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -mirror z -map_sphere "+spin1+','+spin2+','+spin3+" -array_fade "+spin4+','+spin5+" -frame_fuzzy "+spin6+','+spin7+" -resize "+spin8+','+spin9+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			elif self.listeComboReglage[self.i][1]=='la_planete_1':
				#################################################
				# Pour Bulles en tableau:
				# -----------------------
				# spin1 --> Position des doubles
				# spin2 --> Rayon de la planète
				# spin3 --> Dilatation
				# spin4 --> Largeur finale de l'image
				# spin5 --> Hauteur finale de l'image
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = self.listeComboReglage[self.i][3].spin3.value()
				spin3 = str(spin3/100.0)
				spin4 = str(self.listeComboReglage[self.i][3].spin4.value())
				spin5 = str(self.listeComboReglage[self.i][3].spin5.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -repeat "+spin1+ " --mirror x -a x -done -map_sphere "+spin4+','+spin5+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
					#self.process.start("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -repeat "+spin1+ " --mirror x -a x -done -map_sphere "+spin4+','+spin5+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"")
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -repeat "+spin1+ " --mirror x -a x -done -map_sphere "+spin4+','+spin5+','+spin2+','+spin3+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
						
			########Rajout le 28/11/2010 par LUCAS Thomas et CABANA Antoine###################################
			elif self.listeComboReglage[self.i][1]=='vision_thermique':
				#################################################
				# Pour Vision Thermique :
				# -----------------------
				# spin1 --> Minimum de Luminance
				# spin2 --> Maximum de Luminance
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				'''
				if spin1>=spin2:
					erreur=QMessageBox(self)
					erreur.setText(_(u"Attention, <b>la valeur du mini ne doit jamais être supérieure ou égale à la valeur du maxi de la luminance</b>. L'opération demandée ne sera pas effectuée. Refaites vos réglages correctement et recommencez l'opération."))
					erreur.setWindowTitle(_(u"Erreur de réglage"))
					erreur.setIcon(QMessageBox.Warning)
					erreur.exec_()
					sys.exit
				else :	
					#spin1 = str(self.listeComboReglage[self.i][3].spin1.value()) # Ce réglage est déjà définis plus haut ds le code
					#spin2 = str(self.listeComboReglage[self.i][3].spin2.value()) # Ce réglage est déjà définis plus haut ds le code
				'''
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -luminance -n "+spin1+','+spin2+ " -negative -map 1 -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return		
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex :
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -luminance -n "+spin1+','+spin2+" -negative -map 1 -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					##########################################################################################
					
			elif self.listeComboReglage[self.i][1]=='bord_tendu':
				#################################################
				# Pour Bord tendu:
				# --------------------------------
				# spin1 --> Netteté du trait
				# spin2 --> Fluctuation de couleurs
				# spin3 --> Transparence du trait
				# spin4 --> Floutage
				# spin5 --> Couleurs, début
				# spin6 --> Couleurs, fin
				#################################################
				spin1 = self.listeComboReglage[self.i][3].spin1.value()
				spin1 = str(spin1/10.0)
				spin2 = self.listeComboReglage[self.i][3].spin2.value()
				spin2 = str(spin2/10.0)
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value())
				spin4 = str(self.listeComboReglage[self.i][3].spin4.value())
				spin5 = str(self.listeComboReglage[self.i][3].spin5.value())
				spin6 = str(self.listeComboReglage[self.i][3].spin6.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -edgetensors "+spin1+','+spin2+','+spin3+','+spin4+" -n "+spin5+','+spin6+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return		
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex :
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -edgetensors "+spin1+','+spin2+','+spin3+','+spin4+" -n "+spin5+','+spin6+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
						
			elif self.listeComboReglage[self.i][1]=='erosion':
				#################################################
				# Pour Erosion:
				# --------------------------------
				# spin1 --> Valeur d'érosion
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -erode "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return		
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex :
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -erode "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
				
			elif self.listeComboReglage[self.i][1]=='dilatation':
				#################################################
				# Pour Dilatation:
				# --------------------------------
				# spin1 --> Valeur de dilatation
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -dilate "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return		
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex :
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -dilate "+spin1+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return

			elif self.listeComboReglage[self.i][1]=='figuration_libre':
				#################################################
				# Pour Figuration libre:
				# --------------------------------
				# spin1 --> Amplitude
				# spin2 --> Abstraction
				# spin3 --> Douceur de la peinture
				# spin4 --> Couleur
				# spin5 --> Seuil du bord (segmentation)
				# spin6 --> Douceur de la segmentation
				#################################################
				spin1 = self.listeComboReglage[self.i][3].spin1.value()
				spin1 = str(spin1/100)
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = self.listeComboReglage[self.i][3].spin3.value()
				spin3 = str(spin3/100)
				spin4 = self.listeComboReglage[self.i][3].spin4.value()
				spin4 = str(spin4/100)
				spin5 = self.listeComboReglage[self.i][3].spin5.value()
				spin5 = str(spin5/100)
				spin6 = self.listeComboReglage[self.i][3].spin6.value()
				spin6 = str(spin6/100)
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+"  -drawing  "+spin1+" -gimp_painting "+spin2+','+spin3+','+spin4+" -gimp_segment_watershed_preview "+spin5+','+spin6+',0,0'+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return		
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				# Uniquement pour windows
				elif os.name == 'nt':
					for self.j in self.listeIndex :
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+"  -drawing  "+spin1+" -gimp_painting "+spin2+','+spin3+','+spin4+" -gimp_segment_watershed_preview "+spin5+','+spin6+',0,0'+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
						
			######## Rajout le 4/02/2011 par LUCAS Thomas et CABANA Antoine ##################
			elif self.listeComboReglage[self.i][1]=='effet_flamme':
				#################################################
				# Pour Enflamme :
				# -----------------------
				# spin1 --> Palette
				# spin2 --> Amplitude
				# spin3 --> Echantillonnage
				# spin4 --> Lissage
				# spin5 --> Opacité
				# spin6 --> Bord
				# spin7 --> Amplitude du lissage anisotropique
				# spin8 --> Netteté
				# spin9 --> Anisotropie
				# spin10 --> Gradiant de lissage
				# spin11 --> Tenseur de lissage
				# spin12 --> Précision spaciale
				# spin13 --> Précision angulaire
				# spin14 --> Valeur de la précision
				# spin15 --> Iterations
				#################################################
				spin1 = str(self.listeComboReglage[self.i][3].spin1.value()-1)
				spin2 = str(self.listeComboReglage[self.i][3].spin2.value())
				spin3 = str(self.listeComboReglage[self.i][3].spin3.value()/100.0)
				spin4 = str(self.listeComboReglage[self.i][3].spin4.value()/100.0)
				spin5 = str(self.listeComboReglage[self.i][3].spin5.value()/100.0)
				spin6 = str(self.listeComboReglage[self.i][3].spin6.value())
				spin7 = str(self.listeComboReglage[self.i][3].spin7.value())
				spin8 = str(self.listeComboReglage[self.i][3].spin8.value()/100.0)
				spin9 = str(self.listeComboReglage[self.i][3].spin9.value()/100.0)
				spin10 = str(self.listeComboReglage[self.i][3].spin10.value()/100.0)
				spin11 = str(self.listeComboReglage[self.i][3].spin11.value()/100.0)
				spin12 = str(self.listeComboReglage[self.i][3].spin12.value()/100.0)
				spin13 = str(self.listeComboReglage[self.i][3].spin13.value())
				spin14 = str(self.listeComboReglage[self.i][3].spin14.value()/100.0)
				spin15 = str(self.listeComboReglage[self.i][3].spin15.value())
				# Uniquement pour Linux et MacOSX
				if os.name in ['posix', 'mac']:
					###############################################################################
					## On passe par ce traitement sous Linux et MacOSX car pour l'instant il y a ##
					### un bug d'affichage (à la fin du rendu et dans l'onglet Images après      ##
					### traitement).                                                             ##
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+" -m "+self.rep_annexe+"fire2.gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -fire "+spin1+','+spin2+','+spin3+','+spin4+','+spin5+','+spin6+','+spin7+','+spin8+','+spin9+','+spin10+','+spin11+','+spin12+','+spin13+','+spin14+','+spin15+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return		
					###############################################################################
					# Momentanément désactivé le temps de trouver une solution au bug d'affichage
				# Uniquement pour windows
				elif os.name == 'nt':
					# Sous windows (comme la plupart du temps EKD est installé dans Program Files), une
					# erreur est générée et le filtre Effet flamme ne peut pas être mis en oeuvre car
					# G'MIC ne peut pas aller chercher le fichier fire2.gmic dans un chemin comportant
					# des espace (des trous) ... il faut donc créer un chemin sous windows et copier
					# ce fichier pour qu'on puisse aller le chercher.
					# Répertoire courant
					rep_cour = os.getcwd()
					# Chemin exact du répertoire annexe en local dans l'arborescence d'EKD
					rep_chem_annex_local = rep_cour + os.sep + "gui_modules_image" + os.sep + "filtres_images" + os.sep + "annexe" + os.sep
					#
					# Scan pour récupérer le fichier fire2.gmic en local (filtre image Effet flamme)
					fich_gmic_filtre_effet_flam = rep_chem_annex_local + 'fire2.gmic'
					# Là ou se trouve le lecteur par défaut sous windows (souvent C:)
					lecteur = os.environ['HOMEDRIVE']
					self.rep_annexe = lecteur + os.sep + 'ekd_gmic_filtres_image' + os.sep
					# Si le répertoire n'existe pas, il est crée
					if os.path.isdir(self.rep_annexe) is False: os.makedirs(self.rep_annexe)
					if os.path.isfile(fich_gmic_filtre_effet_flam) is True:
						shutil.copy(rep_chem_annex_local+os.sep+'fire2.gmic', self.rep_annexe[:-1])
					# Traitement ...
					for self.j in self.listeIndex :
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						os.system(("gmic "+" -m "+self.rep_annexe+"fire2.gmic "+"\\\""+self.listeImgSource[self.j]+"\\\""+" -fire "+spin1+','+spin2+','+spin3+','+spin4+','+spin5+','+spin6+','+spin7+','+spin8+','+spin9+','+spin10+','+spin11+','+spin12+','+spin13+','+spin14+','+spin15+" -o "+"\\\""+self.cheminCourantSauv+"\\\"").encode(locale.getdefaultlocale()[1]))
						if not self.opReccurApresApp(): return
					##################################################################################

		#--------------------------------------------------------
		# Filtres utilisant notamment un module python (ex. PIL)
		#--------------------------------------------------------

		elif self.listeComboReglage[self.i][1]=='vieux_films':
			self.appliquerVieuxFilms()

		elif self.listeComboReglage[self.i][1]=='illustration_niveau_gris':
			for self.j in self.listeIndex:
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg = Image.open(self.listeImgSource[self.j])
				convert = obImg.convert("1")
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='traits_fins_et_couleur':
			for self.j in self.listeIndex:
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg = Image.open(self.listeImgSource[self.j])
				convert = obImg.filter(ImageFilter.EDGE_ENHANCE_MORE)
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='emboss':
			for self.j in self.listeIndex:
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg = Image.open(self.listeImgSource[self.j])
				convert = obImg.filter(ImageFilter.EMBOSS)
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='sharpen':
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg = Image.open(self.listeImgSource[self.j])
				convert = obImg.filter(ImageFilter.SHARPEN)
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='niveau_gris':
			for self.j in self.listeIndex:
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg = Image.open(self.listeImgSource[self.j])
				convert = obImg.convert("L")
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='amelior_des_bords':
			for self.j in self.listeIndex:
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg = Image.open(self.listeImgSource[self.j])
				# Application de la matrice d'amélioration des bords. Matrice trouvee ici :
				# http://blogs.codes-sources.com/tkfe/archive/2005/04/15/6004.aspx
				convert = obImg.filter(ImageFilter.Kernel((3, 3), (-1, -2, -1, -2, 16, -2, -1, -2, -1)))
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='debruitage':
			for self.j in self.listeIndex:
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg = Image.open(self.listeImgSource[self.j])
				# Application de la matrice de débruitage. Attention !!! ne fonctionne pas
				# avec les images GIF (.gif)
				convert = obImg.filter(ImageFilter.Kernel((5, 5), (2, 4, 5, 4, 2, 4, 9, 12, 9, 4, 5, 12, 15, 12, 5, 4, 9, 12, 9, 4, 2, 4, 5, 4, 2)))
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		elif self.listeComboReglage[self.i][1]=='evanescence':
			self.appliquerEvanescence()

		elif self.listeComboReglage[self.i][1]=='seuillage':
			self.appliquerSeuillage()

		elif self.listeComboReglage[self.i][1]=='imitation_bd_1':
			self.appliquerImitationBd_1()

		elif self.listeComboReglage[self.i][1]=='negatif':
			self.appliquerNegatif()

		elif self.listeComboReglage[self.i][1]=='encadre_photo':
			self.appliquerEncadrePhoto()

		elif self.listeComboReglage[self.i][1]=='couleurs_predefinies':
			self.appliquerCouleursPredef()

		elif self.listeComboReglage[self.i][1]=='couleurs_personnalisees':
			listeCouleurImgPerso=[]
			for k in range(3):
				for l in range(3):
					listeCouleurImgPerso.append(float('0.'+str(self.listeComboReglage[self.i][3].spin[k][l].value())))
				listeCouleurImgPerso.append(0)

			#print listeCouleurImgPerso
			EkdPrint(u"%s" % listeCouleurImgPerso)

			for self.j in self.listeIndex:
				# Sauvegarde
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
				obImg=Image.open(self.listeImgSource[self.j])
				convert = obImg.convert("RGB").convert("RGB", listeCouleurImgPerso)
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return

		# Ceci a ete réalisé à partir de: http://www.yourmachines.org/tutorials/mgpy.html
		# et à partir du script example2c.py contenu dans l'archive mgpy.tgz. mgpy
		# ('Motion Graphics in Python' (mgpy)) a été realisé par Simon Yuill en 2006.
		# Une partie du code de example2c.py a été repris ici (avec quelques transformations)
		elif self.listeComboReglage[self.i][1]=='separ_en_modules':
			# Valeurs de taille mini et maxi de la forme
			spin1 = self.listeComboReglage[self.i][3].spin1.value()
			spin2 = self.listeComboReglage[self.i][3].spin2.value()
			# La taille minimum ne doit jamais etre superieure a la taille maximum
			if spin1>=spin2:
				erreur=QMessageBox(self)
				erreur.setText(_(u"Attention, <b>la valeur de taille mini de la forme ne doit jamais être supérieure ou égale à la valeur de la taille maxi de la forme</b>. La conversion demandée ne sera pas effectuée. Refaites vos réglages correctement et recommencez l'opération."))
				erreur.setWindowTitle(_(u"Erreur de réglage"))
				erreur.setIcon(QMessageBox.Warning)
				erreur.exec_()
				sys.exit
			else:
				try:
					# Boucle principale
					for self.j in self.listeIndex:
						self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+self.spin1valNombres.value()), self.spin2valNombres.value())+self.ext
						# Ouverture des images
						obImg=Image.open(self.listeImgSource[self.j])
						'''
						############### ERREUR ! ##################################################################
						if obImg.mode=='L':
							erreur=QMessageBox(self)
							erreur.setText(_(u"Vous ne pouvez pas travailler avec des images en niveaux de gris, c'est le cas de %s. Le traitement va s'arrêter !." % os.path.basename(self.listeImgSource[self.j])))
							erreur.setWindowTitle(_(u"Erreur"))
							erreur.setIcon(QMessageBox.Warning)
							erreur.exec_()
							sys.exit
							return 0
						###########################################################################################
						'''
						# Taille des images
						width, height=obImg.size
						# Creation de la surface de l'image
						drawImage = ImageDraw.Draw(obImg)
						# Collecte des donnees (pixels)
						pixels = list(obImg.getdata())
						# Travail avec les pixels
						for y in range(0, height, spin1):
							yp = y * width
							for x in range(0, width, spin1):
								xyp = yp + x
								p = pixels[xyp]
								rndSize = random.randint(spin1, spin2)
								x1 = x - rndSize
								y1 = y - rndSize
								x2 = x + rndSize
								y2 = y + rndSize
								drawImage.rectangle((x1, y1, x2, y2), fill=p, outline=(0,0,0))
						obImg.save(self.cheminCourantSauv)
						if not self.opReccurApresApp(): return

				except:
					erreur=QMessageBox(self)
					erreur.setText(_(u"<p>Une (ou plusieurs) des images que vous avez chargé n'a pas le bon mode, en effet, pour ce filtre, EKD ne peut pas travailler avec les images dont le mode est <b>L</b> (il s'agit d'images en niveaux de gris), <b>P</b> (images GIF). Vérifiez le mode de chacune de vos images (et ce dans les onglets <b>Image(s) source</b>), pour ce faire sélectionnez une image et cliquez sur le bouton <b>Infos</b> (dans la fenêtre qui s'ouvre, chacune des images fautives devrait avoir soit <b>L</b> ou soit <b>P</b> indiqué en face du champ <b>Mode</b>). Eliminez chacune de ces images (par le bouton <b>Retirer</b>) et relancez le traitement (par les boutons <b>Voir le résultat</b> ou <b>Appliquer et sauver</b>).</p><p>La première image incriminée par ce problème est <b>%s</b>.</p><p>Le traitement va s'arrêter !.</p>" % os.path.basename(self.listeImgSource[self.j])))
					erreur.setWindowTitle(_(u"Erreur"))
					erreur.setIcon(QMessageBox.Critical)
					erreur.exec_()
					sys.exit
					return 0

		elif self.listeComboReglage[self.i][1]=='omb_lum_a_la_coul':
			self.appliquerOmbreEtLumALaCouleur()

		elif self.listeComboReglage[self.i][1]=='rotation_image':
			self.appliquerRotationImage()

		elif self.listeComboReglage[self.i][1]=='imitation_bd_2':
			self.appliquerImitationBd_2()

		elif self.listeComboReglage[self.i][1]=='laplacien_1':
			self.appliquerLaplacien_1()

		elif self.listeComboReglage[self.i][1]=='contour_et_couleur':
			self.appliquerContourEtCouleur()
			
		elif self.listeComboReglage[self.i][1]=='peintur_degrade_de_coul':
			self.appliquerPeintureMonochromEnDegrade()
			
		elif self.listeComboReglage[self.i][1]=='peinture_aquarelle_1':
			self.appliquerPeintureAquarelle_1()

		'''
		elif self.listeComboReglage[self.i][1]=='ombre_lumiere':
			for self.j in self.listeIndex:
				self.cheminCourantSauv = self.cheminSauv+'_'+string.zfill((self.j+1), 6)+self.ext
				process = QProcess(self)
				process.start("convert -fx 'cos(3.22*pi*R)*100' "+"\""+self.listeImgSource[self.j]+"\" "+self.repTampon+"vf_ombre_lumiere")
				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)
				obImg = Image.open(self.repTampon+"vf_ombre_lumiere")
				convert = obImg.filter(ImageFilter.SMOOTH_MORE)
				convert.save(self.cheminCourantSauv)
				if not self.opReccurApresApp(): return
		'''


	def afficherAide(self):
		"""Boîte de dialogue de l'aide"""
		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<p><b>Vous pouvez ici appliquer des filtres (dans l'ensemble assez différents les uns des autres) sur un lot d'images.</b></p><p>Dans l'onglet <b>'Image(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher votre/vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Dans l'onglet <b>Réglages</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b>, sélectionnez ensuite votre <b>'Type'</b> de filtre dans la boîte déroulante, faites les réglages par rapport au <b>'Type'</b> choisi. Cliquez sur le bouton <b>'Voir le résultat'</b> (vous voyez à ce moment le résultat de vos réglages sur la première image du lot s'afficher dans l'onglet <b>Images après traitement</b>).</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer et sauver'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>Images après traitement</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>'Infos'</b> vous permet de voir le filtre utilisé, les image(s) chargée(s) et les image(s) convertie(s).</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'choixFiltre', unicode(self.comboReglage.currentIndex()))
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1valNombres.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2valNombres.value()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.comboReglage.setCurrentIndex(int(EkdConfig.get(self.idSection, 'choixFiltre')))
		self.spin1valNombres.setValue(int(EkdConfig.get(self.idSection, 'spin1')))
		self.spin2valNombres.setValue(int(EkdConfig.get(self.idSection, 'spin2')))
