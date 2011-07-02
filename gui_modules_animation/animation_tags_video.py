#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from gui_modules_animation.animation_base_encodageFiltre import Base_EncodageFiltre
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_common.mencoder_gui import WidgetMEncoder
from gui_modules_common.EkdWidgets import EkdSaveDialog
from gui_modules_image.selectWidget import SelectWidget

from gui_modules_animation.infoVideo import infovideo

from moteur_modules_animation.tags import Tags
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Animation_TagsVideo(Base) :
	"Cadre de Animation -> Encodage -> Gestion AVCHD. But: encodages spécifiques au départ du format AVCHD haute définition (Caméra digitale HD)"

	def __init__(self):

		#=== Variable de configuration ===#
		self.config=EkdConfig
		# Identifiant de la classe
		self.idSection = "animation_tag_video" # idSection à modifier lorsqu'il y aura des données dans la config.

		super(Animation_TagsVideo, self).__init__('hbox', titre=_(u"Tags Vidéo"))
		
		self.printSection()

		# Customisation de l'interface
		# 1. Onglet sources
		self.afficheurVideoSource=SelectWidget(extensions = ["*.avi", "*.mp4", "*.mpg", "*.mpeg", "*.flv"], mode="texte", video = True)
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
		
		self.ligne = {}
                # Présentation ------------------------------------
		layoutPres = QHBoxLayout()
                titre = QLabel("<h2>" + _(u"Tags contenus dans la vidéo :") + "</h2>")
		layoutPres.addWidget(titre)
		self.layoutReglage.addLayout(layoutPres)
                # Les Tags ----------------------------------------
		self.layoutTags = QVBoxLayout()
                # Un bouton d'ajout et de suppression de tags
                self.layoutButton = QHBoxLayout()
                self.buttonAdd = QPushButton(_(u"Ajouter un tag"))
                self.buttonDel = QPushButton(_(u"Supprimer un tag"))
                self.labelWarn = QLabel(_(u"Veuillez charger au moins un fichier."))
                # Menu déroulant pour chaque pour chaque bouton
                self.menuDel = QMenu()
                self.buttonDel.setMenu(self.menuDel)
                self.menuAdd = QMenu()
                self.buttonAdd.setMenu(self.menuAdd)

		self.connect(self.buttonAdd, SIGNAL("clicked()"), self.buttonAdd.showMenu)
		#self.connect(self.buttonAdd, SIGNAL("clicked()"), self.showAddMenu)
		self.connect(self.buttonDel, SIGNAL("clicked()"), self.buttonDel.showMenu)
		#self.connect(self.buttonDel, SIGNAL("clicked()"), self.showDelMenu)
		self.connect(self.menuAdd, SIGNAL("aboutToHide()"), self.setToAdd)
		self.connect(self.menuDel, SIGNAL("aboutToHide()"), self.setToDel)

                self.layoutButton.addWidget(self.buttonAdd)
                self.layoutButton.addWidget(self.buttonDel)
                self.layoutButton.addWidget(self.labelWarn)
                ## Par défaut, on ne voit pas les boutons, ils seront activé si un fichier est chargé
                self.buttonAdd.hide()
                self.buttonDel.hide()
                self.labelWarn.show()
                self.layoutButton.addStretch()

		self.layoutReglage.addLayout(self.layoutTags)
		self.layoutReglage.addLayout(self.layoutButton)
		self.layoutReglage.addStretch()

		## On charge les options depuis EkdConfig
		self.loadOptions()
		
		##
		self.add(groupReglage, _(u"Réglages"))

		# 4 Onglet info.
		self.addLog()
		
        def setToAdd(self):
                self.toAdd = self.menuAdd.activeAction()
        def setToDel(self):
                self.toDel = self.menuDel.activeAction()

        def addTagsEdit(self, label, value):
                """Fonction d'ajout d'un champ de modification d'un tag"""
		layoutTag = QHBoxLayout()
		#
		lab = QLabel(_(u"%s :"% label))
                lab.setFixedWidth(90)
		layoutTag.addWidget(lab)
		#
                num = len(self.ligne)
		self.ligne[label] = QLineEdit()
		self.ligne[label].setMaxLength(80)
		self.ligne[label].setText(value)
		self.ligne[label].setToolTip(_(u"Vous n'avez droit ici qu'à maximum 80 caractères. <b>Au delà de cette taille, plus aucun caractère ne s'affichera !</b>"))
		layoutTag.addWidget(self.ligne[label])
		# 
		self.layoutTags.addLayout(layoutTag)
		#
		#self.connect(self.ligne[label], SIGNAL("textChanged(const QString&)"), self.updateLigne)
		self.connect(self.ligne[label], SIGNAL("editingFinished()"), self.updateLigne)
		
        def updateLigne(self):
                for k in self.tags.get_tags().keys() :
                    self.tags.setTag(k, self.ligne[k].text())


        def clearTags(self):
                """Supprimme tous les Tags"""
                def deleteItems(layout):
                    if layout is not None:
                        while layout.count():
                            item = layout.takeAt(0)
                            widget = item.widget()
                            if widget is not None:
                                widget.deleteLater()
                            else:
                                deleteItems(item.layout())
                deleteItems(self.layoutTags)

        def showAddMenu(self):
                #print "Visu du menu Add"
                self.buttonAdd.showMenu()

        def showDelMenu(self):
                #print "Visu du menu Del"
                self.buttonDel.showMenu()

        def tagDel(self):
                #print "Deleting %s" % self.toDel.text()
                self.clearTags()
                self.tags.delTag("%s" % self.toDel.text())
                self.refreshTags()

        def tagAdd(self):
                #print "Adding %s" % self.toAdd.text()
                self.clearTags()
                self.tags.addTag("%s" % self.toAdd.text(), "Exemple")
                self.refreshTags()

        def refreshTags(self):
                self.menuDel.clear()
                self.menuAdd.clear()
                for tag in self.tags.get_tags().keys() :
                    ## On ajoute cette condition si on veut restreindre
                    ## la visualisation des tags à seulement ceux gérés
                    ## par mencoder.
                    ## Sans cette condition, tous les tags sont affichés
                    if tag in Tags.DEFAULT_TAGS:
                        self.addTagsEdit(tag, self.tags[tag])
                        self.menuDel.addAction("%s" % tag, self.tagDel)
                for t in Tags.DEFAULT_TAGS :
                    if not t in self.tags.get_tags().keys() :
                        self.menuAdd.addAction("%s" % t, self.tagAdd)

	def getFile(self):
	
		# Choisir getFile à la place de getFiles
		#self.chemin = self.afficheurVideoSource.getFiles()
		
		# Chemin de la vidéo sélectionnée
		self.chemin = self.afficheurVideoSource.getFile()

                if self.chemin :
                    self.buttonAdd.show()
                    self.buttonDel.show()
                    self.labelWarn.hide()
                else:
                    ## Par défaut, on ne voit pas les boutons, ils seront activé si un fichier est chargé
                    self.buttonAdd.hide()
                    self.buttonDel.hide()
                    self.labelWarn.show()

		#print 'Chemin', self.chemin
		EkdPrint('Chemin ' + self.chemin)
		
                # Clear all TagsEdit
                self.clearTags()

		# A partir du moment où au moins une vidéo a 
		# été chargée, le bouton Appliquer devient actif
		self.boutApp.setEnabled(True)

                self.moteurInfosTags()
                #print 'Tags : %s' % self.tags
                self.refreshTags()

		#self.emit(SIGNAL("loaded"))
		return self.chemin
		
	
	def moteurInfosTags(self):
	
		# Chemin de la vidéo sélectionnée
		self.chemin = self.afficheurVideoSource.getFile()
		
                self.tags = Tags(self.chemin)

		

	def appliquer(self, nomSortie=None, ouvert=1):
		"Appel du moteur du cadre"
		
		if not nomSortie:
			#chemin = self.getFile()
			chemin = self.chemin
			
			self.suffix_sortie = os.path.splitext(chemin)[1]
			
			# Suffix du codec actif
                        saveDialog = EkdSaveDialog(self, mode="video", suffix=self.suffix_sortie, title=_(u"Sauver"))
			self.cheminFichierEnregistrerVideo = saveDialog.getFile()
			
		else: # module séquentiel
			self.cheminFichierEnregistrerVideo = nomSortie

		if not self.cheminFichierEnregistrerVideo:
			return
		
		# Appel de la classe
#		try:
                mencoder = WidgetMEncoder('tag_video', chemin, self.cheminFichierEnregistrerVideo, valeurNum = self.tags.get_tags(), laisserOuvert=ouvert)
                mencoder.setWindowTitle(_(u"Créer des tags vidéo"))
                mencoder.exec_()
#		except:
#			messageErrTagVid=QMessageBox(self)
#			messageErrTagVid.setText(_(u"Un problème est survenu lors de l'exécution de Mencoder"))
#			messageErrTagVid.setWindowTitle(_(u"Erreur"))
#			messageErrTagVid.setIcon(QMessageBox.Warning)
#			messageErrTagVid.exec_()
#			return

		### Information à l'utilisateur
		self.lstFichiersSortie = self.cheminFichierEnregistrerVideo
		self.infoLog(None, chemin, None, self.cheminFichierEnregistrerVideo)
	

	def afficherAide(self):
		"Boîte de dialogue de l'aide du cadre"

		super( Animation_TagsVideo,self).afficherAide(_(u"<p><b>Vous pouvez ici apposer des tags vidéo. Imaginez vous ayez une création vidéo et que vous voulez la mettre sur internet et en même temps vous voulez bien spécifier (et non par une signature ou par un logo en bas de la vidéo) que c'est bien la votre (par exemple par un copyright), ... et bien c'est possible, c'est là qu'interviennent les tags vidéo.</b></p><p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher la/les vidéo(s). Si vous voulez sélectionner plusieurs vidéos d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos vidéos), cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès lors sélectionner une vidéo dans la liste et la visionner (par le bouton juste à la droite de cette liste), vous noterez que vous pouvez visionner la vidéo en quatre tiers, en seize neuvième ou avec les proportions d'origine de la vidéo (w;h). De même si vous le désirez, vous pouvez obtenir des informations complètes sur la vidéo sélectionnée, et ce par le bouton <b>'Infos'</b> (en bas).</p><p>Dans l'onglet <b>'Réglages'</b> sélectionnez les entrées (c'est à dire les tags) dans la liste déroulante <b>'Ajouter un tag'</b> (c'est à dire Title, Artist, Genre, Subject, Copyright et Comments), une fois les entrées ajoutées renseignez les différents tags dans les champs de texte correspondants.</p><p>Une fois tout ceci fait, cliquez sur le bouton <b>'Appliquer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b> et attendez le temps du traitement.</p><p>L'onglet <b>'Infos'</b> vous permet de voir les vidéos chargées (avec leurs chemins exacts) avant et après conversion.</p>"))


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
		'''
		# On charge les différentes variables necessaire au widget

		# Sert maintenant à imprimer les infos des tags
		'''
		#print "Pas d'options à afficher"
		EkdPrint(u"Pas d'option à afficher")


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
