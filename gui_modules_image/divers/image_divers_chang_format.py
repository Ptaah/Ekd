#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, glob, string, Image, ImageOps
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurImagePourEKD
from gui_modules_image.image_base import Base, SpinSlider

from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_lecture.affichage_image.afficheurImage import VisionneurEvolue

# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Gestion de l'aide via EkdAide
from gui_modules_common.EkdWidgets import EkdAide

# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Image_Divers_ChangFormat(QWidget):
	"""# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Changer format
	# Gestion de 16 formats de fichiers
	# -----------------------------------"""
	def __init__(self, statusBar, geometry):
        	QWidget.__init__(self)

		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------
		#=== tout sera mis dans une boîte verticale ===#
		vbox=QVBoxLayout(self)

		#=== Création des répertoires temporaires ===#
		# Utilisation de EkdConfig
		self.repTampon = EkdConfig.getTempDir() + os.sep

		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)

		# Au cas où le répertoire existait déjà et qu'il n'était pas vide
		# -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			os.remove(toutRepCompo)

		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)

		# Est-ce que des images ont été converties et qu'elles n'ont pas encore été montrées?
		# Marche aussi quand la conversion a été arrêté avant la fin de la 1ère image
		self.conversionImg = 0

		# Est-ce qu'une prévisualisation a été appelée?
		self.previsualImg = 0
		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0

		# Délai avant conversion
		self.timer = QTimer()
		self.connect(self.timer, SIGNAL('timeout()'), self.sonderTempsActuel)

		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()
		# Gestion de la configuration via EkdConfig
		# Paramètres de configuration
		self.config = EkdConfig
		# Identifiant du cadre
		self.idSection = "image_changer_format"
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

		# boite de combo
		self.comboReglage=QComboBox()
		self.listeComboReglage=[(_(u'JPEG (.jpg)'), '.jpg'),\
					(_(u'JPEG (.jpeg)'), '.jpeg'),\
					(_(u'PNG (.png)'), '.png'),\
					(_(u'GIF (.gif)'), '.gif'),\
					(_(u'BMP (.bmp)'), '.bmp'),\
					(_(u'PPM (.ppm)'), '.ppm'),\
					(_(u'TIFF (.tiff)'), '.tiff'),\
					(_(u'TIF (.tif)'), '.tif')]

		# Se trouve directement dans l'onglet Réglages
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

		# Insertion des formats dans la combo box
		for i in self.listeComboReglage:
                	self.comboReglage.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"), self.changerComboReglage)
		# Affiche l'entrée de la boite de combo inscrite dans un fichier de configuration
		self.base.valeurComboIni(self.comboReglage, self.config, self.idSection, 'format')

		self.grid2 = QGridLayout()

		# Label qualité pour la qualité (compression) lors de la sauvegarde en JPEG
		self.labQualite=QLabel(_(u"Qualité"))
		self.labQualite.hide()

		self.grid2.addWidget(QLabel(_(u'Type de format après traitement')), 0, 0)
		self.grid2.addWidget(self.comboReglage, 0, 1)
		self.grid2.addWidget(self.labQualite, 2, 0)
		# Réglage de la qualité pour la qualité (compression) lors de la sauvegarde en JPEG
		self.spin3=SpinSlider(1, 100, 75, '', self)
		self.spin3.hide()

		i = self.comboReglage.currentIndex()
		idCombo=str(self.comboReglage.itemData(i).toStringList()[0])
		if idCombo in ['.jpg', '.jpeg']:
			self.labQualite.show()
			self.spin3.show()
		else:
			self.labQualite.hide()
			self.spin3.hide()

		self.grid2.addWidget(self.spin3, 2, 1)
		self.connect(self.spin3, SIGNAL("valueChanged(int)"), self.changeQualitePourJPEG)

		self.grid2.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid2)
		vboxReglage.addStretch()

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
		self.afficheurImgSource=SelectWidget(geometrie = geometry)
 		self.afficheurImgDestination=Lecture_VisionImage(statusBar)

		self.indexTabImgSource = self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		self.indexTabReglage=self.tabwidget.addTab(self.framReglage, _(u'Réglages'))
		self.indexTabImgDestin=self.tabwidget.addTab(self.afficheurImgDestination, _(u'Image(s) après traitement'))
		self.indexTabInfo=self.tabwidget.addTab(self.framImg, _(u'Infos'))

		vbox.addWidget(self.tabwidget)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.

		#------------------
		# Widgets du bas
		#------------------

		# boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones/icone_aide_128.png"))
		boutAide.setFocusPolicy(Qt.NoFocus)
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
		self.boutApPremImg = QPushButton(_(u" Voir le résultat"))
		self.boutApPremImg.setIcon(QIcon("Icones/icone_visionner_128.png"))
		self.boutApPremImg.setFocusPolicy(Qt.NoFocus)
		self.boutApPremImg.setEnabled(False)
		self.connect(self.boutApPremImg, SIGNAL("clicked()"), self.visu_1ere_img)
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
		hbox.addWidget(self.boutApPremImg)
		hbox.addStretch()
		hbox.addWidget(self.boutApp)
		vbox.addLayout(hbox)

		self.setLayout(vbox)

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

		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)

		#----------------------------------------------------------------------------------------------------
		# Signal pour afficher ou ne pas afficher les widgets de changement de qualité pour les images
		#----------------------------------------------------------------------------------------------------

		self.connect(self.comboReglage, SIGNAL("currentIndexChanged(int)"), self.changerQualJPEG)


	def modifBoutonsAction(self, i):
		"On active ou désactive les boutons d'action selon s'il y a des images ou pas dans le widget de sélection"
		self.boutApp.setEnabled(i)
		self.boutApPremImg.setEnabled(i)
		self.modifImageSource = 1


	def changerComboReglage(self, i):
		"""Récup/affichage ds le terminal de l'index de self.comboReglage"""
		#print self.comboReglage.currentText()
		EkdPrint(u"%s" % self.comboReglage.currentText())
		self.config.set(self.idSection, 'format', self.listeComboReglage[i][1])


	def changerQualJPEG(self):
		''' Changement de la qualité pour les images jpeg à l'enregistrement '''

		# Si on sélectionne le format JPEG (avec extension .jpg ou .jpeg) dans la liste
		# déroulante, on peut régler la qualité du JPEG pour la sauvegarde
		if self.comboReglage.currentIndex() in [0, 1]:
			self.labQualite.show()
			self.spin3.show()
		# Si on sélectionne tous les autres formats, les widgets n'apparaissent pas
		else:
			self.labQualite.hide()
			self.spin3.hide()


	def changeValNbreImg_1(self):
		"""Gestion du nombre d'images à traiter"""
		#print "Traitement a partir de l'image (numero):", self.spin1.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2.value())


	def changeQualitePourJPEG(self):
		#print "Compression JPEG, qualité:", self.spin3.value()
		EkdPrint(u"Compression JPEG, qualité: %s" % self.spin3.value())


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


	def visu_1ere_img(self):
		"""Fonction pour faire une simulation de rendu (avec les réglages opérés dans l'onglet Réglages)
		et ce à partir du bouton Aperçu à partir de la première image, toujours dans l'onglet Réglages.
		Pour les commentaires, se référer à la fonction chang_format juste en dessous"""

		# Récupération du fichier sélectionné par l'utilisateur (si pas de fichier
		# sélectionné par l'utilisateur, la 1ère image de la liste est prise)
		file = self.afficheurImgSource.getFile()
		if not file: return
		self.listeImgSource = [file]

		i = self.comboReglage.currentIndex()
		ext=self.comboReglage.itemData(i).toString()
		ext=str(ext).lower()

		# Formats (extensions) supportées: .bmp, .gif, .jpeg, .jpg, .mng, .pbm, .pgm,
		# .png, .ppm, .svg, .tif, .tiff, .xbm, .xpm
		formats = [".%s" % unicode(format).lower() \
			for format in QImageReader.supportedImageFormats()]

		# Chemin+nom d'image pour la sauvegarde
		self.cheminCourantSauv = self.repTampon+'0_image_visu_'+string.zfill(1, 6)+ext

		# CONVERSION

		# Uniquement pour Linux et MacOSX
		if os.name in ['posix', 'mac']:
			# On sélectionne le 'Type de format après traitement' à JPEG (.jpg)
			# ou JPEG (.jpeg) le traitement se fait par Python Imaging Library
			if i in [0, 1]:
				im = Image.open(self.listeImgSource[0]).save(self.cheminCourantSauv, quality=self.spin3.value())
			# Si on sélectionne les autres entrées, le traitement se fait par ImageMagick
			else:
				import locale
				# Conversion immédiate dans le rep tampon
				os.system(("convert "+"\""+self.listeImgSource[0]+"\""+' '+"\""+self.cheminCourantSauv+"\"").encode(locale.getdefaultlocale()[1]))
				
		# Uniquement pour windows
		elif os.name == 'nt':
			# Dans la version windows les autres entrees ne sont pas traitees 
			# par ImageMagik mais directement par Python Imaging Library (car 
			# par le traitement avec ImageMagick rien ne s'affiche, bizarre !!!)
			if i in [0, 1, 2, 3, 4, 5, 6, 7]:
				im = Image.open(self.listeImgSource[0]).save(self.cheminCourantSauv, quality=self.spin3.value())

		# AFFICHAGE

		# Récup de l'extension chargée
		ext_chargee=os.path.splitext(self.listeImgSource[0])[1]

		# Si le format (l'extension) chargé et le format sélectionné pour la sortie
		# dans Réglages sont des formats supportés, l'image avec ce format est
		# simplement affichéé
		# ----------------------------------------------------------------------
		# Aussi bizarre que cela puisse paraître (et .xpm est un format reconnu)
		# la conversion en xpm se fait bien mais l'image n'est pas lue dans le
		# lecteur --> alors conversion en jpeg ... et l'image est lue
		# ----------------------------------------------------------------------
		if ext in formats:
			# Récupération de la liste contenant le chemin+fichier contenus
			# contenu dans le répertoire temporaire
			listeImgDestinVisuTmp_0=glob.glob(self.repTampon+'*.*')
			listeImgDestinVisuTmp_0.sort()
			# Elimination des fichiers parasites si multiples conversions
			# --> seulement l'extension de sortie sélectionnée est gardée
			for parctemp_0 in listeImgDestinVisuTmp_0:
				if os.path.splitext(parctemp_0)[1]!=ext:
					os.remove(parctemp_0)

		# Affichage de l'image temporaire
		# Ouverture d'une boite de dialogue affichant l'aperçu.
		#
		# Affichage par le bouton Voir le résultat
		visio = VisionneurEvolue(self.cheminCourantSauv)
		visio.redimenFenetre(self.mainWindowFrameGeometry, 1., 0.7)
		visio.exec_()

		return 0


	def chang_format(self):
		""" Changer format (gestion de différents formats de fichiers) """

		# Récupération de la liste des fichiers chargés
		self.listeChemin=self.afficheurImgSource.getFiles()

		# Récup du format sélectionné par l'utilisateur
		i = self.comboReglage.currentIndex()
		ext=self.comboReglage.itemData(i).toString()
		ext=str(ext).lower()
		#print "format:", ext
		EkdPrint(u"format: %s" % ext)

		nbreElem=len(self.listeChemin)

		# Liste pour affichage des images chargées (ds le tabwidget)
		listeAff_1=[]
		# Liste pour affichage des pages sauvegardées (ds le tabwidget)
		listeAff_2=[]

		# La page Image résultat devient visible
		#self.tabwidget.setCurrentIndex(self.indexImageResultat)

		# Liste des formats supportés pour l'affichage
		formats = [".%s" % unicode(format).lower() \
			for format in QImageReader.supportedImageFormats()]

		#print "formats:", formats
		EkdPrint(u"formats: %s" % formats)

		process = QProcess(self)

		# Boucle principale
		for parc in range(nbreElem):

			# Chemin de sauvegarde
			vraiCheminSauv = self.chemDossierSauv+'_'+string.zfill(parc+self.spin1.value(), self.spin2.value())+ext

			# On sélectionne le 'Type de format après traitement' à JPEG (.jpg) ou JPEG (.jpeg)
			
			# Uniquement pour Linux et MacOSX
			if os.name in ['posix', 'mac']:
				# le traitement se fait par Python Imaging Library
				if i in [0, 1]:

					im = Image.open(self.listeChemin[parc]).save(vraiCheminSauv, quality=self.spin3.value())
					
			# Uniquement pour windows
			elif os.name == 'nt':
				
				if i in [0, 1, 2, 3, 4, 5, 6, 7]:
					
					im = Image.open(self.listeChemin[parc]).save(vraiCheminSauv, quality=self.spin3.value())

			# Bouton Cancel pour arrêter la progression donc le process
			if (self.progress.wasCanceled()): break


			# Si on sélectionne les autres entrées, le traitement se fait par ImageMagick
			else:

				# Enregistrement/conversion des formats sélectionnés
				process.start("convert "+"\""+self.listeChemin[parc]+"\" "+"\""+vraiCheminSauv+"\"")

				# Ajout des images par la variable vraiCheminSauv dans la liste
				self.listeImgDestin.append(vraiCheminSauv)

				listeAff_1.append(self.listeChemin[parc])
				listeAff_2.append(vraiCheminSauv)

				# ================================================================== #
				# Calcule le pourcentage effectue a chaque passage et ce pour la
				# barre de progression .
				# ---------------------------------------------
				val_pourc=((parc+1)*100)/nbreElem

				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée
				self.progress.setValue(val_pourc)
				QApplication.processEvents()
				# Bouton Cancel pour arrêter la progression donc le process
				if (self.progress.wasCanceled()): break
				# --------------------------------------------

				if not process.waitForStarted(3000):
					QMessageBox.warning(None, _(u"Erreur"), _(u"Bogue au lancement de la commande"))
				process.waitForFinished(-1)

		# Conditions d'affichage des images dans l'interface
		# Si le format est supporté pour l'affichage ...
		if ext in formats:

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
		texte1=_(u" Image(s) chargée(s)")
		texte2=_(u" Image(s) convertie(s)")
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
		self.framImg.setEnabled(True)

		# remise à 0 de la variable provisoire de log
		self.infosImgProv=''
		# ---------------------------------------------------------


	def sonderTempsActuel(self):
		"""x ms après l'apparition de la boite de dialogue, on lance la conversion. But: faire en sorte que la boite de dialogue ait le temps de s'afficher correctement"""
		self.timer.stop()
		self.appliquer()


	def appliquer(self):
		"""Lancement de la fonction chang_format"""
		self.chang_format()


	def appliquer0(self):
		"""Préparation de la conversion"""

		suffix=""
		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
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

		# ATTENTION _ a été mis à la place de tr car le script de mise à jour gettext (mise_a_jour_gettext.py)
		# ne fonctionne pas pour ekdDoc.pot avec les clés --keyword donc les nouvelles lignes vides encore
		# non traduites de la doc se retrouveront dans ekd.pot au lieu de ekdDoc.pot

		# Utilisation de EkdAide
		messageAide=EkdAide(parent=self)
		messageAide.setText(_(u"<p><b>Vous pouvez ici changer/transformer le format des images (et par là même en changer leur extension). En ce qui concerne le JPEG, vous pourrez sélectionner deux types d'extension (jpeg ou jpg), toujours pour le JPEG, vous aurez aussi la possiblité de régler la qualité (c'est à dire la compression).</b></p><p><b>Les formats pris en compte sont: JPEG, PNG, GIF, BMP, PPM, TIFF et TIF.</b></p><p>Dans l'onglet <b>'Images sources'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Dans l'onglet <b>'Réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</b></font>, ensuite choisissez votre <b>'Type de format après traitement'</b> et réglez la <b>'Qualité'</b> (disponible uniquement si vous avez sélectionné une image JPEG en sortie). Cliquez sur le bouton <b>'Voir le résultat'</b> (vous voyez à ce moment le résultat de vos réglages sur la première image du lot s'afficher dans une nouvelle fenêtre).</p></p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Si vous faites un clic droit de la souris (sur l'image) dans l'onglet <b>Image(s) après traitement</b>, vous accédez à des paramètres vous permettant différents affichages de la dite image. De même dans cet onglet vous pouvez lancer la visualisation des images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite).</p><p>L'onglet <b>'Infos'</b> vous permet de voir le filtre utilisé, les image(s) chargée(s) et les image(s) convertie(s).</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'choixReglage', unicode(self.comboReglage.currentIndex()))
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2.value()))
		EkdConfig.set(self.idSection, u'spin3', unicode(self.spin3.value()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.comboReglage.setCurrentIndex(int(EkdConfig.get(self.idSection, u'choixReglage')))
		self.spin1.setValue(int(EkdConfig.get(self.idSection, u'spin1')))
		self.spin2.setValue(int(EkdConfig.get(self.idSection, u'spin2')))	
		self.spin3.setValue(int(EkdConfig.get(self.idSection, u'spin3')))
