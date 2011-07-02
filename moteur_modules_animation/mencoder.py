# -*- coding: utf-8 -*-

import os, re
from PyQt4.QtCore import SIGNAL, QString, QThread
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdProcess import EkdProcess
from moteur_modules_common.EkdTools import debug

####################################################################

# --> Ceci a été fait pour séparer les traitements gérés par Mencoder de ceux gérés par
# FFmpeg et FFmpeg2theora
######################################################################################
### Ici il s'agit de l'extraction d'image pour la prévisualisation du résultat
### de l'effet pour les filtres vidéo. C'est Mencoder qui s'occupe des filtres vidéo
### ... MAIS ... pour cette partie spécifique d'extraction des images c'est FFmpeg
### qui est utilisé !.

# La syntaxe Mplayer a été remplacée par la syntaxe FFmpeg car la syntaxe
# Mplayer generait des bugs dans l'extraction des images --> avec certaines
# vidéos (et de façon alléatoire). Le rendu est un peu plus lent qu'avec
# Mplayer mais plus de bugs.
def extraireImage(cheminVideoSource, cheminRepDestination, valeurNum, multiple=True):
    "Extraction d'une image d'une vidéo"

    patern = ""
    if multiple :
        patern = u"_%8d.jpg"

    commande = 'ffmpeg -i '+ "\"" + cheminVideoSource + "\"" + \
            ' -vframes 1 ' + ' -ss ' + str(valeurNum) + ' -an -f image2 ' + "\"" +\
            cheminRepDestination + patern + "\""
    os.system(commande.encode("UTF8"))
######################################################################################

if os.name in ['posix', 'mac']:
    unix = True
    coding = "utf-8"
else :
    unix = False
    coding = "cp1252"

class Mencoder(QThread):
    """
    Classe permettant de ne gérer que la partie moteur de mencoder (sans avoir
    besoin d'interface graphique)
    """
    def __init__(self, inputfile, outputfile, codec=None, imgsize=None,
                 videosize=None, location=None):
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
        super(Mencoder, self).__init__()
        self.codec = codec

        self.setInputFile(inputfile)
        self.outputfile = outputfile

        if unix and (location == None):
            self.location=u"mencoder"
        else :
            ## We are not on linux we force the ffmpeg location
            self.location=u"mencoder"

        self.dfltOptions = ""

        # Initialisation de la commande
        self.command = None

        # Initialisation de la progression
        self.progress = 0

        # Log d'output de la commande
        self.log = ""


    def setOutputFile(self, outputfile):
        self.outputfile = outputfile

    def setInputFile(self, inputfile):
        if type(inputfile) == tuple:
            self.inputfile = inputfile[0]
            self.audiofile = inputfile[1]
        else:
            self.inputfile = inputfile
            self.audiofile = None

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
            debug(u"Mencoder log : %s" % unicode(line, EkdConfig.coding))
            self.log = "%s\n%s" % (self.log, unicode(line, EkdConfig.coding))
            self.emit(SIGNAL("log(QString)"), line)
        except:
            debug(u"Mencoder log : %s" % unicode(line, EkdConfig.coding))
            self.log = "%s\n%s" % (self.log, line)
            self.emit(SIGNAL("log(QString)"), line)

    def run(self):
        """ Démarre le processus mencoder """
        if self.command == None :
            debug("FFmpeg: Commande mencoder non définie")
            raise Exception
        self.addLog(self.command.encode(EkdConfig.coding))
        try :
            self.process = EkdProcess( self.command.encode(EkdConfig.coding),
                                        stdinput = None)
            self.emit(SIGNAL("void started()"))
        except Exception, e:
            debug("Erreur dans le lancement de %s\n(%s)" % (self.command, e))
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
        """ Traite la fin du processus mencoder """
        if returnCode != 0:
            self.addLog(u"Une erreur est survenue "
                        "lors de l'encodage".encode(EkdConfig.coding))
            errors = ""
            self.process.stderr.flush()
            for line in self.process.stderr.readlines():
                errors += line
            self.addLog(QString(errors))
        self.emit(SIGNAL("finished(int)"), returnCode)

    def progression(self):
        """
        Recupération de la progression du process en cours
        """
        line = self.process.stdout.readline()
        if re.match('^Pos.*', line):
            val = re.findall("\d+%",line)[0]
            self.setProgress(int(val[:-1]))
        else:
            self.addLog(line)

    def setCommand(self, parametres, apercu = False):
        """
            Définie la ligne de commande de façon générique pour le traitement
            video
        """
        if parametres :
            debug (u"Mencoder : type de parametres : %s len : %s " % (type(parametres), len(parametres)))
            for param in parametres :
                debug (u"Mencoder : parametres : %s" % param)

        if type(parametres) != list and type(parametres) != tuple and type(parametres) != dict:
            codecs_command = {
                'copie' : '-ovc copy -oac pcm',
                'youtube_16/9_HQ' : '-oac mp3lame -lameopts cbr=256 -ffourcc xvid -ovc lavc -lavcopts vbitrate=3000 -vf scale=512:288',
                'youtube_16/9_MQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=1000 -vf scale=512:288',
                'youtube_16/9_LQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=564 -vf scale=512:288',
                'youtube_4/3_HQ' : '-oac mp3lame -lameopts cbr=256 -ffourcc xvid -ovc lavc -lavcopts vbitrate=3000 -vf scale=482:361',
                'youtube_4/3_MQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=1000 -vf scale=482:361',
                'youtube_4/3_LQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=564 -vf scale=482:361',
                'google_video_16/9_HQ' : '-oac mp3lame -lameopts cbr=256 -ffourcc xvid -ovc lavc -lavcopts vbitrate=3000 -vf scale=872:520',
                'google_video_16/9_MQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=1000 -vf scale=872:520',
                'google_video_16/9_LQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=564 -vf scale=872:520',
                'google_video_4/3_HQ' : '-oac mp3lame -lameopts cbr=256 -ffourcc xvid -ovc lavc -lavcopts vbitrate=3000 -vf scale=694:520',
                'google_video_4/3_MQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=1000 -vf scale=694:520',
                'google_video_4/3_LQ' : '-oac mp3lame -lameopts cbr=128 -ffourcc xvid -ovc lavc -lavcopts vbitrate=564 -vf scale=694:520',
                'dailymotion_sd_4/3' : '-oac faac -faacopts mpeg=4:raw:br=192 -of lavf -lavfopts format=mp4 -srate 44100 -ovc x264 ' \
                                       '-x264encopts bitrate=2400 -vf scale=640:480 -lavcopts aspect=4/3 -ofps 25',
                'dailymotion_sd_16/9' : '-oac faac -faacopts mpeg=4:raw:br=192 -of lavf -lavfopts format=mp4 -srate 44100 -ovc x264 ' \
                                        '-x264encopts bitrate=2400 -vf scale=848:480 -lavcopts aspect=16/9 -ofps 25',
                'dailymotion_HD720p' : '-oac faac -faacopts mpeg=4:raw:br=192 -of lavf -lavfopts format=mp4 -srate 44100 -ovc x264 ' \
                                       '-x264encopts bitrate=4800 -vf scale=1280:720 -lavcopts aspect=16/9 -ofps 25',
                'niveaudegris':'-ovc lavc -lavcopts gray -oac pcm',
                'placesoustitres':'-ovc lavc -vf expand=0:-50:0:0 -oac pcm',
                'miroir':'-ovc lavc -vf mirror -oac pcm',
                'tournervideo':'-vf rotate=1 -oac pcm -ovc lavc',
                'desentrelacer':'-vf pp=0x20000 -oac pcm -ovc lavc',
                'extractionvideo': '-ovc lavc -nosound',
                'fusion_video': '-noidx -oac pcm -ovc copy',
                'fusion_audio_et_video_1': '-idx -audiofile \"%s\" -oac lavc -lavcopts acodec=ac3 -stereo 0 -ovc copy' % self.audiofile ,
                'fusion_audio_et_video_2': '-idx -audiofile \"%s\" -oac pcm -stereo 0 -ovc copy' % self.audiofile,
		'avirawsanscompression' : '-ovc raw -vf %sformat=i420 -oac pcm' % parametres,
                }
		#### Changé/rectifié le 26/03/11 ###########################################
		# ('codecdivx4', 'codecmotionjpeg', 'codecmpeg1', 'codecmpeg2', 'codecwmv2', 
		# 'macromediaflashvideo', 'codech264mpeg4_ext_h264', 'codech264mpeg4' et 
		# 'codech264mpeg4_nosound' ont été enlevés ici et mis juste en dessous car 
		# la plupart comportent maintenant 2 réglages).
		#### Changé/rectifié le 10/04/11 ###########################################
		# 'avirawsanscompression' comporte maintenant le réglage de la taille de la 
		# vidéo.
		#### Changé/rectifié le 10/04/11 ###########################################
		# 'codecxvid' a été enlevé ici et mis juste en dessous car il comporte 
		# maintenant 2 réglages.
        elif len(parametres) == 2 and type(parametres) != dict :
            # Cas de parametres standards
            codecs_command = {}
            codecs_command['luminositecontraste'] = '-ovc lavc -vf eq=%s:%s -oac pcm' % (parametres[0], parametres[1])
            codecs_command['decoupervideo'] = '-ss %s -endpos %s -oac pcm -ovc copy' % (parametres[0], parametres[1])
            codecs_command['couleursaturationhue'] ='-ovc lavc -vf hue=%s:%s -oac pcm' % (parametres[0], parametres[1])
            codecs_command['decoupervideo_nosound'] = '-ss %s -endpos %s -nosound -ovc copy' % (parametres[0], parametres[1])
            codecs_command['flouboitebloxblur'] = '-ovc lavc -vf boxblur=%s:%s -oac pcm' % (parametres[0], parametres[1])
            codecs_command['changement_resolution'] = '-vf scale=%s:%s -ovc lavc -lavcopts vcodec=mjpeg:vqmin=1:vpass=1 -oac pcm' % (parametres[0], parametres[1])
	    codecs_command['codecxvid'] = '-ovc lavc -ffourcc xvid -xvidencopts pass=1:bitrate=%s %s -oac pcm' % (parametres[0], parametres[1])
	elif len(parametres) == 3 and type(parametres) != dict :
            codecs_command = {}
	    #### Changé/rectifié le 26/03/11 -- intégration de réglages supplémentaires ###################
	    #### Le 02/03/11 --> Intégration de la condition pour == 3 et de parametres[2] pour les presets 
	    # de taille vidéo ####
	    codecs_command['codecmotionjpeg'] = '-ovc lavc -lavcopts vcodec=mjpeg:vbitrate=%s:vqmin=%s:vpass=1 %s -oac pcm' % (parametres[0], parametres[1], parametres[2])
	    codecs_command['codecmpeg1'] = '-ovc lavc -lavcopts vcodec=mpeg1video:vbitrate=%s:vqmin=%s:vpass=1 %s -oac pcm' % (parametres[0], parametres[1], parametres[2])
	    codecs_command['codecmpeg2'] = '-ovc lavc -lavcopts vcodec=mpeg2video:vbitrate=%s:vqmin=%s:vpass=1 %s -oac pcm' % (parametres[0], parametres[1], parametres[2])
	    codecs_command['codech264mpeg4'] = '-oac faac -faacopts mpeg=4:raw:br=24 -of lavf -lavfopts format=mp4 %s -ovc x264 -x264encopts bitrate=%s' % (parametres[2], parametres[0]) # Ajout du paramètre du bitrate vidéo + le 02/04/11 le paramètre de la taille de la vidéo (preset) #### (1 seul paramètre utilisé sur les présents 2 ds le tuple)
	    codecs_command['codech264mpeg4_nosound'] = '-of lavf -lavfopts format=mp4 %s -nosound -ovc x264 -x264encopts bitrate=1200' % parametres[2] # Pas de paramètre utilisé mais ici le paramètre pour codech264mpeg4 est un tuple de 2 valeurs
	    codecs_command['macromediaflashvideo'] = '-ovc lavc -ffourcc FLV1 -lavcopts vcodec=flv:vbitrate=%s:vqmin=%s %s -oac pcm' % (parametres[0], parametres[1], parametres[2])
	    codecs_command['codech264mpeg4_ext_h264'] = '-nosound -of lavf -lavfopts format=h264 %s -ovc x264 -x264encopts bitrate=%s' % (parametres[2], parametres[0]) # Ajout du paramètre du bitrate vidéo + le 02/04/11 le paramètre de la taille de la vidéo (preset) #### (1 seul paramètre utilisé sur les présents 2 ds le tuple)
	    codecs_command['codecdivx4'] = '-ovc lavc -lavcopts vcodec=mpeg4:vbitrate=%s:vqmin=%s:vpass=1 %s -oac pcm' % (parametres[0], parametres[1], parametres[2])
	    codecs_command['codecwmv2'] = '-ovc lavc -lavcopts vcodec=wmv2:vbitrate=%s:vqmin=%s:vpass=1 %s -oac pcm' % (parametres[0], parametres[1], parametres[2])
	    ###############################################################################################
        elif len(parametres) == 4 and type(parametres) != dict :
            codecs_command = {}
            # Cas Luma et Chroma et découpage, on a besoin de 4 parametres
            codecs_command['bruit'] = '-ovc lavc -vf noise=%s[%s]:%s[%s] -oac pcm' % (parametres[2], parametres[0], parametres[3], parametres[1])
            codecs_command['decoupagelibre'] ='-ovc lavc -vf crop=%s:%s:%s:%s -oac pcm' % (parametres[0], parametres[1],parametres[2],parametres[3])
            codecs_command['decoupageassiste'] ='-ovc lavc -vf crop=%s:%s:%s:%s -oac pcm' % (parametres[0], parametres[1],parametres[2],parametres[3])
	    ### Ajouté le 05/09/10 pour la gestion des tags vidéo #### ##########################################################
        else :
            codecs_command = {}
            info = ""
	    # Cas de Vidéo > Tags vidéo
            for key in parametres.keys():
                valeur = parametres[key.capitalize()] 
                if valeur == "":
                    ## On évite de planter la ligne de commande si un champ n'a pas été renseigné
                    valeur = " "
                if key == "Title" :
                    ## On traite le bug de Title dans la ligne de commande qui est en fait remplacée par name
                    key = "name"
                elif key == "Comments":
                    ## On traite le bug de Comments dans la ligne de commande qui est en fait remplacée par comment
                    key = "comment"
                info = '%s:%s="%s"' % (info, key.lower(), valeur)
            codecs_command['tag_video'] ='-ovc copy -oac copy -info %s' % info.strip(":")
	    ##########################################################
        if apercu :
            apercu_cmd = "-ss %s -frames 2" % (apercu)
        else:
            apercu_cmd = ""

        self.command = u"%s %s \"%s\" %s %s -o \"%s\"" % \
                (self.location, self.dfltOptions, self.inputfile, codecs_command[self.codec], apercu_cmd, self.outputfile)


