#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import threading
from PyQt4.QtCore import  QSize, SIGNAL, QString, Qt, QVariant, QDir, QTimer, QThread, QPoint, QSettings, PYQT_VERSION_STR
from PyQt4.QtGui import QAbstractItemView, QStandardItemModel, QFontMetricsF, QWidget, QFont, QListView, QToolButton, QIcon, QHBoxLayout, QVBoxLayout, QAction, QKeySequence, QComboBox, QFrame, QLabel, QSplitter, QIcon, QDirModel, QTreeView, QPushButton, QMenu, QStandardItem, QPixmap, QPixmapCache, QImage, QImageReader

# Gestion de l'aperçu de la vidéo
from moteur_modules_animation.mplayer import Mplayer
# Ajout InfosImage dans l'import.
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue, InfosImage
# Fenêtre d'info pour les vidéos
from gui_modules_animation.infoVideo import InfosVideo

import time

# Nouvel objet pour les preview
from gui_modules_common.EkdWidgets import EkdPreview
# Utilisation de EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class SelectWidget(QWidget):
	"""Module de sélection d'images"""

	def __init__(self, extensions=None, mode=None, geometrie=None, video=False, audio=False):
		"""
                Création du widget
                attributs : 
                    extensions : Filtre de selection des fichiers
                    mode : Mode d'affichage (texte, icones, icones+texte)
                    geometrie : Taille du widget
                    video : affiche en mode video ?
                    audio : affiche en mode audio ?
                """
		QWidget.__init__(self)

		self.video = video

		self.audio = audio

		# Liste des extensions
		if extensions:
			self.extensions  = extensions

		else:
			if self.video:
				self.extensions = ["*.avi", "*.mov", "*.mpg", "*.mpeg", "*.mjpeg", "*.flv", "*.mp4", "*.h264", "*.dv", "*.vob", "*.mkv", "*.mod"]
			elif self.audio :
				self.extensions = ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.mp2"]
			else:
				self.extensions  = ["*.jpg", "*.jpeg", "*.png", "*.bmp",
						"*.gif", "*.tif", "*.tiff", "*.ppm"]

		self.extensionsDepart = self.extensions 

		# Mode d'affichage: icone ou texte
		self.mode = mode
		# Fonction QMainWindow.frameGeometry
		self.tailleFenetrePrincipale = geometrie

		# Place réservée à ligne des QListView pour l'affichage texte
		font = QFont(self.font())
		fm = QFontMetricsF(font)
		self.hauteurTexteListe = 1.33 * fm.height()

		# HBox et Vbox
		hbox = QHBoxLayout()
		vbox = QVBoxLayout()
		#stackVisio.setLayout(vbox)
		self.setLayout(vbox)

		# Listview
		self.modeleBase = QStandardItemModel()
		self.listeBase = QListView()
		self.listeBase.setModel(self.modeleBase)
		self.listeBase.setMovement(QListView.Static)
		self.listeBase.setUniformItemSizes(0)
		self.listeBase.setViewMode(QListView.IconMode)
		self.listeBase.setEditTriggers(QAbstractItemView.NoEditTriggers)
		#self.listeBase.setLayoutMode(QListView.SinglePass)
		#self.listeApercus.setSelectionRectVisible(0)
		self.listeBase.setGridSize(QSize(128, 100))
		self.listeBase.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.listeBase.setIconSize(QSize(64, 64))
		if not self.video and not self.audio :
			self.listeBase.setToolTip(_(u"Liste des images sources qui vont subir un traitement.") + '\n' +
						  _(u"Double-cliquez sur une pour l'afficher en grand dans une nouvelle fenêtre."))

		if self.video or self.audio :
			self.listeBase.setToolTip(_(u"<p>Sélectionnez le ou les fichier(s), selon les cas, pour visionner/écouter<br> et/ou poursuivre le traitement <b>(si vous avez chargé un<br> seul fichier vidéo/audio, celui-ci sera automatiquement<br> sélectionné, sauf si vous le déselectionnez en<br> cliquant sur une partie vide du panel)</b>.</p><p>Le traitement se fera avec le fichier vidéo/audio sélectionné <b>(sauf<br> pour le Montage vidéo, et en particulier: Vidéo<br> seulement et Vidéo + audio) ... et pour <br>Vidéo > Transcodage > Gestion AVCHD, dans ce cas précis<br> toutes les vidéos présentes dans la liste seront traitées<br> (traitement par lot).<br>Ce traitement par lot concerne aussi les fichiers audio dans<br>Musique-Son > Joindre plusieurs fichiers audio (dans la partie Musique-Son)</b>.</p>"))

		else :
			self.connect(self.listeBase, SIGNAL("doubleClicked(const QModelIndex &)"), self.apercuBase)
		self.connect(self.listeBase, SIGNAL("clicked (const QModelIndex &)"), self.selectItem)

		# Boutons

		# Ajouter
		ajouter = QToolButton()
		ajouter.setIcon(QIcon("Icones" + os.sep + "ajouter2.png"))
		ajouter.setIconSize(QSize(32, 32))
		ajouter.setText(QString(_(u"Ajouter")))
		ajouter.setToolTip(_(u"Ajouter des images à la liste"))
		ajouter.setAutoRaise(1)
		ajouter.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.connect(ajouter, SIGNAL("clicked()"), self.ajouter)
		hbox.addWidget(ajouter)

		# Supprimer
		supprimer = QToolButton()
		supprimer.setIcon(QIcon("Icones" + os.sep + "supprimer.png"))
		supprimer.setIconSize(QSize(32, 32))
		supprimer.setText(QString(_(u"Retirer")))
		supprimer.setAutoRaise(1)
		supprimer.setToolTip(_(u"Retirer toutes les images sélectionnées dans la liste"))
		supprimer.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.connect(supprimer, SIGNAL("clicked()"), self.supprimer)
		# Raccourci-clavier de suppression
		actionSuppression = QAction(self)
		actionSuppression.setShortcut(QKeySequence.Delete)
		self.connect(actionSuppression, SIGNAL('triggered()'), self.supprimer)
		self.addAction(actionSuppression)
		# Enfant du bouton: suppression de tous les éléments du QListView
		actionSuppressionTotale = QAction(_(u"Retirer toutes les images de la liste"), self)
		supprimer.addAction(actionSuppressionTotale)
		self.connect(actionSuppressionTotale, SIGNAL('triggered()'), self.toutSupprimer)
		hbox.addWidget(supprimer)

		if not self.video and not self.audio :
			# Aperçu
			apercu = QToolButton()
			apercu.setIcon(QIcon("Icones" + os.sep + "apercu.png"))
			apercu.setIconSize(QSize(32, 32))
			apercu.setText(QString(_(u"Afficher")))
			apercu.setToolTip(_(u"Affiche l'image sélectionnée dans une nouvelle fenêtre sans autre modification"))
			apercu.setAutoRaise(1)
			apercu.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
			self.connect(apercu, SIGNAL("clicked()"), self.apercuBase)
			hbox.addWidget(apercu)

		# Mode d'affichage de la liste
		self.modeAffichageBaseCombo = QComboBox()
		self.modeAffichageBaseCombo.addItem(_(u"Mode icône"), QVariant("icone"))
		self.modeAffichageBaseCombo.addItem(_(u"Mode icône en colonne"), QVariant("icone&colonne"))
		self.modeAffichageBaseCombo.addItem(_(u"Mode texte"), QVariant("texte"))
		self.modeAffichageBaseCombo.setToolTip(_(u"Type d'affichage de la liste ci-dessus"))
		self.connect(self.modeAffichageBaseCombo, SIGNAL("currentIndexChanged(int)"), self.modeAffichageBase)
		hbox.addWidget(self.modeAffichageBaseCombo)

		# Pour fenêtre d'info pour les vidéos / audio
		info = QToolButton()
		info.setIcon(QIcon("Icones" + os.sep + "icone_info_128.png"))
		info.setIconSize(QSize(32, 32))
		info.setText(QString(_(u"Infos")))
		info.setAutoRaise(1)
		info.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.connect(info, SIGNAL("clicked()"), self.info)
		hbox.addWidget(info)

		if not self.video and not self.audio :
			# Infos
			info.setToolTip(_(u"Diverses informations sur l'image sélectionnée"))
		else:
			info.setToolTip(_(u"Diverses informations sur la vidéo/l'audio sélectionné(e)"))

		hbox.addStretch()

		# Label pour les infos
		self.infoLabel = QLabel(QString(_(u"Aucun élément")))
		self.connect(self.listeBase, SIGNAL("dataChanged()"), self.infoImages)
		hbox.addWidget(self.infoLabel)

		# Ajouts au Layout

		# Module Mplayer en mode video
		centralBox = QHBoxLayout()

		centralBox.addWidget(self.listeBase)
		if self.video or self.audio :
			self.mplayer = Mplayer([], (50,50), (Mplayer.RATIO, Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_SUR_UNE_LIGNE,Mplayer.PAS_PARCOURIR))
			self.connect(self.listeBase, SIGNAL("doubleClicked(const QModelIndex &)"), self.mplayer.demarrerMPlayer)
			if self.audio :
				self.mplayer.setAudio(True)
			playerBox = QVBoxLayout()
			playerBox.addWidget(self.mplayer)
			self.InfoVideo = QLabel(_(u"Pas d'information"))
			self.connect(self, SIGNAL("pictureSelected()"), self.setPlayerFile)
			centralBox.addLayout(playerBox)

		vbox.addLayout(centralBox)

		vbox.addLayout(hbox)

		# Fenetre de selection d'images
		self.frameSelect = QFrame()

		# Définition du titre de la frame

		# Un titre différent pour chaque boîte de chargement
		if not self.video and not self.audio :
			self.frameSelect.setWindowTitle(_(u"Parcours d'images"))
		if self.video:
			self.frameSelect.setWindowTitle(_(u"Parcours des vidéos"))
		if self.audio :
			self.frameSelect.setWindowTitle(_(u"Parcours des fichiers audio"))

		# 1ère ouverture pour le widget?
		self.premiereOuvertureFrameSelect = 1
		self.frameSelect.hide()
		self.frameSelect.setAutoFillBackground(1)
		self.frameSelect.setFrameShape(QFrame.StyledPanel)
		self.frameSelect.setFrameShadow(QFrame.Plain)

		# Contenu de la fenêtre de sélection d'images
		split = QSplitter()
		vboxFrameSelectO = QVBoxLayout()
		hboxFrameSelect = QHBoxLayout()
		hboxBouton = QHBoxLayout()
		vboxFrameSelect = QVBoxLayout()
		widgetFrameSelect = QWidget()
		widgetFrameSelect.setLayout(vboxFrameSelect)
		hboxFrameSelect.addWidget(split)
		self.label = QLabel()
		vboxFrameSelectO.addLayout(hboxFrameSelect, 1)
		vboxFrameSelectO.addWidget(self.label, 0)
		self.frameSelect.setLayout(vboxFrameSelectO)


		# Treeview
		self.modeleDossiers = QDirModel()
                sorting = QDir.DirsFirst
                if int(EkdConfig.get("general", "ignore_case")):
                    sorting |= QDir.IgnoreCase
                self.modeleDossiers.setSorting(sorting)
		# Ajout des fichier cachés puisque le répertoire temporaire par défaut est ~/.temp_ekd
		if int(EkdConfig.get("general", "show_hidden_files")) : shf = QDir.Hidden
		else : shf = QDir.Dirs
		self.modeleDossiers.setFilter(shf | QDir.Dirs | QDir.NoDotAndDotDot)
		self.dossiers = QTreeView()

		self.dossiers.setModel(self.modeleDossiers)
		# Récupération du dossier contenant les vidéos (EkdConfig)
		try:
			if self.video :
				directory = EkdConfig.get("general", 'video_input_path')
			elif self.audio :
				directory = EkdConfig.get("general", 'sound_input_path')
			else :
				## Images
				directory = EkdConfig.get("general", 'image_input_path')
				
			#print "[Debug] Chargement des fichiers |",files,"| de la section :",idsection

		except Exception, e :
			directory = QDir.homePath()
			#print "Cannot set input path (%s) taking default: %s" % (e, directory)
			EkdPrint(u"Cannot set input path (%s) taking default: %s" % (e, directory))

		index = self.modeleDossiers.index(directory)
		self.dossiers.setCurrentIndex(self.modeleDossiers.index(directory))
		self.dossiers.setExpanded(index, True)
		self.dossiers.hideColumn(1)
		self.dossiers.hideColumn(2)
		self.dossiers.hideColumn(3)
		self.dossiers.setMinimumWidth(200)

                if PYQT_VERSION_STR == "4.4.4" :
                    ## Correction d'un bug segfault sur updateDir dans la version 4.4.4 de PYQT (jaunty)
                    self.dossiers.setExpandsOnDoubleClick(False)
                    self.connect(self.dossiers,SIGNAL("clicked(QModelIndex)"), self.updateDir)
                else :
                    self.connect(self.dossiers,SIGNAL("pressed(QModelIndex)"), self.updateDir)
                    self.connect(self.dossiers,SIGNAL("activated(QModelIndex)"), self.updateDir)

		# Listview
		self.modeleAjout = QStandardItemModel()
		self.listeAjout = QListView()
		self.listeAjout.setModel(self.modeleAjout)
		# On affiche en mode liste par défaut
		self.listeAjout.setViewMode(QListView.ListMode)

		self.listeAjout.setMovement(QListView.Static)
		self.listeAjout.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.listeAjout.setUniformItemSizes(0)
		self.listeAjout.setGridSize(QSize(128, 100))
		self.listeAjout.setIconSize(QSize(64, 64))
		self.listeAjout.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.listeAjout.setToolTip(_(u"Double-cliquez sur un élément pour l'afficher en grand dans une nouvelle fenêtre."))
		vboxFrameSelect.addWidget(self.listeAjout)

		# Boutons

		# Ajouter
		ajouter = QToolButton()
		ajouter.setIcon(QIcon("Icones" + os.sep + "ajouter.png"))
		ajouter.setIconSize(QSize(32, 32))
		ajouter.setText(QString(_(u"Ajouter")))
		ajouter.setAutoRaise(1)
		ajouter.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		ajouter.setToolTip(_(u"Ajouter des images à la liste"))
		self.connect(ajouter, SIGNAL("clicked()"), self.ajouterListview)
		hboxBouton.addWidget(ajouter)

		# Fermer
		supprimer = QToolButton()
		supprimer.setIcon(QIcon("Icones" + os.sep + "annuler.png"))
		supprimer.setIconSize(QSize(32, 32))
		supprimer.setText(QString(_(u"Annuler")))
		supprimer.setAutoRaise(1)
		supprimer.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		supprimer.setToolTip(_(u"Ferme la fenêtre d'ajout sans ajouter d'image"))
		self.connect(supprimer, SIGNAL("clicked()"), self.fermerAjout)
		hboxBouton.addWidget(supprimer)

		if not self.video and not self.audio :
			# Aperçu
			apercu = QToolButton()
			apercu.setIcon(QIcon("Icones" + os.sep + "apercu.png"))
			apercu.setIconSize(QSize(32, 32))
			apercu.setText(QString(_(u"Afficher")))
			apercu.setAutoRaise(1)
			apercu.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
			apercu.setToolTip(_(u"Affiche l'image sélectionnée dans une nouvelle fenêtre sans autre modification"))
			self.connect(apercu, SIGNAL("clicked()"), self.apercuAjout)
			hboxBouton.addWidget(apercu)

		# Mode d'affichage de la liste
		self.modeAffichageAjoutCombo = QComboBox()
		self.modeAffichageAjoutCombo.addItem(_(u"Mode icône"), QVariant("icone"))
		self.modeAffichageAjoutCombo.addItem(_(u"Mode icône en colonne"), QVariant("icone&colonne"))
		self.modeAffichageAjoutCombo.addItem(_(u"Mode texte"), QVariant("texte"))
		self.modeAffichageAjoutCombo.setToolTip(_(u"Type d'affichage de la liste ci-dessus"))
		self.connect(self.modeAffichageAjoutCombo, SIGNAL("currentIndexChanged(int)"), self.modeAffichageAjout)
		hboxBouton.addWidget(self.modeAffichageAjoutCombo)

		# Filtres image (extensions)
		self.filtreImageBouton = QPushButton()
		self.filtreImageBouton.setIcon(QIcon("Icones" + os.sep + "icone_extension.png"))
		self.filtreImageBouton.setIconSize(QSize(32, 32))
		self.filtreImageBouton.setText("  " + u"Filtres")
		self.txtToutSelFiltre = _(u"Tout sélectionner")
		lst = self.extensions[:]
		lst.insert(0, self.txtToutSelFiltre)
		# Drapeau pour pour éviter de lancer la fonction filtreImage plusieurs fois en même temps
		self.verrouillerFiltreImage = 0
		# Menu du bouton
		self.menuFiltreImageBouton = QMenu(self.filtreImageBouton)
		self.connect(self.filtreImageBouton, SIGNAL('pressed()'), self.onFiltreImageBouton)
		for ext in lst:
			action = QAction(ext, self)
			action.setCheckable(1)
			if ext == self.txtToutSelFiltre:
				action.setData(QVariant('tout'))
				action.setEnabled(0)
			action.setChecked(1)
			self.menuFiltreImageBouton.addAction(action)
			self.connect(action, SIGNAL('changed()'), lambda a=action:self.filtreImage(a))
		self.indicationsFiltreImage()
		hboxBouton.addWidget(self.filtreImageBouton)

		# Pour fenêtre d'info pour les vidéos
		info = QToolButton()
		info.setIcon(QIcon("Icones" + os.sep + "icone_info_128.png"))
		info.setIconSize(QSize(32, 32))
		info.setText(QString(_(u"Infos")))
		info.setAutoRaise(1)
		info.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		if not self.video and not self.audio :
			# Infos
			info.setToolTip(_(u"Diverses informations sur l'image sélectionnée"))
		elif self.video :
		        info.setToolTip(_(u"Diverses informations sur la vidéo sélectionnée"))
		elif self.audio :
			info.setToolTip(_(u"Diverses informations sur le fichier audio sélectionné"))

		self.connect(info, SIGNAL("clicked()"), self.info)
		hboxBouton.addWidget(info)

		# Assemblage
		split.addWidget(self.dossiers)
		split.addWidget(widgetFrameSelect)
		vboxFrameSelect.addLayout(hboxBouton)

		# On sélectionne le mode si l'information a été donnée lors de l'instanciation
		if self.mode:
			i = self.modeAffichageBaseCombo.findData(QVariant(mode))
			self.modeAffichageBaseCombo.setCurrentIndex(i)

		self.updateDir(self.modeleDossiers.index(directory))

		# Modification du comportement du doubleclick sur un élément en fonction du type d'élément
		if not self.video and not self.audio :
		        self.connect(self.listeAjout, SIGNAL("doubleClicked(const QModelIndex &)"), self.apercuAjout)
		else:
			self.connect(self.listeAjout, SIGNAL("doubleClicked(const QModelIndex &)"), self.info)


	def setPlayerFile(self):
		'''
		Lorsque un fichier est selectionné, on le definit comme fichier à lire dans l'apperçu mplayer
		'''
		fichier_lu = self.getFile()
		if self.video or self.audio :
			self.mplayer.setVideos([fichier_lu])
		self.emit(SIGNAL('fileSelected'))


	def indicationsFiltreImage(self):
		"""Modification de l'info-bulle du bouton de filtrage des formats des images et de la barre des tâches
		pour indiquer quels sont les formats actifs"""

		text1 = _(u"Limite l'affichage des images à un ou plusieurs formats")
		txt2 = _(u"Les formats actifs sont")
		txt2bis = _(u"Le format actif est")
		txt2ter = _(u"Aucun format n'est actif")

		extensions = [ext for ext in self.extensions if ext != self.txtToutSelFiltre]
		nbrExtensionActive = len(extensions)
		if nbrExtensionActive > 1:
			text2 = txt2 + ' : '
		elif nbrExtensionActive == 1:
			text2 = txt2bis + ' : '
		elif nbrExtensionActive == 0:
			text2 = txt2ter + '.'

		self.filtreImageBouton.setToolTip(text1+'.\n'+text2+' '.join(extensions))
		self.label.setText(text2+' '.join(extensions))


	def onFiltreImageBouton(self):
		"Affiche le menu du bouton de filtre"
		self.menuFiltreImageBouton.exec_(self.filtreImageBouton.mapToGlobal(QPoint(0,0)))


	def filtreImage(self, action):
		"Limite l'affichage des images à un ou plusieurs formats grâce aux cases à cocher du bouton"

		# Quand on modifie l'état des actions du bouton depuis cette fonction,
		# on s'assure qu'elle ne sera pas relancée plusieurs fois en même temps
		if self.verrouillerFiltreImage:
			return

		# On verrouille la fonction, le temps de son application
		self.verrouillerFiltreImage = 1

		self.extensions = []

		actionTxt = action.text()
		if actionTxt in self.extensionsDepart:
			# Sélection d'un filtre normal
			nbrFiltresSelect = 0
			for act in self.menuFiltreImageBouton.actions():
				if act.isChecked():
					self.extensions.append(unicode(act.text()))
					if not act.data().toString() == 'tout':
						nbrFiltresSelect += 1
			if nbrFiltresSelect == len(self.extensionsDepart):
				self.menuFiltreImageBouton.actions()[0].setChecked(1)
				self.menuFiltreImageBouton.actions()[0].setEnabled(0)
			else:
				self.menuFiltreImageBouton.actions()[0].setChecked(0)
				self.menuFiltreImageBouton.actions()[0].setEnabled(1)
		else:
			# Sélection de l'action: « sélection de tous les filtres »
			for act in self.menuFiltreImageBouton.actions():
				act.setChecked(1)
			self.menuFiltreImageBouton.actions()[0].setEnabled(0)
			self.extensions = self.extensionsDepart[:]

		#print "self.extensions:", self.extensions
		EkdPrint(u"self.extensions: %s" % self.extensions)
		self.indicationsFiltreImage()
		self.verrouillerFiltreImage = 0

		self.updateDir(self.modeleDossiers.index(self.tmpdir.canonicalPath()))


	def ajouter(self):
		"Montre le stack de selection de fichier"

                taille = QSettings().value("MainWindow/Size", QVariant(QSize(800, 600))).toSize()
                self.frameSelect.setMaximumSize(taille)
                #print "Taille : %s" % taille
                EkdPrint(u"Taille : %s" % taille)
                self.frameSelect.resize(taille.width(), taille.height())
                #print "Debug %s: fenêtre retaillée" % (getattr(self, '__class__') )

		# On fait coïncider le mode d'affichage avec celui de l'autre liste la 1ère fois
		if self.premiereOuvertureFrameSelect:
                    self.modeAffichageAjoutCombo.setCurrentIndex(self.modeAffichageBaseCombo.currentIndex())
                    self.premiereOuvertureFrameSelect = 0
                    #print "Debug %s: première ouverture" % getattr(self, '__class__')

		self.frameSelect.show()
                #print "Debug %s: affichage de la selection des images" % (getattr(self, '__class__'))
		self.dossiers.resizeColumnToContents(0)
                #print "Debug %s: Mise à jour de la taille des dossiers" % (getattr(self, '__class__'))


	def supprimer(self):
		"Supprimer l'objet de la liste"

		if not self.modeleBase.rowCount() or not self.listeBase.selectedIndexes():
			return

		# Récupération des indices de ligne des fichiers selectionnées
		# À chaque suppression d'index (QModelIndex) dans le modèle, ceux d'indices supérieurs vont voir
		# leur indices diminuer de 1. Pour être sûr de bien supprimer les bons index, il faut les supprimer
		# dans l'ordre décroissant
		lstRow = []
		for index in self.listeBase.selectedIndexes():
			i = index.row()
			lstRow.append(i)
		lstRow.sort(reverse = True)
		for row in lstRow:
			self.modeleBase.removeRow(row)

		# Informations
		self.infoImages()

		# On indique à la classe ayant instanciée ce widget si des images sont chargées ou pas (boléen)
		if range(self.modeleBase.rowCount()):
			i = 1
		else:
			i = 0
		self.emit(SIGNAL('pictureChanged(int)'), i)


	def toutSupprimer(self):
		"Purge de la liste de Principale"
		self.modeleBase.clear()
		self.infoImages()
		if range(self.modeleBase.rowCount()):
			i = 1
		else:
			i = 0
		self.emit(SIGNAL('pictureChanged(int)'), i)


	def apercuCommun(self, listView):
		"Outils communs aux 2 fonctions d'aperçus"
		try:
			index = listView.selectedIndexes()[0]
		except IndexError, e:
			#print "pas d'icône sélectionnée"
			EkdPrint(u"pas d'icône sélectionnée")
			return

		# Fenetre d'aperçu
		apercu = VisionneurEvolue(unicode(index.data(Qt.UserRole + 2).toString()))
		apercu.redimenFenetre(self.tailleFenetrePrincipale, 1., 0.7)
		apercu.exec_()


	def apercuBase(self):
		"Montre l'image en grand dans une nouvelle fenêtre depuis la liste principale"
		self.apercuCommun(self.listeBase)


	def selectItem(self):
		"Sélection d'un item"
		# L'adresse de l'image sélectionnée n'est pas jointe au signal
		# pour ne pas renvoyer un QString qui compliquerait tout
		self.emit(SIGNAL('pictureSelected()'))


	def apercuAjout(self):
		"Montre l'image en grand dans une nouvelle fenêtre depuis la liste d'ajout"
		self.apercuCommun(self.listeAjout)


	def infoImages(self):
		"Affiche des infos sur la liste de fichiers sélectionnés"
		if self.modeleBase.rowCount() == 0:
			self.infoLabel.setText(QString(_(u"Aucun élément")))
		elif self.modeleBase.rowCount() == 1:
			self.infoLabel.setText(QString(_(u"1 élément")))
		else:
			self.infoLabel.setText(QString(str(self.modeleBase.rowCount()) + ' ' + _(u"éléments")))


	def info(self):
		"Affiche des infos sur la vidéo/image sélectionnée pour les 2 QListView"

		if self.frameSelect.isVisible():
			liste = self.listeAjout
			modele = self.modeleAjout

		else:
			liste = self.listeBase
			modele = self.modeleBase

		img = self.getFile(liste, modele)

		if img:
			if self.video :
				info = InfosVideo(img)
			elif self.audio :
				info = InfosVideo(img, audio = True)
			else:
				info = InfosImage(img)
			info.exec_()


	def modeAffichageCommun(self, liste, i=None):
		"Change le mode d'affichage d'un des deux QListView"

		if liste == self.listeBase:
			combo = self.modeAffichageBaseCombo
		elif liste == self.listeAjout:
			combo = self.modeAffichageAjoutCombo

		# Pour quand le changement de mode n'est pas appelé depuis la boite de combo
		# mais depuis un clic sur un répertoire ou sur le bouton Ajouter de la boite de dialogue d'ajout
		if not i:
			i = combo.currentIndex()
		mode = combo.itemData(i).toString()

		if mode == "icone":
			liste.setViewMode(QListView.IconMode)
			liste.setIconSize(QSize(64, 64))
			liste.setGridSize(QSize(128, 100))
		elif mode == "icone&colonne":
			liste.setViewMode(QListView.ListMode)
			liste.setIconSize(QSize(64, 64))
			liste.setGridSize(QSize(128, 100))
		elif mode == "texte":
			liste.setViewMode(QListView.ListMode)
			# On affiche une toute petite icone même en mode texte
			liste.setIconSize(QSize(16, 16))
			liste.setGridSize(QSize(128, self.hauteurTexteListe))

		self.mode = mode
		self.affiche_preview()

	def modeAffichageBase(self, i):
		"Changement du mode d'affichage de la liste principale"
		self.modeAffichageCommun(self.listeBase, i)


	def modeAffichageAjout(self, i):
		"Changement du mode d'affichage de la liste d'ajout"
		self.modeAffichageCommun(self.listeAjout, i)
		# On met à jour lorsqu'on change de mode de visualisation
		self.affiche_preview()


	def fermerAjout(self):
		"Ferme la boite de dialogue d'ajout"
		self.frameSelect.hide()


	def ajouterListview(self):
		"Ajoute les fichiers selectionnés au Listview"

		# Si rien n'est sélectionné, on sort
		if not len(self.listeAjout.selectedIndexes()):
			return

		# Arreter de charger les miniatures du dossier precedent
		self.loading = 0

		# Cacher la fenetre
		self.frameSelect.hide()

		elementAvantAjout = self.modeleBase.rowCount()
		# Récupération des fichiers selectionnées
		for index in self.listeAjout.selectedIndexes():
			itemSource = self.modeleAjout.itemFromIndex(index)

			# le contenu des fichiers
			# On fait en sorte que la liste source ne contienne pas de doublon
			# sinon on passe à l'item suivant
			doulon = False

			# La suppression des doublon seulement si la liste est inférieur à 65635 éléments 
			# (performances), il faudrait peut-être revoir la partie detection des doublons
			nbelement=self.modeleBase.rowCount()
			if (elementAvantAjout > 0) and (nbelement < 65635) and (self.modeleBase.findItems(itemSource.data(Qt.UserRole + 3).toString())):
				#print _(u"Suppression des doublons : %s" % itemSource.data(Qt.UserRole + 3).toString())
				EkdPrint(_(u"Suppression des doublons : %s" % itemSource.data(Qt.UserRole + 3).toString()))
				continue

			if doulon:
				continue

			# Un icône pour les images, un autre icône pour les vidéos, et un pour audio
			if not self.video and not self.audio :
				item = QStandardItem(QIcon("Icones" + os.sep + "image_image.png"), itemSource.data(Qt.UserRole + 3).toString())
			if self.video:
				item = QStandardItem(QIcon("Icones" + os.sep + "image_video.png"), itemSource.data(Qt.UserRole + 3).toString())
			# Gestion audio ####### image_icone.png
			if self.audio:
				item = QStandardItem(QIcon("Icones" + os.sep + "image_audio.png"), itemSource.data(Qt.UserRole + 3).toString())

			item.setData(itemSource.data(Qt.UserRole + 2), Qt.UserRole + 2)
			item.setData(itemSource.data(Qt.UserRole + 3), Qt.UserRole + 3)
			item.setToolTip(itemSource.data(Qt.UserRole + 3).toString())
			self.modeleBase.appendRow(item)

		# Informations
		self.infoImages()

		self.loading = 1

		# Miniatures
		if self.modeleBase.rowCount() > 0:
			self.itemNum = 0
			self.modelPreview = self.modeleBase
			self.modeAffichageCommun(self.listeBase)
			self.affiche_preview()

		# On indique à la classe ayant instanciée ce widget que des images ont été chargées (boléen)
		self.emit(SIGNAL('pictureChanged(int)'), 1)


	def updateDir(self, item):
		"Rafraichit le listview en fonction du dossier sélectionné"

		self.dossiers.resizeColumnToContents(0)
                self.dossiers.expand(item)
		# Arreter de charger les miniatures du dossier precedent
		self.loading = 0

		# Benchmark
		depart = time.time()

		self.modeleAjout.clear()
		self.tmpdir = QDir()
		self.tmpdir.setPath(self.modeleDossiers.filePath(item))
		self.tmpdir.setNameFilters(self.extensions)

		# On met a jour à la fois la liste de droite et le QTree à gauche
		self.modeleDossiers.refresh()
		
		for wlfile in self.tmpdir.entryList(QDir.Files):
			# Un icône pour les images, un autre icône pour les vidéos, et un pour audio
			if not self.video and not self.audio :
				item = QStandardItem(QIcon("Icones" + os.sep + "image_image.png"), QString(wlfile))
			if self.video:
				item = QStandardItem(QIcon("Icones" + os.sep + "image_video.png"), QString(wlfile))
			# Gestion audio ####### image_icone.png
			if self.audio:
				item = QStandardItem(QIcon("Icones" + os.sep + "image_audio.png"), QString(wlfile))

			item.setToolTip(wlfile)
			item.setData(QVariant(self.tmpdir.absolutePath() + os.sep + wlfile), Qt.UserRole + 2)
			item.setData(QVariant(wlfile), Qt.UserRole + 3)
			self.modeleAjout.appendRow(item)

		#print str(time.time() - depart)
		EkdPrint(u"%s" % str(time.time() - depart))

		self.loading = 1

		if self.modeleAjout.rowCount() > 0 :
			self.itemNum = 0
			self.modelPreview = self.modeleAjout
			self.modeAffichageCommun(self.listeAjout)
			# On ne génère pas la préview si on est en mode texte
			if self.mode != "texte":
				self.affiche_preview()


	def affiche_preview(self):
		"Affiche progressivement les miniatures des images"

		if self.video or self.audio :
			return

		# Recuperation de l'item
		try :
			item = self.modelPreview.item(self.itemNum)
		except AttributeError :
			#print "erreur de récupération de l'item"
			EkdPrint(u"erreur de récupération de l'item")
			# Si problème de récupération de l'item on quitte
			return

		if item is None:
			return

		# Rafraîchissement de la grille traitée pour éviter les chevauchements du texte des icônes
		h = 100
		if self.mode == "texte":
			h = self.hauteurTexteListe
			return
                
		if self.frameSelect.isVisible() or self.premiereOuvertureFrameSelect:
			self.listeAjout.setGridSize(QSize(128, h))
		else:
			self.listeBase.setGridSize(QSize(128, h))
                #print "Debug %s.affiche_preview: grille rafraichie" % getattr(self, '__class__')

		imageName = item.data(Qt.UserRole + 2).toString()

		minipix = EkdPreview(imageName).get_preview()

		item.setIcon(QIcon(minipix))
		self.itemNum += 1

		# Recursion jusqu'a la fin des images
		if self.itemNum < self.modelPreview.rowCount() and self.loading == 1:
			QTimer.singleShot(3, self.affiche_preview)


	def getHelp(nomOnglet1, nomOnglet2=None):
		"Renvoie l'aide selon que le cadre contienne un ou deux onglets de sélection d'image"
		txt0 = tr(u"<div>L'aide de l'onglet %s</div>" %nomOnglet1)
		if txtArg2:
			txt1 = tr(u"<div>Faites la même chose pour l'onglet %s</div>" %nomOnglet2)
		else:
			txt1 = ''
		return  txt0 + txt1


	def loadFileLocation(self, idsection, var=u'sources'):
		if not idsection:
			return
		try :
			files = eval(EkdConfig.get(idsection, var))
			#print "[Debug] Chargement des fichiers |",files,"| de la section :",idsection
			self.setFiles(files)
		except Exception, e :
			#print "No files to load: ", e
			EkdPrint(u"No files to load: %s" % e)

		# Miniatures
		if self.modeleBase.rowCount() > 0:
			self.itemNum = 0
			self.modelPreview = self.modeleBase
			self.modeAffichageCommun(self.listeBase)
			self.affiche_preview()
			i = 1
		else:
			i = 0
		self.emit(SIGNAL('pictureChanged(int)'), i)

		
	def saveFileLocation(self, idsection, var=u'sources'):
		if not idsection:
			return
		files = self.getFiles()
		#print "[Debug] Sauvegarde des fichier |",files,"| de la section :",idsection
		EkdConfig.set(idsection, var, files)


	def getFiles(self):
		"Renvoie la liste des fichiers chargés"
		liste = []
		# On récupère le chemin absolu de chaque item
		for row in range(self.modeleBase.rowCount()):
                        filename = self.modeleBase.item(row).data(Qt.UserRole + 2).toString()
			liste.append(unicode(filename))
		return liste

	def getSelFiles(self):
		"Renvoie la liste des fichiers sélectionnés dans la liste des fichiers chargés ou toute la liste si aucun fichier n'est sélectionné"
		liste = []
		listIndex = self.listeBase.selectedIndexes()
		if len(listIndex) == 0 :
			return self.getFiles()
		# On récupère le chemin absolu de chaque item
		for row in listIndex :
                        filename = self.modeleBase.itemFromIndex(row).data(Qt.UserRole + 2).toString()
			liste.append(unicode(filename))
		return liste


	def setFiles(self, filesliste, append=0):
		"Remplie la liste des fichier par filesliste"

		liste = self.listeBase
		modele = self.modeleBase
		if not append :
			modele.clear()

		for file in filesliste:
			fullfilename = unicode(file.strip())
			filename = os.path.basename(fullfilename)

			#print "[DEBUG] Items: |"+ filename+ "|" + fullfilename 
			if not self.video and not self.audio :
				item = QStandardItem(QIcon("Icones" + os.sep + "image_image.png"), QString(filename))
			if self.video:
				item = QStandardItem(QIcon("Icones" + os.sep + "image_video.png"), QString(filename))
			# Gestion audio ####### image_icone.png
			if self.audio:
				item = QStandardItem(QIcon("Icones" + os.sep + "image_audio.png"), QString(filename))

			item.setToolTip(fullfilename)
			item.setData(QVariant(fullfilename), Qt.UserRole + 2)
			item.setData(QVariant(fullfilename), Qt.UserRole + 3)
			if append :
				if len(self.modeleBase.findItems(QString(filename))) == 0 : # pour supprimer les doublons
					modele.appendRow(QStandardItem(item))
			else :
					modele.appendRow(QStandardItem(item))
			self.itemNum = 0
			self.modelPreview = modele
			self.affiche_preview()
		# On indique à la classe ayant instanciée ce widget si des images sont chargées ou pas (boléen)
		if range(self.modeleBase.rowCount()):
			i = 1
		else:
			i = 0
		self.emit(SIGNAL('pictureChanged(int)'), i)
		#print "[Debug : ] Premier objet : |" + modele.item(0).data(Qt.UserRole + 2).toString()+"|"


	def getFile(self, liste=None, modele=None):
		"Renvoie le premier fichier sélectionné dans la liste de base (ou dans la liste indiquée)"

		if not liste:
			liste = self.listeBase
			modele = self.modeleBase

		select = liste.selectedIndexes()
		if select:
			return unicode(select[0].data(Qt.UserRole + 2).toString())
		elif modele.rowCount():
			liste.setCurrentIndex(modele.indexFromItem(modele.item(0)))
			self.setPlayerFile()
			return unicode(modele.item(0).data(Qt.UserRole + 2).toString())
		# ... sinon on ne renvoie rien


	def getLength(self):
		"Renvoie le nombre de fichiers chargés dans la liste de base"
		return range(self.modeleBase.rowCount())
