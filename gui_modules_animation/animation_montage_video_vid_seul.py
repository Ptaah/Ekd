#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, glob
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from gui_modules_common.mencoder_gui import WidgetMEncoder
from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_image.selectWidget import SelectWidget
from gui_modules_music_son.multiplesound import selectJoinMultipleSound
from gui_modules_common.mencoder_concat_gui import WidgetMEncoderConcatExtResol
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############
### Affichage des traces de débug dans la console -> debug = 1 
debug = 1

class Animation_MontagVideoVidSeul(Base):
	""" -----------------------------------------
	# Cadre accueillant les widgets de :
	# Animation >> Montage vidéo >> Vidéo seulement
	# -----------------------------------------"""


	def __init__(self, statusBar):

		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------

		#=== tout sera mis dans une boîte verticale ===#
		vbox=QVBoxLayout()

		#=== Variable de configuration ===#
		self.config=EkdConfig

		# Identifiant de la classe
		self.idSection = "animation_montage_video_seul"

		super(Animation_MontagVideoVidSeul, self).__init__(boite='vbox', titre=_(u"Montage: Vidéo seulement"))

		self.printSection()

		# Création des répertoires temporaires
		self.repTampon = EkdConfig.getTempDir() + os.sep

		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)

		# Au cas où le répertoire existait déjà et qu'il n'était pas vide -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			os.remove(toutRepCompo)

		# Liste de fichiers initiaux (contenu dans le fichier de configuration)
		self.lstFichiersSource = []
		self.lstFichiersSourceProv = [] # idem mais provisoire (sert à récupérer les chemins dans l'ordre de sélection)

		self.statusBar = statusBar

		#-------------------------------------------------------------------
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.mpg", "*.mpeg", "*.mjpeg", "*.flv", "*.mp4", "*.h264", "*.dv", "*.vob"], mode="texte", video = True)

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.

		#####################################################################
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		#--------------------------------------------------------------------
		self.addReglage(boite="vbox")
		#--------------------------------------------------------------------
		#=== Widget qui seront inclus dans la boite de réglage ===#
		self.ordreVideo = selectJoinMultipleSound(0, self)
		self.ordreVideo.setTitleAndTips(_(u"Fichiers vidéos à joindre"), _(u"Liste des fichiers vidéo à joindre. <b>Pour information, vous pouvez monter et descendre les fichiers grâce aux flèches haut et bas (les fichiers apparaissant en haut de la liste sont ceux qui seront au début du montage)</b>"))
		self.layoutReglage.addWidget(self.ordreVideo)

		# ----------------------------
		# Boite de groupe de mplayer
		# ----------------------------
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


	def listeChemins(self, ch):
		"""transforme une chaine de caractères en liste de chemins"""
		lst = ch.split("'")
		for i in lst: # i: élément de la ligne
			if (',' in i) or ('[' in i) or (']' in i):
				lst.remove(i)
		return lst


	def fctRadioSource(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: 
			self.mplayer.listeVideos = self.lstFichiersSource
			try :
				self.radioConvert.setChecked(False)
			except : None


	def fctRadioConvert(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: 
			self.mplayer.listeVideos = self.lstFichiersSortie
			try :
				self.radioSource.setChecked(False)
			except : None


	def ouvrirSource(self, nomEntree=None):
		""" Récupération des chemins vidéo sélectionnée """
		chemin = self.recupSources(nomEntree)
		if not chemin: return
		self.lstFichiersSource = []

		for fichier in chemin:
			self.lstFichiersSource.append(fichier)

		self.lstFichiersSourceProv = self.lstFichiersSource[:] # ':' car sinon on créé un alias

		if len(self.lstFichiersSourceProv)>1:
			self.boutApp.setEnabled(True)
			self.boutApp.setToolTip("")
		else:
			self.boutApp.setEnabled(False)
			self.boutApp.setToolTip(_(u"Veuillez sélectionner au moins 2 vidéos"))

		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = self.lstFichiersSource
		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(False)
		self.radioConvert.setEnabled(False)

		self.statusBar.showMessage(_(u"La vidéo résultante ne pourra pas être lue avec tous les logiciels"))


	def afficherAide(self):
		""" Boîte de dialogue de l'aide """
		
		super(Animation_MontagVideoVidSeul, self).afficherAide(_(u"<p><b>Sous le terme de montage vidéo, vous pouvez ici assembler des vidéos pour en constituer une seule. EKD peut assembler des vidéos de diférentes nature (extensions).</b></p><p><b>Il est à noter ici (pour le Montage vidéo) que vous bénéficiez d'un traitement par lot, c'est à dire que tous les fichiers que vous allez charger seront traités (et pas seulement le fichier sélectionné).</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>Réglages</b>, vous pouvez changer l'ordre de montage des fichiers et ce en remontant ou en redéscendant (par les flèches haut et bas) dans la liste des <b>'Fichiers vidéo à joindre'</b>.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la concaténation) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la concaténation <b>'vidéo convertie'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


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
		EkdPrint(u"Nombre de tailles de vidéos différentes dans le lot: %s" % len(self.lStatDimSeq))
		EkdPrint(u'')

		if len(self.lStatDimSeq)>1:
			return 0
		else:
			return 1
	#########################################################################################

	def stat_codec_video(self):
		"""Calcul detecte si une vidéo a un codec différent dans le lot"""
		from gui_modules_animation.infoVideo import infovideo
		listeCodec = {}
		for video in self.lstFichiersSource:
			info = infovideo(video)
			try:
				listeCodec[info.video_codec] = listeCodec[info.video_codec] + 1
			except KeyError:
				listeCodec[info.video_codec] = 1
		#print "Ensemble des codecs detectés : %s " % listeCodec.keys()
		EkdPrint(u"Ensemble des codecs détectés : %s " % listeCodec.keys())
		self.codecStatVideo = listeCodec
		
	def appliquer(self, nomSortie=None, ouvert=1):
		"""Fusion de vidéos"""

		self.lstFichiersSource = self.ordreVideo.getListFile()
		self.stat_dim_video()
		resolution = self.dimStatVideo

		self.stat_codec_video()
		
		# Chemin du répertoire temporaire
		rep_video_ext_resol = self.repTampon  + 'video_extension_resol' + os.sep

		chemin=unicode(self.ordreVideo.getListFile())

		if not nomSortie:
			suffix = '.avi'
			##############################################################################
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			cheminFichierEnregistrerVideo = saveDialog.getFile()
			###################################################################################################################

		else: # module séquentiel
			cheminFichierEnregistrerVideo=nomSortie

		if not cheminFichierEnregistrerVideo: return

		fichiersSource=self.lstFichiersSource

		if os.path.isdir(rep_video_ext_resol) is False: os.makedirs(rep_video_ext_resol)


		## Dans tous les cas on change le format (mjpeg/avi)
		## # Si la liste contient plus d'un élément, c'est à dire si elle contient des
		## # extensions différentes et si la résolution des vidéos est différente
		###########################################################################################################
		wmcer = WidgetMEncoderConcatExtResol(self.lstFichiersSource, valeurNum=resolution)
		wmcer.setWindowTitle(_(u"Traitement vidéo (extension et résolution)"))
		wmcer.exec_()

		# Les vidéos chargées en vue de la concaténation sont maintenant ds
		# le rep tampon .../video_extension_resol
		self.lstFichiersSource = glob.glob(unicode(rep_video_ext_resol+'*.*'))
		# Mise en ordre (numérotation) car cela peut
		# poser problème au moment de la concaténation
		#print "Debug:: Files to mix : ", self.lstFichiersSource
		EkdPrint(u"Debug:: Files to mix : %s" % self.lstFichiersSource)
		self.lstFichiersSource.sort()

		### Concaténation élégante #########################################################
		cheminVideoProv = self.repTampon + "video" + suffix
		# on écrit dans "output" (descripteur de fichier de cheminVideoProv)

		try:
			output = open(cheminVideoProv, 'wb+')
			for cheminFichier in self.lstFichiersSource:
				input = open(cheminFichier, 'rb')
				output.write(input.read())
				input.close()
			output.close()
		except Exception, details:
			#print "**** DEBUG: Erreur dans l'ouverture du fichier : " , details
			EkdPrint(u"**** DEBUG: Erreur dans l'ouverture du fichier : %s" % details)
		# Maintenant cheminVideoProv contient la concaténation de tous fichiers
		###########################################################################################################

		#=== Commande de concaténation finale ===#
		try:
			mencoder = WidgetMEncoder('fusion_video', cheminVideoProv, cheminFichierEnregistrerVideo, laisserOuvert=ouvert)
			mencoder.setWindowTitle(_(u"Fusion des fichiers vidéos"))
			mencoder.exec_()
		except:

			messageErrAnEnc=QMessageBox(self)
			messageErrAnEnc.setText(_(u"Problème lors de l'étape finale de concaténation vidéo (mencoder)\n"))
			messageErrAnEnc.setWindowTitle(_(u"Erreur"))
			messageErrAnEnc.setIcon(QMessageBox.Warning)
			messageErrAnEnc.exec_()
			os.remove(cheminVideoProv)
			return

		# Suppression du fichier temporaire
		os.remove(cheminVideoProv)

		self.lstFichiersSortie = cheminFichierEnregistrerVideo # pour la boite de dialogue de comparaison
		self.radioConvert.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		### Ajouté le 04/09/2009 pour donner les infos à l'utilisateur sur ce qui a été traité.
		self.infoLog(None, fichiersSource, None, cheminFichierEnregistrerVideo)
		return self.lstFichiersSortie # module séquentiel


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
		files = EkdConfig.get(self.idSection, 'ordreVideo')
		if debug : 
			#print files
			EkdPrint(u"%s" % str(files))
		self.ordreVideo.addSoundAction(files.split(u":"))

	def save(self):
		'''
		Sauvegarde de la configuration de tous les objets
		'''
		self.saveFiles()
		entry = u""
		for files in self.ordreVideo.getListFile() : entry += files+u":"
		EkdConfig.set(self.idSection, u'ordreVideo', entry[:-1])
