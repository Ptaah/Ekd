# -*- coding: utf-8 -*-

from PyQt4.QtGui import QDialog, QLabel, QTextEdit, QPushButton
from PyQt4.QtGui import QProgressBar, QVBoxLayout, QHBoxLayout
from PyQt4.QtCore import SIGNAL, PYQT_VERSION_STR
from gui_modules_animation.infoVideo import infovideo
from moteur_modules_common.EkdTools import debug
from moteur_modules_animation.ffmpeg2theora import FFmpeg2theora


class WidgetFFmpeg2theora(QDialog):

    def __init__(self, idCodec, cheminVideoEntre, cheminSorti, valeurNum=0, laisserOuvert=1, systeme=None, cheminFfmpeg2theora=None, tempsApercu=None, optionSpeciale=None, cheminMPlayer=None):

        """widget mplayer"""
        QDialog.__init__(self)

        #=== Paramètres généraux ===#

        self.systeme=systeme

        # système d'exploitation
        if self.systeme=='linux' or self.systeme=='darwin' or self.systeme==None:
            self.cheminFfmpeg2theora=u"ffmpeg2theora"

        elif self.systeme=='windows':
            self.cheminFfmpeg2theora=unicode(cheminFfmpeg2theora)

        # chemins vidéos
        self.cheminVideoEntre = unicode(cheminVideoEntre)
        self.cheminSorti = unicode(cheminSorti)

        # identifiant du codec
        self.idCodec = idCodec

        # valeur de la boite de spin pour l'encodage
        self.valeurNum = valeurNum

        # laisser ouvert la fenêtre après encodage
        self.laisserOuvert = laisserOuvert

        # Conversion minimale du filtre pour avoir un aperçu.
        # Indique le temps où l'aperçu doit être créé
        self.tempsApercu = tempsApercu

        # drapeau pour ne pas lancer 2 fois l'encodage
        self.estLancee = False

        # Est-ce que le 1er % de progression a été récupéré (utile pour montage vidéo -> découper)?
        self.__recupPourcentDebut = 0

        self.log = [] # stocke les infos de mplayer et mencoder

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
        self.zoneTexte.hide()

        self.bout_annuler = QPushButton(_(u"Annuler"))

        self.bout_preZoneTexte = QPushButton(_("Voir les informations de l'encodage"))
        self.bout_preZoneTexte.hide()

        self.pbar = QProgressBar()
        self.pbar.setMaximum(100)

        #self.ffmpeg2theoraProcess = QProcess(self)
        self.ffmpeg2theoraProcess = FFmpeg2theora(cheminVideoEntre, cheminSorti, codec = idCodec)

        #=== mise-en-page/plan ===#

        vbox = QVBoxLayout()
        vbox.addWidget(self.labelAttente)
        vbox.addWidget(self.bout_preZoneTexte)
        vbox.addWidget(self.zoneTexte)
        hbox = QHBoxLayout()
        hbox.addWidget(self.pbar)
        hbox.addWidget(self.bout_annuler)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        #self.adjustSize()

        #=== connexion des widgets à des fonctions ===#

        # TEST # sert à calculer la durée d'exécution du script -> comparaison avec avec et sans traitement
        # des lignes de sortie de QProcess
        # 'readyReadStandardOutput()': signal émis lors de la sortie standart de lecture
        self.connect(self.ffmpeg2theoraProcess, SIGNAL('progress(int)'),
                                            self.pbar.setValue)
        self.connect(self.ffmpeg2theoraProcess, SIGNAL('log(QString)'),
                                            self.zoneTexte.append)
        self.connect(self.ffmpeg2theoraProcess, SIGNAL('finished(int)'),
                                            self.finEncodage)

        self.connect(self.bout_annuler, SIGNAL('clicked()'), self.close)
        self.connect(self.bout_preZoneTexte, SIGNAL('clicked()'), self.afficherLog)

    def close(self):
        """ Annule le traitement en cours """
        self.ffmpeg2theoraProcess.cancel()
        self.ffmpeg2theoraProcess.wait()
        #super(WidgetFFmpeg, self).close() # Python 2.6
        QDialog.close(self)

    def exec_(self):
        """ Surcharge de la fonction exec permettant l'execution hors de l'init"""
        self.demarrerEncodeur('Ffmpeg2theora')
        #super(WidgetFFmpeg, self).exec_() # Python 2.6
        QDialog.exec_(self)

    def demarrerEncodeur(self, encodeur):
        """démarrage de mencoder avec les arguments choisis"""

        if self.estLancee == False: # pas question de démarrer 2 fois l'encodage

            infos = "\n########################\n"
            infos += "# Informations MPlayer :\n"
            infos += "########################\n"

            debug(infos)

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

            self.log.append(infos+id_filename+id_demuxer+id_video_format+id_video_codec+id_video_bitrate+id_video_largeur+id_video_hauteur+id_img_par_sec+id_duree_totale_video+id_audio_codec+id_audio_rate+id_audio_bitrate)
            ##############################################################################################

            infos = "\n############################\n"
            infos += "# Informations %s :\n" % encodeur
            infos += "############################\n"

            debug(infos)
            self.log.append(infos)

            self.ffmpeg2theoraProcess.setVideoLen(self.dureeTotaleVideo)

            if encodeur == 'Ffmpeg2theora':
                # mode de canal: on fusionne le canal de sortie normal
                # (stdout) et celui des erreurs (stderr)

                self.ffmpeg2theoraProcess.setCommand(self.valeurNum)
                self.ffmpeg2theoraProcess.start()

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
        self.bout_preZoneTexte.show()


    def afficherLog(self):
        """afficher les information de la vidéo de départ et de l'encodage"""
        self.zoneTexte.setText(self.ffmpeg2theoraProcess.log)
        self.zoneTexte.show()
        self.resize(500, 300)

