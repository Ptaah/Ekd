#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob
import shutil
import string
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_modules_animation.animation_base_encodageFiltre \
                                    import Base_EncodageFiltre
from gui_modules_common.mencoder_gui import WidgetMEncoder
from gui_modules_common.ffmpeg_gui import WidgetFFmpeg
from moteur_modules_animation.mencoder import extraireImage
from gui_modules_lecture.affichage_image.afficheurImage \
                                    import VisionneurImagePourEKD
from moteur_modules_animation.mplayer import getVideoSize, getVideoLength
from gui_modules_common.EkdWidgets import EkdSaveDialog
from moteur_modules_common.EkdConfig import EkdConfig
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Filtres_SansReglages(QWidget):
    # -------------------------------------------------------------------
    # Widgets associés aux filtres : Niveaux de gris, Reserve
    # pour sous-titres (Expand) et Miroir
    # -------------------------------------------------------------------
    def __init__(self):
        QWidget.__init__(self)

        # label texte
        txt1=_(u"Réglage automatique pour ce choix")
        label=QLabel("<center>%s</center>" %txt1)

        vbox=QVBoxLayout()
        vbox.addWidget(label)
        self.setLayout(vbox)


class Filtre_Bruit(QWidget):
    # -------------------------------------------------------------------
    # Widgets associés au filtre : Bruit
    # -------------------------------------------------------------------

    def __init__(self):
        QWidget.__init__(self)

        self.idSection = "animation_filtresvideo"

        hbox = QHBoxLayout(self)

        #=== boîte de groupe: Luma ===#

        vboxLuma = QVBoxLayout()

        lumaLabel = QLabel(_(u"Luma (%)"))

        # boite de combo
        # le self sert à afficher des informations sur les items à partir de la
        # fonction
        self.comboLuma=QComboBox() 
        self.listeCombo=[(_(u'Bruit uniforme'),    'bruituniforme', 'u'),\
            (_(u'Bruit Temporel'),        'bruittemporel', 't'),\
            (_(u'Bruit Temporel M'),    'bruittemporelm', 'a'),\
            (_(u'Haute Qualité'),        'hautequalite', 'h'),\
            (_(u'Mixe du Bruit'),        'mixedubruit', 'p')]

        # Insertion des codecs de compression dans la combo box
        for i in self.listeCombo:
                    self.comboLuma.addItem(i[0],QVariant(i[1]))

        self.connect(self.comboLuma,SIGNAL("activated(int)"),
                                            self.sauverTypeLuma)

        hboxLabelCombo = QHBoxLayout()
        hboxLabelCombo.addStretch()
        hboxLabelCombo.addWidget(lumaLabel)
        hboxLabelCombo.addWidget(self.comboLuma)
        hboxLabelCombo.addStretch()
        vboxLuma.addLayout(hboxLabelCombo)

        self.spinBruitLuma=QSpinBox()
        self.spinBruitLuma.setRange(0,100)

        self.curseurBruitLuma = QSlider(Qt.Horizontal)
        self.curseurBruitLuma.setRange(0,100)

        hboxSpinSlider = QHBoxLayout()
        hboxSpinSlider.addWidget(self.spinBruitLuma)
        hboxSpinSlider.addWidget(self.curseurBruitLuma)
        vboxLuma.addLayout(hboxSpinSlider)
        hbox.addLayout(vboxLuma)

        #=== séparateur ===#

        ligne = QFrame()
        ligne.setFrameShape(QFrame.VLine)
        ligne.setFrameShadow(QFrame.Sunken)
        hbox.addWidget(ligne)

        #=== boîte de groupe: Chroma ===#

        vboxChroma = QVBoxLayout()

        labelChroma = QLabel(_(u"Chroma (%)"))

        self.comboChroma=QComboBox()
        for i in self.listeCombo:
                    self.comboChroma.addItem(i[0],QVariant(i[1]))

        self.connect(self.comboChroma,SIGNAL("activated(int)"),
                                            self.sauverTypeChroma)

        hboxLabelCombo = QHBoxLayout()
        hboxLabelCombo.addStretch()
        hboxLabelCombo.addWidget(labelChroma)
        hboxLabelCombo.addWidget(self.comboChroma)
        hboxLabelCombo.addStretch()
        vboxChroma.addLayout(hboxLabelCombo)

        self.spinBruitChroma=QSpinBox()
        self.spinBruitChroma.setRange(0,100)

        self.curseurBruitChroma = QSlider(Qt.Horizontal)
        self.curseurBruitChroma.setRange(0,100)

        hboxSpinSlider = QHBoxLayout()
        hboxSpinSlider.addWidget(self.spinBruitChroma)
        hboxSpinSlider.addWidget(self.curseurBruitChroma)
        vboxChroma.addLayout(hboxSpinSlider)
        hbox.addLayout(vboxChroma)

        #=== sauver configuration ===#

        # spins

        self.connect(self.spinBruitLuma,SIGNAL("valueChanged(int)"),
                                                    self.sauverSpinLuma)
        self.connect(self.spinBruitChroma,SIGNAL("valueChanged(int)"),
                                                    self.sauverSpinChroma)
        self.connect(self.curseurBruitLuma, SIGNAL("sliderMoved(int)"),
                                                    self.curseurLumaBouge)
        self.connect(self.curseurBruitChroma, SIGNAL("sliderMoved(int)"),
                                                    self.curseurChromaBouge)

        try:
            #print EkdConfig.get(self.idSection,'valeur_bruit_luma')
            EkdPrint(EkdConfig.get(str(self.idSection),' valeur_bruit_luma'))
            self.spinBruitLuma.setValue(int(EkdConfig.get(self.idSection,
                                                        'valeur_bruit_luma')))
            #print EkdConfig.get(self.idSection,'valeur_bruit_chroma')
            EkdPrint(EkdConfig.get(str(self.idSection),' valeur_bruit_chroma'))
            self.spinBruitChroma.setValue(int(EkdConfig.get(self.idSection,
                                                        'valeur_bruit_chroma')))

        except:
	    '''
            print "Pas de paramètres de configuration pour:\n\
            Valeur de Bruit Luma ou Bruit Chroma"
	    '''
	    EkdPrint(u"Pas de paramètre de configuration pour:\nValeur de Bruit Luma ou Bruit Chroma")
	    
        # boites de combo: sauvegarde pas encore implémentée

        self.comboLuma.setCurrentIndex(1)

        # affichage des entrée de boite de combo correspondant à celles du
        # fichier de config
        try:
            #print EkdConfig.get(self.idSection,'type_bruit_luma')
            EkdPrint(EkdConfig.get(str(self.idSection),' type_bruit_luma'))
            typ = EkdConfig.get(self.idSection,'type_bruit_luma')
            # indice de la ligne de self.listeCombo correspondant au type
            # de bruit
            indice = 0
            for i in self.listeCombo:
                if i[1]!=typ:
                    indice += 1
                else:
                    break
            self.comboLuma.setCurrentIndex(indice)

            #print EkdConfig.get(self.idSection,'type_bruit_chroma')
            EkdPrint(EkdConfig.get(str(self.idSection),' type_bruit_chroma'))
            typ = EkdConfig.get(self.idSection,'type_bruit_chroma')
            # indice de la ligne de self.listeCombo correspondant au type de
            # bruit
            indice = 0
            for i in self.listeCombo:
                if i[1]!=typ:
                    indice += 1
                else:
                    break
            self.comboChroma.setCurrentIndex(indice)
        except:
	    '''
            print "Pas de paramètres de configuration pour:\n\
            Type de Bruit Luma ou Bruit Chroma"
            '''
            EkdPrint(u"Pas de paramètre de configuration pour:\nType de Bruit Luma ou Bruit Chroma")

    def sauverTypeLuma(self,i):
        """ Pas d'utilité pour le moment """
        idLuma = str(self.comboLuma.itemData(i).toStringList()[0])
        #print 'identifiant type de bruit luma :', idLuma, '; indice :', i
        EkdPrint(u'identifiant type de bruit luma : %s ; indice %s' % (idLuma, i))
        EkdConfig.set(self.idSection,'type_bruit_luma',idLuma)

    def sauverTypeChroma(self,i):
        """ Pas d'utilité pour le moment """
        idChroma = str(self.comboChroma.itemData(i).toStringList()[0])
        #print 'identifiant type de bruit chroma :', idChroma, '; indice :', i
        EkdPrint(u'identifiant type de bruit chroma : %s ; indice %s' % (idChroma, i))
        EkdConfig.set(self.idSection,'type_bruit_chroma',idChroma)

    def sauverSpinLuma(self,i):
        """
            conserver le spin dans le fichier de configuration et modifier le 
            curseur
        """
        #print 'Luma :',i
        EkdPrint(u'Luma : %s' % i)
        EkdConfig.set(self.idSection,'valeur_bruit_luma',i)
        self.curseurBruitLuma.setValue(i)

    def sauverSpinChroma(self,i):
        """
            conserver le spin dans le fichier de configuration et modifier le 
            curseur
        """
        #print 'Chroma :',i
        EkdPrint('Chroma : %s' % i)
        EkdConfig.set(self.idSection,'valeur_bruit_chroma',i)
        self.curseurBruitChroma.setValue(i)

    def curseurLumaBouge(self,i):
        """
            Quand on change la position du curseur la valeur du spin est
            automatiquement modifiée
        """
        self.spinBruitLuma.setValue(i)

    def curseurChromaBouge(self,i):
        """
            Quand on change la position du curseur la valeur du spin est
            automatiquement modifiée
        """
        self.spinBruitChroma.setValue(i)


class Filtre_LuminosContrast(QWidget):
    # -------------------------------------------------------------------
    # Widgets associés au filtre : Luminosite-contraste
    # -------------------------------------------------------------------

    def __init__(self):
        QWidget.__init__(self)

        self.idSection = "animation_filtresvideo"

        vbox = QVBoxLayout(self)
        grid=QGridLayout()

        # ligne de la luminosité
        self.spinLuminosite=QSpinBox()
        self.spinLuminosite.setRange(-100,100) # 0 par défaut
        grid.addWidget(self.spinLuminosite,1,1)

        self.curseurLuminosite = QSlider(Qt.Horizontal)
        self.curseurLuminosite.setRange(-100,100)
        grid.addWidget(self.curseurLuminosite,1,2)

        label=QLabel('%s <font color="green">%s</font>' \
                     '-- <font color="red">%s</font>' % \
                     (  _(u"Luminosité entre -100 et 100 -> "),
                        _(u'-100: Basse'),
                        _(u'100: Haute')))
        grid.addWidget(label,1,3)

        # ligne du contraste
        self.spinContraste=QSpinBox()
        self.spinContraste.setRange(-100,100) # 0 par défaut
        grid.addWidget(self.spinContraste,2,1)

        self.curseurContraste = QSlider(Qt.Horizontal)
        self.curseurContraste.setRange(-100,100)
        grid.addWidget(self.curseurContraste,2,2)

        label=QLabel('%s <font color="green">%s</font> ' \
                     '-- <font color="red">%s</font>' % \
                     (   _(u"Contraste entre -100 et 100 -> "), \
                         _(u'-100: Bas'), \
                         _(u'100: Haut')))
        grid.addWidget(label,2,3)

        vbox.addStretch()
        vbox.addLayout(grid)
        vbox.addStretch()

        #=== sauver configuration ===#

        self.connect(self.spinLuminosite,SIGNAL("valueChanged(int)"),
                                                    self.sauverSpinLuminosite)
        self.connect(self.spinContraste,SIGNAL("valueChanged(int)"),
                                                    self.sauverSpinContraste)
        self.connect(self.curseurLuminosite, SIGNAL("sliderMoved(int)"),
                                                    self.curseurLuminositeBouge)
        self.connect(self.curseurContraste, SIGNAL("sliderMoved(int)"),
                                                    self.curseurContrasteBouge)

        try:
            #print EkdConfig.get(self.idSection,'luminosite')
            EkdPrint(EkdConfig.get(str(self.idSection),' luminosite'))
            self.spinLuminosite.setValue(int(EkdConfig.get(self.idSection,
                                                                'luminosite')))
            #print EkdConfig.get(self.idSection,'contraste')
            EkdPrint(EkdConfig.get(str(self.idSection),' contraste'))
            self.spinContraste.setValue(int(EkdConfig.get(self.idSection,
                                                                'contraste')))
        except:
	    '''
            print "Pas de paramètres de configuration pour:\n\
            Bruit Luminosite ou Contraste"
	    '''
	    EkdPrint(u"Pas de paramètres de configuration pour:\nBruit Luminosite ou Contraste")

    def sauverSpinLuminosite(self,i):
        """
            conserver le spin dans le fichier de configuration et modifier le 
            curseur
        """
        #print 'Luminosite :',i
        EkdPrint(u'Luminosite : %s' % i)
        EkdConfig.set(self.idSection,'luminosite',i)
        self.curseurLuminosite.setValue(i)

    def sauverSpinContraste(self,i):
        """
            conserver le spin dans le fichier de configuration et modifier le
            curseur
        """
        #print 'Contraste :',i
        EkdPrint(u'Contraste : %s' % i)
        EkdConfig.set(self.idSection,'contraste',i)
        self.curseurContraste.setValue(i)

    def curseurLuminositeBouge(self,i):
        """
            Quand on change la position du curseur la valeur du spin est
            automatiquement modifiée
        """
        self.spinLuminosite.setValue(i)

    def curseurContrasteBouge(self,i):
        """
            Quand on change la position du curseur la valeur du spin est
            automatiquement modifiée
        """
        self.spinContraste.setValue(i)


class Filtre_Decouper(QWidget):
    # -------------------------------------------------------------------
    # Widgets associés au filtre : Decouper (Crop)
    # -------------------------------------------------------------------

    def __init__(self, extractionImages, modeSelect=0):
        QWidget.__init__(self)

        self.idSection = "animation_filtresvideo"

        # Référence à la fonction d'extraction d'images
        self.extractionImages = extractionImages

        hbox = QHBoxLayout(self)

        #---- Grille de boutons radio des positions
        self.widgetRadio = QWidget()
        gridRadio = QGridLayout(self.widgetRadio)
        self.listeRadio = [[0] * 3, [0] * 3, [0] *3 ]
        for i in range(3):
            for j in range(3):
                radio = QRadioButton()
                radio.setToolTip(_(u"Position de la sélection dans la vidéo"))
                self.listeRadio[i][j] = radio
                gridRadio.addWidget(radio, i, j)
        self.listeRadio[1][1].setChecked(True)
        gridRadio.setAlignment(Qt.AlignHCenter)

        #---- Grille des boites de spin de position
        self.widgetPosition = QWidget()
        gridPosition = QGridLayout(self.widgetPosition)

        # largeur
        self.spinPositionL = QSpinBox()
        self.spinPositionL.setRange(0, 10000)
        gridPosition.addWidget(self.spinPositionL, 1, 1)

        txt1 = _(u"Position horizontale (px)")
        label = QLabel("%s" %txt1)
        self.spinPositionL.setProperty('', QVariant(txt1))
        gridPosition.addWidget(label, 1, 2)

        # hauteur
        self.spinPositionH = QSpinBox()
        self.spinPositionH.setRange(0, 10000) # 600 par défaut
        gridPosition .addWidget(self.spinPositionH, 2, 1)

        txt1 = _(u"Position en verticale (px)")
        label = QLabel("%s" %txt1)
        self.spinPositionH.setProperty('', QVariant(txt1))
        gridPosition.addWidget(label, 2, 2)

        self.stackedPosition = QStackedWidget()
        self.stackedPosition.addWidget(self.widgetRadio)
        self.stackedPosition.addWidget(self.widgetPosition)

        hbox.addWidget(self.stackedPosition, 0, Qt.AlignHCenter)

        #---- Séparateur
        ligne = QFrame()
        ligne.setFrameShape(QFrame.VLine)
        ligne.setFrameShadow(QFrame.Sunken)
        hbox.addWidget(ligne)

        #---- Boites de spin de largeur et hauteur de la sélection
        widgetSelection = QWidget()
        grid = QGridLayout(widgetSelection)

        # largeur
        self.spinDecoupeL = QSpinBox()
        self.spinDecoupeL.setRange(1,10000) # 800 par défaut
        grid.addWidget(self.spinDecoupeL, 1, 1)

        txt1 = _(u"Nouvelle Largeur (px)")
        label = QLabel("%s" %txt1)
        self.spinDecoupeL.setProperty('', QVariant(txt1))
        grid.addWidget(label, 1, 2)

        # hauteur
        self.spinDecoupeH = QSpinBox()
        self.spinDecoupeH.setRange(1, 10000) # 600 par défaut
        grid.addWidget(self.spinDecoupeH, 2, 1)

        txt1 = _(u"Nouvelle Hauteur (px)")
        label = QLabel("%s" %txt1)
        self.spinDecoupeH.setProperty('', QVariant(txt1))
        grid.addWidget(label, 2, 2)

        hbox.addWidget(widgetSelection, 0, Qt.AlignHCenter)

        #---- Séparateur
        ligne = QFrame()
        ligne.setFrameShape(QFrame.VLine)
        ligne.setFrameShadow(QFrame.Sunken)
        hbox.addWidget(ligne)

        #---- Bouton de configuration avancée
        self.boutonReglageAvance = QPushButton(_(u"Réglages avancés"))
        self.boutonReglageAvance.setEnabled(False)
        self.connect(self.boutonReglageAvance, SIGNAL("clicked()"),
                                                    self.__reglagesAvances)
        hbox.addWidget(self.boutonReglageAvance, 0, Qt.AlignHCenter)

        #---- Sauvegarde de la configuration
        self.connect(self.spinDecoupeL, SIGNAL("valueChanged(int)"),
                                                    self.__sauverSpinDecouperL)
        self.connect(self.spinDecoupeH, SIGNAL("valueChanged(int)"),
                                                    self.__sauverSpinDecouperH)
        self.connect(self.spinPositionL, SIGNAL("valueChanged(int)"),
                                                    self.__sauverSpinPositionL)
        self.connect(self.spinPositionH, SIGNAL("valueChanged(int)"),
                                                    self.__sauverSpinPositionH)

        try:
            #print EkdConfig.get(self.idSection,'decouper_largeur')
            EkdPrint(EkdConfig.get(str(self.idSection),' decouper_largeur'))
            self.spinDecoupeL.setValue(int(EkdConfig.get(self.idSection,
                                                        'decouper_largeur')))
            #print EkdConfig.get(self.idSection,'decouper_hauteur')
            EkdPrint(EkdConfig.get(str(self.idSection),' decouper_hauteur'))
            self.spinDecoupeH.setValue(int(EkdConfig.get(self.idSection,
                                                        'decouper_hauteur')))
            #print EkdConfig.get(self.idSection,'decouper_position_largeur')
            EkdPrint(EkdConfig.get(str(self.idSection),' decouper_position_largeur'))
            self.spinPositionL.setValue(int(EkdConfig.get(self.idSection,
                                                'decouper_position_largeur')))
            #print EkdConfig.get(self.idSection,'decouper_position_hauteur')
            EkdPrint(EkdConfig.get(str(self.idSection),' decouper_position_hauteur'))
            self.spinPositionH.setValue(int(EkdConfig.get(self.idSection,
                                                'decouper_position_hauteur')))

        except:
	    '''
            print "Pas de paramètres de configuration pour:\n" \
                                    "Decouper Largeur ou Longueur"
	    '''
	    EkdPrint(u"Pas de paramètre de configuration pour:\nDecouper Largeur ou Longueur")

    def __sauverSpinDecouperL(self, i):
        "Conserve la valeur dans le fichier de configuration"
        EkdConfig.set(self.idSection, 'decouper_largeur', i)

    def __sauverSpinDecouperH(self, i):
        "Conserve la valeur dans le fichier de configuration"
        EkdConfig.set(self.idSection, 'decouper_hauteur', i)

    def __sauverSpinPositionL(self, i):
        "Conserve la valeur dans le fichier de configuration"
        EkdConfig.set(self.idSection, 'decouper_position_largeur', i)

    def __sauverSpinPositionH(self, i):
        "Conserve la valeur dans le fichier de configuration"
        EkdConfig.set(self.idSection,'decouper_position_hauteur', i)

    def setStacked(self, stack):
        """Montre le widget de réglage de la position conforme à celui de
        la boite de combo du widget parent (widget de sélection du filtre).
        """
        if stack == 'decoupageassiste':
            self.stackedPosition.setCurrentWidget(self.widgetRadio)
        elif stack == 'decoupagelibre':
            self.stackedPosition.setCurrentWidget(self.widgetPosition)

    def setComboParent(self, combo):
        """
            Donne la référence de la boite de combo indiquant quel type
            de découpage est actuellement sélectionné: assisté ou contraint
        """
        self.comboParent = combo

    def setButtonEnabled(self, boolean):
        """Active ou désactive le bouton de réglage avancé"""
        self.boutonReglageAvance.setEnabled(boolean)

    def __getComboParent(self):
        """
            Récupère la boite de combo indiquant quel type de découpage est
            actuellement sélectionné: assisté ou contraint
        """
        return self.comboParent

    def __setNewValues(self, mode, posLibreL, posLibreH,
            posRadioC, posRadioL, tailleSelL, tailleSelH):
        """
            Attribut de nouvelles valeurs de découpage.
            Celles-ci proviennent de la boite de dialogue de découpage
        """
        self.setWidthHeight(posLibreL, posLibreH, tailleSelL, tailleSelH)
        self.listeRadio[posRadioC][posRadioL].setChecked(True)
        self.emit(SIGNAL("changerModeDecoupe(QString)"), mode)

    # Fonction permettant simplement de changer les valeurs des spinBox
    def setWidthHeight(self, x, y, width, height):
        self.spinPositionL.setValue(x)
        self.spinPositionH.setValue(y)
        self.spinDecoupeL.setValue(width)
        self.spinDecoupeH.setValue(height)


    def __coordRadio(self):
        """Renvoie un tuple d'indices de la ligne et de la colonne de la grille
        correspondant au bouton radio sélectionné
        """
        for i in range(3):
            for j in range(3):
                if self.listeRadio[i][j].isChecked():
                    return i, j

    def getPos(self, largeurVideo, hauteurVideo):
        """Renvoie un tuple contenant:
        - la largeur de la sélection
        - la hauteur de la sélection
        - la position en largeur (abscisse) du point supérieur-gauche du
          rectangle de sélection
        - la position en hauteur (abscisse) du point supérieur-gauche du
          rectangle de sélection
        Prend la largeur et la hauteur de la vidéo source en argument.
        """

        # Selon le mode de découpe, la position de la sélection n'est pas
        # la même
        # On récupère donc le mode de découpe
        comboParent = self.__getComboParent()
        i = comboParent.currentIndex()
        mode = comboParent.itemData(i).toString()

        if mode == 'decoupageassiste':
            indiceLigneBoutonRadio, indiceColonneBoutonRadio = \
                                                self.__coordRadio()
            a = largeurVideo - self.spinDecoupeL.value()
            b = hauteurVideo - self.spinDecoupeH.value()
            posX = int(1. / 2 * indiceColonneBoutonRadio * a)
            posY = int(1. / 2 * indiceLigneBoutonRadio * b)
            # Pas de coordonnées négatives
            if posX < 0:
                posX = 0
            if posY < 0:
                posY = 0

        elif mode == 'decoupagelibre':
            posX, posY = self.spinPositionL.value(), self.spinPositionH.value()

        return self.spinDecoupeL.value(), self.spinDecoupeH.value(), posX, posY

    def __getImages(self):
        """Renvoie la liste des adresses des 12 images réparties sur la vidéo.
        Elles serviront d'aperçu de la découpe
        """
        liste = self.extractionImages()
        return liste

    def __reglagesAvances(self):
        """
            Créée et affiche une boite de dialogue de découpe comprenant
            12 images réparties sur la vidéo source, ainsi que les widgets de
            réglage (position et taille de la sélection)
        """

        # Liste des adresses des images
        listeImages = self.__getImages()
        # Si l'utilisateur clique sur le bouton annuler de la boite de dialogue
        # de progression alors la liste renvoyée sera vide -> on annule la
        # création de la boite de dialogue de réglage
        if not listeImages:
            return

        # Mode de découpe
        comboParent = self.__getComboParent()
        i = comboParent.currentIndex()
        mode = comboParent.itemData(i).toString()

        # Indices de la ligne et de la colonne du bouton radio sélectionné
        posRadio = self.__coordRadio()

        # Propriétés de position supérieure-gauche du rectangle de sélection
        a, b = self.spinPositionL, self.spinPositionH
        posLibre = ((a.minimum(), a.maximum(), a.value(), 
                                    a.property('').toString()),
                    (b.minimum(), b.maximum(), b.value(),
                                    b.property('').toString()))

        # Propriétés de taille du rectangle de sélection
        a, b = self.spinDecoupeL, self.spinDecoupeH
        tailleSel = ((a.minimum(), a.maximum(), a.value(), 
                                    a.property('').toString()),
                    (b.minimum(), b.maximum(), b.value(),
                                    b.property('').toString()))

        # Creéation de la boite de dialogue de réglage de découpe avancé
        dialog = DialogReglagesDecoupe(mode, posLibre, posRadio, tailleSel,
                                                                    listeImages)
        # On récupère les nouvelles valeurs de découpe avant la fermeture de
        # la boite de dialogue
        self.connect(dialog, 
                    SIGNAL("newValues(QString, int, int, int, int, int, int)"),
                    self.__setNewValues)
        dialog.exec_()


class DialogReglagesDecoupe(QDialog):
    """
        Boite de dialogue de réglage de découpe avancé comprenant 12 images
        réparties sur la vidéo source, ainsi que les widgets de réglage
        (position et taille de la sélection)
    """

    def __init__(self, mode="decoupagelibre", 
                 posLibre=((10, 20, 15, "texte"), (10, 20, 15, "texte")),
                 posRadio=(2, 2),
                 tailleSel=((10, 20, 15, "texte"), (10, 20, 15, "texte")),
                 listeImages=[]):

        QDialog.__init__(self)

        self.setWindowTitle(_(u"Aperçu du découpage"))
        #=== Définition de variables ===#

        # On sauvegarde les paramètres de sélection pour éventuellement les
        # restaurer plus tard
        self.posLibreIni = posLibre[0][2], posLibre[1][2]
        self.posRadioIni = posRadio
        self.tailleSelIni = tailleSel[0][2], tailleSel[1][2]
        self.modeIni = mode

        # Déclaration d'une liste des objet-images
        self.listeImages = [QImage(i) for i in listeImages]
        # Largeur et hauteur des images
        self.largeurImage = self.listeImages[0].size().width()
        self.hauteurImage = self.listeImages[0].size().height()

        # Positions
        if mode == 'decoupagelibre':
            posX, posY = self.posLibreIni
        elif mode =='decoupageassiste':
            posX, posY = self.__getPos(self.posRadioIni[0], self.posRadioIni[1],
                        self.tailleSelIni[0], self.tailleSelIni[1])

        #=== Création des widgets  ===#
        self.main = QVBoxLayout(self)
        vbox = QVBoxLayout()
        #vbox = QVBoxLayout(self)

        #---- Création des aperçus (images placés dans une grille 3 x 4)
        #self.nbrLignesImg, self.nbrColImg = 3, 4
        self.nbrLignesImg, self.nbrColImg = 3, 4
        self.listeApercu = [[0] * self.nbrColImg, [0] * self.nbrColImg, [0] * \
                                                                self.nbrColImg]
        gridImg = QGridLayout()

        # Détermination du paramètre de taille limitant (largeur ou hauteur)
        # pour l'affichage de notre grille d'images

        # Taille de l'écran
        largeurEcran = QDesktopWidget().screenGeometry().width()
        hauteurEcran = QDesktopWidget().screenGeometry().height()
        # Largeur et hauteur de la série (grille) d'images
        largeurSerieImg = self.nbrColImg * self.largeurImage
        hauteurSerieImg = self.nbrLignesImg * self.hauteurImage

        if largeurEcran - largeurSerieImg >= hauteurEcran - hauteurSerieImg:
            # Largeur = facteur limitant de la grille d'images
            limitationHauteur = 0
        else:
            # Hauteur = facteur limitant de la grille d'images
            limitationHauteur = 1

        # Tailles maximum des lignes et des colonnes d'images en pixels
        if limitationHauteur:
            #tailleColMaxImgDialog = int(hauteurEcran * 0.66)
            tailleColMaxImgDialog = int(hauteurEcran * 0.4)

            # Hauteur de l'image (à l'écran)
            tailleImg = tailleColMaxImgDialog / self.nbrLignesImg
        else:
            #tailleLigneMaxImgDialog = int(largeurEcran * 0.66)
            tailleLigneMaxImgDialog = int(largeurEcran * 0.4)

            # Largeur d'une image (à l'écran)
            tailleImg = tailleLigneMaxImgDialog / self.nbrColImg
        for i in range(self.nbrLignesImg):
            for j in range(self.nbrColImg):
                # Création des aperçus
                apercu = ApercuDecoupe((posX, posY), 
                            (self.tailleSelIni[0],  self.tailleSelIni[1]),
                            (limitationHauteur, tailleImg),
                            self.listeImages[self.nbrLignesImg * i + j])

                self.listeApercu[i][j] = apercu
                gridImg.addWidget(apercu, i, j)

        vbox.addLayout(gridImg)

        #---- Création des widgets de réglage

        hbox = QHBoxLayout()
        #---- Grille de boutons radio des positions
        self.widgetRadio = QWidget()
        gridRadio = QGridLayout(self.widgetRadio)
        self.listeRadio = [[0] * 3, [0] * 3, [0] * 3]
        for i in range(3):
            for j in range(3):
                radio = QRadioButton()
                radio.setToolTip(_(u"Position de la sélection dans la vidéo"))
                self.connect(radio, SIGNAL("released()"),
                                self.__rafraichirApercus)
                gridRadio.addWidget(radio, i, j)
                self.listeRadio[i][j] = radio
        self.listeRadio[self.posRadioIni[0]][self.posRadioIni[1]].setChecked(
                                                                        True)
        gridRadio.setAlignment(Qt.AlignHCenter)

        #---- Grille des boites de spin des positions
        self.widgetPosition = QWidget()
        gridPosition = QGridLayout(self.widgetPosition)

        # largeur
        self.spinPositionL = QSpinBox()
        self.spinPositionL.setRange(posLibre[0][0], posLibre[0][1])
        self.spinPositionL.setValue(posLibre[0][2])
        self.connect(self.spinPositionL, SIGNAL('valueChanged(int)'), 
                                                    self.__rafraichirApercus)
        gridPosition.addWidget(self.spinPositionL, 1, 1)

        gridPosition.addWidget(QLabel(posLibre[0][3]), 1, 2)

        # hauteur
        self.spinPositionH = QSpinBox()
        self.spinPositionH.setRange(posLibre[1][0], posLibre[1][1])
        self.spinPositionH.setValue(posLibre[1][2])
        self.connect(self.spinPositionH, SIGNAL('valueChanged(int)'),
                                                    self.__rafraichirApercus)
        gridPosition.addWidget(self.spinPositionH, 2, 1)

        gridPosition.addWidget(QLabel(posLibre[1][3]), 2, 2)

        self.stackedPosition = QStackedWidget()
        self.stackedPosition.addWidget(self.widgetRadio)
        self.stackedPosition.addWidget(self.widgetPosition)

        hbox.addWidget(self.stackedPosition, 0, Qt.AlignHCenter)

        # Boite de combo
        self.combo = QComboBox()
        listeCombo = [    ('decoupageassiste',
                         _(u'Decoupage assisté (Crop)')),
                          ('decoupagelibre',
                         _(u'Decoupage libre (Crop)'))]
        for i in listeCombo:
                    self.combo.addItem(i[1], QVariant(i[0]))
        self.connect(self.combo, SIGNAL("currentIndexChanged(int)"),
                        self.__rafraichirApercus)

        vbox.addWidget(self.combo)

        #---- Séparateur
        ligne = QFrame()
        ligne.setFrameShape(QFrame.VLine)
        ligne.setFrameShadow(QFrame.Sunken)
        hbox.addWidget(ligne)

        #---- largeur et hauteur de la sélection
        widgetSelection = QWidget()
        grid = QGridLayout(widgetSelection)

        # largeur
        self.spinDecoupeL=QSpinBox()
        # 800 par défaut
        self.spinDecoupeL.setRange(tailleSel[0][0], tailleSel[0][1])
        self.spinDecoupeL.setValue(self.tailleSelIni[0])
        self.connect(self.spinDecoupeL, SIGNAL('valueChanged(int)'),
                                                self.__rafraichirApercus)
        grid.addWidget(self.spinDecoupeL,1,1)

        grid.addWidget(QLabel(tailleSel[0][3]), 1, 2)

        # hauteur
        self.spinDecoupeH=QSpinBox()
        self.spinDecoupeH.setRange(tailleSel[1][0], tailleSel[1][1])
        self.spinDecoupeH.setValue(self.tailleSelIni[1])
        self.connect(self.spinDecoupeH, SIGNAL('valueChanged(int)'),
                                                self.__rafraichirApercus)
        grid.addWidget(self.spinDecoupeH,2,1)

        grid.addWidget(QLabel(tailleSel[1][3]), 2, 2)

        hbox.addWidget(widgetSelection, 0, Qt.AlignHCenter)

        #=== Widgets du bas ===#

        # ligne de séparation juste au dessus des boutons
        ligne = QFrame()
        ligne.setFrameShape(QFrame.HLine)
        ligne.setFrameShadow(QFrame.Sunken)

        boutReinitialiser = QPushButton(_(u"Réinitialiser"))
        boutConserver = QPushButton(_(u"Conserver les paramètres"))
        boutAnnuler = QPushButton(_(u"Annuler"))
        self.connect(boutReinitialiser, SIGNAL("clicked()"),
                                            self.__reinitialiserParam)
        self.connect(boutConserver, SIGNAL("clicked()"), self.__conserverParam)
        self.connect(boutAnnuler, SIGNAL("clicked()"), self.close)
        hboxBas = QHBoxLayout()
        hboxBas.addWidget(boutReinitialiser)
        hboxBas.addStretch()
        hboxBas.addWidget(boutConserver)
        hboxBas.addWidget(boutAnnuler)

        vbox.addWidget(self.combo, 0, Qt.AlignHCenter)
        vbox.addLayout(hbox)
        vbox.addStretch()
        vbox.addWidget(ligne)
        vbox.addSpacing(-5)
        vbox.addLayout(hboxBas)

        self.scroll = QScrollArea()
        self.scroll.setLayout(vbox)
        self.main.addWidget(self.scroll)

        #=== Sélection de la bonne entrée de la boite de combo===#
        if mode == 'decoupagelibre':
            indexCombo = self.combo.findData(QVariant('decoupagelibre'))
        elif mode =='decoupageassiste':
            indexCombo = self.combo.findData(QVariant('decoupageassiste'))
        self.combo.setCurrentIndex(indexCombo)
        self.setMinimumSize(QSettings().value("MainWindow/Size",
                                            QVariant(QSize(800, 600))).toSize())

    def __conserverParam(self):
        """
            Transmet les paramètres de découpe (position, taille et type de la
            sélection) au widget de réglage de la fenêtre principale avant de
            fermer la boite de dialogue
        """
        coordRadio =  self.__coordRadio()
        self.emit(SIGNAL("newValues(QString, int, int, int, int, int, int)"),
                self.combo.itemData(self.combo.currentIndex()).toString(),
                self.spinPositionL.value(),
                self.spinPositionH.value(),
                coordRadio[0],
                coordRadio[1],
                self.spinDecoupeL.value(),
                self.spinDecoupeH.value())
        self.close()

    def __reinitialiserParam(self):
        """
            Remet les paramètres de réglages dans l'état dans lequel ils
            étaient lors de la création de la boite de dialogue
        """
        self.spinPositionL.setValue(self.posLibreIni[0])
        self.spinPositionH.setValue(self.posLibreIni[1])
        self.spinDecoupeL.setValue(self.tailleSelIni[0])
        self.spinDecoupeH.setValue(self.tailleSelIni[1])
        self.listeRadio[self.posRadioIni[0]][self.posRadioIni[1]].setChecked(
                                                                        True)
        indexCombo = self.combo.findData(QVariant(self.modeIni))
        self.combo.setCurrentIndex(indexCombo)

    def __coordRadio(self):
        """Renvoie un tuple d'indices de la ligne et de la colonne de la grille
        correspondant au bouton radio sélectionné
        """
        for i in range(3):
            for j in range(3):
                if self.listeRadio[i][j].isChecked():
                    return i, j

    def __rafraichirApercus(self, paramInutile=None):
        """
            Fait coïncider les images d'aperçu de découpe aux les paramètres
            de réglages
        """

        # On récupère les principaux paramètres de sélection et on les donne
        # aux images d'aperçu de sélection.

        # Récupération du mode de découpe
        i = self.combo.currentIndex()
        mode = self.combo.itemData(i).toString()

        if mode == "decoupageassiste":
            # On calcule la position du coin supérieur-gauche du rectangle de
            # sélection qui sera affiché sur l'image d'aperçu
            m, n = self.__coordRadio()
            posX, posY = self.__getPos(m, n)
            self.stackedPosition.setCurrentWidget(self.widgetRadio)
        elif mode == "decoupagelibre":
            posX, posY = self.spinPositionL.value(), self.spinPositionH.value()
            self.stackedPosition.setCurrentWidget(self.widgetPosition)
        # Mise-à-jour des 12 images d'aperçu
        for i in range(self.nbrLignesImg):
            for j in range(self.nbrColImg):
                self.listeApercu[i][j].setValues((posX, posY),
                    (self.spinDecoupeL.value(), self.spinDecoupeH.value()))

    def __getPos(self, indiceLigneBoutonRadio, indiceColonneBoutonRadio,
            largeurSelection=None, hauteurSelection=None):
        """
        Renvoie le tuple de la position (abscisses et ordonnées en pixel) de la
        sélection pour le mode de sélection assistée. Le bouton radio
        sélectionné et les tailles des images seront utilisés à cette fin.
        Prend les indices de la ligne et de la colonne de la grille
        correspondant au bouton radio sélectionné (voire la largeur et la
        hauteur de a sélection) en arguments.
        """
        if not largeurSelection:
            largeurSelection = self.spinDecoupeL.value()
            hauteurSelection = self.spinDecoupeH.value()
        a = self.largeurImage - largeurSelection
        b = self.hauteurImage - hauteurSelection
        posX = 1. / 2 * indiceColonneBoutonRadio * a
        posY = 1. / 2 * indiceLigneBoutonRadio * b
        # Pas de coordonnées négatives
        if posX < 0:
            posX = 0
        if posY < 0:
            posY = 0

        return posX, posY


class ApercuDecoupe(QWidget):
    """
        Aperçu de la découpe d'une image de la vidéo. La partie sélectionnée
        est rectangulaire
    """

    def __init__(self, posSel=(10, 20), tailleSel=(100, 150),
            (limitationHauteur, tailleImg)=(100, 120), img=QImage()):
        QWidget.__init__(self)

        # Position de la sélection (abscisse supérieure-droite, ordonnée
        # supérieure-droite)
        self.posSel = posSel
        # Taille de la sélection (largeur de la sélection, hauteur de la
        # sélection)
        self.tailleSel = tailleSel

        if limitationHauteur:
            # La hauteur des images est le facteur limitant
            self.ratio = float(tailleImg) / img.size().height()
            self.image = img.scaledToHeight(tailleImg)
        else:
            # La largeur des images est le facteur limitant
            self.ratio = float(tailleImg) / img.size().width()
            self.image = img.scaledToWidth(tailleImg)

    def sizeHint(self):
        return QSize(self.image.size().width(), self.image.size().height())

    def minimumSizeHint(self):
            return QSize(self.image.size().width(), self.image.size().height())

    def setValues(self, pos=(10, 20), taille=(100, 150)):
        "Spécifie les paramètres de sélection de la zone rectangulaire"
        self.posSel = pos
        self.tailleSel = taille
        self.repaint()

    def paintEvent(self, event):
        "Trace le rectangle de sélection"
        paint = QPainter()
        paint.begin(self)
        paint.drawImage(0, 0, self.image)
        f = self.ratio
        paint.drawRect(f*self.posSel[0], f*self.posSel[1], f*self.tailleSel[0], 
                                                            f*self.tailleSel[1])
        paint.end()


class Filtre_CouleurSaturation(QWidget):
    # -------------------------------------------------------------------
    # Widgets associés au filtre : Couleur/Saturation (Hue)
    # -------------------------------------------------------------------
    def __init__(self):
        QWidget.__init__(self)

        self.idSection = "animation_filtresvideo"

        vbox = QVBoxLayout(self)
        grid=QGridLayout()

        # ligne de la couleur
        self.spinCouleur=QSpinBox()
        self.spinCouleur.setRange(-180,180) # 0 par défaut
        grid.addWidget(self.spinCouleur,1,1)

        self.curseurCouleur=QSlider(Qt.Horizontal)
        self.curseurCouleur.setRange(-180,180)
        grid.addWidget(self.curseurCouleur,1,2)

        txt1,txt2,txt3=_(u"Couleur entre -180 et 180 -> "),_(u'-180: Basse'),_(u'180: Haute')
        label=QLabel('%s <font color="green">%s</font> -- <font color="red">%s</font>' %(txt1,txt2,txt3))
        grid.addWidget(label,1,3)

        # ligne de la saturation
        self.spinSaturation=QSpinBox()
        self.spinSaturation.setRange(-10,10) # 0 par défaut
        grid.addWidget(self.spinSaturation,2,1)

        self.curseurSaturation=QSlider(Qt.Horizontal)
        self.curseurSaturation.setRange(-10,10)
        grid.addWidget(self.curseurSaturation,2,2)

        txt1,txt2,txt3=_(u"Saturation entre -10 et 10 -> "),_(u'-10: Basse'),_(u'10: Haute')
        label=QLabel('%s <font color="green">%s</font> -- <font color="red">%s</font>' %(txt1,txt2,txt3))
        grid.addWidget(label,2,3)

        vbox.addStretch()
        vbox.addLayout(grid)
        vbox.addStretch()

        #=== sauver configuration ===#

        self.connect(self.spinCouleur,SIGNAL("valueChanged(int)"),self.sauverSpinCouleur)
        self.connect(self.spinSaturation,SIGNAL("valueChanged(int)"),self.sauverSpinSaturation)
        self.connect(self.curseurCouleur,SIGNAL("sliderMoved(int)"),self.curseurCouleurBouge)
        self.connect(self.curseurSaturation,SIGNAL("sliderMoved(int)"),self.curseurSaturationBouge)

        try:
            #print EkdConfig.get(self.idSection,'couleur')
            EkdPrint(EkdConfig.get(str(self.idSection),' couleur'))
            self.spinCouleur.setValue(int(EkdConfig.get(self.idSection,'couleur')))
            #print EkdConfig.get(self.idSection,'saturation')
            EkdPrint(EkdConfig.get(str(self.idSection),' saturation'))
            self.spinSaturation.setValue(int(EkdConfig.get(self.idSection,'saturation')))
        except:
	    '''
            print "Pas de paramètres de configuration pour:\n\
            Couleur ou Saturation"
            '''
            EkdPrint(u"Pas de paramètre de configuration pour:\nCouleur ou Saturation")

    def sauverSpinCouleur(self,i):
        """conserver le spin dans le fichier de configuration et modifier le curseur"""
        #print 'Couleur :',i
        EkdPrint(u'Couleur : %s' % i)
        EkdConfig.set(self.idSection,'couleur',i)
        self.curseurCouleur.setValue(i)

    def sauverSpinSaturation(self,i):
        """conserver le spin dans le fichier de configuration et modifier le curseur"""
        #print 'Saturation :',i
        EkdPrint(u'Saturation : %s' % i)
        EkdConfig.set(self.idSection,'saturation',i)
        self.curseurSaturation.setValue(i)

    def curseurCouleurBouge(self,i):
        """Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
        self.spinCouleur.setValue(i)

    def curseurSaturationBouge(self,i):
        """Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
        self.spinSaturation.setValue(i)


class Filtre_FlouBoite(QWidget):
    # -------------------------------------------------------------------
    # Widgets associés au filtre : Flou boîte (Boxblur)
    # -------------------------------------------------------------------
    def __init__(self):
        QWidget.__init__(self)

        self.idSection = "animation_filtresvideo"

        vbox = QVBoxLayout(self)
        grid=QGridLayout()

        # ligne du rayon
        self.spinFlouBoiteRayon=QSpinBox()    # self car on va récupérer la variable depuis le moteur

        self.spinFlouBoiteRayon.setRange(1,100) # 1 par défaut
        grid.addWidget(self.spinFlouBoiteRayon,1,1)

        self.curseurFlouBoiteRayon=QSlider(Qt.Horizontal)
        self.curseurFlouBoiteRayon.setRange(1,100)
        grid.addWidget(self.curseurFlouBoiteRayon,1,2)

        txt1=_(u"Rayon du flou (%)")
        label=QLabel("%s" %txt1)
        grid.addWidget(label,1,3)

        # ligne de la puissance
        self.spinFlouBoitePuiss=QSpinBox()
        self.spinFlouBoitePuiss.setRange(1, 100) # 1 par défaut
        grid.addWidget(self.spinFlouBoitePuiss,2,1)

        self.curseurFlouBoitePuiss=QSlider(Qt.Horizontal)
        self.curseurFlouBoitePuiss.setRange(1,100)
        grid.addWidget(self.curseurFlouBoitePuiss,2,2)

        txt1=_(u"Puissance du flou (%)")
        label=QLabel("%s" %txt1)
        grid.addWidget(label,2,3)

        vbox.addStretch()
        vbox.addLayout(grid)
        vbox.addStretch()

        #=== sauver configuration ===#

        self.connect(self.spinFlouBoiteRayon,SIGNAL("valueChanged(int)"),self.sauverSpinFlouBoiteRayon)
        self.connect(self.spinFlouBoitePuiss,SIGNAL("valueChanged(int)"),self.sauverSpinFlouBoitePuiss)
        self.connect(self.curseurFlouBoiteRayon,SIGNAL("sliderMoved(int)"),self.curseurFlouBoiteRayonBouge)
        self.connect(self.curseurFlouBoitePuiss,SIGNAL("sliderMoved(int)"),self.curseurFlouBoitePuissBouge)

        try:
            #print EkdConfig.get(self.idSection,'flou_boite_rayon')
            EkdPrint(EkdConfig.get(str(self.idSection),' flou_boite_rayon'))
            self.spinFlouBoiteRayon.setValue(int(EkdConfig.get(self.idSection,'flou_boite_rayon')))
            #print EkdConfig.get(self.idSection,'flou_boite_puissance')
            EkdPrint(EkdConfig.get(str(self.idSection),' flou_boite_puissance'))
            self.spinFlouBoitePuiss.setValue(int(EkdConfig.get(self.idSection,'flou_boite_puissance')))

        except:
	    '''
            print "Pas de paramètres de configuration pour:\n\
            Flou Boite Rayon ou Puissance"
	    '''
	    EkdPrint(u"Pas de paramètre de configuration pour:\nFlou Boite Rayon ou Puissance")
	    
    def sauverSpinFlouBoiteRayon(self,i):
        """conserver le spin dans le fichier de configuration et modifier le curseur"""
        #print 'FlouBoiteRayon :',i
        EkdPrint(u'FlouBoiteRayon : %s' % i)
        EkdConfig.set(self.idSection,'flou_boite_rayon',i)
        self.curseurFlouBoiteRayon.setValue(i)

    def sauverSpinFlouBoitePuiss(self,i):
        """conserver le spin dans le fichier de configuration et modifier le curseur"""
        #print 'FlouBoitePuiss :',i
        EkdPrint(u'FlouBoitePuiss : %s' % i)
        EkdConfig.set(self.idSection,'flou_boite_puissance',i)
        self.curseurFlouBoitePuiss.setValue(i)

    def curseurFlouBoiteRayonBouge(self,i):
        """Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
        self.spinFlouBoiteRayon.setValue(i)

    def curseurFlouBoitePuissBouge(self,i):
        """Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
        self.spinFlouBoitePuiss.setValue(i)


class Filtre_ChangResolution(QWidget):
    # -------------------------------------------------------------------
    # Widgets associés au filtre : Changement de résolution -->
    # redimensionnement des vidéos. Attention lors de l'encodage (car si
    # on redimensionne il faut en même temps encoder), l'encodage (voir
    # ds mencoder.py) se fera en Motion JPEG
    # -------------------------------------------------------------------

    def __init__(self):
        QWidget.__init__(self)

        self.idSection = "animation_filtresvideo"

        vbox = QVBoxLayout(self)
        grid=QGridLayout()

        # ligne nouvelle largeur
        self.spinRedimLargeur=QSpinBox()    # self car on va récupérer la variable depuis le moteur
        self.spinRedimLargeur.setRange(100, 2048) # 640 par défaut
        grid.addWidget(self.spinRedimLargeur, 1, 1)

        self.curseurRedimLargeur=QSlider(Qt.Horizontal)
        self.curseurRedimLargeur.setRange(100, 2048)
        grid.addWidget(self.curseurRedimLargeur, 1, 2)

        txt1=_(u"Nouvelle largeur")
        label=QLabel("%s" %txt1)
        grid.addWidget(label, 1, 3)

        # ligne nouvelle hauteur
        self.spinRedimHauteur=QSpinBox()
        self.spinRedimHauteur.setRange(100, 2048) # 480 par défaut
        grid.addWidget(self.spinRedimHauteur, 2, 1)

        self.curseurRedimHauteur=QSlider(Qt.Horizontal)
        self.curseurRedimHauteur.setRange(100, 2048)
        grid.addWidget(self.curseurRedimHauteur, 2, 2)

        txt1=_(u"Nouvelle hauteur")
        label=QLabel("%s" %txt1)
        grid.addWidget(label, 2, 3)

        vbox.addStretch()
        vbox.addLayout(grid)
        vbox.addStretch()

        #=== sauver configuration ===#

        self.connect(self.spinRedimLargeur,SIGNAL("valueChanged(int)"),self.sauverSpinRedimLargeur)
        self.connect(self.spinRedimHauteur,SIGNAL("valueChanged(int)"),self.sauverSpinRedimHauteur)
        self.connect(self.curseurRedimLargeur,SIGNAL("sliderMoved(int)"),self.curseurRedimLargeurBouge)
        self.connect(self.curseurRedimHauteur,SIGNAL("sliderMoved(int)"),self.curseurRedimHauteurBouge)

        try:
            #print EkdConfig.get(self.idSection,'resolution_redim_largeur')
            EkdPrint(EkdConfig.get(str(self.idSection),' resolution_redim_largeur'))
            self.spinRedimLargeurgg.setValue(int(EkdConfig.get(self.idSection,'resolution_redim_largeur')))
            #print EkdConfig.get(self.idSection,'resolution_redim_hauteur')
            EkdPrint(EkdConfig.get(str(self.idSection),' resolution_redim_hauteur'))
            self.spinRedimHauteur.setValue(int(EkdConfig.get(self.idSection,'resolution_redim_hauteur')))

        except:
	    '''
            print "Pas de paramètres de configuration pour:\n\
            Changement de résolution (nouvelle largeur et/ou nouvelle hauteur)"
            '''
            EkdPrint(u"Pas de paramètres de configuration pour:\nChangement de résolution (nouvelle largeur et/ou nouvelle hauteur)")

    def sauverSpinRedimLargeur(self,i):
        """conserver le spin dans le fichier de configuration et modifier le curseur"""
        #print 'NouvelleLargeur :',i
        EkdPrint(u'NouvelleLargeur : %s' % i)
        EkdConfig.set(self.idSection,'resolution_redim_largeur',i)
        self.curseurRedimLargeur.setValue(i)

    def sauverSpinRedimHauteur(self,i):
        """conserver le spin dans le fichier de configuration et modifier le curseur"""
        #print 'NouvelleHauteur :',i
        EkdPrint(u'NouvelleHauteur : ' % i)
        EkdConfig.set(self.idSection,'resolution_redim_hauteur',i)
        self.curseurRedimHauteur.setValue(i)

    def curseurRedimLargeurBouge(self,i):
        """Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
        self.spinRedimLargeur.setValue(i)

    def curseurRedimHauteurBouge(self,i):
        """Quand on change la position du curseur la valeur du spin est automatiquement modifiée"""
        self.spinRedimHauteur.setValue(i)


class Animation_FiltresVideos(Base_EncodageFiltre):
    # -------------------------------------------------------------------
    # Cadre accueillant les widgets de :
    # Animation >> Filtres videos
    # -------------------------------------------------------------------
    def __init__(self):

        #=== Identifiant de la classe ===#
        self.idSection = "animation_filtresvideo"
                
	# ------------------------------------------------------------------- #
	# Chemin des répertoires temporaires pour la gestion des fichiers
	# mod (extension .mod). Ce sont (apparemment) des fichiers mpeg avec
	# une extension .mod. Les fichiers en question ont juste besoin
	# d'être renommés avec une extension .mpg avant le traitement.
	# ------------------------------------------------------------------- #
	self.repTampon = EkdConfig.getTempDir() + os.sep
	# création des répertoires temporaires
	if os.path.isdir(self.repTampon) is False: os.makedirs(self.repTampon)	
        # Chemin exact d'écriture pour le tampon des fichiers mod
        self.repTempFichiersMod = self.repTampon+'transcodage'+os.sep+'fichiers_mod'+os.sep
	# Création du chemin
	if os.path.isdir(self.repTempFichiersMod) is False: os.makedirs(self.repTempFichiersMod)
	# Epuration/elimination des fichiers tampon contenus dans le rep tampon
	for toutRepTemp in glob.glob(self.repTempFichiersMod+'*.*'): os.remove(toutRepTemp)

        # -------------------------------------------------------------------
        # Widgets intégrés à la boîte de groupe "Choix et affichage des
        # différents filtres". La boîte de combo définie ci-dessus
        # 'sélectionne' ceux qui vont s'afficher -> utilisation d'un stacked
        # -------------------------------------------------------------------

        # === Stacked par défaut - QLabel ================================

        # Apparaît lorsque les entrées suivantes sont sélectionnées dans la
        # boîte de combo: Niveaux de gris (0), Reserve pour sous-titres
        # (Expand) (1) et Miroir (6) .

        # création de stacked pour les QWidget
        self.stacked=QStackedWidget()
        self.stacked.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))

        # par défaut
        self.indexStacked_sansReglages=self.stacked.addWidget(Filtres_SansReglages())


        # === Stacked : "Bruit" ==========================================

        # Apparaît lorsque l'entrée suivante est sélectionnée dans la
        # boîte de combo: Bruit (2) .

        self.filtreBruit = Filtre_Bruit()

        self.indexStacked_bruit=self.stacked.addWidget(self.filtreBruit)


        # === Stacked : "Luminosite-contraste" ===========================

        # Apparaît lorsque l'entrée suivante est sélectionnée dans la
        # boîte de combo: Luminosite-contraste (3) .

        self.filtreLuminosite = Filtre_LuminosContrast()

        self.indexStacked_luminContrast=self.stacked.addWidget(self.filtreLuminosite)


        # === Stacked : "Decouper (Crop)" ================================

        # Apparaît lorsque l'entrée suivante est sélectionnée dans la
        # boîte de combo: Decouper (Crop) (4) .
        # On communique la fonction d'extraction des images de la vidéo au widget de découpe

        self.filtreDecouper = Filtre_Decouper(self.extractionImages)

        self.indexStacked_decouper=self.stacked.addWidget(self.filtreDecouper)
        self.indexStacked_decouperLibre=self.stacked.addWidget(self.filtreDecouper)
        self.connect(self.filtreDecouper, SIGNAL("changerModeDecoupe(QString)"), self.changerTypeDecoupe)


        # === Stacked : "Couleur/Saturation (Hue)" =======================

        # Apparaît lorsque l'entrée suivante est sélectionnée dans la
        # boîte de combo: Couleur/Saturation (Hue) (5) .

        self.filtreCouleurSat = Filtre_CouleurSaturation()
        self.indexStacked_coulSat=self.stacked.addWidget(self.filtreCouleurSat)


        # === Stacked : "Flou boite (Boxblur)" ===========================

        # Apparaît lorsque l'entrée suivante est sélectionnée dans la
        # boîte de combo: Flou boite (Boxblur) (7) .

        self.filtreFlouBoite = Filtre_FlouBoite()
        self.indexStacked_flouBoite=self.stacked.addWidget(self.filtreFlouBoite)


        # === Stacked : "Changement de résolution" ========================

        # Apparaît lorsque l'entrée suivante est sélectionnée dans la
        # boîte de combo: Changement de resolution (8) .

        self.filtreChangResolution = Filtre_ChangResolution()
        self.indexStacked_changResolution=self.stacked.addWidget(self.filtreChangResolution)


        #-------------------------------------------------------------------------------------
        # Paramètres de la liste de combo: [(identifiant, nom entrée, index du stacked),...]
        #-------------------------------------------------------------------------------------

        self.listeCombo=[\
        ('niveaudegris',    _(u'Niveaux de gris'),        self.indexStacked_sansReglages),
        ('placesoustitres',    _(u'Reserve (place) pour sous-titres (Expand)'),
                                    self.indexStacked_sansReglages),
        ('bruit',         _(u'Bruit'),            self.indexStacked_bruit),
        ('luminositecontraste',    _(u'Luminosite-contraste'),    self.indexStacked_luminContrast),
        ('decoupageassiste',    _(u'Decoupage assisté (Crop)'),        self.indexStacked_decouper),
        ('decoupagelibre',    _(u'Decoupage libre (Crop)'),        self.indexStacked_decouperLibre),
        ('couleursaturationhue',_(u'Couleur/Saturation (Hue)'),    self.indexStacked_coulSat),
        ('miroir',        _(u'Miroir horizontal'),    self.indexStacked_sansReglages),
        ('flouboitebloxblur',    _(u'Flou boite (Boxblur)'),    self.indexStacked_flouBoite),
        ('changement_resolution',_(u'Changement de résolution'),self.indexStacked_changResolution),
        ('tournervideo',    _(u'Tourner la vidéo (90 degrés vers la droite)'),self.indexStacked_sansReglages),
        ('desentrelacer',    _(u'Désentrelacer'),self.indexStacked_sansReglages)]

        #---------------------------
        # Dérivation de la classe
        #---------------------------
        Base_EncodageFiltre.__init__(self, titre=_(u"Filtres"))

        # Quand le fichier est chargé et qu'on a pas eu la config,
        # on définie la largeur et la position à la largeur de la
        # moitié de la vidéo
        # On connecte l'action quand le fichier est chargé
        #self.connect(self, SIGNAL("loaded"), self.setDefaultDecoupe) # Supprimé le 16/02/2010

    def setDefaultDecoupe(self): # Fonction non utilisée - correction bug du 16/02/2010
        # Quand le fichier est chargé et qu'on a pas eu la config,
        # on définie la largeur et la position à la largeur de la
        # moitié de la vidéo
        # Principe : On extrait la première image de la vidéo pour avoir la résolution
        # On définit les valeurs correpondantes à la résolution de l'image/2
        #print "Défault découpe : fichier chargé"
        EkdPrint(u"Défault découpe : fichier chargé")

        try:
            self.spinDecoupeL.setValue(int(EkdConfig.get(self.idSection,'decouper_largeur')))
            self.spinDecoupeH.setValue(int(EkdConfig.get(self.idSection,'decouper_hauteur')))
            self.spinPositionL.setValue(int(EkdConfig.get(self.idSection,'decouper_position_largeur')))
            self.spinPositionH.setValue(int(EkdConfig.get(self.idSection,'decouper_position_hauteur')))
        except:
            if self.chemin != None :
                (width, height) = getVideoSize(self.chemin)
                self.filtreDecouper.setWidthHeight(width/4, height/4, width/2, height/2)


    def afficherAide(self):
        """ Boîte de dialogue de l'aide du cadre Animation > Filtres Vidéo """

        super(Animation_FiltresVideos,self).afficherAide(
                _(u"<p><b>Vous pouvez appliquer ici quelques filtres sur les " \
                        u"vidéos. Les possibilités offertes sont assez " \
                        u"différentes les unes des autres. Un aperçu en image " \
                        u"du filtre vous est proposé (dans l'onglet Visionner " \
                        u"Vidéo) avant de faire le traitement final.</b></p>" \
                        u"<p>Dans l'onglet <b>'Vidéo(s) source'</b> cliquez " \
                        u"sur le bouton <b>Ajouter</b>, une boîte de dialogue " \
                        u"apparaît, sur la partie gauche sélectionnez le " \
                        u"répertoire (au besoin dépliez les sous-répertoires), "\
                        u"allez chercher la/les vidéo(s). Si vous voulez " \
                        u"sélectionner plusieurs vidéos d'un coup, maintenez " \
                        u"la touche <b>CTRL</b> (ou <b>SHIFT</b>) du clavier " \
                        u"enfoncée (tout en sélectionnant vos vidéos), " \
                        u"cliquez sur <b>Ajouter</b>.</p><p>Vous pouvez dès " \
                        u"lors sélectionner une vidéo dans la liste et la " \
                        u"visionner (par le bouton juste à la droite de cette" \
                        u"liste), vous noterez que vous pouvez visionner la " \
                        u"vidéo en quatre tiers, en seize neuvième ou avec " \
                        u"les proportions d'origine de la vidéo (w;h). De " \
                        u"même si vous le désirez, vous pouvez obtenir des " \
                        u"informations complètes sur la vidéo sélectionnée, " \
                        u"et ce par le bouton <b>'Infos'</b> (en bas).</p><p>" \
                        u"Dans l'onglet <b>'Réglages'</b> sélectionnez le " \
                        u"filtre de votre choix dans la liste déroulante, " \
                        u"et s'il le faut, faites les réglages qui vous sont " \
                        u"proposés juste en dessous (juste après avoir opéré " \
                        u"le réglage, vous pouvez voir en image le résultat " \
                        u"avant traitement de votre filtre, pour ce faire " \
                        u"cliquez sur le bouton <b>'Aperçu'</b> dans l'onglet " \
                        u"<b>'Visionner vidéo'</b>).</p><p>Une fois tout ceci " \
                        u"fait, cliquez sur le bouton <b>'Appliquer'</b>, " \
                        u"sélectionnez le répertoire de sauvegarde, indiquez " \
                        u"votre <b>'Nom de fichier'</b>, cliquez sur le bouton" \
                        u" <b>'Enregistrer'</b> et attendez le temps de la " \
                        u"conversion. A la fin cliquez sur le bouton <b>'Voir " \
                        u"les informations d'encodage'</b> et fermez cette " \
                        u"dernière fenêtre après avoir vu les informations en " \
                        u"question.</p><p>Dans l'onglet <b>'Visionner vidéo' " \
                        u"</b> vous pouvez visionner le résultat (avant la " \
                        u"conversion) en sélectionnant <b>'vidéo(s) source(s)'" \
                        u"</b>, après la conversion <b>'vidéo convertie'</b> " \
                        u"ou bien encore les deux en même temps, en cliquant " \
                        u"sur le bouton <b>'Comparateur de vidéos'</b>.</p>" \
                        u"<p>L'onglet <b>'Infos'</b> vous permet de voir les " \
                        u"vidéos chargées (avec leurs chemins exacts) avant " \
                        u"et après conversion.</p>"))


    def appliquer(self, nomSortie=None, ouvert=1, tempsApercu=None):
        """appel du moteur de ekd -> filtre"""

        # quel est l'index du dernier item sélectionné de la boîte de combo?
        index=self.combo.currentIndex()
        # Récupération du chemin source
        chemin=unicode(self.getFile())
        
	# suffix du fichier actif
	suffix = os.path.splitext(chemin)[1]
        
        # ------------------------------------------------------------------- #
	# Gestion des fichiers mod (extension .mod). Ce sont (apparemment)
	# des fichiers mpeg avec une extension .mod. Les fichiers en question 
	# ont juste besoin d'être renommés avec une extension .mpg avant le 
	# traitement.
	# ------------------------------------------------------------------- #
	nom_fich_sans_ext = os.path.splitext(os.path.basename(chemin))[0]
	if suffix in ['.mod', '.MOD']:
		# Copie du fichier concerné dans le rep tampon et renommage avec ext .mpg
		shutil.copy(chemin, self.repTempFichiersMod+nom_fich_sans_ext + '.mpg')
		chemin = unicode(self.repTempFichiersMod + nom_fich_sans_ext + '.mpg')
		# L'extension finale est positionnée à .mpg
		suffix = '.mpg'
        
        if not nomSortie:
            # suffix du fichier actif
            #suffix=os.path.splitext(chemin)[1]
            saveDialog = EkdSaveDialog(self, mode="video", suffix=suffix, title=_(u"Sauver"))
            cheminFichierEnregistrerVideo = saveDialog.getFile()

        else: # module séquentiel
            cheminFichierEnregistrerVideo=nomSortie

        if not cheminFichierEnregistrerVideo:
            return

        idCodec=self.listeCombo[index][0]

        # Si le codec a besoin de 2 valeurs de spin -> tuple de spin 2 éléments
        if idCodec == 'bruit':
            # Pour 'bruit', on n'oublie pas de récupérer de type de bruit Luma ou Chroma
            # et on intégre ces valeurs dans un tuple de 3 èlements: (idFiltre, typeLuma, typeChroma)
            spin = (str(self.filtreBruit.spinBruitLuma.value()), str(self.filtreBruit.spinBruitChroma.value()))

            # tuple qui constituera idCodec
            idComboBrouillon = []
            idComboBrouillon.append(idCodec)

            # On récupère l'identifiant explicite du fichier de configuration pour luma et chroma
            # de façon à avoir l'identifiant servant dans la commande de mencoder

            # récupération identifiant luma mencoder
            i = self.filtreBruit.comboLuma.currentIndex()
            idLuma=str(self.filtreBruit.comboLuma.itemData(i).toStringList()[0]) # méthode de QVariant

            for i in self.filtreBruit.listeCombo:
                if i[1]!=idLuma:
                    pass
                else:
                    idComboBrouillon.append(str(i[2]))
	            spin = spin + tuple(str(i[2]))
                    break

            # récupération identifiant chroma mencoder
            i = self.filtreBruit.comboChroma.currentIndex()
            idChroma=str(self.filtreBruit.comboChroma.itemData(i).toStringList()[0]) # méthode de QVariant

            for i in self.filtreBruit.listeCombo:
                if i[1]!=idChroma:
                    pass
                else:
                    idComboBrouillon.append(str(i[2]))
	            spin = spin + tuple(str(i[2]))
                    break

        elif idCodec == 'luminositecontraste':
            spin = (str(self.filtreLuminosite.spinLuminosite.value()),str(self.filtreLuminosite.spinContraste.value()))
        elif idCodec == 'decoupageassiste' or idCodec == 'decoupagelibre':
            # L'affichage ne se faisait pas dans la fenêtre d'Aperçu du filtre vidéo
            # --> c'est maintenant réparé.
            #largeurVid, hauteurVid, log = getVideoSize(chemin)
            largeurVid, hauteurVid = getVideoSize(chemin)
            #debug :
            #print "largeur video : ", largeurVid, "Hauteur video : ", hauteurVid
            EkdPrint(u"largeur video : %s Hauteur vidéo : %s" % (largeurVid, hauteurVid))
            w, h, x, y = self.filtreDecouper.getPos(largeurVid, hauteurVid)
            #print w, h, x, y
            EkdPrint(u"%s %s %s %s" % (w, h, x, y))
            spin = (str(w), str(h), str(x), str(y))
        elif idCodec == 'couleursaturationhue':
            spin = (str(self.filtreCouleurSat.spinCouleur.value()),str(self.filtreCouleurSat.spinSaturation.value()))
        elif idCodec == 'flouboitebloxblur':
            spin = (str(self.filtreFlouBoite.spinFlouBoiteRayon.value()),str(self.filtreFlouBoite.spinFlouBoitePuiss.value()))
        elif idCodec == 'changement_resolution':
            spin = (str(self.filtreChangResolution.spinRedimLargeur.value()),str(self.filtreChangResolution.spinRedimHauteur.value()))
        else: # Pas de valeur de spin pour les filtres 'niveaudegris', 'placesoustitres', 'miroir', 'tournervideo'
            spin = None

        try:
            #print "FILTRE"
            EkdPrint(u"FILTRE")
            mencoder = WidgetMEncoder(idCodec, chemin, cheminFichierEnregistrerVideo,
                      valeurNum = spin, laisserOuvert=ouvert, tempsApercu=tempsApercu)
            mencoder.setWindowTitle(_(u"Filtres vidéo"))
            mencoder.exec_()

        except None:
            return

        if tempsApercu:
            # Création et affichage de l'aperçu
            # On lance l'extraction d'image de la vidéo
            ffmpeg = WidgetFFmpeg('jpeg', cheminFichierEnregistrerVideo, self.repTampon, laisserOuvert=ouvert)
            ffmpeg.exec_()

        else:
            # Activation de widget pour voir le résultat
            self.lstFichiersSortie = cheminFichierEnregistrerVideo # pour la boite de dialogue de comparaison
            self.radioConvert.setChecked(True)
            self.radioSource.setEnabled(True)
            self.radioSource.setChecked(False)
            self.radioConvert.setEnabled(True)
            self.boutCompare.setEnabled(True)
            ### Information à l'utilisateur
            self.infoLog(None, chemin, None, cheminFichierEnregistrerVideo)

            return self.lstFichiersSortie # module séquentiel

    def extractionImages(self):
        """On extrait plusieurs images de la vidéo (qui serviront d'aperçu pour
        les réglages de découpe) dans un répertoire, puis on renvoie la liste de leur adresse
        """

        # Au cas où le répertoire existait déjà et qu'il n'était pas vide -> purge (simple précausion)
        for file in glob.glob(self.repTampon + '*.*'):
            os.remove(file)

        # Répertoire où seront extraites provisoirement les images
        repProv = unicode(self.repTampon + "simpleExtration/")
        # On le supprime s'il existe déjà
        if os.path.isdir(repProv) is True:
            shutil.rmtree(repProv)
        # On le (re)créée
        os.makedirs(repProv)

        # Récupération du chemin de la vidéo source
        cheminVideoEntre=unicode(self.getFile())

        # Détermination de la durée de la vidéo
        tempsTotal, log = getVideoLength(cheminVideoEntre)

        # On extrait une image de la vidéo à chaque intervalle de temps
        # On extrait 12 images
        nbrImg = 12

        # Intervalle de temps
        tempsIntervalle = tempsTotal / nbrImg
        # Boite de dialogue de progression
        progressDialog = QProgressDialog(_(u"Extraction d'images d'aperçu"), _(u"Annuler l'extraction"),
                    0, nbrImg - 1, self)
        progressDialog.setWindowTitle(_(u"EnKoDeur-Mixeur. Fenêtre de progression"))
        progressDialog.show()
        progressDialog.setValue(0)
        QApplication.processEvents()
        for i in range(nbrImg):
            if progressDialog.wasCanceled():
                return
            tps = i * tempsIntervalle
            # Extraction d'une image
            extraireImage(cheminVideoEntre, repProv, str(tps))
            # Nouveau % de progression
            progressDialog.setValue(i)
            QApplication.processEvents()
            # Déplacement de l'image dans un autre répertoire de façon à la renommer comme on veut
            shutil.move(glob.glob(repProv + '*.*')[0],
                    self.repTampon + 'img_' + string.zfill(i + 1, 2) + '.jpg')

        # Suppression du répertoire provisoire
        shutil.rmtree(repProv)
        # Liste des images d'aperçu
        listeImg = []
        for fichier in glob.glob(self.repTampon + '*.*'):
            listeImg.append(fichier)
        listeImg.sort()

        return listeImg

    def apercu(self):
        "Aperçu du filtre en affichant une image convertie"

        # Au cas où le répertoire existait déjà et qu'il n'était pas vide -> purge (simple précausion)
        for toutRepCompo in glob.glob(self.repTampon+'*.*'):
            os.remove(toutRepCompo)

        cheminVideoEntre=unicode(self.chemin)

        # Détermination de la durée de la vidéo
        (tempsTotal, log) = getVideoLength(cheminVideoEntre)

        # Détermination du temps où l'on doit créer l'aperçu
        if self.mplayer.estLue:
            tempsApercu = str(self.mplayer.temps)
        else:
            tempsApercu = str(tempsTotal / 2)

        # On créé l'image d'aperçu
        self.appliquer(nomSortie=self.repTampon + "video", ouvert=0, tempsApercu=tempsApercu)

        # Le bouton 'Revenir' a été ajouté car il permet de fermer proprement la boîte de dialogue
        #
        # On affiche l'image dans une boite de dialogue
        #
        vboxFrame = QVBoxLayout()
        visio = VisionneurImagePourEKD(glob.glob(self.repTampon + '*.png*')[0])
        vboxFrame.addWidget(visio)
        #
        dialog = QDialog(self)
        #
        boutonFermer = QPushButton(_(u"Revenir"))
        boutonFermer.setIcon(QIcon("Icones/revenir.png"))
        self.connect(boutonFermer, SIGNAL('clicked()'), dialog, SLOT('close()'))
        vboxFrame.addWidget(boutonFermer)
        #
        dialog.setWindowTitle(_(u"Aperçu du filtre vidéo"))
        dialog.setLayout(vboxFrame)
        dialog.show()
