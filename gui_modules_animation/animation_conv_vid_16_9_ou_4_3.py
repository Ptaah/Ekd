#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, glob
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_common.EkdWidgets import EkdAide
from gui_modules_image.selectWidget import SelectWidget
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Animation_ConvertirAnimEn_16_9_Ou_4_3(Base):
	""" -----------------------------------------
	# Cadre accueillant les widgets de :
	# Animation >> Montage vidéo >> Vidéo seulement
	# -----------------------------------------"""

	def __init__(self, statusBar):

		# On joue avec l'héritage de Base
		vbox=QVBoxLayout()

		# Identifiant de la classe
		self.idSection = "animation_conversion_video_16_9_4_3"
		super(Animation_ConvertirAnimEn_16_9_Ou_4_3, self).__init__('vbox', titre=_(u"Conversion 16/9 - 4/3"))
		self.printSection()

		# Liste de fichiers initiaux (contenu dans le fichier de configuration)
		self.lstFichiersSource = []
		self.lstFichiersSourceProv = [] # idem mais provisoire (sert à récupérer les chemins dans l'ordre de sélection)

		self.statusBar = statusBar
		# -------------------------------------------------------------------
		# Boîte de groupe : "Fichier vidéo source"
		# -------------------------------------------------------------------
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.mpg", "*.mpeg", "*.vob"], mode="texte", video = True)
		###################################################################################################
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		#--------------------------------------------------------------------

		groupReglage=QGroupBox()
		self.layoutReglage=QVBoxLayout(groupReglage)

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.


		#=== Widget qui seront inclus dans la boite de réglage ===#
		# boite de combo
		self.combo=QComboBox() # le self sert à afficher des informations sur les items à partir de la fonction
		listeCombo=[	(_(u'16/9 ème --> rapport 1.77') ,'16_9'),\
				(_(u'16/10 ème --> rapport 1.60') ,'16_10'),\
				(_(u'4/3 --> rapport 1.33') ,'4_3'),\
				(_(u'5/3 --> rapport 1.66') ,'5_3'),\
				(_(u'Panoramique 1,85:1 --> rapport 1.85') ,'1_85'),\
				(_(u'Cinemascope Panavision 2,35:1 --> rapport 2.35') ,'2_35'),\
				(_(u'CinemaScope optique 2,39:1 --> rapport 2.39') ,'2_39'),\
				(_(u'CinemaScope magnétique 2,55:1 --> rapport 2.55') ,'2_55'),]
		##############################################################################################
		# Insertion des codecs de compression dans la combo box
		for i in listeCombo:
                	self.combo.addItem(i[0],QVariant(i[1]))

		self.connect(self.combo, SIGNAL("activated(int)"), self.nouvelleResolution)

		self.layoutReglage.addWidget(self.combo, 0, Qt.AlignHCenter)

		# Chargement du paramètre de configuration
		try:
			typ = EkdConfig.get(self.idSection,'type')
			indice = 0 # indice de la ligne de self.listeCombo correspondant au type d'ordre
			for i in listeCombo:
				if i[1]!=typ:
					indice += 1
				else:
					break
			self.combo.setCurrentIndex(indice)
		except:
			self.combo.setCurrentIndex(0)

		self.nouvelleResolution()
		self.add(groupReglage, _(u"Réglages"))
		self.addPreview()
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

		self.emit(SIGNAL("loaded"))
		return self.chemin


	def nouvelleResolution(self):
		"""Mets une liste de chemins vidéos dans l'ordre alpha-numérique si tel est le choix de l'utilisateur"""
		i=self.combo.currentIndex()
		idCombo = str(self.combo.itemData(i).toStringList()[0])
		#print "Combo :", idCombo
		EkdPrint(u"Combo : %s" % idCombo)
		# Si ordre alpha-numérique choisi, alors on ordonne la liste
		if idCombo == '16_9':
			self.idCombo=1.77777
		elif idCombo == '16_10':
			self.idCombo=1.60
		elif idCombo == '4_3':
			self.idCombo=1.33333
		elif idCombo == '5_3':
			self.idCombo=1.66666
		elif idCombo == '1_85':
			self.idCombo=1.85
		elif idCombo == '2_35':
			self.idCombo=2.35
		elif idCombo == '2_39':
			self.idCombo=2.39
		elif idCombo == '2_55':
			self.idCombo=2.55
		######################################################################################
		EkdConfig.set(self.idSection,'type',idCombo)
		######################################################################################


	def fctRadioSource(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: self.mplayer.listeVideos = self.lstFichiersSource


	def fctRadioConvert(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: self.mplayer.listeVideos = self.lstFichiersSortie


	def ouvrirSource(self, nomEntree=None):
		""" Récupération des chemins vidéo sélectionnée """

		# On n'utilise pas le fonction recupSources du fichier animation_base.py contenu dans
		# le répertoire gui_modules_animation car pour cette fonction uniquement les fichiers
		# AVI (donc extension .avi) sont autorisés
		try:
			repEntree = EkdConfig.get('general', 'video_input_path')
		except:
			repEntree = os.path.expanduser('~')
		####################################################################################

		txt = _(u"Fichiers vidéos")

		if not nomEntree:
			liste=QFileDialog.getOpenFileNames(None, _(u"Ouvrir"), repEntree,
				"%s (*.avi *.mpg *.mpeg *.vob)\n" %txt)

			self.liste = [unicode(i) for i in liste]
		####################################################################################

		chemin=self.liste
		if not chemin: return

		## On a récupérer la vidéo, on défini le nouveau chemin par défaut des vidéos
		EkdConfig.set('general', 'video_input_path', os.path.dirname(chemin[0]))

		self.lstFichiersSource = []

		for fichier in chemin:
			self.lstFichiersSource.append(fichier)

		# Appel de la fonction nouvelleResolution pour application 16/9 ou 4/3
		self.nouvelleResolution()
		#print 'self.idCombo', self.idCombo
		EkdPrint(u'self.idCombo %s' % self.idCombo)

		# Le bouton appliquer devient utilisable
		self.boutApp.setEnabled(True)
		self.boutApp.setToolTip("")

		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = self.lstFichiersSource
		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(False)
		self.radioConvert.setEnabled(False)

		# Affichage du chemin + nom de fichier dans la ligne d'édition
		self.ligneEditionSource.setText(liste[0])

		self.statusBar.showMessage(_(u"La vidéo résultante ne pourra pas être lue avec tous les logiciels"))


	def afficherAide(self):
		""" Boîte de dialogue de l'aide """

		super(Animation_ConvertirAnimEn_16_9_Ou_4_3,self).afficherAide(_(u"<p><b>Vous pouvez ici changer les proportions des images dans une vidéo (en quelque sorte les dimensions d'ensemble de la vidéo). Selon la définition de Wikipédia: 'Le format de projection cinématographique définit le rapport entre la largeur et la hauteur de l'image projetée'. Source: http://fr.wikipedia.org/wiki/Format_de_projection<b></p><p><b>Les options proposées ici sont: 16/9ème, 16/10ème, 4/3, 5/3, 1:85, 2:35, 2:39 et 2:55.<b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> faites votre choix dans la liste déroulante.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la conversion) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la conversion <b>'vidéo convertie'</b> ou bien encore les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


	def appliquer(self, nomSortie=None, ouvert=1):
		"""Fusion de vidéos"""

		#=== Récupération de la liste de fichiers ===#
		chemin=unicode(self.getFile())
		if not nomSortie:
			# suffix du fichier actif
			suffix=os.path.splitext(chemin)[1]
			# suffix du codec actif
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))

			cheminFichierEnregistrerVideo = saveDialog.getFile()
		else: # module séquentiel
			cheminFichierEnregistrerVideo = nomSortie
		if not cheminFichierEnregistrerVideo:
			return
		#####################################################################################################
		from moteur_modules_animation.mplayer import getVideoSize
		(videoLargeur, videoHauteur) = getVideoSize(chemin)
		#print videoLargeur, videoHauteur
		EkdPrint(u"%s %s" % (videoLargeur, videoHauteur))
		# ---------------------------------------------------------------------------------------------
		#####################################################################################################

		#######Détection/redimensionnement de la taille de la vidéo #################
		# --> Car FFmpeg ne peut traitre que des vidéo de résolution paire
		#videoLargeur = float(videoLargeur)
		videoHauteur = float(videoLargeur) / float(self.idCombo) # Changement fait le 25/03/11
		videoLargeur = int(videoLargeur)
		videoHauteur = int(videoHauteur) # Changement fait le 25/03/11

		# Si dimension largeur impaire
		if int(videoLargeur) % 2 == 1 and int(videoHauteur) % 2 == 0:
			videoLargeur = videoLargeur - 1
			videoHauteur = videoHauteur
			tailleVideo = [str(videoLargeur), str(videoHauteur)]
			#print tailleVideo, type(tailleVideo)
			EkdPrint(u"%s %s" % (tailleVideo, type(tailleVideo)))
		# Si dimension hauteur impaire
		if int(videoHauteur) % 2 == 1 and int(videoLargeur) % 2 == 0:
			videoLargeur = videoLargeur
			videoHauteur = videoHauteur - 1
			tailleVideo = [str(videoLargeur), str(videoHauteur)]
			#print tailleVideo, type(tailleVideo)
			EkdPrint(u"%s %s" % (tailleVideo, type(tailleVideo)))
		# Si les deux dimensions (largeur et hauteur) sont impaires
		if int(videoLargeur) % 2 == 1 and int(videoHauteur) % 2 == 1:
			videoLargeur = videoLargeur - 1
			videoHauteur = videoHauteur - 1
			tailleVideo = [str(videoLargeur), str(videoHauteur)]
			#print tailleVideo, type(tailleVideo)
			EkdPrint(u"%s %s" % (tailleVideo, type(tailleVideo)))
		# Si les deux dimensions sont paires
		if int(videoLargeur) % 2 == 0 and int(videoHauteur) % 2 == 0:
			videoLargeur = videoLargeur
			videoHauteur = videoHauteur
			tailleVideo = [str(videoLargeur), str(videoHauteur)]
			#print tailleVideo, type(tailleVideo)
			EkdPrint(u"%s %s" % (tailleVideo, type(tailleVideo)))
			
		#print 'self.idCombo', self.idCombo
		EkdPrint(u'self.idCombo %s' % self.idCombo)
		#####################################################################################################

		try:
			ffmpeg = WidgetFFmpeg('conv_en_16_9_ou_4_3', chemin, cheminFichierEnregistrerVideo, self.idCombo, laisserOuvert=ouvert, tailleVideo=tailleVideo)
			ffmpeg.setWindowTitle(_(u"Conversion de vidéos en 16/9 ou 4/3"))
			ffmpeg.exec_()
			#############################################################################################

		except None:
			messageErrAnEnc=QMessageBox(self)
			messageErrAnEnc.setText(_(u"Problème lors de la conversion (FFmpeg)"))
			messageErrAnEnc.setWindowTitle(_(u"Erreur"))
			messageErrAnEnc.setIcon(QMessageBox.Warning)
			messageErrAnEnc.exec_()
			return

		self.lstFichiersSortie = cheminFichierEnregistrerVideo # pour la boite de dialogue de comparaison
		self.radioConvert.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		self.boutCompare.setEnabled(True)
		#########################################
		### Information à l'utilisateur
		self.infoLog(None, chemin, None, cheminFichierEnregistrerVideo)

		return self.lstFichiersSortie # module séquentiel
		###############################################################


	def sequentiel(self, entree, sortie, ouvert=0):
		"""Utile dans le module du même nom. Applique les opérations de la classe. Retourne le vrai nom du fichier de sortie"""
		self.ouvrirSource(entree)
		return self.appliquer(sortie, ouvert)


	def sequentielReglage(self):
		"""Utile dans le module du même nom. Récupère le widget de réglage associé à l'identifiant donné en 1er argument. Retourne l'instance du widget de réglage"""
		return self.groupReglage

	def saveFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurVideoSource.saveFileLocation(self.idSection)

	def loadFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurVideoSource.loadFileLocation(self.idSection)

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
