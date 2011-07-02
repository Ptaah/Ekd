#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, string, shutil, glob ## shutil et glob ajoutés le 23/12/08
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_image.image_base import Base, SpinSlider
from gui_modules_image.selectWidget import SelectWidget
from gui_modules_lecture.lecture_image import Lecture_VisionImage

# Gestion de la configuration via EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig
# Nouvelle fenêtre d'aide ######
from gui_modules_common.EkdWidgets import EkdAide

import Image, ExifTags


# Nouvelle boite de dialogue pour sauver les fichiers
from gui_modules_common.EkdWidgets import EkdSaveDialog

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Image_Divers_RenomImg(QWidget):
	# -----------------------------------
	# Cadre accueillant les widgets de :
	# Image >> Divers >> Renommer images
	# -----------------------------------
	def __init__(self, geometry):
        	QWidget.__init__(self)
		
		# Boite d'alignement vertical
		vbox=QVBoxLayout(self)
		
		#=== Création des répertoires temporaires ===#
		# Gestion du repertoire tmp avec EkdConfig
		self.repTampon = EkdConfig.getTempDir() + os.sep + "tampon" + os.sep + "image_divers_renommage" + os.sep
		if os.path.isdir(self.repTampon) is False:
        		os.makedirs(self.repTampon)
		
		# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
		# -> purge (simple précausion)
		for toutRepCompo in glob.glob(self.repTampon+'*.*'):
			os.remove(toutRepCompo)
		
		#=== Drapeaux ===#
		# Une conversion (même partielle) a-t-elle eu lieu après le chargement des images? (1: vrai)

		# Est-ce que des images sources ont été modifiées? (c'est-à-dire ajoutées ou supprimées)
		self.modifImageSource = 0

		#=== Variable de configuration ===#

		# Fonctions communes à plusieurs cadres du module Image
		self.base = Base()
		
		# Gestion de la configuration via EkdConfig

		# Paramètres de configuration
		self.config = EkdConfig
		# Identifiant du cadre
		self.idSection = "image_renommer"
		# Log du terminal
		self.base.printSection(self.idSection)
		# Fonction appelant la fenêtre principale
		self.mainWindowFrameGeometry = geometry

		self.listeImgSource = []
		
		# là où s'afficheront les infos
		self.zoneTexte = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneTexte.setText = self.zoneTexte.setPlainText
		self.zoneTexte.setReadOnly(True)
		
		self.tabwidget=QTabWidget()
		
		# Boîte de combo
		self.comboClassement=QComboBox()
		self.listeComboClassement=[(_(u'Par ordre de sélection'),  'ord_select'),\
					   (_(u'Par ordre alpha-numérique'),  'ord_apha_num'),\
				    	   (_(u'Par ordre de prise de vue (données Exif): ordre croissant'),  'ord_exif_oc'),\
					   (_(u'Par ordre de prise de vue (données Exif): ordre décroissant'),  'ord_exif_dc')]
		# Insertion de l'ordre de classement des images/photos dans la combo box
		for i in self.listeComboClassement:
                	self.comboClassement.addItem(i[0],QVariant(i[1]))
		self.connect(self.comboClassement, SIGNAL("currentIndexChanged(int)"), self.classement)
		
		#=== 1er onglet ===#
		self.framNbreImg=QFrame()
		vboxReglage=QVBoxLayout(self.framNbreImg)
		
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel(_(u"Traitement à partir de l'image (numéro)")), 0, 0)
		self.spin1=SpinSlider(1, 10000, 1, '', self)
		self.grid.addWidget(self.spin1, 0, 1)
		self.connect(self.spin1, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		self.grid.addWidget(QLabel(_(u"Nombre de chiffres après le nom de l'image")), 1, 0)
		self.spin2=SpinSlider(3, 18, 6, '', self)
		self.grid.addWidget(self.spin2, 1, 1)
		self.connect(self.spin2, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		# Demandé par Marc de la liste lprod
		# "J'aurais été interressé par un paramètre supplémentaire pour définir l'incrément (ou le pas ...).
		# En fait cela permettrait d'insérer (donc classer) facilement les photos issues d'appareils 
		# différents mais traitant les mêmes sujets. En fait, je voudrais réaliser une série finale des 
		# photos prises avec mon APN, mon camescope et l'APN de mon épouse. Je numérote de 10 en 10 la 
		# plus grosse série de photos et viens insérer les autres au bon endroit sans avoir à utiliser 
		# des indices a, b, c, etc."
		self.grid.addWidget(QLabel(_(u"Valeur d'incrément (passage d'une image à l'autre)")), 2, 0)
		#self.spin3=SpinSlider(1, 1000, 1, 'increment', self) # Ne fonctionne pas
		self.spin3=SpinSlider(1, 1000, 1, '', self)
		self.grid.addWidget(self.spin3, 2, 1)
		self.connect(self.spin3, SIGNAL("valueChanged(int)"), self.changeValNbreImg_1)
		self.grid.addWidget(QLabel(_(u"Classement")), 3, 0)
		self.grid.addWidget(self.comboClassement, 3, 1)
		
		self.grid.setAlignment(Qt.AlignHCenter)
		vboxReglage.addLayout(self.grid)
		vboxReglage.addStretch()
		
		#=== 2ème onglet ===#
		# infos - logs
		self.zoneAffichInfosImg = QTextEdit("")
		if PYQT_VERSION_STR < "4.1.0":
			self.zoneAffichInfosImg.setText = self.zoneAffichInfosImg.setPlainText
		self.zoneAffichInfosImg.setReadOnly(True)
		self.framImg=QFrame()
		vboxReglage=QVBoxLayout(self.framImg)
		vboxReglage.addWidget(self.zoneAffichInfosImg)
		self.framImg.setEnabled(False)

		# Là où s'afficheront les images
		self.afficheurImgSource=SelectWidget(geometrie = self.mainWindowFrameGeometry)
		## ---------------------------------------------------------------------
		# Variables pour la fonction tampon
		## ---------------------------------------------------------------------
		self.typeEntree = "image" # Défini le type de fichier source.
		self.typeSortie = "image" # Défini le type de fichier de sortie.
		self.sourceEntrees = self.afficheurImgSource # Fait le lien avec le sélecteur de fichier source.

		self.indexTabImgSource = self.tabwidget.addTab(self.afficheurImgSource, _(u'Image(s) source'))
		self.indexTabReglage=self.tabwidget.addTab(self.framNbreImg, _(u'Réglages'))
		self.indexTabInfo=self.tabwidget.addTab(self.framImg, _(u'Infos'))
		
		vbox.addWidget(self.tabwidget)
		
		# -------------------------------------------------------------------
		# widgets du bas : ligne + boutons Aide et Appliquer
		# -------------------------------------------------------------------
		
		# Boutons
		boutAidetRenomImg=QPushButton(_(u" Aide"))
		boutAidetRenomImg.setIcon(QIcon("Icones/icone_aide_128.png"))
		self.connect(boutAidetRenomImg, SIGNAL("clicked()"), self.afficherAide)
		self.boutApp=QPushButton(_(u" Renommer"))
		self.boutApp.setIcon(QIcon("Icones/icone_appliquer_128.png"))
		
		self.connect(self.boutApp, SIGNAL("clicked()"), self.appliquer)
		
		# Ligne de séparation juste au dessus des boutons
		ligne = QFrame()
		ligne.setFrameShape(QFrame.HLine)
		ligne.setFrameShadow(QFrame.Sunken)
		vbox.addWidget(ligne)
		vbox.addSpacing(-5)	# la ligne doit être plus près des boutons
		
		hbox=QHBoxLayout()
		hbox.addWidget(boutAidetRenomImg)
		hbox.addStretch()	# espace entre les 2 boutons
		hbox.addWidget(self.boutApp)
		self.boutApp.setEnabled(False)
		vbox.addLayout(hbox)
		
		# Affichage de la boîte principale
		self.setLayout(vbox)
		
		#----------------------------------------------------------------------------------------------------
		# Signal de présence d'images dans ler widget de sélection -> modifie le statut des boutons d'action
		#----------------------------------------------------------------------------------------------------
		
		self.connect(self.afficheurImgSource, SIGNAL("pictureChanged(int)"), self.modifBoutonsAction)
		
		
	def modifBoutonsAction(self, i):
		"On active ou désactive les boutons d'action selon s'il y a des images ou pas dans le widget de sélection"
		self.boutApp.setEnabled(i)
		self.modifImageSource = 1


	def changeValNbreImg_1(self): ##
		#print "Traitement a partir de l'image (numero):", self.spin1.value()
		EkdPrint(u"Traitement a partir de l'image (numero): %s" % self.spin1.value())
		#print "Nombre de chiffres apres le nom de l'image:", self.spin2.value()
		EkdPrint(u"Nombre de chiffres apres le nom de l'image: %s" % self.spin2.value())
		# Demandé par Marc de la liste lprod
		#print "Valeur d'incrément (passage d'une image à l'autre):", self.spin3.value()
		EkdPrint(u"Valeur d'incrément (passage d'une image à l'autre): %s" % self.spin3.value())


	def classement(self, i):
		"""Récup/affichage ds le terminal de l'index de self.comboClassement"""
		
		idCombo=str(self.comboClassement.itemData(i).toString())
		
		if idCombo=='ord_select': 
	                #print 'Par ordre de sélection'
			EkdPrint(u'Par ordre de sélection')
		elif idCombo=='ord_apha_num': 
		        #print 'Par ordre alpha-numérique'
		        EkdPrint(u'Par ordre alpha-numérique')
		elif idCombo=='ord_exif_oc': 
		        #print 'Par ordre de prise de vue (données Exif): ordre croissant'
		        EkdPrint(u'Par ordre de prise de vue (données Exif): ordre croissant')
		elif idCombo=='ord_exif_dc': 
		        #print 'Par ordre de prise de vue (données Exif): ordre décroissant'
		        EkdPrint(u'Par ordre de prise de vue (données Exif): ordre décroissant')
		
	
	# Gestion du nombre d'images à traiter
	# Si l'utilisateur charge une seule image l'image sera renommée comme ceci: le_titre.extension
	# Si l'utilisateur charge plusieurs images les images seront renommées comme ceci: le_titre_001.extension,
	# le_titre_002.extension, le_titre_003.extension, ...
	def appliquer(self):
		"""Appliquer le renommage des images"""
		
		self.a1='###########################\n'
		self.b1=_('Fichiers avant renommage')+':\n'
		self.c1='###########################\n\n'
		
		# Récupération de la liste des fichiers chargés
		self.listeImgSource=self.afficheurImgSource.getFiles()
		
		# Nombre d'éléments présents dans la liste
		nbreElem=len(self.listeImgSource)
		
		# Copie par une boucle des images chargées par l'utilisateur dans le rep.
		# tampon --> shutil.copy(...) (on ne va pas utiliser
		# os.rename(source, destination) mais shutil.move(source, destination))
		# car avec os.rename les fichiers source sont détruits, ce qui est une très
		# mauvaise chose. De plus si on utilise os.rename on obtient l'erreur: OSError:
		# [Errno 18] Lien croisé invalide
		#
		for n in range(nbreElem): shutil.copy(self.listeImgSource[n], self.repTampon)

		# On récupère le nom des fichiers chargés (seulement le nom, pas le chemin)
		# --> là il faut absolument garder les noms des fichiers exactement dans 
		# l'ordre dans lequel ils ont été chargés. On ne peut pas utiliser glob, ni
		# os.listdir(...) car ils rangent dans un ordre qui n'est pas le bon 
		# (certainement car ils utilisent à la base un dictionnaire).
		l_pre_imgSource = [os.path.basename(fich) for fich in self.listeImgSource]
		# On concatène le chemin (juste le chemin) du rep. tampon avec les fichiers
		l_imgSource = [self.repTampon+add for add in l_pre_imgSource]
		
		# Récup du classement choisi par l'utilisateur (par la QComboBox)
		i = self.comboClassement.currentIndex()
		classemt = self.comboClassement.itemData(i).toString()
		
		if classemt == 'ord_select': pass
		
		elif classemt == 'ord_apha_num': l_imgSource.sort()
		
		else: 
			l_imgSource.sort()
			
			listeExif = []
			for fichier in l_imgSource:
				# Sélection du chemin (sans extension) et de l'extension elle-même
				fich, ext = os.path.splitext(fichier)
				# Condition de sélection de l'extension pour EXIF et ouverture image
				try:
					if ext in [".jpg", ".JPG", ".jpeg", ".JPEG"]:
						imgExif = Image.open(fichier)
					else:
						# Si l'utilisateur charge des images avec des extensions autres que ...
						erreur_0 = QMessageBox.critical(self,_(u"Par ordre de prise de vue (données Exif)"),_(u"<p><b>Vous ne pouvez charger que des images avec des extensions jpg, JPG, jpeg ou JPEG (!).</b></p>"), QMessageBox.Yes)
						if erreur_0 == QMessageBox.Yes: return
					# Données brutes contenues dans le dictionnaire
					exifdata = imgExif._getexif()
					# Certaines images délivrent None à _getexif(), dans ce/ces cas
					# la boîte de dialogue erreur_1 est affichée et le traitement
					# est stoppé. Les 2 boîtes de dialogue (erreur_1 et erreur_2)
					# sont utilisées dans 2 cas différents (même si le message
					# d'erreur délivré est le même)
					if exifdata == None:
						erreur_1 = QMessageBox.critical(self,_(u"Par ordre de prise de vue (données Exif)"),_(u"<p>Une ou plusieurs de vos image(s) possède(nt) de fausses donnée(s) Exif.</p><p><b>Le traitement demandé ne pourra pas se dérouler avec succès.</b></p><p><b>Veuillez, s'il vous plaît (la prochaine fois), charger des photos avec des données Exif correctes.</b></p>"), QMessageBox.Yes)
						if erreur_1 == QMessageBox.Yes: return
				# Si on charge des images ne possédant pas de données Exif
				# ou de fausses images avec données Exif (comme par exemple
				# les copies d'écran faites par Gimp, qui elles, bizarre !
				# possèdent des données Exif inexploitables) tout se ferme
				except:
					erreur_2 = QMessageBox.critical(self,_(u"Par ordre de prise de vue (données Exif)"),_(u"<p>Une ou plusieurs de vos image(s) possède(nt) de fausses donnée(s) Exif.</p><p><b>Le traitement demandé ne pourra pas se dérouler avec succès.</b></p><p><b>Veuillez, s'il vous plaît (la prochaine fois), charger des photos avec des données Exif correctes.</b></p>"), QMessageBox.Yes)
					if erreur_2 == QMessageBox.Yes: return
					
				# Récup des clés et valeurs du dictionnaire
				for keyExif, valueExif in zip(exifdata.keys(), exifdata.values()):
					try:
						# On ne récupère que le tag DateTime
						if ExifTags.TAGS[keyExif] == 'DateTimeOriginal':
							listeExif.append(valueExif.split(' '))
					except KeyError:
						pass
						
			# Split pour récup des données de la sorte: [..., [année, mois, jour], [heure, min, sec], ...]
			listeSplit = [parc_2.split(':') for parc_1 in  listeExif for parc_2 in parc_1]
			
			# Récup de la 1ère sous-liste uniquement index pair
			# [[année_1, mois_1, jour_1], [année_2, mois_2, jour_2], ...]
			listeIndexPair = [n for n in listeSplit if listeSplit.index(n) % 2 == 0]
			
			# Récup de la 2ème sous-liste uniquement index impair
			# [[heure_1, min_1, sec_1], [heure_2, min_2, sec_2], ...]
			listeIndexImpair = [n for n in listeSplit if listeSplit.index(n) % 2 != 0]
			
			# Fusion des 2 listes
			listeReunion = zip(listeIndexPair, listeIndexImpair)
			
			listeDate = []
			for nb, group in enumerate(zip(listeReunion, l_imgSource)):
				# Les données de temps affichées ne sont pas directement exploitables
				# Il y a des choses à transformer ... surtout si on trouve des '00'
				# -------------------
				annee = group[0][0][0]
				if annee[0] == '0': annee = annee[-1:]
				else: annee = annee
				# -------------------
				mois = group[0][0][1]
				if mois[0] == '0': mois = mois[-1:]
				else: mois = mois
				# -------------------
				jour = group[0][0][2]
				if jour[0] == '0': jour = jour[-1:]
				else: jour = jour
				# -------------------
				heure = group[0][1][0]
				if heure[0] == '0': heure = heure[-1:]
				else: heure = heure
				# -------------------
				minute = group[0][1][1]
				if minute[0] == '0': minute = minute[-1:]
				else: minute = minute
				# -------------------
				seconde = group[0][1][2]
				if seconde[0] == '0': seconde = seconde[-1:]
				else: seconde = seconde

				# Liste remplie de la sorte: [..., [annee, mois, jour,
				# heure, minute, seconde, index, chemin_image], ...]
				listeDate.append([int(annee), int(mois), int(jour), int(heure), int(minute), int(seconde), nb, group[1]])

			listeDate.sort()
			
			# Sélection de chaque élément à l'indice 7 dans les sous-listes, 
			# c'est à dire le chemin de l'image (ordre croissant)
			listeOrdreDateCrois = [ordre for pre_ordre in listeDate for ordre in pre_ordre if pre_ordre.index(ordre) / 7 == 1]
			
			l_imgSource = listeOrdreDateCrois
			
			# Si l'utilisateur choisit l'ordre décroissant, le même 
			# traitement est effectué, mais l'ordre de la liste finale
			# est inversé
			if classemt == 'ord_exif_dc': l_imgSource.reverse()
		
		# Demandé par Marc de la liste lprod
		# La liste liste_increment_2 contient les données comme ceci:
		# [(indice img 1, incrément img 1), (indice img 2, incrément img 2),
		# (indice img 3, incrément img 3), (indice img 4, incrément img 4),  ...]
		liste_increment_1 = [c_pas_1*self.spin3.value() for c_pas_1 in range(nbreElem)]
		liste_increment_2 = [(inc, c_pas_2) for inc, c_pas_2 in enumerate(liste_increment_1)]

		# Récupération du chemin + vidéo chargée et de l'extension 
		# (la première image de la liste) 
		fich, ext=os.path.splitext(self.listeImgSource[0])
		
		# Utilisation de la nouvelle boîte de dialogue de sauvegarde
		# Boîte de dialogue pour sauvegarder (nom du nouveau fichier)
		suffix=""
                sauver = EkdSaveDialog(self, mode="image", suffix=suffix, title=_(u"Sauver"), multiple=True)
		sauver = sauver.getFile()
		
		# Pour la version windows
		# Autrement les fichiers seront (a la fin) renommes comme ceci:
		# a.jpg_000001.jpg, a.jpg_000002.jpg, ... alors que la ils seront renommes
		# comme ceci (c'est quand meme mieux !): a_000001.jpg, a_000002.jpg, ...
		
		# Uniquement pour windows
		if os.name == 'nt': 
			sauver, ext_sauv = os.path.splitext(sauver)
		
		if not sauver: return
		
		listeSauve=[]

		if len(self.listeImgSource)==1:
			
			# Renommage et sauvegarde
			shutil.move(l_imgSource[0], sauver+ext)
			listeSauve.append(sauver+ext)
			
		elif len(self.listeImgSource)>1:
		
			# Barre de progression dans une fenêtre séparée . Attention la fenêtre
			# de la barre se ferme dès que la progression est terminée . En cas de
			# process très court, la fenêtre peut n'apparaître que très brièvement
			# (voire pas du tout si le temps est très très court) .
			self.progress=QProgressDialog(_(u"Opération en cours ..."), _(u"Annuler conversion"), 0, 100)
			self.progress.setWindowTitle(_(u'EnKoDeur-Mixeur . Fenêtre de progression'))
			# Attribution des nouvelles dimensions 
			self.progress.setMinimumWidth(500)
			self.progress.setMinimumHeight(100)
			# setGeometry est utilisé ici uniquement pour le placement à la position 0, 0
			# je ne suis pas un adepte de la position 0,0 :-P (Romain)
			#self.progress.setGeometry(QRect(0, 0, 500, 100))
		
			self.progress.show()
			
			# Demandé par Marc de la liste lprod
			# Le parcours se fait maintenant par la liste liste_increment_2 (le contenu 
			# de cette liste est précisé est précisé plus haut). Ceci pour mettre en 
			# pratique l'icrémentation des images, c'est à dire de pouvoir les renommer 
			# comme ceci: a_0001.jpg, a_0004.jpg, a_0007.jpg, a_0010.jpg, ... --> quand
			# l'utilisateur change la Valeur d'incrément (passage d'une image à l'autre)
			# à 3 (ce n'est qu'un exemple)
			
			for parc, increment in liste_increment_2:
				
				# Renommage et sauvegarde
				
                                # Uniquement pour Linux et MacOSX
                                if os.name in ['posix', 'mac']:
                                        shutil.move(l_imgSource[parc], sauver+'_'+string.zfill(increment+self.spin1.value(), self.spin2.value())+ext)                                        
                                
                                # Uniquement pour windows
                                elif os.name == 'nt':
                                        # ---------------
                                        # On avait prealablement (uniquement sous windows) l'erreur suivante:
                                        # WindowsError: [Error 32] Le processus ne peut pas acceder au fichier car ce
                                        # fichier est utilise par un autre processus: ...
                                        # ---------------
                                        # La solution pour la version windows a ete trouvee ici:
                                        # http://www.nabble.com/Windows-process-ownership-trouble-td18110819.html
                                        # --> try: ... except WindowsError: ...
                                        # ---------------
                                        try:
                                                shutil.move(l_imgSource[parc], sauver+'_'+string.zfill(increment+self.spin1.value(), self.spin2.value())+ext)
                                        except WindowsError: pass
				
				# Gestion du nombre d'images à traiter
				listeSauve.append(sauver+'_'+string.zfill(increment+self.spin1.value(), self.spin2.value())+ext)
			
				# --------------------------------------------
				# Affichage de la progression (avec
				# QProgressDialog) ds une fenêtre séparée .
				val_pourc=((parc+1)*100)/nbreElem

				# Bouton Cancel pour arrêter la progression donc le process
				if (self.progress.wasCanceled()):
					break

				self.progress.setValue(val_pourc)
		
				QApplication.processEvents()
				# --------------------------------------------

		self.a2='###########################\n'
		self.b2=_(u'Fichiers après renommage')+':\n'
		self.c2='###########################\n\n'

		# Affichage dans zoneTexte des fichiers avant et après renommage
		self.zoneAffichInfosImg.setText(self.a1+self.b1+self.c1+"\n".join(self.listeImgSource)+'\n\n'+self.a2+self.b2+self.c2+"\n".join(listeSauve))
		self.framImg.setEnabled(True)
		self.tabwidget.setCurrentIndex(self.indexTabInfo)


	def afficherAide(self):
		""" Boîte de dialogue de l'aide du cadre Image > Renommer """
		# Nouvelle fenêtre d'aide

		messageAide=EkdAide(parent=self)
		messageAide.setText(tr(u"<p><b>Vous pouvez ici renommer un lot d'images. Pour information (et ce dans l'onglet Réglages), vous pouvez choisir un ordre spécifique dans le classement de vos images (les deux derniers choix dans la liste font référence aux données EXIF des photographies numériques).</b></p><p>Dans l'onglet <b>'Images sources'</b> cliquez sur le bouton <b>Ajouter</b>, une boîte de dialogue apparaît, sur la partie gauche sélectionnez le répertoire (au besoin dépliez les sous-répertoires), allez chercher vos image(s). Si vous voulez sélectionner plusieurs images d'un coup, maintenez la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier enfoncée (tout en sélectionnant vos images), cliquez sur <b>Ajouter</b>.<p></p>Dans l'onglet <b>'Réglages'</b> faites les réglages du <b>'Traitement à partir de l'image (numéro)'</b> et du <b>'Nombre de chiffres après le nom de l'image' <font color='red'>(la plupart du temps les valeurs par défaut suffisent)</font></b></p>.<p>Une fois tout ceci fait, cliquez sur le bouton <b>'Renommer'</b>, sélectionnez le répertoire de sauvegarde, indiquez votre <b>'Nom de fichier'</b>, cliquez sur le bouton <b>'Enregistrer'</b>.</p><p>Après le traitement vous pouvez immédiatement voir l'affichage du résultat avant et après renommage des fichiers par l'onglet <b>'Infos'</b>.</p>"))
		messageAide.show()


	def save(self) :
		self.afficheurImgSource.saveFileLocation(self.idSection)
		EkdConfig.set(self.idSection, u'spin1', unicode(self.spin1.value()))
		EkdConfig.set(self.idSection, u'spin2', unicode(self.spin2.value()))
		EkdConfig.set(self.idSection, u'spin3', unicode(self.spin3.value()))
		EkdConfig.set(self.idSection, u'comboClassement', unicode(self.comboClassement.currentIndex()))


	def load(self) :
		self.afficheurImgSource.loadFileLocation(self.idSection)
		self.spin1.setValue(int(EkdConfig.get(self.idSection, 'spin1')))
		self.spin2.setValue(int(EkdConfig.get(self.idSection, 'spin2')))
		self.spin3.setValue(int(EkdConfig.get(self.idSection, 'spin3')))
		self.comboClassement.setCurrentIndex(int(EkdConfig.get(self.idSection, 'comboClassement')))
