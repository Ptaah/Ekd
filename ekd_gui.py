#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re
import sys
from gui_modules_music_son.music_son_base_sox import checkSoxEncoding
from moteur_modules_common.EkdProcess import EkdProcess
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############
from moteur_modules_common.EkdTools import debug
from gui_modules_common.EkdTamponIn import *

from PyQt4.QtCore import Qt, SIGNAL, QSize, QFile, QIODevice, QTextStream
from PyQt4.QtCore import QLocale, QTranslator, QStringList
from PyQt4.QtGui import QDialog, QTabWidget, QVBoxLayout, QFrame, QTextBrowser
from PyQt4.QtGui import QPixmap, QDialogButtonBox, QImage, QMainWindow
from PyQt4.QtGui import QApplication, QMessageBox, QStyleFactory


# Pour windows uniquement
if os.name == 'nt':
    "#! "+sys.executable

'''
-----------------------------------------------------------------------
GPL v3
-----------------------------------------------------------------------
EKD can be used to make post production operations for video files and images.
Copyright (C) 2011 Lama Angelo (the historical developer of the
program) with the contribution of Aurélien Cedeyn and Olivier Ponchaut to
this 2011 version of EKD.

EKD is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your
option) any later version.

EKD is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see http://www.gnu.org/licenses
or write to the Free Software Foundation,Inc., 51 Franklin Street,
Fifth Floor, Boston, MA 02110-1301  USA

To contact the developpers of EKD, go here:
http://ekd.tuxfamily.org/forum/forumdisplay.php?fid=8
-----------------------------------------------------------------------
'''

### Vérification des possibilités ffmpeg - Sox ########
import subprocess
###############################################################################
import gettext


### Import de minidom pour Videoporama
##############################################################
from xml.dom import minidom



def verifAppliManquante():
    """# -------------------------------------
    # Dépendances ...
    # Vérification de la présence des logs
    # indispensables au lancement d'EKD
    # -------------------------------------"""

    #print ""
    EkdPrint(u"")
    manquantes = []

    ##########################################################################
    all = ['pyqt4', 'python imaging library', 'numpy', 'mplayer', 'mencoder',\
    'imagemagick', 'ffmpeg', 'ffmpeg2theora', 'lame', 'mjpegtools', 'sox']
    ##########################################################################

    ### Les vérifications pour FFMPEG sont valable pour Win.
    if os.name in ['posix', 'mac']:

        commandesBash = ['mplayer', 'mencoder', 'composite', 'ffmpeg', 
                            'ffmpeg2theora', 'lame', 'ppmtoy4m', 'sox']

        for commande in commandesBash:
            resultat = os.popen("which " + commande).readline()
            if not resultat:
                if commande == 'composite': manquantes.append('imagemagick')
                # ppmtoy4m est inclu dans mjpegtools dans ubuntu hardy #########
                elif commande == 'ppmtoy4m': manquantes.append('mjpegtools')
                else: manquantes.append(commande)
            ####################################################################

    fmsg = 0
    msgffmpeg = QStringList()
    listformats = QStringList()
    convertformat = []

    #f = subprocess.Popen("ffmpeg -version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    f = EkdProcess("ffmpeg -version")

    ffmpeglib=[[0,"raw","RAW DV (dv)","","dv"],[1,"VCD","VCD","","mpg"],[2,"SVCD","SVCD","","mpg"],[3,"DVD","DVD","","mpg"],[4,"flv","Flash FLV","","flv"],[5,"libtheora","Theora (ogg)","--enable-libtheora","ogg"],[6,"mjpeg","MJPEG (avi)","","avi"],[7,"libxvid","Xvid (avi)","--enable-libxvid","avi"],[8,"libx264","H264 (avi)","--enable-libx264","avi"]]

    verffmpeg = f.communicate()[1]
    # Vérification de la version de FFmpeg pour les fonctions AVCHD
    z = verffmpeg.split("\n")
    avchd = False
    for a in z :
        ## Utilisation des expression regulières
        if re.match('\s+libavformat.*', a):
            ffmpegversion = re.findall("\d+", a)[0]
            if int(ffmpegversion) >= 52 :
                avchd = True

    for ff in ffmpeglib :
        if verffmpeg.find(ff[3]) == -1 :
            fmsg = 1
            msgffmpeg.append(u"Le package ffmpeg installé n'inclut pas %s et n'est pas capable d'encoder en %s. Ce format sera désactivé de l'interface utilisateur." % (ff[1],ff[2]))
        else :
            listformats.append(ff[2])
            convertformat.append((ff[0],ff[1],ff[4]))
    #s = subprocess.Popen("sox -h", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid).communicate()[0]
    s = EkdProcess("sox -h").communicate()[0]
    soxErr=0
    msgsox = QStringList()
    if s.find("wav") == -1 :
        soxErr = 1
        msgsox.append(_(u"Le format Wav n'est pas supporté par votre package SoX. Ajouter les paquets nécessaires au départ des dépôts de votre distribution sans quoi vous ne serez pas en mesure de faire des diaporamas d'image vidéo."))
    if s.find("ogg") == -1 :
        soxErr = 1
        msgsox.append(_(u"Le format Ogg n'est pas supporté par votre package SoX. Ajouter les paquets nécessaires au départ des dépôts de votre distribution sans quoi vous ne serez pas en mesure d'utiliser des fichiers son au format Ogg."))
    if s.find("mp3") == -1 :
        soxErr = 1
        msgsox.append(_(u"Le format Mp3 n'est pas supporté par votre package SoX. Ajouter les paquets nécessaires au départ des dépôts de votre distribution sans quoi vous ne serez pas en mesure d'utiliser des fichiers son au format Mp3."))
    ############################################################################################################

    try: from PyQt4 import QtGui, QtCore
    except ImportError, e:
        manquantes.append('python-qt4')
        #print "ImportError:", e
        EkdPrint(u"ImportError: %s" % e)

    try: from numpy import lib
    except ImportError, e:
        manquantes.append('python-numpy')
        #print "ImportError:", e
        EkdPrint(u"ImportError: %s" % e)

    try: from PIL import Image
    except ImportError, e:
        manquantes.append('python-imaging')
        #print "ImportError:", e
        EkdPrint(u"ImportError: %s" % e)

    a=u'\n'+u'='*40+u'\n'
    if manquantes:
        apps = u', '.join(manquantes)
        m1=u"Les applications suivantes n'ont pas été détectées:\n"
        m2=u"\nEKD ne sera pas pleinement fonctionnel (s'il démarre...)\n\
        \nYou must install the packages:\n"
        #print a,m1.encode("UTF-8"),apps.encode("UTF-8"),m2.encode("UTF-8"),apps.encode("UTF-8"),a,msgffmpeg,msgsox
        EkdPrint("%s %s %s %s %s %s %s %s" % (a, m1, apps, m2, apps, a, msgffmpeg, msgsox))
        return 0, ', '.join(manquantes), fmsg, msgffmpeg, listformats, convertformat, soxErr, msgsox

    else:
        #print u'PyQT version : ', QtCore.PYQT_VERSION_STR
        EkdPrint(u'PyQT version : %s' % QtCore.PYQT_VERSION_STR)
        m = u"Toutes les dépendances sont satisfaites\n\nAll packages are installed"
        return 1, ', '.join(all), fmsg, msgffmpeg, listformats, convertformat, soxErr, msgsox, avchd


import ConfigParser, locale, platform

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Version de ekd
__version__ = "2.0.8"


class Aide_Info(QDialog):
    '''# -------------------------------------------------------------
    # Classe pour Chargement de la boîte de dialogue pour afficher
    # l'aide en ligne (affichée dans le browser web par défaut du
    # système), les infos de développement et la licence
    # -------------------------------------------------------------
    '''
    ## La largeur de la fenêtre est définie de façon à pouvoir afficher les caractères suivants sur une ligne
    #WSTRING = "EKD is free software; you can redistribute it and/or modify it under the terms of the GNU General Public"

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setMinimumSize(QSize(800, 480))
        # Titre de la fenetre
        self.setWindowTitle(_(u'Infos'))

        vbox_aide=QVBoxLayout()

        self.tabwidget=QTabWidget()

        #=== 1er onglet ===#
        self.fram_2=QFrame()
        vboxFram_2=QVBoxLayout(self.fram_2)

        txt = ""
        txt += _(u"<p><u><b>Version</b></u>")
        txt += "<p><b>Ekd</b> v %s" % __version__
        txt_ = _(u"Cette application peut être utilisée pour des opérations de post-production pour vidéo et lots d'images")
        txt += "<p>" + txt_
        txt_ = _(u"Mai 2011")
        txt += "<p>" + txt_
        txt += """<p>Python %s - Qt %s - PyQt %s - %s""" % (
            platform.python_version(),
            QT_VERSION_STR, PYQT_VERSION_STR, platform.system())
        txt += _(u"<p><u><b>Développement</b></u>")
        txt += _(u"<p>* Lama Angelo: développeur historique du logiciel")
        txt += _(u"<p>* Olivier Ponchaut (Marmotte): développeur")
        txt += _(u"<p>* Aurélien Cedeyn (Ptah): développeur")
        txt += _(u"<p><u><b>Traduction anglaise</b></u>")
        txt += _(u"<p>* Bellegarde Sophie")
        txt += _(u"<p>* Bellegarde Laurent")
        txt += _(u"<p><u><b>Traduction espagnole</b></u>")
        txt += _(u"<p>* Jesús MUÑOZ")
        txt += _(u"<p><u><b>Traduction anglaise du site officiel</b></u>")
        txt += _(u"<p>* Paparelle Giorgio")
        txt += _(u"<p><u><b>Graphisme</b></u>")
        txt += _(u"<p>* Labarussias Thomas: conception des icônes et du logo officiel")
        txt += _(u"<p><u><b>Avec la participation de ...</b></u>")
        txt += _(u"<p>* Bellegarde Laurent: tests divers et conseils")
        txt += _(u"<p>* Lusson Julien: tests divers et conseils")
        txt += _(u"<p><u><b>Partenariat (le projet EKD est soutenu par):</b></u>")
        txt += _(u"<p>* Lprod: http://fr.lprod.org")
        txt += _(u"<p>* Le collège Dunois à Caen (France): http://lcs.dunois.clg14.ac-caen.fr/~site-web")
        txt += _(u"<p><u><b>Suivre EKD:</b></u>")
        txt += _(u"<p>* Le site: http://ekd.tuxfamily.org")
        txt += _(u"<p>* Le blog: http://ekdm.wordpress.com")
        txt += _(u"<p>* Le forum: http://ekd.tuxfamily.org/forum")

        zoneText = QTextEdit(txt)
        if PYQT_VERSION_STR >= "4.1.0":
            zoneText.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.TextSelectableByKeyboard)
        zoneText.setReadOnly(True)

        vboxFram_2.addWidget(zoneText,1)
        vboxFram_2.setAlignment(Qt.AlignHCenter)
        vboxFram_2.addStretch()
        #########################################################################################################################

        #=== 2ème onglet ===#
	#### Changements faits le 13/02/11 --> pour pouvoir afficher les didacticiels d'EKD en anglais quand ############
	#### un utilisateur non francophone les consulte ################################################################
	locale_debut = str(QLocale.system().name())[0:2]
	# Liens en français
	if locale_debut == 'fr':
		docGen = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/Linux\">" # Documentation générale
		docBarrOutConfEkd = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/MenuEtBarreOutils\">" # Barre d'outils et configuration d'EKD
		docTraitVidParExemp = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/TraitementVideoPresentation\">" # Le traitement vidéo par l’exemple
		docTraitImgParExemp = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/TraitementImagePresentation\">" # Le traitement des images par l’exemple
		docFiltresVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/VideoFiltres\">" # Les filtres vidéo
		docMontagVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/VideoMontageVideo\">" # Le montage vidéo
		docTitDsUneVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/VideoTitrageDansVideo\">" # Titrage dans une vidéo
		docGestionAVCHD = "<p align=\"center\"><a href=\"http://ekdm.wordpress.com/2009/11/09/gestion-de-lavchd-dans-ekd\">" # Gestion de l'AVCHD dans EKD
		docGestProjetDsEkd = "<p align=\"center\"><a href=\"http://ekdm.wordpress.com/2010/01/02/la-gestion-de-projet-dans-ekd\">" # La gestion de projet dans EKD
		docStructFormFichPourEkd = "<p align=\"center\"><a href=\"http://ekdm.wordpress.com/2010/01/18/structure-du-format-de-fichier-pour-ekd\">" # Structure du format de fichier pour EKD
		PlanchContactImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ImagesPlancheContact\">" # Planche-contact pour les images
		docInfosImgPhoto = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ImagesInformation\">" # Informations pour les images/photos
		docAjoutTxtSurImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/AjoutElements\">" # Ajout d’éléments (texte/images)
		docCompositing = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ImageComposite\">" # Faire du compositing avec EKD
		docRenomImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/RenommageImages\">" # Le renommage d’images dans EKD
		docPourLeWeb = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/PourLeWebLinux\">" # Pour le web (gif animé et morcellement/découpe) 
		docTransitionsImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/Transitions\">" # Transitions pour les images
		docMasqueAlpha3D = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/MasqueAlpha3D\">" # Masque alpha/3D (chroma key) pour les images
		docFiltresImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/FiltresImage\">" # Les différents filtres image pour EKD
		docLecturImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/LectureImage\">" # Visionner des images sous EKD
		docLecturVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/LectureVideo\">" # Lecture de vidéos dans EKD
		docInstallSourcEkdLinux = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/INSTekd/Linux\">" # Installation des sources d’EKD sous Linux
		docKitWindows = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/KitWindows\">" # Kit EKD Windows à partir du dépôt SVN
		docContructExeEkd = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ConstructExeWindows\">" # Construire un exécutable d’EKD pour Windows
	# Liens en anglais (ou dans toute autre langue que francophone)
	else:
		docGen = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/Linux\">" # Documentation générale
		docBarrOutConfEkd = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/MenuEtBarreOutilsEnglish\">" # Barre d'outils et configuration d'EKD
		docTraitVidParExemp = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/TraitementVideoPresentationEnglish\">" # Le traitement vidéo par l’exemple
		docTraitImgParExemp = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/TraitementImagePresentationEnglish\">" # Le traitement des images par l’exemple
		docFiltresVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/VideoFiltresEnglish\">" # Les filtres vidéo
		docMontagVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/VideoMontageVideo\">" # Le montage vidéo
		docTitDsUneVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/VideoTitrageDansVideo\">" # Titrage dans une vidéo
		docGestionAVCHD = "<p align=\"center\"><a href=\"http://ekdm.wordpress.com/2009/11/09/gestion-de-lavchd-dans-ekd\">" # Gestion de l'AVCHD dans EKD
		docGestProjetDsEkd = "<p align=\"center\"><a href=\"http://ekdm.wordpress.com/2010/01/02/la-gestion-de-projet-dans-ekd\">" # La gestion de projet dans EKD
		docStructFormFichPourEkd = "<p align=\"center\"><a href=\"http://ekdm.wordpress.com/2010/01/18/structure-du-format-de-fichier-pour-ekd\">" # Structure du format de fichier pour EKD
		PlanchContactImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ImagesPlancheContactEnglish\">" # Planche-contact pour les images
		docInfosImgPhoto = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ImagesInformationEnglish\">" # Informations pour les images/photos
		docAjoutTxtSurImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/AjoutElementsEnglish\">" # Ajout d’éléments (texte/images)
		docCompositing = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ImageCompositeEnglish\">" # Faire du compositing avec EKD
		docRenomImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/RenommageImagesEnglish\">" # Le renommage d’images dans EKD
		docPourLeWeb = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/PourLeWebLinuxEnglish\">" # Pour le web (gif animé et morcellement/découpe) 
		docTransitionsImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/TransitionsEnglish\">" # Transitions pour les images
		docMasqueAlpha3D = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/MasqueAlpha3DEnglish\">" # Masque alpha/3D (chroma key) pour les images
		docFiltresImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/FiltresImage\">" # Les différents filtres image pour EKD
		docLecturImg = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/LectureImageEnglish\">" # Visionner des images sous EKD
		docLecturVid = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/LectureVideoEnglish\">" # Lecture de vidéos dans EKD
		docInstallSourcEkdLinux = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/INSTekd/LinuxEnglish\">" # Installation des sources d’EKD sous Linux
		docKitWindows = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/KitWindowsEnglish\">" # Kit EKD Windows à partir du dépôt SVN
		docContructExeEkd = "<p align=\"center\"><a href=\"http://ekd.tuxfamily.org/index.php/Documents/ConstructExeWindowsEnglish\">" # Construire un exécutable d’EKD pour Windows
	
        if PYQT_VERSION_STR >= "4.1.0":
            textBrowser = QTextBrowser()

            textBrowser.setHtml(
                "<h3><center>" + _(u"Documentation et didacticiels") + "</center></h3>"
                + "<br>" 
		+ docGen + _(u"Documentation générale") +"</a></p>"
                + docBarrOutConfEkd + _(u"Barre d'outils et configuration d'EKD") +"</a></p>"
                + docTraitVidParExemp + _(u"Le traitement vidéo par l’exemple") +"</a></p>"
                + docTraitImgParExemp + _(u"Le traitement des images par l’exemple") +"</a></p>"
                + docFiltresVid + _(u"Les filtres vidéo") +"</a></p>"
                + docMontagVid + _(u"Le montage vidéo") +"</a></p>"
                + docTitDsUneVid + _(u"Titrage dans une vidéo") +"</a></p>"
                + docGestionAVCHD + _(u"Gestion de l'AVCHD dans EKD") +"</a></p>"
                + docGestProjetDsEkd + _(u"La gestion de projet dans EKD") +"</a></p>"
                + docStructFormFichPourEkd + _(u"Structure du format de fichier pour EKD") +"</a></p>"
                + PlanchContactImg + _(u"Planche-contact pour les images") +"</a></p>"
                + docInfosImgPhoto + _(u"Informations pour les images/photos") +"</a></p>"
                + docAjoutTxtSurImg + _(u"Ajout d’éléments (texte/images)") +"</a></p>"
                + docCompositing + _(u"Faire du compositing avec EKD") +"</a></p>"
                + docRenomImg + _(u"Le renommage d’images dans EKD") +"</a></p>"
		+ docPourLeWeb + _(u"Pour le web (gif animé et morcellement/découpe)") +"</a></p>"
                + docTransitionsImg + _(u"Transitions pour les images") +"</a></p>"
                + docMasqueAlpha3D + _(u"Masque alpha/3D (chroma key) pour les images") +"</a></p>"
                + docFiltresImg + _(u"Les différents filtres image pour EKD") +"</a></p>"
                + docLecturImg + _(u"Visionner des images sous EKD") +"</a></p>"
                + docLecturVid + _(u"Lecture de vidéos dans EKD") +"</a></p>"
                + docInstallSourcEkdLinux + _(u"Installation des sources d’EKD sous Linux") +"</a></p>"
                + docKitWindows + _(u"Kit EKD Windows à partir du dépôt SVN") +"</a></p>"
                + docContructExeEkd + _(u"Construire un exécutable d’EKD pour Windows") +"</a></p>"
                )
            textBrowser.setOpenExternalLinks(True)

        else:
            # On fait au plus simple sous debian etch
            textBrowser = QWidget()
            vboxLiens = QVBoxLayout(textBrowser)
            lab = EkdLabel(_(u"Documentation générale"),"http://ekd.tuxfamily.org/index.php/Documents/Linux")
            vboxLiens.addWidget(lab, 0, Qt.AlignTop)
	#################################################################################################################

        #=== 3ème onglet ===#
        self.fram_3=QFrame()
        vboxFram_3=QVBoxLayout(self.fram_3)

        v_box_fram_3=QVBoxLayout()

        label_texte=QLabel(_(u"<b><center>EKD est placé sous licence libre <font color=red>GNU GPL version 3</font>: Vous pouvez l’utiliser, le copier, le modifier (l’équipe de développement souhaiterait tout de même avoir accès au code modifié) et le diffuser librement.</center></b>"))
        label_texte.setWordWrap(1)

        vboxFram_3.addWidget(label_texte)

        # Ajout de l'image logo GPL v3 au milieu de la fenêtre
        objImg = QImage("Icones"+os.sep+"gplv3-127x51.png") # objet-image
        label = QLabel()
        label.setPixmap(QPixmap.fromImage(objImg)) # on inclut l'image dans le QLabel
        label.setAlignment(Qt.AlignCenter) # centrage de l'image

        texte_1=_(u"<h2><b>Termes de l'utilisation d'EKD par la GPL version 3</b></h2>")

        fh = QFile('menu_et_toolbar'+os.sep+'copyright_ekd_gplv3_mise_en_forme.txt')
        fh.open(QIODevice.ReadOnly)
        stream = QTextStream(fh)
        stream.setCodec("UTF-8")
        texte_2 = unicode(stream.readLine())
        fh.close()

        texte_3="<h2><b>GNU General Public License Version 3, 29 June 2007</b></h2>"

        fh = QFile('menu_et_toolbar'+os.sep+'gplv3_mise_en_forme.txt')
        fh.open(QIODevice.ReadOnly)
        stream = QTextStream(fh)
        stream.setCodec("UTF-8")
        texte_4 = unicode(stream.readLine())
        fh.close()

        zoneTexte = QTextEdit(texte_1+texte_2+texte_3+texte_4)
        zoneTexte.setReadOnly(True)
        #zoneTexte.setMinimumHeight(408)
	zoneTexte.setMinimumHeight(204)

        vboxFram_3.addLayout(v_box_fram_3)
        vboxFram_3.addWidget(label)
        vboxFram_3.addWidget(zoneTexte)
        vboxFram_3.addStretch()

        self.index_1=self.tabwidget.addTab(self.fram_2, _(u'Développement et graphisme'))
        self.index_2=self.tabwidget.addTab(textBrowser, _(u'Documentation'))
        self.index_3=self.tabwidget.addTab(self.fram_3, _(u'Licence'))

        boutonFermer = QPushButton(_(u"Revenir"))
        boutonFermer.setIcon(QIcon("Icones"+os.sep+"revenir.png"))
        self.connect(boutonFermer, SIGNAL('clicked()'), SLOT('close()'))

        vbox_aide.addWidget(self.tabwidget)
        vbox_aide.addWidget(boutonFermer)
        self.setLayout(vbox_aide)



class DialogQuitter(QDialog):
    '''
    Boite de dialogue de fermeture de ekd
      sauverConfCase : Case à cocher de sauvegarde des paramètres
    '''
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.setWindowTitle(_(u'Message'))

        vbox = QVBoxLayout(self)
        questionLabel = QLabel(_(u"Voulez-vous sauver les nouveaux paramètres de configuration?"))
        self.sauverConfCase = QCheckBox(_(u"Ne plus poser la question à chaque fois"))
        if PYQT_VERSION_STR >= "4.1.0":
            buttonBox = QDialogButtonBox(QDialogButtonBox.Yes|QDialogButtonBox.No)
            boutonOui = buttonBox.button(QDialogButtonBox.Yes)
            boutonNon = buttonBox.button(QDialogButtonBox.No)
        else:
            buttonBox = QWidget()
            vboxButtonBox = QHBoxLayout(buttonBox)
            vboxButtonBox.addStretch()
            boutonOui = QPushButton(_(u'&Oui'))
            boutonNon = QPushButton(_(u'&Non'))
            vboxButtonBox.addWidget(boutonOui)
            vboxButtonBox.addWidget(boutonNon)
        messagebox_info = QPixmap("Icones"+os.sep+"messagebox_info.png")
        icone = QLabel()
        icone.setPixmap(messagebox_info)
        hboxButton = QHBoxLayout()
        hboxButton.addStretch()
        hboxButton.addWidget(buttonBox)
        vboxText = QVBoxLayout()
        vboxText.addWidget(questionLabel)
        vboxText.addWidget(self.sauverConfCase)
        hboxIconText = QHBoxLayout()
        hboxIconText.addWidget(icone)
        hboxIconText.addStretch(0)
        hboxIconText.addLayout(vboxText)
        vbox.addLayout(hboxIconText)
        vbox.addStretch(0)
        vbox.addLayout(hboxButton)
        boutonOui.setFocus()
        self.connect(boutonOui,SIGNAL("clicked()"),self.accept)
        self.connect(boutonNon,SIGNAL("clicked()"),self.reject)


class Gui_EKD(QMainWindow):
    '''
    # -----------------------------------------
    # Classe principale . Base de l'interface .
    # -----------------------------------------
    '''

    ## On ajoute la taille minimale du split gauche
    minMenuSize = 250

    def __init__(self):
        QMainWindow.__init__(self)

        # -----------------------------------------------------
        # Parametres Generaux de la fenetre Principale (début)
        # -----------------------------------------------------

        # Titre de la fenetre
        self.setWindowTitle('EnKoDeur-Mixeur')

        # Icone de EKD
        self.setWindowIcon(QIcon('Icones' + os.sep + 'logo_ekd.png'))
        # Dimension mini de la fenêtre. La taille est différente sous windows et sous Linux.
        # Pour windows uniquement
        #if os.name == 'nt':
        #    self.setMinimumSize(QSize(1010, 584))
        # Pour Linux et MacOSX
        #elif os.name in ['posix', 'mac']:
        #    # Dimension mini de la fenêtre
        #    self.setMinimumSize(QSize(800, 550))
        #######################################################################################################
        self.setMinimumSize(QSize(800, 480))

        #=== chargement et lecture du fichier de configuration
        #   (plutôt méthode linux) ===#
        home = unicode(QDir.homePath())
        # Variable pour la fonction tamponEKD
        self.tableauCourant = None
        # Pour windows uniquement
        if os.name == 'nt':
            # Pour windows. Les fichiers de config sont mis directement dans l'arborescence d'EKD.
            # L'arborescence d'EKD sous windows sera:
            # windows\\...\\... tous les reps. et fichiers spécifiques à la version windows
            self.configdir = 'windows'
            pathConfig = 'windows'
            ##############################################################################
            if not QDir(pathConfig).exists():
                #print " pathConfig didn't exist, creating - " + pathConfig
                EkdPrint(u" pathConfig didn't exist, creating - %s" % pathConfig)
                os.makedirs(os.getcwd + os.sep + pathConfig)
            else:
                #print " pathConfig exists, not creating - " + pathConfig
                EkdPrint(u" pathConfig exists, not creating - %s" % pathConfig)

        # Pour Linux et MacOSX
        elif os.name in ['posix', 'mac']:
            # appelé depuis une fonction
            self.configdir = '.config' + os.sep +'ekd'
            pathConfig = home + os.sep + self.configdir
            if not QDir(pathConfig).exists():
                #print " pathConfig didn't exist, creating - " + pathConfig
                EkdPrint(u" pathConfig didn't exist, creating - %s" % pathConfig)
                if not QDir(home).mkpath(pathConfig):
                    #print " Création : echec"
                    EkdPrint(u" Création : echec")
            else:
                #print " pathConfig exists, not creating - " + pathConfig
                EkdPrint(u" pathConfig exists, not creating - %s" % pathConfig)
        #######################################################################################################

        pathname = os.path.dirname (sys.argv[0])
        refdir = os.path.abspath (pathname) + os.sep + "videoporama" + os.sep + "template" + os.sep
        ### Vérification que les fichiers de config videoporama existent, sinon les copier
        ### à partir du répertoire template.
        if (not os.path.exists(pathConfig + os.sep + "template_data.idv")) :
            reffile=open(refdir + os.sep +u"template_data.idv","r")
            destfile=open(pathConfig + os.sep + u"template_data.idv","w")
            destfile.write(reffile.read())
            destfile.close()
        #######################################################################################################

        # Import de données de configurations au départ du fichier xml
        self.msgDiapo = 0
        ### Activation ou non de l'onglet Audio si Sox est installé ou non
        self.audioSox = True
        #####################################################################################
        # Vérification des possibilités de Sox en encodage
        #####################################################################################
        self.soxSuppFormat = []
        if  not verif[0] and "sox" in verif[1] :
            self.audioSox = False
            self.suitInit()
        else :
            usableFormat = [u"wav",u"ogg",u"flac",u"mp3",u"mp2"]
            checkSox = checkSoxEncoding(usableFormat,self)
            self.connect(checkSox,SIGNAL("checkSox"),self.composeListeFormat)
            checkSox.run()

    ### Lorsque la verification des possibilites de Sox seront terminees, les fonctions
    ### d'initialisation se poursuivent.
    def composeListeFormat(self,formatValide) :
        for format in formatValide :
            if format[1] :
                self.soxSuppFormat.append(format[0])
        self.suitInit()

    def suitInit(self) :
        # Suite des fonctions d'initialisation.
        # ---------------------------------------------------------
        # Menu principal - Barre d'outils
        # ---------------------------------------------------------

        #=== Actions générales ===#

        #################################################################################
        if PYQT_VERSION_STR >= "4.1.0": raccourcis = QKeySequence.Save
        else : raccourcis = "Ctrl + S"
        sauverProjetAction = self.createAction(_(u'&Sauver le projet'), slot=self.sauver,
            shortcut=raccourcis, icon='Icones'+os.sep+'icone_save_128.png',tip=_(u"Sauver le projet"),signal="triggered()")

        if PYQT_VERSION_STR >= "4.1.0": raccourcis = QKeySequence.Open
        else : raccourcis = "Ctrl + O"
        chargerProjetAction = self.createAction(_(u'&Charger le projet'), slot=self.charger,
            shortcut=raccourcis, icon='Icones'+os.sep+'icone_load_128.png',tip=_(u"Charger le projet"),signal="triggered()")

        if PYQT_VERSION_STR >= "4.1.0": raccourcis = QKeySequence.Close
        else : raccourcis = "Ctrl + Q"
        quitterAction = self.createAction(_(u'&Quitter'), slot=self.close,
            shortcut=raccourcis, icon='Icones'+os.sep+'icone_quit_128.png',tip=_(u"Fermer l'application"),signal="triggered()")
        #######################################################################################################

        self.barreOutilsAction = self.createAction(_(u"&Barre d'outils"), slot=self.barreOutils,
            tip=_(u"Afficher" + os.sep + "Masquer la barre d'outils"), checkable=True, signal="triggered()")

        if PYQT_VERSION_STR >= "4.1.0": raccourcis = QKeySequence.HelpContents
        else: raccourcis = "F1"
        aboutAction = self.createAction(_(u"&A propos d'EKD"), slot=self.info_aide,
            shortcut=raccourcis, icon='Icones' + os.sep + 'icone_info_128.png',
            tip=_(u"Afficher les contributeurs, les liens vers documentation et la licence de EKD"), signal="triggered()")

        mplayerAction = self.createAction(_(u"&Lecteur vidéo"), slot=self.mplayerAction,
            icon='Icones' + os.sep + 'icone_visionner_128.png',tip=_(u"Lancer un lecteur vidéo"), signal="triggered()")
            
        tamponEKDAction = self.createAction(_(u"&Tampon"), slot=self.tamponEKDAction,
            icon='Icones' + os.sep + 'database.png', tip=_(u"Réserve de fichiers sources"), signal="triggered()")
        """
        # Inutilisé, ces action sont gérées dans la configuration générale
        self.dialogSauvAction = self.createAction(_(u"B&oite de dialogue de sauvegarde"), checkable=True, slot=self.dialogSauv, signal="triggered()", tip=_(u"Afficher la boite de dialogue de sauvegarde des paramètres de configuration à la fermeture de EKD"))

        self.splitAction = self.createAction(_(u"&Conserver les positions relatives des menus verticaux et des cadres (split)"), checkable=True, slot=self.splitPosition, signal="triggered()", tip=_(u"Risqué! Cette action prendra effet au prochain démarrage de EKD. Les positions seront enregistrées à la fermeture si vous le décidez."))

        self.purgeConfigAction = self.createAction(_(u"&Réinitialiser les paramètres de configuration"), checkable=True, slot=self.purgeConfig, signal="triggered()", tip=_(u"Purge des fichiers de configurations. Cette action prendra effet au prochain démarrage de EKD"))
        """
        ### Ajout de la boite de dialogue de configuration
        self.ConfigAction = self.createAction(_(u"&Configuration générale"), slot=self.launchConfig, signal="triggered()", tip=_(u"Configuration des différents composants de Ekd"))

        # Uniquement pour Linux et MacOSX
        if os.name == 'posix':
            # Sortie vidéo de mplayer
            groupVideoOutput = QActionGroup(self)
            defautvoAction = self.createAction(_(u"&défaut"), checkable=True,
                slot=lambda a, b='':self.videoOutput(a, b),
                tip=_(u"Sortie vidéo définie dans les fichiers de configuration de mplayer"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(defautvoAction)
            xmgaAction = self.createAction("x&mga", checkable=True,
                slot=lambda a, b='xmga':self.videoOutput(a, b),
                tip=_(u"Matrox G200/G4x0/G550 overlay in X11 window (using /dev/mga_vid)"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(xmgaAction)
            xvAction = self.createAction("&xv", checkable=True,
                slot=lambda a, b='xv':self.videoOutput(a, b), tip=_(u" X11/Xv"), signal="toggled(bool)")
            groupVideoOutput.addAction(xvAction)
            x11Action = self.createAction("x&11", checkable=True,
                slot=lambda a, b='x11':self.videoOutput(a, b), tip=_(u"X11 (XImage/Shm)"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(x11Action)
            glAction = self.createAction("&gl", checkable=True,
                slot=lambda a, b='gl':self.videoOutput(a, b), tip=_(u"X11 (OpenGL)"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(glAction)
            gl2Action = self.createAction("gl&2", checkable=True,
                slot=lambda a, b='gl2':self.videoOutput(a, b),
                tip=_(u"X11 (OpenGl) - multiple textures version"), signal="toggled(bool)")
            groupVideoOutput.addAction(gl2Action)
            dxr3Action = self.createAction("dx&r3", checkable=True,
                slot=lambda a, b='dxr3':self.videoOutput(a, b), tip=_(u"DXR3/H+ video out"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(dxr3Action)
            xvidixAction = self.createAction("xv&idix", checkable=True,
                slot=lambda a, b='xvidix':self.videoOutput(a, b), tip=_(u"X11 (VIDIX)"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(xvidixAction)
            vidixAction = self.createAction("v&idix", checkable=True,
                slot=lambda a, b='vidix':self.videoOutput(a, b), tip=_(u"VIDIX (VIDeo Interface for *niX)"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(vidixAction)
            cvidixAction = self.createAction("cv&idix", checkable=True,
                slot=lambda a, b='cvidix':self.videoOutput(a, b), tip=_(u"Generic and platform independent VIDIX frontend"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(cvidixAction)
            vesaAction = self.createAction("vesa", checkable=True,
                slot=lambda a, b='vesa':self.videoOutput(a, b), tip=_(u"Very general video output driver that should work on any VESA VBE 2.0 compatible card"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(vesaAction)
            svgaAction = self.createAction("svga", checkable=True,
                slot=lambda a, b='svga':self.videoOutput(a, b), tip=_(u"Play video using the SVGA library"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(svgaAction)
            fbdevAction = self.createAction("fbdev", checkable=True,
                slot=lambda a, b='fbdev':self.videoOutput(a, b), tip=_(u"Uses the kernel framebuffer to play video"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(fbdevAction)
            dfbmgaAction = self.createAction("dfbmga", checkable=True,
                slot=lambda a, b='dfbmga':self.videoOutput(a, b), tip=_(u"Matrox G400/:G450/:G550 specific video output driver that uses the DirectFB library"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(dfbmgaAction)
            s3fbAction = self.createAction("s3fb", checkable=True,
                slot=lambda a, b='s3fb':self.videoOutput(a, b), tip=_(u"S3 Virge specific video output driver"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(s3fbAction)
            wiiAction = self.createAction("wii", checkable=True,
                slot=lambda a, b='wii':self.videoOutput(a, b), tip=_(u"Nintendo Wii/GameCube specific video output driver"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(wiiAction)
            a3dfxAction = self.createAction("3dfx", checkable=True,
                slot=lambda a, b='3dfx':self.videoOutput(a, b), tip=_(u"3dfx-specific video output driver that directly uses the hardware on top of X11"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(a3dfxAction)
            #############################################
            xvmcAction = self.createAction("xvm&c", checkable=True,
                slot=lambda a, b='xvmc':self.videoOutput(a, b), tip=_(u"XVideo Motion Conpensation"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(xvmcAction)

        # Uniquement pour MacOSX
        if os.name == 'mac':
            # Sortie vidéo de mplayer
            groupVideoOutput = QActionGroup(self)
            defautvoAction = self.createAction(_(u"&défaut"), checkable=True,
                slot=lambda a, b='':self.videoOutput(a, b),
                tip=_(u"Sortie vidéo définie dans les fichiers de configuration de mplayer"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(defautvoAction)
            quartzAction = self.createAction("quartz", checkable=True,
                slot=lambda a, b='quartz':self.videoOutput(a, b),
                tip=_(u"Mac OS X Quartz video output driver"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(quartzAction)
            macosxAction = self.createAction("macosx", checkable=True,
                slot=lambda a, b='macosx':self.videoOutput(a, b),
                tip=_(u"Mac OS X CoreVideo video output driver"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(macosxAction)
            vesaAction = self.createAction("vesa", checkable=True,
                slot=lambda a, b='vesa':self.videoOutput(a, b), tip=_(u"Very general video output driver that should work on any VESA VBE 2.0 compatible card"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(vesaAction)
            svgaAction = self.createAction("svga", checkable=True,
                slot=lambda a, b='svga':self.videoOutput(a, b), tip=_(u"Play video using the SVGA library"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(svgaAction)
            glAction = self.createAction("&gl", checkable=True,
                slot=lambda a, b='gl':self.videoOutput(a, b), tip=_(u"OpenGL 1"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(glAction)
            gl2Action = self.createAction("gl&2", checkable=True,
                slot=lambda a, b='gl2':self.videoOutput(a, b),
                tip=_(u"OpenGl 2 - multiple textures version"), signal="toggled(bool)")
            groupVideoOutput.addAction(gl2Action)

        # Uniquement pour Windows
        if os.name == 'nt':
            # Sortie vidéo de mplayer
            groupVideoOutput = QActionGroup(self)
            defautvoAction = self.createAction(_(u"&défaut"), checkable=True,
                slot=lambda a, b='':self.videoOutput(a, b),
                tip=_(u"Sortie vidéo définie dans les fichiers de configuration de mplayer"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(defautvoAction)
            directxAction = self.createAction("&directx", checkable=True,
                slot=lambda a, b='directx':self.videoOutput(a, b),
                tip=_(u"DirectX"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(directxAction)
            glAction = self.createAction("&gl", checkable=True,
                slot=lambda a, b='gl':self.videoOutput(a, b), tip=_(u"OpenGL 1"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(glAction)
            gl2Action = self.createAction("gl&2", checkable=True,
                slot=lambda a, b='gl2':self.videoOutput(a, b),
                tip=_(u"OpenGl 2 - multiple textures version"), signal="toggled(bool)")
            groupVideoOutput.addAction(gl2Action)
            ##################################
            winvidixAction = self.createAction("winvidix", checkable=True,
                slot=lambda a, b='winvidix':self.videoOutput(a, b),
                tip=_(u"Windows frontend for VIDIX"), signal="toggled(bool)")
            groupVideoOutput.addAction(winvidixAction)
            direct3dAction = self.createAction("direct3d", checkable=True,
                slot=lambda a, b='direct3d':self.videoOutput(a, b),
                tip=_(u"Video output driver that uses the Direct3D interface (useful for Vista)"), signal="toggled(bool)")
            groupVideoOutput.addAction(direct3dAction)
            dfbmgaAction = self.createAction("dfbmga", checkable=True,
                slot=lambda a, b='dfbmga':self.videoOutput(a, b), tip=_(u"Matrox G400/:G450/:G550 specific video output driver that uses the DirectFB library"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(dfbmgaAction)
            vesaAction = self.createAction("vesa", checkable=True,
                slot=lambda a, b='vesa':self.videoOutput(a, b), tip=_(u"Very general video output driver that should work on any VESA VBE 2.0 compatible card"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(vesaAction)
            svgaAction = self.createAction("svga", checkable=True,
                slot=lambda a, b='svga':self.videoOutput(a, b), tip=_(u"Play video using the SVGA library"),
                signal="toggled(bool)")
            groupVideoOutput.addAction(svgaAction)
            #############################################

        settings = QSettings()

        # Uniquement pour Linux et MacOSX
        if os.name == 'posix':
            vo = settings.value("vo", QVariant('')).toString()
            if vo == '':
                defautvoAction.setChecked(True)
            elif vo == 'xmga':
                xmgaAction.setChecked(True)
            elif vo == 'xv':
                xvAction.setChecked(True)
            elif vo == 'x11':
                x11Action.setChecked(True)
            elif vo == 'gl':
                glAction.setChecked(True)
            elif vo == 'gl2':
                gl2Action.setChecked(True)
            elif vo == 'dxr3':
                gl2Action.setChecked(True)
            elif vo == 'xvidix':
                gl2Action.setChecked(True)
            ###################################
            elif vo == 'vidix':
                vidixAction.setChecked(True)
            elif vo == 'cvidix':
                cvidixAction.setChecked(True)
            elif vo == 'vesa':
                vesaAction.setChecked(True)
            elif vo == 'svga':
                svgaAction.setChecked(True)
            elif vo == 'fbdev':
                fbdevAction.setChecked(True)
            elif vo == 'dfbmga':
                dfbmgaAction.setChecked(True)
            elif vo == 's3fb':
                s3fbAction.setChecked(True)
            elif vo == 'wii':
                wiiAction.setChecked(True)
            elif vo == '3dfx':
                a3dfxAction.setChecked(True)
            #############################################
            elif vo == 'xvmc':
                xvmcAction.setChecked(True)

        # Uniquement pour MacOSX
        if os.name == 'mac':
            vo = settings.value("vo", QVariant('')).toString()
            if vo == '':
                defautvoAction.setChecked(True)
            elif vo == 'quartz':
                quartzAction.setChecked(True)
            elif vo == 'macosx':
                macosxAction.setChecked(True)
            elif vo == 'vesa':
                vesaAction.setChecked(True)
            elif vo == 'svga':
                svgaAction.setChecked(True)
            elif vo == 'gl':
                glAction.setChecked(True)
            elif vo == 'gl2':
                gl2Action.setChecked(True)

        # Uniquement pour Windows
        if os.name == 'nt':
            vo = settings.value("vo", QVariant('')).toString()
            if vo == '':
                defautvoAction.setChecked(True)
            elif vo == 'directx':
                directxAction.setChecked(True)
            elif vo == 'gl':
                glAction.setChecked(True)
            elif vo == 'gl2':
                gl2Action.setChecked(True)
            ###################################
            elif vo == 'winvidix':
                winvidixAction.setChecked(True)
            elif vo == 'direct3d':
                direct3dAction.setChecked(True)
            elif vo == 'dfbmga':
                dfbmgaAction.setChecked(True)
            elif vo == 'vesa':
                vesaAction.setChecked(True)
            elif vo == 'svga':
                svgaAction.setChecked(True)
            #############################################

        #=== Menus ===#
        # Menu Fichier ==========================================
        menuFichier=self.menuBar().addMenu(_(u'&Fichier'))
        self.addActions(menuFichier, (chargerProjetAction, sauverProjetAction, None, quitterAction,))


        # Menu Outils =================================
        menuOutils=self.menuBar().addMenu(_(u'O&utils'))
        self.addActions(menuOutils, (mplayerAction, tamponEKDAction,))
        
        # Menu Configuration ==========================================
        self.menuConfig=self.menuBar().addMenu(_(u'&Configuration'))
        self.addActions(self.menuConfig, (self.ConfigAction, self.barreOutilsAction
                          ))
        ### N'est plus nécessaire, géré dans la configuration Générale
        #self.connect(self.menuConfig,SIGNAL("aboutToShow()"),self.fctMenuConfig)


        # Uniquement pour Linux
        if os.name == 'posix':
            menuMplayer = self.menuConfig.addMenu(_(u"&Sortie vidéo de mplayer"))
            self.addActions(menuMplayer, (defautvoAction, xmgaAction, xvAction, x11Action, glAction, gl2Action, dxr3Action, xvidixAction, vidixAction, cvidixAction, vesaAction, svgaAction, fbdevAction, dfbmgaAction, s3fbAction, s3fbAction, wiiAction, a3dfxAction, xvmcAction))

        # Uniquement MacOSX
        if os.name == 'mac':
            menuMplayer = self.menuConfig.addMenu(_(u"&Sortie vidéo de mplayer"))
            self.addActions(menuMplayer, (defautvoAction, quartzAction, macosxAction, vesaAction, svgaAction, glAction, gl2Action))

        # Uniquement pour Windows
        if os.name == 'nt':
            menuMplayer = self.menuConfig.addMenu(_(u"&Sortie vidéo de mplayer"))
            self.addActions(menuMplayer, (defautvoAction, directxAction, glAction, gl2Action, winvidixAction, direct3dAction, dfbmgaAction, vesaAction, svgaAction))

        # Menu Aide ==========================================
        menu=self.menuBar().addMenu(_(u'&Infos'))
        self.addActions(menu, (aboutAction,))

        #=== Barre d'outils ===#
        self.toolBar = self.addToolBar(_(u"&Barre d'outils"))
        self.toolBar.setObjectName("BarreOutils") # obligatoire pour le déplacement
        self.toolBar.setIconSize(QSize(16,16))
        self.toolBar.hide()

        self.toolBar.addAction(quitterAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(tamponEKDAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(mplayerAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(aboutAction)
        self.toolBar.addSeparator()

        # Dictionnaire pour ne pas avoir à changer la fonction connectée à chaque
        # modif du nom d'un item . Une valeur (et non pas une clé) de notre
        # dictionnaire est unique. Elle est différente du texte de l'item pour
        # éviter les pièges et pour pouvoir donner des noms identiques à certains
        # items au besoin .
        self.itemDict = {}

        # ---------------------------------------------------------
        # TamponEKD
        # ---------------------------------------------------------
        self.tamponEKD = EkdTamponIn(self)

        # ---------------------------------------------------------
        # Onglets
        # ---------------------------------------------------------
        tabWidget=QTabWidget()

        largeurEcran = QDesktopWidget().screenGeometry().height()
        # Sous Qt4.0 pas moyen de paramètrer la taille des icônes pour les en-têtes d'onglet.
        # Elles sont beaucoup trop petite -> on préfère le texte seul (on préfère aussi le texte
        # pour les petites écrans)
        if largeurEcran < 800 or PYQT_VERSION_STR < "4.1.0": petitEcran = 1
        else:
            petitEcran = 0
            tabWidget.setIconSize(QSize(36,36))

        self.connect(tabWidget,SIGNAL('currentChanged(int)'),self.changeOnglet)

        # onglet Animation ============================
        # DICO - clé: référence du split; valeur: paramètres de configuration
        #        Permet de faire le lien entre la stack de widget et l'arbre de menu
        self.dicoSplit = {}
        self.animSplitter = QSplitter(Qt.Horizontal)
        self.dicoSplit[self.animSplitter] = "AnimSplitter"

        # Liste de hbox
        # Rq: les self de cette partie (sauf pour le dictionnaire) sont nécessaires
        # à l'activation les liens hypertextes du cadre d'accueil "Montage Vidéo"
        self.treeWidgetAnimation=QTreeWidget()

        self.animSplitter.addWidget(self.treeWidgetAnimation)
        self.treeWidgetAnimation.headerItem().setText(0, _(u"Vidéo"))
        self.treeWidgetAnimation.setMinimumWidth(Gui_EKD.minMenuSize)
        ###################################################################################################################

        # ajout de la liste et des widgets associés dans hbox
        self.stacked_onglet_animation=QStackedWidget()

        # widget principal de la page d'accueil contenant le logo ekd
        widget_img_accueil = self.widgetOngletAccueil("Icones" + os.sep + "logo_ekd.png")
        # Drapeau pour savoir éventuellement afficher l'image d'accueil propre à l'onglet
        self.clicInitialAnim = 1
        # widget principal de la page d'accueil animation
        imageAccueilAnim = self.widgetOngletAccueil("Icones" + os.sep + "icone_video_256.png")

        # page d'accueil de ekd
        self.stacked_page_accueil=self.stacked_onglet_animation.addWidget(widget_img_accueil)
        # page d'accueil de animation
        self.imageAccueilAnim=self.stacked_onglet_animation.addWidget(imageAccueilAnim)
        # Animation >> Encodage
        (self.itemTree_Encodage, self.stacked_animation_encodage)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_Encodage(self), _(u"Transcodage"),\
                                    QIcon("Icones" + os.sep + "db_update.png"), self.itemDict)

        # Animation >> Encodage >> Général
        (self.itemTree_Encodage_General, self.stacked_animation_encodage_general)=self.createMenu(self.itemTree_Encodage, self.stacked_onglet_animation,\
                                    Animation_Encodage_General(), _(u"Général"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> Encodage >> Pour le web
        (self.itemTree_Encodage_Web, self.stacked_animation_encodage_web)=self.createMenu(self.itemTree_Encodage, self.stacked_onglet_animation,\
                                    AnimationEncodageWeb(), _(u"Pour le web"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> Encodage >> Haute Définition
        (self.itemTree_Encodage_HD, self.stacked_animation_encodage_hd)=self.createMenu(self.itemTree_Encodage, self.stacked_onglet_animation,\
                                    AnimationEncodageHD(), _(u"Haute Définition"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> Encodage >> AVCHD
        # Utilisation de la vérification de la version de ffmpeg
        if verif[8] :
            (self.itemTree_Encodage_AVCHD, self.stacked_animation_encodage_avchd)=self.createMenu(self.itemTree_Encodage, self.stacked_onglet_animation,\
                                    AnimationEncodageAVCHD(), _(u"Gestion AVCHD"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> filtres vidéos
        (trash, self.stacked_animation_filtesVideos)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_FiltresVideos(), _(u"Filtres"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> montage vidéo
        (self.itemTree_MontagVideo, self.stacked_animation_MontagVideo)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_MontagVideo(self), _(u"Montage vidéo"),\
                                    QIcon("Icones" + os.sep + "db_update.png"), self.itemDict)

        # Animation >> montage vidéo >> video seulement
        (self.itemTree_SVideo, self.stacked_animation_MontagVideoVidSeul)=self.createMenu(self.itemTree_MontagVideo, self.stacked_onglet_animation,\
                                    Animation_MontagVideoVidSeul(self.statusBar()), _(u"Vidéo seulement"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)
        # Animation >> montage vidéo >> video + audio
        (self.itemTree_SVideoAudio, self.stacked_animation_MontagVideoVidPlusAudio)=self.createMenu(self.itemTree_MontagVideo, self.stacked_onglet_animation,\
                                    Animation_MontagVideoVidPlusAudio(self.statusBar(), self), _(u"Vidéo + audio"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> montage vidéo >> decouper une video
        (self.itemTree_SDecouperVideo, self.stacked_animation_MontagVideoDecoupUneVideo)=self.createMenu(self.itemTree_MontagVideo, self.stacked_onglet_animation,\
                                    Animation_MontagVideoDecoupUneVideo(self.statusBar()), _(u"Découpage d'une vidéo"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> separer video et audio
        (trash, self.stacked_animation_SeparVideoEtAudio)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_SeparVideoEtAudio(), _(u"Séparation audio-vidéo"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> convertir des images en animation
        (trash, self.stacked_animation_ConvertirImgEnAnim)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_ConvertirImgEnAnim(self.statusBar(), self.frameGeometry), _(u"Conversion d'images en vidéo"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> convertir une animation en images
        (trash, self.stacked_animation_ConvertirUneAnimEnImg)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_ConvertirUneAnimEnImg(self.statusBar(), self.frameGeometry), _(u"Conversion d'une vidéo en images"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> reglages divers
        (trash, self.stacked_animation_ReglagesDivers)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_ReglagesDivers(), _(u"Nombre d'images par seconde"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Animation >> conversion une vidéo en 16/9 ou 4/3
        (trash, self.stacked_animation_ConvertirAnimEn_16_9_Ou_4_3)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_ConvertirAnimEn_16_9_Ou_4_3(self.statusBar()), _(u"Convertir une vidéo en 16/9 ou 4/3"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        ### Menu Diaporama d'images en vidéo (Videoporama) ###
        # Animation >> Diaporama d'images en vidéo
        (trash, self.stacked_animation_Videoporama)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Videoporama_Main(verif,self), _(u"Diaporama d'images en vidéo"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

	### Ajouté le 05/09/10 pour la gestion des Tags vidéo ##############################################################
        # Animation >> Tags vidéo
        (trash, self.stacked_animation_TagsVideo)=self.createMenu(self.treeWidgetAnimation, self.stacked_onglet_animation,\
                                    Animation_TagsVideo(), _(u"Tags vidéo"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)
	####################################################################################################################

        # connecteur de la liste
        self.connect(self.treeWidgetAnimation,SIGNAL("itemClicked(QTreeWidgetItem *,int)"),self.liste_animation)


        self.animSplitter.addWidget(self.stacked_onglet_animation)

        # ajout du widget contenant la boite dans l'onglet Animation
        i = tabWidget.addTab(self.animSplitter, '')
        txt = _(u"Vidéo")
        tabWidget.setTabToolTip(i, txt)
        if not petitEcran:
            tabWidget.setTabIcon(i, QIcon("Icones" + os.sep + "icone_video_128.png"))
        else: tabWidget.setTabText(i, txt)

        # onglet Image ================================
        self.imageSplitter = QSplitter(Qt.Horizontal)
        self.dicoSplit[self.imageSplitter] = "ImageSplitter"

        # liste de hbox
        self.treeWidgetDiversImage=QTreeWidget()
        self.imageSplitter.addWidget(self.treeWidgetDiversImage)
        self.treeWidgetDiversImage.headerItem().setText(0,_(u"Image"))
        self.treeWidgetDiversImage.setMinimumWidth(Gui_EKD.minMenuSize)

        # widget principal de la page d'accueil
        widget_img_accueil = self.widgetOngletAccueil("Icones" + os.sep + "icone_images_256.png")

        # ajout de la liste et des widgets associés dans hbox
        self.stacked_onglet_image=QStackedWidget(self)
        # page d'accueil
        self.stacked_onglet_image.addWidget(widget_img_accueil)
        # Image >> Divers
        (self.treeWidgetImagesDivers, self.stacked_image_divers)=self.createMenu(self.treeWidgetDiversImage, self.stacked_onglet_image,\
                                    Image_Divers(self), _(u"Divers"),\
                                    QIcon("Icones" + os.sep + "db_update.png"), self.itemDict)

        # Image >> Divers >> Planche-contact
        (self.itemTree_PlContact, self.stacked_image_divers_PlContact)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_PlContact(self.statusBar(), self.frameGeometry), _(u"Planche-contact"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Information
        (self.itemTree_Information, self.stacked_image_divers_Information)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_Info(self.frameGeometry), _(u"Information"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Changer format
        (self.itemTree_ChangFormat, self.stacked_image_divers_ChangFormat)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_ChangFormat(self.statusBar(), self.frameGeometry), _(u"Changement de format"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Redimensionner
        (self.itemTree_Redimens, self.stacked_image_divers_Redimens)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_Redimensionner(self.statusBar(), self.frameGeometry), _(u"Redimension"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Texte sur images
        if PYQT_VERSION_STR >= "4.1.0":
            (self.itemTree_TxtSurImg, self.stacked_image_divers_TxtSurImg)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_TxtSurImg(self.statusBar(), self.frameGeometry), _(u"Ajout d'éléments"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Compositing
        (self.itemTree_ImgComposit, self.stacked_image_divers_Compositing)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_Compositing(self.statusBar(), self.frameGeometry), _(u"Image composite"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Renommer images
        (self.itemTree_RenomImg, self.stacked_image_divers_RenomImg)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_RenomImg(self.frameGeometry), _(u"Renommage d'images"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Pour le web
        (self.itemTree_PourLeWeb, self.stacked_image_divers_PourLeWeb)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_PourLeWeb(self.statusBar(), self.frameGeometry), _(u"Pour le web"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Divers >> Multiplication d'images
        (self.itemTree_MultiplicImg, self.stacked_image_divers_MultiplicImg)=self.createMenu(self.treeWidgetImagesDivers, self.stacked_onglet_image,\
                                    Image_Divers_MultiplicImg(self.statusBar(), self.frameGeometry), _(u"Multiplication d'images"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Transitions
        (self.itemTree_Transition, self.stacked_image_transitions)=self.createMenu(self.treeWidgetDiversImage, self.stacked_onglet_image,\
                                    Image_Transitions(self), _(u"Transitions"),\
                                    QIcon("Icones" + os.sep + "db_update.png"), self.itemDict)

        # Image >> Transitions >> Fondu enchaîné
        (self.itemTree_FonduEnchaine, self.stacked_image_transitions_fondEnch)=self.createMenu(self.itemTree_Transition, self.stacked_onglet_image,\
                                    Image_Transitions_FondEnch(self.statusBar(), self.frameGeometry), _(u"Fondu enchaîné"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Transitions >> Spirale
        (self.itemTree_Spirale, self.stacked_image_transitions_Spirale)=self.createMenu(self.itemTree_Transition, self.stacked_onglet_image,\
                                    Image_Transitions_Spirale(self.statusBar(), self.frameGeometry), _(u"Spirale"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

        # Image >> Masque alpha/3D
        (self.itemTree_ImageMasqueAlpha3D, self.stacked_image_masque_alpha_3d)=self.createMenu(self.treeWidgetDiversImage, self.stacked_onglet_image,\
                                    Image_MasqueAlpha3D(self.statusBar(), self.frameGeometry), _(u"Masque alpha/3D"),\
                                    QIcon("Icones" + os.sep + "db_update.png"), self.itemDict)

        # Image >> Filtres image
        (self.itemTree_FiltresImage, self.stacked_image_filtres_image)=self.createMenu(self.treeWidgetDiversImage, self.stacked_onglet_image,\
                                    Image_FiltresImage(self.statusBar(), self.frameGeometry), _(u"Filtres"),\
                                    QIcon("Icones" + os.sep + "db_update.png"), self.itemDict)


        # connecteur de la liste
        self.connect(self.treeWidgetDiversImage,SIGNAL("itemClicked(QTreeWidgetItem *,int)"),self.liste_image)

        self.imageSplitter.addWidget(self.stacked_onglet_image)

        # ajout du widget contenant la boite dans l'onglet Image
        i = tabWidget.addTab(self.imageSplitter, '')
        txt = _(u"Image")
        tabWidget.setTabToolTip(i, txt)
        if not petitEcran:
            tabWidget.setTabIcon(i, QIcon("Icones" + os.sep + "icone_images_128.png"))
        else: tabWidget.setTabText(i, txt)

        if self.audioSox :
            self.sonSplitter = QSplitter(Qt.Horizontal)
            self.dicoSplit[self.sonSplitter] = "SonSplitter"

            # liste de hbox
            self.treeWidgetSon=QTreeWidget()
            self.sonSplitter.addWidget(self.treeWidgetSon)
            self.treeWidgetSon.headerItem().setText(0, _(u"Musique-Son"))
            self.treeWidgetSon.setMinimumWidth(Gui_EKD.minMenuSize)

            # ajout de la liste et des widgets associés dans hbox
            self.stacked_onglet_musique_son=QStackedWidget()

            # page d'accueil
            # widget principal de la page d'accueil
            widget_img_accueil = self.widgetOngletAccueil("Icones" + os.sep + "icone_sons_256.png")
            self.stacked_onglet_musique_son.addWidget(widget_img_accueil)

            # Musique-Son >> Encodage
            (self.itemTree_MusiqueSonEcodage, self.stacked_musique_son_encodage)=self.createMenu(self.treeWidgetSon, self.stacked_onglet_musique_son,\
                                    MusiqueSon_Encodage(self), _(u"Transcodage audio"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

            # Musique-Son >> Join multiple file
            (self.itemTree_MusiqueSonEcodage, self.stacked_musique_son_join_sound)=self.createMenu(self.treeWidgetSon, self.stacked_onglet_musique_son,\
                                    MusiqueSon_Join(self), _(u"Joindre plusieurs fichiers audio"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

            # Musique-Son >> Découpe fichier son 
            (self.itemTree_MusiqueSonEcodage, self.stacked_musique_son_decoupe)=self.createMenu(self.treeWidgetSon, self.stacked_onglet_musique_son,\
                                    MusiqueSon_decoupe(self), _(u"Découpe dans un fichier audio"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

            # Musique-Son >> Normalize fichier audio 
            (self.itemTree_MusiqueSonEcodage, self.stacked_musique_son_decoupe)=self.createMenu(self.treeWidgetSon, self.stacked_onglet_musique_son,\
                                    MusiqueSon_normalize(self), _(u"Normaliser et convertir un fichier audio"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)

            self.connect(self.treeWidgetSon,SIGNAL("itemClicked(QTreeWidgetItem *,int)"),self.liste_musique_son)

            self.sonSplitter.addWidget(self.stacked_onglet_musique_son)

            # ajout du widget contenant la boite dans l'onglet Musique_Son
            i = tabWidget.addTab(self.sonSplitter, '')
            txt = _(u"Musique-Son")
            tabWidget.setTabToolTip(i, txt)
            if not petitEcran:
                tabWidget.setTabIcon(i, QIcon("Icones" + os.sep + "icone_sons_128.png"))
            else: tabWidget.setTabText(i, txt)

        # onglet Lecture ==============================
        self.lectureSplitter = QSplitter(Qt.Horizontal)
        self.dicoSplit[self.lectureSplitter] = "LectureSplitter"

        splitLect=QSplitter(Qt.Vertical)

        # liste des entrées de menu de splitLect
        self.treeWidgetLecture=QTreeWidget()
        self.treeWidgetLecture.headerItem().setText(0, _(u"Lecture"))
        ## Ajouté le 3/07/2009 : On s'assure que la taille du treeWidget est suffisante
        self.treeWidgetLecture.setMinimumWidth(Gui_EKD.minMenuSize)

        splitLect.addWidget(self.treeWidgetLecture)


        self.stackedVisio = QStackedWidget()

        splitLect.addWidget(self.stackedVisio)

        self.lectureSplitter.addWidget(splitLect)

        # connecteur de la liste
        self.connect(self.treeWidgetLecture,SIGNAL("itemClicked(QTreeWidgetItem *,int)"),self.liste_lecture)

        # ajout de la liste et des widgets associés dans hbox
        self.stacked_onglet_lecture=QStackedWidget()

        # page d'accueil
        # widget principal de la page d'accueil
        widget_img_accueil = self.widgetOngletAccueil("Icones" + os.sep + "icone_visionner_256.png")
        self.stacked_onglet_lecture.addWidget(widget_img_accueil)
        # Lecture >> Visionner des images
        self.lecture_VisionImage = Lecture_VisionImage(self.statusBar(), True, False)

        (self.itemTree_LectureVisionImage, self.stacked_lecture_vision_image)=self.createMenu(self.treeWidgetLecture, self.stacked_onglet_lecture,\
                                    self.lecture_VisionImage, _(u"Lecture d'images"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)
        self.indexStacked_visioImg = self.stackedVisio.addWidget(self.lecture_VisionImage.getFolder())

        # Lecture >> Visionner des vidéos
        self.lecture_VisionVideo = Lecture_VisionVideo(self.statusBar())
        (self.itemTree_LectureVisionVideo, self.stacked_lecture_vision_video)=self.createMenu(self.treeWidgetLecture, self.stacked_onglet_lecture,\
                                    self.lecture_VisionVideo, _(u"Lecture de vidéos"),\
                                    QIcon("Icones" + os.sep + "database.png"), self.itemDict)
        self.indexStacked_visioVideo = self.stackedVisio.addWidget(self.lecture_VisionVideo.getFolder())

        self.lectureSplitter.addWidget(self.stacked_onglet_lecture)

        # ajout du widget contenant la boite dans l'onglet Lecture
        i = tabWidget.addTab(self.lectureSplitter, '')
        txt = _(u"Lecture")
        tabWidget.setTabToolTip(i, txt)
        if not petitEcran:
            tabWidget.setTabIcon(i, QIcon("Icones" + os.sep + "icone_visionner_128.png"))
        else: tabWidget.setTabText(i, txt)


        # onglet Mode Séquentiel ===========================

        # En construction
        if len(sys.argv)==2 and sys.argv[1]=="sequentiel":
            # widget de base du dernier onglet
            sequentiel = Sequentiel(self)

            # ajout du widget contenant la boite dans l'onglet Séquentiel
            i = tabWidget.addTab(sequentiel, '')
            tabWidget.setTabToolTip(i, _(u"Conversions séquentielles"))
            if not petitEcran:
                tabWidget.setTabIcon(i, QIcon("Icones" + os.sep + "icone_sequenciel_128.png"))
            else: tabWidget.setTabText(i, _(u"Sequentiel"))


        # -----------------
        # Barre des tâches
        # -----------------
        self.statusBar().showMessage(u'Prêt', 5000)

        # affichage des onglets au centre de la fenêtre
        self.setCentralWidget(tabWidget)

        # A pour effet d'assurer une taille minimale
        # aux QTreeWidget lors de la 1ère ouverture de ekd
        self.animSplitter.setStretchFactor(0, 4)
        self.animSplitter.setStretchFactor(1, 4)
        self.imageSplitter.setStretchFactor(0, 3)
        self.imageSplitter.setStretchFactor(1, 4)
        if self.audioSox :
            self.sonSplitter.setStretchFactor(0, 1)
            self.sonSplitter.setStretchFactor(1, 3)
            self.lectureSplitter.setStretchFactor(0, 1)
            self.lectureSplitter.setStretchFactor(1, 1)

        #--------------------------------------------------
        # Paramètres généraux de la fenêtre (suite et fin)
        #--------------------------------------------------
        # Paramètres contenus dans ~/.config/ekd/ekd.conf sous linux
        display_mode = EkdConfig.get("general", 'display_mode')
        ## display_mode peut-être : auto ou une résolution type WxH
        if ( display_mode == "auto"):
            size = settings.value("MainWindow/Size", QVariant(QSize(800, 484))).toSize()
        else:
            width, height = display_mode.split("x")
            size = QSize(int(width), int(height))
            settings.setValue("MainWindow/Size", QVariant(size))
        self.resize(size)
        position = settings.value("MainWindow/Position",QVariant(QPoint(0, 0))).toPoint()
        self.move(position)
        self.restoreState(settings.value("MainWindow/State").toByteArray())
        splitList = [self.animSplitter, self.imageSplitter, self.sonSplitter,self.lectureSplitter ]
        if int(EkdConfig.get("general", 'charger_split')):
            for split, optionConfig in self.dicoSplit.items():
                splitSetting = settings.value(optionConfig).toByteArray()
                split.restoreState(splitSetting)


    def info_aide(self):
        """ Chargement de la classe de la boîte de dialogue pour afficher
        l'aide en ligne (affichée dans le browser web par défaut du système),
        les infos de développement et la licence """
        aide_info = Aide_Info(self)
        aide_info.show()

    def fctMenuConfig(self):
        "L'état des cases à cocher du menu configuration sont générés lors du clic sur le menu"
        self.barreOutilsAction.setChecked(self.toolBar.isVisible())
        actif = int(EkdConfig.get("general", 'boite_de_dialogue_de_fermeture'))
        #
        self.dialogSauvAction.setChecked(actif)
        actif = int(EkdConfig.get("general", 'charger_split'))
        #
        self.splitAction.setChecked(actif)

    def barreOutils(self):
        "Affichage/masquage de la barre d'outils"
        self.toolBar.setVisible(not self.toolBar.isVisible())


    def mplayerAction(self):
        "Widget mplayer"
        try:
            repEntree = EkdConfig.get('general','video_input_path').decode("UTF8")
        except IndexError, e: #ConfigParser.NoOptionError, e:
            repEntree = None

        mplayer = Mplayer([], (600, 600*3/4),
            (Mplayer.REVENIR,Mplayer.PRECEDENT_SUIVANT,Mplayer.CURSEUR_A_PART,Mplayer.PARCOURIR),
            cheminParcourir=repEntree, parent=self)

        mplayer.show()

    def tamponEKDAction(self) :
        "Affiche le tamponEKD"
        self.tamponEKD.show()

    def changerComboQA(self):
        """ Affichage de l'index du combo """
        #print self.comboConfigQA.currentIndex()
        EkdPrint(u"%s" % self.comboConfigQA.currentIndex())


    def quoiAfficher(self):
        """ L'utilisateur fait le choix de ce qui doit être visible
        entre le menu, la barre des taches et les deux en même temps """
        if self.comboConfigQA.currentIndex()==0:
            # Uniquement la barre des taches sera visible
            self.menuBar().hide()
            self.toolBar.show()
        elif self.comboConfigQA.currentIndex()==1:
            # Uniquement le menu sera visible
            self.menuBar().show()
            self.toolBar.hide()
        elif self.comboConfigQA.currentIndex()==2:
            # Les deux seront affichés
            self.menuBar().show()
            self.toolBar.show()
    # --------------------------------------------------------------------------


    def dialogSauv(self):
        "Faire apparaître/disparaître la boite de dialogue de sauvegarde en sortie"
        if self.dialogSauvAction.isChecked():
            EkdConfig.set("general", 'boite_de_dialogue_de_fermeture', '1')
        else:
            EkdConfig.set("general", 'boite_de_dialogue_de_fermeture', '0')


    def splitPosition(self):
        "Charger les paramètres de position relatives des menus/cadres (QSplitter)"
        if self.splitAction.isChecked():
            if QMessageBox.critical(self, _(u"Alerte"), _(u"Vous souhaitez activer le chargement des dernières positions relatives des menus verticaux et des cadres (split). Sous certaines configurations, le chargement des positions relatives des menus verticaux/cadres de chaque onglet fait apparaître des onglets vides au démarrage de EKD. Dans ce cas nous vous conseillons de ne plus charger les positions relatives des menus verticaux/cadres des onglets voire de réinitialiser les paramètres de configuration (voir les entrées du menu «Configuration» appropriées).\n\nVoulez-vous quand-même confimer votre choix?"), QMessageBox.Yes, QMessageBox.No)==QMessageBox.Yes:
                EkdConfig.set("general", 'charger_split', '1')
            else: self.splitAction.setChecked(False)
        else:
            EkdConfig.get("general", 'charger_split', '0')


    def purgeConfig(self):
        "Purge des fichiers de configuration"
        #if self.purgeConfigAction.isChecked():
        if int(EkdConfig.get("general", 'effacer_config')):
            #if QMessageBox.warning(self, _(u"Alerte"), _(u"Vous souhaitez remettre les paramètres de configuration à leurs valeurs initiales. Cela purgera vos fichiers de configurations.\nSi vous faites cela pour résoudre un problème d'onglets vides, nous vous conseillons ensuite de redémarrer EKD.\n\nVoulez-vous quand-même confirmer votre choix?"), QMessageBox.Yes, QMessageBox.No)==QMessageBox.Yes:
            if QMessageBox.warning(self, _(u"Alerte"),
                    _(u"Vous souhaitez remettre les paramètres de configuration à leurs valeurs initiales. Cela purgera vos fichiers de configurations.\n Si vous faites cela pour résoudre un problème d'onglets vides, nous vous conseillons ensuite de redémarrer EKD.\n\nVoulez-vous quand-même confirmer votre choix?"),
                    QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                EkdConfig.purge()


    def closeEvent(self, event):
        "actions à effectuer au moment de quitter"

        def sauvChangements():
            EkdConfig.save()
            #

            settings = QSettings()
            settings.setValue("MainWindow/Size", QVariant(self.size()))
            settings.setValue("MainWindow/Position",QVariant(self.pos()))
            settings.setValue("MainWindow/State",QVariant(self.saveState()))
            for split, optionConfig in self.dicoSplit.items():
                settings.setValue(optionConfig, QVariant(split.saveState()))

        if int(EkdConfig.get("general", 'boite_de_dialogue_de_fermeture')):
            dialog = DialogQuitter(self)
            if dialog.exec_():
                sauverConf =  not dialog.sauverConfCase.isChecked()
                EkdConfig.set("general", 'boite_de_dialogue_de_fermeture',
                                                        str(int(sauverConf)))
                EkdConfig.set("general", 'sauvegarder_parametres', str(Qt.Checked) )
                sauvChangements()
            else:
                sauverConf =  not dialog.sauverConfCase.isChecked()
                EkdConfig.set("general", 'boite_de_dialogue_de_fermeture',
                                                str(int(sauverConf)))
                EkdConfig.set("general", 'sauvegarder_parametres', str(Qt.Unchecked))
                self.purgeConfig()

        elif int(EkdConfig.get("general", 'sauvegarder_parametres')):
            sauvChangements()
            self.purgeConfig()
        event.accept()


    def changeOnglet(self,i):
        """ Effacer les données de la barre des tâches lorsque l'on change
            d'onglet
        """
        if i==1 and self.clicInitialAnim:
            self.stacked_onglet_animation.setCurrentIndex(self.imageAccueilAnim)
            self.clicInitialAnim = 0
        self.statusBar().clearMessage()


    def createAction(self, text, slot=None, shortcut=None, icon=None,
            tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


    def addActions(self, target, actions):
        '''
        Ajoute une liste d'actions à un menu :
        target doit être un menu
        actions une liste de QActions
        ex : addActions(menu, (Ouvrir, Enregistrer, None, Quitter))
          crée le menu suivant :
          menu
          |- Ouvrir
          |- Enregistrer
          |-------------
          |- Quitter
        '''
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    def videoOutput(self, vrai, vo):
        "Enregistre la valeur de l'option '-vo' de mplayer dans un fichier de configuration"
        if vrai:
            settings = QSettings()
            settings.setValue("vo", QVariant(vo))


    def widgetOngletAccueil(self, cheminImg):
        "Widget principal de la page d'accueil d'un onglet"
        widget_img_accueil=QWidget()
        # fond gris
        if PYQT_VERSION_STR >= "4.1.0":
            widget_img_accueil.setStyleSheet("QWidget { background-color: %s }"\
                % QColor(140,140,140).name())
        else:
            widget_img_accueil.setAutoFillBackground(True)
            widget_img_accueil.setPalette(QPalette(QColor(140,140,140)))
        hbox_label=QHBoxLayout(widget_img_accueil)
        objImg = QPixmap(cheminImg) # objet-image
        label = QLabel()
        label.setPixmap(objImg) # on inclut l'image dans le QLabel
        hbox_label.addWidget(label, 0, Qt.AlignHCenter)
        return widget_img_accueil


    def naviguerImages(self, item):
        "Ouvrir le contenu d'un répertoire (images)"
        self.listViewVisioImg.setRootIndex(item)
        modele = item.model()
        rep=QDir(modele.filePath(item)).absolutePath()
        #print rep
        EkdPrint(u"%s" % rep)
        self.statusBar().showMessage(rep)


    def naviguerVideos(self, item):
        "Ouvrir le contenu d'un répertoire (vidéos)"
        self.listViewVisioVideo.setRootIndex(item)
        modele = item.model()
        rep=QDir(modele.filePath(item)).absolutePath()
        self.statusBar().showMessage(rep)


    def liste_animation(self, item):
        '''Les éléments de la liste de menu à gauche modifient le contenu de la boite de droite de l'onglet animation'''
        # item renvoie la référence de l'objet QTreeWidgetItem.
        # Effacer les données de la barre des tâches lorsque l'on change d'entrée de l'arborescence
        self.statusBar().clearMessage()
        self.clicInitialAnim = 0
        self.stacked_onglet_animation.setCurrentIndex(self.itemDict[item])
        self.tableauCourant = self.stacked_onglet_animation.currentWidget()
        # temporaire !!!
        z=16
        if verif[8] :
            z = 17
        if self.itemDict[item] == z :
            if verif[2] == 1 or verif[6] and self.msgDiapo == 0 :
                QMessageBox.critical(None,_(u"Vérification des possibilités de FFMPEG"), verif[3].join("\n")+"\n"+verif[7].join("\n"))
                self.msgDiapo = 1



    def liste_image(self, item):
        """Les éléments de la liste 2 modifient le contenu de la boite de droite de l'onglet images"""
        # item renvoie la référence de l'objet QTreeWidgetItem.
        self.statusBar().clearMessage()
        self.stacked_onglet_image.setCurrentIndex(self.itemDict[item])
        self.tableauCourant = self.stacked_onglet_image.currentWidget()


    def liste_musique_son(self, item):
        """Les éléments de la liste 1 modifient le contenu de la boite de droite de l'onglet musique_son"""
        # item renvoie la référence de l'objet QTreeWidgetItem.
        self.statusBar().clearMessage()
        self.stacked_onglet_musique_son.setCurrentIndex(self.itemDict[item])
        self.tableauCourant = self.stacked_onglet_musique_son.currentWidget()


    def liste_lecture(self, item):
        """Les éléments de la liste 1 modifient le contenu de la boite de droite de l'onglet lecture"""
        # item renvoie la référence de l'objet QTreeWidgetItem.
        if item == self.itemTree_LectureVisionImage:
            try :
                self.stackedVisio.setCurrentIndex(self.indexStacked_visioImg)
            except :
                None
        elif item == self.itemTree_LectureVisionVideo:
            try :
                self.stackedVisio.setCurrentIndex(self.indexStacked_visioVideo)
            except :
                None
        self.stacked_onglet_lecture.setCurrentIndex(self.itemDict[item])
        self.tableauCourant = self.stacked_onglet_lecture.currentWidget()



    def createMenu(self, menuTree, widgetStack, Widget, name, icone, dico, expanded=True):
        '''
        Permet de faciliter la création des menu et des widget dans la stack
        Le lien entre les deux est fait par cette fonction
        Prend en paramètre:
          * menuTree : racine du menu
          * widgetStack : stack d'objet à lier au menu
          * Widget : Objet à ajouter à la stack
          * name : nom du menu
          * icone : icone du menu
          * dico : tableau contenant les index des objets dans le menu et dans la stack (les deux sont identiques)
          * expended : est-ce que le menu doit être étendu ?
        '''

        itemTree=QTreeWidgetItem(menuTree)
        itemTree.setText(0,_(name))
        itemTree.setIcon(0,QIcon(icone))

        dico[itemTree]=widgetStack.addWidget(Widget)
        itemTree.setExpanded(expanded)

        return (itemTree, dico[itemTree])
    ###################################################################################################################

    def sauver(self):
        """
        Sauve la configuration dans un fichier particulier
        """
        projectFile = EkdSaveDialog(self, path=None, suffix=('.ekd'), title=u"Sauver").getFile()
        #print "Sauvegarde de la configuration : ", projectFile
        EkdPrint(u"Sauvegarde de la configuration : %s" % projectFile)
        if projectFile :
            idvProject = projectFile[:-4]+u".idv"
            try : self.stacked_onglet_animation.widget(self.stacked_animation_Videoporama).saveprj(idvProject)
            except : 
		#print "Echec sauvegarde du diaporama"
		EkdPrint(u"Echec sauvegarde du diaporama")
            count = self.stacked_onglet_animation.count()
            for objet in range(count):
                try :
                    self.stacked_onglet_animation.widget(objet).save()
                except :
                    #print "Debug : Sauvegarde impossible de l'objet : ", objet
                    EkdPrint(u"Debug : Sauvegarde impossible de l'objet : %s" % objet)

                    count = self.stacked_onglet_animation.count()

            count = self.stacked_onglet_image.count()
            for objet in range(count):
                try :
                    self.stacked_onglet_image.widget(objet).save()
                except :
                    #print "Debug : Sauvegarde impossible de l'objet : ", objet
                    EkdPrint(u"Debug : Sauvegarde impossible de l'objet : %s" % objet)

            count = self.stacked_onglet_musique_son.count()
            for objet in range(count):
                try :
                    self.stacked_onglet_musique_son.widget(objet).save()
                except :
                    #print "Debug : Sauvegarde impossible de l'objet : ", objet
                    EkdPrint(u"Debug : Sauvegarde impossible de l'objet : %s" % objet)

            EkdConfig.save(configfile=projectFile)

    def charger(self):
        """
        Charge la configuration à partir d'un fichier particulier
        """
        projectFile = EkdOpenDialog(self, path=None, suffix=('.ekd'), title=u"Charger").getFile()
        #print "Chargement de la configuration : ", projectFile
        EkdPrint(u"Chargement de la configuration : %s" % projectFile)
        if projectFile :
            idvProject = projectFile[:-4]+u".idv"
            try :
                self.stacked_onglet_animation.widget(self.stacked_animation_Videoporama).empty()
                self.stacked_onglet_animation.widget(self.stacked_animation_Videoporama).loadprj(idvProject)
            except : 
		#print "Pas de fichier idv à charger ou projet idv sans fichiers images"
		EkdPrint(u"Pas de fichier idv à charger ou projet idv sans fichiers images")
            EkdConfig.init(projectFile)
            # Reload all objet
            count = self.stacked_onglet_animation.count()
            for objet in range(count):
                try :
                    self.stacked_onglet_animation.widget(objet).load()
                except :
                    #print "Debug : Chargement impossible de l'objet : ", objet
                    EkdPrint(u"Debug : Chargement impossible de l'objet : %s" % objet)

            count = self.stacked_onglet_image.count()
            for objet in range(count):
                try :
                    self.stacked_onglet_image.widget(objet).load()
                except :
                    #print "Debug : Chargement impossible de l'objet : ", objet
                    EkdPrint(u"Debug : Chargement impossible de l'objet : %s" % objet)

            count = self.stacked_onglet_musique_son.count()
            for objet in range(count):
                try :
                    self.stacked_onglet_musique_son.widget(objet).load()
                except :
                    #print "Debug : Chargement impossible de l'objet : ", objet
                    EkdPrint(u"Debug : Chargement impossible de l'objet : %s" % objet)

    def launchConfig(self):
        """
        Lance l'outil de configuration à partir du menu configuration
        """
        self.configBox = EkdConfigBox(parent=self)
        self.configBox.show()


if __name__ == "__main__":

    import __builtin__
    from functools import partial
    
    '''
    # ENLEVE CAR PROBLEMES DE DROITS QUAN EKD INTALLE SUR LE DD
    # Elimination du fichier ekd_result_terminal.txt s'il existe
    # (fichier ds lequel sont ecrits les retours des renseignements
    # délivrés par la classe EkdPrint)
    if os.path.isfile('ekd_result_terminal.txt') is True: os.remove('ekd_result_terminal.txt')
    '''
    
    # Traduction des boites de dialogue Qt
    locale = unicode(QLocale.system().name()) # ex: fr_FR
    #print "\n\n", locale
    EkdPrint(u"\n\n%s" % locale)

    # Sélection du répertoire de traduction
    localeDir = os.path.join(os.getcwd(), "locale")
    if not os.path.exists(localeDir):
        localeDir = os.path.join(os.path.dirname(sys.argv[0]), "locale")

    app = QApplication(sys.argv)

    qtTranslator = QTranslator()
    try: symboleLangue = locale.split('_')[0] # ex: fr
    except ValueError, e:
        #print e
        EkdPrint(u"%s" % e)
        symboleLangue = "inconnu"
    if qtTranslator.load("qt_"+locale, os.path.join(localeDir, 'translations')):
        app.installTranslator(qtTranslator)
    elif qtTranslator.load("qt_"+symboleLangue, os.path.join(localeDir, 'translations')):
        app.installTranslator(qtTranslator)
    else:
        #print "Pas de fichier", "qt_"+locale+'.qm', "ou", "qt_"+symboleLangue+'.qm', "détecté"
        EkdPrint(u"Pas de fichier qt_%s.qm ou qt_%s.qm détecté" % (locale, symboleLangue))

    qtTranslator2 = QTranslator()
    if qtTranslator2.load("videoporama_"+symboleLangue,os.path.join(localeDir, 'translations')) :
        app.installTranslator(qtTranslator2)
        #print "Langue videoporama OK"
        EkdPrint(u"Langue videoporama OK")
    elif qtTranslator.load("videoporama_"+locale,os.path.join(localeDir, 'translations')) :
        app.installTranslator(qtTranslator2)
        #print "Langue videoporama OK"
        EkdPrint(u"Langue videoporama OK")

    # Traduction de l'interface courante (ex. locale/es_ES/LC_MESSAGES/ekd.po pour l'espagnol)
    try:
        traduction = gettext.translation('ekd', localeDir, languages=[locale])
    except IOError, e:
        traduction = gettext.translation('ekd', localeDir, languages=[symboleLangue], fallback=True)
    # Traduction de l'aide (ex. locale/es_ES/LC_MESSAGES/ekdDoc.po pour l'espagnol)
    try:
        traductionDoc = gettext.translation('ekdDoc', localeDir, languages=[locale])
    except IOError:
        traductionDoc = gettext.translation('ekdDoc', localeDir, languages=[symboleLangue], fallback=True)

    __builtin__.__dict__['_'] = partial(traduction.ugettext)
    __builtin__.__dict__['tr'] = partial(traductionDoc.ugettext)

    verif = verifAppliManquante()


    # Nom du répertoire et du début du fichier de configuration
    app.setOrganizationName("ekd")
    app.setApplicationName("ekd")
    app.setOrganizationDomain("ekd.tuxfamily.org")

    txt1 = _(u"Les applications suivantes n'ont pas été détectées:")
    txt2 = _(u"EKD ne sera pas pleinement fonctionnel (s'il démarre...) \n")

    depMsg = u""

    if not verif[0]:
        depMsg = txt1 + u" " + verif[1] + u"\n"

    if verif[6] or not verif[0] : #or verif[2] :
        QMessageBox.critical(None,_(u"Vérification des dépendances de EKD"),depMsg + verif[7].join("\n" + txt2))


    # -------------------------------------------------------------
    # Import des modules contenus dans des fichiers separes
    # -------------------------------------------------------------
    
    # Uniquement pour windows
    if os.name == 'nt':
	#
        # Nombre de dependances pour EKD
	nbre_dep = 11
        # Chemin du script d'installation sous windows
	chem_inst_win = os.getcwd()+os.sep+'windows'+os.sep+'chemin_install_applis'
        # Si le répertoire ... windows\chemin_install_applis n'existe pas, il faut le creer
        if os.path.exists(chem_inst_win) is False: os.mkdir(chem_inst_win)
	# Liste des fichiers contenus ds le repertoire
	liste_chem_inst_win = os.listdir(chem_inst_win)
	# Si un fichier est vide (c'est à dire d'un poids 0 octet) il est signale ds cette liste
	l_lect_dep_non_inst = [[dep_no] for dep_no in liste_chem_inst_win if os.path.getsize(chem_inst_win+os.sep+dep_no) == 0]
	# 
	if len(liste_chem_inst_win) < nbre_dep or len(l_lect_dep_non_inst) > 0:
		# DEPENDANCES (vérif de la présence de ttes les applis pour EKD) -----
		from dependances_windows.chemin_install_applis import DetectionRegistreApplis
		# Appel de la classe
		detect = DetectionRegistreApplis()
		toto # Erreur provoquee pour pouvoir fermer --> NameError: name 'toto' is not defined
		# Seule solution trouvee pour l'instant pour que EKD ne s'execute pas a la fin de
		# l'install par la nouvelle fenetre d'install d'EKD sous windows


        # GESTION DES LANGUES ------------------------------------------------
        from gestion_des_langues_en_local import GestionLangues
        # Appel de la classe
        glang = GestionLangues()
    
    # Outils Communs --------------------------------------------------------------------------
    from gui_modules_common.EkdWidgets import EkdLabel, EkdSaveDialog, EkdOpenDialog, EkdConfigBox
    from moteur_modules_common.EkdConfig import EkdConfig


    # ANIMATION --------------

    from gui_modules_animation.animation_encodage import Animation_Encodage
    # + ---------------------------
    from gui_modules_animation.animation_encodage_general import Animation_Encodage_General
    from gui_modules_animation.animation_encodage_web import AnimationEncodageWeb
    from gui_modules_animation.animation_encodage_hd import AnimationEncodageHD
    if verif[8] :
        from gui_modules_animation.animation_encodage_avchd import AnimationEncodageAVCHD
    # + ---------------------------
    from gui_modules_animation.animation_filtres_video import Animation_FiltresVideos
    from gui_modules_animation.animation_montage_video import Animation_MontagVideo
    # + ---------------------------
    from gui_modules_animation.animation_montage_video_vid_seul import Animation_MontagVideoVidSeul
    from gui_modules_animation.animation_montage_video_vid_plus_audio import Animation_MontagVideoVidPlusAudio
    from gui_modules_animation.animation_montage_video_decoup_une_vid import Animation_MontagVideoDecoupUneVideo
    # -----------------------------
    from gui_modules_animation.animation_separer_video_et_audio import Animation_SeparVideoEtAudio
    from gui_modules_animation.animation_conv_img_en_anim import Animation_ConvertirImgEnAnim
    from gui_modules_animation.animation_conv_anim_en_img import Animation_ConvertirUneAnimEnImg
    from gui_modules_animation.animation_reglag_divers import Animation_ReglagesDivers
    from gui_modules_animation.animation_conv_vid_16_9_ou_4_3 import Animation_ConvertirAnimEn_16_9_Ou_4_3
    # -----------------------------
    from videoporama.videoporama_main import *
    # -----------------------------
    ### Ajouté le 05/09/10 pour la gestion des Tags vidéo #####################
    from gui_modules_animation.animation_tags_video import Animation_TagsVideo
    ###########################################################################

    # IMAGE ------------------
    # divers
    from gui_modules_image.divers.image_divers import Image_Divers
    # + ---------------------------
    from gui_modules_image.divers.image_divers_chang_format import Image_Divers_ChangFormat
    from gui_modules_image.divers.image_divers_compositing import Image_Divers_Compositing
    from gui_modules_image.divers.image_divers_info import Image_Divers_Info
    from gui_modules_image.divers.image_divers_pl_contact import Image_Divers_PlContact
    from gui_modules_image.divers.image_divers_pour_le_web import Image_Divers_PourLeWeb
    from gui_modules_image.divers.image_divers_redimensionner import Image_Divers_Redimensionner
    from gui_modules_image.divers.image_divers_renom_img import Image_Divers_RenomImg
    from gui_modules_image.divers.image_divers_multiplic_img import Image_Divers_MultiplicImg
    # Pas de module texte sur items sous debian etch
    if PYQT_VERSION_STR >= "4.1.0":
        from gui_modules_image.divers.image_divers_txt_sur_img import Image_Divers_TxtSurImg
    # -----------------------------
    # transitions
    from gui_modules_image.transitions.image_transitions import Image_Transitions
    # + ---------------------------
    from gui_modules_image.transitions.image_transitions_fond_ench import Image_Transitions_FondEnch
    from gui_modules_image.transitions.image_transitions_spirale import Image_Transitions_Spirale
    # -----------------------------
    # masque_alpha_3d
    from gui_modules_image.masque_alpha_3d.image_masque_alpha_3d import Image_MasqueAlpha3D
    # -----------------------------
    # filtres_images
    from gui_modules_image.filtres_images.image_filtres_image import Image_FiltresImage

    # MUSIQUE-SON ------------
    from gui_modules_music_son.music_son_encodage import MusiqueSon_Encodage
    from gui_modules_music_son.music_son_join_multiplefile import MusiqueSon_Join
    from gui_modules_music_son.music_son_decoupe import MusiqueSon_decoupe
    from gui_modules_music_son.music_son_normalize import MusiqueSon_normalize

    # LECTURE ----------------
    from gui_modules_lecture.lecture_image import Lecture_VisionImage
    from gui_modules_lecture.lecture_video import Lecture_VisionVideo

    # MODE-SEQUENTIEL ------------- # En construction
    if len(sys.argv)==2 and sys.argv[1]=="sequentiel":
        from gui_modules_sequentiel.sequentiel import Sequentiel
    # -------------------------------------------------------------

    # ----------------------------------------------------------
    # MPlayer
    from moteur_modules_animation.mplayer import Mplayer
    # ----------------------------------------------------------

    EkdConfig.init()

    main = Gui_EKD()

    app.setStyle(QStyleFactory.create(EkdConfig.get("general", "qtstyle")))

    main.show()
    sys.exit(app.exec_())
