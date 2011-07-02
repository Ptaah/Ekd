#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
import random, string, locale, gettext
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurImagePourEKD
from gui_modules_image.image_base import Base
from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage 
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue

# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

if sys.version_info[:2] < (2, 5):
	def partial(func, arg):
		def callme():
			return func(arg)
		return callme
else:
	from functools import partial

# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Nouvelle fenêtre d'aide ######
from gui_modules_common.EkdWidgets import EkdAide

PointSize = 10

FORMAT = "JPEG (*.jpg *.JPG *.jpeg *.JPEG);;PNG (*.png *.PNG);;GIF (*.gif *.GIF)\
	;;BMP (*.bmp *.BMP);;SGI (*.sgi *.SGI);;TIF (*.tif *.TIF);;TARGA (*.tga *.TGA)\
	;;PNM (*.pnm *.PNM);;PPM (*.ppm *.PPM);;Tous les fichiers (*.*)"


class TextItemDlg(QDialog):
	"Boite de dialogue de texte"
	def __init__(self, item=None, position=None, scene=None,
			parent=None, z=1):
		QDialog.__init__(self, parent)
		
		self.item = item
		self.position = position
		self.scene = scene
		self.z = z
		
		self.editor = QTextEdit()
		self.editor.setAcceptRichText(False)
		self.editor.setTabChangesFocus(True)
		editorLabel = QLabel(_(u"&Texte:"))
		editorLabel.setBuddy(self.editor)
		self.fontComboBox = QFontComboBox()
		self.fontComboBox.setCurrentFont(QFont("Sans Serif", PointSize))
		fontLabel = QLabel(_(u"&Police:"))
		fontLabel.setBuddy(self.fontComboBox)
		self.fontSpinBox = QSpinBox()
		self.fontSpinBox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.fontSpinBox.setRange(6, 280)
		self.fontSpinBox.setValue(PointSize)
		fontSizeLabel = QLabel(_(u"&Taille:"))
		fontSizeLabel.setBuddy(self.fontSpinBox)
		self.fontComboColor = QComboBox()
		
		self.listComboColor=[	(_(u'défaut'),		QColor(QPalette.Text)),
					(_(u'noir'),		QColor('#000000')),
					(_(u'gris foncé'),	QColor('#808080')),
					(_(u'gris'),		QColor('#a0a0a4')),
					(_(u'gris clair'),	QColor('#c0c0c0')),
					(_(u'blanc'),		QColor('#ffffff')),
					(_(u'rouge'),		QColor('#ff0000')),
					(_(u'rouge foncé'),	QColor('#800000')),
					(_(u'vert'),		QColor('#00ff00')),
					(_(u'vert foncé'),	QColor('#008000')),
					(_(u'bleu'),		QColor('#0000ff')),
					(_(u'bleu foncé'),	QColor('#000080')),
					(_(u'cyan'),		QColor('#00ffff')),
					(_(u'cyan foncé'),	QColor('#008080')),
					(_(u'magenta'),		QColor('#ff00ff')),
					(_(u'magenta foncé'),	QColor('#800080')),
					(_(u'jaune'),		QColor('#ffff00')),
					(_(u'jaune foncé'),	QColor('#808000')),
						]
		
		font =QFont()
		fm = QFontMetricsF(font)
		hauteurPixmap = fm.height() - 2 # icones espacées de 2 pixels
		
		for i in self.listComboColor:
			pixmap = QPixmap(hauteurPixmap, hauteurPixmap)
			color = i[1]
			pixmap.fill(color)
			self.fontComboColor.addItem(QIcon(pixmap), i[0], QVariant(i[1]))
		fontColorLabel = QLabel(_(u"&Couleur:"))
		fontColorLabel.setBuddy(self.fontComboColor)
		self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
						QDialogButtonBox.Cancel)
		self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
		
		if self.item is not None:
			self.editor.setPlainText(self.item.toPlainText())
			self.fontComboBox.setCurrentFont(self.item.font())
			self.fontSpinBox.setValue(self.item.font().pointSize())
			for i, tColor in enumerate(self.listComboColor):
				if tColor[1]==self.item.defaultTextColor(): break
			self.fontComboColor.setCurrentIndex(i)
			self.editor.setTextColor(self.item.defaultTextColor())
		
		layout = QGridLayout()
		layout.addWidget(editorLabel, 0, 0)
		layout.addWidget(self.editor, 1, 0, 1, 9)
		layout.addWidget(fontLabel, 2, 0)
		layout.addWidget(self.fontComboBox, 2, 1, 1, 2)
		layout.addWidget(fontSizeLabel, 2, 3)
		layout.addWidget(self.fontSpinBox, 2, 4, 1, 2)
		layout.addWidget(fontColorLabel, 2, 6)
		layout.addWidget(self.fontComboColor, 2, 7, 1, 2)
		layout.addWidget(self.buttonBox, 3, 0, 1, 9)
		self.setLayout(layout)
	
		self.connect(self.fontComboBox,SIGNAL("currentFontChanged(QFont)"),self.updateUi)
		self.connect(self.fontSpinBox,SIGNAL("valueChanged(int)"),self.updateUi)
		self.connect(self.editor,SIGNAL("textChanged()"),self.updateUi)
		self.connect(self.fontComboColor, SIGNAL("activated(int)"),self.updateUi)
		self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
		self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)
		txt1,txt2=_(u"Texte sur images"),_(u"texte")
		if self.item is None: txt3 = _(u"Ajouter")
		else:  txt3 = _(u"Editer")
		self.setWindowTitle("%s - %s %s" % (txt1, txt3, txt2))
		self.updateUi()

	def updateUi(self):
		font = self.fontComboBox.currentFont()
		font.setPointSize(self.fontSpinBox.value())
		self.editor.document().setDefaultFont(font)
		i = self.fontComboColor.currentIndex()
		styleSheet = "QTextEdit{color: %s}" %self.fontHexaColor()
		self.editor.setStyleSheet(styleSheet)
		self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
			not self.editor.toPlainText().isEmpty())

	def accept(self):
		if self.item is None:
			self.item = TextItem("", self.position, self.scene, z=self.z)
		font = self.fontComboBox.currentFont()
		font.setPointSize(self.fontSpinBox.value())
		self.item.setFont(font)
		self.item.setHtml(self.editor.toHtml())
		self.item.setDefaultTextColor(self.fontColor())
		self.item.update()
		QDialog.accept(self)
	
	def fontColor(self):
		"Renvoie la couleur de la police en type QColor"
		i = self.fontComboColor.currentIndex()
		color = self.fontComboColor.itemData(i).toString()
		return QColor(color)
	
	def fontHexaColor(self):
		"Renvoie la couleur de la police en type hexadécimal"
		return self.fontColor().toRgb().name()


class TextItem(QGraphicsTextItem):
	"Item texte"
	def __init__(self, text, position, scene, font=QFont("Sans Serif", PointSize),
			color=QColor(0,0,0), rotation=0, z=1):
		QGraphicsTextItem.__init__(self, text)
		self.setFlags(QGraphicsItem.ItemIsSelectable|
				QGraphicsItem.ItemIsMovable)
		self.__rotation = 0
		self.setFont(font)
		self.setPos(position)
		self.setRotateR(rotation)
		self.setDefaultTextColor(color)
		scene.clearSelection()
		scene.addItem(self)
		self.setZValue(z)
		self.setSelected(True)
		#print "adresse classe", self
		EkdPrint(u"adresse classe %s" % self)

	def parentWidget(self):
		return self.scene().views()[0]
		
	def hexaColor(self):
		return self.defaultTextColor().toRgb().name()
	
	def mouseDoubleClickEvent(self, event):
		dialog = TextItemDlg(self, self.parentWidget())
		dialog.exec_()
	
	def setRotateR(self, rotation):
		self.__rotation += rotation
		#print self.__rotation
		EkdPrint(u"%s" % self.__rotation)
		while self.__rotation >= 360:
			self.__rotation -= 360
		self.rotate(rotation)
	
	def setRotateL(self, rotation):
		self.__rotation -= rotation
		#print self.__rotation
		EkdPrint(u"%s" % self.__rotation)
		while self.__rotation >= 360:
			self.__rotation -= 360
		self.rotate(-rotation)

	def getRotate(self):
		return self.__rotation


class BoxItem(QGraphicsItem):
	"Item boite rectangulaire"
	def __init__(self, position, scene, style=Qt.SolidLine, borderWidth=1, boxColor = QColor('#000000'),
			rect=None, rotation=0, z=1) :
		QGraphicsItem.__init__(self)
		self.setFlags(QGraphicsItem.ItemIsSelectable|
				QGraphicsItem.ItemIsMovable|
				QGraphicsItem.ItemIsFocusable)
		if rect is None:
			rect = QRectF(-10 * PointSize, -PointSize,
					20 * PointSize, 2 * PointSize)
		self.rect = rect
		self.style = style
		self.borderWidth = borderWidth
		self.boxColor = boxColor
		self.__rotation = 0
		self.setPos(position)
		self.setRotateR(rotation)
		scene.clearSelection()
		scene.addItem(self)
		self.setZValue(z)
		self.setSelected(True)
		self.setFocus()

	def parentWidget(self):
		return self.scene().views()[0]

	def boundingRect(self):
		return self.rect.adjusted(-2, -2, 2, 2)

	def paint(self, painter, option, widget):
		pen = QPen(self.style)
		pen.setColor(self.boxColor)
		pen.setWidth(self.borderWidth)
		if option.state & QStyle.State_Selected:
			pen.setColor(Qt.cyan)
		painter.setPen(pen)
		painter.drawRect(self.rect)

	def contextMenuEvent(self, event):
		wrapped = [] # indispensable mais je ne sais pas pourquoi
		#print "contextMenuEvent_contextMenuEvent_contextMenuEvent"
		EkdPrint(u"contextMenuEvent_contextMenuEvent_contextMenuEvent")
		menu = QMenu(self.parentWidget())
		for text, param in (
			(_(u"Contour &solide"), Qt.SolidLine),
			(_(u"Contour en &pointillets"), Qt.DashLine),
			(_(u"Contour en p&oints"), Qt.DotLine),
			(_(u"Contour en po&intillets et points"), Qt.DashDotLine),
			(_(u"Contour en pointillets et poin&ts (x2)"), Qt.DashDotDotLine),
			(_(u"Contour en noir"), QColor('#000000')),
			(_(u"Contour en rouge"), QColor('#FF0000')),
			(_(u"Contour en vert"), QColor('#00FF00')),
			(_(u"Contour en bleu"), QColor('#0000FF')),
			(_(u"Contour en jaune"), QColor('#FFFF00'))) :
			wrapper = partial(self.setStyle, param)
			wrapped.append(wrapper)
			menu.addAction(text, wrapper)
		menu.exec_(event.screenPos())

	def setStyle(self, style):
		if style in [Qt.SolidLine, Qt.DashLine, Qt.DotLine, Qt.DashDotLine, Qt.DashDotDotLine] :
			self.style = style
		else :
			self.boxColor = style
		self.update()

	def keyPressEvent(self, event):
		factor = PointSize / 4
		changed = False
		if event.modifiers() & Qt.ShiftModifier:
			if event.key() == Qt.Key_Left:
				self.rect.setRight(self.rect.right() - factor)
				changed = True
			elif event.key() == Qt.Key_Right:
				self.rect.setRight(self.rect.right() + factor)
				changed = True
			elif event.key() == Qt.Key_Up:
				self.rect.setBottom(self.rect.bottom() - factor)
				changed = True
			elif event.key() == Qt.Key_Down:
				self.rect.setBottom(self.rect.bottom() + factor)
				changed = True
		# Taille du trait
		if event.modifiers() & Qt.ControlModifier :
			if event.key() == Qt.Key_Up:
				self.borderWidth += 1
				changed = True
			if event.key() == Qt.Key_Down:
				self.borderWidth -= 1
				if self.borderWidth < 1 :
					self.borderWidth = 1
				changed = True
		if changed:
			self.update()
		else:
			QGraphicsItem.keyPressEvent(self, event)
	
	def setRotateR(self, rotation):
		self.__rotation += rotation
		while self.__rotation >= 360:
			self.__rotation -= 360
		self.rotate(rotation)
	
	def setRotateL(self, rotation):
		self.__rotation -= rotation
		while self.__rotation >= 360:
			self.__rotation -= 360
		self.rotate(-rotation)

	def getRotate(self):
		return self.__rotation


class GraphicsPixmapItem(QGraphicsPixmapItem):
	"Item image"
	def __init__(self, pixmap, position, rotation=0, z=1):
		QGraphicsPixmapItem.__init__(self, pixmap)
		self.__rotation = 0
		self.setPos(position)
		self.setRotateR(rotation)
		self.setZValue(z)
		
	def setRotateR(self, rotation):
		self.__rotation += rotation
		while self.__rotation >= 360:
			self.__rotation -= 360
		self.rotate(rotation)

	def setRotateL(self, rotation):
		self.__rotation -= rotation
		while self.__rotation >= 360:
			self.__rotation -= 360
		self.rotate(-rotation)
	
	def getRotate(self):
		return self.__rotation


class GraphicsView(QGraphicsView):

	def __init__(self, parent=None):
		QGraphicsView.__init__(self, parent)
		self.setDragMode(QGraphicsView.RubberBandDrag)
		self.setRenderHint(QPainter.Antialiasing)
		self.setRenderHint(QPainter.TextAntialiasing)
	
	def wheelEvent(self, event):
		factor = 1.41 ** (-event.delta() / 240.0)
		self.scale(factor, factor)


class Image_Divers_TxtSurImg(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Texte sur images
	# -----------------------------------
	
	ZOOM_MOINS,ZOOM_PLUS,ZOOM_REEL,ZOOM_FIT = range(4)

	def __init__(self, statusBar, geometry):
		QWidget.__init__(self)
		
		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()

		# Gestion de la configuration via EkdConfig
		# Paramètres de configuration
		self.config = EkdConfig
		self.nProc = 0

		vbox = QVBoxLayout() # Layout principal
		# Modification de structure pour mettre ce module conforme au nouveau design.
		# 1.Ajout du tab principal
		self.tabwidget=QTabWidget()

		# 2. Création du tab de sélection de fichier source - basé sur le widget de sélection standard
		self.afficheurImgSource=SelectWidget(geometrie = geometry)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.
		
		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifImgSource)
		self.connect(self.afficheurImgSource, SIGNAL("pictureSelected()"), self.modifImgSource)
		self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))

		# 3. Création du tab réglages

		self.listFileNames = []
		self.z = 1 # "Hauteur" initiale des graphicsItems ajoutés
		self.baseImage = None
		self.copiedItem = QByteArray()
		self.pasteOffset = 5
		self.prevPoint = QPoint()
		self.addOffset = 5
		self.borders = []

		self.widReglage = QWidget()

		self.view = GraphicsView()
		self.scene = QGraphicsScene(self)
		self.view.setScene(self.scene)
		
		# Image de fond
		self.background = QGraphicsPixmapItem()
		
		buttonLayout = QVBoxLayout()
		# Liste qui servira à activer/désactiver les boutons
		self.buttonsList = []
		# Liste des boutons à éviter sous PyQt4.1.0 (ex.ubuntu feisty) à cause d'un bogue
		# sur les fonctions associées
		self.buttonListeNoireFeisty = []
		self.zoomPlus = partial(self.zoom, Image_Divers_TxtSurImg.ZOOM_PLUS)
		self.zoomMoins = partial(self.zoom, Image_Divers_TxtSurImg.ZOOM_MOINS)
		self.zoomReel = partial(self.zoom, Image_Divers_TxtSurImg.ZOOM_REEL)
		self.zoomFit = partial(self.zoom, Image_Divers_TxtSurImg.ZOOM_FIT)
		layoutEdition = QHBoxLayout()
		for text, slot, icon in (
			(_(u"Ajouter &Texte"), self.addText, "Icones/text_add.png"),
			(_(u"Ajouter &Boite"), self.addBox, "Icones/ajouter_shape.png"),
			(_(u"Ajouter Ima&ge"), self.addPixmap, "Icones/image.png"),
			(_(u"C&opier"), self.copy, "Icones/copy.png"),
			(_(u"Cou&per"), self.cut, "Icones/cut.png"),
			(_(u"Co&ller"), self.paste, "Icones/paste.png"),
			(_(u"&Effacer..."), self.delete, "Icones/bin.png"),
			(_(u"&Monter"), self.upItem, "Icones/up.png"),
			(_(u"Descen&dre"), self.downItem, "Icones/down.png"),
			(_(u"Pivoter &Droite"), self.rotateR, "Icones/rotationd.png"),
			(_(u"Pivoter &Gauche"), self.rotateL, "Icones/rotationg.png"),
			(_(u"Zoom &fit"), self.zoomFit, "Icones/fenetre.png"),
			(_(u"Zoom &avant"), self.zoomPlus, "Icones/zoomplus.png"),
			(_(u"Zoom a&rrière"), self.zoomMoins, "Icones/zoommoins.png"),
			(_(u"Zoom &100%"), self.zoomReel, "Icones/taillereelle.png"),
			):
			if text in [_(u"C&opier"),_(u"Cou&per"),_(u"Co&ller"),_(u"&Effacer...")]:
				button = QToolButton()
				button.setIcon(QIcon(icon))
				button.setIconSize(QSize(16, 16))
				button.setToolTip(text)
				layoutEdition.addWidget(button)
				self.buttonListeNoireFeisty.append(button)
			else :
				if icon != None :
					button = QPushButton(QIcon(icon), text)
				else :
					button = QPushButton(text)
				buttonLayout.addWidget(button)

			button.setEnabled(False)
			self.buttonsList.append(button)
			self.connect(button, SIGNAL("clicked()"), slot)

			if text == _(u"&Effacer...") : # provisoire...
				buttonLayout.addLayout(layoutEdition)
				buttonLayout.addStretch(0)
			if text == _(u"Pivoter &Gauche"): # prochainement...
				buttonLayout.addStretch(0)
		buttonLayout.addStretch()

		# ComboBox de choix du format de sortie
		self.choixSortie = QComboBox()
		self.listFormatSortie = []
		self.indexFormatSortie = 0
		for text, format, extension, compression in (
				(_(u"PNG"),"PNG",u".png", 1),
				(_(u"JPEG"),"JPEG",u".jpg", 2),
				(_(u"BMP"),"BMP",u".bmp", 0),
				(_(u"TIFF"),"TIFF",u".tiff", 0),
				(_(u"PPM"),"PPM",u".ppm", 0)) :
			self.choixSortie.addItem(text)
			self.listFormatSortie.append([format,extension,compression])
		self.connect(self.choixSortie, SIGNAL("currentIndexChanged(int)"), self.setFormatSortie)
		buttonLayout.addWidget(self.choixSortie)
		
		self.labelQualite = QLabel(_(u"Qualité de l'image"))
		self.cbQualite = QComboBox()
		self.cbQualite.addItems(["0","10","20","30","40","50","60","70","80","85","90","95","100"])
		self.cbQualite.setCurrentIndex(8)
		hboxQ = QHBoxLayout()
		hboxQ.addWidget(self.labelQualite)
		hboxQ.addWidget(self.cbQualite)
		buttonLayout.addLayout(hboxQ)
		self.labelQualite.hide()
		self.cbQualite.hide()

		hbox = QHBoxLayout()
		hbox.addWidget(self.view, 1)
		hbox.addLayout(buttonLayout)
		self.widReglage.setLayout(hbox)
		self.tabwidget.addTab(self.widReglage, _(u"Réglage"))
		
		# 4. Création du tab de visualisation du résultat
		self.afficheurImgDestination=Lecture_VisionImage(statusBar)
		self.tabwidget.addTab(self.afficheurImgDestination, _(u'Visualisation des images créées'))

		# 5. Création du tab Info
		self.Logs = QTextEdit() # Zone d'affichage des infos (Zone acceptant le formatage HTML et avec assenceur automatique si nécessaire)
		self.tabwidget.addTab(self.Logs, _(u'Infos'))
		
		#-----------------
		# widgets du bas
		#-----------------
		
		# Boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones/icone_aide_128.png"))
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
		
		self.boutAppliquer=QPushButton(_(u"Appliquer"))
		self.boutAppliquer.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		
		# Bouton inactif au départ
		self.boutAppliquer.setEnabled(False)
		
		self.connect(self.boutAppliquer, SIGNAL("clicked()"), self.appliquer)
		
		# Ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		
		hbox=QHBoxLayout()
		hbox.addWidget(boutAide)
		hbox.addStretch()
		hbox.addWidget(self.boutAppliquer)

		vbox.addWidget(self.tabwidget)
		vbox.addWidget(ligne)
		vbox.addLayout(hbox)

		self.setLayout(vbox)


	def setFormatSortie(self, index) :
		self.indexFormatSortie = index
		if self.listFormatSortie[index][2] == 2 :
			self.labelQualite.show()
			self.cbQualite.show()
		else :
			self.labelQualite.hide()
			self.cbQualite.hide()


	def modifImgSource(self, i=True):
		"""On active ou désactive les boutons d'action et on recharge le pseudo-aperçu de planche-contact
		en fonction du nombre d'images présentes dans le widget de sélection"""
		###self.displayImg()
		self.boutAppliquer.setEnabled(i)
		selectedImg = self.afficheurImgSource.getFile()
		if self.setBackgroundImg(selectedImg) :
			if PYQT_VERSION_STR != "4.1.0":
				for button in self.buttonsList:
					button.setEnabled(True)
			else:
				# Pour empêcher le bogue de PyQt4.1.0 Feisty
				for button in self.buttonsList:
					if button not in self.buttonListeNoireFeisty:
						button.setEnabled(True)
			self.zoom(Image_Divers_TxtSurImg.ZOOM_FIT)


	def setBackgroundImg (self, selectedImg) :
		if selectedImg and selectedImg != self.baseImage :
			self.baseImage = selectedImg
			# Création de l'objet QImage de l'image de base
			pixmap = QPixmap(self.baseImage)
			# Suppression de la précédente image si elle existait
			if not self.background.pixmap().isNull():
				self.scene.removeItem(self.background)
		
			# Ajout de la nouvelle image
			self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
			self.background = self.scene.addPixmap(pixmap)
			self.background.setZValue(0)
			return True
		else : return False


	def position(self, pixmap=None):
		#print "QCursor.pos()", QCursor.pos().x(), QCursor.pos().y()
		EkdPrint(u"QCursor.pos() %s %s" % (QCursor.pos().x(), QCursor.pos().y()))
		point = self.mapFromGlobal(QCursor.pos())
		#print "self.mapFromGlobal(QCursor.pos()", point.x(), point.y()
		EkdPrint(u"self.mapFromGlobal(QCursor.pos() %s %s" % (point.x(), point.y()))
		if not self.view.geometry().contains(point) or pixmap:
			#print "if not self.view.geometry().contains(point) or pixmap"
			EkdPrint(u"if not self.view.geometry().contains(point) or pixmap")
			coord = random.randint(36, 144)
			point = QPoint(coord, coord)
		else:
			#print "else de if not self.view..."
			EkdPrint(u"else de if not self.view...")
			if point == self.prevPoint:
				#print "if point == self.prevPoint"
				EkdPrint(u"if point == self.prevPoint")
				point += QPoint(self.addOffset, self.addOffset)
				self.addOffset += 5
			else:
				#print "else de if point..."
				EkdPrint(u"else de if point...")
				self.addOffset = 5
				self.prevPoint = point
		#print "point", point.x(), point.y(), '\n'
		EkdPrint("upoint %s %s\n" % (point.x(), point.y()))
		# La position du point haut-gauche du rectangle encadrant le texte
		#print "self.view.mapToScene(point)", self.view.mapToScene(point).x(), self.view.mapToScene(point).y()
		EkdPrint(u"self.view.mapToScene(point) %s %s" % (self.view.mapToScene(point).x(), self.view.mapToScene(point).y()))
		return self.view.mapToScene(point)


	def addText(self):
		self.z += 1
		dialog = TextItemDlg(position=self.position(), scene=self.scene, parent=self, z=self.z)
		dialog.exec_()
	

	def addBox(self):
		self.z += 1
		BoxItem(self.position(), self.scene, z=self.z)
	

	def addPixmap(self):
		formats = ["*.%s" % unicode(format).lower() \
			for format in QImageReader.supportedImageFormats()]
		path = self.base.getRepSource(self.config)
		txt = _(u"Fichiers Image")
		fname = unicode(QFileDialog.getOpenFileName(self, "Ouvrir des images",
			path, "%s (%s);;%s" %(txt, " ".join(formats), FORMAT)))
		if not fname: return
		self.base.setRepSource(self.config, fname)
		self.createPixmapItem(QPixmap(fname), self.position(pixmap=True))
	

	def createPixmapItem(self, pixmap, position, rotation=0):
		self.z += 1
		item = GraphicsPixmapItem(pixmap, position, rotation, z=self.z)
		item.setFlags(QGraphicsItem.ItemIsSelectable|
			QGraphicsItem.ItemIsMovable)
		self.scene.clearSelection()
		self.scene.addItem(item)
		item.setZValue(self.z+1)
		self.z += 1
		item.setSelected(True)
	

	def selectedItem(self):
		items = self.scene.selectedItems()
		if len(items) == 1:
			return items[0]
		return None
	

	def copy(self):
		item = self.selectedItem()
		if item is None:
			return
		self.copiedItem.clear()
		self.pasteOffset = 5
		stream = QDataStream(self.copiedItem, QIODevice.WriteOnly)
		self.writeItemToStream(stream, item)
	

	def cut(self):
		item = self.selectedItem()
		if item is None:
			return
		self.copy()
		self.scene.removeItem(item)
		del item
	

	def paste(self):
		if self.copiedItem.isEmpty():
			return
		stream = QDataStream(self.copiedItem, QIODevice.ReadOnly)
		self.readItemFromStream(stream, self.pasteOffset)
		self.pasteOffset += 5


	def upItem(self) :
		'''Fonction pour relever le/les item(s) sélectionné(s))'''
		for item in self.scene.selectedItems():
			z = item.zValue()
			item.setZValue(z+1)


	def downItem(self) :
		'''Fonction pour descendre le/les item(s) sélectionné(s))'''
		for item in self.scene.selectedItems():
			z = item.zValue()
			if z>1 : # Pour éviter de placer un élément en dessous de l'image source qui est au niveau 0.
				item.setZValue(z-1)
	

	def rotateR(self):
		for item in self.scene.selectedItems():
			item.setRotateR(22.5)
	

	def rotateL(self):
		for item in self.scene.selectedItems():
			item.setRotateL(22.5)
	

	def delete(self):
		items = self.scene.selectedItems()
		#print "items sélectionnés", items ###
		EkdPrint(u"items sélectionnés %s" % items)
		txt1,txt2=_(u"Effacer"),_(u"élément")
		if len(items) != 1: s = "s"
		else: s = ""
		if len(items) and QMessageBox.question(self,
			_(u"Texte sur images - Effacer"),
			"%s %d %s%s?" % (txt1,len(items),txt2,s),
			QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
			while items:
				item = items.pop()
				#print "item?", item
				EkdPrint(u"item? %s" % item)
				self.scene.removeItem(item)
				del item
	
	
	def readItemFromStream(self, stream, offset=0):
		type_ = QString()
		position = QPointF()
		stream >> type_ >> position
		rotation = stream.readInt16()
		if offset:
			position += QPointF(offset, offset)
		if type_ == "Text":
			text = QString()
			font = QFont()
			color = QColor()
			stream >> text >> font >> color
			self.z += 1
			TextItem(text, position, self.scene, font, color, rotation, self.z)
		elif type_ == "Pixmap":
			pixmap = QPixmap()
			stream >> pixmap
			self.createPixmapItem(pixmap, position, rotation)
		elif type_ == "Box":
			rect = QRectF()
			stream >> rect
			style = Qt.PenStyle(stream.readInt16())
			borderWidth = stream.readInt16()
			boxColor = QColor()
			stream >> boxColor 
			self.z += 1
			BoxItem(position, self.scene, style, borderWidth, boxColor, rect, rotation, self.z)
	

	def writeItemToStream(self, stream, item):
		if isinstance(item, QGraphicsTextItem):
			stream << QString("Text") << item.pos()
			stream.writeInt16(item.getRotate())
			stream << item.toPlainText() << item.font() << item.defaultTextColor()
		elif isinstance(item, QGraphicsPixmapItem):
			stream << QString("Pixmap") << item.pos()
			stream.writeInt16(item.getRotate())
			stream << item.pixmap()
		elif isinstance(item, BoxItem):
			stream << QString("Box") << item.pos()
			stream.writeInt16(item.getRotate())
			stream << item.rect
			stream.writeInt16(item.style)
			stream.writeInt16(item.borderWidth)
			stream << item.boxColor
	

	def appliquer(self):
		"Conversion des images: ajout de textes, images et boites"
		
		# Utilisation de la nouvelle boîte de dialogue de sauvegarde
		suffix=""
                fname = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		fname = fname.getFile()

		if not fname: return

		# Gestion de l'extension
		if fname.endswith(self.listFormatSortie[self.indexFormatSortie][1]) :
			fname = fname[:-len(self.listFormatSortie[self.indexFormatSortie][1])]

		# Progression
		progress=QProgressDialog(_(u"Conversion en cours..."), _(u"Arrêter"), 0, 100)
		progress.setWindowTitle(_(u'EnKoDeur-Mixeur. Fenêtre de progression'))
		progress.show()
		progress.setValue(0)

		# Module traitement par lot
		lstImg = self.afficheurImgSource.getFiles()
		nbrImg = len(lstImg)
		lstFname = []
		k = 1
		for bimg in lstImg :
			self.setBackgroundImg(bimg)
			# Enregistrement de l'image composée
			imgDim = self.scene.sceneRect()
			imgFinal = QImage(imgDim.width(), imgDim.height(), QImage.Format_ARGB32)
			self.scene.clearSelection()
			self.scene.render(QPainter(imgFinal))
			if self.listFormatSortie[self.indexFormatSortie][2] == 2 : # Qualité = valeur de la combobox
				qu = int(self.cbQualite.currentText())
			elif self.listFormatSortie[self.indexFormatSortie][2] == 0 : # Qualité 100 pour les images sans compression
				qu = 100
			else : # Compression maximale pour les images PNG car format non destructif.
				qu = 0

			if imgFinal.save(fname+string.zfill(str(k), 5)+self.listFormatSortie[self.indexFormatSortie][1], self.listFormatSortie[self.indexFormatSortie][0], qu) :
				lstFname.append(fname+string.zfill(str(k), 5)+self.listFormatSortie[self.indexFormatSortie][1])
			else :
				#print "Erreur lors de la sauvegarde de l'image"
				EkdPrint(u"Erreur lors de la sauvegarde de l'image")
			progress.setValue(int(100*k/nbrImg))
			k += 1
		# Affichage du résultat
		self.afficheurImgDestination.cheminImage = u""
		self.afficheurImgDestination.updateImages(lstFname)
		# Mise à jour du log
		self.updateLog(lstImg, lstFname)


	def updateLog(self, images, sorties) :
		"""Fonction pour la mise à jour des informations de log données à l'utilisateur en fin de process sur les données entrées, et le résultat du process"""
		msgIm = _(u"<p>####################################<br># Image(s) chargée(s)<br>####################################</p>")
		for i in images :
			msgIm += unicode(i)+u"<br>"

		msgOut = _(u"<br><p>####################################<br># Fichier(s) de sortie<br>####################################</p>")
		for s in sorties :
			msgOut += unicode(s)+u"<br>"

		self.Logs.setHtml(QString(msgIm+msgOut))


	def zoom(self, val):
		if val==Image_Divers_TxtSurImg.ZOOM_PLUS:
			self.view.scale(1.2, 1.2)
		elif val==Image_Divers_TxtSurImg.ZOOM_MOINS:
			self.view.scale(0.8, 0.8)
		elif val==Image_Divers_TxtSurImg.ZOOM_REEL:
			self.view.resetTransform()
		elif val==Image_Divers_TxtSurImg.ZOOM_FIT :
			self.view.fitInView(self.background, Qt.KeepAspectRatio)
	

	def afficherAide(self):
		"Boîte de dialogue de l'aide"

		messageAide = EkdAide(parent=self)
		messageAide.setText(_(u"<p><b>Ici vous pouvez ajouter du texte, des cadres ou des petites images comme des logos sur des images. Cela peut être utile pour <i>signer</i> ou indiquer la provenance d'un lot d'images (avant par exemple de les diffuser sur internet).</b></p><p><b>De nombreux réglages vous sont proposés (dans l'onglet 'Réglage') afin d'inscrire et disposer comme bon vous semble du texte sur un lot d'images.</b></p>\
		\
		<p>Dans l'onglet <b>Image(s) source</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>. Toujours dans l'onglet <b>Image(s) source</b> sélectionnez une des miniatures.</p><p>Allez maintenant dans l'onglet <b>Réglages</b>, l'image de la miniature que vous venez de sélectionner est affichée. Vous pouvez zoomer ou dézoomer l'image avec le bouton du milieu de la souris. Dans cet onglet <b>Réglages</b> (et sur la droite), vous voyez toute une série de boutons (qui correspondent aux différentes actions que vous pouvez effectuer sur l'image ou sur le texte que vous allez écrire sur cette image). Nous allons maintenant, simplement ajouter un texte, pour ce faire cliquez sur le bouton <b>Ajouter texte</b>, la boîte de dialogue <b>Texte sur images - Ajouter texte</b> apparaît, avant d'écrire quoi que ce soit (dans le champ réservé à cet effet), faites le choix de la <b>Police</b>, de la <b>Taille</b> et de la <b>Couleur</b>, écrivez maintenant votre texte, une fois fait, cliquez sur le bouton <b>OK</b>. Vérifiez que votre texte ne dépasse pas de l'image (si cela est la cas, double-cliquez sur le texte en question, la boîte de dialogue de saisie va réapparaître) et faites ce qu'il faut ... . Vous pouvez positionner le texte sur l'image en bougeant le cadre où se trouve le texte avec la souris. Vous pouvez si vous le désirez ajouter une boîte (par le bouton <b>Ajouter Boîte</b>). Pour choisir le contour de la boîte, faites un clic droit dessus, un menu vous permettra de choisir le contour que vous désirez. En ce qui concerne la taille de la boîte, il est possible de régler la taille de celle-ci en pressant simultanément les touches <b>Shift</b> et <b>Flèche droite (ou gauche)</b> pour changer la taille en largeur, <b>Shift</b> et <b>Flèche haut (ou bas)</b> pour changer la taille en hauteur (pas besoin d'utiliser la souris pour changer la taille). Vous pouvez ajouter une image (par le bouton <b>Ajouter Image</b>), sélectionnez le chemin de votre image (puis l'image elle-même) dans la boîte de dialogue <b>Ouvrir des images</b>, cliquez sur le bouton <b>Ouvrir</b>. Certaines actions peuvent être effectuées (comme Copier, Couper, Coller, Effacer) par les boutons juste en dessous de <b>Ajouter Image</b> (positionnez votre souris sur ces boutons et il vous sera indiqué à quoi ils correspondent). Vous pouvez déplacer les éléments un à un dans la scène en cliquant dessus et en déplaçant la souris sans relacher le clic gauche (vu précédemment). Vous pouvez aussi déplacer plusieurs éléments en même temps comme expliqué précédemment mais en 'dessinant' au préalable un rectangle qui les englobera (bouton gauche de la souris maintenu en la déplaçant). L'ordre d'affichage des éléments peut-être modifié au moyen des boutons <b>Monter</b> et <b>Descendre</b>.</p><p>Sélectionnez votre format d'image (PNG, JPEG, BMP, TIFF ou PPM), c'est à dire votre extension d'image, dans la liste déroulante (tout en bas) prévue à cet effet. Dans le cas d'une sélection JPEG, n'oubliez pas de régler la <b>Qualité de l'image</b>.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>Appliquer</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>Nom de fichier</b>, cliquez sur le bouton <b>Enregistrer</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>Visualisation des images créées</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>Infos</b> vous permet de voir le filtre utilisé, les image(s) chargée(s) et les image(s) convertie(s).</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
