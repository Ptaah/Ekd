# -*- coding: utf-8 -*-

import os
from PyQt4.QtGui import QDialog, QLabel, QPushButton, QProgressBar
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QApplication
from PyQt4.QtCore import SIGNAL, SLOT

from moteur_modules_animation.ffmpeg_avchd import FfmpegAvchd
from moteur_modules_common.EkdTools import debug

class WidgetFFmpegAvchd(QDialog):

    ### Ajout (le 13/08/2010) de spec_sortie_DNxHD et son_sortie_DNxHD #################
    def __init__(self, cheminVideoEntre, enregistrerSortie, codec_sortie, reso_largeur_sortie, reso_hauteur_sortie, nbreImgSec_sortie, qualite_sortie, spec_sortie_DNxHD, son_sortie_DNxHD, parent, cheminFFmpeg=None):

        QDialog.__init__(self)

        #=== Paramètres généraux ===#

        # Uniquement pour Linux et MacOSX
        if os.name in ['posix', 'mac']: self.cheminFFmpeg = "ffmpeg"

        # Uniquement pour windows
        elif os.name == 'nt': self.cheminFFmpeg = "ffmpeg.exe"

        # chemin(s) des vidéos chargées
        self.cheminVideoEntre = cheminVideoEntre
        # Chemin + nom de fichier en sortie
        self.enregistrerSortie = enregistrerSortie
        # Sélection du codec en sortie (par l'utilisateur)
        self.codec_sortie = codec_sortie
        # Sélection de la largeur (vidéo) en sortie (par l'utilisateur)
        self.reso_largeur_sortie = reso_largeur_sortie
        # Sélection de la hauteur (vidéo) en sortie (par l'utilisateur)
        self.reso_hauteur_sortie = reso_hauteur_sortie
        # Sélection du nbr d'img/sec en sortie (par l'utilisateur)
        self.nbreImgSec_sortie = nbreImgSec_sortie
        # Sélection de la qualité (de la vidéo) en sortie (par l'utilisateur)
        self.qualite_sortie = qualite_sortie
        # Widget qui appelle le traitement
        self.parent = parent

	### Ajouté le 13/08/2010 ###################################################
	self.spec_sortie_DNxHD = spec_sortie_DNxHD
	self.son_sortie_DNxHD = son_sortie_DNxHD
	############################################################################

        #self.fichiers = [os.path.basename(parc) for parc in self.cheminVideoEntre]

        # Appel de la fonction appliquer
        self.appliquer()
        self.fichiers_traites = []


    def appliquer(self):

        self.labelAttente=QLabel()
        self.labelAttente.setText(_(u"<p><b>Traitement des fichiers AVCHD par FFmpeg.</b></p><p>Traitement en cours, attendez la fin du calcul s'il vous plaît (soyez patient !)</p>"))

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

        #self.th = FfmpegAvchd(self.cheminVideoEntre, self.enregistrerSortie, self.codec_sortie, self.reso_largeur_sortie, self.reso_hauteur_sortie, self.nbreImgSec_sortie, self.qualite_sortie, self.cheminFFmpeg)

	### Rectification (le 13/08/2010) de self.spec_sortie_DNxHD et self.son_sortie_DNxHD #######
        self.th = FfmpegAvchd(self.cheminVideoEntre, self.enregistrerSortie, self.codec_sortie, self.reso_largeur_sortie, self.reso_hauteur_sortie, self.nbreImgSec_sortie, self.qualite_sortie, self.spec_sortie_DNxHD, self.son_sortie_DNxHD, self.cheminFFmpeg)

        # Connections pour l'appel et l'application du pourcentage dans la barre
        # ... essai de récup du fichier chargé ... pour eventuellement pouvoir
        # afficher le fichiers en cours dans la barre (au dessus de la barre
        # elle même --> mais pas réussi à importer fichier_1 pour pouvoir
        # l'afficher à la place de self.fichiers dans self.progress
        self.th.connect(self.th, SIGNAL("increment(int)"), self.affichPourcent)
        self.th.connect(self.th, SIGNAL("travail_avec_fichier"), self.fichierDeTravail)
        self.th.connect(self.th, SIGNAL("fin process"), self.end)

        self.progress.connect(self.progress, SIGNAL("canceled()"), self.th, SLOT("cancel()"))

        self.progress.show()
        self.th.start()

    def end(self) :
        debug(u"Conversion AVCHD terminé")
        self.parent.actionsFin(self.fichiers_traites)

    # On ajoute un parametre à la méthode
    def affichPourcent(self, pourcent):

        self.progress.setValue(pourcent)

        QApplication.processEvents()

        # Quand la progression arrive à 100%, la fenêtre
        # contenant la QProgressBar se ferme
        if pourcent == 100: self.close()

    # De même, on ajoute un parametre à la méthode
    def fichierDeTravail(self, fichier_1, out):
        self.fichiers_traites.append(out)
        debug(u'Fichier chargé: %s' % fichier_1)
