# -*- coding: utf-8 -*-

import os, string
from PyQt4.QtCore import QThread, QProcess, QByteArray, QString, SIGNAL, pyqtSignature
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdTools import debug

from moteur_modules_animation.mplayer import getParamVideo

############################################################################################
# Merci à l'auteur de: http://snippets.prendreuncafe.com/snippets/tagged/pyqt/order_by/date
# pour son code ... et son aide
############################################################################################

class MencoderConcatThread(QThread):

	def __init__(self, cheminVideoEntre, valeurNum=0, cheminMEncoder=None):

		QThread.__init__(self)

		self.cancel = False

		#=== Paramètres généraux ===#

		self.repTampon = unicode(EkdConfig.getTempDir() + os.sep)
		# Répertoire de sauvegarde ds le rep tampon
		self.rep_video_ext_resol = self.repTampon  + u'video_extension_resol' + os.sep

		# Uniquement pour Linux et MacOSX
		if os.name in ['posix', 'mac'] or not cheminMEncoder :
			self.cheminMEncoder=u"mencoder"

		# Uniquement pour windows
		elif os.name == 'nt' and cheminMEncoder :
			self.cheminMEncoder=unicode(cheminMEncoder)

		# chemin(s) des vidéos chargées
		self.cheminVideoEntre = cheminVideoEntre

		# valeur de la boite de spin pour l'encodage
		self.valeurNum = valeurNum


	def infoAudio(self):


		# Remplissage de la liste pour vérifier si au moins une des vidéos
		# du lot n'a pas de canal audio (voir dans la fonction appliquer)
		self.listeNoAudio = []
		for parc_audio in self.cheminVideoEntre:

			#### La récupération directer fonctionne elle ###########
			infos = {'Fichier':parc_audio}
			getParamVideo(parc_audio, ['ID_AUDIO_CODEC'], infos)
			try:
				audioCodec = infos['ID_AUDIO_CODEC']
			except :
				audioCodec = _(u"pas d'info disponible")
			#########################################################

			if audioCodec in [u"pas d'info disponible"]:
				self.listeNoAudio.append(parc_audio)


	def run(self):

		self.infoAudio()

		for nb_1, fichier_1 in enumerate(self.cheminVideoEntre):

			if self.cancel: break

			# Si au moins une des vidéos du lot ne possède pas de canal audio (comme défini dans
			# la fonction lanceur), le paramètre -nosound est défini dans Mencoder, c'est à dire
			# que toutes les vidéos concaténées le seront sans le son.
			if len(self.listeNoAudio) >= 1:

				# Sans le son
				commande = self.cheminMEncoder+u" \""+unicode(fichier_1)+u"\" -vf scale="+unicode(self.valeurNum[0])+u":"+unicode(self.valeurNum[1])+u" -ovc lavc -lavcopts vcodec=mjpeg:vbitrate=2000:vqmin=2:vpass=1 -nosound -o \""+self.rep_video_ext_resol+u"fich_ext_"+unicode(string.zfill(str(nb_1+1), 5))+u".avi\""

			# Autrement ...
			else:
				# Avec du son
				commande = self.cheminMEncoder+u" \""+unicode(fichier_1)+u"\" -vf scale="+unicode(self.valeurNum[0])+u":"+unicode(self.valeurNum[1])+u" -ovc lavc -lavcopts vcodec=mjpeg:vbitrate=2000:vqmin=2:vpass=1 -oac pcm -srate 44100 -o \""+self.rep_video_ext_resol+u"fich_ext_"+unicode(string.zfill(str(nb_1+1), 5))+u".avi\""

			try:
				self.sp = QProcess()
				self.connect(self.sp, SIGNAL('readyReadStandardOutput()'), self.recupSortie)
				self.connect(self.sp, SIGNAL('finished(int)'), self.fin)
				self.sp.start("%s" % commande)
				debug("Debug:: %s" % commande)
				###

			except Exception, e:
				debug (u"Erreur dans le lancement de %s : %s" % (commande, e))

			# Ca marche mieux avec pourcent calculé comme ça
			pourcent=((nb_1+1)*100)/len(self.cheminVideoEntre)

			# Emetteur pour la récup des valeurs du pourcentage
			self.emit(SIGNAL("increment(int)"), pourcent)

			# Emetteur pour (essayer) d'afficher chaque fichier chargé
			# (pour info) au bon moment dans la barre de progression
			self.emit(SIGNAL("travail_avec_fichier"), fichier_1)

			debug("%d " % (nb_1))
			self.sp.waitForFinished()
			
	def recupSortie(self):
		""" Travail avec les QProcess"""
		self.tampon = QByteArray(self.sp.readLine())

	def fin(self, returnCode):
		""" Travail avec les QProcess"""
		if returnCode == QProcess.CrashExit:
			debug(QString(self.sp.readAllStandardError()))
			debug(QString(self.sp.readAllStandardOutput()))
			raise Exception(_(u"Erreur de traitement lors de la concatenation"))

	@pyqtSignature("")
	def cancel(self):
		"""SLOT to cancel treatment"""
		self.cancel = True


