#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, shutil, glob
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_image.image_base import Base
#### v--- Pas très propre.... Il vaudrait mieu différencier chaque base par un nom unique
BaseImg = Base # pour différencier les 2 bases
from gui_modules_common.gui_base import Base
from moteur_modules_animation.mplayer import Mplayer
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from gui_modules_lecture.lecture_image import Lecture_VisionImage
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
###########################################################################################
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

class Animation_ConvertirUneAnimEnImg(Base):
	# ----------------------------------------------------------------------------------------
	# Cadre accueillant les widgets de : Animation >> Séparer le flux vidéo et le flux audio
	# ----------------------------------------------------------------------------------------

	def __init__(self, statusBar, geometry):
		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------

		#=== Variable de configuration ===#
		self.config=EkdConfig

		self.baseImg = BaseImg() # module de image
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		#=== tout sera mis dans une boîte verticale ===#
		vbox=QVBoxLayout()

		#=== Identifiant de la classe ===#
		self.idSection = "animation_convertir_une_video_en_images"

		super(Animation_ConvertirUneAnimEnImg, self).__init__(titre=_(u"Conversion d'une vidéo en images"))
		self.printSection()

		######## Gestion de la nouvelle interface de chargement #######
		## -------------------------------------------------------------------
		## on utilise le selecteur d'image pour les vidéos
		from gui_modules_image.selectWidget import SelectWidget
		# Là où on naviguera entre les fichiers
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.mpg", "*.mpeg", "*.mjpeg", "*.flv", "*.mp4", "*.h264", "*.dv", "*.vob"], mode="texte", video = True)
		###################################################################################
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)
		## -------------------------------------------------------------------

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.


		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)

		# Est-ce que des images ont été converties et qu'elles n'ont pas encore été montrées?
		# Marche aussi quand la conversion a été arrêté avant la fin de la 1ère image
		self.conversionImg = 0

		#=== Accès à la barre des tâches ===#
		# On ne passe pas tout le parent, mais juste ce dont on a besoin
		self.statusBar = statusBar

		# -------------------------------------------------------------------
		# Boîte de groupe : "Fichier vidéo source"
		# -------------------------------------------------------------------
		self.afficheurImgDestination=Lecture_VisionImage(self.statusBar)
		#####################################################################################################

		self.listeImgDestin = []

		#----------
		# Onglets
		#----------
		self.dicoTab = {}

		self.add(self.afficheurImgDestination, _(u"Visualisation"))

		self.addLog()


	def fctTab(self):
		"Affichage d'une ou plusieurs images converties"

		# Cela ne concerne que l'onglet de visualisation des images après leur conversion
		# Affichage si on sauvegarde par le bouton Appliquer et sauver
		#print "La conversion vient d'avoir lieu -> affichage des images du lot de destination"
		EkdPrint(u"La conversion vient d'avoir lieu -> affichage des images du lot de destination")
		cheminImages = os.path.dirname(self.listeImgDestin[0])
		liste = []
		for fichier in self.listeImgDestin:
			liste.append(os.path.basename(fichier))
		self.afficheurImgDestination.updateImages(liste, cheminImages)

		self.conversionImg = 0

		####################################################################
		# Car erreur: Traceback (most recent call last): ... KeyError: 'images'
		# Affichage (après conversion) de l'onglet contenant les images
		####################################################################

		# On libere la memoire
		del cheminImages, liste, fichier


	def ouvrirSource(self, nomEntree=None):
		"""Récupération du chemin de la vidéo sélectionnée et activation de certains widgets"""

		chemin = self.recupSource(nomEntree)

		if not chemin: return
		self.ligneEditionSource.setText(chemin)

		self.boutApp.setEnabled(True)

		self.mplayer.setEnabled(True)
		self.mplayer.listeVideos = [chemin]

		self.tab.setCurrentIndex(self.dicoTab['video'])

		# On libere la memoire
		del chemin


	def getFile(self):
		'''
		# On utilise la nouvelle interface de récupération des vidéos
		Récupération de la vidéo source selectionnée
		'''
		self.chemin = self.afficheurVideoSource.getFile()
		self.boutApp.setEnabled(True)

		self.boutApp.setEnabled(True)
		if self.idSection == "animation_filtresvideo":
			self.boutApercu.setEnabled(True)
			self.filtreDecouper.setButtonEnabled(True)
		# On emet un signal quand le fichier est chargé
		self.emit(SIGNAL("loaded"))
		return self.chemin
	###################################################################################


	def appliquer(self, nomSortie=None, ouvert=1):
		""" Appelle la boite de dialogue de sélection de fichier à sauver et appel de la fonction de conversion d'une vidéo en images """

		#=== Détermination des chemins d'entrée et sortie ===#
		chemin = self.getFile()

		if not nomSortie:
			suffix=""
                        saveDialog = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"),multiple=True)
			cheminFichierEnregistrerVideo = saveDialog.getFile()

		else: # module séquentiel
			cheminFichierEnregistrerVideo = nomSortie

		if not cheminFichierEnregistrerVideo: return
		###################################################################################

		# Préfixe des images
		prefixeImg=os.path.basename(cheminFichierEnregistrerVideo)

		# Chemin du répertoire de sortie des images
		cheminRepDestination = os.path.dirname(cheminFichierEnregistrerVideo) + os.sep + os.path.basename(cheminFichierEnregistrerVideo)

		cheminVideoSource=unicode(self.getFile())
		###################################################################################
		try:
			#### la conversion de vidéo en images est maintenant gérée par FFmpeg #####
                        ffmpeg = WidgetFFmpeg('jpeg', cheminVideoSource, cheminRepDestination, laisserOuvert=ouvert)
                        ffmpeg.setWindowTitle(_(u"Convertir une animation en images"))
                        ffmpeg.exec_()
                        ##################################################################################################

		except :
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"Problème lors de la conversion d'une vidéo en images (ffmpeg) %s") % e)
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Warning)
			messageErreur.exec_()
			return

                imgDep=glob.glob(cheminRepDestination+'*.png')

		imgDep.sort()

                # Nettoyage ... insertion des images dans la liste de visualisation
               	self.listeImgDestin=[]
		for parc_1 in imgDep:
			# Condition pour détection windows
			if os.name == 'nt':
                        	if '\\' in parc_1:
                                	self.listeImgDestin.append(parc_1.replace('\\', '/'))
			# Condition pour détection Linux ou MacOSX
			elif os.name in ['posix', 'mac']:
				self.listeImgDestin.append(parc_1)

		# Affichage des images après traitement (appel de la fonction fctTab)
		self.conversionImg = 1
		self.fctTab()
		### Information à l'utilisateur
		self.infoLog(None, cheminVideoSource, None, self.listeImgDestin)

		return self.listeImgDestin # module séquentiel

		# ATTENTION IL FAUT AJOUTER CECI NE PAS OUBLIER !!!
		# La liste pour l'affichage des images ds l'interface est
		# vidée pour que les images affichées ne s'amoncellent pas
		# si plusieurs rendus à la suite
		self.listeImgDestin=[]

		# On libere la memoire
		del nomSortie, rep, chemin, prefixeImg, cheminRepDestination, cheminRepDestination, cheminVideoSource, commande, mencoder, listeFichiers, nomFichier


	def sequentiel(self, entree, sortie, ouvert=0):
		"""Utile dans le module du même nom. Applique les opérations de la classe. Retourne le vrai nom du fichier de sortie"""
		self.ouvrirSource(entree)
		return self.appliquer(sortie, ouvert)


	def sequentielReglage(self):
		"""Utile dans le module du même nom. Récupère le widget de réglage associé à l'identifiant donné en 1er argument. Retourne l'instance du widget de réglage"""
		groupReglage =  QGroupBox(_(u"Réglages: convertir une animation en images"))
		hbox = QHBoxLayout(groupReglage)
		hbox.addWidget(QLabel(_(u"<center>Pas de réglages ici</center>")))
		return groupReglage


	def afficherAide(self):
		""" Boîte de dialogue de l'aide """
		super( Animation_ConvertirUneAnimEnImg, self).afficherAide(_(u"<p><b>Qu’est-ce qu’une vidéo en fin de compte ?. La réponse est des images se succédant à une certaine fréquence (24 images par seconde, par exemple), que nous interprétons comme un mouvement, c’est-à-dire une image animée. Traiter une vidéo dans EKD, c’est donner à cette vidéo la possibilité de se séparer en images (le nombre d'images contenues ici sera la durée de la vidéo en secondes multiplié par son nombre d'images par seconde). C'est ce que se propose de faire cette fonction.</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Cliquez ensuite sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps de la conversion. A la fin cliquez sur le bouton <b>'Voir les informations d'encodage'</b> et fermez cette dernière fenêtre après avoir vu les informations en question.</p><p>Vous pouvez voir le résultat de la conversion en images dans l'onglet <b>Visualisation</b>. Dans cet onglet vous pouvez faire défiler les images par le bouton <b>Lancer le diaporama</b> (le bouton violet avec une flèche blanche vers la droite). Si vous faites un clic droit de la souris sur une des images résultantes, vous accédez à des paramètres vous permettant différents affichages de la dite image.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


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
