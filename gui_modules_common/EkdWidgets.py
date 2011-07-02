#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, SIGNAL, QSize, QVariant, QMetaObject, QString, QDir
from PyQt4.QtCore import QObject, QStringList, QFile, QFileInfo
from PyQt4.QtGui import QFileDialog, QLabel, QPixmap, QPixmapCache, QImage
from PyQt4.QtGui import QImageReader, QDialog, QVBoxLayout, QHBoxLayout
from PyQt4.QtGui import QSpacerItem, QColor, QProgressBar, QTextEdit, QPalette
from PyQt4.QtGui import QBrush, QSizePolicy, QPushButton, QFrame, QCheckBox
from PyQt4.QtGui import QLayout, QListWidget, QStackedLayout, QLineEdit
from PyQt4.QtGui import QScrollArea, QGridLayout, QGroupBox, QComboBox
from PyQt4.QtGui import QSpinBox, QColorDialog, QColor, QIcon, QDirModel
from PyQt4.QtGui import QListView, QTreeView, QLineEdit, QInputDialog
from PyQt4.QtGui import QMessageBox, QCompleter, QStandardItem
from PyQt4.QtGui import QStandardItemModel, QDoubleSpinBox
import webbrowser, locale, os

from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdTools import debug

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

'''
Package crée pour simplifier la gestion des widgets spécifiques à Ekd
'''

class EkdMessage(QDialog):
    '''
    EkdMessage : Classe représentant une boite de dialogue avec un texte,
    des bouton et une icone permettant d'avertir l'utilisateur
    '''
    def __init__(self, titre, texte="", min_w=320, min_h=250, max_w=500,
                    max_h=600, icone="Icones/messagebox_info.png",
                    checkbox=False, parent=None):
        """Boite de message standard pour ekd.
           Usage :
             1. initialisation en spécifiant la taille, le titre et
                éventuellement le texte de la fenêtre.
                l'icone est également paramétrable
             2. Ajout du text avec la fonction setAideText.
             3. Affichage de la fenêtre en appelant la fonction show().
           Facilité :
             1. Redimensionnement de la fenêtre par appel de la fonction
                setSize(w, h)
             2. Ajout automatique des bars de défilement."""
        super(EkdMessage, self).__init__(parent)
        self.setWindowTitle(titre)
        self.setMaximumHeight(max_h)
        self.setMaximumWidth(max_w)
        self.setMinimumHeight(min_h)
        self.setMinimumWidth(min_w)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)

        self.w = min_w
        self.h = min_h
        self.verticalLayout = QVBoxLayout(self)
        self.hbox1 = QHBoxLayout()
        self.vbox1 = QVBoxLayout()

        # Icone
        self.iconeI = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                    self.iconeI.sizePolicy().hasHeightForWidth())
        self.iconeI.setSizePolicy(sizePolicy)
        self.iconeI.setPixmap(QPixmap(icone))
        self.vbox1.addWidget(self.iconeI)
        spacerItem = QSpacerItem(20, 40,
                                QSizePolicy.Minimum,
                                QSizePolicy.Expanding)
        self.vbox1.addItem(spacerItem)
        self.hbox1.addLayout(self.vbox1)
        ##

        # Definition de la zone de texte
        self.text = QTextEdit(self)

        ## On utilise le même thème que la fenêtre pour la zone de texte
        ## On force les couleur ici, on ne laisse pas le Thème s'en charger
        palette = self.text.palette()
        palette.setBrush(QPalette.Active,
                            QPalette.Base,
                            self.palette().window())
        palette.setBrush(QPalette.Inactive,
                            QPalette.Base,
                            self.palette().window())
        palette.setBrush(QPalette.Disabled,
                            QPalette.Base,
                            self.palette().window())
        palette.setBrush(QPalette.Active,
                            QPalette.Text,
                            self.palette().windowText())
        palette.setBrush(QPalette.Inactive,
                            QPalette.Text,
                            self.palette().windowText())
        palette.setBrush(QPalette.Disabled,
                            QPalette.Text,
                            self.palette().windowText())
        self.text.setPalette(palette)

        self.text.setFrameShape(QFrame.NoFrame)
        self.text.setFrameShadow(QFrame.Plain)
        self.text.setLineWidth(0)
        self.text.setReadOnly(True)
        self.text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text.sizePolicy().hasHeightForWidth())
        self.text.setSizePolicy(sizePolicy)
        self.hbox1.addWidget(self.text)
        ##

        self.verticalLayout.addLayout(self.hbox1)
        self.hbox2 = QHBoxLayout()
        self.ok = QPushButton(self)
        self.ok.setText(_("Ok"))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ok.sizePolicy().hasHeightForWidth())
        self.ok.setSizePolicy(sizePolicy)
        self.hbox2.addWidget(self.ok)
        self.verticalLayout.addLayout(self.hbox2)
        self.setText(texte)

        '''
        Checkbox pour savoir si l'utilisateur veut oui ou non revoir
        l'avertissement
        '''
        if checkbox :
            self.checkbox = QCheckBox(_(u"Voir ce message la prochaine fois"),
                                        self)
            self.hbox2.addWidget(self.checkbox)
            try :
                self.checkbox.setCheckState(int(EkdConfig.get("general",
                                                    "show_warning_messages")))
            except Exception, e:
                #print "First time launched"
		EkdPrint(u"First time launched")
            self.connect(self.checkbox, SIGNAL("stateChanged(int)"),
                                                    self.setDontShow)

        self.connect(self.ok, SIGNAL("clicked()"), self.close)

    def setText(self, text) :
        self.text.setHtml(text)


    def setSize(self,w,h) :
        self.h = h
        self.w = w
        self.resize(w,h)

    def setDontShow(self, state):
        EkdConfig.set("general", "show_warning_messages", state)

class EkdSaveDialog(QDialog):
    '''
    EkdSaveDialog : Classe représentant la boite de dialogue utiliser lors de
                    l'enregistrement des modification sur un fichier donné
        attributs : suffix   - Suffix utilisé en filtre
                    filter   - Filtre (déduit à partir du suffix)
                    chemin   - Chemin du dernier fichier enregistré
                    multiple - va-t-on enregistrer plus d'un fichier ?
                                (ex: extraction d'image d'une vidéo)
        méthodes  : getFile - Invoque la boite de dialogue et retourne
                    le fichier saisi
    '''
    ### Pourquoi avoir réimplémenté cette classe au lieu de passer par
    ### QFileDialog ?
    ## Correction du bug de consommation mémoire
    ##
    ##  Explication du problème :
    ##   Par défaut un QFileDialog utilise un QFileSystemModel qui lui
    ##   crée un QWatchFileSystem
    ##   Hors QWatchFileSystem scan régulièrement les changement
    ##   dans le répertoire courant
    ##   Ce phénomène provoque une réaction en chaine :
    ##     1 - je choisi mon répertoire de destination d'enregistrement
    ##         de mes images
    ##     2 - ffmpeg se lance
    ##     3 - ffmpeg crée un fichier dans l'arborescence
    ##     4 - QWatchFileSystem (est toujours dans le répertoire courant)
    ##         détecte un changement
    ##         et recharge l'ensemble du contenue du répertoire
    ##     5 - goto 3 jusqu'à plus de mémoire ou fin du process ffmpeg
    ##
    ##

    def __init__(self, parent, path = None, suffix = '', title = u"Sauver",
                                            multiple = False, mode = None):

        if type(suffix) == tuple or type(suffix) == list :
            sfilter=""
            for s in suffix :
                sfilter += "*"+s+" "
            self.filter=sfilter[:-1]
            # Si on a plusieur suffix, on prend le premier par défaut pour
            # la sauvegarde
            self.suffix = suffix[0]
        else :
            self.suffix = suffix
            self.filter = "*" + self.suffix

        QDialog.__init__(self, parent)

        self.setWindowTitle(title)
        self.multiple = multiple
        self.mode = mode

        if not path:
            if self.mode == "image" :
                path = EkdConfig.get("general", "image_output_path")
            elif self.mode == "video" :
                path = EkdConfig.get("general", "video_output_path")
            elif self.mode == "audio" :
                path = EkdConfig.get("general", "sound_output_path")
            else :
                path = unicode(QDir.homePath())

        # Nom du répertoire courant
        self.location = QLabel("<b>%s</b>" % path)
        # Variable permettant de savoir à tout moment le répertoire courant.
        self.currentDir = path
        self.mkdirButton = QPushButton(u"  Créer un répertoire")
        self.mkdirButton.setIcon(QIcon("Icones" + os.sep + "add_sub_task.png"))
        if int(EkdConfig.get("general", "show_hidden_files")) :
            #print "hidden shown"
	    EkdPrint(u"hidden shown")
            shf = QDir.Hidden
        else : shf = QDir.Readable
        # Liste des fichiers
        self.dirList = QListView()
        sorting = QDir.DirsFirst
        if int(EkdConfig.get("general", "ignore_case")):
            sorting |= QDir.IgnoreCase
        self.sorting = sorting
        self.flags = QDir.Files | QDir.Readable | shf
        self.dirModel = QStandardItemModel()
        self.dirList.setModel(self.dirModel)
        self.updateDir(path)
        self.dirList.setWrapping(True)

        #panneau latéral
        self.dirTree = QTreeView()
        self.dirModelLight = QDirModel(QStringList(""), QDir.AllDirs |
                                    QDir.NoDotAndDotDot | shf, QDir.DirsFirst |
                                    QDir.Name | QDir.IgnoreCase)
        self.dirTree.setModel(self.dirModelLight)
        self.dirTree.setColumnHidden(1,True)
        self.dirTree.setColumnHidden(2,True)
        self.dirTree.setColumnHidden(3,True)
        self.dirTree.setMaximumWidth(200)
        self.dirTree.setMinimumWidth(150)
        self.dirTree.setCurrentIndex(self.dirModelLight.index(path))
        self.dirTree.resizeColumnToContents(0)
        self.connect(self.dirTree, SIGNAL("pressed(QModelIndex)"),
                                                    self.updateLatDir)
        self.connect(self.dirTree, SIGNAL("expanded(QModelIndex)"),
                                                        self.treeMAJ)
        self.connect(self.dirTree, SIGNAL("collapsed(QModelIndex)"),
                                                        self.treeMAJ)

        # Nom du fichier
        self.fileField = QLineEdit()

        # Nom du filtre
        self.filterField = QComboBox()
        self.filterField.addItems(QStringList(self.filter))

        # Bouton de sauvegarde et d'annulation
        self.saveButton = QPushButton(_(u"  Enregistrer"))
        self.saveButton.setIcon(QIcon("Icones" + os.sep + "action.png"))
        self.cancelButton = QPushButton(_(u"  Annuler"))
        self.cancelButton.setIcon(QIcon("Icones" + os.sep + "annuler.png"))

        # Organisation des différents objets de la boite de dialogue
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.dirTree)
        self.filelinelayout = QGridLayout()
        self.filelinelayout.addWidget(self.location, 0, 0, 1, 0)
        self.filelinelayout.addWidget(self.mkdirButton, 0, 2)
        self.filelinelayout.addWidget(self.dirList, 1, 0, 1, 0)
        self.filelinelayout.addWidget(QLabel(_("Nom de fichier : ")), 2, 0)
        self.filelinelayout.addWidget(self.fileField, 2, 1)
        self.filelinelayout.addWidget(self.saveButton, 2, 2)
        self.filelinelayout.addWidget(QLabel(_("Filtre extension : ")), 3, 0)
        self.filelinelayout.addWidget(self.filterField, 3, 1)
        self.filelinelayout.addWidget(self.cancelButton, 3, 2)

        self.layout.addLayout(self.filelinelayout)

        # Connexion des différents objets
        self.connect(self.dirList, SIGNAL("clicked(QModelIndex)"),
                                                        self.updateFile)
        self.connect(self.saveButton, SIGNAL("clicked()"), self.accept)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.reject)
        self.connect(self.mkdirButton, SIGNAL("clicked()"), self.mkdir)
        self.connect(self.dirList,
                    SIGNAL("indexesMoved (const QModelIndexList&)"),
                    self.updateFile)
        self.connect(self.fileField, SIGNAL("textChanged (const QString&)"),
                    self.activate)
        self.connect(self.fileField, SIGNAL("returnPressed()"), self.accept)

        # Taille minimum
        self.setMinimumSize(700, 480)

        # Par défaut, on désactive
        self.deactivate()

        # Completion des fichiers
        self.completion = QCompleter(self.dirModel, self.dirList)

    def updateLatDir(self, item) :
        """ Fonction permettant de naviguer dans la listes des répertoires """
        self.updateDir(self.dirModelLight.filePath(item))

    def treeMAJ(self, item) :
        self.dirTree.resizeColumnToContents(0)

    def activate(self, filename=None):
        """ Activation des boutton de sauvegarde """
        self.dirList.clearSelection()
        if filename != "":
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def deactivate(self):
        """ Désactivation des boutton de sauvegarde """
        self.saveButton.setEnabled(False)

    def updateDir(self, path = None):
        """ Fonction permettant de naviguer dans la listes des répertoires """

        if path :
            self.currentDir = path
            self.location.setText("<b>%s</b>" % path)
        self.dirModel.clear()
        self.tmpdir = QDir()
        self.tmpdir.setPath(self.currentDir)
        self.tmpdir.setNameFilters(QStringList(self.filter))

        # Une icône pour les images, un autre icône pour les vidéos, et
        # une pour audio
        if self.mode == "image" :
            icone = QIcon("Icones" + os.sep + "image_image.png")
        elif self.mode == "video" :
            icone = QIcon("Icones" + os.sep + "image_video.png")
        elif self.mode == "audio" :
            icone = QIcon("Icones" + os.sep + "image_audio.png")
        else:
            icone = QIcon("Icones" + os.sep + "image_default.png")

        for wlfile in self.tmpdir.entryList(QDir.Files):
            if self.mode == "image" :
                icone = QIcon(EkdPreview("Icones" + os.sep + "image_default.png").get_preview())
            item = QStandardItem(icone, QString(wlfile))
            item.setToolTip(wlfile)
            item.setData(QVariant(self.tmpdir.absolutePath() + os.sep + wlfile), Qt.UserRole + 2)
            item.setData(QVariant(wlfile), Qt.UserRole + 3)
            self.dirModel.appendRow(item)


    def updateFile(self, item):
        """ Fonction appelée par la listView lors d'un changement de repertoire"""
        # On récupère le QModel parent du QModelItem
        path = "%s" % item.data(Qt.UserRole + 2).toString()
        name = os.path.basename(path)
        self.fileField.selectAll()
        self.fileField.setFocus()
        self.fileField.setText(name)
        self.activate(name)

    def selectedFile(self):
        """ Renvoi le fichier selectionné pour la sauvegarde"""
        # Récupération du fichier selectionné
        fichier = self.fileField.text()
        output = "%s%s%s" % (self.currentDir, os.sep, fichier)
        info = QFileInfo(output)
        # Si l'utilisateur n'a pas spécifié de suffix, on l'ajoute
        if info.suffix() != self.suffix[1:]:
            output = "%s%s" % (output, self.suffix)
        return output

    def mkdir(self):
        """ Crée un répertoire dans le répertoire courant """
        (dirname, ok) = QInputDialog.getText(self, _(u"Nouveau répertoire"), _(u"Nom du répertoire"), QLineEdit.Normal, _(u"Nouveau répertoire"))
        if ok :
            try :
                os.mkdir("%s%s%s" % (self.currentDir, os.sep,dirname))
                #print u"Création de : %s%s%s" % (self.currentDir, os.sep, dirname)
		EkdPrint(u"Création de : %s%s%s" % (self.currentDir, os.sep, dirname))
                self.updateDir()
                self.dirModelLight.refresh()
            except Exception, e:
                #print _(u"Impossible de crée un nouveau répertoire : %s" % e)
		EkdPrint(_(u"Impossible de crée un nouveau répertoire : %s" % e))

    def getFile(self):
        '''
        Invoque la boite de dialogue et retourne le fichier saisi
        '''
        ## Ajout d'une boite de dialogue avertissant du format des fichier de sortis dans le cas de multiples fichier à enregistrer
        show = Qt.Unchecked
        try :
            show = int(EkdConfig.get("general", "show_warning_messages"))
        except Exception, e:
            #print "%s" % e
	    EkdPrint("%s" % e)
            pass
        if (self.multiple and (show != Qt.Unchecked)):
            warning = EkdMessage(_(u"Attention"), icone="Icones/messagebox_info.png", min_w=320, min_h=200, checkbox=True, parent=self)
            warning.setText(_(u"<p>Attention, les fichiers enregistrés seront de la forme : fichier_00000X")+ self.suffix +"</p>"+
                                   _(u"<p><b>Tous les fichiers</b> ayant le même nom seront écrasés.</p>"))
            warning.exec_()
        ######

        self.chemin = None
        ok = None
        while ok != QMessageBox.Ok:
            ok = QMessageBox.Ok
            if self.exec_():
                self.chemin = unicode(self.selectedFile())
                if QFile.exists(self.chemin) and (not self.multiple):
                    ok = QMessageBox.warning(self, _(u"Attention"), _(u"Le fichier existe, voulez-vous écraser le fichier existant ?"), QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            else :
                return None

        ## On met à jour les chemins d'enregistrement
        if self.mode == "image" :
            EkdConfig.set("general", "image_output_path", os.path.dirname(self.chemin))
        elif self.mode == "video" :
            EkdConfig.set("general", "video_output_path", os.path.dirname(self.chemin))
        elif self.mode == "audio" :
            EkdConfig.set("general", "sound_output_path", os.path.dirname(self.chemin))

        debug('EkdSaveDialog:: Suffix : %s Filename : %s' % (self.suffix, self.chemin))
        return self.chemin

    def setAcceptMode(self, mode=QFileDialog.AcceptSave):
        """ Défini le mode d'ouvertue Ouverture ou Sauvegarde """
        self.mode = mode
        if self.mode == QFileDialog.AcceptSave :
            self.saveButton.setText(_(u"Enregistrer"))
        elif self.mode == QFileDialog.AcceptOpen :
            self.saveButton.setText(_(u"Ouvrir"))
            self.fileField.setReadOnly(True)


class EkdOpenDialog(EkdSaveDialog):
    '''
    EkdSaveDialog : Classe représentant la boite de dialogue utiliser lors de l'ouverture de fichier
    '''
    def __init__(self, parent, path=None, suffix='', title=u"Ouvrir", multiple=False):
        EkdSaveDialog.__init__(self, parent, path=path, suffix=suffix, title=title, multiple=multiple)
        self.setAcceptMode(QFileDialog.AcceptOpen)

    def getFile(self):
        '''
        Invoque la boite de dialogue et retourne le(s) fichier(s) saisi(s)
        '''
        self.chemin = None
        if self.exec_():
            if self.multiple :
                ### FIXME : La gestion de l'ouverture multiple est à gérer
                self.chemin = unicode(self.selectedFiles())
            else:
                self.chemin = unicode(self.selectedFile())
        #print 'EkdOpenDialog:: Suffix : ' , self.suffix, "Filename : ", self.chemin
	EkdPrint(u'EkdOpenDialog:: Suffix : %s Filename : %s' % (self.suffix, self.chemin))
        return self.chemin


class EkdLabel(QLabel):
        '''
        Chaîne de caractères ayant un comportement hyper-texte
        Pour toute intéraction avec ce label, il suffit de le connecter avec un fonction dédié sur le signal "click"

        '''
        def __init__(self, texte, url=None):
            QLabel.__init__(self)
            self.setText("<font color='blue'><center>%s</center></font>" %texte)
            # le pointeur de la souris change au survol du label
            self.setCursor(Qt.PointingHandCursor)
            self.url=url

        def mousePressEvent(self, event):
            '''
                Émission d'un signal click quand le label est cliqué
            '''
            self.emit(SIGNAL("click"))
            if self.url != None :
                webbrowser.open(self.url)


class EkdPreview():
    """ On gère un cache des Pixmap générés
    La méthode est simple : au lieu de charger toute l'image et d'en faire une préview après
    on génère la préview au chargement de l'image. On est ainsi moins dépendant de la taille
    de l'image à prévisualiser
    Pour faire ça, on utilise le QImageReader
    On utilise également la fonction de cache pour éviter d'avoir à regénérer à chaque fois les
    apperçus"""
    def __init__(self, imagePath, width=64, height=0, quality=0, Cache=True, keepRatio=True, magnify=False):
        """
        imagePath : chemin de l'image a charger
        size : taille de la préview a générer
        quality : qualité de la preview (0=mavaise, 10=très bonne)
        keepRation : garde-t-on les proportion de l'image
        magnify : agrandit-on l'image si la preview demandée est plus grande que l'image originale
        """
        self.preview = QPixmap()
        if width == 0:
            width = 64
        if height == 0:
            height = width
        self.size = QSize(width, height)
        self.quality = quality
        self.imageName = imagePath
        self.keepRatio = keepRatio
        self.magnify = magnify
        self.cache = Cache
        QPixmapCache.setCacheLimit(50*1024)
        self.update()

    def get_preview(self):
        return self.preview

    def toggle_keepRatio(self):
        self.keepRatio = not self.keepRatio

    def get_image(self):
        return self.preview.toImage()

    def get_imageName(self):
        return self.imageName

    def set_imageName(self, path):
        self.imageName = path

    def get_size(self):
        return self.size

    def set_size(self, size):
        self.size = size

    def get_quality(self):
        return self.quality

    def set_quality(self, quality):
        self.quality = quality

    def width(self):
        return self.preview.width()

    def height(self):
        return self.preview.height()

    def origin(self):
        old_keepRatio=self.keepRatio
        self.keepRatio=False
        self.set_size(self.origineSize)
        self.update()
        self.keepRatio=old_keepRatio

    def update(self):
        """ Fonction de mise à jour de la préview :
            * Si la taille de l'image est plus petite que la taille souhaité, on n'agrandi pas l'image, on prend la plus petite des deux
            * Le cache contient en index les images+size"""
        miniImg = QImage()
        image = QImageReader(self.imageName)
        self.origineSize = image.size()
        image.setQuality(self.quality)
        if not self.magnify :
            if ( ( self.size.width() + self.size.height() ) > (image.size().width() + image.size().height() ) ) :
                self.size = image.size()

        if self.keepRatio :
            image.setScaledSize(QSize(self.size.width(), image.size().height() * self.size.width() / image.size().width() ) )
        else :
            image.setScaledSize(self.size)

        if not QPixmapCache.find(self.imageName + str(self.size), self.preview) or not self.cache:
            image.read(miniImg)
            self.preview = self.preview.fromImage(miniImg)
            if self.cache :
                QPixmapCache.insert(self.imageName + str(self.size), self.preview)

class EkdProgress(QDialog) :
    """EkdProgress est une boite de dialog contenant l'état de la progression de chaque processus"""

    def __init__(self, parent=None, totfile=0):
        super(EkdProgress, self).__init__(parent)
        self.setupUi(self)
        self.barProgress.setMaximum(totfile)
        self.fermer.setEnabled(False)
        self.totframe=totfile
        self.value = 0
        self.connect(self.fermer,SIGNAL("clicked()"),self.tmpclose)

    def upProgress(self) :
        self.value += 1
        self.barProgress.setValue(self.value)

    def addText(self, text) :
        self.infoText.append(QString(text))

    def tmpclose(self) :
        self.emit(SIGNAL("cleantmp"))
        self.close()

    def setupUi(self, showprogress):
        showprogress.setObjectName("showprogress")
        showprogress.resize(335, 310)
        self.verticalLayout = QVBoxLayout(showprogress)
        self.verticalLayout.setObjectName("verticalLayout")
        self.barProgress = QProgressBar(showprogress)
        self.barProgress.setProperty("value", QVariant(0))
        self.barProgress.setObjectName("barProgress")
        self.verticalLayout.addWidget(self.barProgress)
        self.infoText = QTextEdit(showprogress)
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(126, 125, 124))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        self.infoText.setPalette(palette)
        self.infoText.setObjectName("infoText")
        self.verticalLayout.addWidget(self.infoText)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.fermer = QPushButton(showprogress)
        self.fermer.setObjectName("fermer")
        self.horizontalLayout.addWidget(self.fermer)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(showprogress)
        QMetaObject.connectSlotsByName(showprogress)

    def retranslateUi(self, showprogress):
        showprogress.setWindowTitle(_(u"Progression"))
        self.barProgress.setToolTip(_(u"Progression de l\'encodage"))
        self.infoText.setToolTip(_(u"Messages"))
        self.fermer.setToolTip(_(u"Fermer la fenêtre"))
        self.fermer.setText(_(u"Fermer"))

class EkdAide(EkdMessage) :
    """EkdAide est une boite de dialog contenant l'aide contextuelle lors de l'action sur
    les boutons "Aide" présents dans chaque module"""
    def __init__(self, w=500, h=600, parent=None):
        """Boite d'aide standard pour ekd.
           Usage :
             1. initialisation en spécifiant la taille de la fenêtre.
             2. Ajout du text avec la fonction setAideText.
             3. Affichage de la fenêtre en appelant la fonction show().
           Facilité :
             1. Redimensionnement de la fenêtre par appel de la fonction setSize(w, h)
             2. Ajout automatique des bars de défilement."""
        super(EkdAide, self).__init__(titre=_(u"Aide"), icone="Icones/messagebox_info.png", min_w=700, max_w=w, max_h=h, parent=parent)

    def setAideText(self, text) :
        self.text.setText(text)


### Boite de réglage de la configuration Ekd
class EkdConfigBox(QDialog) :
    """
    EkdConfigBox permet à l'utilisateur de configurer EkdConfig
    """
    def __init__(self, w=550, h=480, titre=u"Configuration de Ekd", parent=None):
        super(EkdConfigBox, self).__init__(parent)
        self.resize(w,h)
        self.w = w
        self.h = h
        self.setWindowTitle(titre)

        self.layout = QVBoxLayout(self)
        ## Menu contient l'ensemble des sections à paramétrer
        self.menu = QListWidget(self)
        self.layout.addWidget(self.menu)
        ## Pour chaque section à paramétrer, on utilise un Stack d'objets
        self.leftpart = QStackedLayout()
        self.leftpart.setSizeConstraint(QLayout.SetNoConstraint)
        self.layout.addLayout(self.leftpart)

        ## propWidget contient l'ensemble des objets propriété de toutes les section
        ## (il est nécessaire de les stocker pour être capable de les faire interagir)
        self.propWidget=[]
        wid = 0

        ## On crée les différentes parties de configuration qui ne sont pas inclues dans le tableau SECTION_MASK de EkdConfig
        for section in EkdConfig.SECTIONS :
            if not section in EkdConfig.SECTION_MASK :
                self.menu.addItem(EkdConfig.SECTIONS[section])
                allprops = EkdConfig.getAllProperties(EkdConfig.getConfigSection(section))
                scroll = QScrollArea()
                frame = QFrame()
                frame.setMinimumSize(self.w-50, self.h/2) # Ajouté le 10/12/2009 Pour que la partie réglage prenne toute la place dispo.
                frame.setMaximumSize(self.w, self.h)
                linelayout = QGridLayout(frame)

                linelayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
                row = 0
                ## Insertion des propriété de la section en fonction de son type
                allkeys = allprops.keys()
                found = False
                for prop in allkeys :
                    if not prop in EkdConfig.PROPERTIES_MASK :
                        if prop in EkdConfig.PATH_PROPERTIES :
                            self.propWidget.append( EkdPathPropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], section=section) )
                            linelayout.addWidget(self.propWidget[wid].label, row, 0)
                            linelayout.addWidget(self.propWidget[wid].widget, row, 1)
                            wid += 1
                            found = True
                        row += 1
                for prop in allkeys :
                    if not prop in EkdConfig.PROPERTIES_MASK :
                        if prop in EkdConfig.STYLE_PROPERTIES :
                            self.propWidget.append( EkdStylePropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], EkdConfig.STYLE_PROPERTIES[prop], section=section ) )
                            linelayout.addWidget(self.propWidget[wid].label, row, 0)
                            linelayout.addWidget(self.propWidget[wid].widget, row, 1)
                            wid += 1
                            found = True
                        row += 1
                for prop in allkeys :
                    if not prop in EkdConfig.PROPERTIES_MASK :
                        if prop in EkdConfig.CODEC_PROPERTIES :
                            self.propWidget.append( EkdCodecPropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], EkdConfig.CODEC_PROPERTIES[prop], section=section ) )
                            linelayout.addWidget(self.propWidget[wid].label, row, 0)
                            linelayout.addWidget(self.propWidget[wid].widget, row, 1)
                            wid += 1
                            found = True
                        row += 1
                for prop in allkeys :
                    if not prop in EkdConfig.PROPERTIES_MASK :
                        if prop in EkdConfig.BOOLEAN_PROPERTIES :
                            self.propWidget.append( EkdBoolPropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], section=section) )
                            linelayout.addWidget(self.propWidget[wid].widget, row, 0, 1, 2)
                            wid += 1
                            found = True
                        row += 1
                for prop in allkeys :
                    if not prop in EkdConfig.PROPERTIES_MASK :
                        if prop in EkdConfig.NUM_PROPERTIES :
                            self.propWidget.append( EkdNumPropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], section=section) )
                            linelayout.addWidget(self.propWidget[wid].label, row, 0)
                            linelayout.addWidget(self.propWidget[wid].widget, row, 1)
                            wid += 1
                            found = True
                        row += 1
                for prop in allkeys :
                    if not prop in EkdConfig.PROPERTIES_MASK :
                        if prop in EkdConfig.TIME_PROPERTIES :
                            self.propWidget.append( EkdTimePropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], section=section) )
                            linelayout.addWidget(self.propWidget[wid].label, row, 0)
                            linelayout.addWidget(self.propWidget[wid].widget, row, 1)
                            wid += 1
                            found = True
                        row += 1
                for prop in allkeys :
                    if not prop in EkdConfig.PROPERTIES_MASK :
                        if prop in EkdConfig.COLOR_PROPERTIES :
                            self.propWidget.append( EkdColorPropertie(prop, EkdConfig.PROPERTIES[prop], allprops[prop], section=section) )
                            linelayout.addWidget(self.propWidget[wid].label, row, 0)
                            linelayout.addWidget(self.propWidget[wid].widget, row, 1)
                            wid += 1
                            found = True
                        elif not found:
                            line = QLineEdit(allprops[prop])
                            linelayout.addWidget(QLabel(prop), row, 0)
                            linelayout.addWidget(line, row, 1)
                        row += 1

                frame.setLineWidth(0)
                scroll.setWidget(frame)
                self.leftpart.addWidget(scroll)

        self.menu.setAlternatingRowColors(True)
        # Define the size of the list depending of its content
        self.menu.setFixedHeight(( self.menu.sizeHintForRow(0) + self.menu.verticalStepsPerItem() + 1)* self.menu.count())
        self.menu.updateGeometries()

        ## Boutton pour  fermer la boite de dialogue
        self.fermer = QPushButton(_(u"Fermer"))
        self.layout.addWidget(self.fermer)

        ## Lorsqu'on clique sur fermer, la fenêtre se ferme
        self.connect(self.fermer, SIGNAL("clicked()"), self.close)

        ## Lorsqu'on selectionne un élément du menu, on met à jour la partie droite du menu
        self.connect(self.menu, SIGNAL("currentItemChanged(QListWidgetItem *,QListWidgetItem *)"), self.updateMenu)

    def updateMenu(self):
        propriete = self.menu.currentRow()
        self.leftpart.setCurrentIndex(propriete)

class EkdPropertie(QObject) :
    """
    Objet maitre contenant les attributs de base d'une propriété Ekd
    """
    ## Définition des différents types de propriété
    PATH, NUM, STYLE, CODEC, BOOL, COLOR, TIME = range(0,7)
    def __init__(self, prop, name, value, propType, propSection):
        super(EkdPropertie, self).__init__()
        self.id = prop
        self.label = None
        self.name = name
        self.value = value
        self.type = propType
        self.section = propSection

class EkdBoolPropertie(EkdPropertie):
    """
    Définition de la propriété correspondant à un Booléen
    """
    def __init__(self, prop, name, value, section=None):
        super(EkdBoolPropertie, self).__init__(prop, name, value, EkdPropertie.BOOL, section)
        self.widget = QCheckBox(name)
        if int(self.value) != Qt.Unchecked :
            self.widget.setChecked(True)

        # Quand on change la valeur de la propriété, on met à jour EkdConfig
        self.connect(self.widget, SIGNAL("stateChanged(int)"), self.updateState)

    def updateState(self):
        self.value = self.widget.checkState()
        EkdConfig.set(self.section, self.id, self.value)

class EkdNumPropertie(EkdPropertie):
    """
    Définition de la propriété correspondant à un conteur ou une valeur numérique
    """
    def __init__(self, prop, name, value, minimum=0, maximum=100, section=None ):
        super(EkdNumPropertie, self).__init__(prop, name, value, EkdPropertie.NUM, section)
        self.label = QLabel(name)
        self.widget = QSpinBox()
        self.widget.setValue(int(value))
        self.widget.setMaximum(maximum)
        self.widget.setMinimum(minimum)

        # Quand on change la valeur de la propriété, on met à jour EkdConfig
        self.connect(self.widget, SIGNAL("valueChanged(int)"), self.updateNum)

    def updateNum(self, val):
        self.value = val
        EkdConfig.set(self.section, self.id, self.value)

class EkdTimePropertie(EkdPropertie):
    """
    Définition de la propriété correspondant à un conteur ou une valeur de temps
    """
    def __init__(self, prop, name, value, minimum=0, maximum=100, section=None ):
        super(EkdTimePropertie, self).__init__(prop, name, value, EkdPropertie.TIME, section)
        self.label = QLabel(name)
        self.widget = QDoubleSpinBox()
        self.widget.setValue(float(value))
        self.widget.setMaximum(maximum)
        self.widget.setMinimum(minimum)

        # Quand on change la valeur de la propriété, on met à jour EkdConfig
        self.connect(self.widget, SIGNAL("valueChanged(double)"), self.updateNum)

    def updateNum(self, val):
        self.value = val
        EkdConfig.set(self.section, self.id, self.value)
        #print "Debug:: TIMER %s | value %s | value Ekd config %s | section %s" % (self.id, self.value, EkdConfig.get(self.section, self.id), self.section)
	EkdPrint(u"Debug:: TIMER %s | value %s | value Ekd config %s | section %s" % (self.id, self.value, EkdConfig.get(self.section, self.id), self.section))

class EkdStylePropertie(EkdPropertie):
    """
    Définition de la propriété correspondant à un QStyle
    """
    def __init__(self, prop, name, value, choices=[], section=None ):
        super(EkdStylePropertie, self).__init__(prop, name, value, EkdPropertie.STYLE, section)
        self.label = QLabel(name)
        self.widget = QComboBox()
        self.widget.addItems(choices)
        self.widget.setCurrentIndex(self.widget.findText(value))

        # Quand on change de codec, on met à jour EkdConfig
        self.connect(self.widget, SIGNAL("currentIndexChanged(int)"), self.updateStyle)

    def updateStyle(self):
        self.value = self.widget.currentText()
        EkdConfig.set(self.section, self.id, self.value)

class EkdCodecPropertie(EkdPropertie):
    """
    Définition de la propriété correspondant à un Codec
    """
    def __init__(self, prop, name, value, choices=[], section=None ):
        super(EkdCodecPropertie, self).__init__(prop, name, value, EkdPropertie.CODEC, section)
        self.label = QLabel(name)
        self.widget = QComboBox()
        self.widget.addItems(choices)
        self.value = value
        self.widget.setCurrentIndex(int(value))

        # Quand on change de codec, on met à jour EkdConfig
        self.connect(self.widget, SIGNAL("currentIndexChanged(int)"), self.updateCodec)

    def updateCodec(self):
        self.value = self.widget.currentIndex()
        EkdConfig.set(self.section, self.id, self.value)


class EkdPathPropertie(EkdPropertie):
    """
    Définition de la propriété correspondant à un chemin
    """
    def __init__(self, prop, name, value, section=None ):
        super(EkdPathPropertie, self).__init__(prop, name, value, EkdPropertie.PATH, section)
        self.label = QLabel(name)
        self.widget = QFrame()
        self.layout = QHBoxLayout(self.widget)
        self.line = QLineEdit(value)
        self.line.setReadOnly(True)
        self.layout.addWidget(self.line)
        self.boutton = QPushButton(u"...")
        self.boutton.setFixedSize(25,25)
        self.layout.addWidget(self.boutton)

        # Quand on clique sur le boutton on défini le path
        self.connect(self.boutton, SIGNAL("clicked()"), self.updatePath)

    def updatePath(self):
        newpath = QFileDialog.getExistingDirectory(None, _(u"Choisissez un chemin"), self.value )
        if newpath:
            self.value = newpath
            self.line.setText(self.value)
            EkdConfig.set(self.section, self.id, self.value)

class EkdColorPropertie(EkdPropertie):
    """
    Définition de la propriété correspondant à une Couleur
    """
    def __init__(self, prop, name, value, section=None ):
        super(EkdColorPropertie, self).__init__(prop, name, value, EkdPropertie.COLOR, section)
        self.label = QLabel(name)
        self.widget = QFrame()
        self.layout = QHBoxLayout(self.widget)
        self.line = QLineEdit(value)
        self.value = value
        self.line.setReadOnly(True)
        self.layout.addWidget(self.line)
        self.color = QPixmap(15, 15)
        self.color.fill(QColor.fromRgb(int("%d" % int(self.value, 16))))
        self.boutton = QPushButton(QIcon(self.color), u"")
        self.boutton.setFixedSize(25,25)
        self.layout.addWidget(self.boutton)

        # Quand on clique sur le boutton on défini la couleur
        self.connect(self.boutton, SIGNAL("clicked()"), self.updateColor)

    def updateColor(self):
        newcolor = QColorDialog.getColor(QColor.fromRgb(int("%d" % int(self.value, 16))), None )# Non supporté sous Jaunty ??
        if newcolor.isValid():
            self.value = str("%x" % newcolor.rgb())[2:]
            self.color.fill(QColor.fromRgb(int("%d" % int(self.value, 16))))
            self.boutton.setIcon(QIcon(self.color))
            self.line.setText(self.value)
            EkdConfig.set(self.section, self.id, self.value)
