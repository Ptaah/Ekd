#!/usr/bin/python
# -*- coding: utf-8 -*-

import platform
from moteur_modules_common.EkdConfig import EkdConfig

class EkdPrint(object):
	""" Classe pour gérer les print sous python 2 et 3 """

	def __init__(self, texte):

		# Texte qui sera affiché
		self.texte = texte.encode(EkdConfig.coding)
		
		# Affichage selon les versions de Python
		if platform.python_version()[0] == '2': print self.texte
		elif platform.python_version()[0] == '3': print(self.texte)
