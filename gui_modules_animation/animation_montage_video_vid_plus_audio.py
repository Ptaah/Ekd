#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, glob, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base

from gui_modules_common.mencoder_gui import WidgetMEncoder

from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_image.selectWidget import SelectWidget
from moteur_modules_common.moteurJoinAudio import *
from gui_modules_music_son.multiplesound import selectJoinMultipleSound
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

### DEBUG : Pour afficher les messages de debug dans la console, mettre la variable à 1.
debug = 1

# On joue avec l'héritage de Base
class Animation_MontagVideoVidPlusAudio(Base):
	""" --------------------------------------------
	# Cadre accueillant les widgets de :
	# Animation >> Montage vidéo >> Vidéo et Audio
	# -------------------------------------------"""

	def __init__(self, statusBar, parent=None):
		vbox=QVBoxLayout()

		#=== Variable de configuration ===#
		self.config=EkdConfig

		# Identifiant de la classe
		self.idSection = "animation_montage_video_et_audio"

		super(Animation_MontagVideoVidPlusAudio, self).__init__(boite='vbox', titre=_(u"Montage: Vidéo et audio"))
		self.printSection()

		self.repTampon = EkdConfig.getTempDir() + os.sep

		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)

		# Au cas où le répertoire existait déjà et qu'il n'était pas vide -> purge (simple précaution)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			os.remove(toutRepCompo)

		# Liste de fichiers initiaux (contenu dans le fichier de configuration)
		self.lstFichiersSource = []
		self.lstFichiersSourceProv = [] # idem mais provisoire (sert à récupérer les chemins dans l'ordre de sélection)

		self.lstFichiersSourceAudio = []
		self.lstFichiersSourceProvAudio = []

		# Par soucis de lisibilité, on préfère ne pas utiliser des objets présent dans le parent de cette façon
		# mais plutôt le passer en paramètre (le code est plus facile à lire de cette façon)
		self.statusBar = statusBar

		#-------------------------------------------------------------------
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.mpg", "*.mpeg", "*.mjpeg", "*.flv", "*.mp4", "*.h264", "*.dv", "*.vob"], mode="texte", video = True)
		###################################################################################
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		#--------------------------------------------------------------------


		# -------------------------------------------------------------------
		# Boîte de groupe : "Fichiers source"
		# -------------------------------------------------------------------
		extFormat=[]
		for fmt in parent.soxSuppFormat :
			extFormat.append("*."+fmt)

		self.afficheurAudioSource=SelectWidget(extensions=extFormat ,mode="texte", audio = True)
		# Onglets
		self.indexAudioSource = self.add(self.afficheurAudioSource, _(u'Audio(s) source'))
		self.connect(self.afficheurAudioSource,SIGNAL("fileSelected"), self.getFileA)
		self.connect(self.afficheurAudioSource, SIGNAL("pictureChanged(int)"),  self.getFileA)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = ["video","audio"] # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = [self.afficheurVideoSource, self.afficheurAudioSource] # Fait le lien avec le sélecteur de fichier source.


		self.addReglage("vbox")
		#=== Widget qui seront inclus dans la boite de réglage ===#
		self.ordreVideo = selectJoinMultipleSound(0, self)
		self.ordreVideo.setTitleAndTips(_(u"Fichiers vidéos à joindre"), _(u"Liste des fichiers vidéo à joindre. <b>Pour information, vous pouvez monter et descendre les fichiers grâce aux flèches haut et bas (les fichiers apparaissant en haut de la liste sont ceux qui seront au début du montage)</b>"))
		self.ordreAudio = selectJoinMultipleSound(0, self)
		self.ordreAudio.setTitleAndTips(_(u"Fichiers audios à joindre"), _(u"Liste des fichiers audio à joindre. <b>Pour information, vous pouvez monter et descendre les fichiers grâce aux flèches haut et bas (les fichiers apparaissant en haut de la liste sont ceux qui seront au début du montage)</b>")) 

		self.layoutReglage.addWidget(self.ordreVideo)
		self.layoutReglage.addWidget(self.ordreAudio)

		# ---------------------------
		# Boite de groupe de mplayer
		# ---------------------------
		self.addPreview()
		self.addLog()

	def getFile(self):
		'''
		# On utilise la nouvelle interface de récupération des vidéos
		Récupération de la vidéo source selectionnée
		'''
		self.chemin = self.afficheurVideoSource.getFile()
		self.lstFichiersSource = self.afficheurVideoSource.getFiles()
		self.ordreVideo.addSoundAction(self.lstFichiersSource)
		self.ordreVideo.delFile(self.lstFichiersSource)

		self.boutApp.setEnabled(True)

		self.mplayer.setEnabled(True)
		self.mplayer.setVideos([self.chemin])

		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(True)

		self.emit(SIGNAL("loaded"))
		return self.chemin

	def getFileA(self):
		'''
		# On utilise la nouvelle interface de récupération des fichiers audio
		'''
		chemin = self.afficheurAudioSource.getFile()
		self.lstFichiersSourceAudio = self.afficheurAudioSource.getFiles()
		self.ordreAudio.addSoundAction(self.lstFichiersSourceAudio)
		self.ordreAudio.delFile(self.lstFichiersSourceAudio)
		self.boutApp.setEnabled(True)

		self.mplayer.setEnabled(True)
		self.mplayer.setVideos([chemin])

		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(True)

		self.emit(SIGNAL("loaded"))
		return chemin

	def fctRadioSource(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: 
			self.mplayer.listeVideos = self.lstFichiersSource
			try :
				self.radioConvert.setChecked(False)
			except : None

	def fctRadioAudio(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: self.mplayer.listeVideos = self.lstFichiersSourceAudio

	def fctRadioConvert(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: 
			self.mplayer.listeVideos = self.lstFichiersSortie
			try :
				self.radioSource.setChecked(False)
			except : None

	def listeChemins(self, ch):
		"""transforme une chaine de caractères en liste de chemins"""
		lst = ch.split("'")
		for i in lst: # i: élément de la ligne
			if (',' in i) or ('[' in i) or (']' in i):
				lst.remove(i)
		return lst


	def ouvrirSourceAudio(self, nomEntree=None):
		""" Récupération des chemins vidéo sélectionnée """

		chemin = self.recupSourcesAudio(nomEntree)
		if not chemin: return

		self.lstFichiersSourceAudio = chemin

		self.lstFichiersSourceProvAudio = self.lstFichiersSourceAudio[:] # ':' car sinon on créé un alias

		# Ordonner la liste si l'option a été sélectionnée et l'afficher dans la ligne d'édition
		self.ordonnerListeAudio()

		self.boutApp.setEnabled(True)

		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = self.lstFichiersSourceAudio
		self.radioAudio.setChecked(True)
		self.radioConvert.setEnabled(False)

		if len(self.lstFichiersSource)!=0:
			self.radioSource.setEnabled(True)
			self.radioAudio.setEnabled(True)
		else:
			self.radioSource.setEnabled(False)
			self.radioAudio.setEnabled(False)

		self.statusBar.showMessage(_(u"La vidéo résultante ne pourra pas être lue avec tous les logiciels"))


	def ouvrirSourceVideo(self, nomEntree=None):
		""" Récupération des chemins vidéo sélectionnée """
		chemin = self.recupSources(nomEntree)

		if not chemin: return

		self.lstFichiersSource = chemin

		self.lstFichiersSourceProv = self.lstFichiersSource[:] # ':' car sinon on créé un alias

		# Ordonner la liste si l'option a été sélectionnée et l'afficher dans la ligne d'édition
		self.ordonnerListeVideo()

		self.boutApp.setEnabled(True)

		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = self.lstFichiersSource
		self.radioSource.setChecked(True)
		self.radioConvert.setEnabled(False)

		if len(self.lstFichiersSourceAudio)!=0:
			self.radioSource.setEnabled(True)
			self.radioAudio.setEnabled(True)
		else:
			self.radioSource.setEnabled(False)
			self.radioAudio.setEnabled(False)

		self.statusBar.showMessage(_(u"La vidéo résultante ne pourra pas être lue avec tous les logiciels"))


	def afficherAide(self):
		""" Boîte de dialogue de l'aide """

		super(Animation_MontagVideoVidPlusAudio, self).afficherAide(_(u"<p><b>Sous le terme de montage vidéo, vous pouvez ici assembler des vidéos pour en constituer une seule, mais aussi des fichiers audio. EKD peut assembler des vidéos (mais aussi des fichiers audio) de différentes nature (extensions).</b></p><p><b>Il est à noter ici (pour le Montage vidéo) que vous bénéficiez d'un traitement par lot, c'est à dire que tous les fichiers que vous allez charger seront traités (et pas seulement le fichier sélectionné).</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Passez maintenant dans l'onglet <b>'Audio(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher votre/vos fichier(s) audio. Si vous voulez sélectionner plusieurs fichiers audio d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos fichiers), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner un fichier audio dans la liste et l'écouter (par le bouton juste à la droite de cette liste). De même si vous le désirez, vous pouvez obtenir des informations complètes sur le fichier audio sélectionné, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>Réglages</b>, vous pouvez changer l'ordre de montage des fichiers et ce en remontant ou en redescendant (par les flèches haut et bas) dans les listes <b>'Fichiers vidéo à joindre'</b> et <b>'Fichiers audio à joindre'</b>.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la concaténation) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la concaténation <b>'vidéo convertie'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos et fichiers audio chargés (avec leurs chemins exacts) avant et après conversion.</p>"))


	def stat_dim_video(self):
		"""Calcul statistique des dimensions des vidéos les plus présentes dans le lot"""

		from gui_modules_animation.infoVideo import infovideo

		listePrepaRedim = []

		# Détection des dimensions différentes (résolutions)
		# dans les vidéos chargées par l'utilisateur
		for parcVideoResolution in self.lstFichiersSource:
			info = infovideo(parcVideoResolution)
			listePrepaRedim.append((info.videoLargeur, info.videoHauteur))

		# Merci beaucoup à Marc Keller de la liste: python at aful.org de m'avoir
		# aidé pour cette partie (les 4 lignes en dessous)
		dictSeq={}.fromkeys(listePrepaRedim, 0)
		for cle in listePrepaRedim: dictSeq[cle]+=1
		self.lStatDimSeq=sorted(zip(dictSeq.itervalues(), dictSeq.iterkeys()), reverse=1)
		#print self.lStatDimSeq[0][1]
		EkdPrint(u"%s" % str(self.lStatDimSeq[0][1]))
		self.dimStatVideo=self.lStatDimSeq[0][1]

		'''
		print
		print "Toutes les dimensions des vidéos (avec le nbre de vidéos):", self.lStatDimSeq
		print 'Dimension des vidéos la plus presente dans la sequence:', self.dimStatVideo
		print "Nombre de tailles de vidéos différentes dans le lot :", len(self.lStatDimSeq)
		print
		'''
		EkdPrint(u'')
		EkdPrint(u"Toutes les dimensions des vidéos (avec le nbre de vidéos): %s" % self.lStatDimSeq)
		EkdPrint(u'Dimension des vidéos la plus presente dans la sequence: %s' % str(self.dimStatVideo))
		EkdPrint(u"Nombre de tailles de vidéos différentes dans le lot: %s" % str(len(self.lStatDimSeq)))
		EkdPrint(u'')

		if len(self.lStatDimSeq)>1:
			return 0
		else:
			return 1
	#########################################################################################

	def recupOrdreAV(self) :
		self.lstFichiersSource = self.ordreVideo.getListFile()
		self.lstFichiersSourceAudio = self.ordreAudio.getListFile()

	def appliquer(self, nomSortie=None, ouvert=1):
		"""Fusion de vidéos"""

		self.recupOrdreAV()
		# ----- Vidéo ------ #
		self.stat_dim_video()
		resolution = self.dimStatVideo

		# Chemin du répertoire temporaire
		rep_video_ext_resol = self.repTampon  + 'video_extension_resol' + os.sep

		# Scan des extensions des vidéos chargées pour concaténation des vidéos
		lVideoExt = [parcVidExt.split('.') for parcVidExt in self.lstFichiersSource]
		lExtVideo = [parcExtVideo[1].lower() for parcExtVideo in lVideoExt]

		# On elimine les doublons s'il y en a. TTes les
		# extensions différentes sont mises en avant
		uniqExtVideo = list(set(lExtVideo))

		# ----- Audio ------ #
		# Chemin du répertoire temporaire
		rep_video_audio = self.repTampon  + 'concat_audio' + os.sep

		# Scan des extensions des fichiers audio chargés pour concaténation
		lAudioExt = [parcAudExt.split('.') for parcAudExt in self.lstFichiersSourceAudio]
		lExtAudio = [parcExtAudio[1].lower() for parcExtAudio in lAudioExt]

		# On elimine les doublons s'il y en a. TTes les
		# extensions différentes sont mises en avant
		uniqExtAudio = list(set(lExtAudio))

		#######################################################################

		#=== Récupération du fichier de sortie ===#
		chemin=unicode(self.ordreVideo.getListFile())

		if not nomSortie:
			# suffix du fichier actif
			#suffix=os.path.splitext(chemin)[1]
			suffix = u".avi"

			##############################################################################
			# Si la liste contient plus d'un élément, c'est à dire si elle contient des
			# extensions différentes et si la résolution des vidéos est différente.
			# ----------------------------------------------------------------------------
			# Ici l'extension à la sortie sera en avi car on encode en Motion JPEG.
			if len(uniqExtVideo) > 1 or len(self.lStatDimSeq) > 1: suffix = '.avi'
			##############################################################################
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			self.cheminFichierEnregistrerVideo = saveDialog.getFile()
			####################################################################################################################

		else: # module séquentiel
			self.cheminFichierEnregistrerVideo=nomSortie

		if not self.cheminFichierEnregistrerVideo: return

		# Video
		# Chemin de sortie temporaire de la vidéo
		self.cheminVideoProv = self.repTampon+u"video"

		# Audio
		# Chemin de sortie temporaire de l'audio
		self.cheminAudioProv = self.repTampon+u"audio.wav"

		if os.path.isdir(rep_video_ext_resol) is False: os.makedirs(rep_video_ext_resol)

		#from moteur_modules_animation.mencoder_concat_video import WidgetMEncoderConcatExtResol
		from gui_modules_common.mencoder_concat_gui import WidgetMEncoderConcatExtResol

		self.sourceVideo = self.lstFichiersSource
		# Si la liste contient plus d'un élément, c'est à dire si elle contient des
		# extensions différentes et si la résolution des vidéos est différente
		if len(uniqExtVideo) > 1 or len(self.lStatDimSeq) > 1:
			wmcer = WidgetMEncoderConcatExtResol(self.lstFichiersSource, valeurNum=resolution)
			wmcer.setWindowTitle(_(u"Traitement vidéo (extension et résolution)"))
			wmcer.exec_()

			# Les vidéos chargées en vue de la concaténation sont maintenant ds
			# le rep tampon .../video_extension_resol
			self.lstFichiersSource = glob.glob(unicode(rep_video_ext_resol+'*.*'))
			if debug : 
				#print self.lstFichiersSource
				EkdPrint(u"%s" % self.lstFichiersSource)
			# Mise en ordre (numérotation) car cela peut
			# poser problème au moment de la concaténation
			self.lstFichiersSource.sort()
			if debug : 
				#print "sources tmp mise en ordre : ", self.lstFichiersSource
				EkdPrint(u"sources tmp mise en ordre : %s" % self.lstFichiersSource)
			# Comme l'encodage se fait ici en Motion JPEG
			# (AVI) l'extension doit être .avi
			suffix = '.avi'

		else:
			# Au cas où le répertoire existait déjà et qu'il n'était pas vide -> purge
			# ... ici dans le cas de vidéos avec la même extension et la même résolution
			if os.path.isdir(rep_video_ext_resol) is True:
				for toutRepCompoVideo in glob.glob(rep_video_ext_resol+'*.*'):
					os.remove(toutRepCompoVideo)
		##################################################################################################

		self.sourceAudio = self.lstFichiersSourceAudio
		self.process = soxProcessMulti(self.lstFichiersSourceAudio, self.cheminAudioProv, u"")
		self.process.show()
		self.process.run()
		self.connect(self.process,SIGNAL("endProcess"),self.endProcess)

	def endProcess(self, sortie) :
		# Suite du process

		self.process.close()
			# Les fichiers audio chargés en vue de la concaténation
			# sont maintenant ds le rep tampon .../concat_audio
		
		###################################################################################################
		### Concaténation élégante (à transformer en objet dans le package moteur) ###############
		# on écrit dans "output" (descripteur de fichier de cheminVideoProv)
		try:
			output = open(self.cheminVideoProv, 'wb+')
			for cheminFichier in self.lstFichiersSource:
				input = open(cheminFichier, 'rb')
				output.write(input.read())
				input.close()
			output.close()
		except Exception, details:
			#print "**** DEBUG: Erreur dans l'ouverture du fichier : " , details
			EkdPrint(u"**** DEBUG: Erreur dans l'ouverture du fichier : %s" % details)
		# Maintenant cheminVideoProv contient la concaténation de tous fichiers
		###################################################################################################

		#=== Commandes de concaténation finale ===#
		if debug : 
			#print self.cheminVideoProv, self.cheminAudioProv, self.cheminFichierEnregistrerVideo
			EkdPrint(u"%s %s %s" % (self.cheminVideoProv, self.cheminAudioProv, self.cheminFichierEnregistrerVideo))
		
		try:
			mencoder = WidgetMEncoder('fusion_audio_et_video_2', (self.cheminVideoProv, self.cheminAudioProv), self.cheminFichierEnregistrerVideo, laisserOuvert=1)
			mencoder.setWindowTitle(_(u"Fusion des fichiers vidéos et audios"))
			mencoder.exec_()
		except:
			messageErrAnEnc=QMessageBox(self)
			messageErrAnEnc.setText(_(u"Problème lors de l'étape de concaténation vidéo et audio (mencoder)"))
			messageErrAnEnc.setWindowTitle(_(u"Erreur"))
			messageErrAnEnc.setIcon(QMessageBox.Warning)
			messageErrAnEnc.exec_()
			os.remove(self.cheminVideoProv)
			os.remove(self.cheminAudioProv)
			return

		# Suppression des fichiers temporaires
		os.remove(self.cheminVideoProv)
		os.remove(self.cheminAudioProv)

		self.lstFichiersSortie = self.cheminFichierEnregistrerVideo # pour la boite de dialogue de comparaison
		self.radioConvert.setEnabled(True)
		self.radioConvert.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		#self.radioAudio.setEnabled(True)
		self.infoLog(None, self.sourceVideo, self.sourceAudio, self.lstFichiersSortie)
		return self.lstFichiersSortie # module séquentiel


	def sequentiel(self, entree, sortie, ouvert=0):
		"""Utile dans le module du même nom. Applique les opérations de la classe. Retourne le vrai nom du fichier de sortie"""
		self.ouvrirSourceVideo(entree[0])
		self.ouvrirSourceAudio(entree[1])
		return self.appliquer(sortie, ouvert)


	def sequentielReglage(self):
		"""Utile dans le module du même nom. Récupère le widget de réglage associé à l'identifiant donné en 1er argument. Retourne l'instance du widget de réglage"""
		return self.groupReglage

	def saveFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurVideoSource.saveFileLocation(self.idSection, u'sourcesVideo')
		self.afficheurAudioSource.saveFileLocation(self.idSection, u'sourcesAudio')

	def loadFiles(self):
		'''
		# On sauvegarde la liste des fichiers chargés
		'''
		self.afficheurVideoSource.loadFileLocation(self.idSection, u'sourcesVideo')
		self.afficheurAudioSource.loadFileLocation(self.idSection, u'sourcesAudio')

	def load(self):
		'''
		Chargement de la configuration de tous les objets
		'''
		self.loadFiles()
		files = EkdConfig.get(self.idSection, 'ordreVideo')
		if debug : 
			#print files
			EkdPrint(u"%s" % str(files))
		self.ordreVideo.addSoundAction(files.split(u":"))
		files = EkdConfig.get(self.idSection, 'ordreAudio')
		if debug : 
			#print files
			EkdPrint(u"%s" % str(files))
		self.ordreAudio.addSoundAction(files.split(u":"))
		

	def save(self):
		'''
		Sauvegarde de la configuration de tous les objets
		'''
		self.saveFiles()
		entry = u""
		for files in self.ordreVideo.getListFile() : entry += files+u":"
		EkdConfig.set(self.idSection, u'ordreVideo', entry[:-1])
		entry = u""
		for files in self.ordreAudio.getListFile() : entry += files+u":"
		EkdConfig.set(self.idSection, u'ordreAudio', entry[:-1])

