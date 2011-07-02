# -*- coding: utf-8 -*-

import os, string, subprocess
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdProcess import EkdProcess
from moteur_modules_common.EkdTools import debug


#######################################################
# 2010-04-07 : cette classe ne semble plus utilisée (à supprimer)
#
# $ grep ffmpeg_concat_audio -R . | grep import
#
#######################################################

############################################################################################
# Merci à l'auteur de: http://snippets.prendreuncafe.com/snippets/tagged/pyqt/order_by/date
# pour son code ... et son aide
############################################################################################
if os.name in ['posix', 'mac']:
        coding = "utf-8"
else :
        coding = "cp1252"

class FfmpegConcatThread(QThread):

    def __init__(self, cheminVideoEntre, cheminFFmpeg=None):

        QThread.__init__(self)

        self.cancel = False

        #=== Paramètres généraux ===#

        self.repTampon = unicode(EkdConfig.getTempDir() + os.sep)
        # Répertoire de sauvegarde ds le rep tampon
        self.rep_audio = self.repTampon  + u'concat_audio' + os.sep

        # Uniquement pour Linux et MacOSX
        if os.name in ['posix', 'mac'] or not cheminFFmpeg  :
            self.cheminFFmpeg=u"ffmpeg"

        elif cheminFFmpeg :
            self.cheminFFmpeg=unicode(cheminFFmpeg)

        # Uniquement pour windows
        else :
            self.cheminFFmpeg=u"ffmpeg"

        # chemin(s) des vidéos chargées
        self.cheminVideoEntre = cheminVideoEntre


    def run(self):

        for nb_1, fichier_1 in enumerate(self.cheminVideoEntre):

            if self.cancel: break

            commande = self.cheminFFmpeg+u" -i \""+unicode(fichier_1)+u"\" -ab 192k -ar 44100 -ac 2 -f wav -y \""+self.rep_audio+u"audio_"+unicode(string.zfill(str(nb_1+1), 5))+u".wav\""

            try:
                # Travail avec subprocess
                #sp = subprocess.Popen(commande.encode(coding), shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
                sp = EkdProcess(commande.encode(coding), outputerr=subprocess.STDOUT)
                # Important permet le traitement (!)
                self.tampon = sp.stdout.readlines()
            except Exception:
                debug (u"Erreur dans le lancement de %s" % commande)

            # Ca marche mieux avec pourcent calculé comme ça
            pourcent=((nb_1+1)*100)/len(self.cheminVideoEntre)

            # Emetteur pour la récup des valeurs du pourcentage
            self.emit(SIGNAL("increment(int)"), pourcent)

            # Emetteur pour (essayer) d'afficher chaque fichier chargé
            # (pour info) au bon moment dans la barre de progression
            self.emit(SIGNAL("travail_avec_fichier"), fichier_1)

            debug("%d " % (nb_1))


    @pyqtSignature("")
    def cancel(self):
        """SLOT to cancel treatment"""
        self.cancel = True


