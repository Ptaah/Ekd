# -*- coding: utf-8 -*-

import os
from PyQt4.QtGui import QDialog, QLabel, QPushButton, QProgressBar
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout
from PyQt4.QtCore import SIGNAL

from moteur_modules_animation.ffmpeg_concat_audio import FfmpegConcatThread
from moteur_modules_common.EkdTools import debug

#######################################################
# 2010-04-07 : cette classe ne semble plus utilisée (à supprimer)
#
# $ grep ffmpeg_concat_audio -R . | grep import
#
#######################################################

class WidgetFFmpegConcatAudio(QDialog):

    def __init__(self, cheminVideoEntre, cheminFFmpeg=None):

        QDialog.__init__(self)

        #=== Paramètres généraux ===#

        # Uniquement pour Linux et MacOSX
        if os.name in ['posix', 'mac'] or not cheminFFmpeg :
            self.cheminFFmpeg=u"ffmpeg"

        # Uniquement pour windows
        elif os.name == 'nt' and cheminFFmpeg :
                self.cheminFFmpeg=unicode(cheminFFmpeg)

        # chemin(s) des vidéos chargées
        self.cheminVideoEntre = cheminVideoEntre

        self.fichiers = [os.path.basename(parc) for parc in self.cheminVideoEntre]

        self.appliquer()


    @pyqtSignature("")
    def appliquer(self):

        self.labelAttente=QLabel()
        self.labelAttente.setText(_(u"<p><b>Encodage des fichiers audio en WAV</b></p><p>Attendez la fin du calcul s'il vous plaît (soyez patient !) ... traitement des fichiers: </p><p><b>%s</b></p>" % "<br>".join(self.cheminVideoEntre)))

        self.bout_annuler = QPushButton(_(u"Annuler"))

        self.progress = QProgressBar()

        self.progress.setMaximum(100)
        self.progress.setValue(0)

        vbox = QVBoxLayout()
        vbox.addWidget(self.labelAttente)
        hbox = QHBoxLayout()
        hbox.addWidget(self.progress)
        hbox.addWidget(self.bout_annuler)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.connect(self.bout_annuler, SIGNAL('clicked()'), SLOT('close()'))

        self.th = FfmpegConcatThread(self.cheminVideoEntre, self.cheminFFmpeg)

        # Connections pour l'appel et l'application du pourcentage dans la barre
        # ... essai de récup du fichier chargé ... pour eventuellement pouvoir
        # afficher le fichiers en cours dans la barre (au dessus de la barre
        # elle même --> mais pas réussi à importer fichier_1 pour pouvoir
        # l'afficher à la place de self.fichiers dans self.progress
        self.th.connect(self.th, SIGNAL("increment(int)"), self.affichPourcent)
        self.th.connect(self.th, SIGNAL("travail_avec_fichier"), self.fichierDeTravail)

        self.progress.connect (self.progress, SIGNAL("canceled()"), self.th, SLOT("cancel()"))

        self.progress.show()
        self.th.start()


    # On ajoute un parametre à la méthode
    def affichPourcent(self, pourcent):
        self.progress.setValue(pourcent)

        QApplication.processEvents()

        # Quand la progression arrive à 100%, la fenêtre
        # contenant la QProgressBar se ferme
        if pourcent == 100: self.close()


    # De même, on ajoute un parametre à la méthode
    def fichierDeTravail(self, fichier_1):
        debug('Fichier chargé: %s' % fichier_1)
