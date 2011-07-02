# -*- coding: utf-8 -*-

import os, re
from PyQt4.QtCore import SIGNAL, QThread
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdProcess import EkdProcess
from moteur_modules_common.EkdTools import debug
###################################################################
# --> Création de l'objet ffmpeg pour séparer les traitements gérés
# par FFmpeg de ceux gérés par Mencoder et FFmpeg2theora
###################################################################

class FFmpeg(QThread):
    """
    Classe permettant de ne gérer que la partie moteur de ffmpeg (sans avoir
    besoin d'interface graphique)
    """
    #'''
    def __init__(self, inputfile, outputfile, codec=None, imgsize=None,
                 videosize=None, location=None):
    #'''
        """
            codec : Identifiant du codec à utiliser
            inputfile : fichier audio/video d'entree
            outputfile : fichier de sortie
            imgsize : taille des images de sortie (conversion d'image en video)
            videosize : taille de la video en sortie
            location : chemin d'accèss à ffmpeg

            command  : ligne de commande du processus
            progress : progression du processus
            process  : processus ffmpeg de conversion
            log      : contenu des log de ffmpeg
        """
        super(FFmpeg, self).__init__()
        self.codec = codec
        self.inputfile = inputfile
        self.outputfile = outputfile

        if os.name in ['posix', 'mac'] and (location == None):
            self.location=u"ffmpeg"
        else :
            ## We are not on linux we force the ffmpeg location
            self.location=u"ffmpeg"

        self.dfltOptions = u""

        # Initialisation de la commande
        self.command = None

        # Initialisation de la progression
        self.progress = 0

        # Log d'output de la commande
        self.log = ""

        ### On passe par subprocess.popen


    def setOutputFile(self, outputfile):
        self.outputfile = outputfile

    def setInputFile(self, inputfile):
        self.inputfile = inputfile

    def setVideoLen(self, videoLen):
        """ Définie la durée de la vidéo """
        self.videoLen = videoLen

    def setProgress(self, val):
        """
            Définie le niveau de progression et envoie un signal progress(int)
        """
        self.progress = val
        self.emit(SIGNAL("progress(int)"), self.progress)

    def addLog(self, line):
        """
            Ajout une ligne de log dans self.log et envoie un signal log(string)
        """
        try:
            #debug(u"FFmpeg log : %s" % line)
            self.log = "%s\n%s" % (self.log, unicode(line, EkdConfig.coding))
            self.emit(SIGNAL("log(QString)"), line)
        except:
            #debug(u"FFmpeg log : %s" % line)
            self.log = "%s\n%s" % (self.log, line)
            self.emit(SIGNAL("log(QString)"), line)

    def run(self):
        """ Démarre le processus ffmpeg """
        if self.command == None :
            debug(u"FFmpeg: Commande ffmpeg non définie")
            raise Exception
        self.addLog(self.command.encode(EkdConfig.coding))
        try :
            ## Attention, ffmpeg envoie sa sortie de progression sur stderr !!!
            self.process = EkdProcess( self.command.encode(EkdConfig.coding),
                                        stdinput = None, output = None)
            self.emit(SIGNAL("void started()"))
        except Exception, e:
            debug(u"Erreur dans le lancement de %s\n(%s)" % (self.command, e))
            raise
        self.retCode = None
        while self.retCode == None :
            self.progression()
            self.retCode = self.process.poll()
            self.usleep(10)
        self.end(self.retCode)

    def cancel(self):
        """ Cancel the process if it is currently running """
        try:
            self.process.terminate()
        except:
            pass

    def end(self, returnCode):
        """ Traite la fin du processus ffmpeg """
        #if returnCode == QProcess.CrashExit:
        if returnCode != 0:
            self.addLog(u"Une erreur est survenue"
                        "lors de l'encodage".encode(EkdConfig.coding))
        self.emit(SIGNAL("finished(int)"), returnCode)

    def progression(self):
        """
        Recupération de la progression du process en cours
        """
        if self.videoLen==0 : self.videoLen = 1
        line = self.process.stderr.readline()
        if re.match('^frame=.*', line):
            val = re.findall("time=([^ ]+)",line)[0]
            self.setProgress(int( ( float(val) * 100 / self.videoLen) ))
        else:
            self.addLog(line)

    def setCommandVideo(self, size, vcodec, bitrate, aspect, acodec):
        """
            Définie la ligne de commande de façon générique pour le traitement
            video
        """
        self.command = u"%s %s -i \"%s\" -vcodec %s -b %s -deinterlace -s %s -aspect %s -acodec %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, vcodec, bitrate, size, aspect, acodec, self.outputfile)

    def setCommandAudio(self, vbitrate="44100", abitrate="192k", achannel="2", format="wav"):
        """ Définie la ligne de commande de façon générique pour le traitement audio """
        self.command = u"%s %s -i \"%s\" -vn -ar %s -ab %s -ac %s -f %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, vbitrate, abitrate, achannel, format, self.outputfile)

    def commandeFfmpegConvHD(self, size, vcodec="mpeg4", vbitrate="6000k", aspect="16:9", acodec="pcm_s16be"):
        """ Définie la ligne de commande pour la conversion HD """
        self.command = u"%s %s -i \"%s\" -vcodec %s -b %s -deinterlace -s %s -aspect %s -acodec %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, vcodec, vbitrate, size, aspect, acodec, self.outputfile)

    ### Ajouté le 19/08/10 (Gestion du codec Avid DNxHD) ################################
    def commandeFfmpegConvHD_DNxHD(self, size, vcodec, rate, vbitrate, acodec="copy"):
        """ Définie la ligne de commande pour la conversion HD pour les différents 
	traitement avec le codec Avid DNxHD """
	# Commande (exemple): ffmpeg -i video_in.avi -s 1280x720 -r 23.976 -b 90000k -vcodec dnxhd -deinterlace -acodec copy -y video_out.mov
        self.command = u"%s %s -i \"%s\" -s %s -r %s -b %s -vcodec %s -deinterlace -acodec %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, size, rate, vbitrate, vcodec, acodec, self.outputfile)
    #####################################################################################

    def commandeFfmpegSeparation(self, vbitrate="44100", achannel="2", format="wav"):
        """ Définie la commande de séparation de l'audio et de la vidéo """
        self.setCommandAudio(vbitrate=vbitrate, achannel=achannel, format=format)

    def commandeFfmpegEncodageWav(self, vbitrate="44100", abitrate="192k", achannel="2", format="wav"):
        """ Définie la commande d'encodage Wav """
        self.setCommandAudio(vbitrate, abitrate, achannel, format)

    def commandeFfmpegNbrImgSec(self, rate, sync="1", vbitrate="800k"):
        """ Définie la commande de modification du nombre d'image par seconde """
        self.command = u"%s %s -i \"%s\" -r %s -vsync %s -b %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, rate, sync, vbitrate, self.outputfile)

    def commandeFfmpegConvAnimImg(self):
        """ Définie la commande pour la conversion d'une video en image """
        self.setOutputFile(unicode(self.outputfile) + u"_%09d.png")
        self.command = u"%s %s -i \"%s\" -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, self.outputfile)

    def commandeFfmpegEncodageDv(self, format="dv", target="pal-dv"):
        """ Définie la commande pour la conversion d'une vidéo au format DV"""
        self.command = u"%s %s -i \"%s\" -f %s -target %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, format, target, self.outputfile)

    ##### Enlevé le 09/04/11 ######################################
    '''
    def commandeFfmpegEncodageMov(self, vcodec="mov", acodec="pcm_s16be"):
        """ Définie la commande pour l'encodage en format mov """
        self.command = u"%s %s -i \"%s\" -f %s -sameq -acodec %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, vcodec, acodec, self.outputfile)
    '''
    ###############################################################

    ##### Ajouté/rectifié le 09/04/11 #############################
    def commandeFfmpegEncodageMov(self, comp, size, vcodec="mov", acodec="pcm_s16be"):
        """ Définie la commande pour l'encodage en format mov """
        self.command = u"%s %s -i \"%s\" -qscale %s %s -f %s -acodec %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, comp, size, vcodec, acodec, self.outputfile)
    ###############################################################

    ##### Enlevé le 10/04/11 ######################################
    '''
    def commandeFfmpegEncodageHfyu(self, audio=True, vcodec="huffyuv", acodec="pcm_s16be", format="yuv422p"):
        """ Définie la commande d'encodage Hfyu """
        if audio:
            self.command = u"%s %s -i \"%s\" -vcodec %s -pix_fmt %s -sameq -y \"%s\"" % \
                    (self.location, self.dfltOptions, self.inputfile, vcodec, format, self.outputfile)
        else:
            self.command = u"%s %s -i \"%s\" -vcodec %s -pix_fmt %s -sameq -acodec %s -y \"%s\"" % \
                    (self.location, self.dfltOptions, self.inputfile, vcodec, format, acodec, self.outputfile)
    '''
    ###############################################################

    ##### Ajouté/rectifié le 10/04/11 #############################
    def commandeFfmpegEncodageHfyu(self, size, audio=True, vcodec="huffyuv", acodec="pcm_s16be", format="yuv422p"):
        """ Définie la commande d'encodage Hfyu """
        if audio:
            self.command = u"%s %s -i \"%s\" %s -vcodec %s -pix_fmt %s -sameq -y \"%s\"" % \
                    (self.location, self.dfltOptions, self.inputfile, size, vcodec, format, self.outputfile)
        else:
            self.command = u"%s %s -i \"%s\" %s -vcodec %s -pix_fmt %s -sameq -acodec %s -y \"%s\"" % \
                    (self.location, self.dfltOptions, self.inputfile, size, vcodec, format, acodec, self.outputfile)
    ###############################################################

    def commandeFfmpegEncodageVob(self, vquantizer, audiofreq="44100"):
        """ Définie la commande d'encodage en vob """
        self.command = u"%s %s -i \"%s\" -ar %s -qscale %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, audiofreq, vquantizer, self.outputfile)

    ##### Enlevé le 30/03/11 ######################################
    '''
    def commandeFfmpegEncodageAMV(self, size="160x120", achannel="1", audiofreq="22050", qmin="3", qmax="3"):
        """ Définie la commande d'encodage en AMV """
        self.command = u"%s %s -i \"%s\" -s %s -ac %s -ar %s -qmin %s -qmax %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, size, achannel, audiofreq, qmin, qmax, self.outputfile)
        # La commande: ffmpeg -i entree.avi -s 160x120 -ac 1 -ar 22050 -qmin 3 -qmax 3 sortie.avi
    '''
    ###############################################################
    
    ##### Ajouté/rectifié le 30/03/11 #############################
    def commandeFfmpegEncodageAMV(self, size, achannel="1", audiofreq="22050", qmin="3", qmax="3"):
        """ Définie la commande d'encodage en AMV """
        self.command = u"%s %s -i \"%s\" -s %s -ac %s -ar %s -qmin %s -qmax %s -y \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, size, achannel, audiofreq, qmin, qmax, self.outputfile)
        # La commande: ffmpeg -i entree.avi -s 160x120 -ac 1 -ar 22050 -qmin 3 -qmax 3 sortie.avi
    
    ##### Enlevé le 30/03/11 ######################################
    '''
    def commandeFfmpegEncodage3gp(self, vcodec="3gp", size="qcif", acodec="aac", audio=True):
        """ Définie la commande d'encodage en 3gp """
        if audio :
            self.command = u"%s %s -i \"%s\" -f %s -sameq -s %s -acodec %s -y \"%s\"" % \
                    (self.location, self.dfltOptions, self.inputfile, vcodec, size, acodec, self.outputfile)
        else:
            self.command = u"%s %s -i \"%s\" -f %s -sameq -s %s -y \"%s\"" % \
                    (self.location, self.dfltOptions, self.inputfile, vcodec, size, self.outputfile)
    '''
    ###############################################################

    ##### Ajouté/rectifié le 30/03/11 #############################
    # Pour l'instant le son n'est pas géré
    def commandeFfmpegEncodage3gp(self, size, vcodec="3gp", acodec="aac", audio=True):
        """ Définie la commande d'encodage en 3gp """
	self.command = u"%s %s -i \"%s\" -s %s -f %s -sameq -y \"%s\"" % \
                    (self.location, self.dfltOptions, self.inputfile, size, vcodec, self.outputfile)
    ###############################################################
    
    def commandeFfmpegConvertImg(self, rate, size, vcodec, format="image2", vbitrate="1800", qscale="1"):
        """ Définie la commande de convertion d'images en video """
        if vcodec == 'dv' :
            vcodec = '-target pal-dv'
            format = "-f dv"
        elif vcodec == 'mov':
            format = '-f mov'
            vcodec = ''
        elif vcodec == 'vob':
            vcodec = ''
            format = ""
            rate = ""
        elif vcodec == 'mp4':
            vcodec = ""
            format = "-f mp4"
        elif vcodec == 'ljpeg':
            vcodec = "-vcodec %s" % vcodec
            self.dfltOptions = ''
            ## On ajoute le format yuv420p qui permet une conversion directe en
            ## ljpeg contrairement au format par défaut
            format = "-pix_fmt yuvj420p"
        else :
            vcodec = "-vcodec %s" % vcodec
            format = ""
            self.dfltOptions = ''
        if rate != "" :
            rate = "-r %s" % rate

        self.command = u"%s %s %s -s %s -f image2 -i \"%s\" -b %s %s %s -qscale %s -y \"%s\"" % \
                (self.location, self.dfltOptions, rate, size, self.inputfile, vbitrate, format, vcodec, qscale, self.outputfile)

    def commandeFfmpegConv_16_9_ou_4_3(self, ext, size, aspect, audio=True):
        """ Définie la commande de convertion de résolution 16/9 4/3"""

        a_codec_d_s = '-deinterlace'
	aspect = str(aspect) #### Ajouté/changé le 25/03/11
        if ext == '.avi':
            v_codec = '-vcodec mjpeg'
            self.addLog(_(u"Vous avez décidé de traiter une vidéo AVI, sachez qu'elle sera encodée (votre vidéo) en Motion JPEG (extension .avi).\n"))
        elif ext == '.mov':
            v_codec = '-vcodec mpeg4'
            a_codec_d_s = '-acodec pcm_s16be %s' % a_codec_d_s
        elif ext == '.vob':
            v_codec = ''
        elif ext == '.flv':
            v_codec = u'-f flv'
            if audio:
                a_codec_d_s = u'-acodec pcm_s16be %s' %a_codec_d_s
        else: #'.mpg', '.mpeg'
            v_codec = '-vcodec mpeg2video'
            self.addLog(_(u"Vous avez décidé de traiter une vidéo MPEG, sachez qu'elle sera encodée (votre vidéo) MPEG2 (extension .mpg ou .mpeg).\n"))

        self.command = u"%s -i \"%s\" %s %s -s %s -aspect %s -sameq -y \"%s\"" \
                % (self.location, self.inputfile, v_codec, a_codec_d_s, size,
                   aspect, self.outputfile)

    def commandeConcatAudio(self):
            self.command = u"%s -i \"%s\" -ab 192k -ar 44100 -ac 2 -f wav -y \"%s\"" % \
                        (self.location, self.inputfile, self.output)
