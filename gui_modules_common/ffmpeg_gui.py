# -*- coding: utf-8 -*-

import sys, os, re
import subprocess
from PyQt4.QtGui import QDialog, QLabel, QTextEdit, QPushButton, QProgressBar, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt4.QtCore import PYQT_VERSION_STR, SIGNAL, QProcess, QByteArray, QObject, QString, QThread, Qt

from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_animation.infoVideo import infovideo
from moteur_modules_animation.ffmpeg import FFmpeg
from moteur_modules_common.EkdTools import debug

class WidgetFFmpeg(QDialog):

    def __init__(self, idCodec, cheminVideoEntre, cheminSorti, valeurNum=0, laisserOuvert=1, tailleIm=None, tailleVideo=None, systeme=None, cheminFfmpeg=None, tempsApercu=None, optionSpeciale=None, cheminMPlayer=None):

        """widget ffmpeg"""
        super(WidgetFFmpeg, self).__init__()

        self.cheminFfmpeg=u"ffmpeg"

        self.cheminVideoEntre = unicode(cheminVideoEntre)
        self.cheminSorti = unicode(cheminSorti)

        # identifiant du codec
        self.idCodec = idCodec

        # valeur de la boite de spin pour l'encodage
        self.valeurNum = valeurNum

        # dimension des images (liste de 2 éléments)
        self.tailleIm = tailleIm

        # dimension de la vidéo (liste de 2 éléments)
        self.tailleVideo = tailleVideo

        # laisser ouvert la fenêtre après encodage
        self.laisserOuvert = laisserOuvert

        # Conversion minimale du filtre pour avoir un aperçu.
        # Indique le temps où l'aperçu doit être créé
        self.tempsApercu = tempsApercu

        # drapeau pour ne pas lancer 2 fois l'encodage
        self.estLancee = False

        # Est-ce que le 1er % de progression a été récupéré (utile pour montage vidéo -> découper)?
        self.__recupPourcentDebut = 0

        # Pour le son lors de la découpe vidéo pour l'instant
        if optionSpeciale!=None:
            self.optionSpeciale = optionSpeciale

        self.resize(500, 100)

        #=== Widgets ===#

        self.labelAttente=QLabel()
        self.labelAttente.setText(_(u"Attendez la fin du calcul s'il vous plaît, soyez patient !"))

        self.zoneTexte = QTextEdit("") # là où s'afficheront les infos
        if PYQT_VERSION_STR < "4.1.0":
            self.zoneTexte.setText = self.zoneTexte.setPlainText
        self.zoneTexte.setReadOnly(True)
        self.zoneTexte.setText("#######\n# LOG :\n#######\n")
        self.zoneTexte.hide()

        self.bout_annuler = QPushButton(_(u"Annuler"))

        self.bout_preZoneTexte = QPushButton(_("Voir les informations de l'encodage"))
        self.bout_preZoneTexte.hide()

        self.pbar = QProgressBar()
        self.pbar.setMaximum(100)

        vbox = QVBoxLayout()
        vbox.addWidget(self.labelAttente)
        vbox.addWidget(self.bout_preZoneTexte)
        vbox.addWidget(self.zoneTexte)
        hbox = QHBoxLayout()
        hbox.addWidget(self.pbar)
        hbox.addWidget(self.bout_annuler)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.ffmpegProcess = FFmpeg(inputfile = unicode(self.cheminVideoEntre), outputfile = unicode(self.cheminSorti), codec = self.idCodec, imgsize = self.tailleIm, videosize = self.tailleVideo)

        #=== connexion des widgets à des fonctions ===#
        self.connect(self.ffmpegProcess, SIGNAL('progress(int)'), self.pbar.setValue)
        self.connect(self.ffmpegProcess, SIGNAL('log(QString)'), self.zoneTexte.append)
        self.connect(self.ffmpegProcess, SIGNAL('finished(int)'), self.finEncodage)
        self.connect(self.bout_annuler, SIGNAL('clicked()'), self.close)
        self.connect(self.bout_preZoneTexte, SIGNAL('clicked()'), self.afficherLog)

        ## On sort cette partie qui ne doit pas être lancée dans l'init de l'objet.
        # Uniquement FFmpeg
        #self.demarrerEncodeur('Ffmpeg')

    def setVideoLen(self, videoLen) :
        self.ffmpegProcess.setVideoLen(videoLen)

    def close(self):
        """ Annule le traitement en cours """
        self.ffmpegProcess.cancel()
        self.ffmpegProcess.wait()
        #super(WidgetFFmpeg, self).close() # Python 2.6
        QDialog.close(self)

    def exec_(self):
        """ Surcharge de la fonction exec permettant l'execution hors de l'init"""
        self.demarrerEncodeur('Ffmpeg')
        #super(WidgetFFmpeg, self).exec_() # Python 2.6
        QDialog.exec_(self)

    def demarrerEncodeur(self, encodeur):
        """démarrage de mencoder avec les arguments choisis"""

        if self.estLancee == False: # pas question de démarrer 2 fois l'encodage
            commande = None
            has_audio = False

            debug('\n')

            # Si la conversion d'images en vidéo est sélectionné, aucune
            # info Mplayer n'est affichée (problème de récup infos par Mplayer)
            if self.idCodec in ['mpeg1video', 'mjpeg', 'h263p', 'mpeg4', 'msmpeg4v2', 'ljpeg', 'dv', 'huffyuv', 'mov', 'flv', 'mp4', 'vob']:
                # ICI SI LES FICHIERS CHARGES SONT DES IMAGES
                a = "###############################"
                b = "# Informations sur les images :"
                c = "###############################"

                infos = '\n'+a+'\n'+b+'\n'+c+'\n'
                debug(infos)
                self.zoneTexte.append(infos)

                import glob
                # Le chemin pour l'affichage des infos sur les images ne fonctionnait
                # plus après la nouvelle structure des fichiers temporaires
                self.recupTempImgAnim = glob.glob(EkdConfig.getTempDir() + os.sep + "*.*")
                self.recupTempImgAnim.sort()
                # Affichage du chemin (temp) + le poids de chaque image
                # --> Une énumération de parcours a été introduite
                for parcNb, parcInfIm in enumerate(self.recupTempImgAnim):
                    debug('* '+str(parcNb+1)+'. '+parcInfIm+' --> '+str(float(os.path.getsize(parcInfIm)/1000))+' ko'+'\n')
                    self.zoneTexte.append('* '+str(parcNb+1)+'. '+parcInfIm+' --> '+str(float(os.path.getsize(parcInfIm)/1000))+' ko'+'\n')

                # Elimination de la dernière image de la liste car car elle
                # s'affiche en double ds la fenêtre information de l'encodage
                # et aussi ds la console
                #self.log = self.log[:len(self.log)-1]

                # On définie la longueur de la futur vidéo en divisant le nombre d'image par le
                # nombre d'image par seconde (valeurNum ici)
                self.ffmpegProcess.setVideoLen(len(self.recupTempImgAnim) / int(self.valeurNum))

            # Pour les traitements autres que la transformation des images en vidéo
            if self.idCodec not in ['mpeg1video', 'mjpeg', 'h263p', 'mpeg4', 'msmpeg4v2', 'ljpeg', 'dv', 'huffyuv', 'mov', 'flv', 'mp4', 'vob']:

                a = "########################"
                b = "# Informations MPlayer :"
                c = "########################"

                infos = '\n'+a+'\n'+b+'\n'+c+'\n'
                debug(infos)
                ######## Ajouté le 24/07/09 ##################################################################
                # Utilisation de la classe infovideo (et en particilier la fonction setVideo)
                # présents dans gui_modules_animation/infoVideo.py
                info = infovideo(self.cheminVideoEntre)

                id_filename = 'ID_FILENAME='+self.cheminVideoEntre+'\n'
                debug(id_filename)
                id_demuxer = 'ID_DEMUXER='+info.demux+'\n'
                debug(id_demuxer)
                id_video_format = 'ID_VIDEO_FORMAT='+info.videoFormat+'\n'
                debug(id_video_format)
                id_video_codec = 'ID_VIDEO_CODEC='+info.video_codec+'\n'
                debug(id_video_codec)
                id_video_bitrate = 'ID_VIDEO_BITRATE='+str(info.videoBitrate)+'\n'
                debug(id_video_bitrate)
                id_video_largeur = 'ID_VIDEO_WIDTH='+str(info.videoLargeur)+'\n'
                debug(id_video_largeur)
                id_video_hauteur = 'ID_VIDEO_HEIGHT='+str(info.videoHauteur)+'\n'
                debug(id_video_hauteur)
                id_img_par_sec = 'ID_VIDEO_FPS='+str(info.imgParSec)+'\n'
                debug(id_img_par_sec)
                ##### Donnée très importante pour la suite du calcul (pour ffmpeg.py et ffmpeg2theora) ####
                self.dureeTotaleVideo = float(info.dureeTotaleVideo)
                ###########################################################################################
                id_duree_totale_video = 'ID_LENGTH='+str(info.dureeTotaleVideo)+'\n'
                debug(id_duree_totale_video)
                id_audio_codec = 'ID_AUDIO_CODEC='+info.audioCodec+'\n'
                debug(id_audio_codec)
                id_audio_rate = 'ID_AUDIO_RATE='+str(info.audioRate)+'\n'
                debug(id_audio_rate)
                id_audio_bitrate = 'ID_AUDIO_BITRATE='+str(info.audioBitrate)+'\n'
                debug(id_audio_bitrate)

                self.zoneTexte.append(infos+id_filename+id_demuxer+id_video_format+id_video_codec+id_video_bitrate+id_video_largeur+id_video_hauteur+id_img_par_sec+id_duree_totale_video+id_audio_codec+id_audio_rate+id_audio_bitrate)
                ##############################################################################################
                ## On définie la longueur de la vidéo pour le process
                self.ffmpegProcess.setVideoLen(self.dureeTotaleVideo)

                if info.audioCodec :
                    has_audio = True

            debug('\n')

            a = "############################"
            b = "# Informations %s :" %encodeur
            c = "############################"


            infos = '\n'+a+'\n'+b+'\n'+c+'\n'
            debug(infos)
            self.zoneTexte.append(infos)

            if self.idCodec=='codec_dv_ffmpeg':
                self.ffmpegProcess.commandeFfmpegEncodageDv()
	    elif self.idCodec=='codec_mov_ffmpeg':
		#### Enlevé le 09/04/11 ##############################
		#self.ffmpegProcess.commandeFfmpegEncodageMov()
		######################################################
		#### Ajouté/rectifié le 09/04/11 #####################
                self.ffmpegProcess.commandeFfmpegEncodageMov(comp = self.valeurNum[0], size = self.valeurNum[1])
		######################################################
	    elif self.idCodec=='codec_hfyu_ffmpeg':
		#### Enlevé le 10/04/11 ##############################
                #self.ffmpegProcess.commandeFfmpegEncodageHfyu(audio = has_audio)
		######################################################
		#### Ajouté/rectifié le 10/04/11 #####################
                self.ffmpegProcess.commandeFfmpegEncodageHfyu(size = self.valeurNum, audio = has_audio)
		######################################################
            elif self.idCodec=='codec_vob_ffmpeg':
                self.ffmpegProcess.commandeFfmpegEncodageVob(vquantizer = self.valeurNum)
            elif self.idCodec=='codec_3GP_ffmpeg':
		#### Enlevé le 30/03/11 ##############################
                #self.ffmpegProcess.commandeFfmpegEncodage3gp(audio = has_audio)
		#### Ajouté/rectifié le 30/03/11 #####################
		self.ffmpegProcess.commandeFfmpegEncodage3gp(size = self.valeurNum)
		######################################################
            elif self.idCodec=='codec_AMV_ffmpeg':
		#### Rectifié le 30/03/11 ## Ajout de size ###########
                self.ffmpegProcess.commandeFfmpegEncodageAMV(size = self.valeurNum)
		######################################################
            elif self.idCodec=='idx':
                self.ffmpegProcess.commandeFfmpegNbrImgSec(rate = self.valeurNum)
            elif self.idCodec in ['mpeg1video', 'mjpeg', 'h263p', 'mpeg4', 'msmpeg4v2', 'ljpeg', 'dv', 'huffyuv', 'mov', 'flv', 'mp4', 'vob']:
                self.ffmpegProcess.commandeFfmpegConvertImg(rate = self.valeurNum, size = "%sx%s" % (self.tailleIm[0], self.tailleIm[1]), vcodec = self.idCodec)

	    # --------------------------------------------------------------------------------- #
	    # Traitement pour chaque entrée concernant la HD (classique, en dehors du codec Avid DNxHD)
	    # --------------------------------------------------------------------------------- #
            elif self.idCodec in ['hd_1920x1080_mov__pcm_s16be__16/9', 'hd_1280x720_mov__pcm_s16be__16/9', 'hd_1440x1080_mov__pcm_s16be__4/3']:
                ## FIXME : La taille est récupérée du nom de idCodec (crade)
                self.ffmpegProcess.commandeFfmpegConvHD(size = self.idCodec.split("_")[1])

	    ### Ajouté le 19/08/10 (Gestion du codec Avid DNxHD) ################################
	    # --------------------------------------------------------------------------------- #
	    # Traitement pour chaque entrée (24) concernant le codec Avid DNxHD pour la HD
	    # --------------------------------------------------------------------------------- #
            elif self.idCodec=='hd_dnxhd_1920x1080_29.97_220_mbs':
                ## FIXME : Les éléments utiles sont récupérés du nom de idCodec (crade mais utile)
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 1
	    elif self.idCodec=='hd_dnxhd_1920x1080_29.97_145_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 2
	    elif self.idCodec=='hd_dnxhd_1920x1080_25_185_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 3
	    elif self.idCodec=='hd_dnxhd_1920x1080_25_120_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 4
	    elif self.idCodec=='hd_dnxhd_1920x1080_25_36_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 5
	    elif self.idCodec=='hd_dnxhd_1920x1080_24_175_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 6
	    elif self.idCodec=='hd_dnxhd_1920x1080_24_115_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 7
	    elif self.idCodec=='hd_dnxhd_1920x1080_24_36_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 8
	    elif self.idCodec=='hd_dnxhd_1920x1080_23.976_175_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 9
	    elif self.idCodec=='hd_dnxhd_1920x1080_23.976_115_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 10
	    elif self.idCodec=='hd_dnxhd_1920x1080_23.976_36_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 11
	    elif self.idCodec=='hd_dnxhd_1920x1080_29.97_220_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 12
	    elif self.idCodec=='hd_dnxhd_1920x1080_29.97_145_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 13
	    elif self.idCodec=='hd_dnxhd_1920x1080_29.97_45_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 14
	    elif self.idCodec=='hd_dnxhd_1280x720_59.94_220_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 15
	    elif self.idCodec=='hd_dnxhd_1280x720_59.94_145_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 16
	    elif self.idCodec=='hd_dnxhd_1280x720_50_175_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 17
	    elif self.idCodec=='hd_dnxhd_1280x720_50_115_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 18
	    elif self.idCodec=='hd_dnxhd_1280x720_29.97_110_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 19
	    elif self.idCodec=='hd_dnxhd_1280x720_29.97_75_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 20
	    elif self.idCodec=='hd_dnxhd_1280x720_25_90_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 21
	    elif self.idCodec=='hd_dnxhd_1280x720_25_60_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 22
	    elif self.idCodec=='hd_dnxhd_1280x720_23.976_90_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 23
	    elif self.idCodec=='hd_dnxhd_1280x720_23.976_60_mbs':
                self.ffmpegProcess.commandeFfmpegConvHD_DNxHD(size=self.idCodec.split("_")[2], vcodec=self.idCodec.split("_")[1], rate=self.idCodec.split("_")[3], vbitrate=self.idCodec.split("_")[4]+'000k') # 24     
		#################################################################################

            elif self.idCodec=='jpeg': # convertir animation en images
                self.ffmpegProcess.commandeFfmpegConvAnimImg()
            elif self.idCodec=='extractionaudio':
                self.ffmpegProcess.commandeFfmpegSeparation()
            elif self.idCodec=='encodage_wav': # encodage de fichiers audio en wav
                self.ffmpegProcess.commandeFfmpegEncodageWav()
            elif self.idCodec=='conv_en_16_9_ou_4_3': # Convertir vidéo en 16/9 ou 4/3
                self.ffmpegProcess.commandeFfmpegConv_16_9_ou_4_3(
                            ext = os.path.splitext(self.cheminVideoEntre)[1],
                            size = "%sx%s" % (self.tailleVideo[0], self.tailleVideo[1]),
                            aspect = self.valeurNum,
                            audio = has_audio)

            # Remonté d'un niveau pour simplifier le code et éviter les répetitions
            if commande == None:
                commande = self.ffmpegProcess.command
            else :
                self.ffmpegProcess.command = commande

            debug(commande)
            self.zoneTexte.append(commande+'\n\n')
            self.ffmpegProcess.start()
            debug(u"Commande lancée")
            self.estLancee = True



    def finEncodage(self, statutDeSortie):
        """choses à faire à la fin de l'encodage de la vidéo"""

        # fermer la fenêtre à la fin de l'encodage
        if not self.laisserOuvert:
            self.close()

        debug("fini!")
        self.labelAttente.hide()
        self.pbar.setValue(100)
        # l'encodage est fini. Il ne peut plus être annulé. La
        # seule action possible devient ainsi la fermeture
        self.bout_annuler.setText(_(u"Fermer"))
        if statutDeSortie != 0 :
            self.bout_annuler.setText(_(u"Crash"))
        self.bout_preZoneTexte.show()
        self.emit(SIGNAL("finEncodage"))


    def afficherLog(self):
        """afficher les information de la vidéo de départ et de l'encodage"""
        self.zoneTexte.setText(self.ffmpegProcess.log)
        self.zoneTexte.show()
        self.resize(500, 300)


