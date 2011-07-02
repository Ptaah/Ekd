#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from gui_modules_animation.animation_base_encodageFiltre import Base_EncodageFiltre
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_common.EkdWidgets import EkdSaveDialog
from gui_modules_image.selectWidget import SelectWidget
from gui_modules_common.ffmpeg_avchd_gui import WidgetFFmpegAvchd

from gui_modules_animation.infoVideo import infovideo
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

class AnimationEncodageAVCHD(Base) :
	"Cadre de Animation -> Encodage -> Gestion AVCHD. But: encodages spécifiques au départ du format AVCHD haute définition (Caméra digitale HD)"

	def __init__(self):

		#=== Variable de configuration ===#
		self.config=EkdConfig
		# Identifiant de la classe
		self.idSection = "animation_encodage_avchd" # idSection à modifier lorsqu'il y aura des données dans la config.

		super(AnimationEncodageAVCHD, self).__init__('hbox', titre=_(u"Transcodage: Gestion de l'AVCHD"))
		self.printSection()

		# Customisation de l'interface aux besoins de l'AVCHD
		# 1. Onglet sources
		self.afficheurVideoSource=SelectWidget(extensions = ["*.m2ts", "*.mts", "*.m2t", "*.mp4"], mode="texte", video = True)
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"), self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.

		# 2. Onglet réglages
		groupReglage = QGroupBox()
		self.layoutReglage = QVBoxLayout(groupReglage)
		
		##=== Widget qui seront inclus dans la boite de réglage ===#
		layoutSortie = QHBoxLayout()
		sortie = QLabel(_(u"Encodage sortie vidéo :"))
		layoutSortie.addWidget(sortie)
		#
		self.codecSortie = QComboBox()
		liste_codecs = ["MOV (.mov)", "VOB (.vob)", "MPEG2 (.mpg)", "MPEG1 (.mpg)", "MPEG4 (.mp4)", "WMV2 (.wmv)", "HFYU (yuv422p) (.avi)", "MSMPEG 4 version 2 (.avi)", "Motion JPEG (.avi)", "FFV1 (FFmpeg) (.avi)", "Avid DNxHD (.mov)"]
		codecs = QStringList([QString(f) for f in liste_codecs])
		#
		self.codecSortie.addItems(codecs)
		layoutSortie.addWidget(self.codecSortie)
		self.layoutReglage.addLayout(layoutSortie)
		self.connect(self.codecSortie, SIGNAL("currentIndexChanged(int)"), self.changerReglagesCodec)
		self.connect(self.codecSortie, SIGNAL("activated(QString)"), self.selection)
		
		# Widgets pour la sélection de la résolution en sortie ---------------------
		layoutReso = QHBoxLayout()
		self.resolu = QLabel(_(u"Résolution sortie :"))
		layoutReso.addWidget(self.resolu)
		self.resoSortie = QComboBox()
		liste_reso = ["1920x1080", "1440x1080", "1280x720", "720x576"]
		reso = QStringList([QString(r) for r in liste_reso])
		self.resoSortie.addItems(reso)
		layoutReso.addWidget(self.resoSortie)
		self.layoutReglage.addLayout(layoutReso)
		self.connect(self.resoSortie, SIGNAL("currentIndexChanged(int)"), self.changerReglagesResol)

		### Ajouté le 13/08/2010 ###################################################
		# Widgets pour la sélection des spécificités DNxHD -------------------------
		layoutSpec_DNxHD = QHBoxLayout()
		self.label_spec_DNxHD = QLabel(_(u"Spécificités :"))
		layoutSpec_DNxHD.addWidget(self.label_spec_DNxHD)
		self.specSortie_DNxHD = QComboBox()
		liste_spec_DNxHD = [_(u"Dimension:1920x1080 Img/sec:29.97 Bitrate:220 Mb/s"), _(u"Dimension:1920x1080 Img/sec:29.97 Bitrate:145 Mb/s"), _(u"Dimension:1920x1080 Img/sec:25 Bitrate:185 Mb/s"), _(u"Dimension:1920x1080 Img/sec:25 Bitrate:120 Mb/s"), _(u"Dimension:1920x1080 Img/sec:25 Bitrate:36 Mb/s"), _(u"Dimension:1920x1080 Img/sec:24 Bitrate:175 Mb/s"), _(u"Dimension:1920x1080 Img/sec:24 Bitrate:115 Mb/s"), _(u"Dimension:1920x1080 Img/sec:24 Bitrate:36 Mb/s"), _(u"Dimension:1920x1080 Img/sec:23.976 Bitrate:175 Mb/s"), _(u"Dimension:1920x1080 Img/sec:23.976 Bitrate:115 Mb/s"), _(u"Dimension:1920x1080 Img/sec:23.976 Bitrate:36 Mb/s"), _(u"Dimension:1920x1080 Img/sec:29.97 Bitrate:220 Mb/s"), _(u"Dimension:1920x1080 Img/sec:29.97 Bitrate:145 Mb/s"), _(u"Dimension:1920x1080 Img/sec:29.97 Bitrate:45 Mb/s"), _(u"Dimension:1280x720 Img/sec:59.94 Bitrate:220 Mb/s"), _(u"Dimension:1280x720 Img/sec:59.94 Bitrate:145 Mb/s"), _(u"Dimension:1280x720 Img/sec:50 Bitrate:175 Mb/s"), _(u"Dimension:1280x720 Img/sec:50 Bitrate:115 Mb/s"), _(u"Dimension:1280x720 Img/sec:29.97 Bitrate:110 Mb/s"), _(u"Dimension:1280x720 Img/sec:29.97 Bitrate:75 Mb/s"), _(u"Dimension:1280x720 Img/sec:25 Bitrate:90 Mb/s"), _(u"Dimension:1280x720 Img/sec:25 Bitrate:60 Mb/s"), _(u"Dimension:1280x720 Img/sec:23.976 Bitrate:90 Mb/s"), _(u"Dimension:1280x720 Img/sec:23.976 Bitrate:60 Mb/s")]
		spec_DNxHD = QStringList([QString(spec_DNxHD) for spec_DNxHD in liste_spec_DNxHD])
		self.specSortie_DNxHD.addItems(spec_DNxHD)
		layoutSpec_DNxHD.addWidget(self.specSortie_DNxHD)
		self.layoutReglage.addLayout(layoutSpec_DNxHD)
		self.connect(self.specSortie_DNxHD, SIGNAL("currentIndexChanged(int)"), self.changerReglagesSpec_DNxHD)
		# Par défaut ces 2 widgets sont invisibles (comme ça ils n'apparaissent pas
		# dans le cas d'une sélection autre que Avid DNxHD (.mov))
		self.label_spec_DNxHD.hide()
		self.specSortie_DNxHD.hide()

		# Widgets pour la sélection du flux audio en sortie uniquement DNxHD -------
		layoutSon_DNxHD = QHBoxLayout()
		self.label_son_DNxHD = QLabel(_(u"Sortie flux audio :"))
		layoutSon_DNxHD.addWidget(self.label_son_DNxHD)
		self.sonSortie_DNxHD = QComboBox()
		liste_son_DNxHD = [_(u"Copie du flux audio"), _(u"Flux audio PCM sur 2 canaux (stereo)"), _(u"Pas de flux audio")]
		son_DNxHD = QStringList([QString(son_DNxHD) for son_DNxHD in liste_son_DNxHD])
		self.sonSortie_DNxHD.addItems(son_DNxHD)
		layoutSon_DNxHD.addWidget(self.sonSortie_DNxHD)
		self.layoutReglage.addLayout(layoutSon_DNxHD)
		self.connect(self.sonSortie_DNxHD, SIGNAL("currentIndexChanged(int)"), self.changerReglagesSon_DNxHD)
		# Par défaut ces 2 widgets sont invisibles (comme ça ils n'apparaissent pas
		# dans le cas d'une sélection autre que Avid DNxHD (.mov))
		self.label_son_DNxHD.hide()
		self.sonSortie_DNxHD.hide()
		############################################################################

		# Widgets pour la sélection du nombre d'images/seconde en sortie -----------
		layoutNbrIm = QHBoxLayout()
		self.labelNbrImage = QLabel(_(u"Nombre d'images/seconde (entre 2 et 60) :"))
		layoutNbrIm.addWidget(self.labelNbrImage)
		self.nbrImage = QSpinBox()
		self.nbrImage.setRange(2, 60)
		self.nbrImage.setValue(25)
		layoutNbrIm.addWidget(self.nbrImage)
		self.layoutReglage.addLayout(layoutNbrIm)
		self.connect(self.nbrImage, SIGNAL("valueChanged(int)"), self.changerReglagesNbrImgSec)

		# Widgets pour la sélection de la qualité de la vidéo en sortie ------------
		layoutQualite = QHBoxLayout()
		self.labelQualite = QLabel(_(u"Qualité de la vidéo (2:bonne, 31:mauvaise) :"))
		layoutQualite.addWidget(self.labelQualite)
		self.qualite = QSpinBox()
		self.qualite.setRange(2, 31)
		self.qualite.setValue(2)
		layoutQualite.addWidget(self.qualite)
		self.layoutReglage.addLayout(layoutQualite)
		self.connect(self.qualite, SIGNAL("valueChanged(int)"), self.changerReglagesQual)

		## On charge les options depuis EkdConfig
		self.loadOptions()
		##
		self.add(groupReglage, _(u"Réglages"))

		# 3 et 4 Onglet prévisualisation et info.
		self.addPreview()
		self.addLog()
		
	
	def changerReglagesCodec(self):
		"""Fonction pour collecte du réglage du codec en sortie"""
		self.select_codec = self.codecSortie.currentText()
		#print 'Codec sélectionné en sortie:', self.select_codec
		EkdPrint(u'Codec sélectionné en sortie: %s' % str(self.select_codec))
		EkdConfig.set(self.idSection, 'codec', self.codecSortie.currentIndex())

		
	def changerReglagesResol(self):
		"Fonction pour collecte du réglage de la résolution en sortie"
		# Afficher le changement de sélection dans le combo 
		# de sélection de la résolution en sortie
		self.select_resolution = self.resoSortie.currentText()
		resolution = EkdConfig.set(self.idSection, 'resolution', self.resoSortie.currentIndex())


	### Ajouté le 13/08/2010 ###################################################
	def changerReglagesSpec_DNxHD(self):
		"Fonction pour collecte du réglage des spécificités pour l'Avid DNxHD"
		# Afficher le changement de sélection dans le combo de
		# sélection des spécificités en sortie pour l'Avid DNxHD
		self.select_spec_DNxHD = self.specSortie_DNxHD.currentText()
		spec_DNxHD = EkdConfig.set(self.idSection, 'spec_DNxHD', self.specSortie_DNxHD.currentIndex())


	def changerReglagesSon_DNxHD(self):
		"Fonction pour collecte du réglage du flux audio en sortie uniquement pour l'Avid DNxHD"
		# Afficher le changement de sélection dans le combo de
		# sélection du flux audio en sortie pour l'Avid DNxHD
		self.select_son_DNxHD = self.sonSortie_DNxHD.currentText()
		son_DNxHD = EkdConfig.set(self.idSection, 'audio_DNxHD', self.sonSortie_DNxHD.currentIndex())
	############################################################################
		
		
	def changerReglagesNbrImgSec(self):
		"Fonction pour collecte du nombre d'images/seconde en sortie"
		# Afficher la valeur choisie par l'utilisateur du nbre d'img/sec
		self.select_nbreImgSec = self.nbrImage.value()
		#print "Valeur du nombre d'images par seconde:", self.select_nbreImgSec
		EkdPrint(u"Valeur du nombre d'images par seconde: %s" % self.select_nbreImgSec)
		EkdConfig.set(self.idSection, 'images_par_seconde', self.select_nbreImgSec)
		
	def changerReglagesQual(self):
		"Fonction pour collecte de la qualité de la vidéo en sortie"
		# Afficher la valeur choisie par l'utilisateur de la qualité de la vidéo
		self.select_qualite = self.qualite.value()
		#print "Valeur de la qualité de la vidéo:", self.select_qualite
		EkdPrint(u"Valeur de la qualité de la vidéo: %s" % self.select_qualite)
		EkdConfig.set(self.idSection, 'qualite', self.select_qualite)
		
		
	def selection(self):
		"Fonction pour affichage/masquage des widgets selon la sélection des codecs en sortie"
		# Le label d'info et le spinbox sont visibles dans la situation par défaut
		if self.codecSortie.currentText() in ["MOV (.mov)", "MPEG4 (.mp4)", "WMV2 (.wmv)", "HFYU (yuv422p) (.avi)", "MSMPEG 4 version 2 (.avi)", "Motion JPEG (.avi)", "FFV1 (FFmpeg) (.avi)"]:
			self.label_spec_DNxHD.hide() # Ajouté le 13/08/2010
			self.specSortie_DNxHD.hide() # Ajouté le 13/08/2010
			self.label_son_DNxHD.hide() # Ajouté le 13/08/2010
			self.sonSortie_DNxHD.hide() # Ajouté le 13/08/2010
			self.labelNbrImage.show()
			self.nbrImage.show()
			self.resolu.show() # Ajouté le 13/08/2010
			self.resoSortie.show() # Ajouté le 13/08/2010
			self.labelQualite.show()
			self.qualite.show()
		# Si l'utilisateur sélectionne VOB, MPEG1 ou MPEG2 dans l'encodage
		# final, le label d'info et le spinbox associé deviennent invisibles
		elif self.codecSortie.currentText() in ["VOB (.vob)", "MPEG1 (.mpg)", "MPEG2 (.mpg)"]:
			self.label_spec_DNxHD.hide() # Ajouté le 13/08/2010
			self.specSortie_DNxHD.hide() # Ajouté le 13/08/2010
			self.labelNbrImage.hide()
			self.nbrImage.hide()
			self.label_son_DNxHD.hide() # Ajouté le 13/08/2010
			self.sonSortie_DNxHD.hide() # Ajouté le 13/08/2010
			self.resolu.show() # Ajouté le 13/08/2010
			self.resoSortie.show() # Ajouté le 13/08/2010
			self.labelQualite.show()
			self.qualite.show()
		### Ajouté le 13/08/2010 ###################################################
		# Si l'utilisateur sélectionne Avid DNxHD dans l'encodage final,
		# le label d'info et le spinbox associé deviennent invisibles
		elif self.codecSortie.currentText() in ["Avid DNxHD (.mov)"]:
			self.resolu.hide()
			self.resoSortie.hide()
			self.labelNbrImage.hide()
			self.nbrImage.hide()
			self.labelQualite.hide()
			self.qualite.hide()
			self.label_spec_DNxHD.show()
			self.specSortie_DNxHD.show()
			self.label_son_DNxHD.show()
			self.sonSortie_DNxHD.show()
		############################################################################


	def getFile(self):
		self.chemin = self.afficheurVideoSource.getFiles()
		#self.chemin est une list comprenant le ou les fichiers sélectionnés.
		self.boutApp.setEnabled(True)
		self.mplayer.setEnabled(True)
		self.mplayer.setVideos(self.chemin)

		self.emit(SIGNAL("loaded"))
		return self.chemin


	def appliquer(self, nomSortie=None, ouvert=1):
		"Appel du moteur du cadre"
		
		if not nomSortie:
			chemin = self.getFile()
			
			self.chemins = chemin
			# suffix du codec actif (et collecte de l'extension en sortie)
			if self.codecSortie.currentText() == "MOV (.mov)": self.suffix_sortie = '.mov'
			elif self.codecSortie.currentText() == "VOB (.vob)": self.suffix_sortie = '.vob'
			elif self.codecSortie.currentText() == "MPEG4 (.mp4)": self.suffix_sortie = '.mp4'
			elif self.codecSortie.currentText() == "WMV2 (.wmv)": self.suffix_sortie = '.wmv'
			### Ajouté le 13/08/2010 ###################################################
			elif self.codecSortie.currentText() == "Avid DNxHD (.mov)": self.suffix_sortie = '.mov'
			############################################################################
			elif self.codecSortie.currentText() in ["MPEG1 (.mpg)", "MPEG2 (.mpg)"]: self.suffix_sortie = '.mpg'
			else: self.suffix_sortie = '.avi'
			
			# Sélection du codec pour la sortie
			self.codec_sortie = str(self.codecSortie.currentText())
			# Sélection de la résolution pour la vidéo en sortie (Largeur x Hauteur)
			resolution_sortie_texte = str(self.resoSortie.currentText())
			resol_l_h = resolution_sortie_texte.split('x')
			self.reso_largeur_sortie = str(resol_l_h[0])
			self.reso_hauteur_sortie = str(resol_l_h[1])
			#print 'Largeur', self.reso_largeur_sortie, type(self.reso_largeur_sortie)
			EkdPrint(u'Largeur %s %s' % (self.reso_largeur_sortie, type(self.reso_largeur_sortie)))
			#print 'Hauteur', self.reso_hauteur_sortie, type(self.reso_hauteur_sortie)
			EkdPrint(u'Hauteur %s %s' % (self.reso_hauteur_sortie, type(self.reso_hauteur_sortie)))
			# Nombre d'images par secondes sélectionnées pour la sortie
			self.nbreImgSec_sortie = str(self.nbrImage.value())
			# Valeur de  la qualité de la vidéo pour la sortie
			self.qualite_sortie = str(self.qualite.value())

			### Ajouté le 13/08/2010 ###################################################
			# Spécifications Avid DNxHD (.mov) 
			self.spec_sortie_DNxHD = str(self.specSortie_DNxHD.currentText())
			# Choix du flux audio en sortie pour Avid DNxHD
			self.son_sortie_DNxHD = str(self.sonSortie_DNxHD.currentText())
			############################################################################

			# suffix du codec actif
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=self.suffix_sortie, title=_(u"Sauver"))
			self.cheminFichierEnregistrerVideo = saveDialog.getFile()
			
			# A revoir mais là le fichier est nommé comme il faut (!)
			pre_cheminFichierEnregistrerVideo = self.cheminFichierEnregistrerVideo.split('.')
			self.cheminFichierEnregistrerVideo = pre_cheminFichierEnregistrerVideo[0]

		else: # module séquentiel
			self.cheminFichierEnregistrerVideo = nomSortie

		if not self.cheminFichierEnregistrerVideo:
			return

		# quel est l'index du dernier item sélectionné de la boîte de combo?
		#print 'index du codec sélectionné', self.codecSortie.currentIndex()
		EkdPrint(u'index du codec sélectionné %s' % self.codecSortie.currentIndex())

		### Rectification le 14/08/2010 ############################################
		if self.codecSortie.currentText() == "Avid DNxHD (.mov)":
			# Affectation des valeurs de nouvelle largeur et nouvelle hauteur
			# sélectionnées par l'utilisateur pour le traitement final
			self.reso_largeur_sortie = ""
			self.reso_hauteur_sortie = ""
			#
			self.qualite_sortie = ""
		elif self.codecSortie.currentText() != "Avid DNxHD (.mov)":
			# Si l'utilisateur sélectionne une autre option que Avid DNxHD (.mov)
			# ces valeurs sont définies comme vides (ça fonctionne bien)
			self.spec_sortie_DNxHD = ""
			self.son_sortie_DNxHD = ""
		############################################################################

		# identifiant du codec actif		
		# Appel de la classe

		try:
			### Ajout (le 13/08/2010) de self.spec_sortie_DNxHD, self.son_sortie_DNxHD #
			wfa = WidgetFFmpegAvchd(self.chemins, self.cheminFichierEnregistrerVideo, self.codec_sortie, self.reso_largeur_sortie, self.reso_hauteur_sortie, self.nbreImgSec_sortie, self.qualite_sortie, self.spec_sortie_DNxHD, self.son_sortie_DNxHD, self)	
			wfa.setWindowTitle(_(u"Traitement AVCHD (FFmpeg)"))
			wfa.exec_()
			############################################################################
		except:
			messageErrWfa=QMessageBox(self)
			messageErrWfa.setText(_(u"Problème lors de la conversion des fichiers (FFmpeg)\n"))
			messageErrWfa.setWindowTitle(_(u"Erreur"))
			messageErrWfa.setIcon(QMessageBox.Warning)
			messageErrWfa.exec_()
			return
	

	def actionsFin(self,sorties) :
		self.lstFichiersSortie = sorties
		# Mise à jour de la liste des fichiers de sortie dans la comboBox de sélection.
		self.mplayer.setVideos(sorties)
		self.radioConvert.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		self.boutCompare.setEnabled(True)
		self.infoLog(None, self.chemins, None, sorties)
		

	def afficherAide(self):
		"Boîte de dialogue de l'aide du cadre"

		super( AnimationEncodageAVCHD,self).afficherAide(_(u"<p><b>Vous pouvez ici transcoder des vidéos AVCHD (extension mts ou m2ts) en différents autres codecs tels que MOV, VOB, MPEG2, Motion JPEG.</b></p><p><b>AVCHD (Advanced Video Codec High Definition) est un format d'enregistrement et stockage numérique vidéo haute définition, mis au point par Sony et Panasonic. Ce format permet de réduire la taille des fichiers HD, tout en préservant un certain niveau de qualité de l'image restituée. Plus particulièrement adapté aux caméscopes, ce format vient en complément des formats HDV et MiniDV. <br>Source: http://fr.wikipedia.org/wiki/Advanced_Video_Codec_High_Definition.</b></p><p><b>Il est à noter ici (pour la gestion de l'AVCHD) que vous bénéficiez d'un traitement par lot, c'est à dire que tous les fichiers que vous allez charger seront traités (et pas seulement le fichier sélectionné).</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> sélectionnez le codec, et s'il le faut, faites les réglages de l'<b>Encodage sortie vidéo</b>, de la <b>Résolution sortie</b>, du <b>Nombre d'images/seconde</b> (n'est pas disponible pour une sortie en VOB, MPEG2 et MPEG1) et la <b>Qualité de la vidéo</b>.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la conversion) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la conversion <b>'vidéo convertie'</b> ou bien encore les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b>. A ce propos, vous noterez (et comme vous bénéficiez d'un traitement par lot des vidéos) que vous pouvez sélectionner (et ce pour chaque cas) la vidéo à visionner dans une liste déroulante qui est apparue juste en dessous du bouton de lecture. Dans le comparateur de vidéos, la sélection d'une vidéo avant encodage dans la liste déroulante (et ce dans la partie gauche), correspondra exactement à la vidéo après conversion (dans la partie droitre), vous pourrez ainsi comparer, comme il se doit, les deux vidéos.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))

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

	def loadOptions(self):
		"""
		On charge les différentes variables necessaire au widget
		"""
		idCodec = EkdConfig.get(self.idSection,'codec')
		self.codecSortie.setCurrentIndex(int(idCodec))
		resolution = EkdConfig.get(self.idSection,'resolution')
		self.resoSortie.setCurrentIndex(int(resolution))
		frequence = EkdConfig.get(self.idSection,'images_par_seconde')
		self.nbrImage.setValue(int(frequence))
		qualite = EkdConfig.get(self.idSection,'qualite')
		self.qualite.setValue(int(qualite))


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
