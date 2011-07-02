# -*- coding: utf-8 -*-

import os, string, subprocess
from PyQt4.QtCore import SIGNAL, SLOT, QThread

from moteur_modules_common.EkdProcess import EkdProcess
from moteur_modules_common.EkdTools import debug
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint

############################################################################################
# Merci à l'auteur de: http://snippets.prendreuncafe.com/snippets/tagged/pyqt/order_by/date
# pour son code ... et son aide
############################################################################################

class FfmpegAvchd(QThread):

	### Ajout (le 13/08/2010) de spec_sortie_DNxHD et son_sortie_DNxHD #################
	def __init__(self, cheminVideoEntre, enregistrerSortie, codec_sortie, reso_largeur_sortie, reso_hauteur_sortie, nbreImgSec_sortie, qualite_sortie, spec_sortie_DNxHD, son_sortie_DNxHD, cheminFFmpeg=None):

		QThread.__init__(self)
		
		self.cancel = False
		
		#=== Paramètres généraux ===#
		
		# Uniquement pour Linux et MacOSX
		if os.name in ['posix', 'mac']: self.cheminFFmpeg = "ffmpeg"
			
		# Uniquement pour windows
		elif os.name == 'nt': self.cheminFFmpeg = "ffmpeg.exe"

		# chemin(s) des vidéos chargées
		self.cheminVideoEntre = cheminVideoEntre
		# Chemin + nom de fichier en sortie
		self.enregistrerSortie = enregistrerSortie
		# Sélection du codec en sortie (par l'utilisateur)
		self.codec_sortie = codec_sortie
		# Sélection de la largeur (vidéo) en sortie (par l'utilisateur)
		self.reso_largeur_sortie = reso_largeur_sortie
		# Sélection de la hauteur (vidéo) en sortie (par l'utilisateur)
		self.reso_hauteur_sortie = reso_hauteur_sortie
		# Sélection du nbr d'img/sec en sortie (par l'utilisateur)
		self.nbreImgSec_sortie = nbreImgSec_sortie
		# Sélection de la qualité (de la vidéo) en sortie (par l'utilisateur)
		self.qualite_sortie = qualite_sortie
		### Ajouté le 13/08/2010 ###################################################
		# Spécifications pour l'Avid DNxHD
		self.spec_sortie_DNxHD = spec_sortie_DNxHD
		# Choix du flux audio en sortie pour l'Avid DNxHD
		self.son_sortie_DNxHD = son_sortie_DNxHD
		############################################################################	
	
	
	def run(self):
		
		for nb_1, fichier_1 in enumerate(self.cheminVideoEntre):
			
			if self.cancel: break
			
			if self.codec_sortie == "MOV (.mov)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.mov'
				vcodec = ' -vcodec mpeg4'
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "MPEG2 (.mpg)":
				fps = ' -r 25'
				extSortie = '.mpg'
				vcodec = ' -vcodec mpeg2video'
				acodec = ' -acodec mp2 -ac 1 -ar 22050 -ab 64k'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "MPEG1 (.mpg)":
				fps = ' -r 25'
				extSortie = '.mpg'
				vcodec = ' -vcodec mpeg1video'
				acodec = ' -acodec mp2 -ac 1 -ar 22050 -ab 64k'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "VOB (.vob)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.vob'
				vcodec = ' '
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "MPEG4 (.mp4)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.mp4'
				vcodec = ' -vcodec mpeg4'
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "WMV2 (.wmv)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.wmv'
				vcodec = ' -vcodec wmv2'
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
					
			elif self.codec_sortie == "HFYU (yuv422p) (.avi)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.avi'
				vcodec = ' -vcodec huffyuv -pix_fmt yuv422p'
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "MSMPEG 4 version 2 (.avi)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.avi'
				vcodec = ' -vcodec msmpeg4v2'
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "Motion JPEG (.avi)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.avi'
				vcodec = ' -vcodec mjpeg'
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010
				
			elif self.codec_sortie == "FFV1 (FFmpeg) (.avi)":
				fps = ' -r '+str(self.nbreImgSec_sortie)
				extSortie = '.avi'
				vcodec = ' -vcodec ffv1'
				acodec = ' -acodec copy'
				qual_video = ' -qscale '+str(self.qualite_sortie) # Adapté le 13/08/2010

			### Rectification le 14/08/2010 ############################################
			elif self.codec_sortie == "Avid DNxHD (.mov)":
				# Extension sortie
				extSortie = '.mov'
				# Codec vidéo pour l'Avid DNxHD
				vcodec = ' -vcodec dnxhd'
				# Choix du flux audio pour l'Avid DNxHD
				if self.son_sortie_DNxHD == "Copie du flux audio": acodec = ' -acodec copy'
				elif self.son_sortie_DNxHD == "Flux audio PCM sur 2 canaux (stereo)": acodec = ' -ac 2 -acodec pcm_s16le'
				elif self.son_sortie_DNxHD == "Pas de flux audio": acodec = ' -an'
				# Les valeurs de qualité de la vidéo ne sont pas conservées
				qual_video = ''
				# ------------------------ #
				# Valeurs particulières
				# ------------------------ #
				if self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:29.97 Bitrate:220 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 29.97 -b 220000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:29.97 Bitrate:145 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 29.97 -b 145000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:25 Bitrate:185 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 25 -b 185000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:25 Bitrate:120 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 25 -b 120000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:25 Bitrate:36 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 25 -b 36000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:24 Bitrate:175 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 24 -b 175000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:24 Bitrate:115 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 24 -b 115000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:24 Bitrate:36 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 24 -b 36000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:23.976 Bitrate:175 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 23.976 -b 175000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:23.976 Bitrate:115 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 23.976 -b 115000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:23.976 Bitrate:36 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 23.976 -b 36000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:29.97 Bitrate:220 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 29.97 -b 220000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:29.97 Bitrate:145 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 29.97 -b 145000k'
				elif self.spec_sortie_DNxHD == "Dimension:1920x1080 Img/sec:29.97 Bitrate:45 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1920'
					self.reso_hauteur_sortie = '1080'
					# Nbre d'img/sec et bitrate
					fps = ' -r 29.97 -b 45000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:59.94 Bitrate:220 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 59.94 -b 220000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:59.94 Bitrate:145 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 59.94 -b 145000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:50 Bitrate:175 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 50 -b 175000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:50 Bitrate:115 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 50 -b 115000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:29.97 Bitrate:110 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 29.97 -b 110000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:29.97 Bitrate:75 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 29.97 -b 75000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:25 Bitrate:90 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 25 -b 90000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:25 Bitrate:60 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 25 -b 60000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:23.976 Bitrate:90 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 23.976 -b 90000k'
				elif self.spec_sortie_DNxHD == "Dimension:1280x720 Img/sec:23.976 Bitrate:60 Mb/s": 
					# Taille largeur x hauteur
					self.reso_largeur_sortie = '1280'
					self.reso_hauteur_sortie = '720'
					# Nbre d'img/sec et bitrate
					fps = ' -r 23.976 -b 60000k'
			############################################################################
	
			commande = self.cheminFFmpeg+' -i '+"\""+fichier_1+"\""+' -s '+self.reso_largeur_sortie+'x'+self.reso_hauteur_sortie+fps+vcodec+acodec+qual_video+' -y '+"\""+self.enregistrerSortie+'_'+string.zfill(str(nb_1+1), 5)+extSortie+"\""
			outputfile = self.enregistrerSortie+'_'+string.zfill(str(nb_1+1), 5)+extSortie

			EkdPrint(u'commande %s' % commande)

			try:
				## Travail avec subprocess
				## sp = subprocess.Popen(commande, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)

				# Travail avec EkdProcess, bien
				sp = EkdProcess(commande, outputerr=subprocess.STDOUT)
				# Important permet le traitement (!)
				self.tampon = sp.stdout.readlines()
			except Exception:
				debug(u"Erreur dans le lancement de %s" % commande)
			
			# Ca marche mieux avec pourcent calculé comme ça
			pourcent=((nb_1+1)*100)/len(self.cheminVideoEntre)

			# Emetteur pour la récup des valeurs du pourcentage
			self.emit(SIGNAL("increment(int)"), pourcent)

			# Emetteur pour (essayer) d'afficher chaque fichier chargé
			# (pour info) au bon moment dans la barre de progression
			self.emit(SIGNAL("travail_avec_fichier"), fichier_1, outputfile)
			
			debug ("%d "%(nb_1))
	
		self.emit(SIGNAL("fin process"))
	
	def cancel(self):
		"""SLOT to cancel treatment"""
		self.cancel = True
