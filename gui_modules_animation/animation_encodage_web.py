#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, glob, shutil
from gui_modules_animation.animation_base_encodageFiltre import Base_EncodageFiltre
from gui_modules_common.mencoder_gui import WidgetMEncoder
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

class AnimationEncodageWeb(Base_EncodageFiltre):
	"""Cadre de Animation -> Transcodage -> Pour le web. But: encodages spécifiques à youtube, dailymotion..."""

	def __init__(self):

		# Identifiant de la classe
		self.idSection = "animation_encodage_web"
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

		self.listeCombo = [
			('youtube_16/9_HQ', _(u'Transcodage YouTube 16/9 Haute Qualité'), 0, '.avi'),
			('youtube_16/9_MQ', _(u'Transcodage YouTube 16/9 Moyenne Qualité'), 1, '.avi'),
			('youtube_16/9_LQ', _(u'Transcodage YouTube 16/9 Basse qualité'), 2, '.avi'),
			('youtube_4/3_HQ', _(u'Transcodage YouTube 4/3 Haute Qualité'), 3, '.avi'),
			('youtube_4/3_MQ', _(u'Transcodage YouTube 4/3 Moyenne Qualité'), 4, '.avi'),
			('youtube_4/3_LQ', _(u'Transcodage YouTube 4/3 Basse qualité'), 5, '.avi'),
			('google_video_16/9_HQ', _(u'Transcodage Google vidéo 16/9 Haute qualité'), 6, '.avi'),
			('google_video_16/9_MQ', _(u'Transcodage Google vidéo 16/9 Qualité moyenne'), 7, '.avi'),
			('google_video_16/9_LQ', _(u'Transcodage Google vidéo 16/9 Basse qualité'), 8, '.avi'),
			('google_video_4/3_HQ', _(u'Transcodage Google vidéo 4/3 Haute qualité'), 9, '.avi'),
			('google_video_4/3_MQ', _(u'Transcodage Google vidéo 4/3 Qualité moyenne'), 10, '.avi'),
			('google_video_4/3_LQ', _(u'Transcodage Google vidéo 4/3 Basse qualité'), 11, '.avi'),
			('dailymotion_sd_4/3', _(u'Transcodage Dailymotion SD 4/3'), 12, '.mp4'),
			('dailymotion_sd_16/9',  _(u'Transcodage Dailymotion SD 16/9'), 13, '.mp4'),
			('dailymotion_HD720p',  _(u'Transcodage Dailymotion HD720p'), 14, '.mp4'),
			]

		#---------------------------
		# Dérivation de la classe
		#---------------------------
		Base_EncodageFiltre.__init__(self, titre=_(u"Transcodage: Pour le Web"))


	def appliquer(self, nomSortie=None, ouvert=1):
		"""Appel du moteur du cadre"""

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
				
			# ------------------------------------------------------------------- #
			# Gestion des fichiers mod (extension .mod). Ce sont (apparemment)
			# des fichiers mpeg avec une extension .mod. Les fichiers en question 
			# ont juste besoin d'être renommés avec une extension .mpg avant le 
			# traitement.
			# ------------------------------------------------------------------- #
			ext_chargee = os.path.splitext(chemin)[1]
			nom_fich_sans_ext = os.path.splitext(os.path.basename(chemin))[0]
			if ext_chargee in ['.mod', '.MOD']:
				# Copie du fichier concerné dans le rep tampon et renommage avec ext .mpg
				shutil.copy(chemin, self.repTempFichiersMod+nom_fich_sans_ext + '.mpg')
				chemin = unicode(self.repTempFichiersMod + nom_fich_sans_ext + '.mpg')
				
			# suffix du codec actif
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			cheminFichierEnregistrerVideo = saveDialog.getFile()
			###################################################################################################################

		else: # module séquentiel
			chemin = cheminFichierEnregistrerVideo = nomSortie

		if not cheminFichierEnregistrerVideo:
			return

		# quel est l'index du dernier item sélectionné de la boîte de combo?
		#print 'index', index
		EkdPrint('index ' + str(index))
		# identifiant du codec actif
		idCodec = self.listeCombo[index][0]
		#print 'idCodec', idCodec
		EkdPrint('idCodec ' + idCodec)

		# Condition pour détection windows
		if os.name == 'nt':
			mencoder = WidgetMEncoder(idCodec, chemin, cheminFichierEnregistrerVideo, laisserOuvert=ouvert)
		# Condition pour détection Linux
		elif os.name in ['posix', 'mac']:
			mencoder = WidgetMEncoder(idCodec, chemin, cheminFichierEnregistrerVideo, laisserOuvert=ouvert)
		mencoder.setWindowTitle(_(u"Encodage vidéo - Pour le web"))
		mencoder.exec_()

		# Condition pour détection windows
		if os.name == 'nt':
			self.lstFichiersSortie =  cheminFichierEnregistrerVideo # pour la boite de dialogue de comparaison
		# Condition pour détection Linux
		elif os.name in ['posix', 'mac']:
			self.lstFichiersSortie =  cheminFichierEnregistrerVideo # pour la boite de dialogue de comparaison
		self.radioConvert.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		self.boutCompare.setEnabled(True)
		### Information à l'utilisateur
		self.infoLog(None, chemin, None, cheminFichierEnregistrerVideo)

		return cheminFichierEnregistrerVideo # module séquentiel

	def tamponAction(self) :
		#print u"Message différent"
		EkdPrint(u"Message différent")


	def afficherAide(self):
		"""Boîte de dialogue de l'aide du cadre"""

		super(AnimationEncodageWeb,self).afficherAide(_(u"<p><b>Sous la dénomination 'Pour le web', vous pouvez ici transcoder vos vidéos afin qu'elles soient publiables sur internet et plus précisément sur Google (Google video), Youtube ou sur Dailymotion.</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> sélectionnez le type d'encodage que vous voulez faire.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la conversion) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la conversion <b>'vidéo convertie'</b> ou bien encore les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))
