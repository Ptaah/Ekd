#!/usr/bin/python
# -*- coding: Utf-8 -*-

# script de création du fichier *.pot dans locale/

import os, glob
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

def fichiersModule(dossier, ligne):
	"""transforme une ligne __init__ en liste de fichiers (chemin est extension compris) à traduire"""
	
	d = 0	# drapeau: le caractère traité est au-delà de '['
	ch = '' # chaîne de caractère qui deviendra progressivement un nom du fichier (sans chemin ni '.py')
	tot=''	# ce que l'on retourne (voir doc initiale)
	
	for i in ligne: # i: un caractère de la ligne
		if i == '[':
			d = 1
		elif i == ']':
			tot = tot + dossier + '/' + ch + '.py'+ ' '
			break
		elif i in ["'",' ']:
			pass
		elif i == ',':
			tot = tot + dossier + '/' + ch + '.py' + ' '
			ch = ''
		elif d:
			ch = ch + i
	return tot

totalFichiersSource = ''

######## Rajouté le 14/11/09 ###########################################
# Rajout de gui_modules_common, gui_modules_lecture, gui_modules_lecture/affichage_image
# gui_modules_music_son, moteur_modules_common
########################################################################
# liste des répertoires contenant les fichiers à traduire
listeModulesGui = ['gui_modules_animation', 'gui_modules_common', 'gui_modules_image', 
	           'gui_modules_image/divers', 'gui_modules_image/filtres_images', 
		   'gui_modules_image/masque_alpha_3d','gui_modules_image/transitions', 
		   'gui_modules_music_son', 'gui_modules_lecture', 'gui_modules_lecture/affichage_image', 
		   'gui_modules_sequentiel', 'moteur_modules_common', 'moteur_modules_animation']

# construction de la chaîne de caractères contenant les fichiers à traduire (chemin est extension compris)
for i in listeModulesGui:
	ficOb = open(i+'/__init__.py', 'r')
	ligne = ficOb.readline()
	fichiersModulesGui = fichiersModule(i, ligne)
	totalFichiersSource = totalFichiersSource + fichiersModulesGui
	ficOb.close()

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg2theora.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'ffmpeg2theora.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_avchd.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'ffmpeg_avchd.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_concat_audio.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'ffmpeg_concat_audio.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_concat_audio.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'ffmpeg_concat_audio.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'ffmpeg.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier mencoder_concat_video.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'mencoder_concat_video.py'

# Ajout du fichier mencoder.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'mencoder.py'

# Ajout du fichier mplayer.py présent dans le rep. moteur_modules_animation
totalFichiersSource += ' moteur_modules_animation'+os.sep+'mplayer.py'

######## Rajouté le 01/06/09 ###########################################
# Ajout du fichier videoporama_main.py présent dans le rep. videoporama
totalFichiersSource += ' videoporama'+os.sep+'videoporama_main.py'
########################################################################

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_avchd.py présent dans le rep. gui_modules_music_son
totalFichiersSource += ' gui_modules_music_son'+os.sep+'multiplesound.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_avchd.py présent dans le rep. gui_modules_music_son
totalFichiersSource += ' gui_modules_music_son'+os.sep+'music_son_base_sox.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_avchd.py présent dans le rep. gui_modules_music_son
totalFichiersSource += ' gui_modules_music_son'+os.sep+'music_son_decoupe.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_avchd.py présent dans le rep. gui_modules_music_son
totalFichiersSource += ' gui_modules_music_son'+os.sep+'music_son_encodage.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_avchd.py présent dans le rep. gui_modules_music_son
totalFichiersSource += ' gui_modules_music_son'+os.sep+'music_son_join_multiplefile.py'

######## Rajouté le 14/11/09 ###########################################
# Ajout du fichier ffmpeg_avchd.py présent dans le rep. gui_modules_music_son
totalFichiersSource += ' gui_modules_music_son'+os.sep+'music_son_normalize.py'

# Ajout du script principal
totalFichiersSource += ' ekd_gui.py'

'''
print
print u'Création des fichiers .po pour: '
print
print totalFichiersSource  # test
print
'''
EkdPrint('')
EkdPrint(u'Création des fichiers .po pour: ')
EkdPrint(totalFichiersSource)  # test
EkdPrint('')

# commande de création des fichier-sources de traduction *.pot (un pour l'interface de base et l'autre pour l'aide)
os.system("xgettext --no-wrap -o locale/ekd.po " + totalFichiersSource)
os.system("xgettext --no-wrap -k --keyword='tr' -o locale/ekdDoc.po " + totalFichiersSource)
