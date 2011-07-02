#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, Image, shutil, glob, string
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_image.image_base import Base
BaseImg = Base # pour différencier les 2 bases
from gui_modules_common.gui_base import Base
from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_common.EkdWidgets import EkdSaveDialog, EkdPreview
from moteur_modules_common.EkdConfig import EkdConfig
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Animation_ConvertirImgEnAnim(Base):
	"""-----------------------------------------
	# Cadre accueillant les widgets de :
	# Animation >> convertir images en animations
	# -----------------------------------------"""

	def __init__(self, statusBar, geometry):
		#=== Variable de configuration ===#
		self.config=EkdConfig

		# Identifiant de la classe
		self.idSection = 'animation_convertir_des_images_en_video'

		self.statusBar = statusBar

		self.baseImg = BaseImg() # module de image

		# Par soucis de lisibilité, on préfère ne pas utiliser des objets présent dans le parent de cette façon
		# mais plutôt le passer en paramètre (le code est plus facile à lire de cette façon)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		self.repTempEntree = EkdConfig.getTempDir() + os.sep
		# création des répertoires temporaires
		if os.path.isdir(self.repTempEntree) is False:
        		os.makedirs(self.repTempEntree)

		if os.path.isdir(self.repTempEntree+'redim' + os.sep) is False:
        		os.makedirs(self.repTempEntree+'redim'+ os.sep)

		# Ce répertoire est crée pour le cas où l'utilsateur charge des images dont une des dimensions
		# (largeur et/ou hauteur) est impaire, en effet FFmpeg veut des images avec des résolutions
		# paires pour faire son travail !
		if os.path.isdir(self.repTempEntree+'img_res_impair'+ os.sep) is False:
        		os.makedirs(self.repTempEntree+'img_res_impair'+ os.sep)

		# Epuration/elimination des fichiers tampon contenus dans le rep tampon
		for toutRepTempE in glob.glob(self.repTempEntree+'*.*'):
			os.remove(toutRepTempE)

		# Scan du répertoire tampon ... /redim
		listeRepTempRedim=glob.glob(self.repTempEntree+'redim' + os.sep + '*.*')

		# Epuration/elimination des fichiers tampon contenus dans ... /redim
		if len(listeRepTempRedim)>0:
			for toutRepTempE_Redim in listeRepTempRedim:
				os.remove(toutRepTempE_Redim)

		# Scan du répertoire tampon ... /img_res_impair
		listeRepTempImResImp=glob.glob(self.repTempEntree+'img_res_impair' + os.sep + '*.*')

		# Epuration/elimination des fichiers tampon contenus dans ... /img_res_impair
		if len(listeRepTempImResImp)>0:
			for toutRepTempE_ImResImp in listeRepTempImResImp:
				os.remove(toutRepTempE_ImResImp)

		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)

		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0

		# -------------------------------------------------------------------
		# Boîte de groupe "Réglage de sortie de l'encodage"
		# -------------------------------------------------------------------
		vbox=QVBoxLayout()
		super(Animation_ConvertirImgEnAnim, self).__init__('grid', titre=_(u"Conversion d'images en vidéo")) # module de animation
		self.printSection()

		# Là où s'afficheront les images
		self.afficheurImgSource=SelectWidget(mode="texte", geometrie = self.mainWindowFrameGeometry)

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.

		#----------
		# Onglets
		#----------
		self.dicoTab = {}

		#=== Tabwidget de boîte de chargement des images ===#
		widget = QWidget()
		vboxMplayer = QVBoxLayout(widget)
		self.dicoTab['images']=self.tab.addTab(self.afficheurImgSource, _(u'Image(s) source(s)'))


		#=== Widget qui seront inclus dans la boite de réglage ===#
		self.addReglage(boite='grid')
		#||| titre |||#
		txt = _(u"Nombre d'images/s")
		self.label = QLabel("<u>%s</u> :" %txt) 
		self.layoutReglage.addWidget(self.label, 2, 0) 

		#||| Stacked |||#

		# Élement par défaut du stacked

		# Le codec mpeg1 prenant un nombe limité de valeurs
		# il n'aura pas droit à son spin mais à une boite de combo
		self.comboMPEG1 = QComboBox()
		listeComboMPEG1 = ['24','25','30']
		for i in listeComboMPEG1:
			self.comboMPEG1.addItem(i)
		self.connect(self.comboMPEG1,SIGNAL("currentIndexChanged(int)"),self.comboMPEG1Change)

		self.frameCombo = QFrame()
		boiteFrame = QHBoxLayout()
		boiteFrame.addWidget(self.comboMPEG1)
		self.frameCombo.setLayout(boiteFrame)

		# autre élément du stacked

		self.spin = QSpinBox()
		self.spin.setRange(1,100) # 25 par défaut

		self.curseur = QSlider(Qt.Horizontal)
		self.curseur.setRange(1,100)
		self.curseur.setMaximumSize(175,175)

		self.FrameSpinCurseur = QFrame()
		boiteFrame = QHBoxLayout()
		boiteFrame.addWidget(self.spin)
		boiteFrame.addWidget(self.curseur)
		self.FrameSpinCurseur.setLayout(boiteFrame)

		# remplissage du stacked

		self.stacked = QStackedWidget()
		self.stackedCombo = self.stacked.addWidget(self.frameCombo)
		self.stackedspinCurseur = self.stacked.addWidget(self.FrameSpinCurseur)
		self.layoutReglage.addWidget(self.stacked, 2, 1)

		txt = _(u"Codecs")
		label = QLabel("<u>%s</u> :" %txt)
		self.layoutReglage.addWidget(label, 3, 0)

		#||| boite de combo |||#

		self.combo=QComboBox() # le self sert à afficher des informations sur les items à partir de la fonction

		self.listeCombo=[(_(u'MPEG1 video (.mpg)'), 'mpeg1video', '.mpg'),\
			(_(u'HFYU: Huffman Losless YUV (.avi)'), 'huffyuv', '.avi'),\
			(_(u'DV (.dv)'), 'dv', '.dv'),\
			(_(u'QuickTime MOV (.mov)'), 'mov', '.mov'),\
			(_(u'Motion JPEG (.avi)'), 'mjpeg', '.avi'),\
			(_(u'VOB: DVD-Video stream MPEG-2 (.vob)'), 'vob', '.vob'),\
			(_(u'MPEG 4 (.mp4)'), 'mp4', '.mp4'),\
			(_(u'H263 Plus (.avi)'), 'h263p', '.avi'),\
			(_(u'DivX 4-5 (.avi)'),	'mpeg4', '.avi'),\
			(_(u'MS-MPEG4v2 (.avi)'), 'msmpeg4v2', '.avi'),\
			(_(u'Lossless JPEG (.avi)'), 'ljpeg', '.avi'),\
			(_(u'Macromedia Flash Video (.flv)'), 'flv', '.flv')]

		# Insertion des codecs de compression dans la combo box
		for i in self.listeCombo:
                	self.combo.addItem(i[0],QVariant(i[1]))

		self.layoutReglage.addWidget(self.combo, 3, 1)
		self.layoutReglage.setRowStretch(1, 1)
		self.layoutReglage.setRowStretch(4, 1)

		self.connect(self.spin,SIGNAL("valueChanged(int)"), self.spinChange)
		self.connect(self.curseur,SIGNAL("sliderMoved(int)"), self.curseurBouge)
		self.connect(self.combo,SIGNAL("currentIndexChanged(int)"),self.stackedChange)

		# [bidouillage] espacement entre les 2 colonnes
		# Rq: spacing espace les cellules en horizontal et en vertical -> pas joli
		self.layoutReglage.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

		# Chargement des paramètres de configuration
		try:
			typ = self.config.get(self.idSection,'codec')
			indice = 0 # indice de la ligne de self.listeCombo correspondant au type d'ordre
			for i in listeCombo:
				if i[1]!=typ:
					indice += 1
				else:
					break
			self.combo.setCurrentIndex(indice)
		except:
			self.combo.setCurrentIndex(0)

		try:
			spin = int(self.config.get(self.idSection,'nbr_img_sec'))
			self.spin.setValue(spin)
		except:
			self.spin.setValue(25)

		try:
			spin = self.config.get(self.idSection,'nbr_img_sec_mpeg1video')
			indice = 0 # indice de la ligne de self.listeCombo correspondant au type d'ordre
			for i in listeComboMPEG1:
				if i!=spin:
					indice += 1
				else:
					break
			self.comboMPEG1.setCurrentIndex(indice)
		except:
			# Valeur 25 sélectionnée par défaut
			indice = 0 # indice de la ligne de self.listeCombo correspondant à 25
			for i in listeComboMPEG1:
				if i!='25':
					indice += 1
				else:
					break
			self.comboMPEG1.setCurrentIndex(int(indice))


		#=== Widgets mplayer ===#
		widget = QWidget()
		vboxMplayer = QVBoxLayout(widget)
		vboxMplayer.addStretch()
		hbox = QHBoxLayout()
		vboxMplayer.addLayout(hbox)
		hbox.addStretch()

		self.mplayer=Mplayer(taille=(350,252), choixWidget=(Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_SUR_UNE_LIGNE,Mplayer.PAS_PARCOURIR))

		hbox.addWidget(self.mplayer)
		hbox.addStretch()
		vboxMplayer.addStretch()
		self.mplayer.setEnabled(False)
		self.dicoTab['video']=self.tab.addTab(widget, _(u'Vidéo créé'))

		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
		#----------------------------------------------------------------------------------------------------
		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)
		self.addLog()

	def modifBoutonsAction(self, i):
		"On active ou désactive les boutons d'action selon s'il y a des images ou pas dans le widget de sélection"
		self.boutApp.setEnabled(i)
		self.modifImageSource = 1


	def spinChange(self, i):
		"""modifie le curseur lorsque le curseur bouge"""
		self.curseur.setValue(i)
		self.config.set(self.idSection,'nbr_img_sec',self.spin.value())


	def curseurBouge(self, i):
		"""Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
		self.spin.setValue(i)


	def comboMPEG1Change(self, i):
		idCombo = self.comboMPEG1.currentText()
		self.config.set(self.idSection,'nbr_img_sec_mpeg1video',idCombo)


	def stackedChange(self,i):
		"""Le widget de sélection de la valeur numérique associée à la boite de combo peut changer suivant le codec"""
		idCombo = str(self.combo.itemData(i).toStringList()[0])

		# On cache ou on affiche le spin et le cuseur. Pour le codec DV et
		# VOB le réglage du nombre d'images/secondes n'est pas utilisé.
		if idCombo=='dv':
			self.label.hide()
			self.spin.hide()
			self.curseur.hide()
		elif idCombo=='vob':
			self.label.hide()
			self.spin.hide()
			self.curseur.hide()
		else:
			self.label.show()
			self.spin.show()
			self.curseur.show()

		#print "Combo :", idCombo
		EkdPrint(u"Combo : %s" % idCombo)
		if idCombo=='mpeg1video':
			self.stacked.setCurrentIndex(self.stackedCombo)
		else:
			self.stacked.setCurrentIndex(self.stackedspinCurseur)
		if idCombo=='ljpeg':
			self.statusBar.showMessage(_(u"La vidéo résultante ne pourra pas être lue avec tous les logiciels (ex. bon avec mplayer mais pas avec xine)"))
		else:
			self.statusBar.clearMessage()
		self.config.set(self.idSection,'codec', idCombo)


	def img_resolution_impaire(self):
		""" Fonction servant à redimensionner les images dans des résolutions paires car
		si les images chargées par l'utilisateur (au moins une des dimensions) est impaire
		FFmpeg (pour la conversion des images en vidéo) ne fera rien et renverra un
		message d'erreur: Frame size must be a multiple of 2 """

		# Si l'utilisateur charge des images de taille différente, fait le traitement
		# ...,  recharge de nouvelles images, il faut que le répertoire img_res_impair
		# soit vidé
		
		# Uniquement pour Linux et MacOSX
		if os.name in ['posix', 'mac']:
			listePresTempImResImp=glob.glob(self.repTempEntree+'img_res_impair' + os.sep + '*.*')
			listePresTempImResImp.sort()
			if len(listePresTempImResImp)>0:
				for parcIRI in listePresTempImResImp: os.remove(parcIRI)
			
		# Uniquement pour windows
		elif os.name == 'nt':
			# ---------------
			# On avait prealablement (uniquement sous windows) l'erreur suivante:
                	# WindowsError: [Error 32] Le processus ne peut pas acceder au fichier car ce
                	# fichier est utilise par un autre processus: ...
			# ---------------
			# La solution pour la version windows a ete trouvee ici:
			# http://www.nabble.com/Windows-process-ownership-trouble-td18110819.html
			# --> try: ... except WindowsError: ...
			# ---------------
			try:
				listePresTempImResImp=glob.glob(self.repTempEntree+'img_res_impair'+os.sep+'*.*')
				listePresTempImResImp.sort()
				if len(listePresTempImResImp)>0:
					for parcIRI in listePresTempImResImp: os.remove(parcIRI)
		
			except WindowsError:
				pass

		# Récupération de la liste des fichiers chargés
		lImg=self.afficheurImgSource.getFiles()

		# Liste vérif si img avec résolution impaire ds le lot d'img
		lResImpair=[]
		# Liste servant si des images avec résolution paire sont
		# présentes ds le lot
		lResPair=[]
		# Redimensionnement
		for parc_lImg in lImg:
			chemin = self.repTempEntree+'img_res_impair'+ os.sep + os.path.basename(parc_lImg)
			ouvIm = Image.open(parc_lImg)
			w = ouvIm.size[0] # largeur
			h = ouvIm.size[1] # hauteur
			# Si dimension largeur impaire
			if w % 2 == 1 and h % 2 == 0:
				red = ouvIm.resize((w-1, h)).save(chemin)
				lResImpair.append(parc_lImg)
			# Si dimension hauteur impaire
			if h % 2 == 1 and w % 2 == 0:
				red = ouvIm.resize((w, h-1)).save(chemin)
				lResImpair.append(parc_lImg)
			# Si les deux dimensions (largeur et hauteur) impaires
			if w % 2 == 1 and h % 2 == 1:
				red = ouvIm.resize((w-1, h-1)).save(chemin)
				lResImpair.append(parc_lImg)
			# Dans le cas où l'utilisateur charge des images de résolutions
			# différentes et dans ce lot il y a des images avec dimension paires,
			# la liste lResPair est remplie par ces images, les images sont tout
			# de même traitées ds la fonction stat_dim_img
			if w % 2 == 0 and h % 2 == 0: lResPair.append(parc_lImg)

		# Si la liste des images avec résolution impaire n'est pas vide, les images avec
		# résolution paire sont copiées ds le rep. img_res_impair pour être traitées avec
		# tout le lot d'images
		if len(lResImpair)>0:
			# Copie des images collectées dans le rep.tempo img_res_impair
			for parcl in lResPair: p=shutil.copy(parcl, self.repTempEntree+'img_res_impair')


	def stat_dim_img(self):
		"""Calcul statistique des dimensions des images les plus présentes dans le lot"""

		self.listeChemin=self.afficheurImgSource.getFiles()
		self.listeChemin.sort()

		# Ouverture et mise ds une liste des dimensions des images
		listePrepaRedim=[Image.open(aA).size for aA in self.listeChemin]

		# Merci beaucoup à Marc Keller de la liste: python at aful.org de m'avoir
		# aidé pour cette partie (les 4 lignes en dessous)
		dictSeq={}.fromkeys(listePrepaRedim, 0)
		for cle in listePrepaRedim: dictSeq[cle]+=1
		self.lStatDimSeq=sorted(zip(dictSeq.itervalues(), dictSeq.iterkeys()), reverse=1)
		self.dimStatImg=self.lStatDimSeq[0][1]

		#print "Toutes les dimensions des images (avec le nbre d'images):", self.lStatDimSeq
		#print 'Dimension des images la plus presente dans la sequence:', self.dimStatImg
		#print "Nombre de tailles d'images différentes dans le lot :", len(self.lStatDimSeq)
		EkdPrint(u"Toutes les dimensions des images (avec le nbre d'images): %s" % self.lStatDimSeq)
		EkdPrint(u'Dimension des images la plus presente dans la sequence: %s' % str(self.dimStatImg))
		EkdPrint(u"Nombre de tailles d'images différentes dans le lot: %s" % len(self.lStatDimSeq))

		if len(self.lStatDimSeq)>1:
			return 0
		else:
			return 1

		# On libere la memoire
		del listePrepaRedim, aA, dictSeq, cle


	def redim_img(self):
		"""Si l'utilisateur charge des images avec des tailles complètement différentes --> les images de la séquence  peuvent être redimensionnées"""

		if not self.stat_dim_img():
			reply = QMessageBox.warning(self, 'Message',
			_(u"Vos images ne sont pas toutes de la même taille. Voulez-vous redimensionner les images de sortie à la taille la plus répandue dans la séquence?"), QMessageBox.Yes, QMessageBox.No) ##
			if reply == QMessageBox.No:
				return

			# Les images de tailles différentes à la plus répandue sont redimensionnées
			# dans un répertoire temporaire.
			# Les images redimensionnées voient leur chemin modifié dans la liste des
			# chemins des images sources. Les autres chemins ne changent pas.

		index=0

		for chemImg in self.listeChemin:
			obImg=QImageReader(chemImg)
			size = (obImg.size().width(), obImg.size().height())
			## On retaille sur une dimension paire
			if ( ( self.dimStatImg[0] % 2 ) != 0 ):
				self.dimStatImg = ( self.dimStatImg[0] + 1, self.dimStatImg[1] )
			if ( ( self.dimStatImg[1] % 2 ) != 0 ):
				self.dimStatImg = (self.dimStatImg[0], self.dimStatImg[1] + 1)
			##
			# Dans cet ancien code seulement les images qui n'avaient pas les mêmes dimensions
			# que les autres étaient redimensionnées, mais cela pose un problème au moment du
			# traitement final car ces images redimensionnées sont reversées/mises à la fin
			# du lot d'images au moment du traitement, ce qui evidemment pose un énorme souci !
			'''
			if size==self.dimStatImg:
				chemSortie = chemImg
				print chemImg, " : Ok"
			else :
				chemSortie = self.repTempEntree+'redim'+ os.sep + os.path.basename(chemImg)
				sRedim=EkdPreview(chemImg, self.dimStatImg[0], self.dimStatImg[1], 10, False, False, True).get_preview()
				sRedim.save(chemSortie)
			'''
			# ... la solution (quand au moins une des images) n'a pas la même dimension que les
			# autres est d'opérer le redimensionnement sur tout le lot d'images chargées (et là 
			# les images sont forcément dans le bon ordre)
			chemSortie = self.repTempEntree+'redim'+ os.sep + os.path.basename(chemImg)
			sRedim=EkdPreview(chemImg, self.dimStatImg[0], self.dimStatImg[1], 10, False, False, True).get_preview()
			sRedim.save(chemSortie)

			self.listeChemin[index] = chemSortie
			index += 1
		

	def appliquer(self, nomSortie=None, ouvert=1):
		""" appelle la boite de dialogue de sélection de fichier à sauver et appel de la fonction de séparation audio-vidéo """
		
		# Si l'utilisateur charge des images de taille différente, fait le traitement
		# ...,  recharge de nouvelles images, il faut que le répertoire de redimen-
		# sionnement  soit vidé
		listePresRedim=glob.glob(self.repTempEntree+'redim'+ os.sep +'*.*')
		if len(listePresRedim)>0:
			for parcR in listePresRedim: os.remove(parcR)
			
		listePresTemp=glob.glob(self.repTempEntree+'*.*')
		if len(listePresTemp)>0:
			for parcT in listePresTemp: os.remove(parcT)

		self.img_resolution_impaire()

		listeRedim=glob.glob(self.repTempEntree+'img_res_impair'+ os.sep + '*.*')
		listeRedim.sort()

		# Si aucune image ne comporte une résolution impaire
		if len(listeRedim)==0:
			# ATTENTION IL FAUT AJOUTER CECI NE PAS OUBLIER !!!
			# Récupération de la liste des fichiers chargés
			self.listeChemin=self.afficheurImgSource.getFiles()
		# Si une image comporte une résolution impaire
		elif len(listeRedim)>0: self.listeChemin=listeRedim

		# Récupération du chemin + image chargée et de l'extension
		# (la première image de la liste)
		fich, self.ext=os.path.splitext(self.listeChemin[0])
		
		self.ext = self.ext.lower()

		# Recup de la taille de la 1ère chargée
		imgTaille=Image.open(self.listeChemin[0])

		# Si toutes les images sont de la même taille, alors on applique la procédure normale
		# sinon on passe par la création d'un répertoire tampon et on entre dans la structure
		# conditionnelle « if not taillesImgCorrectes »
		taillesImgCorrectes = 1 # par défaut les images sont considérant comme étant à la bonne taille
		nbrImg = len(self.listeChemin)

		for parcChemTempo in self.listeChemin:
			if Image.open(parcChemTempo).size==imgTaille.size:
				pass
			else:
				taillesImgCorrectes = 0
				break

		#print "taillesImgCorrectes", taillesImgCorrectes
		EkdPrint(u"taillesImgCorrectes %s" % taillesImgCorrectes)
		self.redim_img()

		#=== Détermination des chemins d'entrée et sortie ===#

		index=self.combo.currentIndex()
		if not nomSortie:
			# suffix du fichier actif
			suffix=self.listeCombo[index][2]
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			cheminFichierEnregistrerVideo = saveDialog.getFile()

		else: # module séquentiel
			cheminFichierEnregistrerVideo = nomSortie

		if not cheminFichierEnregistrerVideo: return

		imgObj = Image.open(self.listeChemin[0])

		idCombo = self.listeCombo[index][1]
		#print "Combo :", idCombo
		EkdPrint(u"Combo : %s" % idCombo)

		# On récupère la valeur numérique associée au codec de 2 façon différentes
		if idCombo=='mpeg1video':
			valeurNum = str(self.comboMPEG1.currentText())
		else:
			valeurNum = str(self.spin.value())
		
		# Uniquement pour Linux et MacOSX
		if os.name in ['posix', 'mac']:
		
			listeTemp=[]
			for parcChemTempo in self.listeChemin:
				cop=shutil.copy("".join(parcChemTempo), self.repTempEntree)
				listeTemp.append(parcChemTempo)
			# Mise en ordre
			listeTemp.sort()

			# Renommage des images dans le répertoire temporaire
			for parc in range(len(listeTemp)):
				## Il existe shutil.copy pour copier les fichier de ##########
				## façon identique sous windows et sous Linux ################
				shutil.copy(listeTemp[parc], self.repTempEntree+string.zfill((parc+1), 8) + self.ext)

			## On duplique la dernière image pour que quand le nombre d'image est faible, on puisse la voir
			shutil.copy(listeTemp[parc], self.repTempEntree+string.zfill((parc+2), 8) + self.ext)

		# Uniquement pour windows
		elif os.name == 'nt':
			
			listePreTemp=[]
			for parcChemPreTempo in self.listeChemin:
				cop=shutil.copy("".join(parcChemPreTempo), self.repTempEntree)
				listePreTemp.append(parcChemPreTempo)
			# Mise en ordre
			listePreTemp.sort()
                	# Scan du répertoire temporaire
                	listeTemp = glob.glob(self.repTempEntree+os.sep+'*.*')
                	listeTemp.sort()
                
                	# Renommage des fichiers du rep temporaire vers lui-même.
                	# Renommage des images: 00000001.jpg, 00000002.jpg, 00000003.jpg, ...
                	for nbr, parcRenom in enumerate(listeTemp): 
				s=shutil.move(parcRenom, self.repTempEntree+string.zfill((nbr+1), 8)+self.ext)

		# Scan du répertoire tampon (liste)
		repT=glob.glob(self.repTempEntree+'*.*')
		repT.sort()

		# Si les images chargées par l'utilisateur et les images copiées dans le rep
		# temporaire sont identiques (c'est à dire les images avant renommange), elles
		# sont eliminées.
		for parc_repT in repT:
			for parc_lChem in self.listeChemin:
				if os.path.basename(parc_repT)==os.path.basename(parc_lChem):
					os.remove(parc_repT)

		cheminVideoEntre = self.repTempEntree+'%08d'+self.ext

		#print 'cheminVideoEntre', cheminVideoEntre
		EkdPrint(u'cheminVideoEntre %s' % cheminVideoEntre)

		tailleIm = [str(imgObj.size[0]), str(imgObj.size[1])]

		# Drapeau de bon déroulement des opérations
		drapReussi = 1

		try:
                       ffmpeg = WidgetFFmpeg(idCombo, cheminVideoEntre, cheminFichierEnregistrerVideo, valeurNum=valeurNum, laisserOuvert=ouvert, tailleIm=tailleIm)
                       ffmpeg.setWindowTitle(_(u"Conversion des images en vidéo"))
                       ffmpeg.exec_()

		except:
			drapReussi = 0
			messageErrAnEnc=QMessageBox(self)
			messageErrAnEnc.setText(_(u"Un problème est survenu lors de la conversion"))
			messageErrAnEnc.setWindowTitle(_(u"Error"))
			messageErrAnEnc.setIcon(QMessageBox.Warning)
			messageErrAnEnc.exec_()

		# Si tout a bien marché, on active mplayer avec le chemin de sortie de la vidéo
		if drapReussi:
			self.mplayer.listeVideos = [cheminFichierEnregistrerVideo]
			self.mplayer.setEnabled(True)
			self.tab.setCurrentIndex(self.dicoTab['video'])
		### Information à l'utilisateur
		self.infoLog(self.listeChemin, None, None, cheminFichierEnregistrerVideo)

		return cheminFichierEnregistrerVideo

		# On libere la memoire
		del listePresRedim, parcR, listePresTemp, parcT, fich, self.ext, imgTaille, taillesImgCorrectes, nbrImg, parcChemTempo, nomSortie, rep, cheminVideoSorti, imgObj, i, idCombo, valeurNum, ext, cheminVideoSorti, listeTemp, parcChemTempo, cop, parc,repT, parc_repT, parc_lChem, cheminVideoEntre, tailleIm, mencoder, drapReussi


	def sequentiel(self, entree, sortie, ouvert=0):
		"""Utile dans le module du même nom. Applique les opérations de la classe. Retourne le vrai nom du fichier de sortie"""

		return self.appliquer(sortie, ouvert)


	def sequentielReglage(self):
		"""Utile dans le module du même nom. Récupère le widget de réglage associé à l'identifiant donné en 1er argument. Retourne l'instance du widget de réglage"""
		self.groupReglage.setTitle(_(u"Réglages: convertir des images en animation"))
		return self.groupReglage


	def afficherAide(self):
		""" Boîte de dialogue d'aide """
		
		super(Animation_ConvertirImgEnAnim, self).afficherAide(_(u"<p><b>Qu’est-ce qu’une vidéo en fin de compte ?. La réponse est des images se succédant à une certaine fréquence (24 images par seconde, par exemple), que nous interprétons comme un mouvement, c’est-à-dire une image animée. Traiter les images pour EKD, c’est leur donner la possibilité de se transformer en fichier vidéo, c'est exactement ce que vous pouvez faire ici.</b></p><p>Dans l'onglet <b>'Images sources'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.<p><p>Faites ensuite les réglages du <b>'Nombre d'images/s'</b> (nombre d'images par seconde), puis choisissez le codec dans la liste déroulante <b>'Codecs'</b>.</p><p>Cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde de votre vidéo dans la boîte de dialogue, entrez le <b>'Nom de Fichier'</b> dans le champ de texte réservé à cet effet ... cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion <b><font color='blue'>(attention, la barre de progression reste à 10, mais ne vous inquietez pas le traitement des images a bien lieu)</font></b>. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Vous pouvez visionner votre vidéo (après conversion) dans l'onglet <b>'Vidéo créée'</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>'Image(s) source(s)'</b>, vous accédez à des paramètres vous permettant différents affichages des images</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


	def saveFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurImgSource.saveFileLocation(self.idSection)

	def loadFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurImgSource.loadFileLocation(self.idSection)

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
