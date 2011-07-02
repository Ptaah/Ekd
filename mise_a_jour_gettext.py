#!/usr/bin/python
# -*- coding: utf-8 -*-


# Script de mise à jour des fichiers *.pot dans le répertoire de l'utilisateur
# ----------------------------------------------------------------------------
# Voilà comment procéder:
# -----------------------
#
# Créer les fichiers (lors de la toute première traduction):
# ----------------------------------------------------------
# 1) Si les fichiers locale/ekd.pot et locale/ekdDoc.pot n'existent pas, il
# faut les créer par la commande: python gettext0.py
# 2) Faire la traduction des fichiers ekd.pot et ekdDoc.pot dans PoEdit et
# les sauvegarder dans le répertoire locale/es_ES/LC_MESSAGES (dans le cas de
# la traduction espagnole) sous le nom ekd.pot et ekdDoc.pot
#
# Mettre à jour les fichiers (lors de traductions ultérieures):
# -------------------------------------------------------------
#
# 1) Ouvrez une console dans le répertoire où se trouve ce script 
# mise_a_jour_gettext.py (dans la console: cd /chemin/vers/le/répertoire/d'ekd)
# et mettez à jour les fichiers .pot par la commande:
# python mise_a_jour_gettext.py
# ==> Les fichiers .pot de mise à jour seront crées dans votre /home/utilisateur 
# et porteront les noms:
# ekd_symbole_langue_mois_année_heure.pot ... et ...
# ekdDoc_symbole_langue_mois_année_heure.pot
# (par exemple ekd_es_ES_8_3_2009_20h37.pot et ekdDoc_es_ES_8_3_2009_20h37.pot)
#
# 2) Mettez en téléchargement quelque part ces fichiers pour les développeurs du 
# projet ... de votre côté passez-les à la moulinette dans PoEdit pour obtenir les 
# fichiers ekd.po, ekd.pot et ekd.mo, puis ekdDoc.po, ekdDoc.pot et ekdDoc.mo, (en
# les ayant renommés) puis copiez-les (toujours dans le cas d'une traduction en 
# espagnol) dans locale/es_ES/LC_MESSAGES avec un système en espagnol ... et vérifier 
# que tout s'affiche correctement ... (gardez tout de même une copie de sauvegarde 
# de vos fichiers ekd.pot et ekdDoc.pot quelque part [fruit d'une traduction préalable 
# ... histoire de ne pas perdre le travail déjà effectué] , avant de faire une 
# quelconque mise à jour de ces deux fichiers !!!).


import os, time, shutil, glob, string

####### Ajouté le 25/09/2009 : Utilisation de EkdConfig ###################################
from moteur_modules_common.EkdConfig import EkdConfig
###########################################################################################

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

# Création du répertoire temporaire pour copie des fichiers .pot
# les fichiers seront ensuite renommés et copiés ds le rep utilisateur
####### Changé le 15/11/09 : Utilisation de EkdConfig #####################################
'''
Erreur dans la récupération de la section : general
Erreur dans la récupération de la propriété : temporaire  dans la section :  general
Traceback (most recent call last):
  File "mise_a_jour_gettext.py", line 53, in <module>
    repTampon = EkdConfig.getTempDir()+os.sep+'tampon'+os.sep+'mise_a_jour_gettext'+os.sep
  File "/home/angelo/ekd_toto/moteur_modules_common/EkdConfig.py", line 713, in getTempDir
    tmpBase = EkdConfig.get("general", "temporaire")
  File "/home/angelo/ekd_toto/moteur_modules_common/EkdConfig.py", line 622, in get
    raise e
AttributeError: 'NoneType' object has no attribute 'getElementsByTagName'
'''
#repTampon = EkdConfig.getTempDir()+os.sep+'tampon'+os.sep+'mise_a_jour_gettext'+os.sep

repTampon = os.sep+'tmp'+os.sep+'ekd_mise_a_jour_gettext'+os.sep
###########################################################################################
if os.path.isdir(repTampon) is False:
        os.makedirs(repTampon)
	
# Au cas où le répertoire existait déjà et qu'il n'était pas vide 
# -> purge (simple précausion)
for toutRepCompo in glob.glob(repTampon+'*.*'):
	if len(toutRepCompo)>0:
		os.remove(toutRepCompo)


# Liste sélectionnant les répertoires (donc les symbole langue) de chaque langue gérée
listeRepLocale = [os.path.basename(parcLoc) for parcLoc in glob.glob('locale'+os.sep+'*') if '_' in parcLoc and len(parcLoc) == 12]
listeRepLocale.sort()
# Liste recherchant particulièrement les deux répertoires  en_EN et es_ES (parmi
# tous les autres) car maintenant au 11/03/09 il y en a plein d'autres (toutes 
# les nationalités et communautés) dont la langue officielle est l'anglais
# ou l'espagnol
listeLanguePrincipale = [langP for langP in listeRepLocale if langP == 'es_ES' or langP == 'en_EN']
# Liste sélectionnant les fichiers .pot des répertoires de chaque langue gérée
listeFichPot = [parcPot for parcRepLoc in listeLanguePrincipale for parcPot in glob.glob('locale'+os.sep+parcRepLoc+os.sep+'LC_MESSAGES'+os.sep+'*.*') if parcPot.endswith('pot')]
listeFichPot.sort()
# Liste de listes comportant le chemin + le nom de fichier et en second élément l'extension,
# donne par exemple: [['locale/en_EN/LC_MESSAGES/ekd', 'pot'], ...,
# ['locale/es_ES/LC_MESSAGES/ekdDoc', 'pot']]
lChemNFichExt = [string.split(listeFichPot[parSplit], '.') for parSplit in range(len(listeFichPot))]
# Récupération du chemin + le nom de fichier (sans les extensions) des fichiers .pot, par
# exemple donne: ['locale/en_EN/LC_MESSAGES/ekd', ..., 'locale/es_ES/LC_MESSAGES/ekdDoc']
chemNomFich = [lChemNFichExt[parcNFE][0] for parcNFE in range(len(lChemNFichExt))]
# Multiplication par 2 (pour ekd.pot et ekdDoc.pot) des symboles langues
# pour pouvoir réaliser la mise en relation juste en dessous, donne par
# exemple: ['en_EN', 'en_EN', 'en_US', 'en_US', 'es_ES', 'es_ES']
listeLanguePrincipale_2 = listeLanguePrincipale*2
listeLanguePrincipale_2.sort()
# Mise en relation entre le chemin et le titre de chaque fichier.pot et le symbole langue, ça 
# donne par exemple la liste:
# [('locale/en_EN/LC_MESSAGES/ekd', 'en_EN'), ..., ('locale/es_ES/LC_MESSAGES/ekdDoc', 'es_ES')]
unionPotEtLangue = zip(chemNomFich, listeLanguePrincipale_2)


# Mise en relation du symbole langue dans le titre et copie des fichiers dans le
# répertoire temporaire (ça donne par exemple: ekdDoc_en_EN.pot, ..., ekd_es_ES.pot)
for parc_copie_tampon in unionPotEtLangue:
	if 'ekd' in parc_copie_tampon[0]:
		shutil.copy(os.getcwd()+os.sep+parc_copie_tampon[0]+'.pot', repTampon+os.sep+os.path.basename(parc_copie_tampon[0])+'_'+parc_copie_tampon[1]+'.pot')
	if 'ekdDoc' in parc_copie_tampon[0]:
		shutil.copy(os.getcwd()+os.sep+parc_copie_tampon[0]+'.pot', repTampon+os.sep+os.path.basename(parc_copie_tampon[0])+'_'+parc_copie_tampon[1]+'.pot')


def fichiersModule(dossier, ligne):
	"""transforme une ligne __init__ en liste de fichiers (chemin et extension compris) à traduire"""
	
	d = 0	# drapeau: le caractère traité est au-delà de '['
	ch = '' # chaîne de caractère qui deviendra progressivement un nom du fichier (sans chemin ni '.py')
	tot=''	# ce que l'on retourne (voir doc initiale)
	
	for i in ligne: # i: un caractère de la ligne
		if i == '[':
			d = 1
		elif i == ']':
			tot = tot + dossier + os.sep + ch + '.py'+ ' '
			break
		elif i in ["'",' ']:
			pass
		elif i == ',':
			tot = tot + dossier + os.sep + ch + '.py' + ' '
			ch = ''
		elif d:
			ch = ch + i
	return tot


######## Rajouté le 14/11/09 ###########################################
# Rajout de gui_modules_common, gui_modules_lecture,
# gui_modules_lecture/affichage_image, moteur_modules_common
########################################################################
# Liste des répertoires contenant les fichiers à traduire
listeModulesGui = ['gui_modules_animation', 'gui_modules_common', 'gui_modules_image', 
		   'gui_modules_image/divers', 'gui_modules_image/filtres_images', 
		   'gui_modules_image/masque_alpha_3d', 'gui_modules_image/transitions', 
		   'gui_modules_music_son','gui_modules_lecture', 'gui_modules_lecture/affichage_image', 
		   'gui_modules_sequentiel', 'moteur_modules_common', 'moteur_modules_animation']

######## Enlevé le 15/11/09 #############################################
'''
# Liste des répertoires contenant les fichiers à traduire
listeModulesGui = 	['gui_modules_animation','gui_modules_image',
			'gui_modules_music_son','gui_modules_lecture', 'gui_modules_image/divers',
			'gui_modules_image/filtres_images', 'gui_modules_image/masque_alpha_3d',
			'gui_modules_image/transitions', 'gui_modules_sequentiel']
'''
########################################################################


# Utile pour définir les dates des mises à jour
t = time.localtime()
# Attribution de la date et de l'heure exacte de la mise à jour
tt = str(t[2])+'_'+str(t[1])+'_'+str(t[0])+'_'+str(t[3])+'h'+str(t[4])

surlignageP = '-'*48
surlignageS = '-'*42

# Collecte des fichiers de la liste temporaire
listeTemp = glob.glob(repTampon+'*.*')


# Construction de la chaîne de caractères contenant les mises à jour (chemin est extension compris)
for i_1 in listeModulesGui:
	ficOb = open(i_1+'/__init__.py', 'r')
	ligne = ficOb.readline()
	fichiersModulesGui = fichiersModule(i_1, ligne)
	'''
	print
	print u'La mise à jour a été faite sur le(s) fichier(s): '
	print surlignageP
	print fichiersModulesGui + '\n'
	print
	'''
	EkdPrint('')
	EkdPrint(u'La mise à jour a été faite sur le(s) fichier(s): ')
	EkdPrint(surlignageP)
	EkdPrint(fichiersModulesGui + '\n')
	EkdPrint('')
	
	# Mise à jour des fichiers .pot pour les scripts autres que le script principal
	for collFichTemp in listeTemp:
		# Si on est bien dans la collecte de ekd et pas ekdDoc (ekd comprend bien
		# 13 caractères par exemple ekd_en_EN.pot) ...
		if len(os.path.basename(collFichTemp)) == 13 and 'ekd' in collFichTemp:
			os.system('xgettext --keyword=__ --keyword=_e --default-domain=ekd --language=python ' + fichiersModulesGui + ' --join-existing --output='+collFichTemp)
		'''
		# ----- NE FONCTIONNE PAS ----------------------------
		if len(os.path.basename(collFichTemp)) == 16 and 'ekdDoc' in collFichTemp:
			os.system('xgettext --keyword=tr --keyword=e --default-domain=ekdDoc --language=python ' + os.getcwd()+os.sep+fichiersModulesGui + ' --join-existing --output='+collFichTemp)
		'''
		
# Traitement des fichiers présents dans le rep. moteur_modules_animation =====================
# Collecte du chemin + fichiers présents dans le rep. moteur_modules_animation
listeFichRepMoteurTous = glob.glob('moteur_modules_animation'+os.sep+'*.*')
# Sélection des fichiers .py uniquement (tous les fichiers .py sauf le fichier __init__.py)
listeFichRepMoteurPy = [parcExtPy for parcExtPy in listeFichRepMoteurTous if parcExtPy.endswith('py') and 'moteur_modules_animation'+os.sep+'__init__.py' != parcExtPy]

# Construction de la chaîne de caractères contenant les mises à jour
# pour les fichiers contenus dans le rep. moteur_modules_animation
# -------------------------------------------------------------------
# La mise à jour se fait ici sans passer par le fichier __init__.py
# présent dans le rep. moteur_modules_animation car le fichier en
# question contient: __all__ = ['mencoder', 'mplayer', 'ffmpeg', 
# 'ffmpeg2theora', 'mencoder_concat_video', 'ffmpeg_avchd', 'ffmpeg_concat_audio']
# -------------------------------------------------------------------
for parcFichPy in listeFichRepMoteurPy:
	'''
	print
	print u'La mise à jour a été faite sur le(s) fichier(s): '
	print surlignageP
	print parcFichPy
	print
	'''
	EkdPrint('')
	EkdPrint(u'La mise à jour a été faite sur le(s) fichier(s): ')
	EkdPrint(surlignageP)
	EkdPrint(parcFichPy)
	EkdPrint('')
	
	# Mise à jour des fichiers .pot pour les scripts présents dans le rep. moteur_modules_animation
	for collFichTemp_2 in listeTemp:
		# Si on est bien dans la collecte de ekd et pas ekdDoc (ekd comprend bien
		# 13 caractères par exemple ekd_en_EN.pot) ...
		if len(os.path.basename(collFichTemp_2)) == 13 and 'ekd' in collFichTemp_2:
			os.system('xgettext --keyword=__ --keyword=_e --default-domain=ekd --language=python ' + parcFichPy + ' --join-existing --output='+collFichTemp_2)
# ============================================================================================

######## Rajouté le 01/06/09 ###########################################
# Traitement de videoporama_main.py dans le rep. videoporama ===========

# Collecte du chemin + fichier
fichVideoporamaMain = 'videoporama'+os.sep+'videoporama_main.py'

# Mise à jour pour le script videoporama/videoporama_main.py
for collVideoporamaTemp in listeTemp:
	# Si on est bien dans la collecte de ekd et pas ekdDoc (ekd comprend bien
	# 13 caractères par exemple ekd_en_EN.pot) ...
	if len(os.path.basename(collVideoporamaTemp)) == 13 and 'ekd' in collVideoporamaTemp:
		'''
		print
		print u'La mise à jour a été faite sur le fichier: '
		print surlignageS
		print fichVideoporamaMain
		print
		'''
		EkdPrint('')
		EkdPrint(u'La mise à jour a été faite sur le fichier: ')
		EkdPrint(surlignageS)
		EkdPrint(fichVideoporamaMain)
		EkdPrint('')
		os.system('xgettext --keyword=__ --keyword=_e --default-domain=ekd --language=python ' + fichVideoporamaMain + ' --join-existing --output='+collVideoporamaTemp)

# ======================================================================
########################################################################


######## Rajouté le 15/11/09 #################################################################
# Traitement des fichiers présents dans le rep. gui_modules_music_son ========================

# Collecte du chemin + fichiers présents dans le rep. gui_modules_music_son
listeFichRepMS = glob.glob('gui_modules_music_son'+os.sep+'*.*')
# Sélection des fichiers .py uniquement (tous les fichiers .py sauf le fichier __init__.py)
listeFichRepMusicSon = [parcExtPy for parcExtPy in listeFichRepMS if parcExtPy.endswith('py') and 'gui_modules_music_son'+os.sep+'__init__.py' != parcExtPy]

# Construction de la chaîne de caractères contenant les mises à jour
# pour les fichiers contenus dans le rep. gui_modules_music_son
# -------------------------------------------------------------------
# La mise à jour se fait ici sans passer par le fichier __init__.py
# présent dans le rep. moteur_modules_animation car le fichier en
# question contient: __all__=['multiplesound.py', 'music_son_base_sox.py', 
# 'music_son_decoupe.py', 'music_son_encodage.py', 'music_son_join_multiplefile.py', 
# 'music_son_normalize.py']
# -------------------------------------------------------------------
for parcFichPyMusicSon in listeFichRepMusicSon:
	'''
	print
	print u'La mise à jour a été faite sur le(s) fichier(s): '
	print surlignageP
	print parcFichPyMusicSon
	print
	'''
	EkdPrint('')
	EkdPrint(u'La mise à jour a été faite sur le(s) fichier(s): ')
	EkdPrint(surlignageP)
	EkdPrint(parcFichPyMusicSon)
	EkdPrint('')
	
	# Mise à jour des fichiers .pot pour les scripts présents dans le rep. gui_modules_music_son
	for collFichTemp_3 in listeTemp:
		# Si on est bien dans la collecte de ekd et pas ekdDoc (ekd comprend bien
		# 13 caractères par exemple ekd_en_EN.pot) ...
		if len(os.path.basename(collFichTemp_3)) == 13 and 'ekd' in collFichTemp_3:
			os.system('xgettext --keyword=__ --keyword=_e --default-domain=ekd --language=python ' + parcFichPy + ' --join-existing --output='+collFichTemp_2)
# ============================================================================================
##############################################################################################

# Mise à jour pour le script principal ekd_gui.py
for collEkdGuiTemp in listeTemp:
	# Si on est bien dans la collecte de ekd et pas ekdDoc (ekd comprend bien
	# 13 caractères par exemple ekd_en_EN.pot) ...
	if len(os.path.basename(collEkdGuiTemp)) == 13 and 'ekd' in collEkdGuiTemp:
		'''
		print
		print u'La mise à jour a été faite sur le fichier: '
		print surlignageS
		print 'ekd_gui.py'
		print
		'''
		EkdPrint('')
		EkdPrint(u'La mise à jour a été faite sur le fichier: ')
		EkdPrint(surlignageS)
		EkdPrint('ekd_gui.py')
		EkdPrint('')
		os.system('xgettext --keyword=__ --keyword=_e --default-domain=ekd --language=python ekd_gui.py' + ' --join-existing --output='+collEkdGuiTemp)

ficOb.close()


# Renommage des fichiers .pot (par exemple: ekd_en_EN_8_3_2009_20h4.pot,
# et copie des fichiers dans le répertoire de l'utilisateur
for collRenom in listeTemp:
	fich, ext = os.path.splitext(collRenom)
	shutil.copy(collRenom, os.path.expanduser('~')+os.sep+os.path.basename(fich)+'_'+tt+'.pot')
