#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import SIGNAL, QFileInfo, Qt, QString
from PyQt4.QtGui import QWidget, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QIcon, QFrame, QFileDialog, QTabWidget, QLabel, QTextEdit, QRadioButton, QScrollArea
from moteur_modules_animation.mplayer import Mplayer, MetaMPlayer
from moteur_modules_common.EkdConfig import EkdConfig
from gui_modules_common.EkdWidgets import EkdAide
from gui_modules_common.EkdTamponIn import *

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

# On joue avec l'héritage
class Base(QWidget):
    """
        Module des cadres de l'onglet animation
    """

    Audio = 1
    Video = 2

    def __init__(self, boite='grid', nomReglage=None, nomSource=None, titre="None", parent=None):
        super(Base, self).__init__(parent)
        # Taille du widget mplayer
        self.tailleMplayer = (240,216)

        # Définition du titre
        self.Titre =  QLabel()
        self.setTitle(titre)

        # Définition des tabs
        #----------------------------------------------------------------
        self.Source =  QLabel("<h1>Source</h1>")
        self.Reglage =  QLabel("<h1>Reglage</h1>")
        self.Preview = QLabel("<h1>Preview</h1>")
        self.Logs = QLabel("<h1>Logs</h1>")

        self.tab = QTabWidget()
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.tab)
        self.scroll.setWidgetResizable(True)

        self.connect(self.tab, SIGNAL("currentChanged (int)"), self.activateTab)

        # Definition du layout :
        #| Titre                            |
        # ----------------------------------
        #| tabOuvrir | tabReglage | ... |   |
        #|----------------------------------|
        #|...                               |
        #|----------------------------------|
        #|Aide|                   |Appliquer|
        #'----------------------------------'
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.Titre)
        #self.layout.addWidget(self.tab)
        self.layout.addWidget(self.scroll)
        #----------------------------------------------------------------

        self.boutAide=QPushButton(_(u"Aide"))
        self.boutAide.setIcon(QIcon("Icones" + os.sep + "icone_aide_128.png"))
        self.connect(self.boutAide, SIGNAL("clicked()"), self.afficherAide)

        #self.tamponBut = QPushButton(QIcon("Icones"+os.sep+"icone_load_128.png"), _(u"Tampon test"))
        #self.connect(self.tamponBut, SIGNAL("clicked()"), self.tamponAction)

        # On ajoute des bouton pour forcer l'utilisateur à vérifier ses réglages
        self.Next = QPushButton(_(u"Réglages"))
        ####################################################################
        self.Next.setIcon(QIcon("Icones" + os.sep + "droite.png"))
        ####################################################################
        self.connect(self.Next, SIGNAL("clicked()"), self.next)

        self.boutApp=QPushButton(_(u"Appliquer"))
        self.boutApp.setIcon(QIcon("Icones" + os.sep + "icone_appliquer_128.png"))
        ## Le bouton doit toujours être désactivé à l'initialisation
        self.boutApp.setEnabled(False)

        self.connect(self.boutApp, SIGNAL("clicked()"), self.appliquer)

        # ligne de séparation juste au dessus des boutons
        ligne = QFrame()
        ligne.setFrameShape(QFrame.HLine)
        ligne.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(ligne)
        self.layout.addSpacing(-5)      # la ligne doit être plus près des boutons

        hbox=QHBoxLayout()
        hbox.addWidget(self.boutAide)
        #hbox.addWidget(self.tamponBut)
        hbox.addStretch()       # espace entre les 2 boutons
        hbox.addWidget(self.Next)
        hbox.addWidget(self.boutApp)

        self.layout.addLayout(hbox)

    def tamponAction(self) :
      """Fonction à définir dans chaque tableau pour importer les données du tampon"""
      #print u"[DEBUG] Fonction tamponAction non implémentée dans le tableau ", self.idSection
      EkdPrint(u"[DEBUG] Fonction tamponAction non implémentée dans le tableau %s" % self.idSection)

    def setTitle(self, titre=_(u"Title")):
        titre=u"<h2>" + titre + u"</h2>"
        self.Titre.setText(titre)

    def add(self, objet, nom=_(u"Onglet")):
        self.tab.addTab(objet, nom)

    def activateTab(self, index):
        tabCount = self.tab.count()
        if 0 == index :
            self.Next.setText(_(u"Réglages"))
        elif ( tabCount - 1 ) == index :
            self.Next.setText(_(u"Recommencer"))
        elif (tabCount - 2) == index :
            self.Next.setText(_(u"Infos supplémentaires"))
        else:
            self.Next.setText(_(u"Suivant"))

    def next(self):
        tabCount = self.tab.count()
        index = self.tab.currentIndex()
        index = (index + 1) % tabCount
        self.tab.setCurrentIndex(index)

    #----------------
    # Meta-widgets
    #----------------


    def addSource(self, type, nomSource=None):
        """ Boîte de groupe : "Fichier vidéo source" """
        if type == Base.Video :
            if not nomSource: nomSource=_(u'Vidéo source')
            self.ligneEditionSource=QLineEdit()
            self.ligneEditionSource.setReadOnly(True)
            boutParcourir=QPushButton(_(u'Parcourir...'))
            boutParcourir.setIcon(QIcon("Icones/ouvrir.png"))
            self.connect(boutParcourir, SIGNAL("clicked()"), self.ouvrirSource)

            groupSource=QGroupBox(nomSource)
            hbox=QHBoxLayout(groupSource)
            hbox.addWidget(self.ligneEditionSource)
            hbox.addWidget(boutParcourir)
            self.Source = groupSource
            self.tabOuvrirVideo  = self.tab.addTab(self.Source, nomSource)

        else :
            if not nomSource: nomSource=_(u"Fichier audio source")
            self.ligneEditionSourceAudio=QLineEdit()
            self.ligneEditionSourceAudio.setReadOnly(True)

            boutParcourir=QPushButton(_(u'Parcourir...'))
            boutParcourir.setIcon(QIcon("Icones/ouvrir.png"))
            self.connect(boutParcourir, SIGNAL("clicked()"), self.ouvrirSource)

            groupSource=QGroupBox(nomSource)
            hbox=QHBoxLayout(groupSource)
            hbox.addWidget(self.ligneEditionSourceAudio)
            hbox.addWidget(boutParcourir)
            self.Source = groupSource
            self.tabOuvrirAudio = self.tab.addTab(self.Source, nomSource)


    def addReglage(self, boite='hbox', nomReglage = None):
        """ Boîte de groupe de réglage """
        if not nomReglage: nomReglage=_(u"Réglages")
        self.groupReglage=QGroupBox()

        if boite=='vbox':
            self.layoutReglage = QVBoxLayout(self.groupReglage)
        elif boite=='hbox':
            self.layoutReglage = QHBoxLayout(self.groupReglage)
        elif boite=='grid':
            self.layoutReglage = QGridLayout(self.groupReglage)

        self.Reglage = self.groupReglage
        self.add(self.Reglage, nomReglage)



    def addPreview(self, boite='vbox', nomPreview = None, light = False, mode = "Video"):
        # ----------------------------
        # Boite de groupe de mplayer
        # ----------------------------
        group=QGroupBox("")
        if nomPreview == None : nomPreview=_(u'Visionner vidéo')
        else : nomPreview=_(nomPreview)
        vboxMplayer = QVBoxLayout(group)
        if mode =="Video+Audio" :
            vidtitre = QLabel(_(u"Vidéo"))
            vidtitre.setAlignment(Qt.AlignHCenter)
            vboxMplayer.addWidget(vidtitre)

        self.mplayer=Mplayer(taille=(250, 225), choixWidget=(Mplayer.RATIO, Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_SUR_UNE_LIGNE,Mplayer.PAS_PARCOURIR, Mplayer.LIST))
        ## On utilise la nouvelle interface de récupération des vidéos
        self.mplayer.listeVideos = []
        self.mplayer.setEnabled(False)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.mplayer)
        hbox.addStretch()
        vboxMplayer.addLayout(hbox)
        hbox = QHBoxLayout()
        if not light :
            self.radioSource = QRadioButton(_(u"vidéo(s) source(s)"))
            self.radioSource.setChecked(True)
            self.radioSource.setEnabled(False)
            self.connect(self.radioSource, SIGNAL("toggled(bool)"), self.fctRadioSource)
            self.radioConvert = QRadioButton(_(u"vidéo(s) convertie(s)"))
            self.radioConvert.setEnabled(False)
            self.connect(self.radioConvert, SIGNAL("toggled(bool)"), self.fctRadioConvert)
            self.boutCompare = QPushButton(_(u"Comparateur de vidéos"))
            self.boutCompare.setEnabled(False)

            self.connect(self.boutCompare, SIGNAL("clicked()"), self.widget2Mplayer)
            hbox.addWidget(self.radioSource)
            hbox.addWidget(self.radioConvert)
            hbox.addWidget(self.boutCompare)
            if self.idSection == "animation_filtresvideo":
                self.boutApercu = QPushButton(_(u"Aperçu"))
                self.connect(self.boutApercu, SIGNAL("clicked()"), self.apercu)
                self.boutApercu.setEnabled(False)
                hbox.addWidget(self.boutApercu)

        if mode =="Video+Audio" :
            self.mplayerA=Mplayer(taille=(250, 225), choixWidget=(Mplayer.RATIO,Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_SUR_UNE_LIGNE,Mplayer.PAS_PARCOURIR))
            self.mplayerA.setAudio(True)
            self.mplayerA.listeVideos = []
            self.mplayerA.setEnabled(False)
            hboxA = QHBoxLayout()
            hboxA.addStretch()
            hboxA.addWidget(self.mplayerA)
            hboxA.addStretch()

        hbox.setAlignment(Qt.AlignHCenter)
        vboxMplayer.addLayout(hbox)
        if mode =="Video+Audio" :
            audtitre = QLabel(_(u"Audio"))
            audtitre.setAlignment(Qt.AlignHCenter)
            vboxMplayer.addWidget(audtitre)
            vboxMplayer.addLayout(hboxA)
        vboxMplayer.addStretch()
        group.setAlignment(Qt.AlignHCenter)
        self.add(group, nomPreview)

    def addLog(self):
        self.Logs = QTextEdit()
        self.tabLog = self.add(self.Logs, _(u'Infos'))



    def infoLog(self, image=None, video=None, audio=None, sortie=None) :
        """Fonction pour la mise à jour des informations de log données à l'utilisateur en fin de process sur les données entrées, et le résultat du process"""
        if image != None :
            if type(image) == list :
                msgIm = _(u"<p>####################################<br># Images chargées<br>####################################</p>")
                for im in image :
                    msgIm += unicode(im)+u"<br>"
            else :
                msgIm = _(u"<p>####################################<br># Image chargée<br>####################################</p>")+unicode(image)+u"<br>"
        else :
            msgIm = u""

        if video != None :
            if type(video) == list :
                msgVid = _(u"<p>####################################<br># Vidéos chargées<br>####################################</p>")
                for vid in video :
                    msgVid += unicode(vid)+u"<br>"
            else :
                msgVid = _(u"<p>####################################<br># Vidéo chargée<br>####################################</p>")+unicode(video)+u"<br>"
        else :
            msgVid = u""

        if audio != None :
            if type(audio) == list :
                msgAu = _(u"<p>####################################<br># Fichiers audio chargés<br>####################################</p>")
                for au in audio :
                    msgAu += unicode(au)+u"<br>"
            else :
                msgAu = _(u"<p>####################################<br># Fichier audio chargé<br>####################################</p>")+unicode(audio)+u"<br>"
        else :
            msgAu = u""

        if sortie != None :
            if type(sortie) == list :
                msgOut = _(u"<p>####################################<br># Fichiers de sortie<br>####################################</p>")
                for out in sortie :
                    msgOut += unicode(out)+u"<br>"
            else :
                msgOut = _(u"<p>####################################<br># Fichier de sortie<br>####################################</p>")+unicode(sortie)+u"<br>"
        else :
            msgOut = _(u"<p>Sortie non définie ???</br>")
        messageLog = QString(msgIm+msgVid+msgAu+msgOut)
        self.Logs.setHtml(messageLog)

    def widget2Mplayer(self):
        """Boite de dialogue de comparaison de vidéos"""

        if type(self.chemin) == list :
            chemin = self.chemin
        else :
            chemin = [self.chemin]

        mplayerAvantConv=Mplayer(chemin, (350,262), (Mplayer.RATIO, Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_SUR_UNE_LIGNE,Mplayer.PAS_PARCOURIR, Mplayer.LIST))

        # Widget-mplayer après encodage: lecture du fichier de sortie

        mplayerApresConv=Mplayer(self.lstFichiersSortie, (350,262), (Mplayer.RATIO, Mplayer.PAS_PRECEDENT_SUIVANT,Mplayer.CURSEUR_SUR_UNE_LIGNE,Mplayer.PAS_PARCOURIR, Mplayer.LIST))

        #print "Affichage de la meta-barre mplayer"
	EkdPrint(u"Affichage de la meta-barre mplayer")
        metaMPlayer = MetaMPlayer(mplayerAvantConv,mplayerApresConv)
        metaMPlayer.exec_()

    #---------------------
    # Fonctions communes
    #---------------------

    def fctRadioSource(self, bool=None):
        """"Communique la vidéo appropriée à mplayer"""
        if bool:
            self.mplayer.setVideos(self.chemin)
            self.mplayer.arretMPlayer()
            try :
                self.radioConvert.setChecked(False)
            except : None

    def fctRadioConvert(self, bool=None):
        """"Communique la vidéo résultat appropriée à mplayer"""
        if bool:
            self.mplayer.arretMPlayer()
            self.mplayer.setVideos(self.lstFichiersSortie)
            try :
                self.radioSource.setChecked(False)
            except : None


    def repSortieProv(self):
        """Répertoire sur lequel s'ouvrira la boite de dialogue de sauvegarde"""
        rep = os.path.dirname(unicode(self.chemin))

        if os.path.exists(rep): return rep
        else: return '~'


    def recupSources(self, nomEntree=None):
        """Récupère les fichiers sources vidéo via une boite de dialogue. Utilise et modifie les paramètres de configuration"""

        if not self.lstFichiersSource: listePleine = False
        else:
            listePleine = True
            fichier = self.lstFichiersSource[0]
            path = os.path.dirname(fichier)

        if listePleine and os.path.exists(path):
            repEntree = path
        else:
            try:
                repEntree = EkdConfig.get('general','video_input_path').decode("UTF8")
            except Exception, e:
                repEntree = '~'
                EkdConfig.set('general','video_input_path', repEntree.encode("UTF8"))
            if not os.path.exists(repEntree):
                repEntree = '~'
                EkdConfig.set('general','video_input_path', repEntree.encode("UTF8"))

        txt = _(u"Fichiers vidéo")
        if not nomEntree:
            liste=QFileDialog.getOpenFileNames(None, _(u"Ouvrir"), os.path.expanduser(repEntree),
                    "%s (*.avi *.mpg *.mpeg *.mjpeg *.flv *.mp4 *.h264 *.dv *.vob)\n*" %txt)
            liste = [unicode(i) for i in liste]
        else: # module séquentiel
            liste = nomEntree

        if len(liste)==0: return
        EkdConfig.set('general','video_input_path',os.path.dirname(liste[0]).encode("UTF8"))

        return liste


    def recupSourcesAudio(self, nomEntree=None):
        """Récupère les fichiers sources audio via une boite de dialogue. Utilise et modifie les paramètres de configuration"""

        if not self.lstFichiersSourceAudio: listePleine = False
        else:
            listePleine = True
            fichier = self.lstFichiersSourceAudio[0]
            path = os.path.dirname(fichier)

        if listePleine and os.path.exists(path):
            repEntree = path
        else:
            try:
                repEntree = EkdConfig.get('general','audio_input_path').decode("UTF8")
            except Exception, e:
                repEntree = '~'
                EkdConfig.set('general','audio_input_path', repEntree.encode("UTF8"))
            if not os.path.exists(repEntree):
                repEntree = '~'
                EkdConfig.set('general','audio_input_path', repEntree.encode("UTF8"))

        txt = _(u"Fichiers audio")
        if not nomEntree:
            liste=QFileDialog.getOpenFileNames(None, _(u"Ouvrir"), os.path.expanduser(repEntree),
                    "%s (*.ogg *.mp3 *.wav *.ac3 *.wmv *.mp2)\n*" %txt)
            liste = [unicode(i) for i in liste]
        else: # module séquentiel
            liste = nomEntree

        if len(liste)==0: return
        EkdConfig.set('general','audio_input_path',os.path.dirname(liste[0]).encode("UTF8"))
        return liste


    def recupSource(self, nomEntree=None, exclure_type=None, inclure_type=None):
        """Récupère le fichier source vidéo via une boite de dialogue. Utilise et modifie les paramètres de configuration"""

        try :
            if self.ligneEditionSource.text().isEmpty(): lignePleine = False
        except:
            return
        else:
            lignePleine = True
            fichier = unicode(self.ligneEditionSource.text())
            path = os.path.dirname(fichier)

        if lignePleine and os.path.exists(path):
            repEntree = path
        else:
            try:
                repEntree = EkdConfig.get('general','video_input_path').decode("UTF8")
            except Exception, e:
                repEntree = '~'
                EkdConfig.set('general','video_input_path', repEntree.encode("UTF8"))
            if not QFileInfo(repEntree).exists():
                repEntree = '~'
                EkdConfig.set('general','video_input_path', repEntree.encode("UTF8"))

        if not nomEntree:
            formats = ['avi', 'mpg', 'mpeg', 'mjpeg', 'flv', 'mp4', 'dv', 'vob'] ##
            if exclure_type:
                for type_ in exclure_type:
                    if type_ in formats: formats.remove(type_)
            if inclure_type:
                formats.append(inclure_type)
            formats2 = ["*.%s" %i for i in formats]
            txt = _(u"Fichiers vidéo")
            chemin=unicode(QFileDialog.getOpenFileName(None, _(u"Ouvrir"),os.path.expanduser(repEntree),
                    "%s (%s)\n*" %(txt, " ".join(formats2))))
        else: # module séquentiel
            chemin = nomEntree

        if not chemin: return


        EkdConfig.set('general','video_input_path',os.path.dirname(chemin).encode("UTF8"))
        return chemin


    def recupSourceAudio(self, nomEntree=None):
        """Récupère le fichier source audio via une boite de dialogue. Utilise et modifie les paramètres de configuration"""

        if self.ligneEditionSource.text().isEmpty(): lignePleine = False
        else:
            lignePleine = True
            fichier = unicode(self.ligneEditionSource.text())
            path = os.path.dirname(fichier)

        if lignePleine and os.path.exists(path):
            repEntree = path
        else:
            try:
                repEntree = EkdConfig.get('general','audio_input_path').decode("UTF8")
            except Exception, e:
                repEntree = '~'
                EkdConfig.set('general','audio_input_path', repEntree.encode("UTF8"))
            if not QFileInfo(repEntree).exists():
                repEntree = '~'
                EkdConfig.set('general','audio_input_path', repEntree.encode("UTF8"))

        if not nomEntree:
            txt = _(u"Fichiers audio")
            chemin=unicode(QFileDialog.getOpenFileName(None, _(u"Ouvrir"),os.path.expanduser(repEntree),
                    "%s (*.ogg *.mp3 *.wav *.ac3 *.wmv *.mp2)\n*" %txt))
        else: # module séquentiel
            chemin = nomEntree

        if not chemin: return
        EkdConfig.set('general','audio_input_path',os.path.dirname(chemin).encode("UTF8"))
        return chemin


    def afficherAide(self,msg=None):
        """ Boîte de dialogue de l'aide"""
        if not msg: _(u"Message d'aide")
        message=EkdAide(parent=self)
        message.setText(msg)
        message.show()


    def printSection(self):
        """Affichage dans le terminal de la section initialisée"""
        #print '\n'+'-'*30+'\n| '+self.idSection+'\n'+'-'*30+'\n'
	EkdPrint('\n'+'-'*30+'\n| '+self.idSection+'\n'+'-'*30+'\n')

    def load(self):
        """
        Chargement de la configuration de tous les objets des éléments de l'objet
        """
        #print "[Debug] Chargement non implémenté dans ", self.idSection
	EkdPrint(u"[Debug] Chargement non implémenté dans %s" % self.idSection)

    def save(self):
        """
        Sauvegarde de la configuration de tous les objets des éléments de l'objet
        """
        #print "[Debug] Sauvegarde non implémenté dans ", self.idSection
	EkdPrint(u"[Debug] Sauvegarde non implémenté dans %s" % self.idSection)
