#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from gui_modules_common.mencoder_gui import WidgetMEncoder
from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

class Animation_SeparVideoEtAudio(Base):
	# ----------------------------------------------------------------------------------------
	# Cadre accueillant les widgets de : Animation >> Séparer le flux vidéo et le flux audio
	# ----------------------------------------------------------------------------------------

	def __init__(self):
		vbox=QVBoxLayout()

		#=== Variable de configuration ===#
		self.config=EkdConfig

		#=== Identifiant de la classe ===#
		self.idSection = "animation_separer_audio_et_video"
		super(Animation_SeparVideoEtAudio, self).__init__('vbox', titre=_(u"Séparation audio/vidéo")) # module de animation
		self.printSection()

		## On utilise le selecteur d'image pour les vidéos
		from gui_modules_image.selectWidget import SelectWidget
		# Là où on naviguera entre les fichiers
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.mpg", "*.mpeg", "*.mjpeg", "*.flv", "*.mp4", "*.dv", "*.vob"], mode="texte", video = True)
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		## -------------------------------------------------------------------

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = ["video","audio"] # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.

		# -------------------------------------------------------------------
		# Boîte de groupe "Réglage de sortie de l'encodage"
		# -------------------------------------------------------------------
		groupBox = QGroupBox("")
		self.layoutReglage = QHBoxLayout(groupBox)
		#=== Widget qui seront inclus dans la boite de réglage ===#
		# boite de combo
		self.combo=QComboBox() # le self sert à afficher des informations sur les items à partir de la fonction
		# listeCombo=[(texte, clé QVariant)...]
		self.listeCombo=[        (_(u'Vidéo et audio') ,'video&audio'),\
					 (_(u'Vidéo seulement') ,'video'),\
					 (_(u'Audio seulement') , 'audio'),]

		# Insertion des codecs de compression dans la combo box
		for i in self.listeCombo:
                	self.combo.addItem(i[0],QVariant(i[1]))

		self.connect(self.combo, SIGNAL("activated(int)"), self.sauverTypeExtraction)

		self.layoutReglage.addWidget(self.combo, 0, Qt.AlignHCenter)

		# On tient-compte du paramètre de configuration
		try:
			typ = self.config.get(self.idSection,'type_extraction')
			indice = 0 # indice de la ligne de self.listeCombo correspondant au type d'ordre
			for i in listeCombo:
				if i[1]!=typ:
					indice += 1
				else:
					break
			self.combo.setCurrentIndex(indice)
		except:
			self.combo.setCurrentIndex(0)

		self.add(groupBox, _(u"Réglages"))
		self.addPreview(nomPreview = u"Visualiser / écouter - Vidéo / Audio", light = False, mode = "Video+Audio")
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

		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(True)
		self.boutApp.setEnabled(True)
		if self.idSection == "animation_filtresvideo":
			self.boutApercu.setEnabled(True)
			self.filtreDecouper.setButtonEnabled(True)
		self.emit(SIGNAL("loaded"))
		return self.chemin


	def sauverTypeExtraction(self,i):
		""" Sauvegarde du mode d'extraction """
		idCombo= str(self.combo.itemData(i).toStringList()[0])
		self.config.set(self.idSection,'type_extraction',idCombo)


	def afficherAide(self):
		""" Boîte de dialogue de l'aide """
		super(Animation_SeparVideoEtAudio,self).afficherAide(_(u"<p><b>Ici vous pouvez séparer le canal vidéo et le canal audio dans une vidéo (bien entendu une vidéo qui contient du son).</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> sélectionnez le mode d'extraction (<b>'Vidéo et audio'</b>, <b>'Vidéo seulement'</b> ou <b>'Audio seulement'</b>).</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Dans l'onglet <b>'Visualiser / écouter - Vidéo / Audio'</b>, dans le cas d'une extaction <b>'Vidéo et audio'</b> vous pouvez à la fois visionner la vidéo d'un côté et écouter l'audio de l'autre, dans le cas d'une extraction de la <b>'Vidéo seulement'</b>, vous pouvez lire la vidéo résultante (le bouton de lecture audio reste grisé), et dans le dernier cas résultat de l'extraction de l'<b>'Audio seulement'</b>, vous pourrez écouter la piste audio extraite (dans ce cas la zone de lecture vidéo est cette fois-ci grisée). Dans les deux cas (extraction vidéo et audio, et vidéo seulement) le visionnement de la vidéo d'origine se fait en sélectionnant <b>'vidéo(s) source(s)'</b>, et <b>'vidéo convertie'</b> pour la vidéo résultante de l'extraction. Vous pouvez lire les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b></p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


	def ouvrirSource(self, nomEntree=None):
		"""Récupération du chemin de la vidéo sélectionnée et activation de certains widgets"""

		# Récupération du chemin de la vidéo
		chemin = self.recupSource(nomEntree)

		if not chemin: return
		# Affichage du chemin + nom de fichier dans la ligne d'édition
		self.ligneEditionSource.setText(chemin)

		self.mplayer.listeVideos = [chemin]
		self.mplayer.setEnabled(True)
		self.boutApp.setEnabled(True)


	def extraireVideo(self, cheminVideoEntre, SortieVideoSFA, laisserOuvert=1):
		"""extraction de la vidéo du fichier"""

		try:
			mencoder = WidgetMEncoder("extractionvideo", cheminVideoEntre, SortieVideoSFA, laisserOuvert=laisserOuvert)
			mencoder.setWindowTitle(_(u"Extraction vidéo"))
			mencoder.exec_()
		except:
			messageErrAnEnc=QMessageBox(self)
			messageErrAnEnc.setText(_(u"Problème d'extraction vidéo (mencoder)"))
			messageErrAnEnc.setWindowTitle(_(u"Error"))
			messageErrAnEnc.setIcon(QMessageBox.Warning)
			messageErrAnEnc.exec_()
			return


	def extraireAudio(self, cheminVideoEntre, SortieAudioSFA, laisserOuvert=1):
		"""extraction de l'audio du fichier"""

		ffmpeg = WidgetFFmpeg("extractionaudio", cheminVideoEntre, SortieAudioSFA, laisserOuvert=laisserOuvert)
		ffmpeg.setWindowTitle(_(u"Extraction audio"))
		ffmpeg.exec_()

	def appliquer(self, nomSortie=None, ouvert=1):
		""" appelle la boite de dialogue de sélection de fichier à sauver et appel de la fonction de séparation audio-vidéo """

		# quel est l'index du dernier item sélectionné de la boîte de combo?
		index=self.combo.currentIndex()

		## On utilise la nouvelle interface de récupération des vidéos
		# Récupération du chemin source
		chemin = self.getFile()

		if not nomSortie:
			# suffix du fichier actif
			if self.combo.currentIndex() == 2 : suffix = ".wav"
			else : suffix=os.path.splitext(chemin)[1]
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			cheminFichierEnregistrerVideo = saveDialog.getFile()

		else: # module séquentiel
			cheminFichierEnregistrerVideo = nomSortie

		if not cheminFichierEnregistrerVideo: return
		###########################################################################################################################


		# chemins complets de sortie vidéo et audio
		SortieVideoSFA = cheminFichierEnregistrerVideo
		# Vérification de l'extension du nom de fichier indiqué.
		if cheminFichierEnregistrerVideo.endswith(".wav") : SortieAudioSFA = cheminFichierEnregistrerVideo
		else : SortieAudioSFA = cheminFichierEnregistrerVideo + ".wav"
		##########################################################################################################################

		#=== Separation du fichier video ===#
		idCombo = self.listeCombo[index][1]
		#print "Combo :", idCombo
		EkdPrint(u"Combo : %s" % idCombo)

		# extraction
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		self.boutCompare.setEnabled(True)

		# extraction audio et vidéo
		if idCombo == 'video&audio':
			# le 3ème argument sert à fermer automatiquement la fenêtre d'encodage
			#print "Extraction Vidéo"
			EkdPrint(u"Extraction Vidéo")
			self.extraireVideo(chemin, SortieVideoSFA, 0)
			#print "Extraction Audio"
			EkdPrint(u"Extraction Audio")
			self.extraireAudio(chemin, SortieAudioSFA, ouvert)
			self.lstFichiersSortie = [SortieVideoSFA]
			self.mplayerA.setEnabled(True)
			self.mplayerA.setVideos([SortieAudioSFA])
			self.infoLog(None, chemin, None, [SortieVideoSFA,SortieAudioSFA])
			self.radioConvert.setChecked(True)

		# extraction vidéo
		elif idCombo == 'video':
			self.extraireVideo(chemin, SortieVideoSFA, ouvert)
			self.lstFichiersSortie = [SortieVideoSFA]
			self.mplayerA.setEnabled(False)
			self.infoLog(None, chemin, None, SortieVideoSFA)
			self.radioConvert.setChecked(True)

		# extraction audio
		elif idCombo == 'audio':
			self.extraireAudio(chemin, SortieAudioSFA, ouvert)
			self.lstFichiersSortie = None
			self.mplayerA.setEnabled(True)
			self.mplayerA.setVideos([SortieAudioSFA])
			self.infoLog(None, chemin, None, [SortieVideoSFA,SortieAudioSFA])
			self.infoLog(None, chemin, None, SortieAudioSFA)
			self.radioSource.setChecked(True)
			self.radioConvert.setEnabled(False)
			self.boutCompare.setEnabled(False)

		return SortieVideoSFA


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
