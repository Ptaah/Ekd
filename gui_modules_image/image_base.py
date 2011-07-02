#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
# On importe le strict nécessaire
from PyQt4.QtCore import SIGNAL, SLOT, Qt
from PyQt4.QtGui import QWidget, QSpinBox, QSlider, QHBoxLayout, QGridLayout, QLabel
# Utilisation de EkdConfig
from moteur_modules_common.EkdConfig import EkdConfig

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


class Base(object):
	#-------------------------------------
	# Fonctions communes au module Image
	#-------------------------------------

	def getRepSource(self, config):
		"Renvoie le répertoire source qui sera utilisée dans la boite de dialogue de fichiers"
		try:
			repEntree = config.get('general','image_input_path').decode("UTF8")
		except Exception, e:
			repEntree = '~'
		if not os.path.exists(repEntree):
			repEntree = '~'

		return os.path.expanduser(repEntree)


	def setRepSource(self, config, cheminEntree):
		"Sauvegarde le répertoire source qui sera utilisée dans la boite de dialogue de fichiers"
		if isinstance(cheminEntree, list):
			if len(cheminEntree)==0: return
			config.set('general','image_input_path',os.path.dirname(cheminEntree[0]).encode("UTF8"))

		elif isinstance(cheminEntree, unicode):
			if not cheminEntree: return
			config.set('general','image_input_path',os.path.dirname(cheminEntree).encode("UTF8"))


	def valeurComboIni(self, comboBox, config, idSection, optionConfig):
		"Affiche au lancement du logiciel l'entrée de la boite de combo inscrite dans un fichier de configuration"
		try:
			valeur = config.get(idSection, optionConfig)
		except:
			#print "Pas de valeur dans la config pour : ", idSection, optionConfig
			EkdPrint(u"Pas de valeur dans la config pour : %s %s" % (idSection, optionConfig))
		else:
			codec_trouve = False
			for i in range(comboBox.count()):
				if comboBox.itemData(i).toString() == valeur:
					indice = i
					codec_trouve = True
			if not codec_trouve: indice = 0
			comboBox.setCurrentIndex(indice)


	def printSection(self, idSection):
		"""Affichage dans le terminal de la section initialisée"""
		#print '\n'+'-'*30+'\n| '+idSection+'\n'+'-'*30+'\n'
		EkdPrint('\n%s\n| %s\n%s\n' % ('-'*30, idSection, '-'*30))


class SpinSlider(QWidget):
	"Boite de spin + curseur avec sauvegarde de la dernière valeur sélectionnée"
	def __init__(self, debut, fin, defaut, optionConfig=None, parent=None):
		QWidget.__init__(self)

		self.spin = QSpinBox()
		self.slider = QSlider(Qt.Horizontal)
		self.spin.setRange(debut, fin)
		self.slider.setRange(debut, fin)

		valeur = None
		if optionConfig:
			self.config = parent.config
			self.idSection = parent.idSection
			self.optionConfig = optionConfig
			try :
				valeur = self.config.get(self.idSection, self.optionConfig)
			except:
				valeur = defaut
				self.config.set(self.idSection, self.optionConfig, valeur)
		erreur = False
		if valeur:
			try: valeur = int(valeur)
			except ValueError: erreur = True
		if not erreur and debut <= valeur <= fin:
			self.spin.setValue(valeur)
			self.slider.setValue(valeur)
		else:
			self.spin.setValue(defaut)
			self.slider.setValue(defaut)
		if optionConfig: self.connect(self.spin, SIGNAL("valueChanged(int)"), self.sauveConfig)
		self.connect(self.spin, SIGNAL("valueChanged(int)"), self.slider,
						SLOT("setValue(int)"))
		self.connect(self.slider, SIGNAL("valueChanged(int)"), self.spin,
						SLOT("setValue(int)"))
		self.connect(self.spin, SIGNAL("valueChanged(int)"), self.changed)
		hbox = QHBoxLayout(self)
		hbox.addWidget(self.spin)
		hbox.addWidget(self.slider)
		hbox.setMargin(0) # pour un meilleur alignement dans un grid

	def changed(self, i):
		self.emit(SIGNAL("valueChanged(int)"), i)

	def sauveConfig(self, i):
		self.config.set(self.idSection, self.optionConfig, str(i))

	def value(self):
		return self.spin.value()

	def setValue(self, i):
		self.spin.setValue(i)
		self.slider.setValue(i)


class SpinSliders(QWidget):
	"Boites de spin + curseur avec sauvegarde de la dernière valeur sélectionnée"
	def __init__(self, parent,
				debut1, fin1, defaut1, txt1, optionConfig1,
				debut2=None, fin2=None, defaut2=None, txt2=None, optionConfig2=None,
				debut3=None, fin3=None, defaut3=None, txt3=None, optionConfig3=None,
				):
		QWidget.__init__(self)
		grid = QGridLayout(self)
		self.spin = SpinSlider(debut1, fin1, defaut1, optionConfig1, parent)
		self.spin1= self.spin
		grid.addWidget(self.spin,0,0)
		if txt1: grid.addWidget(QLabel(txt1),0,1)
		if debut2:
			self.spin2 = SpinSlider(debut2, fin2, defaut2, optionConfig2, parent)
			grid.addWidget(self.spin2,1,0)
			if txt2: grid.addWidget(QLabel(txt2),1,1)
		if debut3:
			self.spin3 = SpinSlider(debut3, fin3, defaut3, optionConfig3, parent)
			grid.addWidget(self.spin3,2,0)
			if txt3: grid.addWidget(QLabel(txt3),2,1)
		grid.setAlignment(Qt.AlignCenter)
		grid.setMargin(0)


class SpinSliders20Possibles(QWidget):
	"Boites de spin + curseur avec sauvegarde de la dernière valeur sélectionnée"
	"Modele pour 20 boites de spin possibles (ce qui laisse pas mal de possibilités de réglages"
	def __init__(self, parent,
				debut1, fin1, defaut1, txt1, optionConfig1,
				debut2=None, fin2=None, defaut2=None, txt2=None, optionConfig2=None,
				debut3=None, fin3=None, defaut3=None, txt3=None, optionConfig3=None,
				debut4=None, fin4=None, defaut4=None, txt4=None, optionConfig4=None,
				debut5=None, fin5=None, defaut5=None, txt5=None, optionConfig5=None,
				debut6=None, fin6=None, defaut6=None, txt6=None, optionConfig6=None,
				debut7=None, fin7=None, defaut7=None, txt7=None, optionConfig7=None,
				debut8=None, fin8=None, defaut8=None, txt8=None, optionConfig8=None,
				debut9=None, fin9=None, defaut9=None, txt9=None, optionConfig9=None,
				debut10=None, fin10=None, defaut10=None, txt10=None, optionConfig10=None,
				debut11=None, fin11=None, defaut11=None, txt11=None, optionConfig11=None,
				debut12=None, fin12=None, defaut12=None, txt12=None, optionConfig12=None,
				debut13=None, fin13=None, defaut13=None, txt13=None, optionConfig13=None,
				debut14=None, fin14=None, defaut14=None, txt14=None, optionConfig14=None,
				debut15=None, fin15=None, defaut15=None, txt15=None, optionConfig15=None,
				debut16=None, fin16=None, defaut16=None, txt16=None, optionConfig16=None,
				debut17=None, fin17=None, defaut17=None, txt17=None, optionConfig17=None,
				debut18=None, fin18=None, defaut18=None, txt18=None, optionConfig18=None,
				debut19=None, fin19=None, defaut19=None, txt19=None, optionConfig19=None,
				debut20=None, fin20=None, defaut20=None, txt20=None, optionConfig20=None,				
				):
		QWidget.__init__(self)
		grid = QGridLayout(self)
		self.spin = SpinSlider(debut1, fin1, defaut1, optionConfig1, parent)
		self.spin1= self.spin
		grid.addWidget(self.spin,0,0)
		if txt1: grid.addWidget(QLabel(txt1),0,1)
		if debut2:
			self.spin2 = SpinSlider(debut2, fin2, defaut2, optionConfig2, parent)
			grid.addWidget(self.spin2,1,0)
			if txt2: grid.addWidget(QLabel(txt2),1,1)
		if debut3:
			self.spin3 = SpinSlider(debut3, fin3, defaut3, optionConfig3, parent)
			grid.addWidget(self.spin3,2,0)
			if txt3: grid.addWidget(QLabel(txt3),2,1)
		if debut4:
			self.spin4 = SpinSlider(debut4, fin4, defaut4, optionConfig4, parent)
			grid.addWidget(self.spin4,3,0)
			if txt4: grid.addWidget(QLabel(txt4),3,1)
		if debut5:
			self.spin5 = SpinSlider(debut5, fin5, defaut5, optionConfig5, parent)
			grid.addWidget(self.spin5,4,0)
			if txt5: grid.addWidget(QLabel(txt5),4,1)
		if debut6:
			self.spin6 = SpinSlider(debut6, fin6, defaut6, optionConfig6, parent)
			grid.addWidget(self.spin6,5,0)
			if txt6: grid.addWidget(QLabel(txt6),5,1)
		if debut7:
			self.spin7 = SpinSlider(debut7, fin7, defaut7, optionConfig7, parent)
			grid.addWidget(self.spin7,6,0)
			if txt7: grid.addWidget(QLabel(txt7),6,1)
		if debut8:
			self.spin8 = SpinSlider(debut8, fin8, defaut8, optionConfig8, parent)
			grid.addWidget(self.spin8,7,0)
			if txt8: grid.addWidget(QLabel(txt8),7,1)
		if debut9:
			self.spin9 = SpinSlider(debut9, fin9, defaut9, optionConfig9, parent)
			grid.addWidget(self.spin9,8,0)
			if txt9: grid.addWidget(QLabel(txt9),8,1)
		if debut10:
			self.spin10 = SpinSlider(debut10, fin10, defaut10, optionConfig10, parent)
			grid.addWidget(self.spin10,9,0)
			if txt10: grid.addWidget(QLabel(txt10),9,1)
		if debut11:
			self.spin11 = SpinSlider(debut11, fin11, defaut11, optionConfig11, parent)
			grid.addWidget(self.spin11,10,0)
			if txt11: grid.addWidget(QLabel(txt11),10,1)
		if debut12:
			self.spin12 = SpinSlider(debut12, fin12, defaut12, optionConfig12, parent)
			grid.addWidget(self.spin12,11,0)
			if txt12: grid.addWidget(QLabel(txt12),11,1)
		if debut13:
			self.spin13 = SpinSlider(debut13, fin13, defaut13, optionConfig13, parent)
			grid.addWidget(self.spin13,12,0)
			if txt13: grid.addWidget(QLabel(txt13),12,1)
		if debut14:
			self.spin14 = SpinSlider(debut14, fin14, defaut14, optionConfig14, parent)
			grid.addWidget(self.spin14,13,0)
			if txt14: grid.addWidget(QLabel(txt14),13,1)
		if debut15:
			self.spin15 = SpinSlider(debut15, fin15, defaut15, optionConfig15, parent)
			grid.addWidget(self.spin15,14,0)
			if txt15: grid.addWidget(QLabel(txt15),14,1)
		if debut16:
			self.spin16 = SpinSlider(debut16, fin16, defaut16, optionConfig16, parent)
			grid.addWidget(self.spin16,15,0)
			if txt16: grid.addWidget(QLabel(txt16),15,1)
		if debut17:
			self.spin17 = SpinSlider(debut17, fin17, defaut17, optionConfig17, parent)
			grid.addWidget(self.spin17,16,0)
			if txt17: grid.addWidget(QLabel(txt17),16,1)
		if debut18:
			self.spin18 = SpinSlider(debut18, fin18, defaut18, optionConfig18, parent)
			grid.addWidget(self.spin18,17,0)
			if txt18: grid.addWidget(QLabel(txt18),17,1)
		if debut19:
			self.spin19 = SpinSlider(debut19, fin19, defaut19, optionConfig19, parent)
			grid.addWidget(self.spin19,18,0)
			if txt19: grid.addWidget(QLabel(txt19),18,1)
		if debut20:
			self.spin20 = SpinSlider(debut20, fin20, defaut20, optionConfig20, parent)
			grid.addWidget(self.spin20,19,0)
			if txt20: grid.addWidget(QLabel(txt20),19,1)
		grid.setAlignment(Qt.AlignCenter)
		grid.setMargin(0)
