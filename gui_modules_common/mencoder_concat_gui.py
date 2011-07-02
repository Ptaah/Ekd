# -*- coding: utf-8 -*-
import os, glob
from PyQt4.QtCore import SIGNAL, SLOT, pyqtSignature
from PyQt4.QtGui import QDialog, QMessageBox, QLabel, QPushButton, QVBoxLayout
from PyQt4.QtGui import QHBoxLayout, QProgressBar, QApplication
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_animation.mencoder_concat_video import MencoderConcatThread
from moteur_modules_common.EkdTools import debug

class WidgetMEncoderConcatExtResol(QDialog):

        def __init__(self, cheminVideoEntre, valeurNum=0, cheminMEncoder=None):

                QDialog.__init__(self)

                #=== Paramètres généraux ===#

                self.repTampon = EkdConfig.getTempDir() + os.sep
                # Répertoire de sauvegarde ds le rep tampon
                self.rep_video_ext_resol = self.repTampon  + 'video_extension_resol' + os.sep

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

                self.fichiers = [os.path.basename(parc) for parc in self.cheminVideoEntre]

                # Appel de la fonction lanceur
                self.lanceur()


        def lanceur(self):

                # Au cas où le répertoire existait déjà et qu'il n'était pas vide -> purge (simple précausion)
                # Cela est indispensable ici car si on relance le montage sans avoir purgé le répertoire, le
                # montage se fera avec les anciennes vidéos mélangées aux nouvelles (donc gros problème !)
                if os.path.isdir(self.rep_video_ext_resol) is True:
                        for toutRepCompo in glob.glob(self.rep_video_ext_resol+'*.*'):
                                os.remove(toutRepCompo)

                infoConfirm = QMessageBox.information(self, 'Message',
                _(u"<p>Vous voyez cette boîte de dialogue car vous vous apprêtez à concaténer des vidéos ayant des extensions différentes (c'est à dire préalablement encodées dans des codecs différents).</p><p><b>Sachez malgré tout que la vidéo finale</b> (résultat final de la concaténation), <b>sera encodée en Motion JPEG (extension .avi)</b>.</p><p>Sachez de même que vous pouvez encoder des vidéos ayant des résolutions différentes (largeur x hauteur), <b>la taille de la vidéo finale sera celle de la vidéo la plus répandue dans les vidéos chargées</b> (si vous avez chargé des vidéos avec des dimensions complètement différentes, la taille sélectionnée sera celle de la première vidéo du lot).</p><p><b>Si au moins une des vidéos du lot ne possède pas de canal audio</b> (c'est à dire qu'elle ne comporte pas de son), <b>la concaténation finale se fera sans le son</b>.</p><p><b>Voulez-vous continuer ?</b> (si vous répondez non le traitement n'aura pas lieu correctement)."), QMessageBox.Yes, QMessageBox.No)
                if infoConfirm == QMessageBox.No: return
                elif infoConfirm == QMessageBox.Yes: self.appliquer()


        @pyqtSignature("")
        def appliquer(self):

                self.labelAttente=QLabel()
                self.labelAttente.setText(_(u"<p><b>Encodage des vidéos en Motion JPEG</b></p><p>Attendez la fin du calcul s'il vous plaît (soyez patient !) ... traitement des fichiers: </p><p><b>%s</b></p>" % "<br>".join(self.cheminVideoEntre)))

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

                self.th = MencoderConcatThread(self.cheminVideoEntre, self.valeurNum, self.cheminMEncoder)#, parent=None) #
                
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
                if pourcent == 100:
                        self.th.wait()
                        self.close()


        # De même, on ajoute un parametre à la méthode
        def fichierDeTravail(self, fichier_1):

                debug ( u'Fichier chargé: %s' % fichier_1)
