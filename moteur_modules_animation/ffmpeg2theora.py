# -*- coding: utf-8 -*-

import os, re
from PyQt4.QtCore import SIGNAL, QProcess
from PyQt4.QtCore import QThread
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_animation.infoVideo import infovideo
from moteur_modules_common.EkdTools import debug
from moteur_modules_common.EkdProcess import EkdProcess
####################################################################


#### Création le 14/07/09 ####################################################################
# --> Création de l'objet ffmpeg2theora pour séparer les traitements gérés par FFmpeg2theora
# de ceux gérés par Mencoder et FFmpeg
##############################################################################################

class FFmpeg2theora(QThread):
    """
    Classe permettant de ne gérer que la partie moteur de ffmpeg2theora (sans avoir
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
        super(FFmpeg2theora, self).__init__()
        self.codec = codec
        self.inputfile = inputfile
        self.outputfile = outputfile

        if os.name in ['posix', 'mac'] and (location == None):
            self.location=u"ffmpeg2theora"
        else :
            ## We are not on linux we force the ffmpeg location
            self.location=u"ffmpeg2theora"

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
        """ Démarre le processus ffmpeg2theora """
        if self.command == None :
            debug(u"FFmpeg2theora: Commande ffmpeg2theora non définie")
            raise Exception
        self.addLog(self.command.encode(EkdConfig.coding))
        try :
            ## Attention, ffmpeg envoie sa sortie de progression sur stderr !!!
            self.process = EkdProcess( self.command.encode(EkdConfig.coding),
                                        output = None, stdinput = None)
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
        line = line.strip()
        if re.match('^\d*:.*', line):
            heures, minutes, secondes = line.split(" ")[0].split(":")
            secondes = secondes.split(".")[0]
            val = (int(heures) * 3600) + (int(minutes) * 60) + int(secondes)
            self.setProgress(int( ( float(val) * 100 / self.videoLen) ))
        else:
            self.addLog(line)

    def setCommand(self, parametres):
        """ Configure la ligne de commande ffmpeg2theora """
        self.command = "%s \"%s\" -v %s -o \"%s\"" % \
                ( self.location, self.inputfile, parametres, self.outputfile)

