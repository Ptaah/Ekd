#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, locale, glob, shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#### Enlevé le 30/03/11 #############################
#from PyQt4.QtCore import SIGNAL, Qt
#from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSpinBox, QSlider, QStackedWidget, QSizePolicy, QMessageBox
#####################################################
from gui_modules_animation.animation_base_encodageFiltre import Base_EncodageFiltre
from gui_modules_common.mencoder_gui import WidgetMEncoder
# Création des objets: WidgetFFmpeg2theora et WidgetFFmpeg ... l'objet WidgetMEncoder a été changé en conséquence 
from gui_modules_common.ffmpeg2theora_gui import WidgetFFmpeg2theora
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdTools import debug

# Collecte des infos codec audio
from moteur_modules_animation.mplayer import getParamVideo
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


# Les widgets des 4 1ères classes apparaissent alternativemement
# selon l'entrée de la boîte de combo sélectionnée (stacked)

class Codecs_SansReglages(QWidget):
	# -------------------------------------------------------------------
	# Widgets associés au codecs:
	# Copie (format original) - AVI-RAW Sans Compression - Codec XVID -
	# Qualite SVCD - Qualite DVD - Codec H264 MPEG 4
	# -------------------------------------------------------------------
	def __init__(self):
		QWidget.__init__(self)

		# label texte
		txt1=_(u"Réglage automatique pour ce choix")
		label=QLabel("<center>%s</center>" %txt1)

		vbox=QVBoxLayout()
		vbox.addWidget(label)
		self.setLayout(vbox)


class Codecs_AvecReglages(QWidget):
	# -------------------------------------------------------------------
	# Widgets associés aux codecs :
	# -------------------------------------------------------------------
	# Les données sont définies dans l'appel se trouvant dans la classe
	def __init__(self, choixCodec, min_range_1, max_range_1, min_range_2, max_range_2, txt1 = _(u"Réglage de la compression : "), txt5 = _(u"Réglage du bitrate vidéo : ")):
	
		'''
		Codecs_AvecReglages  : Crée un widget avec : 1 slider, 1 bare de progession et un texte explicatif
		          choixCodec : Nom du codec qui sera utilisé lors de l'enregistrement dans EkdConfig
			  min_range_1  : Valeur minimale du slider et de la barre
			  max_range_1  : Valeur maximale du slider et de la barre
			  min_range_2  : Valeur minimale du slider et de la barre
			  max_range_2  : Valeur maximale du slider et de la barre
			  txt1         : Texte intitulé du réglage (compression vidéo)
			  txt5         : Texte intitulé du réglage (bitrate vidéo)
		'''
		
		QWidget.__init__(self)

		self.choixCodec = choixCodec

		self.idSection = "animation_encodage_general"

		# label titre
		self.txt1 = txt1
		self.txt5 = txt5
		
		self.min_range_2 = min_range_2
		self.max_range_2 = max_range_2
		
		#txt1=_(u"Réglage de la compression : ")
		self.label_1=QLabel("<center><u>%s</u></center>" % txt1)

		# boite de spin pour la compression vidéo
		self.spinCompression=QSpinBox()		# self car on va récupérer la variable depuis le moteur
		self.spinCompression.setRange(min_range_1, max_range_1)
		
		self.label_2=QLabel("<center><u>%s</u></center>" % txt5)
		
		txt6 = _(u'Dimension de la vidéo :')
		self.label_3 = QLabel("<center><u>%s</u></center>" % txt6)
		
		self.label_4 = QLabel("<center><u>%s</u></center>" % txt6)
		self.label_5 = QLabel("<center><u>%s</u></center>" % txt6)
		
		# Boîte de spin pour le bitrate vidéo
		self.spinBitrateVideo=QSpinBox()
		self.spinBitrateVideo.setRange(min_range_2, max_range_2)

		# Curseur associé à spinCompression
		self.curseur_1 = QSlider(Qt.Horizontal)
		self.curseur_1.setRange(min_range_1, max_range_1)
		
		self.connect(self.spinCompression,SIGNAL("valueChanged(int)"),self.sauverSpin_1)
		self.connect(self.curseur_1, SIGNAL("sliderMoved(int)"), self.curseurBouge_1)
		
		# Curseur associé à spinBitrateVideo
		self.curseur_2 = QSlider(Qt.Horizontal)
		self.curseur_2.setRange(min_range_2, max_range_2)
		
		self.connect(self.spinBitrateVideo,SIGNAL("valueChanged(int)"),self.sauverSpin_2)
		self.connect(self.curseur_2, SIGNAL("sliderMoved(int)"), self.curseurBouge_2)

		# Widgets pour la sélection de la résolution 
		# en sortie pour le 3GP
		self.resoSortie3gp = QComboBox()
		liste_reso_3gp = [(u'128x96', '128x96'), (u'176x144', '176x144'), (u'352x288', '352x288'),  (u'704x576', '704x576')]
		for i in liste_reso_3gp: self.resoSortie3gp.addItem(i[0],QVariant(i[1]))
		self.connect(self.resoSortie3gp, SIGNAL("activated(int)"), self.changerReglagesResol3gp)
		
		# Widgets pour la sélection de la résolution 
		# en sortie pour l'AMV
		self.resoSortieAMV = QComboBox()
		liste_reso_AMV = [(u'128x90', '128x90'), (u'128x128', '128x128'), (u'160x120', '160x120'), (u'208x176', '208x176')]
		for i in liste_reso_AMV: self.resoSortieAMV.addItem(i[0],QVariant(i[1]))
		self.connect(self.resoSortieAMV, SIGNAL("activated(int)"), self.changerReglagesResolAMV)
		
		# Widgets pour la sélection de la résolution en sortie pour les codecs: 
		# codecmotionjpeg, codecmpeg2, codech264mpeg4, codech264mpeg4_ext_h264, 
		# codecdivx4, codecmpeg1, macromediaflashvideo, codecwmv2
		self.resoSortieGeneral = QComboBox()
		liste_reso_General = [(_(u"Pas de changement (vidéo avec la même taille que l'original)"), u'idem'), (_(u'HD 1080p (16/9): 1920x1080'), u'-vf scale=1920:1080 -aspect 16:9'), (_(u'HD 720p (16/9): 1280x720'), u'-vf scale=1280:720 -aspect 16:9'), (_(u'HD 1080p divisé par deux (16/9): 960x540'), u'-vf scale=960:540 -aspect 16:9'), (_(u'HD 480 (16/9): 852x480'), u'-vf scale=852:480 -aspect 16:9'), (_(u'PAL/SECAM (16/9): 1024x576'), u'-vf scale=1024:576 -aspect 16:9'), (_(u'PAL/SECAM Computer Video (4/3): 768x576'), u'-vf scale=768:576 -aspect 4:3'), (_(u'PAL/SECAM (rapport 1.25): 720x576'), u'-vf scale=720:576'), (_(u'PAL/SECAM (4/3): 384x288'), u'-vf scale=384:288 -aspect 4:3'), (_(u'PAL/SECAM Qualité VCD (rapport 1.22): 352x288'), u'-vf scale=352:288'), (_(u'PAL/SECAM (4/3): 320x240'), u'-vf scale=320:240 -aspect 4:3'),  (_(u'NTSC (rapport 1.5): 720x480'), u'-vf scale=720:480'), (_(u'NTSC Computer Video (4/3): 640x480'), u'-vf scale=640:480 -aspect 4:3'), (_(u'NTSC Computer Video (4/3): 512x384'), u'-vf scale=512:384 -aspect 4:3'), (_(u'NTSC SVCD (1/1): 480x480'), u'-vf scale=480:480'), (_(u'NTSC Qualité VCD (rapport 1.46): 352x240'), u'-vf scale=352:240'), (_(u'Affichage WHUXGA (rapport 1.6): 7680x4800'), u'-vf scale=7680:4800'), (_(u'Affichage WHSXGA (rapport 1.56): 6400x4096'), u'-vf scale=6400:4096'), (_(u'Affichage HSXGA (rapport 1.25): 5120x4096'), u'-vf scale=5120:4096'), (_(u'Affichage WQUXGA (rapport 1.6): 3840x2400'), u'-vf scale=3840:2400'), (_(u'Affichage WQSXGA (rapport 1.56): 3200x2048'), u'-vf scale=3200:2048'), (_(u'Affichage QSXGA (rapport 1.25): 2560x2048'), u'-vf scale=2560:2048'), (_(u'Affichage WOXGA (rapport 1.6): 2560x1600'), u'-vf scale=2560:1600'), (_(u'Affichage QXGA (4/3): 2048x1536'), u'-vf scale=2048:1536 -aspect 4:3'), (_(u'Affichage WUXGA (rapport 1.6): 1920x1200'), u'-vf scale=1920:1200'), (_(u'Affichage WSXGA (rapport 1.56): 1600x1024'), u'-vf scale=1600:1024'), (_(u'Affichage WXGA (16/9): 1366x768'), u'-vf scale=1366:768 -aspect 16:9'), (_(u'Affichage SXGA (rapport 1.25): 1280x1024'), u'-vf scale=1280:1024'), (_(u'Affichage UXGA (4/3): 1600x1200'), u'-vf scale=1600:1200 -aspect 4:3'), (_(u'Affichage XGA (4/3): 1024x768'), u'-vf scale=1024:768 -aspect 4:3'), (_(u'Affichage SVGA (4/3): 800x600'), u'-vf scale=800:600 -aspect 4:3'), (_(u'Affichage VEGA (rapport 1.83): 640x350'), u'-vf scale=640:350'), (_(u'Affichage VGA (4/3): 640x480'), u'-vf scale=640:480 -aspect 4:3'), (_(u'Affichage QQVGA (4/3): 160x120'), u'-vf scale=160:120 -aspect 4:3'), (_(u'Smartphone (16/10): 800x480'), u'-vf scale=800:480 -aspect 16:10')]
		for i in liste_reso_General: self.resoSortieGeneral.addItem(i[0],QVariant(i[1]))
		self.connect(self.resoSortieGeneral, SIGNAL("activated(int)"), self.changerReglagesResolGeneral)
		
		try:
			debug( "%s" % EkdConfig.get(self.idSection,self.choixCodec))
			self.spinCompression.setValue(int(EkdConfig.get(self.idSection,self.choixCodec)))
		except:
			debug("Pas de parametre ou mauvais parametre de configuration pour:\n\
			DivX4, Codec Motion JPEG, Codec MPEG1, Codec MPEG2 ou Codec WMV2")
			#debug( "Pas de paramètre ou mauvais paramètre de configuration pour:\n\
			#DivX4, Codec Motion JPEG, Codec MPEG1, Codec MPEG2 ou Codec WMV2")

		# Rangement des widgets
		vbox = QVBoxLayout(self)
		grid=QGridLayout()
		# Label pour la compression vidéo
		grid.addWidget(self.label_1,1,2)
		# Slider de la qualité de la compression
		grid.addWidget(self.spinCompression,2,1)
		# Curseur associé à spinCompression
		grid.addWidget(self.curseur_1,2,2)
		# Label pour le bitrate vidéo
		grid.addWidget(self.label_2,3,2)
		# Slider du bitrate vidéo
		grid.addWidget(self.spinBitrateVideo,4,1)
		# Curseur associé à spinBitrateVideo
		grid.addWidget(self.curseur_2,4,2)
		grid.addWidget(self.label_3,5,2)
		grid.addWidget(self.resoSortie3gp,6,2)
		grid.addWidget(self.label_4,7,2)
		grid.addWidget(self.resoSortieAMV,8,2)
		grid.addWidget(self.label_5,9,2)
		grid.addWidget(self.resoSortieGeneral,10,2)
		vbox.addStretch()
		vbox.addLayout(grid)
		vbox.addStretch()

		# On récupère la valeur du bitrate à partir de la configuration
		try:
			bitrate = EkdConfig.get('animation_encodage_general_bitrate_video',self.choixCodec)
			self.spinBitrateVideo.setValue(int(bitrate))
		except IndexError:
			pass
		# On cache certains widgets suivant les codecs choisis dans 
		# la liste ... et on montre ceux qui doivent être montrés
		if self.choixCodec in ['codech264mpeg4', 'codech264mpeg4_ext_h264']:
			self.label_1.hide()
			self.spinCompression.hide()
			self.curseur_1.hide()
			self.label_3.hide()
			self.resoSortie3gp.hide()
			self.label_4.hide()
			self.resoSortieAMV.hide()
		elif self.choixCodec in ['codecoggtheora', 'codec_vob_ffmpeg']:
			self.label_2.hide()
			self.spinBitrateVideo.hide()
			self.curseur_2.hide()
			self.label_3.hide()
			self.resoSortie3gp.hide()
			self.label_4.hide()
			self.resoSortieAMV.hide()
			self.label_5.hide()
			self.resoSortieGeneral.hide()
		elif self.choixCodec in ['codecdivx4', 'codecmotionjpeg', 'codecmpeg1', 'codecmpeg2', 'codecwmv2', 'macromediaflashvideo']:
			self.label_3.hide()
			self.resoSortie3gp.hide()
			self.label_4.hide()
			self.resoSortieAMV.hide()
		elif self.choixCodec in ['avirawsanscompression', 'codec_hfyu_ffmpeg']:
			self.label_1.hide()
			self.spinCompression.hide()
			self.curseur_1.hide()
			self.label_2.hide()
			self.spinBitrateVideo.hide()
			self.curseur_2.hide()
			self.label_3.hide()
			self.resoSortie3gp.hide()
			self.label_4.hide()
			self.resoSortieAMV.hide()
			self.label_5.show()
			self.resoSortieGeneral.show()
		elif self.choixCodec in ['codecxvid']:
			self.label_1.hide()
			self.spinCompression.hide()
			self.curseur_1.hide()
			self.label_2.show()
			self.spinBitrateVideo.show()
			self.curseur_2.show()
			self.label_3.hide()
			self.resoSortie3gp.hide()
			self.label_4.hide()
			self.resoSortieAMV.hide()
			self.label_5.show()
			self.resoSortieGeneral.show()
		elif self.choixCodec in ['codec_3GP_ffmpeg']:
			self.label_1.hide()
			self.spinCompression.hide()
			self.curseur_1.hide()
			self.label_2.hide()
			self.spinBitrateVideo.hide()
			self.curseur_2.hide()
			self.label_4.hide()
			self.resoSortieAMV.hide()
			self.label_3.show()
			self.resoSortie3gp.show()
			self.label_5.hide()
			self.resoSortieGeneral.hide()
		elif self.choixCodec in ['codec_AMV_ffmpeg']:
			self.label_1.hide()
			self.spinCompression.hide()
			self.curseur_1.hide()
			self.label_2.hide()
			self.spinBitrateVideo.hide()
			self.curseur_2.hide()
			self.label_3.hide()
			self.resoSortie3gp.hide()
			self.label_4.show()
			self.resoSortieAMV.show()
			self.label_5.hide()
			self.resoSortieGeneral.hide()
		elif self.choixCodec in ['codec_mov_ffmpeg']:
			self.label_1.show()
			self.spinCompression.show()
			self.curseur_1.show()
			self.label_2.hide()
			self.spinBitrateVideo.hide()
			self.curseur_2.hide()
			self.label_3.hide()
			self.resoSortie3gp.hide()
			self.label_4.hide()
			self.resoSortieAMV.hide()
		
	def sauverSpin_1(self,i):
		"""conserver le spin dans le fichier de configuration et modifie le curseur"""
		debug("%s %d" % (self.choixCodec,i))
		EkdConfig.set(self.idSection,self.choixCodec,i)
		# sauver curseur
		self.curseur_1.setValue(i)

	def curseurBouge_1(self, i):
		"""Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
		self.spinCompression.setValue(i)
	
	def sauverSpin_2(self,i):
		"""conserver le spin dans le fichier de configuration et modifie le curseur"""
		debug("%s %d" % (self.choixCodec,i))
		#EkdConfig.set(self.idSection,self.choixCodec,i)
		EkdConfig.set('animation_encodage_general_bitrate_video',self.choixCodec,i)
		# sauver curseur
		self.curseur_2.setValue(i)

	def curseurBouge_2(self, i):
		"""Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
		self.spinBitrateVideo.setValue(i)
	
	# Pour la sélection de la résolution pour le 3GP
	def changerReglagesResol3gp(self, i):
		# Afficher le changement de sélection dans le combo 
		# de sélection de la résolution en sortie
		idCombo3GP = str(self.resoSortie3gp.itemData(i).toStringList()[0])
		#print "Combo :", idCombo3GP
		EkdPrint(u"Combo : %s" % idCombo3GP)
	
	# Pour la sélection de la résolution pour l'AMV
	def changerReglagesResolAMV(self, i):
		# Afficher le changement de sélection dans le combo 
		# de sélection de la résolution en sortie
		#self.selectResolutionAMV = self.resoSortieAMV.currentText()
		#self.selectResolutionAMV = self.selectResolutionAMV.currentIndex()
		#print self.choixCodec, self.selectResolutionAMV
		idComboAMV = str(self.resoSortieAMV.itemData(i).toStringList()[0])
		#print "Combo :", idComboAMV
		EkdPrint(u"Combo : %s" % idComboAMV)

	# Pour la sélection de la résolution Générale
	def changerReglagesResolGeneral(self, i):
		# Afficher le changement de sélection dans le combo 
		# de sélection de la résolution en sortie
		self.idComboGeneral = str(self.resoSortieGeneral.itemData(i).toStringList()[0])
		#print "Combo :", self.idComboGeneral
		EkdPrint(u"Combo : %s" % self.idComboGeneral)


class Animation_Encodage_General(Base_EncodageFiltre):
	# -------------------------------------------------------------------
	# Cadre accueillant les widgets de : Animation >> Encodage
	# -------------------------------------------------------------------

	def __init__(self):

		#=== Identifiant de la classe ===#
		self.idSection = "animation_encodage_general"
		
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

		# -------------------------------------------------------------------
		# Widgets intégrés à la boîte de groupe "Réglage de sortie de l'encodage".
		# La boîte de combo définie ci-dessus 'sélectionne' ceux qui vont s'afficher
		# -> utilisation d'un stacked
		# -------------------------------------------------------------------

		# === Widgets associés au codecs: Copie (format original) - AVI-RAW Sans
		# Compression - Codec XVID - Qualite SVCD - Qualite DVD - Codec H264 MPEG 4

		# création de stacked pour les QWidget
		self.stacked=QStackedWidget()
		self.stacked.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))

		self.itemStacked_sansReglages=Codecs_SansReglages()
		# par défaut
		self.indexStacked_sansReglages=self.stacked.addWidget(self.itemStacked_sansReglages)
		
		# === Widgets associés aux codecs qui possèdent des réglages (itemStacked)
		self.itemStacked_AVI_RAW=Codecs_AvecReglages('avirawsanscompression', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_HFYU=Codecs_AvecReglages('avirawsanscompression', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_DIVX4=Codecs_AvecReglages('codecdivx4', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_XVID=Codecs_AvecReglages('codecxvid', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_JPEG=Codecs_AvecReglages('codecmotionjpeg', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_MPEG1=Codecs_AvecReglages('codecmpeg1', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_MPEG2=Codecs_AvecReglages('codecmpeg2', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_WMV2=Codecs_AvecReglages('codecwmv2', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_VOB=Codecs_AvecReglages('codec_vob_ffmpeg', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_flash=Codecs_AvecReglages('macromediaflashvideo', min_range_1=1 , max_range_1=100, min_range_2=10, max_range_2=5000, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_oggTheora=Codecs_AvecReglages('codecoggtheora', min_range_1=0 , max_range_1=10, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_mpeg4_h264=Codecs_AvecReglages('codech264mpeg4', min_range_1=800 , max_range_1=2800, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_mpeg4_h264_ext_h264=Codecs_AvecReglages('codech264mpeg4_ext_h264', min_range_1=800 , max_range_1=2800, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_3GP=Codecs_AvecReglages('codec_3GP_ffmpeg', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_AMV=Codecs_AvecReglages('codec_AMV_ffmpeg', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		self.itemStacked_MOV=Codecs_AvecReglages('codec_mov_ffmpeg', min_range_1=1, max_range_1=100, min_range_2=800, max_range_2=2800, txt1=_(u"Réglage de la compression : "), txt5=_(u"Réglage du bitrate vidéo : "))
		
		# === Widgets associés aux codecs qui possèdent des réglages (indexStacked)
		self.indexStacked_AVI_RAW=self.stacked.addWidget(self.itemStacked_AVI_RAW)
		self.indexStacked_HFYU=self.stacked.addWidget(self.itemStacked_HFYU)
		self.indexStacked_DIVX4=self.stacked.addWidget(self.itemStacked_DIVX4)
		self.indexStacked_XVID=self.stacked.addWidget(self.itemStacked_XVID)
		self.indexStacked_JPEG=self.stacked.addWidget(self.itemStacked_JPEG)
		self.indexStacked_MPEG1=self.stacked.addWidget(self.itemStacked_MPEG1)
		self.indexStacked_MPEG2=self.stacked.addWidget(self.itemStacked_MPEG2)
		self.indexStacked_WMV2=self.stacked.addWidget(self.itemStacked_WMV2)
		self.indexStacked_VOB=self.stacked.addWidget(self.itemStacked_VOB)
		self.indexStacked_flash=self.stacked.addWidget(self.itemStacked_flash)
		self.indexStacked_oggTheora=self.stacked.addWidget(self.itemStacked_oggTheora)
		self.indexStacked_mpeg4_h264=self.stacked.addWidget(self.itemStacked_mpeg4_h264)
		self.indexStacked_mpeg4_h264_ext_h264=self.stacked.addWidget(self.itemStacked_mpeg4_h264_ext_h264)
		self.indexStacked_3GP=self.stacked.addWidget(self.itemStacked_3GP)
		self.indexStacked_AMV=self.stacked.addWidget(self.itemStacked_AMV)
		self.indexStacked_MOV=self.stacked.addWidget(self.itemStacked_MOV)

		#----------------------------------------------------------------------------------
		# Paramètres de la liste de combo: [(identifiant, nom entrée, index du stacked,
		# 	instance stacked, extension fichier sortie, valeur spin à récupérer?),...]
		#----------------------------------------------------------------------------------
		self.listeCombo =	[\
		('copie',		_(u'Copie (format original)'),		self.indexStacked_sansReglages,\
			self.itemStacked_sansReglages,	'',		0),\
		('avirawsanscompression',_(u'AVI-RAW i420 (sans compression) (.avi)'),	self.indexStacked_AVI_RAW,\
			self.itemStacked_AVI_RAW,	'.avi',		1),\
		('codec_dv_ffmpeg',_(u'Codec DV (.dv)'),	self.indexStacked_sansReglages,\
			self.itemStacked_sansReglages,	'.dv',		0),\
		('codec_mov_ffmpeg',_(u'Codec QuickTime MOV (.mov)'),	self.indexStacked_MOV,\
			self.itemStacked_MOV,	        '.mov',		1),\
		('codec_hfyu_ffmpeg',_(u'Codec HFYU: Huffman Lossless YUV (yuv422p) (.avi)'), self.indexStacked_HFYU,\
			self.itemStacked_HFYU,	        '.avi',		1),\
		('codecmotionjpeg',	_(u'Codec Motion JPEG (.avi)'),		self.indexStacked_JPEG,\
			self.itemStacked_JPEG,		'.avi',		1),\
		('codecoggtheora',	_(u'Codec OGG THEORA (.ogg)'),		self.indexStacked_oggTheora,\
			self.itemStacked_oggTheora,	'.ogg',		1),\
		('codec_vob_ffmpeg',_(u'Codec VOB (DVD-Video stream MPEG-2) (.vob)'),	self.indexStacked_VOB,\
			self.itemStacked_VOB,	'.vob',		1),\
		('codecmpeg2',		_(u'Codec MPEG 2 (.mpg)'),		self.indexStacked_MPEG2,\
			self.itemStacked_MPEG2,		'.mpg',		1),\
		('codech264mpeg4',	_(u'Codec H264 MPEG 4 (.mp4)'),		self.indexStacked_mpeg4_h264,\
			self.itemStacked_mpeg4_h264,	'.mp4',		1),\
		('codech264mpeg4_ext_h264', _(u'Codec H264 MPEG 4 (.h264)'),	self.indexStacked_mpeg4_h264_ext_h264,\
			self.itemStacked_mpeg4_h264_ext_h264,	'.h264',	1),\
		('codecxvid',		_(u'Codec XVID (.avi)'),		self.indexStacked_XVID,\
			self.itemStacked_XVID,	  '.avi',		1),\
		('codecdivx4',		_(u'Codec DIVX4 (.avi)'),		self.indexStacked_DIVX4,\
			self.itemStacked_DIVX4,		'.avi',		1),\
		('codecmpeg1',		_(u'Codec MPEG 1 (.mpg)'),		self.indexStacked_MPEG1,\
			self.itemStacked_MPEG1,		'.mpg',		1),\
		('macromediaflashvideo',_(u'Macromedia Flash Video (.flv)'),	self.indexStacked_flash,\
			self.itemStacked_flash,		'.flv',		1),\
		('codecwmv2',		_(u'Codec WMV2 (.wmv)'),		self.indexStacked_WMV2,\
			self.itemStacked_WMV2,		'.wmv',		1),\
		('codec_3GP_ffmpeg',_(u'Codec 3GP (3rd Generation Partnership Project) (.3gp)'), self.indexStacked_3GP,\
			self.itemStacked_3GP,	'.3gp',		1),\
		('codec_AMV_ffmpeg',		_(u'Codec AMV: pour lecteurs mp4 (.avi)'),  self.indexStacked_AMV,\
			self.itemStacked_AMV,		'.avi',		1),\
					]
		
		#---------------------------
		# Dérivation de la classe
		#---------------------------
		super(Animation_Encodage_General, self).__init__(_(u"Transcodage: Général"))



	def afficherAide(self):
		""" Boîte de dialogue de l'aide du cadre Animation > Encodage """
		
		super(Animation_Encodage_General,self).afficherAide(_(u"<p><b>Vous pouvez ici coder ou plutôt transcoder une vidéo d'un format vers un autre. Dans certains cas le transcodage permet de compresser la vidéo, c'est à dire d'en réduire le poids.</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> sélectionnez le codec, et s'il le faut, changez le/les réglage(s) proposé(s).</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la conversion) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la conversion <b>'vidéo convertie'</b> ou bien encore les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


	def tailleVideoRetouche(self):
		""" Fonction pour contrôler les changements de syntaxe pour Mencoder et FFmpeg 
		suivant les codecs sélectionnés """

		# quel est l'index du dernier item sélectionné de la boîte de combo?
		i=self.combo.currentIndex()
		# identifiant du codec actif
		idCodec=str(self.combo.itemData(i).toStringList()[0]) # méthode de QVariant

		for j in self.listeCombo: # attribution de la valeur du spin s'il existe
			if j[0]==idCodec and j[5]==1:

				# Dimension de la vidéo (preset). Exception pour contrôler 
				# les cas où l'utilisateur laisse par défaut: 
				# Pas de changement (vidéo avec la même taille que l'original)
				try: self.valeurSizeGeneral = str(j[3].idComboGeneral)
				except: self.valeurSizeGeneral = ''

				if j[0] in ['avirawsanscompression']:
					# Liste contenant les correspondances des tailles (paramètre 1 et la 
					# valeur attribuée dans le paramètre 2, et ce dans chaque tuple)
					listeSizeGeneralAviRaw = [('-vf scale=1920:1080 -aspect 16:9', 'scale=1920:1080,'), ('-vf scale=1280:720 -aspect 16:9', 'scale=1280:720,'), ('-vf scale=960:540 -aspect 16:9', 'scale=960:540,'), ('-vf scale=852:480 -aspect 16:9', 'scale=852:480,'), ('-vf scale=1024:576 -aspect 16:9', 'scale=1024:576,'), ('-vf scale=768:576 -aspect 4:3', 'scale=768:576,'), ('-vf scale=720:576', 'scale=720:576,'), ('-vf scale=384:288 -aspect 4:3', 'scale=384:288,'), ('-vf scale=352:288', 'scale=352:288,'), ('-vf scale=320:240 -aspect 4:3', 'scale=320:240,'), ('-vf scale=720:480', 'scale=720:480,'), ('-vf scale=640:480 -aspect 4:3', 'scale=640:480,'), ('-vf scale=512:384 -aspect 4:3', 'scale=512:384,'), ('-vf scale=480:480', 'scale=480:480,'), ('-vf scale=352:240', 'scale=352:240,'), ('-vf scale=7680:4800', 'scale=7680:4800,'), ('-vf scale=6400:4096', 'scale=6400:4096,'), ('-vf scale=5120:4096', 'scale=5120:4096,'), ('-vf scale=3840:2400', 'scale=3840:2400,'), ('-vf scale=3200:2048', 'scale=3200:2048,'), ('-vf scale=2560:2048', 'scale=2560:2048,'), ('-vf scale=2560:1600', 'scale=2560:1600,'), ('-vf scale=2048:1536 -aspect 4:3', 'scale=2048:1536,'), ('-vf scale=1920:1200', 'scale=1920:1200,'), ('-vf scale=1600:1024', 'scale=1600:1024,'), ('-vf scale=1366:768 -aspect 16:9', 'scale=1366:768,'), ('-vf scale=1280:1024', 'scale=1280:1024,'), ('-vf scale=1600:1200 -aspect 4:3', 'scale=1600:1200,'), ('-vf scale=1024:768 -aspect 4:3', 'scale=1024:768,'), ('-vf scale=800:600 -aspect 4:3', 'scale=800:600,'), ('-vf scale=640:350', 'scale=640:350,'), ('-vf scale=640:480 -aspect 4:3', 'scale=640:480,'), ('-vf scale=160:120 -aspect 4:3', 'scale=160:120,'), ('-vf scale=800:480 -aspect 16:10', 'scale=800:480,')]
					# Sélection du paramètre 2
					for v1 in listeSizeGeneralAviRaw: 
						if self.valeurSizeGeneral == v1[0]:
							self.valeurSizeGeneral = v1[1]

				if j[0] in ['codecxvid']:
					listeSizeGeneralXvid = [('-vf scale=1920:1080 -aspect 16:9', '-vf scale=1920:1080'), ('-vf scale=1280:720 -aspect 16:9', '-vf scale=1280:720'), ('-vf scale=960:540 -aspect 16:9', '-vf scale=960:540'), ('-vf scale=852:480 -aspect 16:9', '-vf scale=852:480'), ('-vf scale=1024:576 -aspect 16:9', '-vf scale=1024:576'), ('-vf scale=768:576 -aspect 4:3', '-vf scale=768:576'), ('-vf scale=720:576', '-vf scale=720:576'), ('-vf scale=384:288 -aspect 4:3', '-vf scale=384:288'), ('-vf scale=352:288', '-vf scale=352:288'), ('-vf scale=320:240 -aspect 4:3', '-vf scale=320:240'), ('-vf scale=720:480', '-vf scale=720:480'), ('-vf scale=640:480 -aspect 4:3', '-vf scale=640:480'), ('-vf scale=512:384 -aspect 4:3', '-vf scale=512:384'), ('-vf scale=480:480', '-vf scale=480:480'), ('-vf scale=352:240', '-vf scale=352:240'), ('-vf scale=7680:4800', '-vf scale=7680:4800'), ('-vf scale=6400:4096', '-vf scale=6400:4096'), ('-vf scale=5120:4096', '-vf scale=5120:4096'), ('-vf scale=3840:2400', '-vf scale=3840:2400'), ('-vf scale=3200:2048', '-vf scale=3200:2048'), ('-vf scale=2560:2048', '-vf scale=2560:2048'), ('-vf scale=2560:1600', '-vf scale=2560:1600'), ('-vf scale=2048:1536 -aspect 4:3', '-vf scale=2048:1536'), ('-vf scale=1920:1200', '-vf scale=1920:1200'), ('-vf scale=1600:1024', '-vf scale=1600:1024'), ('-vf scale=1366:768 -aspect 16:9', '-vf scale=1366:768'), ('-vf scale=1280:1024', '-vf scale=1280:1024'), ('-vf scale=1600:1200 -aspect 4:3', '-vf scale=1600:1200'), ('-vf scale=1024:768 -aspect 4:3', '-vf scale=1024:768'), ('-vf scale=800:600 -aspect 4:3', '-vf scale=800:600'), ('-vf scale=640:350', '-vf scale=640:350'), ('-vf scale=640:480 -aspect 4:3', '-vf scale=640:480'), ('-vf scale=160:120 -aspect 4:3', '-vf scale=160:120'), ('-vf scale=800:480 -aspect 16:10', '-vf scale=800:480')]
					for v2 in listeSizeGeneralXvid: 
						if self.valeurSizeGeneral == v2[0]:
							self.valeurSizeGeneral = v2[1]

				elif j[0] in ['codec_mov_ffmpeg', 'codec_hfyu_ffmpeg']:
					listeSizeGeneralMov = [('-vf scale=1920:1080 -aspect 16:9', '-s 1920x1080 -aspect 16:9'), ('-vf scale=1280:720 -aspect 16:9', '-s 1280x720 -aspect 16:9'), ('-vf scale=960:540 -aspect 16:9', '-s 960x540 -aspect 16:9'), ('-vf scale=852:480 -aspect 16:9', '-s 852x480 -aspect 16:9'), ('-vf scale=1024:576 -aspect 16:9', '-s 1024x576 -aspect 16:9'), ('-vf scale=768:576 -aspect 4:3', '-s 768x576 -aspect 4:3'), ('-vf scale=720:576', '-vf scale=720:576'), ('-vf scale=384:288 -aspect 4:3', '-s 384x288 -aspect 4:3'), ('-vf scale=352:288', '-s 352x288'), ('-vf scale=320:240 -aspect 4:3', '-s 320x240 -aspect 4:3'), ('-vf scale=720:480', '-s 720x480'), ('-vf scale=640:480 -aspect 4:3', '-s 640x480 -aspect 4:3'), ('-vf scale=512:384 -aspect 4:3', '-s 512x384 -aspect 4:3'), ('-vf scale=480:480', '-s 480x480'), ('-vf scale=352:240', '-s 352x240'), ('-vf scale=7680:4800', '-s 7680x4800'), ('-vf scale=6400:4096', '-s 6400x4096'), ('-vf scale=5120:4096', '-s 5120x4096'), ('-vf scale=3840:2400', '-s 3840x2400'), ('-vf scale=3200:2048', '-s 3200x2048'), ('-vf scale=2560:2048', '-s 2560x2048'), ('-vf scale=2560:1600', '-s 2560x1600'), ('-vf scale=2048:1536 -aspect 4:3', '-s 2048x1536 -aspect 4:3'), ('-vf scale=1920:1200', '-s 1920x1200'), ('-vf scale=1600:1024', '-s 1600x1024'), ('-vf scale=1366:768 -aspect 16:9', '-s 1366x768 -aspect 16:9'), ('-vf scale=1280:1024', '-s 1280x1024'), ('-vf scale=1600:1200 -aspect 4:3', '-s 1600x1200 -aspect 4:3'), ('-vf scale=1024:768 -aspect 4:3', '-s 1024x768 -aspect 4:3'), ('-vf scale=800:600 -aspect 4:3', '-s 800x600 -aspect 4:3'), ('-vf scale=640:350', '-s 640x350'), ('-vf scale=640:480 -aspect 4:3', '-s 640x480 -aspect 4:3'), ('-vf scale=160:120 -aspect 4:3', '-s 160x120 -aspect 4:3'), ('-vf scale=800:480 -aspect 16:10', '-s 800x480 -aspect 16:10')]
					for v3 in listeSizeGeneralMov: 
						if self.valeurSizeGeneral == v3[0]:
							self.valeurSizeGeneral = v3[1]


	def appliquer(self, nomSortie=None, ouvert=1):
		"""appel du moteur de ekd -> encodage"""

		if not nomSortie:
			index=self.combo.currentIndex()
			chemin = unicode(self.getFile())

			# suffix du codec actif
			suffix=self.listeCombo[index][4]
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

                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			cheminFichierEnregistrerVideo = saveDialog.getFile()

		else: # module séquentiel
			chemin=cheminFichierEnregistrerVideo=nomSortie

		if not cheminFichierEnregistrerVideo:
			return

		# quel est l'index du dernier item sélectionné de la boîte de combo?
		i=self.combo.currentIndex()
		# identifiant du codec actif
		idCodec=str(self.combo.itemData(i).toStringList()[0]) # méthode de QVariant

		# pas de spin pour Copie (format original) - AVI-RAW Sans Compression
		# Codec XVID - Qualite SVCD - Qualite DVD - Codec H264 MPEG 4
		spin=None # par défaut

		for j in self.listeCombo: # attribution de la valeur du spin s'il existe
			if j[0]==idCodec and j[5]==1:
				if j[0] in ['codecmotionjpeg', 'codecmpeg2', 'codech264mpeg4', 'codech264mpeg4_ext_h264', 'codecdivx4', 'codecmpeg1', 'macromediaflashvideo', 'codecwmv2']:
					# La valeur de compression vidéo va de 31 à 1 (31 --> mauvaise qualité
					# jusqu'à à 1 --> très bonne qualité). Ici on va calculer en mettant
					# en place un réglage qui partira de 1 à 100 (1 --> mauvaise qualité
					# et 100 --> très bonne qualité)
					calculValComp = (31 * j[3].spinCompression.value()) / 100
					# Il faut soustraire le résultat à 31 pour
					# avoir une valeur reconnue par Mencoder
					calculValComp = 31 - calculValComp
					# Si la la valeur de réglage de la compression est réglée sur
					# 100, la valeur retournée sera 0 (ce qui va générer une erreur
					# dans Mencoder ... et ainsi stopper le process), la valeur
					# retournée sera donc de 1 (ce qui sera ok)
					if j[3].spinCompression.value() == 100: calculValComp = 1
					# Dimension de la vidéo (preset). Exception pour contrôler 
					# les cas où l'utilisateur laisse par défaut: 
					# Pas de changement (vidéo avec la même taille que l'original)
					try: valeurSizeGeneral = str(j[3].idComboGeneral)
					except: valeurSizeGeneral = ''
					# La valeur est sous forme de tuple et contient au moins 3 valeurs
					spin = (str(j[3].spinBitrateVideo.value()), str(calculValComp), str(valeurSizeGeneral))
				elif j[0] in ['codec_vob_ffmpeg']:
					# La valeur de compression vidéo va de 255 à 1 (255 --> mauvaise qualité
					# jusqu'à 1 --> très bonne qualité). Ici on va calculer en mettant
					# en place un réglage qui partira de 1 à 100 (1 --> mauvaise qualité
					# et 100 --> très bonne qualité)
					calculValComp = (255 * j[3].spinCompression.value()) / 100
					# Il faut soustraire le résultat à 255 pour
					# avoir une valeur reconnue par Mencoder
					calculValComp = 255 - calculValComp
					# Si la la valeur de réglage de la compression est réglée sur
					# 100, la valeur retournée sera 0 (ce qui va générer une erreur
					# dans Mencoder ... et ainsi stopper le process), la valeur
					# retournée sera donc de 1 (ce qui sera ok)
					if j[3].spinCompression.value() == 100: calculValComp = 1
					# On attribue la valeur
					spin = str(calculValComp)
				elif j[0] in ['codec_3GP_ffmpeg']:
					# On affecte la valeur de la résolution pour le 3GP
					# sélectionnée par l'utilisateur
					self.valeurSize3GP = j[3].resoSortie3gp.currentText()
				elif j[0] in ['codec_AMV_ffmpeg']:
					# On affecte la valeur de la résolution pour l'AMV
					# sélectionnée par l'utilisateur
					self.valeurSizeAMV = j[3].resoSortieAMV.currentText()
				elif j[0] in ['codec_mov_ffmpeg']: 
					# La valeur de compression vidéo va de 31 à 1 (31 --> mauvaise qualité
					# jusqu'à à 1 --> très bonne qualité). Ici on va calculer en mettant
					# en place un réglage qui partira de 1 à 100 (1 --> mauvaise qualité
					# et 100 --> très bonne qualité)
					calculValComp = (31 * j[3].spinCompression.value()) / 100
					# Il faut soustraire le résultat à 31 pour
					# avoir une valeur reconnue par Mencoder
					calculValComp = 31 - calculValComp
					# Si la la valeur de réglage de la compression est réglée sur
					# 100, la valeur retournée sera 0 (ce qui va générer une erreur
					# dans Mencoder ... et ainsi stopper le process), la valeur
					# retournée sera donc de 1 (ce qui sera ok)
					if j[3].spinCompression.value() == 100: calculValComp = 1
					# Appel de la fonction dans laquelle sont définies les tailles 
					# des vidéos pour un traitement pour un changement de syntaxe
					self.tailleVideoRetouche()
					# La valeur est sous forme de tuple et contient au moins 2 valeurs
					self.valeurCompSizeMOV = (str(calculValComp), str(self.valeurSizeGeneral))
				elif j[0] in ['avirawsanscompression']:
					# Appel de la fonction dans laquelle sont définies les tailles 
					# des vidéos pour un traitement pour un changement de syntaxe
					self.tailleVideoRetouche()
					self.valeurSizeAVI_RAW = str(self.valeurSizeGeneral)
				elif j[0] in ['codecxvid']:
					# Appel de la fonction dans laquelle sont définies les tailles 
					# des vidéos pour un traitement pour un changement de syntaxe
					self.tailleVideoRetouche()
					valeurSizeXVID = str(self.valeurSizeGeneral)
					# La valeur est sous forme de tuple et contient au moins 2 valeurs
					spin = (str(j[3].spinBitrateVideo.value()), valeurSizeXVID)
				elif j[0] in ['codec_hfyu_ffmpeg']:
					# Appel de la fonction dans laquelle sont définies les tailles 
					# des vidéos pour un traitement pour un changement de syntaxe
					self.tailleVideoRetouche()
					self.valeurSizeHFYU = str(self.valeurSizeGeneral)

				else:
					spin = str(j[3].spinCompression.value())
		
		debug( "%s %s %s %s" % (idCodec, chemin, spin, type(spin)))
		
		# Collecte des infos codec audio
		infosCodecAudio = {'Fichier':chemin}
		getParamVideo(chemin, ['ID_AUDIO_CODEC'], infosCodecAudio)
		try: audioCodec = infosCodecAudio['ID_AUDIO_CODEC']
		except: audioCodec = "codec audio non disponible"

		# Appel des classes après séparation des traitements gérés par Mencoder, FFmpeg
		# et FFmpeg2theora.
		# Appel du moteur -> animation encodage avec un codec particulier
		try:
			if idCodec in ['copie', 'codecdivx4', 'codecmotionjpeg', 'codecmpeg1', 'codecmpeg2', 'codecwmv2', 'codecxvid', 'macromediaflashvideo', 'codech264mpeg4', 'codech264mpeg4_ext_h264']:
				mencoder = WidgetMEncoder(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = spin, laisserOuvert=ouvert)
				mencoder.setWindowTitle(_(u"Transcodage vidéo"))
				mencoder.exec_()

			elif idCodec in ['avirawsanscompression']:
				mencoder = WidgetMEncoder(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = self.valeurSizeAVI_RAW, laisserOuvert=ouvert)
				mencoder.setWindowTitle(_(u"Transcodage vidéo"))
				mencoder.exec_()

			elif idCodec in ['codecxvid']:
				mencoder = WidgetMEncoder(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = spin, laisserOuvert=ouvert)
				mencoder.setWindowTitle(_(u"Transcodage vidéo"))
				mencoder.exec_()

			elif idCodec in ['codec_hfyu_ffmpeg']:
				ffmpeg = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = self.valeurSizeHFYU, laisserOuvert=ouvert)
				ffmpeg.setWindowTitle(_(u"Transcodage vidéo"))
				ffmpeg.exec_()
				
			elif idCodec == 'codec_3GP_ffmpeg':
				# Pour le transcodage 3GP, si on charge une vidéo qui
				# comporte un canal audio, le transcodage n'a pas lieu
				if audioCodec == "codec audio non disponible":
					ffmpeg = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = self.valeurSize3GP, laisserOuvert=ouvert)
					ffmpeg.setWindowTitle(_(u"Transcodage vidéo"))
					ffmpeg.exec_()
				else:
					messErr3GP=QMessageBox(self)
					messErr3GP.setText(_(u"<p>Le transcodage des vidéos comportant une piste audio en 3GP a momentanément été désactivé.</b></p>"))
					messErr3GP.setWindowTitle(_(u"Erreur"))
					messErr3GP.setIcon(QMessageBox.Warning)
					messErr3GP.exec_()
					return
					
			elif idCodec == 'codec_AMV_ffmpeg':
				ffmpeg = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = self.valeurSizeAMV, laisserOuvert=ouvert)
				ffmpeg.setWindowTitle(_(u"Transcodage vidéo"))
				ffmpeg.exec_()

			elif idCodec == 'codec_mov_ffmpeg':
				ffmpeg = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = self.valeurCompSizeMOV, laisserOuvert=ouvert)
				ffmpeg.setWindowTitle(_(u"Transcodage vidéo"))
				ffmpeg.exec_()

			elif idCodec == 'codecoggtheora':
				#### Gestion de l'extension .h264 ####
				# Si on charge une vidéo avec extension .h264, ffmpeg2theora ne peut 
				# pas effectuer l'encodage
				if ext_chargee == '.h264':
					messErrExtH264ffmpeg2th=QMessageBox(self)
					messErrExtH264ffmpeg2th.setText(_(u"<p>Il n'est pas possible de donner suite au traitement <b>à partir d'une vidéo avec extension h264 et en ayant choisi: %s.</b></p><p><b>Veuillez choisir un autre codec dans la liste proposée.</b></p>" % codec_reglage))
					messErrExtH264ffmpeg2th.setWindowTitle(_(u"Erreur"))
					messErrExtH264ffmpeg2th.setIcon(QMessageBox.Warning)
					messErrExtH264ffmpeg2th.exec_()
					return
				else:	
					ffmpeg2theora = WidgetFFmpeg2theora(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = spin, laisserOuvert=ouvert)
					ffmpeg2theora.setWindowTitle(_(u"Transcodage vidéo"))
					ffmpeg2theora.exec_()

			else:
				#### Gestion de l'extension .h264 ####
				# Si on charge une vidéo avec extension .h264, FFmpeg ne peut 
				# pas effectuer l'encodage
				if ext_chargee == '.h264':
					if codec_reglage in [u'Codec DV (.dv)', u'Codec QuickTime MOV (.mov)', u'Codec HFYU: Huffman Lossless YUV (yuv422p) (.avi)', u'Codec VOB (DVD-Video stream MPEG-2) (.vob)', u'Codec 3GP (3rd Generation Partnership Project) (.3gp)', u'Codec AMV: pour lecteurs mp4 (.avi)']:
						messErrExtH264ffmpeg=QMessageBox(self)
						messErrExtH264ffmpeg.setText(_(u"<p>Il n'est pas possible de donner suite au traitement <b>à partir d'une vidéo avec extension h264 et en ayant choisi: %s.</b></p><p><b>Veuillez choisir un autre codec dans la liste proposée.</b></p>" % codec_reglage))
						messErrExtH264ffmpeg.setWindowTitle(_(u"Erreur"))
						messErrExtH264ffmpeg.setIcon(QMessageBox.Warning)
						messErrExtH264ffmpeg.exec_()
						return
				else:
					ffmpeg = WidgetFFmpeg(idCodec, chemin, cheminFichierEnregistrerVideo, valeurNum = spin, laisserOuvert=ouvert)
					ffmpeg.setWindowTitle(_(u"Transcodage vidéo"))
					ffmpeg.exec_()

		#except Exception, e:
		except None:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"Un problème est survenu.")+str(e))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Warning)
			messageErreur.exec_()
			return


		self.lstFichiersSortie =  cheminFichierEnregistrerVideo # pour la boite de dialogue de comparaison
		self.radioConvert.setChecked(True)
		self.radioSource.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setEnabled(True)
		self.boutCompare.setEnabled(True)
		### Information à l'utilisateur
		self.infoLog(None, chemin, None, cheminFichierEnregistrerVideo)

		return cheminFichierEnregistrerVideo # module séquentiel
