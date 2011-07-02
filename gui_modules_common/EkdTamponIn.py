#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os

from gui_modules_image.selectWidget import SelectWidget
from gui_modules_common.EkdWidgets import EkdAide

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


### Boite de sélection de fichier multimodules ###
class EkdTamponIn(QDialog) :
    """
    EkdTamponIn permet à l'utilisateur de sélectionner les fichiers sur lesquels il veut effectuer des traitements et pouvoir directement les utiliser dans plusieurs modules sans devoir les re-sélectionner.
    """
    def __init__(self, parent) :
      super(EkdTamponIn, self).__init__(parent)
      self.parent = parent # Lien avec EKD main.
      self.setWindowTitle(QString(_(u"Réserve de fichiers sources - tampon"))) 
      self.layout = QVBoxLayout(self) # Layout vertical pour placer les éléments
      ###
      #Tab Vidéo | Tab Image | Tab Audio
      #...
      #----------------------------------------------------
      # Boutons d'action (ajouter, supprimer, importer, aide)
      self.parent = parent
      self.geometry = self.parent.frameGeometry
      # Création du TabWidget + 3 Widgets de sélection de fichiers par type
      self.tab = QTabWidget()
      self.selectVideo = SelectWidget(mode="texte", video = True)
      vidIcon = QIcon("Icones/icone_video_128.png")
      self.tab.addTab(self.selectVideo, vidIcon, _(u"Vidéo")) 
      self.selectImage = SelectWidget(mode="icone", geometrie=self.geometry)
      self.tab.addTab(self.selectImage, QIcon("Icones/icone_images_128.png"), _(u"Images")) 
      self.selectAudio = SelectWidget(mode="texte", audio = True)
      self.tab.addTab(self.selectAudio, QIcon("Icones/icone_sons_128.png"), _(u"Audio")) 
      # Ajout du TabWidget dans le layout
      self.layout.addWidget(self.tab)
      # Layout pour accueillir les boutons d'action
      HLayout = QHBoxLayout()
      # Boutons d'actions + spacer pour aligner'
      self.aide = QPushButton(QIcon("Icones/icone_aide_128.png"), _(u"Aide"))
      self.exportplus = QPushButton(QIcon("Icones"+os.sep+"icone_ajout_plus.png"), _(u"Ajouter"))
      self.exportreplace = QPushButton(QIcon("Icones"+os.sep+"icone_ajout_replace.png"), _(u"Remplacer"))
      self.importFile = QPushButton(QIcon("Icones"+os.sep+"icone_save_128.png"), _(u"Importer"))
      self.retour = QPushButton(QIcon("Icones/revenir.png"), _(u"Revenir"))
      HLayout.addWidget(self.aide)
      HLayout.addWidget(self.exportplus)
      HLayout.addWidget(self.exportreplace)
      HLayout.addWidget(self.importFile)
      HLayout.addStretch()
      HLayout.addWidget(self.retour)
      self.layout.addLayout(HLayout)

      ### TODO : Ajouter les connect des boutons (Au minimum Help, et retour, les autres, c'est à voir comment on va intégrer)
      self.connect(self.aide, SIGNAL("clicked()"), self.afficherAide)
      self.connect(self.retour, SIGNAL("clicked()"), self.hide)
      self.connect(self.exportplus, SIGNAL("clicked()"), self.copyToTab)
      self.connect(self.exportreplace, SIGNAL("clicked()"), self.copyToTabRep)
      self.connect(self.importFile, SIGNAL("clicked()"), self.copyFromOutput)


    def copyFromOutput(self) :
      """Fonction pour importer les fichiers de sortie du tableau courant"""
      if type(self.parent.tableauCourant.typeSortie) != list : # Pour standardiser le processus
        self.parent.tableauCourant.typeSortie = [self.parent.tableauCourant.typeSortie]
      for typeSortie in self.parent.tableauCourant.typeSortie : # Exploration de la liste et recherche des fichiers par type
        try :
          files = self.parent.tableauCourant.getOutputFiles(typeSortie)
          self.addOutputFiles(files, typeSortie) # Ajout des fichiers au sélecteur de fichier correspondant au type.
        except :
          #print "Fonction getOutputFiles pas encore créée dans le tableau ", self.parent.tableauCourant.idSection
	  EkdPrint(u"Fonction getOutputFiles pas encore créée dans le tableau " + str(self.parent.tableauCourant.idSection))


    def addOutputFiles(self, files, typeSortie) :
      """Fonction d'ajout des fichiers files dans le sélecteur de fichier correspondant au type typeSortie'"""
      if typeSortie == "video" :
        if type(files) != list :
          files = [files]
        if len(files) > 0 :
          self.selectVideo.setFiles(files, 1)
      elif typeSortie == "image" :
        if type(files) != list :
          files = [files]
        if len(files) > 0 :
          self.selectImage.setFiles(files, 1)
      elif typeSortie == "audio" :
        if type(files) != list :
          files = [files]
        if len(files) > 0 :
          self.selectAudio.setFiles(files, 1)
 
      
    def copyToTabRep(self) :
      self.copyToTab(append=0)

    def copyToTab(self, append=1) :
      """Fonction pour exporter les fichiers sélectionnés du tampon vers le tab source du tableau courant """
      try :
        ### Changé le 02/03/11 #############################################
	# Boîte de dilogue apparaissant pour informer l'utilisateur quand celui-ci charge des images dans le tampon
	# et que ces images ne peuvent pas être déployées pour le compositing
        if self.parent.tableauCourant.idSection == "image_image_composite":
	  reply = QMessageBox.warning(self, 'Message', _(u"Les images du tampon <b>(pour Image composite)</b> ne peuvent pas être déployées, veuillez charger vos images directement dans les onglets adequats (<b>Image(s) avec canal alpha</b> et <b>Image(s) sans canal alpha</b>) dans l'interface générale."), QMessageBox.Yes)
	  return
	####################################################################
        if self.parent.tableauCourant != None :
          if type(self.parent.tableauCourant.typeEntree) != list :
            ftype = [self.parent.tableauCourant.typeEntree]
            sourceEntree = [self.parent.tableauCourant.sourceEntrees]
          else :
            ftype = self.parent.tableauCourant.typeEntree
            sourceEntree = self.parent.tableauCourant.sourceEntrees
          i=0
          for sftype in ftype :
            files = self.getSelectedFiles(ftype = sftype)
            sourceEntree[i].setFiles(files, append)
            i += 1
          self.hide()
      except :
        #print "[DEBUG] Fonctions tampon non implémentée dans le tableau ", self.parent.tableauCourant.idSection
	EkdPrint(u"[DEBUG] Fonctions tampon non implémentée dans le tableau " + str(self.parent.tableauCourant.idSection))
	### Changé le 02/03/11 #############################################
	# Boîte de dilogue apparaissant pour informer l'utilisateur quand celui-ci charge des images dans le tampon
	# et que ces images ne peuvent pas être déployées dans la fonction en question
	reply = QMessageBox.warning(self, 'Message', _(u"Les images du tampon <b>(définies pour cette fonction)</b> ne peuvent pas être déployées, veuillez charger vos images directement dans les onglets adequats (par exemple <b>Image(s) source</b>) dans l'interface générale."), QMessageBox.Yes)
	####################################################################

    def afficherAide(self):
      """Boîte de dialogue de l'aide du cadre"""
      message=EkdAide(parent=self)
      message.setText(_(u"Message d'aide à compléter")) ### TODO : Définir le texte d'aide à afficher
      message.show()
      
    def getSelectedFiles(self, ftype) :
      """ Fonction pour récupérer les fichiers sélectionné du type ftype (image, video ou audio) à partir du tampon EKD
      Retour des infos sous forme de liste"""
      if ftype == "image" :
        return self.selectImage.getSelFiles()
      elif ftype == "video" :
        return self.selectVideo.getSelFiles()
      elif ftype == "audio" :
        return self.selectAudio.getSelFiles()
