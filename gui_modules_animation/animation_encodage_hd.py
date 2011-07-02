#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, glob, shutil
from PyQt4.QtGui import QMessageBox
from gui_modules_animation.animation_base_encodageFiltre import Base_EncodageFiltre
### Création des objets: WidgetFFmpeg2theora et WidgetFFmpeg ... l'objet WidgetMEncoder a
### été changé en conséquence #############################################################
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_common.EkdWidgets import EkdSaveDialog
###########################################################################################
from moteur_modules_animation.mplayer import getParamVideo
from moteur_modules_common.EkdConfig import EkdConfig
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

class AnimationEncodageHD(Base_EncodageFiltre):
	"""Cadre de Animation -> Encodage -> Haute Définition. But: encodages spécifiques haute définition (pour entre autre import des vidéos générées dans Cinelerra)"""

	def __init__(self):

		# Identifiant de la classe
		self.idSection = "animation_encodage_hd"

		# Pas d'"empilement" car pas de paramètre d'encodage
		self.stacked = None
		
		# ------------------------------------------------------------------- #
		# Chemin des répertoires temporaires pour la gestion des fichiers
		# mod (extension .mod). Ce sont (apparemment) des fichiers mpeg avec
		# une extension .mod. Les fichiers en question ont juste besoin
		# d'être renommés avec une extension .mpg avant le traitement.
		# ------------------------------------------------------------------- #
		self.repTempEntree = EkdConfig.getTempDir() + os.sep
		# création des répertoires temporaires
		if os.path.isdir(self.repTempEntree) is False: os.makedirs(self.repTempEntree)	
        	# Chemin exact d'écriture pour le tampon des fichiers mod
        	self.repTempFichiersMod = self.repTempEntree+'transcodage'+os.sep+'fichiers_mod'+os.sep
		# Création du chemin
		if os.path.isdir(self.repTempFichiersMod) is False: os.makedirs(self.repTempFichiersMod)
		# Epuration/elimination des fichiers tampon contenus dans le rep tampon
		for toutRepTemp in glob.glob(self.repTempFichiersMod+'*.*'): os.remove(toutRepTemp)

		#----------------------------------------------------------------------------------
		# Paramètres de la liste de combo: [(identifiant, nom entrée, instance, extension), ...]
		#----------------------------------------------------------------------------------

		### Ajouté le 19/08/10 (Rajout des codecs DNxHD) ####################################
		self.listeCombo = [
			('hd_1920x1080_mov__pcm_s16be__16/9', _(u'HD1080 16/9 (mpeg4 - pcm s16be) 1920x1080 (.mov)'), 0, '.mov'),
			('hd_1280x720_mov__pcm_s16be__16/9', _(u'HD720 16/9 (mpeg4 - pcm s16be) 1280x720 (.mov)'), 1, '.mov'),
			('hd_1440x1080_mov__pcm_s16be__4/3', _(u'HD1080 4/3 (mpeg4 - pcm s16be) 1440x1080 (.mov)'), 2, '.mov'),
			('hd_dnxhd_1920x1080_29.97_220_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:29.97 Bitrate:220 Mb/s (.mov)"), 3, '.mov'), ('hd_dnxhd_1920x1080_29.97_145_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:29.97 Bitrate:145 Mb/s (.mov)"), 4, '.mov'), ('hd_dnxhd_1920x1080_25_185_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:25 Bitrate:185 Mb/s (.mov)"), 5, '.mov'), ('hd_dnxhd_1920x1080_25_120_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:25 Bitrate:120 Mb/s (.mov)"), 6, '.mov'), ('hd_dnxhd_1920x1080_25_36_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:25 Bitrate:36 Mb/s (.mov)"), 7, '.mov'), ('hd_dnxhd_1920x1080_24_175_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:24 Bitrate:175 Mb/s (.mov)"), 8, '.mov'), ('hd_dnxhd_1920x1080_24_115_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:24 Bitrate:115 Mb/s (.mov)"), 9, '.mov'), ('hd_dnxhd_1920x1080_24_36_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:24 Bitrate:36 Mb/s (.mov)"), 10, '.mov'), ('hd_dnxhd_1920x1080_23.976_175_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:23.976 Bitrate:175 Mb/s (.mov)"), 11, '.mov'), ('hd_dnxhd_1920x1080_23.976_115_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:23.976 Bitrate:115 Mb/s (.mov)"), 12, '.mov'), ('hd_dnxhd_1920x1080_23.976_36_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:23.976 Bitrate:36 Mb/s (.mov)"), 13, '.mov'), ('hd_dnxhd_1920x1080_29.97_220_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:29.97 Bitrate:220 Mb/s (.mov)"), 14, '.mov'), ('hd_dnxhd_1920x1080_29.97_145_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:29.97 Bitrate:145 Mb/s (.mov)"), 15, '.mov'), ('hd_dnxhd_1920x1080_29.97_45_mbs', _(u"Codec Avid DNxHD Dimension:1920x1080 Img/sec:29.97 Bitrate:45 Mb/s (.mov)"), 16, '.mov'), ('hd_dnxhd_1280x720_59.94_220_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:59.94 Bitrate:220 Mb/s (.mov)"), 17, '.mov'), ('hd_dnxhd_1280x720_59.94_145_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:59.94 Bitrate:145 Mb/s (.mov)"), 18, '.mov'), ('hd_dnxhd_1280x720_50_175_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:50 Bitrate:175 Mb/s (.mov)"), 19, '.mov'), ('hd_dnxhd_1280x720_50_115_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:50 Bitrate:115 Mb/s (.mov)"), 20, '.mov'), ('hd_dnxhd_1280x720_29.97_110_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:29.97 Bitrate:110 Mb/s (.mov)"), 21, '.mov'), ('hd_dnxhd_1280x720_29.97_75_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:29.97 Bitrate:75 Mb/s (.mov)"), 22, '.mov'), ('hd_dnxhd_1280x720_25_90_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:25 Bitrate:90 Mb/s (.mov)"), 23, '.mov'), ('hd_dnxhd_1280x720_25_60_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:25 Bitrate:60 Mb/s (.mov)"), 24, '.mov'), ('hd_dnxhd_1280x720_23.976_90_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:23.976 Bitrate:90 Mb/s (.mov)"), 25, '.mov'), ('hd_dnxhd_1280x720_23.976_60_mbs', _(u"Codec Avid DNxHD Dimension:1280x720 Img/sec:23.976 Bitrate:60 Mb/s (.mov)"), 26, '.mov'),]
		#####################################################################################

		#---------------------------
		# Dérivation de la classe
		#---------------------------
		Base_EncodageFiltre.__init__(self, titre=_(u"Transcodage: Haute Définition"))


	def appliquer(self, nomSortie=None, ouvert=1):
		"Appel du moteur du cadre"

		# quel est l'index du dernier item sélectionné de la boîte de combo?
		index=self.combo.currentIndex()
		if not nomSortie:

			## On utilise la nouvelle interface de récupération des vidéos
			# Récupération du chemin source
			chemin=unicode(self.getFile())

			# suffix du codec actif
			suffix=self.listeCombo[index][3]
			if suffix=='':
				suffix=os.path.splitext(chemin)[1]
				
			ext_chargee = os.path.splitext(chemin)[1]
			codec_reglage = self.listeCombo[index][1]
			
			# ------------------------------------------------------------------- #
			# Gestion des fichiers mod (extension .mod). Ce sont (apparemment)
			# des fichiers mpeg avec une extension .mod. Les fichiers en question 
			# ont juste besoin d'être renommés avec une extension .mpg avant le 
			# traitement.
			# ------------------------------------------------------------------- #
			nom_fich_sans_ext = os.path.splitext(os.path.basename(chemin))[0]
			if ext_chargee in ['.mod', '.MOD']:
				# Copie du fichier concerné dans le rep tampon et renommage avec ext .mpg
				shutil.copy(chemin, self.repTempFichiersMod+nom_fich_sans_ext + '.mpg')
				chemin = unicode(self.repTempFichiersMod + nom_fich_sans_ext + '.mpg')
				
			# suffix du codec actif
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			cheminFichierEnregistrerVideo = saveDialog.getFile()

		else: # module séquentiel
			cheminFichierEnregistrerVideo = nomSortie

		if not cheminFichierEnregistrerVideo:
			return

		# quel est l'index du dernier item sélectionné de la boîte de combo?
		#i = self.combo.currentIndex()
		#print 'index', index
		EkdPrint('index ' + str(index))
		# identifiant du codec actif
		idCodec = self.listeCombo[index][0]
		#print 'idCodec', idCodec
		EkdPrint('idCodec ' + idCodec)

		### Ajouté le 19/08/10 (Collecte des infos codec vidéo) #############################
		infosCodecVideo = {'Fichier':chemin}
		getParamVideo(chemin, ['ID_VIDEO_CODEC'], infosCodecVideo)
		videoCodec = infosCodecVideo['ID_VIDEO_CODEC']
		#####################################################################################

		### Ajouté le 27/08/10 (Collecte des infos sur le framerate de la vidéo) ############
		infosImgSec = {'Fichier':chemin}
		getParamVideo(chemin, ['ID_VIDEO_FPS'], infosImgSec)
		imgSec = infosImgSec['ID_VIDEO_FPS']
		#####################################################################################

		### Ajouté le 27/08/10 (Collecte des infos codec audio) #############################
		infosCodecAudio = {'Fichier':chemin}
		getParamVideo(chemin, ['ID_AUDIO_CODEC'], infosCodecAudio)
		audioCodec = infosCodecAudio['ID_AUDIO_CODEC']
		#####################################################################################

		# Si on sélectionne une des 3 entrées classiques pour la HD
		if index < 3:
			######## Gestion de l'extension .h264 ####
			# Si on charge une vidéo avec extension .h264, FFmpeg ne peut 
			# pas effectuer l'encodage
			if ext_chargee == '.h264':
				messErrExtH264ffmpeg=QMessageBox(self)
				messErrExtH264ffmpeg.setText(_(u"<p>Il n'est pas possible de donner suite au traitement <b>à partir d'une vidéo avec extension h264 et en ayant choisi: %s.</b></p><p><b>Veuillez choisir une autre vidéo (sans extension h264).</b></p>" % codec_reglage))
				messErrExtH264ffmpeg.setWindowTitle(_(u"Erreur"))
				messErrExtH264ffmpeg.setIcon(QMessageBox.Warning)
				messErrExtH264ffmpeg.exec_()
				return
			else:
				hd_simple = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, laisserOuvert=ouvert)
				hd_simple.setWindowTitle(_(u"Encodage vidéo - Haute Définition - Simple"))
				hd_simple.exec_()

		### Ajouté le 19/08/10 (Gestion du codec Avid DNxHD) ################################
		# Si on sélectionne une des entrées concernant l'Avid DNxHD.
		if 3 <= index <= 26:
			# Si on charge une vidéo avec extension .mov, FFmpeg ne peut 
			# pas effectuer l'encodage (uniquement pour le DNxHD)
			if ext_chargee == '.mov':
				messErrChargVidMov=QMessageBox(self)
				messErrChargVidMov.setText(_(u"<p>Il n'est pas possible de donner suite au traitement <b>à partir d'une vidéo avec extension mov et ce pour un transcodage Avid DNxHD.</b></p><p><b>Veuillez choisir une autre vidéo (sans extension mov).</b></p>"))
				messErrChargVidMov.setWindowTitle(_(u"Erreur"))
				messErrChargVidMov.setIcon(QMessageBox.Warning)
				messErrChargVidMov.exec_()
				return
			# Si l'utilisateur charge une vidéo avec le codec ffhuffyuv (c'est à
			# dire une vidéo HFYU) le traitement DNxHD ne pourra pas avoir lieu.
			if ext_chargee == '.avi' and videoCodec == 'ffhuffyuv':
				messErrCodecHFYU=QMessageBox(self)
				messErrCodecHFYU.setText(_(u"<p>Il n'est pas possible de donner suite au traitement <b>à partir d'une vidéo dont le codec est: %s.</b></p><p><b>Veuillez choisir une vidéo avec un codec différent.</b></p>" % videoCodec))
				messErrCodecHFYU.setWindowTitle(_(u"Erreur"))
				messErrCodecHFYU.setIcon(QMessageBox.Warning)
				messErrCodecHFYU.exec_()
				return
			### Le 27/08/10 ############
			# Si l'utilisateur charge une vidéo avec un codec audio mp3
			# le traitement DNxHD ne pourra pas avoir lieu.
			if audioCodec == 'mp3':
				messErrCodecAudMp3=QMessageBox(self)
				messErrCodecAudMp3.setText(_(u"<p>Il n'est pas possible de donner suite au traitement <b>à partir d'une vidéo dont le codec audio est: %s.</b></p><p><b>Veuillez choisir une vidéo avec un codec audio différent.</b></p>" % audioCodec))
				messErrCodecAudMp3.setWindowTitle(_(u"Erreur"))
				messErrCodecAudMp3.setIcon(QMessageBox.Warning)
				messErrCodecAudMp3.exec_()
				return
			### Le 27/08/10 ############
			# Si l'utilisateur charge une vidéo dont le nombre d'images par seconde est différent
			# de celui présent dans le preset choisi dans la liste déroulante ...
			if float(imgSec) != float(idCodec.split("_")[3]):
				reply = QMessageBox.warning(self, 'Message',
				_(u"Il apparaît que la vidéo source a un nombre d'images par seconde (%s) différent de celui du preset que vous avez choisi dans la liste déroulante. La conséquence sera certainement un décalage plus ou moins important entre la piste vidéo et la piste audio, à l'arrivée. Voulez-vous malgré tout prendre ce risque ? (Il faut savoir que si votre vidéo source ne comporte pas de canal audio, vous pouvez sans souci répondre oui)." % (float(imgSec), float(idCodec.split("_")[3]))), QMessageBox.Yes, QMessageBox.No)
				if reply == QMessageBox.No: return
				elif reply == QMessageBox.Yes:
					hd_dnxhd_img_sec = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, laisserOuvert=ouvert)
					hd_dnxhd_img_sec.setWindowTitle(_(u"Encodage vidéo - Haute Définition - Avid DNxHD"))
					hd_dnxhd_img_sec.exec_()

			else:
				hd_dnxhd = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, laisserOuvert=ouvert)
				hd_dnxhd.setWindowTitle(_(u"Encodage vidéo - Haute Définition - Avid DNxHD"))
				hd_dnxhd.exec_()
		#####################################################################################

                self.lstFichiersSortie = cheminFichierEnregistrerVideo
		self.radioConvert.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		self.boutCompare.setEnabled(True)
		### Information à l'utilisateur
		self.infoLog(None, chemin, None, cheminFichierEnregistrerVideo)

		return cheminFichierEnregistrerVideo # module séquentiel

	def afficherAide(self):
		"""Boîte de dialogue de l'aide du cadre"""
		
		super( AnimationEncodageHD,self).afficherAide(_(u"<p><b>Vous pouvez ici transformer une vidéo de qualité ordinaire en vidéo 'Haute Définition' et en suivant les standards de la HD, c'est à dire HD 1080 16/9 (dont la résolution sera par défaut: 1920 x 1080), HD 720 16/9 (dont la résolution sera par défaut: 1280 x 720) et HD 1080 4/3 (dont la résolution sera par défaut: 1440 x 1080). Les vidéos résultantes (dans beaucoup de cas) verront leur qualité s'améliorer.</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> sélectionnez le type d'encodage que vous voulez faire.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la conversion) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la conversion <b>'vidéo convertie'</b> ou bien encore les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))
