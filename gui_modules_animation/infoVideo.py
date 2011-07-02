#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog, QVBoxLayout, QLabel, QPushButton, QIcon
import os
from moteur_modules_animation.mplayer import getParamVideo
from moteur_modules_common import EkdProcess
from moteur_modules_animation.tags import Tags

class infovideo(QObject):
	def __init__(self, video = None, audio = False): 
		self.info = ""
		self.video = video
		self.audio = audio
		if video != None:
			self.setVideo(video)
			self.getInfos()

	def getInfos(self):
		def lTab(param, valeur):
			"renvoie une ligne du tableau"
			return "<tr><td>"+param+"</td><td>"+unicode(valeur)+"</td></tr>"
		
		import subprocess

		fichier_lu = self.video
	
		try:
			# Si le codec audio détecté est mad, il est remplacé par ac3
			if self.audioCodec == 'mad': self.audioCodec = 'ac3'
			
			# Slicing pour ne récupérer que les parties essentielles des renseignements
			if self.audioCodec[0:2] == 'ff': self.audioCodec = self.audioCodec[2:]
			
			# Slicing pour ne récupérer que les parties essentielles des renseignements
			if self.video_codec[0:3] == 'ffo': self.video_codec = self.video_codec[3:]
			elif self.video_codec[0:2] == 'ff' and self.video_codec[0:3] != 'ffo': self.video_codec = self.video_codec[2:]
			
			# Si le temps détecté est inférieur a la minute ...
			if int(self.dureeTotaleVideo) < 60:
				dureeVideoAffichage = _(u" secondes")
			# Autrement si le temps détecté est superieur a la minute et inférieur à l'heure ...
			elif int(self.dureeTotaleVideo) >= 60 and int(self.dureeTotaleVideo) < 3600:
				dureeVideoAffichage = _(u" secondes (")+_(u'soit: ')+str(int(round(self.dureeTotaleVideo))/60)+_(u" min ")+str(int(round(self.dureeTotaleVideo))%60)+_(u" sec")+')'
			# Autrement si le temps détecté est superieur a l'heure ...
			elif int(self.dureeTotaleVideo) >= 3600:
				# Durée en heure(s)
				dureeH = int(round(self.dureeTotaleVideo)) / 3600
				# Durée modulo
				duree_H_Mn_Sec = int(round(self.dureeTotaleVideo)) % 3600
				# Durée en minute(s)
				dureeMn = duree_H_Mn_Sec / 60
				# Durée en seconde(s)
				dureeSec = duree_H_Mn_Sec % 60
				# Durée détail
				dureeVideoAffichage = _(u" secondes (")+_(u'soit: ')+str(int(dureeH))+_(u" h ")+str(int(dureeMn))+_(u" min ")+str(int(dureeSec))+_(u" sec")+')'
				
			# Si une vidéo OGG THEORA est ouverte, la récupération des données
			# se fait par FFmpeg au lieu de Mplayer (car Mplayer détecte très
			# mal la durée de la vidéo quand elle est OGG THEORA)
			if fichier_lu.endswith('ogg') or fichier_lu.endswith('ogm'):
				com = u"ffmpeg -i \"" + unicode(fichier_lu) + u"\""
				
                		# Travail avec subprocess
				# Récup des infos sur la vidéo dans une liste
                		#p1=subprocess.Popen(com, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
                		p1 = EkdProcess(com, outputerr=subprocess.STDOUT)
                		lignesSortie_1=p1.stdout.readlines()
                		p1.wait()
				# Séparation des parties avec un espace pour une meilleure récupération
                		recupDonnVid = "".join(lignesSortie_1).split(' ')
				
				# Récupération/capture de la durée de la vidéo
				for comptCom_1, lCapture in enumerate(recupDonnVid):
					if 'Duration:' in lCapture:
						# Durée vidéo. Récupération de la durée sous
						# cette forme (exemple): 00:01:47.9
						dureeVideoAffichage = _(u" secondes ") + "(" + recupDonnVid[comptCom_1 + 1][:-1] + ")"
						
			if fichier_lu.endswith('mts') or fichier_lu.endswith('m2ts') or fichier_lu.endswith('MTS') or fichier_lu.endswith('M2TS'):
				com = u"ffmpeg -i \"" + unicode(fichier_lu) + u"\""
				
                		# Travail avec subprocess
				# Récup des infos sur la vidéo dans une liste
                		#p2=subprocess.Popen(com, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
                		p2 = EkdProcess(com, outputerr=subprocess.STDOUT)
                		lignesSortie_2=p2.stdout.readlines()
                		p2.wait()
		
				# Séparation des parties avec un espace pour une meilleure récupération
                		recupDonnVid = "".join(lignesSortie_2).split(' ')
				
				# Récupération/capture de la durée de la vidéo
				for comptCom_2, lCapture in enumerate(recupDonnVid): 
					if 'Duration:' in lCapture:
						# Durée vidéo. Récupération de la durée sous 
						# cette forme (exemple): 00:01:47.9
						self.dureeTotaleVideo = recupDonnVid[comptCom_2 + 1][:-1]
						
						# Constitution d'une liste avec les valeurs de heure, 
						# minute, seconde sous cette forme ['00', '01', '47.9']
						lCalc_D = "".join(self.dureeTotaleVideo).split(':')

						lSecond = []
						# Les données de temps affichées ds FFmpeg ne sont pas directement exploitables
						# Il y a des choses à transformer ... surtout si on trouve des '00'
						if lCalc_D[0][0]=='0': 
							lCalc_D[0]=float(lCalc_D[0][1])
							lSecond.append(float(lCalc_D[0]))
						elif lCalc_D[0][0]!='0':
							lSecond.append(float(lCalc_D[0]))
						if lCalc_D[1][0]=='0': 
							lCalc_D[1]=float(lCalc_D[1][1])
							lSecond.append(float(lCalc_D[1]))
						elif lCalc_D[1][0]!='0':
							lSecond.append(float(lCalc_D[1]))
						if lCalc_D[2][0]=='0': 
							lCalc_D[2]=float(lCalc_D[2][1])
							lSecond.append(float(lCalc_D[2]))
						elif lCalc_D[2][0]!='0':
							lSecond.append(float(lCalc_D[2]))

						# Calcul de la durée de la vidéo en secondes
						self.dureeVideoSec = str(float((lSecond[0] * 60.0) + (lSecond[1] * 60.0) + lSecond[2]))
						# Retour à la variable d'origine
						self.dureeTotaleVideo = self.dureeVideoSec
						
						dureeVideoAffichage = _(u" secondes ") + "(" + recupDonnVid[comptCom_2 + 1][:-1] + ")"
						
					if 'Video:' in lCapture:
						# Récup Format vidéo
						self.videoFormat = recupDonnVid[comptCom_2 + 1][:-1]
						# Récup Codec vidéo
						self.video_codec  = recupDonnVid[comptCom_2 + 2][:-1]
						# Recup Taille de la vidéo
						# ------------------------------------------------------
						# Si une donnée du style: [PAR': 4:3 DAR 16:9], ou 
						# [PAR 1:1 DAR 16:9], est présente (ce qui est certainement
						# le cas dans les nouvelles versions de FFmpeg ...)
						# ------------------------------------------------------
						if recupDonnVid[comptCom_2 + 4] == '[PAR':
							pre_recup_larg_haut_1 = recupDonnVid[comptCom_2 + 3]
						# Autrement ...
						else:
							pre_recup_larg_haut_1 = recupDonnVid[comptCom_2 + 3][:-1]
						pre_recup_larg_haut_2 = pre_recup_larg_haut_1.split('x')
						self.videoLargeur = pre_recup_larg_haut_2[0]
						self.videoHauteur = pre_recup_larg_haut_2[1]
						# Récup Nombre d'images/secondes
						# ------------------------------------------------------
						# Si une donnée du style: [PAR': 4:3 DAR 16:9], ou 
						# [PAR 1:1 DAR 16:9], est présente (ce qui est certainement
						# le cas dans les nouvelles versions de FFmpeg ...)
						# ------------------------------------------------------
						if recupDonnVid[comptCom_2 + 4] == '[PAR':
							self.imgParSec = recupDonnVid[comptCom_2+8]
						# Autrement ...
						else:
							pre_recup_img_sec_1 = recupDonnVid[comptCom_2 + 4][:-1]
							pre_recup_img_sec_2 = pre_recup_img_sec_1.split(' ')
							self.imgParSec = pre_recup_img_sec_2[0]
						
					if 'bitrate:' in lCapture:
						# Récup du bitrate
						pre_recup_bitrate_1 = recupDonnVid[comptCom_2 + 1]
						pre_recup_bitrate_2 = pre_recup_bitrate_1.split(' ')
						self.videoBitrate = pre_recup_bitrate_2[0]
			
			# Si une vidéo AVCHD est chargée par l'utilisateur le bitrate n'a 
			# pas la même valeur que pour une vidéo non AVCHD
			if fichier_lu.endswith('mts') or fichier_lu.endswith('m2ts') or fichier_lu.endswith('MTS') or fichier_lu.endswith('M2TS'):
				self.videoBitrate = float(self.videoBitrate)
			else: self.videoBitrate = float(self.videoBitrate)/1000.0
			
			self.audioBitrate = float(self.audioBitrate)/1000.0
			
		except: pass
		

		### Les chiffres en int ont été remplace par des float ###
		### Exemple 1000 --> 1000.0 (pour afficher le nombre de chiffres après la vigule #########

		##########################################################################################
		# Le 01/09/10 Ajout des infos pour les Tags vidéo (Non, Artiste, Genre, Copyright
		# et Commentaire(s)
		self.info = '<html><center>' + _(u"Emplacement") + ': ' + fichier_lu + '<br /><br />' + \
			"<table>" + \
			lTab(_(u"Entête vidéo"), str(self.demux)) + \
			lTab(_(u"Format vidéo"), str(self.videoFormat)) + \
			lTab(_(u"Codec vidéo"), str(self.video_codec)) + \
			lTab(_(u"Bitrate vidéo (kbps)"), str(self.videoBitrate)) + \
			lTab(_(u"Taille de la vidéo (largeur x hauteur)   "), str(self.videoLargeur)+' x '+str(self.videoHauteur)) + \
			lTab(_(u"Nombre d'images/secondes"), str(self.imgParSec)) + \
			lTab(_(u"Durée de la vidéo"), str(self.dureeTotaleVideo) + dureeVideoAffichage)
                for t in self.tags.keys() :
                        self.info += lTab(_(u"<b>Tag</b> vidéo : %s</b>" % t), str(self.tags[t]))
                self.info += lTab(_(u"Codec audio"), str(self.audioCodec)) + \
			lTab(_(u"Fréquence audio (Hz)"), str(self.audioRate)) + \
			lTab(_(u"Bitrate audio (kbps)"), str(self.audioBitrate)) + \
			lTab(_(u"Poids de la vidéo"), str(float(os.path.getsize(fichier_lu)/1000.0))+_(u' ko (soit: ')+str(float(os.path.getsize(fichier_lu)/1000000.0))+_(u' méga)')+'\n') + \
			"</table></center></html>"
		##########################################################################################

		if self.audio :
			try:
				# Si le codec audio détecté est mad, il est remplacé par ac3
				if self.audioCodec == 'mad': self.audioCodec = 'ac3'
				
				# Si le temps détecté est inférieur a la minute ...
				if int(self.dureeTotaleVideo) < 60:
					dureeVideoAffichage = _(u" secondes")
				# Autrement si le temps détecté est superieur a la minute et inférieur à l'heure ...
				elif int(self.dureeTotaleVideo) >= 60 and int(self.dureeTotaleVideo) < 3600:
					dureeVideoAffichage = _(u" secondes (")+_(u'soit: ')+str(int(round(self.dureeTotaleVideo))/60)+_(u" min ")+str(int(round(self.dureeTotaleVideo))%60)+_(u" sec")+')'
				# Autrement si le temps détecté est superieur a l'heure ...
				elif int(self.dureeTotaleVideo) >= 3600:
					# Durée en heure(s)
					dureeH = int(round(self.dureeTotaleVideo)) / 3600
					# Durée modulo
					duree_H_Mn_Sec = int(round(self.dureeTotaleVideo)) % 3600
					# Durée en minute(s)
					dureeMn = duree_H_Mn_Sec / 60
					# Durée en seconde(s)
					dureeSec = duree_H_Mn_Sec % 60
					# Durée détail
					dureeVideoAffichage = _(u" secondes (")+_(u'soit: ')+str(int(dureeH))+_(u" h ")+str(int(dureeMn))+_(u" min ")+str(int(dureeSec))+_(u" sec")+')'
					
					
				# Si un fichier audio OGG est ouvert, la récupération des données
				# se fait par FFmpeg au lieu de Mplayer (car Mplayer détecte très 
				# mal la durée du fichier audio quand il est OGG)
				if fichier_lu.endswith('ogg'):
					com = 'ffmpeg -i ' + "\"" + unicode(fichier_lu) + "\""
				
                			# Travail avec subprocess 
					# Récup des infos sur la vidéo dans une liste
                			#p1=subprocess.Popen(com, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
                			p1 = EkdProcess(com, outputerr=subprocess.STDOUT)
                			lignesSortie_1=p1.stdout.readlines()
                			p1.wait()
		
					# Séparation des parties avec un espace pour une meilleure récupération
                			recupDonnVid = "".join(lignesSortie_1).split(' ')
				
					# Récupération/capture de la durée de la vidéo
					for comptCom_1, lCapture in enumerate(recupDonnVid): 
						if 'Duration:' in lCapture:
							# Durée vidéo. Récupération de la durée sous 
							# cette forme (exemple): 00:01:47.9
							dureeVideoAffichage = _(u" secondes ") + "(" + recupDonnVid[comptCom_1 + 1][:-1] + ")"
				
				self.audioBitrate = float(self.audioBitrate)/1000.0
			except: pass
			

			### Les chiffres en int ont été remplace par des float ###
			### Exemple 1000 --> 1000.0 (pour afficher le nombre de chiffres après la vigule #########
			self.info = '<html><center>' + _(u"Emplacement") + ': ' + fichier_lu + '<br /><br />' + \
				"<table>" + \
				lTab(_(u"Entête du fichier"), str(self.demux)) + \
				lTab(_(u"Durée du fichier audio"), str(self.dureeTotaleVideo) + dureeVideoAffichage) + \
				lTab(_(u"Codec audio"), str(self.audioCodec)) + \
				lTab(_(u"Fréquence audio (Hz)"), str(self.audioRate)) + \
				lTab(_(u"Bitrate audio (kbps)"), str(self.audioBitrate)) + \
				lTab(_(u"Poids du fichier audio"), str(float(os.path.getsize(fichier_lu)/1000.0))+_(u' ko (soit: ')+str(float(os.path.getsize(fichier_lu)/1000000.0))+_(u' méga)')+'\n') + \
				"</table></center></html>"
		
		return self.info


	def setVideo(self, video):
		'''
		Met à jour les infos de la vidéo donnée en paramètre
		'''
		##############################################################################################
		# Le 01/09/10 Ajout de Name, Artist, Genre, Subject, Copyright et Comments
		self.video = video
		self.infos = {'Fichier':video}
		getParamVideo(self.video, ['ID_DEMUXER', 'ID_VIDEO_FORMAT', \
						   'ID_VIDEO_CODEC', 'ID_VIDEO_BITRATE',\
						   'ID_VIDEO_WIDTH', 'ID_VIDEO_HEIGHT',\
						   'ID_VIDEO_FPS', 'ID_LENGTH', \
						   'ID_AUDIO_CODEC', 'ID_AUDIO_RATE',\
						   'ID_AUDIO_BITRATE'], self.infos)
		##############################################################################################

		try :
			self.demux = self.infos['ID_DEMUXER']
		except :
			self.demux = _(u"pas d'info disponible")
		try:
			self.videoFormat = self.infos['ID_VIDEO_FORMAT']
		except :
			self.videoFormat = _(u"pas d'info disponible")
		try:
			self.video_codec = self.infos['ID_VIDEO_CODEC']
		except :
			self.video_codec = _(u"pas d'info disponible")
		try:
			self.videoBitrate = int(self.infos['ID_VIDEO_BITRATE'])
		except :
			self.videoBitrate = _(u"pas d'info disponible")
		try:
			self.videoLargeur = int(self.infos['ID_VIDEO_WIDTH'])
		except :
			self.videoLargeur = _(u"pas d'info disponible")
		try:
			self.videoHauteur = int(self.infos['ID_VIDEO_HEIGHT'])
		except :
			self.videoHauteur = _(u"pas d'info disponible")
		try:
			self.imgParSec = self.infos['ID_VIDEO_FPS']
		except :
			self.imgParSec = _(u"pas d'info disponible")
		try:
			self.dureeTotaleVideo = self.infos['ID_LENGTH']
		except :
			self.dureeTotaleVideo = _(u"pas d'info disponible")
		######################################################################################
		# Le 01/09/10 Ajout de Name, Artist, Genre, Subject, Copyright et Comments
                self.tags = Tags(self.video).get_tags()
		######################################################################################
		try:
			self.audioCodec = self.infos['ID_AUDIO_CODEC']
		except :
			self.audioCodec = _(u"pas d'info disponible")
		try:
			self.audioRate = int(self.infos['ID_AUDIO_RATE'])
		except :
			self.audioRate = _(u"pas d'info disponible")
		try:
			self.audioBitrate = int(self.infos['ID_AUDIO_BITRATE'])
		except :
			self.audioBitrate = _(u"pas d'info disponible")

		
class InfosVideo(QDialog):
	"Affiche les informations de la video dans une boite de dialogue"
	
	def __init__(self, video = None, audio = False):
		QDialog.__init__(self)
		self.audio = audio
		if self.audio :
			self.setWindowTitle(_(u"Informations sur le fichier audio"))
		else :
			self.setWindowTitle(_(u"Informations sur la vidéo"))
		
		vbox = QVBoxLayout()
		self.setLayout(vbox)
		
		self.label = QLabel()
		if PYQT_VERSION_STR >= "4.1.0":
			self.label.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
		vbox.addWidget(self.label)

		self.info = infovideo(video, self.audio)
		self.setVideo(video)

		boutonFermer = QPushButton(_(u"Revenir"))
		boutonFermer.setIcon(QIcon("Icones" + os.sep + "revenir.png"))
		self.connect(boutonFermer, SIGNAL('clicked()'), SLOT('close()'))

		vbox.addWidget(boutonFermer)
		

	def setVideo(self, video):
		'''
		Met à jour les infos de la vidéo donnée en paramètre
		'''
		self.info.setVideo(video)
		self.updateInfos()


	def updateInfos(self):
		'''
		Met à jour les informations de la video
		'''
		self.label.setText(self.info.info)

