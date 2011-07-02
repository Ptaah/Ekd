#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of EKD
# EKD is a program to make pre and post treatment on video file
# Copyright (C) 2007-2009  Angelo Lama

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


# script grandement inspiré du code c++ de
# http://doc.qtfr.org/public/2007/qt_mplayer.tar.gz
# merci à IrmatDen

import sys, os
from PyQt4.QtGui import QWidget, QColor, QPalette, QSizePolicy, QPainter, QFont
from PyQt4.QtGui import QFontMetricsF, QDialog, QIcon, QPushButton, QGroupBox
from PyQt4.QtGui import QVBoxLayout, QRadioButton, QSpacerItem, QSlider
from PyQt4.QtGui import QHBoxLayout, QFileDialog, QMessageBox, QLabel, QComboBox
from PyQt4.QtCore import PYQT_VERSION_STR, SLOT, SIGNAL, Qt, QSize, QProcess
from PyQt4.QtCore import QTimer, QStringList, QString, QSettings, QVariant
from PyQt4.QtCore import QByteArray, QTime

from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdTools import debug
################################################################################

if os.name in ['posix', 'mac']:
	coding = "utf-8"
else :
	coding = "cp1252"


def getParamVideo(cheminVideoEntre, parameter, hashInfo = None):
	"""Renvoie un ou plusieurs paramètres de la vidéo sous forme de flottant.
	La variable «cheminVideoEntre» est le chemin de la vidéo de type unicode.
	La variable «parameter» est un tuple de paramètres à renvoyer.
	La dernière variable renvoyée est un tuple des lignes de log
	23/07/2009 : hashInfo contiendra la hashmap des infos demandées
	"""


	#cheminVideoEntre = cheminVideoEntre.encode("UTF8")
	if hashInfo == None:
		hashInfo = {}
	# Condition pour détection windows
	if os.name == 'nt':
		commande = u'mplayer.exe -vo null -ao null -identify -frames 0 '+ u"\"" + unicode(cheminVideoEntre) + u"\""
	# Condition pour détection Linux ou MacOSX
	elif os.name in ['posix', 'mac']:
		commande = u'mplayer ' + u"\""+ unicode(cheminVideoEntre) + u"\" -vo null -ao null -frames 0 -identify '$@' 2>/dev/null"

        #recupDonneesVideo = os.popen(commande.encode(coding)).readlines()
        processus = QProcess()
        processus.start(commande)
        if (not processus.waitForStarted()):
            raise (u"Erreur de récupération des informations")
        if ( not processus.waitForFinished()):
            raise (u"Erreur de récupération des informations")
        recupDonneesVideo = QString(processus.readAllStandardOutput())

	lstValeurs = []
	log = []

	#for ligne in recupDonneesVideo:
	for ligne in recupDonneesVideo.split("\n"):
		try:
			# On veut que les caractères non ASCII s'affichent
                        # correctement pour les noms de fichiers
			log.append(ligne)
		except UnicodeDecodeError:
			debug("Traitement d'exception unicode au niveau de " \
                                "getParamVideo() probablement dûe aux " \
                                "méta-données de la vidéo")
			log.append(ligne)
		for param in parameter:
			if param in ligne:
				ligne = ligne.replace(param, "")
				ligne = ligne.replace("=", "")
				ligne = ligne.replace("\n", "")
				############################################
				# Commenté le 01/09/10 --> voir si tout 
				# fonctionne malgré tout (commenté pour
				# pouvoir lire les tags vidéos correctement)
				#ligne = ligne.replace(" ", "")
				############################################

				############################################
				# Le 01/09/10 Essai de réglage de la sortie  
				# pour les accents dans les tags vidéo
				# VOIR SI SYNTAXE PLUS GENERIQUE
				ligne = ligne.replace("é", "e")
				ligne = ligne.replace("è", "e")
				ligne = ligne.replace("ç", "c")
				ligne = ligne.replace("à", "a")
				ligne = ligne.replace("ù", "u")
				ligne = ligne.replace("ä", "a")
				ligne = ligne.replace("ü", "u")
				ligne = ligne.replace("ö", "o")
				############################################

				try :
					lstValeurs.append(float(ligne))
					hashInfo[param] = float(ligne)
				except :
					lstValeurs.append(str(ligne))
					hashInfo[param] = str(ligne)

	lstValeurs.append(log)
	#lstValeurs.append(hashInfo)
	return lstValeurs


def getVideoLength(cheminVideoEntre):
	"Retourne la durée de la vidéo. L'argument doit être de type unicode"
	return getParamVideo(cheminVideoEntre, ["ID_LENGTH"])

def getVideoSize(cheminVideoEntre):
	"Retourne la taille de la vidéo. L'argument doit être de type unicode"
	hashReturn = {}
	getParamVideo(cheminVideoEntre, ["ID_VIDEO_WIDTH", "ID_VIDEO_HEIGHT"], hashReturn)
	return (hashReturn["ID_VIDEO_WIDTH"], hashReturn["ID_VIDEO_HEIGHT"])

def getVideoFPS(cheminVideoEntre):
	"Retourne le nombre de trames par seconde de la vidéo. L'argument doit être de type unicode"
	return getParamVideo(cheminVideoEntre, ["ID_VIDEO_FPS"])

def getDemuxer(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, ["ID_DEMUXER"])[0]

def getVideoFormat(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, ['ID_VIDEO_FORMAT'])[0]

def getVideoCodec(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, ['ID_VIDEO_CODEC'])[0]

def getVideoBitrate(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, ['ID_VIDEO_BITRATE'])[0]

def getVideoWidth(cheminVideoEntre):
	return getVideoSize(cheminVideoEntre)[0]

def getVideoHeigth(cheminVideoEntre):
	return getVideoSize(cheminVideoEntre)[1]

#########################################################################
# Ajouté le 01/09/10 pour la gestion des tags dans les vidéos

def getVideoTagName(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, [" Name: "])[0]

def getVideoTagArtist(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, [' Artist: '])[0]

def getVideoTagGenre(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, [' Genre: '])[0]

def getVideoTagSubject(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, [' Subject: '])[0]

def getVideoTagCopyright(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, [' Copyright: '])[0]

def getVideoTagComments(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, [' Comments: '])[0]
#########################################################################

def getAudioCodec(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, ['ID_AUDIO_CODEC'])[0]

def getAudioRate(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, ['ID_AUDIO_RATE'])[0]

def getAudioBitrate(cheminVideoEntre):
	return getParamVideo(cheminVideoEntre, ['ID_AUDIO_BITRATE'])[0]

def getVideoRatio(cheminVideoEntre):
	"Retourne l'aspect ratio de la vidéo. L'argument doit être de type unicode"
	return getParamVideo(cheminVideoEntre, ["ID_VIDEO_ASPECT"])


class TracerChrono(QWidget):
	"""On trace le temps car il ne s'affiche pas bien autrement pour certaines configurations"""
	TAILLE = "0:00:00:000"
	def __init__(self):
		# parent nous permettra d'accéder à la valeur du curseur
		QWidget.__init__(self)
		self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
		self.raz()
		######################################################################################

	def paintEvent(self, event):
		paint = QPainter()
		paint.begin(self)
		paint.drawText(event.rect(), Qt.AlignCenter, self.num)
		paint.end()

	def minimumSizeHint(self):
		"Pour être sûr que le texte du chrono ne soit pas tronqué"
		font = QFont(self.font())
		font.setPointSize(font.pointSize() - 1)
		fm = QFontMetricsF(font)
		l = fm.width(TracerChrono.TAILLE*2) # + 10.
		L = fm.height() + 2.
		return QSize(l, L)
		######################################################################################

	def raz(self):
		'''On évite d'avoir à parcourir le code à la recherche de 00:00:00....'''
		self.num = TracerChrono.TAILLE

class DisplayVid(QWidget) :

	def resizeEvent(self,event) :
		QWidget.resizeEvent(self,event)
		self.emit(SIGNAL("changeSize"))

class Mplayer(QDialog):

	REVENIR, PAS_PRECEDENT_SUIVANT, PRECEDENT_SUIVANT, CURSEUR_SUR_UNE_LIGNE,\
		CURSEUR_A_PART, PARCOURIR, PAS_PARCOURIR, LIST, RATIO = range(9)

	HAUTEUR, LARGEUR = range(2)

	def __init__(self, cheminVideo=[], taille=(250,225),
			choixWidget=(RATIO, REVENIR, PAS_PRECEDENT_SUIVANT,CURSEUR_SUR_UNE_LIGNE,PAS_PARCOURIR,LIST),
			debutFin=(0,0), cheminMPlayer=None, barreTaches=None, facteurLimitant=HAUTEUR,
			cheminParcourir=None, parent=None):

		"""widget mplayer"""
		QDialog.__init__(self, parent)

		#=== Paramètres généraux ===#
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.setWindowTitle(_(u"Player vidéo"))
                #On réduit la marge pour gagner de l'espace
                self.setContentsMargins(0,0,0,0)

		self.systeme = os.name
                ### Quand EKD windows est installé, le chemin des dépendances sont ###########
                ### positionnées dans les variables d'environnement donc pas besoin de #######
                ### collecter le chemin des ces dépendances ##################################
                self.cheminMPlayer = "mplayer"

                ##############################################################################

		# liste de chemins vidéos
		if type(cheminVideo) != list :
			self.listeVideos=[cheminVideo]
		else :
			self.listeVideos = cheminVideo

		# est-ce que la vidéo est lue?
		self.estLue=False

		# est-ce que la vidéo est en pause?
		self.estEnPause=False

		self.debutFin = debutFin

		# Nom du fichier courant (le self n'est pas encore utile)
		txtParDefaut = u"Pas de fichier lu"
		if self.listeVideos.__len__()!=0:
			self.fichierCourant =  [txtParDefaut, self.listeVideos[0]]
		else: self.fichierCourant = [txtParDefaut, ""]

		# Barre des tâches de la fenêtre
		self.barreTaches = barreTaches

		# Taille de la vidéo
		self.tailleLargeur=taille[0]
		self.tailleHauteur=taille[1]

		# paramètres des boutons-icones
		iconTaille=22
		flat=1

		# Pour récupérer le temps courant depuis certains cadre
		self.temps = 0

		self.dureeTimer = 10 # temps en ms
		###############################################################################################################################

		#Pour être plus précis lors de la lecture, on prend comme unité la miliseconde. ######################
		## Il faut donc utiliser une echelle 1000 fois plus grande pour les unités du slider
		self.echelle=1000
		###############################################################################################################################

		# Permet de récupérer la durée de la vidéo depuis une instance de la classe
		# Sert dans certains cadres
		self.dureeVideo = 0

		# Chemin sur lequel peut s'ouvrir la boite de dialogue de fichier
		# associée au bouton parcourir
		self.cheminPourBoutonParcourir = cheminParcourir

		self.taille = taille

		debug("self.taille avant lecture : %s %s" % (self.taille, type(self.taille)))

		#=== Widgets ===#

		self.icone_lire=QIcon("Icones" + os.sep + "player_play.png")
		self.icone_pause=QIcon("Icones" + os.sep + "player_pause.png")
		self.icone_arret=QIcon("Icones" + os.sep + "player_stop.png")

		if Mplayer.REVENIR in choixWidget:
			self.bout_revenir = QPushButton(u"Revenir")
			self.bout_revenir.setIcon(QIcon("Icones" + os.sep + "revenir.png"))

		if Mplayer.PARCOURIR in choixWidget:
			self.bout_ouvVideo = QPushButton(u"Parcourir...")

		if Mplayer.PRECEDENT_SUIVANT in choixWidget:
			self.bout_prec = QPushButton(QIcon("Icones" + os.sep + "player_rew.png"),"")
			self.bout_prec.setIconSize(QSize(iconTaille, iconTaille))
			self.bout_prec.setFlat(flat)
			self.bout_suivant = QPushButton(QIcon("Icones" + os.sep + "player_fwd.png"),"")
			self.bout_suivant.setIconSize(QSize(iconTaille, iconTaille))
			self.bout_suivant.setFlat(flat)

		self.LISTW=False
		if Mplayer.LIST in choixWidget :
			self.LISTW = True
			self.listFichiers = QComboBox()
			self.listFichiers.hide()
			self.setListeVideo()


		self.bout_LectPause = QPushButton(self.icone_lire,"")
		self.bout_LectPause.setIconSize(QSize(iconTaille, iconTaille))
		self.bout_LectPause.setFlat(flat)

		self.bout_Arret = QPushButton(self.icone_arret,"")
		self.bout_Arret.setIconSize(QSize(iconTaille, iconTaille))
		self.bout_Arret.setFlat(flat)

		# widget qui contiendra la vidéo
		self.cibleVideo = DisplayVid(self)
		# par défaut le widget-cible est noir
		color = QColor(0, 0, 0)
		self.cibleVideo.setAutoFillBackground(True)
		self.cibleVideo.setPalette(QPalette(color))
		self.cibleVideo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.cibleVideo.setFixedHeight(self.taille[1])
		self.cibleVideo.setToolTip(self.fichierCourant[0])

		#Choix de l'aspect ratio de la vidéo
                if Mplayer.RATIO in choixWidget :
                    self.conf = QGroupBox()
                    self.conf.setContentsMargins(0,0,0,0)
                    self.conf.setMinimumSize(QSize(self.tailleLargeur, 0))
                    self.conf.setObjectName("conf")
                    self.verticalLayout = QHBoxLayout(self.conf)
                    self.verticalLayout.setObjectName("verticalLayout")
                    self.choicenorm = QRadioButton(self.conf)
                    self.choicenorm.setObjectName("choicenorm")
                    self.verticalLayout.addWidget(self.choicenorm)
                    self.choicewide = QRadioButton(self.conf)
                    self.choicewide.setObjectName("choicewide")
                    self.verticalLayout.addWidget(self.choicewide)
                    self.choiceone = QRadioButton(self.conf)
                    self.choiceone.setObjectName("choiceone")
                    self.verticalLayout.addWidget(self.choiceone)
                    self.choicenorm.setText("4:3")
                    self.choicewide.setText("16:9")
                    self.choiceone.setText("w:h")
                # Checked le ratio de la vidéo
                if self.listeVideos.__len__()!=0:
                        self.changeRatio(self.listeVideos[0])
                else :
                        self.setRatio(4.0/3.0)
                        if Mplayer.RATIO in choixWidget :
                            self.choicenorm.setChecked(True)

		self.slider = QSlider(Qt.Horizontal)
		self.slider.setEnabled(True)

		self.mplayerProcess = QProcess(self)

		self.timer = QTimer(self)

		self.tempsChrono = TracerChrono()

		#=== mise-en-page/plan ===#
		mhbox = QHBoxLayout()
		vbox = QVBoxLayout()
		vbox.addWidget(self.cibleVideo)
                if Mplayer.RATIO in choixWidget :
                    vbox.addWidget(self.conf)
		hbox = QHBoxLayout()
		if Mplayer.REVENIR in choixWidget:
			hbox.addWidget(self.bout_revenir)
		if Mplayer.PARCOURIR in choixWidget:
			hbox.addWidget(self.bout_ouvVideo)
		hbox.addWidget(self.bout_LectPause)
		hbox.addWidget(self.bout_Arret)
		if Mplayer.PRECEDENT_SUIVANT in choixWidget:
			hbox.addWidget(self.bout_prec)
			hbox.addWidget(self.bout_suivant)
		hbox.addWidget(self.tempsChrono)
		if Mplayer.CURSEUR_A_PART not in choixWidget:
			hbox.addWidget(self.slider)
		vbox.addLayout(hbox)
		if Mplayer.CURSEUR_A_PART in choixWidget:
			hbox.setAlignment(Qt.AlignLeft)
			hbox = QHBoxLayout()
			hbox.addWidget(self.slider)
			vbox.addLayout(hbox)
		# Liste fichier dans combobox
		if self.LISTW :
			hbox = QHBoxLayout()
			hbox.addWidget(self.listFichiers)
			vbox.addLayout(hbox)

		mhbox.addLayout(vbox)
		self.setLayout(mhbox)

		#=== connexion des widgets à des fonctions ===#

		if Mplayer.REVENIR in choixWidget:
			self.connect(self.bout_revenir, SIGNAL('clicked()'), SLOT('close()'))
		if Mplayer.PARCOURIR in choixWidget:
			self.connect(self.bout_ouvVideo, SIGNAL('clicked()'), self.ouvrirVideo)
		if Mplayer.PRECEDENT_SUIVANT in choixWidget:
			self.connect(self.bout_prec, SIGNAL('clicked()'), self.precedent)
			self.connect(self.bout_suivant, SIGNAL('clicked()'), self.suivant)
		#Ajouté le 08/11/2009 - Liste des fichiers dans une combobox
		if self.LISTW :
			self.connect(self.listFichiers, SIGNAL('currentIndexChanged(int)'), self.changeVideo)
		self.connect(self.bout_LectPause, SIGNAL('clicked()'), self.lectPause)
		self.connect(self.bout_Arret, SIGNAL('clicked()'), self.arretMPlayer)
		self.connect(self.mplayerProcess, SIGNAL('readyReadStandardOutput()'), self.recupSortie)
		self.connect(self.mplayerProcess, SIGNAL('finished(int,QProcess::ExitStatus)'), self.finVideo)
		self.connect(self.timer, SIGNAL('timeout()'), self.sonderTempsActuel)
		self.connect(self.slider, SIGNAL('sliderMoved(int)'), self.changerTempsCurseur)
		self.connect(self.cibleVideo, SIGNAL('changeSize'), self.sizeMplayer)
                if Mplayer.RATIO in choixWidget :
                    self.connect(self.choicenorm, SIGNAL("clicked(bool)"), self.defRatio)
                    self.connect(self.choicewide, SIGNAL("clicked(bool)"), self.defRatio)
                    self.connect(self.choiceone, SIGNAL("clicked(bool)"), self.defRatio)

	def setListeVideo(self) :
		self.referenceVideo = []
		self.listFichiers.clear()
		for vid in self.listeVideos :
			self.referenceVideo.append(vid)
			self.listFichiers.addItem(os.path.basename(vid))
		if self.listeVideos.__len__() > 1 :
			self.listFichiers.show()

	def setAudio(self,au) :
		if au :
			self.cibleVideo.hide()
                        if "conf" in self.__dict__ :
			    self.conf.hide()
		else :
			self.cibleVideo.show()
                        if "conf" in self.__dict__ :
                            self.conf.show()
	def changeVideo(self, index) :
		self.arretMPlayer()
		if index >= 0 : # Condition ajoutée pour éviter une erreure de dépassement de range dans la liste.
			self.listeVideos = self.referenceVideo[index]
			self.listFichiers.setCurrentIndex(index)

	def defRatio(self, state=0) :
		if state :
			if self.choicenorm.isChecked() :
				self.setRatio(4.0/3.0)
			if self.choicewide.isChecked() :
				self.setRatio(16.0/9.0)
			if self.choiceone.isChecked() :
				try :
					dim=getVideoSize(unicode(self.listeVideos[0]))
					self.setRatio(dim[0]/dim[1])
				except :
					None
			self.defRatio()
		else :
			self.adjustSize()

	def setRatio(self,ratio) :
		self.ratio = ratio
		self.sizeMplayer()

	def changeRatio(self,video) :
		rv = getVideoRatio(video)
		if rv[0]==0.0 and type(rv[1])==float :
			rat = rv[1]
		else :
			rat = rv[0]

		if rat > 1.7 :
                        if "choicewide" in self.__dict__ :
                            self.choicewide.setChecked(True)
			self.setRatio(16.0/9.0)
		elif rat > 1.3 and rat <= 1.7 :
                        if "choicenorm" in self.__dict__ :
                            self.choicenorm.setChecked(True)
			self.setRatio(4.0/3.0)
		elif rat < 1.3 and rat != 0.0 :
                        if "choiceone" in self.__dict__ :
                            self.choiceone.setChecked(True)
			dim=getVideoSize(video)
			self.setRatio(dim[0]/dim[1])
		else :
                        if "choicenorm" in self.__dict__ :
                            self.choicenorm.setChecked(True)
			self.setRatio(4.0/3.0)

	def sizeMplayer(self) :
		self.cibleVideo.setFixedHeight(int(self.cibleVideo.width()/self.ratio))

	def ouvrirVideo(self):
		"""Ouverture de la boîte de dialogue de fichiers"""
		txt = u"Fichiers vidéo"
		if self.cheminPourBoutonParcourir:
			chemin = self.cheminPourBoutonParcourir

		else:
			try:
				chemin = EkdConfig.get('general','video_input_path').decode("UTF8")
			except:
				chemin = os.path.expanduser('~')

		liste=QFileDialog.getOpenFileNames(None, u"Ouvrir", chemin, "%s (*.avi *.mpg *.mpeg *.mjpeg *.flv *.mp4 *.ogg *.vob *.mov *.wmv *.3gp *.h264)\n*" %txt)
		if not liste: return
		self.listeVideos = liste
		self.changeRatio(unicode(self.listeVideos[0]))

		chemin = unicode(self.listeVideos[0])
		EkdConfig.set('general','video_input_path',os.path.dirname(chemin).encode("UTF8"))

	def setVideos(self, videos) :
		'''Définie proprement la liste des vidéos à jouer'''
		if type(videos) != list :
			self.listeVideos = [videos]
		else :
			self.listeVideos = videos
		if self.LISTW and videos.__len__() > 1 :
			self.setListeVideo()
		elif self.LISTW :
			self.listFichiers.hide()

	def demarrerMPlayer(self):
		"""démarrage de mplayer avec les arguments choisis"""
		if self.estLue:
			return True

		args = QStringList()	# Liste Qt qui contiendra les options de mplayer
					# Ajout d'options à liste: args << "-option"

		# mplayer fonctionnera comme un terminal dans ce script
		args << "-slave"
		# on ne veut pas avoir des commentaires sans grand intérêt
		args << "-quiet"

		# Sous linux, aucun driver n'a été nécessaire et pas de manip pour Wid :)
		if self.systeme=='posix':
			# try - except?
			# la fenêtre de mplayer restera attaché à la fenêtre
			# wid prend en valeur le nombre identifiant le widget (celui qui contiendra la vidéo)
			args << "-wid" << QString.number(self.cibleVideo.winId()) # Objet QString car args est une liste de ch de caractères
			settings = QSettings()
			videoOutput = settings.value("vo", QVariant('')).toString()
			if videoOutput:
				args << '-vo' << videoOutput

		# Sous windows
		else:
			# reinterpret_cast<qlonglong> obligatoire, winId() ne se laissant pas convertir gentiment ;)
			args << "-wid" << self.cibleVideo.winId().__hex__()
			args << "-vo" << "directx:noaccel"
			#args << "-vo" << "gl" # alternative

		# chemin de la vidéo
		args << self.listeVideos

		if PYQT_VERSION_STR >= "4.1.0":
			# mode de canal: on fusionne le canal de sortie normal (stdout) et celui des erreurs (stderr)
			self.mplayerProcess.setProcessChannelMode(QProcess.MergedChannels)
		# démarrage de mplayer (en tenant compte des arguments définis ci-dessus)
		# comme un nouveau processus
		self.mplayerProcess.start(self.cheminMPlayer, args)
		# au cas où mplayer ne démarrerait pas au bout de 3 sec (ex. problème de codec)
		if not self.mplayerProcess.waitForStarted(3000):
			QMessageBox.critical(self, u"Avertissement", u"Bogue au lancement de la vidéo avec mplayer")
			return False

		# donne le temps toutes les x secondes
		self.timer.start(self.dureeTimer)

		self.estLue = True

		return True

	def recupSortie(self):
		"""récupère les lignes d'information émises par QProcess (mplayerProcess) et en tire les conséquences"""
		while self.mplayerProcess.canReadLine(): # renvoie True si une ligne complète peut être lue à partir du système
			# stocker l'ensemble des bits d'une ligne
			tampon=QByteArray(self.mplayerProcess.readLine()) # readline: lit une ligne ascii à partir du système

			# On vérifie si on a eu des réponses
			if tampon.startsWith("Playing"):
				# On récupère les infos de base ('$ mplayer -input cmdlist' pour avoir la liste complète - file:///usr/share/doc/mplayer-doc/tech/slave.txt.gz pour plus de détails)
				self.mplayerProcess.write("get_video_resolution\n") # récupère la résolution de la vidéo
				self.mplayerProcess.write("get_time_length\n")
				# Nouveau fichier chargé -> on récupère son nom
				ind = tampon.length() - 2 # suppression du '.' à la fin
				tampon.remove(ind,ind)
				tampon.remove(0, 8) # vire Playing
				tampon.replace(QByteArray("\n"), QByteArray(""))
				tampon.replace(QByteArray("\r"), QByteArray(""))
				try:
					# Tour de passe-passe pour ne pas avoir de problème d'accents

					# Condition pour détection windows
					if os.name == 'nt':
						self.fichierCourant[1]=unicode(QString(tampon))
					# Condition pour détection Linux ou MacOSX
					elif os.name in ['posix', 'mac']:
						self.fichierCourant[1]=unicode(QString(tampon)).encode("Latin1").decode("UTF8")
				except UnicodeEncodeError, e:
					debug(e)
					self.fichierCourant[1]="?"
				self.cibleVideo.setToolTip(self.fichierCourant[1])
				if self.barreTaches is not None:
					self.barreTaches.showMessage(self.fichierCourant[1])

			# réponse à get_video_resolution : ANS_VIDEO_RESOLUTION='<width> x <height>'
			if tampon.startsWith("ANS_VIDEO_RESOLUTION"): # retourne True si l'ensemble de bits démarre avec "..."
				debug("tampon : %s" % tampon) # ex. -> ANS_VIDEO_RESOLUTION='352 x 288'
				tampon.remove(0, 21) # suppression des 21 1er caract -> '352 x 288'
				tampon.replace(QByteArray("'"), QByteArray("")) # -> 352 x 288
				tampon.replace(QByteArray(" "), QByteArray("")) # -> 352x288
				tampon.replace(QByteArray("\n"), QByteArray("")) # -> 352x288 # retour chariot unix
				tampon.replace(QByteArray("\r"), QByteArray("")) # -> 352x288 # retour chariot windows
				#print "-----tampon.indexOf('x') :", tampon.indexOf('x'), type(tampon.indexOf('x'))
				sepIndex = tampon.indexOf('x') # récupère la position de 'x' # 3 <type 'int'>
				#print "-----tampon.left(sepIndex).toInt():", tampon.left(sepIndex).toInt(), type(tampon.left(sepIndex).toInt())
				resX = tampon.left(sepIndex).toInt()[0] # -> 352 # (352, True) <type 'tuple'>
				#print "-----tampon.mid(sepIndex+1).toInt() :", tampon.mid(sepIndex+1).toInt(), type(tampon.mid(sepIndex+1).toInt())
				resY = tampon.mid(sepIndex+1).toInt()[0] # -> 288 # (288, True) <type 'tuple'>

				# on définit les nouvelles dimensions de l'image du widget-mplayer.
				# try pour éviter les bogues sur les fichiers audio (sans dimension d'image)!!!
				#try:
				if resX!=0 or resY!=0:
					debug( "ratio : %s - %s" % (self.ratio, type(self.ratio)))
				else:
					debug("fichier audio")

			# réponse à get_time_length : ANS_LENGTH=xx.yy
			elif tampon.startsWith("ANS_LENGTH"):
				debug("tampon : %s" % tampon) # -> ANS_LENGTH=279.38
				tampon.remove(0, 11) # vire ANS_LENGTH=
				tampon.replace(QByteArray("'"), QByteArray(""))
				tampon.replace(QByteArray(" "), QByteArray(""))
				tampon.replace(QByteArray("\n"), QByteArray(""))
				tampon.replace(QByteArray("\r"), QByteArray("")) # -> 279.38
				#print "-----tampon.toFloat() :", tampon.toFloat(), type(tampon.toFloat())
				tempsMax = tampon.toFloat()[0] # (279.3800048828125, True) <type 'tuple'>
				self.dureeVideo = tempsMax
				## Modifié le 28/05/2009 : On augmente la précision du slider
				#self.slider.setMaximum(tempsMax) # déf du domaine de valeur du curseur
				self.slider.setMaximum(tempsMax*self.echelle)

				# ATTENTION J'AI COMMENTE CETTE LIGNE !!!
				#self.slider.setMaximum(tempsMax)

			# réponse à get_time_pos : ANS_TIME_POSITION=xx.y
			elif tampon.startsWith("ANS_TIME_POSITION"):
				#print "tampon :",tampon # -> ANS_TIME_POSITION=1.4 (temps courant)
				tampon.remove(0, 18) # vire ANS_TIME_POSITION=
				tampon.replace(QByteArray("'"), QByteArray(""))
				tampon.replace(QByteArray(" "), QByteArray(""))
				tampon.replace(QByteArray("\n"), QByteArray(""))
				tampon.replace(QByteArray("\r"), QByteArray(""))
				#print "-----tampon.toFloat() :", tampon.toFloat(), type(tampon.toFloat())
				tempsCourant = tampon.toFloat()[0] # (1.3999999761581421, True) <type 'tuple'>
				# récupération du temps courant: utile dans certains cadres
				self.temps = tempsCourant
				# Programmer un arrêt. Utile pour les aperçus
				temps = float("%.1f" %self.temps)
				if self.debutFin!=(0,0) and self.debutFin[1]==temps:
					self.arretMPlayer()
					return
				self.slider.setValue(tempsCourant*self.echelle)
				#############################################################################
				self.changerTempsChrono(tempsCourant) # modifier le chrono du bouton


	def sonderTempsActuel(self):
		"""envoie le temps correspondant à la position de la vidéo dans le tampon"""
		self.mplayerProcess.write("get_time_pos\n")

	def changerTempsCurseur(self, pos):
		"""change la partie de la vidéo qui sera lue"""
		# on arrête le temps pendant le changement de position de la vidéo
		# sinon le curseur ne bouge plus
		self.timer.stop()
		self.mplayerProcess.write("seek " + str(pos/self.echelle) + " 2\n")

		self.timer.start()
		self.estLue, self.estEnPause = True, False
		self.bout_LectPause.setIcon(self.icone_pause)


	def changerTempsChrono(self,nvTemps):
		"""affichage du temps sous la forme h:mm:ss:ms dans un bouton"""
		temps0 = QTime(0, 0, 0)
		## On augemente la précision, on ajoute les milisecondes au lieu des secondes #####
		temps = temps0.addMSecs(nvTemps*self.echelle)
		###########################################################################################################
		mn = str(temps.minute()).zfill(2)
		s = str(temps.second()).zfill(2)
		ms = str(temps.msec()).zfill(3)
		chrono = str(temps.hour())+':'+mn+':'+s+':'+ms
		self.tempsChrono.num = chrono
		self.tempsChrono.repaint()
		###########################################################################################################


	def precedent(self):
		"""affiche la vidéo précédente"""
		if self.estLue:
			self.mplayerProcess.write("pt_step -1\n")
			self.estEnPause = False
			self.bout_LectPause.setIcon(self.icone_pause)


	def suivant(self):
		"""affiche la vidéo suivante"""
		if self.estLue:
			self.mplayerProcess.write("pt_step 1\n")
			self.estEnPause = False
			self.bout_LectPause.setIcon(self.icone_pause)

	def initspeed(self):
		"""Réinitialise la vitesse de lecture"""
		if self.estLue:
			self.mplayerProcess.write("speed_set 1\n")

	def speedup(self):
		"""Augmente la vitesse de lecture"""
		if self.estLue:
			self.mplayerProcess.write("speed_incr 0.1\n")

	def speeddown(self):
		"""Diminue la vitesse de lecture"""
		if self.estLue:
			self.mplayerProcess.write("speed_incr -0.1\n")

	def lectPause(self):
		"""lecture/pause de la vidéo avec mplayer"""
		if not self.estLue:
			if not self.demarrerMPlayer(): # lecture de la vidéo
				return # au cas où mplayer ne démarrerait pas au bout de 3 sec (ex. problème de codec)
			self.estLue, self.estEnPause = True, False
			self.bout_LectPause.setIcon(self.icone_pause)
			self.slider.setEnabled(True) # évite un bogue
			if self.debutFin!=(0,0) and self.debutFin[0]!= 0:
				self.mplayerProcess.write("seek " + str(self.debutFin[0]) + " 2\n")
		elif self.estLue and not self.estEnPause: # lecture -> pause
			self.mplayerProcess.write("pause\n")
			self.timer.stop()
			self.bout_LectPause.setIcon(self.icone_lire)
			self.slider.setEnabled(True) # évite un bogue
			self.estLue, self.estEnPause = True, True
		elif self.estLue and self.estEnPause: # pause -> lecture
			# prévoir le cas où mplayer ne se mettrait pas en pause au bout de 3 sec
			self.timer.start()
			self.bout_LectPause.setIcon(self.icone_pause)
			self.slider.setEnabled(True) # évite un bogue
			self.estLue, self.estEnPause = True, False


	def arretMPlayer(self):
		""""Arrete la lecture de la vidéo et réinitialise les icones et variables"""
		if self.mplayerProcess.state() == QProcess.NotRunning: # ajouté pour ne pas avoir de bogue à la fin de la lecture de la vidéo.
    			return True

		self.mplayerProcess.write("quit\n") # arrêt de la vidéo

		# au cas où mplayer ne s'arrêterait pas au bout de 3 sec
		if not self.mplayerProcess.waitForFinished(3000):
			QMessageBox.critical(self, u"Avertissement", u"Bogue à la tentative d'arrêt de la vidéo avec mplayer")
			return False

		self.slider.setEnabled(False) # évite un bogue
		#self.slider.setEnabled(True)

		#self.tempsChrono.num = "0:00:00"
		self.tempsChrono.raz()

		self.tempsChrono.repaint()
		self.slider.setValue(0)
		self.estLue, self.estEnPause = False, False
		self.bout_LectPause.setIcon(self.icone_lire)
		return True

	def finVideo(self, statutDeSortie, codeSortie):
		"""On change certaines variables à la fin de vidéo"""
		# d'après ce que j'ai compris: récupération du statut de sortie (0: normal ; 1: crash)
		#  pas de récupération du code de sortie (de toute façon je vois pas trop à quoi il servirait)
		if statutDeSortie==1:
			debug(u"Crash de mplayer lors de la fin de la lecture de la vidéo")
		self.estLue, self.estEnPause = False, False
		self.bout_LectPause.setIcon(self.icone_lire)
		self.timer.stop()
		self.slider.setEnabled(False) # évite un bogue
		#self.slider.setEnabled(True)
		self.cibleVideo.setToolTip(self.fichierCourant[0])
		if self.barreTaches is not None:
			self.barreTaches.clearMessage()


class MetaMPlayer(QDialog):
	def __init__(self, mplayer1=None, mplayer2=None):
		"Boite de dalogue de comparaison de 2 vidéos via mplayer"
		QDialog.__init__(self)

		self.setWindowTitle(_(u"Comparateur de vidéos"))
                #On réduit la marge pour gagner de l'espace
                self.setContentsMargins(0,0,0,0)

		# paramètres des boutons-icones
		iconTaille=32
		flat=1

		self.icone_lire=QIcon("Icones" + os.sep + "player_play.png")
		self.icone_pause=QIcon("Icones" + os.sep + "player_pause.png")
		self.icone_arret=QIcon("Icones" + os.sep + "player_stop.png")

		self.bout_ouvVideo = QPushButton(u"Parcourir...")

		self.bout_LectPause = self.bout_LectPause2 = QPushButton(self.icone_lire,"")

		self.bout_LectPause.setIconSize(QSize(iconTaille, iconTaille))
		self.bout_LectPause.setFlat(flat)

		self.bout_Arret = QPushButton(self.icone_arret,"")
		self.bout_Arret.setIconSize(QSize(iconTaille, iconTaille))
		self.bout_Arret.setFlat(flat)

		vbox = QVBoxLayout(self)
                vbox.setSpacing(0)
                vbox.setMargin(0)
		hbox = QHBoxLayout()
                hbox.setSpacing(0)
		vboxG = QVBoxLayout()
                vboxG.setSpacing(0)
                vboxG.setMargin(0)
		vboxG.addWidget(QLabel(_(u"Vidéo avant traitement")),0,Qt.AlignHCenter)
		vboxG.addWidget(mplayer1)
		hbox.addLayout(vboxG,0)
		vboxD = QVBoxLayout()
                vboxD.setSpacing(0)
                vboxD.setMargin(0)
		vboxD.addWidget(QLabel(_(u"Vidéo après traitement")),0,Qt.AlignHCenter)
		vboxD.addWidget(mplayer2)
		hbox.addLayout(vboxD,0)
		vbox.addLayout(hbox)

		hbox = QHBoxLayout()
		hbox.addStretch()
                hbox.setSpacing(0)
                hbox.setMargin(0)
		hbox.addWidget(self.bout_LectPause)
		hbox.addWidget(self.bout_Arret)

		hbox.addStretch()
		vbox.addLayout(hbox)

		# Le bouton 'Revenir' a été ajouté car il permet de fermer proprement la boîte de dialogue
		#
		boutonFermer = QPushButton(_(u"Revenir"))
		boutonFermer.setIcon(QIcon("Icones" + os.sep + "revenir.png"))
		self.connect(boutonFermer, SIGNAL('clicked()'), SLOT('close()'))
		vbox.addWidget(boutonFermer)


		if mplayer1!=None and mplayer2!=None:
			self.lier2MPlayer(mplayer1, mplayer2)

	def connecter1MPlayer(self, mplayer):
		"connexion d'un mplayer"
		self.connect(self.bout_ouvVideo, SIGNAL('clicked()'), mplayer.ouvrirVideo)
		self.connect(self.bout_LectPause, SIGNAL('clicked()'), mplayer.lectPause)
		self.connect(self.bout_Arret, SIGNAL('clicked()'), mplayer.arretMPlayer)

	def lier2MPlayer(self, mplayer1, mplayer2):
		" actions "
		self.connecter1MPlayer(mplayer1)
		self.connecter1MPlayer(mplayer2)
		if mplayer1.LISTW and mplayer2.LISTW :
			mplayer1.connect(mplayer1.listFichiers, SIGNAL('currentIndexChanged(int)'), mplayer2.changeVideo)
			mplayer2.connect(mplayer2.listFichiers, SIGNAL('currentIndexChanged(int)'), mplayer1.changeVideo)
