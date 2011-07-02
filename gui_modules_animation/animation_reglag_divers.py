#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from moteur_modules_animation.mplayer import Mplayer
from moteur_modules_animation.mplayer import getVideoFPS
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_image.selectWidget import SelectWidget
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Animation_ReglagesDivers(Base):
	# ----------------------------------------------------------------------------------------
	# Cadre accueillant les widgets de : Animation >> Séparer le flux vidéo et le flux audio
	# ----------------------------------------------------------------------------------------

	def __init__(self):
		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------
		vbox=QVBoxLayout()

		#=== Variable de configuration ===#
		self.config=EkdConfig

		#=== Identifiant de la classe ===#
		self.idSection = "animation_reglages_divers"

		super(Animation_ReglagesDivers, self).__init__('hbox', titre=_(u"Nombre d'images par seconde"))
		self.printSection()

		# -------------------------------------------------------------------
		# Boîte de groupe : "Fichier vidéo source"
		# -------------------------------------------------------------------
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.dv"], mode="texte", video = True)
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		#--------------------------------------------------------------------

		self.lstFichiersSortie = []
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.

		# -------------------------------------------------------------------
		# Boîte de groupe "Réglage de sortie de l'encodage"
		# -------------------------------------------------------------------
		groupReglage = QGroupBox()
		self.layoutReglage = QHBoxLayout(groupReglage)
		##=== Widget qui seront inclus dans la boite de réglage ===#

		# boite de spin
		self.spin=QSpinBox()		# self car on va récupérer la variable depuis le moteur
		self.spin.setRange(1,60) # valeur 22 par défaut
		self.connect(self.spin,SIGNAL("valueChanged(int)"),self.spinChange)

		# curseur
		self.curseur = QSlider(Qt.Horizontal)
		self.curseur.setRange(1,60)
		self.connect(self.curseur, SIGNAL("sliderMoved(int)"), self.curseurChange)

		#=== Chargement du paramètre de configuration ===#
		try:
			self.spin.setValue(int(self.config.get(self.idSection,'spin')))
		except:
			self.spin.setValue(22)

		# info
		txt2 = _(u"La vidéo source contient")
		txt3=_(u"img/s")
		self.info=QLabel("%s x %s" %(txt2,txt3))

		self.layoutReglage.addWidget(self.spin)
		self.layoutReglage.addWidget(self.curseur)
		self.layoutReglage.addWidget(self.info)

		self.add(groupReglage, _(u"Réglages"))
		self.addPreview()
		self.addLog()

	def getOutputFiles(self, typeSortie) :
		"""Fonction standard pour faire le lien avec le tampon EKD pour récupérer les fichier de sortie du type typeSortie"""
		if typeSortie == "video" :
			return self.lstFichiersSortie


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


	def spinChange(self,i):
		"""conserver le spin dans le fichier de configuration et modifie le curseur"""
		#print "nbr img/s :", i
		EkdPrint(u"nbr img/s : %d" % i)
		# sauver spin
		self.config.set(self.idSection,'spin',i)
		# sauver curseur
		self.curseur.setValue(i)


	def curseurChange(self, i):
		"""Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
		self.spin.setValue(i)


	def fctRadioSource(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""

		if bool: self.mplayer.listeVideos = [[self.chemin]]


	def fctRadioConvert(self, bool=None):
		""""Communique la vidéo appropriée à mplayer"""
		if bool: self.mplayer.listeVideos = self.lstFichiersSortie


	def nbrImgSecIni(self):
		""" Calcule et affiche le nombre d'images par seconde de la vidéo source """
		chemin = self.getFile()
		fps = 0
		if chemin:
			fps = str(int(getVideoFPS(chemin)[0]))
		if fps:
			txt1 = _(u"La vidéo source contient")
			txt2=_(u"img/s")
			self.info.setText(u"%s %s %s" %(txt1,fps,txt2))

	####################################################################################


	def ouvrirSource(self, nomEntree=None):
		"""Récupération du chemin de la vidéo sélectionnée et activation de certains widgets"""

		chemin = self.getFile()

		if not chemin: return
		self.boutApp.setEnabled(True)

		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = [chemin]
		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(False)
		self.radioConvert.setEnabled(False)
		self.boutCompare.setEnabled(False)

		self.nbrImgSecIni()


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
		# On emet un signal quand le fichier est chargé
		self.emit(SIGNAL("loaded"))
		return self.chemin
	###################################################################################


	def afficherAide(self):
		""" Boîte de dialogue de l'aide """

		super(Animation_ReglagesDivers,self).afficherAide(_(u"<p><b>Vous pouvez ici changer le nombre d'images par seconde dans une vidéo.</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> réglez le nombre d'images par seconde.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Dans l'onglet <b>'Visionner vidéo'</b> vous pouvez visionner le résultat (avant la conversion) en sélectionnant <b>'vidéo(s) source(s)'</b>, après la conversion <b>'vidéo convertie'</b> ou bien encore les deux en même temps, en cliquant sur le bouton <b>'Comparateur de vidéos'</b>.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


	def appliquer(self, nomSortie=None, ouvert=1):
		""" appelle la boite de dialogue de sélection de fichier à sauver et appel de la fonction de changement du nombre d'images par seconde """

		#=== Détermination des chemins d'entrée et sortie ===#
		chemin=unicode(self.getFile())

		if not nomSortie:
			# suffix du fichier actif
			suffix=os.path.splitext(chemin)[1]
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
			cheminFichierEnregistrerVideo = saveDialog.getFile()

		else: # module séquentiel
			cheminFichierEnregistrerVideo = nomSortie

		if not cheminFichierEnregistrerVideo: return
		###################################################################################

		nbrImgSec = str(self.spin.value())

		try:
			#### le changement de framerate est maintenant géré par FFmpeg #####
			ffmpeg = WidgetFFmpeg('idx', chemin, cheminFichierEnregistrerVideo, valeurNum=nbrImgSec, laisserOuvert=ouvert)
			ffmpeg.setWindowTitle(_(u"Réglage divers"))
			ffmpeg.exec_()
			###########################################################################################

		except:
			messageErrAnEnc=QMessageBox(self)
			messageErrAnEnc.setText(_(u"Problème lors du changement du nombre d'images par seconde (mencoder)"))
			messageErrAnEnc.setWindowTitle(_(u"Erreur"))
			messageErrAnEnc.setIcon(QMessageBox.Warning)
			messageErrAnEnc.exec_()
			return

		self.lstFichiersSortie = cheminFichierEnregistrerVideo # chemin de la vidéo convertie pour le 2ème mplayer
		self.radioSource.setEnabled(True)
		self.radioConvert.setEnabled(True)
		self.radioSource.setChecked(False)
		self.radioConvert.setChecked(True)
		self.boutCompare.setEnabled(True)
		self.infoLog(None, chemin, None, cheminFichierEnregistrerVideo)
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

	def save(self):
		'''
		Sauvegarde de la configuration de tous les objets
		'''
		self.saveFiles()
