# -*- coding: utf-8 -*-

from PyQt4.QtGui import QTextEdit, QLabel, QDialog, QPushButton, QProgressBar
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt4.QtCore import PYQT_VERSION_STR, QProcess, SIGNAL

from gui_modules_animation.infoVideo import infovideo

from moteur_modules_animation.mencoder import Mencoder
from moteur_modules_common.EkdTools import debug

class WidgetMEncoder(QDialog):
    def __init__(self, idCodec, cheminVideoEntre, cheminSorti, valeurNum=0,
                    laisserOuvert=1, systeme=None, cheminMEncoder=None,
                    tempsApercu=None, optionSpeciale=None):
        #############################################################################
        """widget mencoder"""
        QDialog.__init__(self)

        #=== Paramètres généraux ===#

        self.systeme=systeme

        # système d'exploitation
        if self.systeme=='linux' or self.systeme=='darwin' or self.systeme==None:
                self.cheminMEncoder="mencoder"

        elif self.systeme=='windows':
                self.cheminMEncoder=cheminMEncoder

        # chemins vidéos
        self.cheminVideoEntre = cheminVideoEntre
        self.cheminSorti = cheminSorti

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

        self.mencoderProcess = Mencoder(cheminVideoEntre, cheminSorti, idCodec, location=self.cheminMEncoder)

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

        #=== connexion des widgets à des fonctions ===#

        # TEST # sert à calculer la durée d'exécution du script -> comparaison avec avec et sans traitement
        # des lignes de sortie de QProcess
        # 'readyReadStandardOutput()': signal émis lors de la sortie standart de lecture
        self.connect(self.mencoderProcess, SIGNAL('progress(int)'), self.pbar.setValue)
        self.connect(self.mencoderProcess, SIGNAL('log(QString)'), self.zoneTexte.append)
        self.connect(self.mencoderProcess, SIGNAL('finished(int)'), self.finEncodage)
        self.connect(self.bout_annuler, SIGNAL('clicked()'), self.close)
        self.connect(self.bout_preZoneTexte, SIGNAL('clicked()'), self.afficherLog)

        # Uniquement Mencoder
        self.demarrerEncodeur('Mencoder')


    def demarrerEncodeur(self, encodeur):
        """démarrage de mencoder avec les arguments choisis"""

        if self.estLancee == False: # pas question de démarrer 2 fois l'encodage

                debug('\n')

                # ... pareil pour la concaténation de vidéos ensemble
                if self.idCodec=='fusion_video':
                        pass

                # ... pareil pour la concaténation de vidéos + audio(s)
                elif self.idCodec in ['fusion_audio_et_video_1', 'fusion_audio_et_video_2']:
                        pass

                # Autrement dans tous les autres cas ...
                else:

                        infos  = "\n########################\n"
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
                        self.id_img_par_sec = 'ID_VIDEO_FPS='+str(info.imgParSec)+'\n'
                        debug(self.id_img_par_sec)
                        ##### Donnée très importante pour la suite du calcul (uniquement pour ffmpeg.py) ######
                        #self.dureeTotaleVideo = float(info.dureeTotaleVideo)
                        #######################################################################################
                        id_duree_totale_video = 'ID_LENGTH='+str(info.dureeTotaleVideo)+'\n'
                        debug(id_duree_totale_video)
                        id_audio_codec = 'ID_AUDIO_CODEC='+info.audioCodec+'\n'
                        debug(id_audio_codec)
                        id_audio_rate = 'ID_AUDIO_RATE='+str(info.audioRate)+'\n'
                        debug(id_audio_rate)
                        id_audio_bitrate = 'ID_AUDIO_BITRATE='+str(info.audioBitrate)+'\n'
                        debug(id_audio_bitrate)

                        self.log.append(infos+id_filename+id_demuxer+id_video_format+id_video_codec+id_video_bitrate+id_video_largeur+id_video_hauteur+self.id_img_par_sec+id_duree_totale_video+id_audio_codec+id_audio_rate+id_audio_bitrate)
                        ##############################################################################################

                debug('\n')

                infos  = "\n############################\n"
                infos += "# Informations %s :\n" %encodeur
                infos += "############################\n"

                debug(infos)
                self.log.append(infos)

                if self.idCodec in ['dailymotion_sd_4/3', 'dailymotion_sd_16/9', 'dailymotion_HD720p']:
                    tspl = self.id_img_par_sec.split()
                    nbrISec =[n.split('=')[1] for n in tspl]
                    nbrISec = nbrISec[0]
                    # A une image par seconde, la vidéo chargée n'est pas bien traitrée
                    # (ou voire pas traitée du tout) Message d'information pour l'utilisateur.
                    if nbrISec == '1.0':
                        daily = QMessageBox.information(self, 'Message',
                        _(u"<p>Le nombre d'image(s) par seconde, dans la vidéo avec laquelle vous avez décidé de travailler, n'est que de 1, vous devez savoir que votre vidéo ne pourra pas être transcodée dans un des trois profils pour Dailymotion.</p><p>A partir de deux images par seconde, cela devient possible (en conséquence, éditez votre vidéo et changez le nombre d'images par seconde). <b>Le traitement demandé ne peut pas avoir lieu.</b></p>"), QMessageBox.Yes)
                        if daily == QMessageBox.Yes:return

                elif self.idCodec=='codech264mpeg4':
                    if not info.audioCodec:
                        self.idCodec = "%s_nosound" % self.idCodec
                #elif self.idCodec[0]=='bruit':
		# Rien à faire, c'est tout se passe ici animation_filtres_video.py
                elif self.idCodec=='changement_resolution' and not self.tempsApercu:
                    reponse = QMessageBox.information(self, 'Message',
                        _(u"<p>Vous avez décidé de changer la résolution de cette vidéo, sachez avant tout que la vidéo en question sera (en même temps qu'elle est redimensionnée) encodée en <b><font color='red'>Motion JPEG (extension .avi)</font></b>.</p><p>Vous pouvez (si vous le désirez) <b>vous approcher d'une résolution en 16/9ème</b>, pour ce faire vous devez faire un petit calcul ...</p><p>* pour obtenir la valeur de la hauteur comparativement à la valeur de la largeur, vous devez <b>diviser la valeur de la largeur par 1.777</b>, par exemple si votre vidéo de départ est en 640x480, le calcul à faire sera le suivant:</p><p>640 / 1.777, cela vous donnera (à la virgule près) 360.15756893640969, vous devrez enlever les chiffres après la virgule. Pour conclure, votre vidéo fera à l'arrivée 640x360, vous pourrez donc régler <b>Nouvelle largeur</b> à 640 et <b>Nouvelle hauteur</b> à 360.</p><p><b>Si vous décidez de faire les réglages pour obtenir une vidéo en 16/9ème, répondez non</b> à la question qui vous sera posée (pour ainsi pouvoir refaire les réglages), <b>si vous décidez de changer la résolution tout de suite (et avec les valeurs que vous venez de définir), répondez oui</b>.</p><p><b>Voulez-vous changer la résolution tout de suite ?.</b></p>"), QMessageBox.Yes, QMessageBox.No)
                    if reponse == QMessageBox.No:
                        return


                debug("self.idCodec de mencoder %s" % self.idCodec)
                self.mencoderProcess.setCommand(parametres = self.valeurNum, apercu = self.tempsApercu)
                self.mencoderProcess.start()
                debug(u"Commande lancée")

                self.estLancee = True

    def close(self):
        self.mencoderProcess.cancel()
        QDialog.close(self)

    def finEncodage(self, statutDeSortie):
        """choses à faire à la fin de l'encodage de la vidéo"""

        # fermer la fenêtre à la fin de l'encodage
        if not self.laisserOuvert:
                self.close()

        debug("fini!")
        self.labelAttente.hide()
        self.pbar.setValue(100)

        if statutDeSortie == QProcess.CrashExit:
                self.bout_preZoneTexte.setText(_(u'Problème! Voir les informations'))
                self.bout_annuler.setText(_(u"Crash"))
                self.log.append(_(u"Une erreur est survenue lors de l'encodage"))
        else:
            # l'encodage est fini. Il ne peut plus être annulé. La
            # seule action possible devient ainsi la fermeture
                self.bout_annuler.setText(_(u"Fermer"))
        self.bout_preZoneTexte.show()


    def afficherLog(self):
        """afficher les information de la vidéo de départ et de l'encodage"""
        self.zoneTexte.setText(self.mencoderProcess.log)
        self.zoneTexte.show()
        self.resize(500, 300)


