#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, shutil
import Image, ExifTags
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_image.image_base import Base

from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage

# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig

# Gestion de l'aide via EkdAide
from gui_modules_common.EkdWidgets import EkdAide

# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Image_Divers_Info(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Information
	# -----------------------------------
	def __init__(self, geometry):
        	QWidget.__init__(self)
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		# Est-ce que l'image a déjà été affichée une fois ?
		# -> gain de temps au niveau de l'affichage
		self.drapeauImage = 0 # 0: non ; 1: oui
		
		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()

		# Paramètres de configuration
		self.config = EkdConfig
		self.idSection = "image_divers_infos"
		# Log du terminal
		self.base.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry
		
		self.chemin = []

		# Là où s'afficheront les images
		self.afficheurImgSource=SelectWidget(geometrie = self.mainWindowFrameGeometry)
		
		# -----------
		# Onglets
		# -----------
		
		# Onglets
		self.tab = QTabWidget()
		
		#== onglet chargement d'images ===#
		
		self.indexTabImgSource = self.tab.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		
		#== onglet d'information textuelle ===#
		
		self.zoneTexte = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneTexte.setText = self.zoneTexte.setPlainText
		self.zoneTexte.setReadOnly(True)
		
		frame = QFrame()
		hboxTab = QHBoxLayout(frame)
		hboxTab.addWidget(self.zoneTexte)
		
		self.tabIndexText = self.tab.addTab(frame, _("Infos Texte"))
		
		#== onglet d'information exif ===#
		
		self.table = QTableWidget()
		self.tabIndexExif = self.tab.addTab(self.table, _("Infos Exif"))

		vbox.addWidget(self.tab)
		
		# -------------------------------------------------------------------
		# widgets du bas : ligne + boutons
		# -------------------------------------------------------------------
		
		# boutons
		boutAide=QPushButton(_(u" Aide"))
		boutAide.setIcon(QIcon("Icones/icone_aide_128.png"))
		self.connect(boutAide, SIGNAL("clicked()"), self.afficherAide)
	
		self.boutSauverInfos=QPushButton(_(u" Sauver infos (.txt)"))
		# Show infos (.txt) ==> Sauver infos (.txt)
		self.boutSauverInfos.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		self.boutSauverInfos.setEnabled(False)
		self.connect(self.boutSauverInfos, SIGNAL("clicked()"), self.sauverInfos)
		
		self.boutSauverExif=QPushButton(_(u" Sauver Exif (.html)"))
		# Save Exif (.html) ==> Sauver Exif (.html)
		self.boutSauverExif.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		self.boutSauverExif.setEnabled(False)
		self.connect(self.boutSauverExif, SIGNAL("clicked()"), self.sauverExif)

		# ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons
		
		hbox=QHBoxLayout()
		hbox.addWidget(boutAide)
		hbox.addStretch()	# espace entre les 2 boutons
		hbox.addWidget(self.boutSauverInfos)
		hbox.addWidget(self.boutSauverExif)
		vbox.addLayout(hbox)
		
		# affichage de la boîte principale
		self.setLayout(vbox)
		
		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> appelle la fonction appliquer
		#----------------------------------------------------------------------------------------------------
		
		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifImgSource)
		self.connect(self.afficheurImgSource, SIGNAL("pictureSelected()"), self.appliquer)


	def modifImgSource(self):
		"""Les infos de la 1ère image de la liste sont affichées dans les onglets (soit les
		infos exif+texte, soit uniquement les infos texte"""
#		print "Images chargées"
		self.appliquer()
	
	
	def appliquer(self):
		"""Un chemin de fichier-image a été enregistré -> affichage des infos et possibilité de sauvegarder"""
		#print '\nfonction imAccepte'
		EkdPrint(u'\nfonction imAccepte')
		#print "chemin image d'entrée:", self.chemin, type(self.chemin)

		# Récupération de la liste des fichiers chargés
		self.chemin=self.afficheurImgSource.getFile()
		
		# Récupération du chemin + image chargée et de l'extension
		fich, self.ext=os.path.splitext(self.chemin)
		
		#=== remplissage des onglets avec les infos disponibles ===#
		
		#||| infos texte |||#
		self.afficherInfos()
		# Activation du bouton pour sauvegarder les infos texte
		self.boutSauverInfos.setEnabled(True)
		
		#||| infos exif et infos texte ... avec conditions |||#
		imgExif=Image.open(self.chemin)
		# Seulement si l'extension sélectionnée est en JPEG (et que l'image chargée
		# contient des données EXIF), la fonction self.afficherExif est exécutée
		if self.ext in [".jpg", ".JPG", ".jpeg", ".JPEG"] and 'Profile-exif:' in self.InfosTxtImage:
			exifdata=imgExif._getexif()
			self.afficherExif()
			# La page infos exif est sélectionnée
			self.tab.setCurrentIndex(self.tabIndexExif)
			# Activation du bouton pour sauvegarder les infos exif
			self.boutSauverExif.setEnabled(True)
		# Seulement si l'extension sélectionnée est en JPEG (mais que l'image chargée ne 
		# contient pas de données EXIF), la fonction self.afficherInfos est exécutée,
		# et rien n'est affiché dans la page Infos Exif
		elif self.ext in [".jpg", ".JPG", ".jpeg", ".JPEG"] and 'Profile-exif:' not in self.InfosTxtImage:
			# La page infos exif se vide complètement (lignes et colonnes)
			self.table.setRowCount(0)
			self.table.setColumnCount(0)
			self.afficherInfos()
			# La page infos texte est sélectionnée
			self.tab.setCurrentIndex(self.tabIndexText)
			# Non activation du bouton pour sauvegarder les infos exif
			self.boutSauverExif.setEnabled(False)
		# Seulement si l'extension sélectionnée est tout autre que JPEG (c'est à 
		# dire/et que l'image chargée ne contient pas de données EXIF), la fonction
		# self.afficherInfos est exécutée, et rien n'est affiché dans la page Infos Exif
		elif self.ext not in [".jpg", ".JPG", ".jpeg", ".JPEG"]:
			self.table.setRowCount(0)
			self.table.setColumnCount(0)
			self.afficherInfos()
			self.tab.setCurrentIndex(self.tabIndexText)
			# Activation du bouton pour sauvegarder les infos exif
			self.boutSauverExif.setEnabled(False)
		
		# Dégriser les onglets
		self.tab.setEnabled(True)
		
		# L'image n'a jamais été affichée
		self.drapeauImage = 0
	
	
	def afficherInfos(self):
		"""afficher les infos venant d'ImageMagick"""
		
		# Formats d'images acceptés (aussi ici en tout début) --> Rectifié le 25/12/08
		
		if self.ext in [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG", ".gif", ".GIF", ".tif", ".TIF", ".tiff", ".TIFF", ".ppm", ".PPM", ".bmp", ".BMP"]:
			
			self.listeInfo=[]
			
			chemin = self.chemin.encode("UTF8")
			
			#self.ImageInfos=os.popen('identify -verbose'+' '+"\""+chemin+"\"").readlines()
                        commande = 'identify -verbose \"%s\"' % chemin
                        processus = QProcess()
                        processus.start(commande)
                        if (not processus.waitForStarted()):
                            raise (u"Erreur de récupération des informations")
                        if ( not processus.waitForFinished()):
                            raise (u"Erreur de récupération des informations")
			# QString enlevé car pose de gros problèmes
                        #self.ImageInfos = QString(processus.readAllStandardOutput())
			self.ImageInfos = processus.readAllStandardOutput()
			
			# N'affichera que les infos humainement compréhensibles
			# (dans le cas d'une image avec données EXIF)
			self.listeInfo=[]
			for parcInfo in self.ImageInfos:
				# Ignore les données commençant par ...
				if parcInfo.startswith("0x0") or parcInfo.startswith("    Components Configuration:") or parcInfo.startswith("    Components Configuration:") or parcInfo.startswith("    Maker Note:") or parcInfo.startswith("    CFA Pattern:") or parcInfo.startswith("    User Comment:") or parcInfo.startswith("    File Source:") or parcInfo.startswith("    unknown:") or parcInfo.startswith("    Scene Type:") or parcInfo.startswith("    Print Image Matching:"):
					pass
				else:
					self.listeInfo.append(parcInfo)
			
			a=_(u"Vous ne pouvez sélectionner/afficher les infos que d'une image à la fois.\n==========================================================\nLes formats d'images acceptés sont: .jpg, .jpeg, .png, .gif, .tif, .tiff, .ppm, .bmp. Pour une image avec des informations EXIF, seulement le format .jpg (ou .jpeg, .JPG, .JPEG) est accepté.\n==========================================================\n")
			
			
			# Affichage dans zoneTexte
			self.InfosTxtImage=''.join(self.listeInfo)
			self.zoneTexte.setText(a+"\n"+self.InfosTxtImage)

		else:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"Une erreur est apparue! Cette extension (%s) n'est pas supportée" % self.ext))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()
		
		
	def sauverInfos(self):
		"""Sauver les infos (sous forme de fichier texte)"""
		
		try:

			# Utilisation de la nouvelle boîte de dialogue de sauvegarde
			suffix=""
			# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
                        sauver = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=False)
			sauver = sauver.getFile()
			
			if not sauver: return
			enrTxt=open(sauver+'.txt', 'wb')
			enrTxt.write(self.InfosTxtImage.encode("UTF8"))
			enrTxt.flush()
			enrTxt.close()
		
		except:
			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"Une erreur est apparue!"))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()
		
	
	def miseAJourTable(self, nbrCol, donnees):
		""" On met à jour la table exif """
		self.table.clear()
		self.table.setRowCount(len(donnees))
		self.table.setColumnCount(nbrCol)
		self.table.setHorizontalHeaderLabels([_(u"Paramètre"), _(u"Valeur")])
		self.table.setAlternatingRowColors(True)
		self.table.setEditTriggers(QTableWidget.NoEditTriggers)
		self.table.setSelectionMode(QTableWidget.ExtendedSelection)
		for indexL, ligne in enumerate(donnees):
			for indexC, element in enumerate(ligne):
				item = QTableWidgetItem(str(element))
				item.setTextAlignment(Qt.AlignCenter)
				self.table.setItem(indexL, indexC, item)
				#print indexL, indexC, element
				EkdPrint(u"%s %s %s" % (indexL, indexC, element))
        	self.table.resizeColumnsToContents()
	
	
	def afficherExif(self):
		"""Afficher les infos Exif"""
		
		try :
			# -----------------------------------------------------------------------
			# Extraction des donnees EXIF
			# -----------------------------------------------------------------------
			# Aide de Terry Carroll sur la liste de diffusion : 
			# image-sig at python.org .
			# Avec une petite adaptation personnelle. Merci à Terry Carroll.
			
			imgExif=Image.open(self.chemin.encode("UTF8"))
			
			# Recupération des infos EXIF
			exifdata=imgExif._getexif()
			
			listeExif=[]
	
			for keyExif, valueExif in zip(exifdata.keys(), exifdata.values()):
	
				try:
					if ExifTags.TAGS[keyExif] in ['UserComment', 'ComponentsConfiguration', 'CFAPattern', 'FileSource', 'SceneType', 'MakerNote', '\x01\x02\x03CompressedBitPerPixel']:
						pass
					
					else :
						ImageExif=(str(ExifTags.TAGS[keyExif]), valueExif)
						listeExif.append(ImageExif)
						
				except KeyError:
					pass
			
			# Changement de l'affichage pour l'enregistrement, et ce pour une 
			# meilleure lecture des données EXIF.
			affExif=[]
			for exifAff in listeExif:
				if exifAff[0].startswith("ApertureValue"):
					exifAffnouveau='f/'+str(round(float(exifAff[1][0])/float(exifAff[1][1]), 1))
					affExif.append(('ApertureValue', exifAffnouveau))
				elif exifAff[0].startswith("CompressedBitsPerPixel"):
					exifAffnouveau=str(int(exifAff[1][0])/int(exifAff[1][1]))+' bit/pixel'
					affExif.append(('CompressedBitsPerPixel', exifAffnouveau))
				elif exifAff[0].startswith("ExposureTime"): 
					exifAffnouveau=str(round(float(exifAff[1][0])/float(exifAff[1][1]), 3))+' ('+str(exifAff[1][0]/exifAff[1][0])+'/'+str(exifAff[1][1]/exifAff[1][0])+' sec)'
					affExif.append(('ExposureTime',exifAffnouveau))
				elif exifAff[0].startswith("FNumber"):
					exifAffnouveau='f/'+str(round(float(exifAff[1][0])/float(exifAff[1][1]), 1))+' (diaphragm value)'
					affExif.append(('FNumber', exifAffnouveau))
				elif exifAff[0].startswith("FocalLength"):
					exifAffnouveau=str(round(float(exifAff[1][0])/float(exifAff[1][1]), 2))+' mm'
					affExif.append(('FocalLength', exifAffnouveau))
				elif exifAff[0].startswith("FocalPlaneXResolution"):
					exifAffnouveau=str(round(float(exifAff[1][0])/float(exifAff[1][1]), 1))
					affExif.append(('FocalPlaneXResolution', exifAffnouveau))
				elif exifAff[0].startswith("FocalPlaneYResolution"):
					exifAffnouveau=str(round(float(exifAff[1][0])/float(exifAff[1][1]), 1))
					affExif.append(('FocalPlaneYResolution', exifAffnouveau))
				elif exifAff[0].startswith("MaxApertureValue"):
					exifAffnouveau='f/'+str(round(float(exifAff[1][0])/float(exifAff[1][1]), 1))
					affExif.append(('MaxApertureValue', exifAffnouveau))
				elif exifAff[0].startswith("XResolution"):
					exifAffnouveau=str(int(exifAff[1][0])/int(exifAff[1][1]))+' dpi'
					affExif.append(('XResolution', exifAffnouveau))
				elif exifAff[0].startswith("YResolution"):
					exifAffnouveau=str(int(exifAff[1][0])/int(exifAff[1][1]))+' dpi'
					affExif.append(('YResolution', exifAffnouveau))
				else:
					affExif.append(exifAff)
	
			# Ttes les infos Exif (tags Exif) obtenu(es) avec
			# intégration du code html pour affichage ds tableau.
			# Si on utilisait unicode pour les traductions, val[0] et val[1]
			# seraient à remplacer par _(unicode(val[0])) et _(unicode(val[1]))
			ExifHtml=['<tr>\n<td bgcolor="9dc3d9">'+str(val[0])+'</td>\n<td>'+str(val[1])+'</td>\n</tr>\n' for val in affExif]
			ExifHtml.sort()
			
			# ----------------------------------------------------
			# Conditions de dimensions de l'image pour l'affichage
			# ----------------------------------------------------
			
			# Recuperation de la valeur du poids de l'image 
			poidsDebutImgExif=int(os.stat(self.chemin).st_size)
			# Calcul du poids en kilo-octet de l'image
			self.poidsFinImgExif=int(poidsDebutImgExif)/1000
		
			# Recuperation du chemin de chargement de la photo
			chemEnrExif=os.path.dirname(self.chemin)
			# Recuperation du nom de la photo
			self.nomImageExif=os.path.basename(self.chemin).encode("UTF8")
			
			# On recupere la taille de l'image
			self.widthImgExif, self.heightImgExif=imgExif.size
			
			# Si la dimension la + grde est inférieure ou égale à 640
			if max(self.widthImgExif, self.heightImgExif)<=640 : self.widthImgExif, self.heightImgExif
			# Si la dimension la + grde est supérieure à 640
			if max(self.widthImgExif, self.heightImgExif)>640 :
				# Calcul du ratio de l'image
				ratioWHexif=float(max(self.widthImgExif, self.heightImgExif))/float(min(self.widthImgExif, self.heightImgExif))
				# La dimension la + grde
				MaxWHexif=max(self.widthImgExif, self.heightImgExif)
				# On assigne automatiquement la dimension la +
				# grde à 640 pour affichage ds le fichier html
				MaxWHexif=float(640)
				# Calcul de la dimension la + petite
				MinWHexif=MaxWHexif/ratioWHexif
			
				# Si La dimension la + grde est supérieure à 640 et 
				# la largeur est supérieure ou égale à la hauteur
				if MaxWHexif==float(640) and self.widthImgExif>=self.heightImgExif :
					self.widthImgExif=640
					self.heightImgExif=int(round(MinWHexif))
			
				# Si la hauteur est supérieure à la largeur
				if self.heightImgExif>self.widthImgExif :
					self.heightImgExif=640
					self.widthImgExif=int(round(MinWHexif))
			
			#----------------------------------------------------------
			# mise en forme des données dans un tableau QTableWidget()
			#----------------------------------------------------------
			self.miseAJourTable(2, listeExif)
			
			# -----------------------------------------------------
			# Affichage de l'exif ds le code et ds un tableau . 
			# -----------------------------------------------------
			# --> Quelques traductions :
			# --------------------------
			# NAME OF THE IMAGE --> NOM DE L'IMAGE 
			# WEIGHT OF THE IMAGE --> POIDS DE L'IMAGE
			# kb --> ko (kilobytes --> kilo-octets)
			# EXIF INFORMATIONS ABOUT THE IMAGE --> INFORMATIONS EXIF SUR L'IMAGE 
			# ExifVersion --> Version Exif
			# DateTime --> Date et heure
			# DateTimeOriginal --> Date et heure (d'origine)
			# DateTimeDigitized --> Date et heure (numerisation)
			# ExifImageWidth --> Dimension X en pixels
			# ExifImageHeight --> Dimension Y en pixels
			# XResolution --> Resolution X
			# YResolution --> Resolution Y
			# Make --> Constructeur
			# Model --> Modele
			# READ ATTENTIVELY WHAT IS JUST DOWN --> LISEZ ATTENTIVEMENT CE QUI 
			# SE TROUVE EN DESSOUS
			# Your image has to be exactly in the same directory as your html file,
			# otherwise the image in question will not appear in this page . -->
			# Votre image doit se trouver exactement dans le même répertoire que
			# votre fichier html, autrement l'image en question n'apparaîtra pas
			# dans cette page . 
			# This page html was generated by 
			# <a href='http://ekd.tolosano.info'>EKD</a> (post-production 
			# software for videos and images) . --> Cette page html a été générée
			# par <a href='http://ekd.tolosano.info'>EKD</a> (logiciel de
			# post-production pour les vidéos et les images) .
			
			#----------------------------------------------
			# Construction du tableau html avant affichage
			#----------------------------------------------
			
			self.infosExifPourHtml=u'<table border=1 bgcolor="f6d79a" width=100% align=center bordercolor="black">\n<tr>\n<tr>\n<td colspan="2" bgcolor="black" align="center"><font color="white">'+_(u"NOM DE L'IMAGE")+u'</td>\n</tr>\n<tr>\n<td colspan="2">'+self.nomImageExif+u'</td>\n</tr>\n<tr>\n<td colspan="2" bgcolor="black" align="center"><font color="white">'+_(u"POIDS DE L'IMAGE")+u'</td>\n</tr>\n<tr>\n<td colspan="2">'+str(self.poidsFinImgExif)+_(u' kb')+u'</td>\n</tr>\n<tr>\n<td colspan="2" bgcolor="black" align="center"><font color="white">'+_(u"INFORMATIONS EXIF SUR L'IMAGE")+u'</td>\n</tr>\n'+''.join(ExifHtml)+u'</tr>\n<tr>\n<td colspan="2" bgcolor="black" align="center"><font color="white">'+_(u"LISEZ ATTENTIVEMENT CE QUI SE TROUVE EN DESSOUS")+u'</td>\n</tr>\n<tr>\n<td colspan="2">'+_(u"Votre image doit se trouver exactement dans le m&ecirc;me r&eacute;pertoire que le fichier html, autrement l'image en question n'appara&icirc;tra pas dans la page.")+u'</td>\n</tr>\n<tr>\n<td colspan="2" bgcolor="black" align="center"><font color="white">'+_(u"Cette page html a &eacute;t&eacute; g&eacute;ner&eacute;e par <a href='http://ekd.tuxfamily.org'>EKD</a> (logiciel de post-production pour vid&eacute;os et images).")+u'</td>\n</tr>\n</table>'
			
		except :

			messageErreur=QMessageBox(self) 
			messageErreur.setText(_(u"Il s'est produit un problème !. Certainement que les photos de cet appareil ne contiennent pas des données importantes (comme par exemple 'Date et heure').")) 
			messageErreur.setWindowTitle(_(u"Erreur")) 
			messageErreur.setIcon(QMessageBox.Critical) 
			messageErreur.exec_()


	def sauverExif(self):
		"""Sauver les infos Exif (sous forme de fichier html)"""
	
		try:

			# Utilisation de la nouvelle boîte de dialogue de sauvegarde
			suffix=""
			# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
                        sauver = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=False)
			sauver = sauver.getFile()

			if not sauver: return
			enrHtml=open(sauver+'.html', 'wb')
			
			enrHtml.write('<!DOCTYPE html PUBLIC "-//IETF//DTD HTML 2.0//EN">\n<html>\n<head>\n<meta http-equiv=content-type content="text/html; charset=UTF-8">\n<title>EXIF infos</title>\n</head>\n<body bgcolor="d0cfcd" text="#000000" link="lightblue" vlink="orange">\n<center><IMG src="'+self.nomImageExif+'" '+ 'width="'+str(self.widthImgExif)+'" height="'+str(self.heightImgExif)+'" border="0"></center>\n<h4>'+self.infosExifPourHtml+'</h4>\n</body>\n</html>')
			enrHtml.flush()
			enrHtml.close()

			# Si on enregistre le fichier html dans le répertoire où la photo a été 
			# chargée, il faut vérifier si l'image chargée est déjà présente dans le rep.
			# de sauvegarde
			if os.path.exists(os.path.dirname(sauver)+os.sep+os.path.basename(self.chemin)) is False:
				# Copie de la 1ère image chargée dans le répertoire de sauvegarde
				# ... cela est utile pour que le fichier html généré s'affiche bien
				shutil.copy(self.chemin, os.path.dirname(sauver))
			else: pass

		except:

			messageErreur=QMessageBox(self)
			messageErreur.setText(_(u"Une erreur est apparue!"))
			messageErreur.setWindowTitle(_(u"Erreur"))
			messageErreur.setIcon(QMessageBox.Critical)
			messageErreur.exec_()


	def afficherAide(self):
		"""Boîte de dialogue de l'aide du cadre Image > Informations (txt ou Exif)"""

		# Gestion de l'aide via EkdAide
		messageAide=EkdAide(parent=self)
		messageAide.setText(_(u"<p><b>Vous pouvez ici afficher les informations (en format texte) d'images et/ou les informations EXIF (Exchangeable Image File Format) de prises de vues d'appareils photographiques numériques. Vous pouvez de même exporter ces informations sous forme de fichier html (en vue d'être publié sur internet, par exemple).</b></p><p><b>Voici une défintion de EXIF selon Wikipédia: 'L’Exchangeable image file format ou Exif est une spécification de format de fichier pour les images utilisées par les appareils photographiques numériques.</b></p><p><b>Les balises de métadonnées définies dans le format Exif standard couvrent un large éventail de données, dont:<br><ol><li>Information de la date et de l’heure. Les appareils numériques enregistrent la date et l’heure de la prise de vue et l’insèrent dans les métadonnées.</li><li>Les réglages de l’appareil. Cela comprend des informations statiques telles que la marque et le modèle de l’appareil et des informations variables telles que l’orientation, l’ouverture, la vitesse d’obturation, la longueur de focale, la sensibilité ... .</li><li>Description et information des droits d’auteur.'</b></li></ol></p><p><b><font color='green'>Attention: comme vous pouvez le constater, les boutons 'Sauver infos (.txt)' et 'Sauver Exif (.html)' sont dans un premier temps grisés (ils deviendront actifs dès lors que vous aurez chargé une image).</font></b></p><p>Dans l'onglet <b>'Image source'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher votre/vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.</p><p>Vous avez maintenant la possibilité de consulter les informations sur l'image dans les onglets <b>'Infos Texte'</b> et/ou <b>'Infos Exif'</b>. <b><font color='red'>Il faut savoir que les informations délivrées sont celles de l'image que vous aurez sélectionné dans l'onglet Image(s) source</font></b></p><p>Vous pouvez sauvegarder les informations texte et/ou EXIF (suivant l'image/photo chargée), pour ce faire cliquez sur le bouton <b>'Sauver infos (.txt)'</b> ou <b>'Sauver Exif (.html)'</b>, dans la boîte de dialogue sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>. <b><font color='red'>De même ici les informations qui seront enregistrées seront celles de l'image sélectionnée dans l'onglet Image(s) source.</font></b></p>"))
		messageAide.show()
	
	
	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.appliquer()
