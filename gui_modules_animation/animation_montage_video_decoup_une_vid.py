#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from gui_modules_common.mencoder_gui import WidgetMEncoder
from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_image.selectWidget import SelectWidget
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

class Label(QWidget):
	"""barre de sélection d'un extrait vidéo"""
	def __init__(self, marques, largeur=200):
		# parent nous permettra d'accéder à la valeur du curseur
		QWidget.__init__(self)
		# dimensions minimales de la barre. On gardera 30 px en horizontal. La barre prendra tout l'espace en horizontal
		self.x, self.y = largeur, 35
		self.setMinimumSize(self.x, self.y)
		self.setMaximumSize(self.x, self.y)
		self.update_marques(marques)

	def update_marques(self, marques):
		self.marques=marques

	def paintEvent(self, event):
		paint = QPainter()
		paint.begin(self)

		# QFont.Light: police légère (par défaut)
		font = QFont('Serif', 7, QFont.Light)
		paint.setFont(font)

		# récupération de la valeur de la marque du début, de fin et de la durée de la vidéo
		marques = self.marques
		# Et oui, debut peut correspondre à la valeur de fin
		# si l'utilisateur s'emmêle les pinceaux
		debut = float(marques[0])
		fin = float(marques[1])
		duree = float(marques[2])

		## On évite une division par 0
		if (duree == 0):
			duree = 0.1

		# nbr de px correspondant à la marque de début et de fin de la sélection de la vidéo
		debutPx = int((debut/duree)*self.x)
		finPx = int((fin/duree)*self.x)

		## traçage des 2 rectangles (le global et celui de la zone sélectionnée
		## pas de contour pour les couleurs
		paint.setBrush(QColor(235,215,235)) # mauve clair
		# rectangle plein de la barre
		paint.drawRect(0, 0, self.x, self.y)
		# vert
		paint.setPen(QColor(60, 150, 60)) # vert
		paint.setBrush(QColor(60, 150, 60)) # vert
		paint.drawRect(debutPx, 0, finPx-debutPx, self.y)


		# on paramètre une ligne solide
		pen = QPen(QColor(20, 20, 20), 1, Qt.SolidLine)
		paint.setPen(pen)
		# pas de dessin de fond sinon on ne pourra plus inscrire de rectangle variable dans la barre
		paint.setBrush(Qt.NoBrush)
		# dessin du contour de la barre
		paint.drawRect(0, 0, self.x-1, self.y-1)

		# Indicateur de temps pour le début
		# dessin graduations
		paint.drawLine(debutPx, 0, debutPx, 5)
		# police métrique
		metrics = paint.fontMetrics()
		# taille des valeurs de la police métrique
		debutMetrique="%.1f" %(debut)
		largMetrique = metrics.width(debutMetrique)
		# dessin des valeurs de la police métrique - alignement avec les graduations
		paint.drawText(debutPx-largMetrique/2, 15, debutMetrique)

		# Indicateur de temps pour la fin
		# dessin graduations
		paint.drawLine(finPx, self.y-5, finPx, self.y)
		# police métrique
		metrics = paint.fontMetrics()
		# taille des valeurs de la police métrique
		finMetrique="%.1f" %(fin)
		largMetrique = metrics.width(finMetrique)
		# dessin des valeurs de la police métrique - alignement avec les graduations
		paint.drawText(finPx-largMetrique/2, self.y -8, finMetrique)

		paint.end()

class Animation_MontagVideoDecoupUneVideo(Base):
	# -------------------------------------------------------------------------------------
	# Cadre accueillant les widgets de : Animation >> Montage Vidéo >> Découper une Vidéo
	# -------------------------------------------------------------------------------------
	def __init__(self, statusBar):
		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------
		#=== tout sera mis dans une boîte verticale ===#
		self.vbox=QVBoxLayout()

		#=== Variable de configuration ===#
		self.config=EkdConfig

		#=== Identifiant de la classe ===#
		self.idSection = "animation_decouper_une_video"

		super(Animation_MontagVideoDecoupUneVideo, self).__init__('vbox', titre=_(u"Montage: Découpage d'une vidéo")) # module de animation

		self.printSection()

		#=== Drapeaux ===#
		# drapeau pour savoir si la valeur de début de la sélection vidéo été enregistré
		self.debutEstSelect = False
		# drapeau pour savoir si la valeur de fin de la sélection vidéo été enregistré
		self.finEstSelect = False
		# drapeau d'extraction du son
		self.extraireSon = True

		# -------------------------------------------------------------------
		# Boîte de groupe : "Fichier vidéo source"
		# -------------------------------------------------------------------
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.mpg", "*.mpeg", "*.mjpeg", "*.flv", "*.mp4", "*.dv", "*.vob"], mode="texte", video = True)
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		#--------------------------------------------------------------------

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.


		# --------------------------------------------------------------------------
		# Boîte de groupe de réglage: visualisation et de marquage de la sélection
		# --------------------------------------------------------------------------

		# Création de la boite de groupe de réglage (contenant la boite self.layoutReglage)
		reglageGroup = QGroupBox()
		self.layoutReglage = QVBoxLayout(reglageGroup)
		#=== Widgets mplayer ===#
		vboxMplayer = QVBoxLayout()
		# Le facteur limitant est la largeur -> + simple à coder à cause de la largeur de la barre
		self.mplayer=Mplayer(taille=(300,270), facteurLimitant=Mplayer.LARGEUR,
			choixWidget=(Mplayer.RATIO, Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_A_PART))

		self.mplayer.listeVideos = []
		self.mplayer.setToolTip(_(u"La lecture de la vidéo est nécessaire pour achever la sélection d'une zone de la vidéo"))
		self.mplayer.setEnabled(False)
		hbox = QHBoxLayout()
		hbox.addStretch()
		hbox.addWidget(self.mplayer)
		hbox.addStretch()
		vboxMplayer.addLayout(hbox)

		self.radioSource = QRadioButton(_(u"vidéo(s) source(s)"))
		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(False)
		self.connect(self.radioSource, SIGNAL("clicked(bool)"), self.fctRadioSource)
		self.radioApercu = QRadioButton(_(u"aperçu"))
		self.radioApercu.setEnabled(False)
		self.connect(self.radioApercu, SIGNAL("clicked(bool)"), self.fctRadioApercu)
		self.radioConvert = QRadioButton(_(u"vidéo convertie"))
		self.radioConvert.setEnabled(False)
		self.connect(self.radioConvert, SIGNAL("clicked(bool)"), self.fctRadioConvert)

		self.layoutReglage.addLayout(vboxMplayer)

		self.add(reglageGroup, _(u"Réglages"))
		# Le widget-mplayer récupère des informations tous les 10ème
		# de seconde au lieu de toutes les secondes -> le marquage du
		# début et de la fin de la sélection seront plus précis
		self.mplayer.dureeTimer=100

		self.connect(self.mplayer.bout_LectPause, SIGNAL('clicked()'), self.lectureMPlayer)

		#=== Marquage et affichage des bornes de la sélection ===#

		#||| Label de visualisation de la sélection |||#

		self.marques = (0,0,1)
		self.visuSelect = Label(self.marques, 300)
		self.visuSelect.setToolTip(_(u"La zone sélectionnée apparait en vert dans cette bande"))
		self.valeurDebut=0
		self.valeurFin=0

		hbox=QHBoxLayout()
		hbox.addWidget(self.visuSelect)
		self.layoutReglage.addLayout(hbox)

		#||| boutons de marquage de la sélection |||#

		iconTaille = 28

		self.frameMarque = QFrame()
		boiteMarque = QHBoxLayout()
		boiteMarque.addStretch()

		boutMarqDebutSelect=QPushButton()
		boutMarqDebutSelect.setIcon(QIcon("Icones" + os.sep + "Tdebut.png"))
		boutMarqDebutSelect.setIconSize(QSize(iconTaille, iconTaille))
		boutMarqDebutSelect.setToolTip(_(u"Marquer le début de la sélection"))
		boiteMarque.addWidget(boutMarqDebutSelect)

		self.boutMarqFinSelect=QPushButton()
		self.boutMarqFinSelect.setIcon(QIcon("Icones" + os.sep + "Tfin.png"))
		self.boutMarqFinSelect.setIconSize(QSize(iconTaille, iconTaille))
		self.boutMarqFinSelect.setToolTip(_(u"Marquer la fin de la sélection"))
		self.boutMarqFinSelect.setEnabled(False)
		boiteMarque.addWidget(self.boutMarqFinSelect)

		boutMarqDebutSelect_min=QPushButton()
		boutMarqDebutSelect_min.setIcon(QIcon("Icones" + os.sep + "Tdebut2.png"))
		boutMarqDebutSelect_min.setIconSize(QSize(iconTaille, iconTaille))
		boutMarqDebutSelect_min.setToolTip(_(u"Marquer le début de la sélection au temps minimum (t=0)"))
		boiteMarque.addWidget(boutMarqDebutSelect_min)

		self.boutMarqFinSelect_max=QPushButton()
		self.boutMarqFinSelect_max.setIcon(QIcon("Icones" + os.sep + "Tfin2.png"))
		self.boutMarqFinSelect_max.setIconSize(QSize(iconTaille, iconTaille))
		self.boutMarqFinSelect_max.setToolTip(_(u"Marquer la fin de la sélection au temps maximum (t=\"la durée de la vidéo\")"))
		self.boutMarqFinSelect_max.setEnabled(False)
		boiteMarque.addWidget(self.boutMarqFinSelect_max)

		boutMiseAZeroSelect=QPushButton()
		boutMiseAZeroSelect.setIcon(QIcon("Icones" + os.sep + "update.png"))
		boutMiseAZeroSelect.setIconSize(QSize(iconTaille, iconTaille))
		boutMiseAZeroSelect.setToolTip(_(u"Remettre à zéro les paramètres"))
		boiteMarque.addWidget(boutMiseAZeroSelect)

		self.boutExtractionSon=QPushButton()
		self.boutExtractionSon.setIcon(QIcon("Icones" + os.sep + "sound.png"))
		self.boutExtractionSon.setIconSize(QSize(iconTaille, iconTaille))
		self.boutExtractionSon.setToolTip(_(u"Pressez le bouton si vous voulez exclure le son de l'extraction vidéo"))
		boiteMarque.addWidget(self.boutExtractionSon)

		#-------------------------------------------------------------------------
		## Bouton d'augmentation/réduction de la vitesse
		taille = QSize(15,15)
		speedBox = QVBoxLayout()
		self.moinsvite=QPushButton("-")
		self.moinsvite.setFixedSize(taille)
		self.moinsvite.setToolTip(_(u"Pressez le bouton si vous réduire la vitesse de la vidéo"))
		speedBox.addWidget(self.moinsvite)
		
		self.initspeed=QPushButton("=")
		self.initspeed.setFixedSize(taille)
		self.initspeed.setToolTip(_(u"Pressez le bouton si vous réinitialiser la vitesse de la vidéo"))
		speedBox.addWidget(self.initspeed)

		self.plusvite=QPushButton("+")
		self.plusvite.setFixedSize(taille)
		self.plusvite.setToolTip(_(u"Pressez le bouton si vous augmenter la vitesse de la vidéo"))
		speedBox.addWidget(self.plusvite)
		boiteMarque.addLayout(speedBox)
		
		self.connect(self.moinsvite, SIGNAL("clicked()"), self.mplayer.speeddown)
		self.connect(self.initspeed, SIGNAL("clicked()"), self.mplayer.initspeed)
		self.connect(self.plusvite, SIGNAL("clicked()"), self.mplayer.speedup)
		#-------------------------------------------------------------------------

		self.connect(boutMarqDebutSelect, SIGNAL("clicked()"), self.marqDebutSelect)
		self.connect(self.boutMarqFinSelect, SIGNAL("clicked()"), self.marqFinSelect)
		self.connect(boutMarqDebutSelect_min, SIGNAL("clicked()"), self.marqDebutSelect_min)
		self.connect(self.boutMarqFinSelect_max, SIGNAL("clicked()"), self.marqFinSelect_max)
		self.connect(boutMiseAZeroSelect, SIGNAL("clicked()"), self.miseAZeroSelect)
		self.connect(self.boutExtractionSon, SIGNAL("clicked()"), self.reglageSon)

		self.frameMarque.setLayout(boiteMarque)
		# On grise le widget au début
		self.frameMarque.setEnabled(False)

		self.layoutReglage.addWidget(self.frameMarque)
		boiteMarque.addStretch()

		#||| boutons radio de lecture de la source ou du fichier converti|||#
		hbox = QHBoxLayout()
		hbox.addWidget(self.radioSource)
		hbox.addWidget(self.radioApercu)
		hbox.addWidget(self.radioConvert)
		hbox.setAlignment(Qt.AlignHCenter)
		self.layoutReglage.addLayout(hbox)
		self.layoutReglage.addStretch(50)

		self.addLog()

	def getFile(self):
		'''
		# On utilise la nouvelle interface de récupération des vidéos
		Récupération de la vidéo source selectionnée
		'''
		self.chemin = self.afficheurVideoSource.getFile()
		self.boutApp.setEnabled(True)

		self.mplayer.setEnabled(True)
		self.mplayer.setVideos([self.chemin])

		# On active les réglage
		self.frameMarque.setEnabled(True)
		self.boutMarqFinSelect_max.setEnabled(True)
		self.boutMarqFinSelect.setEnabled(True)
		# Restauration de l'état initial de sélection
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(True)
		self.radioApercu.setEnabled(False)
		self.radioApercu.setChecked(False)
		self.radioConvert.setEnabled(False)
		self.radioConvert.setChecked(False)

		self.emit(SIGNAL("loaded"))
		self.miseAZeroSelect()

	def lectureMPlayer(self):
		"""Dégriser les 2 boutons de sélection de fin si le début a déjà été sélectionné"""
		if self.debutEstSelect:
			self.boutMarqFinSelect.setEnabled(True)
			self.boutMarqFinSelect_max.setEnabled(True)

	def reglageSon(self):
		"""Extraire ou pas le son de la vidéo lors de l'extraction vidéo"""
		if self.extraireSon:
			self.extraireSon = False
			self.boutExtractionSon.setIcon(QIcon("Icones" + os.sep + "nosound.png"))
			self.boutExtractionSon.setToolTip(_(u"Pressez le bouton si vous voulez ré-inclure le son de l'extraction vidéo"))
		else:
			self.extraireSon = True
			self.boutExtractionSon.setIcon(QIcon("Icones" + os.sep + "sound.png"))
			self.boutExtractionSon.setToolTip(_(u"Pressez le bouton si vous voulez exclure le son de l'extraction vidéo"))

	def miseAZeroSelect(self):
		"""On remet à zéro les zones sélectionnées"""
		self.debutEstSelect = False
		self.finEstSelect = False
		self.boutApp.setEnabled(False)
		self.boutMarqFinSelect.setEnabled(False)
		self.boutMarqFinSelect_max.setEnabled(False)
		self.valeurDebut, self.valeurFin = 0, 0
		self.marques = (0,0,1)
		self.visuSelect.update_marques(self.marques)
		self.visuSelect.repaint()

	def marqDebutSelect(self):
		"""Récupération de la valeur du marqueur du début de la sélection"""

		# Le début n'a pas été sélectionné ou il a été sélectionné mais pas la fin
		# -> un seul trait sur le QLabel
		if not self.debutEstSelect or (self.debutEstSelect and not self.finEstSelect):
			self.valeurDebut = self.mplayer.temps
			#print self.valeurDebut
			EkdPrint(u"%s" % self.valeurDebut)
			self.debutEstSelect = True
			# mplayer est en lecture
			if self.mplayer.estLue:
				self.boutMarqFinSelect.setEnabled(True)
				self.boutMarqFinSelect_max.setEnabled(True)
			# tracer d'un seul trait
			self.marques = (self.valeurDebut,self.valeurDebut,self.mplayer.dureeVideo)
			self.visuSelect.update_marques(self.marques)
			self.visuSelect.repaint()

		# Le début et la fin ont déjà été sélectionnés
		elif self.debutEstSelect and  self.finEstSelect:
			self.valeurDebut = self.mplayer.temps
			#print self.valeurDebut
			EkdPrint(u"%s" % self.valeurDebut)
			self.mettreAJourLabel('debut')

	def marqFinSelect(self):
		"""Récupération de la valeur du marqueur de la fin de la sélection"""
		self.valeurFin = self.mplayer.temps
		#print self.valeurFin
		EkdPrint(u"%s" % self.valeurFin)
		self.finEstSelect = True
		self.mettreAJourLabel('fin')

	def marqDebutSelect_min(self):
		"""La valeur du marqueur du début de la sélection est placé au temps t=0 seconde"""

		# Le début n'a pas été sélectionné ou il a été sélectionné mais pas la fin
		# -> un seul trait sur le QLabel
		if not self.debutEstSelect or (self.debutEstSelect and not self.finEstSelect):
			self.valeurDebut = 0
			#print self.valeurDebut
			EkdPrint(u"%s" % self.valeurDebut)
			self.debutEstSelect = True
			# mplayer est en lecture
			if self.mplayer.estLue:
				self.boutMarqFinSelect.setEnabled(True)
				self.boutMarqFinSelect_max.setEnabled(True)
			# tracer d'un seul trait
			self.marques = (self.valeurDebut,self.valeurDebut,self.mplayer.dureeVideo)
			self.visuSelect.update_marques(self.marques)
			self.visuSelect.repaint()

		# Le début et la fin ont déjà été sélectionnés
		elif self.debutEstSelect and  self.finEstSelect:
			self.valeurDebut = 0
			#print self.valeurDebut
			EkdPrint(u"%s" % self.valeurDebut)
			self.mettreAJourLabel()

	def marqFinSelect_max(self):
		"""La valeur du marqueur de la fin de la sélection est placé à la fin de la vidéo"""
		self.valeurFin = self.mplayer.dureeVideo
		#print self.valeurFin
		EkdPrint(u"%s" % self.valeurFin)
		self.finEstSelect = True
		self.mettreAJourLabel()

	def mettreAJourLabel(self, debutOuFin=None):
		"""Redessiner le QLabel"""

		# si les valeurs de début et de fin sont identiques (possible car notre précision est de un dixième de seconde) alors on remet tout à zéro
		if self.valeurDebut == self.valeurFin:
			self.finEstSelect = False
			self.boutApp.setEnabled(False)
			# tracer d'un seul trait
			self.marques = (self.valeurDebut,self.valeurFin,self.mplayer.dureeVideo)
			self.visuSelect.update_marques(self.marques)
			self.visuSelect.repaint()
			self.radioConvert.setEnabled(False)
			self.radioApercu.setEnabled(False)

		# Truisme: la valeur du début de la sélection doit être inférieure à la valeur de la fin
		# sinon les valeurs de début et de fin sont égalisées
		elif self.valeurDebut > self.valeurFin:
			self.radioSource.setEnabled(False)
			self.radioApercu.setEnabled(False)
			if debutOuFin=='debut':
				self.valeurFin = self.valeurDebut
				self.boutApp.setEnabled(False)
				self.marques = (self.valeurDebut,self.valeurFin,self.mplayer.dureeVideo)
				self.visuSelect.update_marques(self.marques)
				self.visuSelect.repaint()

			if debutOuFin=='fin':
				self.valeurDebut = self.valeurFin
				self.boutApp.setEnabled(False)
				self.marques = (self.valeurDebut,self.valeurFin,self.mplayer.dureeVideo)
				self.visuSelect.update_marques(self.marques)
				self.visuSelect.repaint()
		# Le cas normal
		else:
			self.marques = (self.valeurDebut,self.valeurFin,self.mplayer.dureeVideo)
			self.visuSelect.update_marques(self.marques)
			self.visuSelect.repaint()
			self.boutApp.setEnabled(True)
			self.radioSource.setEnabled(True)
			self.radioApercu.setEnabled(True)

		#print "Bornes de la sélection :", self.valeurDebut, self.valeurFin, type(self.valeurDebut), type(self.valeurFin)
		EkdPrint(u"Bornes de la sélection : %s %s %s" % (self.valeurDebut, self.valeurFin, type(self.valeurDebut)), type(self.valeurFin))


	def fctRadioSource(self):
		""""Communique le fichier source à mplayer"""
		self.mplayer.listeVideos = [self.chemin]
		self.mplayer.debutFin = (0,0)
		self.frameMarque.setEnabled(True)
		self.visuSelect.setEnabled(True)
		self.radioApercu.setChecked(False)
		self.radioConvert.setChecked(False)

	def fctRadioApercu(self):
		""""Communique le fichier aperçu à mplayer"""
		self.mplayer.listeVideos = [self.chemin]
		debut = float("%.1f" %self.valeurDebut)
		fin = float("%.1f" %self.valeurFin)
		self.mplayer.debutFin = (debut,fin)
		self.frameMarque.setEnabled(False)
		self.radioSource.setChecked(False)
		self.radioConvert.setChecked(False)

	def fctRadioConvert(self):
		""""Communique le fichier converti à mplayer"""
		self.mplayer.listeVideos = [self.fichierSortie]
		self.mplayer.debutFin = (0,0)
		self.frameMarque.setEnabled(False)
		self.visuSelect.setEnabled(False)
		self.radioSource.setChecked(False)
		self.radioApercu.setChecked(False)


	def ouvrirSource(self, nomEntree=None):
		"""Récupération du chemin de la vidéo sélectionnée et activation de certains widgets"""

		# Récupération du chemin de la vidéo
		chemin = self.recupSource(nomEntree)

		if not chemin: return

		# Affichage du chemin + nom de fichier dans la ligne d'édition
		self.ligneEditionSource.setText(chemin)

		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = [chemin]
		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(False)
		self.radioConvert.setEnabled(False)

		# les boutons de marquage apparaissent
		self.frameMarque.setEnabled(True)

		# Utile lors de la sélection d'une 2ème vidéo et au-delà
		self.miseAZeroSelect()


	def afficherAide(self):
		""" Boîte de dialogue de l'aide du cadre Animation > Encodage """

		super(Animation_MontagVideoDecoupUneVideo, self).afficherAide(_(u"""<p><b>Vous pouvez ici découper une vidéo et ainsi en garder uniquement la partie qui vous intéresse.</b></p><p><font color='green'>Ce cadre est assez différent des autres, vous avez tout d'abord la zone de visualisation vidéo, puis en dessous les boutons marche, arrêt et le compteur, la glissière de défilement, la zone d'affichage de la découpe (les parties découpées seront affichées en vert), les boutons début/fin de sélection, remise à zéro (vous pouvez sélectionner ou non le son par le bouton haut parleur), à la doite de ce dernier bouton, vous avez trois minuscules boutons contenant +, = et - (ils servent à accélérer ou diminuer la vitesse de lecture de la vidéo), puis les choix de visualisation <b>'vidéo(s) source(s)'</b>, <b>'vidéo convertie'</b> et le bouton <b>'Comparateur de vidéos'</b>.</font></p><p><b>Tout ce qui vient de vous être décrit se trouve dans l'onglet Réglages</b>.</p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b>, lisez la vidéo (par le bouton avec la flèche orientée vers la droite <b>'La lecture de la vidéo est nécessaire ...'</b>), pour la vitesse de lecture, profitez des boutons + ou - pour augmenter ou diminuer la vitesse de lecture <b>(plus vous diminuez la vitesse de lecture, plus la découpe pourra se faire de façon précise)</b>, cliquez ensuite sur le bouton <b>'Marquer le début de la sélection'</b> ou <b>'Marquer le début de la sélection au temps minimum (t=0)'</b> (pour sélectionner la vidéo à son tout début), laissez jouer (regardez la vidéo défiler) et cliquez sur le bouton <b>'Marquer la fin de la sélection'</b> au moment propice (ou <b>'Marquer la fin de la sélection au temps maximum t="la durée de la vidéo"'</b> pour garder la dite vidéo jusqu'à la fin).</p><p><font color='blue'>Sachez que vous pouvez revenir aux paramètres par défaut en cliquant sur le bouton <b>'Remettre à zéro les paramètres'</b> (les deux flèches vertes inversées), vous devrez alors rejouer la vidéo et recommencer vos différentes sélections.</font></p><p>Cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde de votre vidéo, entrez le <b>'Nom de Fichier'</b> dans le champ de texte réservé à cet effet ... cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Vous pouvez visionner votre vidéo (avant la conversion) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la conversion <b>'vidéo convertie'</b> ou bien encore les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos et fichiers audio chargés (avec leurs chemins exacts) avant et après conversion.</p>"""))


	def appliquer(self):
		"""Découpage de la vidéo"""

		# Récupération du chemin source
		chemin=unicode(self.chemin)
		# suffix du fichier actif
		suffix=os.path.splitext(chemin)[1]
		# Modifié le 30/06/2009 : On joue avec l'éritage de Base
                saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))

		cheminFichierEnregistrerVideo = saveDialog.getFile()

		if not cheminFichierEnregistrerVideo: return
		###########################################################################################################################

		tempsDebut = float("%.1f" %self.valeurDebut)
		tempsFin = float("%.1f" %self.valeurFin)
		dureeSelection = str(tempsFin - tempsDebut)
		#

		# Extension du fichier
		#print "extension :", suffix, type(suffix)
		EkdPrint(u"extension : %s %s" % (suffix, type(suffix)))

		try:
			mencoder = WidgetMEncoder('decoupervideo', chemin, cheminFichierEnregistrerVideo, valeurNum = (str(tempsDebut), str(dureeSelection)), optionSpeciale = self.extraireSon, laisserOuvert=1)
			mencoder.setWindowTitle(_(u"Découper une vidéo"))
			mencoder.exec_()
		except:
			messageErrAnEnc=QMessageBox(self)
			messageErrAnEnc.setText(_(u"Un problème est survenu lors de l'exécution de \"mencoder -ss ...\""))
			messageErrAnEnc.setWindowTitle(_(u"Error"))
			messageErrAnEnc.setIcon(QMessageBox.Warning)
			messageErrAnEnc.exec_()
			return

		self.fichierSortie = cheminFichierEnregistrerVideo
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		self.radioConvert.setChecked(True)
		### Information à l'utilisateur
		self.infoLog(None, chemin, None, cheminFichierEnregistrerVideo)


	def saveFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurVideoSource.saveFileLocation(self.idSection)
		# Ajout de la sauvegarde des positions début et fin
		EkdConfig.set(self.idSection, u'valeurDebut', unicode(self.valeurDebut))
		EkdConfig.set(self.idSection, u'valeurFin', unicode(self.valeurFin))

	def loadFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurVideoSource.loadFileLocation(self.idSection)
		self.valeurDebut = float(EkdConfig.get(self.idSection, 'valeurDebut'))
		self.valeurFin = float(EkdConfig.get(self.idSection, 'valeurFin'))
		self.mettreAJourLabel("debut")
		self.mettreAJourLabel("fin")

	def load(self):
		'''
		Chargement de la configuration de tous les objets
		'''
		self.loadFiles()

	def save(self):
		'''
		Sauvegarde de la configuration de tous les objets
		'''
		self.saveFiles()
