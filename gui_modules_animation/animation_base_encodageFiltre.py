#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_common.gui_base import Base
from moteur_modules_animation.mplayer import Mplayer
from moteur_modules_common.EkdConfig import EkdConfig

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


# On joue avec l'héritage de Base
class Base_EncodageFiltre(Base):
	# -------------------------------------------------------------------
	# Cadre accueillant les widgets de : Animation >> Encodage
	# -------------------------------------------------------------------

	def __init__(self, titre=_(u"Titre")):
		# -------------------------------
		# Parametres généraux du widget
		# -------------------------------

		self.printSection()

		# tout sera mis dans une boîte verticale
		self.vbox=QVBoxLayout()

		super(Base_EncodageFiltre, self).__init__(boite='vbox', titre=titre)
		## -------------------------------------------------------------------
		## on utilise le selecteur d'image pour les vidéos
		from gui_modules_image.selectWidget import SelectWidget
		# Là où on naviguera entre les fichiers
		self.afficheurVideoSource=SelectWidget(mode="texte", video = True)
		# Onglets
		self.indexVideoSource = self.add(self.afficheurVideoSource, _(u'Video(s) source'))
		self.connect(self.afficheurVideoSource,SIGNAL("fileSelected"),self.getFile)
		self.connect(self.afficheurVideoSource, SIGNAL("pictureChanged(int)"), self.getFile)

		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "video" # Défini le type de fichier source.
		self.typeSortie = "video" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurVideoSource # Fait le lien avec le sélecteur de fichier source.

		#=== Widget qui seront inclus dans la boite de réglage ===#
		# Boite de combo
		self.combo=QComboBox() 	# Le self est nécessaire pour récupérer l'identifiant
					# de l'entrée de la boite de combo
		
		# Insertion des codecs de compression dans la combo box
		# Rq: listeCombo est de la forme: [(clé QVariant, texte à afficher,...), ...]
		for i in self.listeCombo: # self obligatoire pour le module séquentiel
                	self.combo.addItem(i[1], QVariant(i[0]))
		
		self.connect(self.combo,SIGNAL("currentIndexChanged(int)"),self.changerItemQStacked)
		
		# Utilisation de EkdConfig : modification des sections
		if self.idSection == "animation_filtresvideo":
			# On donne la référence de la boite de combo au widget de découpage
			# pour que ce dernier connaisse le type de découpage sélectionné (assisté ou libre)
			self.filtreDecouper.setComboParent(self.combo)
		
		# Widgets intégrés à la boîte de groupe "Réglage de sortie de l'encodage".
		# La boîte de combo définie ci-dessus 'sélectionne' ceux qui vont s'afficher
		# -> utilisation d'un stacked
		BoxReglage = QGroupBox()
		layoutReglage = QVBoxLayout(BoxReglage)
		layoutReglage.addWidget(self.combo)
		layoutReglage.addWidget(self.stacked)
		###

		self.loadOptions()
		
		self.add(BoxReglage, _(u"Réglages"))
		
		self.addPreview()

		self.addLog()

		# -------------------------------------------------------------------
		# widgets du bas : ligne + boutons Aide et Appliquer
		# -------------------------------------------------------------------

	
	def chargerItemCombo(self, idCombo):
		"""Charger un item particulier de la boite de combo"""
		try:
			indice = 0 # indice de la ligne de listeCombo correspondant au type d'ordre
			for i in self.listeCombo:
				if i[0]!=idCombo:
					indice += 1
				else:
					break
			self.combo.setCurrentIndex(indice)
		except:
			self.combo.setCurrentIndex(0)
	
	
	def changerItemQStacked(self, i):
		""" L'entrée sélectionnée de la boîte de combo modifie le QWidget de réglage du codec associée """
		#print "index", i
		EkdPrint(u"index %d" % i)
		idCodec=str(self.combo.itemData(i).toString())
		#print "idCodec:", idCodec, type(idCodec)
		EkdPrint(u"idCodec: %s %s" % (idCodec ,type(idCodec)))
		
		for k in self.listeCombo:
			if k[0]==idCodec:
				# Utilisation de EkdConfig : modification des sections
				if self.idSection == "animation_filtresvideo":
					if k[0] in ('decoupageassiste', 'decoupagelibre'):
						self.filtreDecouper.setStacked(k[0])
				if self.stacked:
					self.stacked.setCurrentIndex(k[2])
		
		EkdConfig.set(self.idSection,'codec', idCodec)
	
	def changerTypeDecoupe(self, mode):
		"Change le mode de découpe vidéo (assisté ou libre)"
		indexCombo = self.combo.findData(QVariant(mode))
		self.combo.setCurrentIndex(indexCombo)
	
	
	def getFile(self):
		'''
		Récupération de la vidéo source selectionnée
		'''
		self.chemin = self.afficheurVideoSource.getFile()
		self.boutApp.setEnabled(True)
		
		self.mplayer.setEnabled(True)
		self.mplayer.setVideos([self.chemin])
		
		self.radioSource.setChecked(True)
		self.radioSource.setEnabled(True)
		#self.radioConvert.setEnabled(True)
		#self.boutCompare.setEnabled(True)
		self.boutApp.setEnabled(True)
		if self.idSection == "animation_filtresvideo":
			self.boutApercu.setEnabled(True)
			self.filtreDecouper.setButtonEnabled(True)
		# On emmet un signal quand le fichier est chargé
		self.emit(SIGNAL("loaded"))
		return self.chemin

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
		# On charge les options
		'''
		idCodec = EkdConfig.get(self.idSection,'codec')
		self.chargerItemCombo(idCodec)

	def load(self):
		'''
		Chargement de la configuration de tous les objets
		'''
		self.loadFiles()
		self.loadOptions()

	def save(self):
		'''
		Sauvegarde de la configuration de tous les objets
		'''
		self.saveFiles()


	def sequentiel(self, entree, sortie, clef=None, ouvert=0):
		"""Utile dans le module du même nom. Applique les opérations associées à l'identifiant donné en 3ème argument. Retourne le vrai nom du fichier de sortie"""
		self.chargerItemCombo(clef)
		self.ouvrirSource(entree)
		return self.appliquer(sortie, ouvert)
	
	
	def sequentielReglage(self, clef):
		"""Utile dans le module du même nom. Récupère le widget de réglage associé à l'identifiant donné en 1er argument. Retourne l'instance du widget de réglage (avec quelques modifications)"""
		for k in self.listeCombo:
			if k[0]==clef:
				self.stacked.setCurrentIndex(k[2])
				titrePartielReglage = k[1]
		self.combo.hide()
		txt = _(u"Réglage")
		self.groupReglage.setTitle(txt+' : '+titrePartielReglage)
		return self.groupReglage
