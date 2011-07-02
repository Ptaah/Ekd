#! /usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, SIGNAL, SLOT, QPoint, QString, QFileInfo, QSize, PYQT_VERSION_STR
from PyQt4.QtGui import QScrollArea, QLabel, QPalette, QMenu, QIcon, QDialog, QPixmap, QImage, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton, QMovie
import os
import Image
from gui_modules_common.EkdWidgets import EkdPreview
from moteur_modules_common.EkdTools import debug

class VisionneurImagePourEKD(QScrollArea):
	''' Classe pour l'affichage des images (avec des barres de
	défilement)'''
	def __init__(self, img=None):
		QScrollArea.__init__(self)

		# Déclaration du drapeau: a-t-on chargé un *.gif
		if img and os.path.splitext(img)[1]!=".gif":
			self.gif = 1
		else:
			self.gif = 0
		
		# Facteur de redimensionnement de l'image à afficher par rapport à la taille réelle de l'image
		self.factor = 1
		
		# Variables de paramètres
		self.modeTransformation=Qt.SmoothTransformation
		#self.modeTransformation=Qt.FastTransformation
		
		# widget qui contiendra l'image
		self.imageLabel = QLabel()
		self.imageLabel.setAlignment(Qt.AlignCenter)
		
		self.setBackgroundRole(QPalette.Dark)
		self.setWidget(self.imageLabel)
		# Indispensable pour ne pas avoir d'images tronquées, lors du chargement de nvll img
		self.setWidgetResizable(True)
		
		# Position du curseur dans le QScrollArea au moment du clic de la souris
		self.positionPresseeSourisIni = QPoint()
		# Position du point haut-gauche du QScrollArea par rapport au QPixMap entier au
		# moment du clic de la souris (par la suite appelée "position de la barre de défilement")
        	self.positionBarrePresseeSourisIni = QPoint()
		
		# Création du menu contextuel
		self.menuZoom=QMenu("Zoom")
		
		# Entrée zoom taille réelle
		self.menuTailleReelle=self.menuZoom.addAction(_(u'&Taille Réelle'))
		self.menuTailleReelle.setIcon(QIcon("Icones" + os.sep + "taillereelle.png"))
		self.connect(self.menuTailleReelle, SIGNAL("triggered()"), self.setTailleReelle)
		
		# Entrée zoom taille fenetre
		self.menuTailleFenetre=self.menuZoom.addAction(_(u'&Adapter à la fenêtre'))
		self.menuTailleFenetre.setIcon(QIcon("Icones" + os.sep + "fenetre.png"))
		self.connect(self.menuTailleFenetre, SIGNAL("triggered()"), self.setTailleFenetre)
	
		# Entrée zoom +
		self.menuZoomPlus=self.menuZoom.addAction(_(u'&Zoom Avant'))
		self.menuZoomPlus.setIcon(QIcon("Icones" + os.sep + "zoomplus.png"))
		self.connect(self.menuZoomPlus, SIGNAL("triggered()"), self.zoomAvant)
		
		# Entrée zoom - 
		self.menuZoomMoins=self.menuZoom.addAction(_(u'&Zoom Arrière'))
		self.menuZoomMoins.setIcon(QIcon("Icones" + os.sep + "zoommoins.png"))
		self.connect(self.menuZoomMoins, SIGNAL("triggered()"), self.zoomArriere)
		
		# Entrée mettre en pause/démarrer l'animation du gif
		self.menuStartPauseGif=self.menuZoom.addAction(_(u"Mettre en pause/démarrer l'animation"))
		self.menuStartPauseGif.setIcon(QIcon("Icones" + os.sep + "player_end.png"))
		self.connect(self.menuStartPauseGif, SIGNAL("triggered()"), self.startPauseGif)
			
		# Entrée mettre en pause/démarrer l'animation du gif
		self.menuStopGif=self.menuZoom.addAction(_(u"Arrêter l'animation"))
		self.menuStopGif.setIcon(QIcon("Icones" + os.sep + "player_stop.png"))
		self.connect(self.menuStopGif, SIGNAL("triggered()"), self.stopGif)
		
		# On cache les 2 menus de *.gif si on ne traite pas ce format
		if not self.gif:
			self.menuStartPauseGif.setVisible(False)
			self.menuStopGif.setVisible(False)
		
		# Si une image est en paramètre de classe, on l'affiche directement
		# sinon on pourra toujours l'afficher plus tard en appelant la
		# méthode setImage(), le moment venu
		if img:
			self.setImage(img)
			self.setToolTip(img)
		else:
			# image par défaut
			self.setImage("Icones" + os.sep + "avant-image.png")
			self.setToolTip(_(u"image d'accueil"))
			self.setTailleReelle()
	
	def mousePressEvent(self, event):
		"Menu contextuel et enregistrement de données préparant le déplacement de l'image par pincement"
		
		# Menu contextuel
		if event.button() == Qt.RightButton: 
			self.menuZoom.popup(event.globalPos())
		
		# On enregistre la position du curseur et de la barre de défilement au moment du clic
		elif event.button() == Qt.LeftButton:
			self.positionPresseeSourisIni = QPoint(event.pos())
			self.positionBarrePresseeSourisIni.setX(self.horizontalScrollBar().value())
			self.positionBarrePresseeSourisIni.setY(self.verticalScrollBar().value())
			if PYQT_VERSION_STR >= "4.1.0": 
				# curseur main fermée
				self.setCursor(Qt.ClosedHandCursor)
			else: self.setCursor(Qt.SizeAllCursor)
			event.accept()
	
	def mouseMoveEvent(self, event):
		"Déplacement de l'image dans le QScrollArea quand la souris est pressée"
		
		if self.positionPresseeSourisIni.isNull():
			event.ignore()
			return
		
		# Nouvelles positions de la barre de défilement (selon x et y)
		self.horizontalScrollBar().setValue(self.positionBarrePresseeSourisIni.x() + (self.positionPresseeSourisIni.x() - event.pos().x()))
		self.verticalScrollBar().setValue(self.positionBarrePresseeSourisIni.y() + (self.positionPresseeSourisIni.y() - event.pos().y()))
		self.horizontalScrollBar().update()
		self.verticalScrollBar().update()
		event.accept()
	
	def mouseReleaseEvent(self, event):
		"Réaffichage du curseur classique de la souris"
		self.setCursor(Qt.ArrowCursor)
		event.accept()
	
	def setScaleMode(self, mode):
		"Choix du mode de redimensionnement"
		# Mise à jour du paramètre
		self.modeTransformation=mode
	
	def setTailleFenetre(self):
		"Affichage taille fenetre"
		
		# Gestion de la taille
		#- Si l'image rentre
		##- Si l'image est trop grande
		# On retaille l'image en gardant le ratio entre 
		# le min (si l'image ne rentre pas dans le cadre), le max (sinon) de :
		#         * La largeur de la fenetre
		#         * La largeur de l'image
		#         * La hauteur de la fenetre
		#         * La hauteur de l'image
		if (self.preview.height() < self.height()) and (self.preview.width() < self.width()):
			width=max(self.preview.width(), self.width())
			height=max(self.preview.height(), self.height())
		else :
			width=min(self.preview.width(), self.width())
			height=min(self.preview.height(), self.height())

		if self.gif:
			self.redimGif(width - 5, height - 5)
		else:
			resultat = self.preview.get_preview().scaled(width - 5, height - 5, Qt.KeepAspectRatio, self.modeTransformation)
			debug(u"Preview : %s, taille : %d, %d" % (self.preview.get_imageName(), self.preview.width(), self.preview.height()))
			self.factor = min(float(self.height())/self.preview.height(), float(self.width())/self.preview.width())
		
		#-- On met l'image et on redimensionne le Label pour les images simples
		if not self.gif:
			self.imageLabel.setPixmap(resultat)


			
	
	def setTailleReelle(self):
		"Fonction d'affichage en taille réelle"
		self.preview.origin()

		width, height = self.preview.width(), self.preview.height()

		# On redimensionne le label à la taille de l'image
		if self.gif:
			self.redimGif(width, height)
		else:
			self.imageLabel.setPixmap(self.preview.get_preview())
		self.factor = 1
	
	def zoomAvant(self):
		"Fonction de zoom avant 25%"
		
		# On redimensionne l'image à 125% de la taille actuelle
		factor = 5/4. * self.factor

		width = int(self.preview.width() * factor)
		height = int(self.preview.height() * factor)

		if self.gif:
			self.redimGif(width, height)
		else:
			image = self.preview.get_preview().scaled(width, height, Qt.KeepAspectRatio)
			self.imageLabel.setPixmap(image)
		self.factor = factor
	
	def zoomArriere(self):
		"Fonction de zoom arrière 25%"
		
		# On redimensionne l'image à 75% de la taille actuelle
		factor = 3/4. * self.factor

		width = int(self.preview.width() * factor)
		height = int(self.preview.height() * factor)

		if self.gif:
			self.redimGif(width, height)
		else:
			image = self.preview.get_preview().scaled(width, height, Qt.KeepAspectRatio)
			self.imageLabel.setPixmap(image)
		self.factor = factor
	
	def startPauseGif(self):
		"Démarrer/mettre en pause l'animation de l'image gif"
		if self.movie.state() == QMovie.NotRunning:
			self.movie.start()
		else:
			self.movie.setPaused(self.movie.state() != QMovie.Paused)
	
	def stopGif(self):
		"Arrêter l'animation de l'image gif"
		if self.movie.state() != QMovie.NotRunning:
			self.movie.stop()
	
	def redimGif(self, width, height):
		"""Changer la taille d'affichage du gif en prenant soin d'arrêter et de
		reprendre l'animation si nécessaire.
		Il y a un petit bogue d'affichage sur la redimension (il disparait en changeant
		d'onglet ou de cadre et en revenant.
		"""
		etatInitial = self.movie.state()
		if etatInitial == QMovie.Running:
			self.movie.stop()
		self.movie.setScaledSize(QSize(width, height))
		if etatInitial == QMovie.Running:
			self.movie.start()
		else:
			# On redémarre le gif sinon l'image n'est pas actualisée et reste à la même taille
			self.movie.start()
			self.movie.stop()
	
	def isGif(self):
		"Indique si l'image affichée est un gif. Le test est effectué sur l'extension du fichier"
		return self.gif
	
	def setImage(self, img=None, fauxChemin=None, anim=False):
		"""Fonction de mise en place de l'image.
		Le faux chemin est utile pour dissocier le chemin que verra l'utilisateur
		du chemin de l'image affichée. Ils sont différents uniquement lorsqu'une image
		composite est affichée (cadres masque alpha 3D et image composite).
		L'argument "anim" dit si une image gif doit être animée.
		"""
		
		if not img:
			img = "Icones" + os.sep + "avant-image.png"
			self.setToolTip(_(u"image d'accueil"))
			self.setTailleReelle()
			return
		elif fauxChemin:
			self.setToolTip(fauxChemin)
		else:
			self.setToolTip(img)
		
		# Chargement du gif le cas échéant
		if isinstance(img, str) or isinstance(img, unicode):
			# En général
			extension = os.path.splitext(img)[1]
		elif isinstance(img, QString):
			# Pour selectWidget.py principalement
			extension = "." + QFileInfo(img).suffix()
		if extension == ".gif":
			self.menuStartPauseGif.setVisible(True)
			self.menuStopGif.setVisible(True)
			self.gif = 1
			self.movie = QMovie(img)
			# On démarre le gif de toute façon sinon l'image n'est pas visible
			self.movie.start()
			if not anim:
				self.movie.stop()
			self.imageLabel.setMovie(self.movie)
		else:
			# Pour des images non-gif, on cache les menus d'animation
			self.menuStartPauseGif.setVisible(False)
			self.menuStopGif.setVisible(False)
			self.gif = 0
		

		# Visiblement sous windows la taille du QScrollArea renvoie 0,
		# on passe par l'Objet à l'intérieur pour obtenir la taille de l'image à créer
		self.preview = EkdPreview(img, self.width(), 0, 10, False, True, True) #(chemin, largeur, qualité, cache?, keepRatio?, magnify? )

		# Par défault on charge en taille fenetre
		self.setTailleFenetre()


class VisionneurEvolue(QDialog):
	"""Le visionneur est une évolution de la classe VisionneurImagePourEKD.
	Il lui ajoute un cadre et des boutons pour manipuler son image
	La fonction visioneur permet d'accéder à la VisionneurImagePourEKD depuis l'extérieur"""
	
	def __init__(self, img = None):
		QDialog.__init__(self)
		self.setWindowTitle(_(u"Ekd : Visionneur d'images "))		
		self.img = img
		
		# VBox
		vbox = QVBoxLayout()
		hbox = QHBoxLayout()
		self.setLayout(vbox)
		
		# Visioneur
		self.visionneur = VisionneurImagePourEKD(self.img)
		if self.img:
			self.setWindowTitle(self.img)
		self.setTailleFenetre = self.visionneur.setTailleFenetre
		vbox.addWidget(self.visionneur)
		vbox.addLayout(hbox)
		
		# Boutons
		
		iconTaille = 32
		flat = 1
		
		#--Bouton taille fenetre
		boutTailleFenetre=QPushButton()
		boutTailleFenetre.setIcon(QIcon("Icones" + os.sep + "fenetre.png"))
		boutTailleFenetre.setIconSize(QSize(iconTaille, iconTaille))
		boutTailleFenetre.setToolTip(_(u"Ajuster à la fenêtre"))
		boutTailleFenetre.setFlat(flat)
		hbox.addWidget(boutTailleFenetre)
		self.connect(boutTailleFenetre, SIGNAL("clicked()"), self.visionneur.setTailleFenetre)
		
		#--Bouton taille reel
		boutTailleReelle=QPushButton()
		boutTailleReelle.setIcon(QIcon("Icones" + os.sep + "taillereelle.png"))
		boutTailleReelle.setIconSize(QSize(iconTaille, iconTaille))
		boutTailleReelle.setToolTip(_(u"Taille réelle"))
		boutTailleReelle.setFlat(flat)
		hbox.addWidget(boutTailleReelle)
		self.connect(boutTailleReelle, SIGNAL("clicked()"), self.visionneur.setTailleReelle)
		
		#--Bouton zoom avant
		boutZoomAvant=QPushButton()
		boutZoomAvant.setIcon(QIcon("Icones" + os.sep + "zoomplus.png"))
		boutZoomAvant.setIconSize(QSize(iconTaille, iconTaille))
		boutZoomAvant.setToolTip(_(u"Zoom avant"))
		boutZoomAvant.setFlat(flat)
		hbox.addWidget(boutZoomAvant)
		self.connect(boutZoomAvant, SIGNAL("clicked()"), self.visionneur.zoomAvant)
		
		#--Bouton zoom arrière
		boutZoomArriere=QPushButton()
		boutZoomArriere.setIcon(QIcon("Icones" + os.sep + "zoommoins.png"))
		boutZoomArriere.setIconSize(QSize(iconTaille, iconTaille))
		boutZoomArriere.setToolTip(_(u"Zoom arrière"))
		boutZoomArriere.setFlat(flat)
		hbox.addWidget(boutZoomArriere)
		self.connect(boutZoomArriere, SIGNAL("clicked()"), self.visionneur.zoomArriere)
		
		hbox.addStretch()
		
		# Fermer
		supprimer = QToolButton()
		supprimer.setIcon(QIcon("Icones" + os.sep + "revenir.png"))
		supprimer.setIconSize(QSize(32, 32))
		supprimer.setText(QString(_(u"Revenir")))
		supprimer.setAutoRaise(1)
		supprimer.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.connect(supprimer, SIGNAL("clicked()"), self.close)
		hbox.addWidget(supprimer)
			
		# Infos
		infos = QToolButton()
		infos.setIcon(QIcon("Icones" + os.sep + "icone_info_128.png"))
		infos.setIconSize(QSize(32, 32))
		infos.setText(QString(_(u"infos")))
		infos.setAutoRaise(1)
		infos.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.connect(infos, SIGNAL("clicked()"), self.infos)
		hbox.addWidget(infos)
		
		# Fonctions de test et de lecture du gif
		self.isGif = self.visionneur.isGif
		self.startPauseGif = self.visionneur.startPauseGif
	
	def setImage(self, img=None, fauxChemin=None, anim=False):
		"Intégration de l'image dans le QScrollArea"
		self.img = img
		self.setWindowTitle(self.img)
		self.visionneur.setImage(self.img, fauxChemin, anim)
	
	def redimenFenetre(self, tailleFenetrePrincipale, ratioLargeur = 0.8, ratioHauteur = 1):
		"Redimensionne la fenêtre en fonction de la taille de la fenêtre principale"
		largeur = ratioLargeur * tailleFenetrePrincipale().width()
		hauteur = ratioHauteur * tailleFenetrePrincipale().height()
		self.resize(largeur, hauteur)
	
	def infos(self):
		"Affiche des infos sur le fichier"
		
		info = InfosImage(self.img)
		info.exec_()


class InfosImage(QDialog):
	"Affiche les informations de l'image dans une boite de dialogue"
	
	def __init__(self, img = None):
		QDialog.__init__(self)
		self.setWindowTitle(_(u"Information sur l'image : "))
		def lTab(param, valeur):
			"renvoie une ligne du tableau"
			return "<tr><td>"+param+"</td><td>"+unicode(valeur)+"</td></tr>"
		
		vbox = QVBoxLayout()
		self.setLayout(vbox)
		
		self.img = img
		img = Image.open(self.img)
		
		txt = '<html><center>' + _(u"Emplacement") + ' : ' + self.img + '<br /><br />' + \
			"<table>" + \
			lTab(_(u"Format"), img.format) + \
			lTab(_(u"Mode"), img.mode) + \
			lTab(_(u"Largeur (px)"), img.size[0]) + \
			lTab(_(u"Hauteur (px)"), img.size[1]) + \
			lTab(_(u"Nombre de pixels (px)"), img.size[0] * img.size[1]) + \
			lTab(_(u"Poids de l'image"), str(float(os.path.getsize(self.img)/1000))+' ko'+'\n') + \
			"</table></center></html>"
			
		## Ligne Poids de l'image ###########################
		
		label = QLabel(txt)
		if PYQT_VERSION_STR >= "4.1.0":
			label.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
		vbox.addWidget(label)
		
		boutonFermer = QPushButton(_(u"Revenir"))
		boutonFermer.setIcon(QIcon("Icones" + os.sep + "revenir.png"))
		self.connect(boutonFermer, SIGNAL('clicked()'), SLOT('close()'))
		#############################################################################
		
		vbox.addWidget(boutonFermer)
		#############################################################################
