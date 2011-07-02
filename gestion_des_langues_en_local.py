#!/usr/bin/python
# -*- coding: Utf-8 -*-	

# Script qui sert à copier ...
#
# locale/en_EN/LC_MESSAGES/ekd.mo et locale/en_EN/LC_MESSAGES/ekdDoc.mo vers 
# (par exemple) locale/en_AU/LC_MESSAGES/ekd.mo locale/en_AU/LC_MESSAGES/ekd.mo 
# (et ce pour tous les répertoires symbole langue dont la langue officielle est l'anglais)
#
# puis ...
#
# locale/es_ES/LC_MESSAGES/ekd.mo et locale/es_ES/LC_MESSAGES/ekdDoc.mo vers 
# (par exemple) locale/es_AR/LC_MESSAGES/ekd.mo locale/es_AR/LC_MESSAGES/ekd.mo 
# (et ce pour tous les répertoires symbole langue dont la langue officielle est l'espagnol).
#
# ATTENTION (!!!): les répertoires (et sous-répertoires):
#
# locale/en_EN/LC_MESSAGES et locale/es_ES/LC_MESSAGES
#
# ... ne doivent jamais être éliminés.
#
# Les nationalités et communautés gérées pour l'instant sont:
#
# pour l'anglais (autres que 'en_EN' ==> English):
#
# 'en_AU' => 'English (Australia)', 'en_CA' => 'English (Canada)', 'en_GB' => 'English (United Kingdom)',
# 'en_HK' => 'English (Hong Kong SAR China)', 'en_IE' => 'English (Ireland)', 'en_IN' => 'English (India)',
# 'en_JM' => 'English (Jamaica)', 'en_LR' => 'English (Liberia)', 'en_NZ' => 'English (New Zealand)',
# 'en_PH' => 'English (Philippines)', 'en_SG' => 'English (Singapore)', 'en_TT' => 'English (Trinidad and Tobago)',
# 'en_US' => 'English (United States)', 'en_ZA' => 'English (South Africa)'.
#
# pour l'espagnol (autres que 'es_ES' => Spanish):
#
# 'es_AR' => 'Spanish (Argentina)', 'es_BO' => 'Spanish (Bolivia)', 'es_CA' => 'Spanish (Canada)', 
# 'es_CL' => 'Spanish (Chile)', 'es_CO' => 'Spanish (Colombia)', 'es_CR' => 'Spanish (Costa Rica)', 
# 'es_CU' => 'Spanish (Cuba)', 'es_DO' => 'Spanish (Dominican Republic)', 'es_EC' => 'Spanish (Ecuador)', 
# 'es_GQ' => 'Spanish (Equatorial Guinea)', 'es_GT' => 'Spanish (Guatemala)', 'es_HN' => 'Spanish (Honduras)', 
# 'es_MX' => 'Spanish (Mexico)', 'es_NI' => 'Spanish (Nicaragua)', 'es_PA' => 'Spanish (Panama)', 
# 'es_PE' => 'Spanish (Peru)', 'es_PR' => 'Spanish (Puerto Rico)', 'es_PY' => 'Spanish (Paraguay)', 
# 'es_SV' => 'Spanish (El Salvador)', 'es_US' => 'Spanish (United States)', 'es_UY' => 'Spanish (Uruguay)', 
# 'es_VE' => 'Spanish (Venezuela)'.


import os, glob, shutil
from PyQt4.QtCore import QLocale

class GestionLangues(object):
	def __init__(self):

		# On liste tous les chemins possibles des nationalités (ou communautés) de langue anglaise et espagnole
		ChemSymbLang_EN_ES = ['locale'+os.sep+'en_AU'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_CA'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_GB'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_HK'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_IE'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_IN'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_JM'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_LR'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_NZ'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_PH'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_SG'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_TT'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_US'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'en_ZA'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_AR'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_BO'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_CA'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_CL'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_CO'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_CR'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_CU'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_DO'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_EC'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_GQ'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_GT'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_HN'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_MX'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_NI'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_PA'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_PE'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_PR'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_PY'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_SV'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_US'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_UY'+os.sep+'LC_MESSAGES', 'locale'+os.sep+'es_VE'+os.sep+'LC_MESSAGES']

		# Ensuite on crée les répertoires (si les répertoires intermédiaires 
		# n'existent pas, ils sont crées --aussi-- à la volée)
		for repNation_EN_ES in ChemSymbLang_EN_ES:
			# Si tous les répertoires existent déjà
			# il ne se passe rien ...
			if os.path.exists(repNation_EN_ES):
				pass
			# Autrement ils sont crées ...
			else: os.makedirs(repNation_EN_ES, 0755)
	
		# Liste récupérant les chemins sous la forme: locale/en_CA (Canada) et en excluant du lot: locale/en_EN
		contenu_locale_EN = [enX for enX in glob.glob('locale'+os.sep+'*') if enX[:-3] == 'locale'+os.sep+'en' and enX != 'locale'+os.sep+'en_EN']
		# Liste récupérant les chemins sous la forme: locale/es_CU (Cuba) et en excluant du lot: locale/es_ES
		contenu_locale_ES = [esX for esX in glob.glob('locale'+os.sep+'*') if esX[:-3] == 'locale'+os.sep+'es' and esX != 'locale'+os.sep+'es_ES']

		# On vérifie si les fichiers ekd.mo et ekdDoc.mo sont déjà présents dans
		# les différents répertoires en_..., si c'est le cas ils sont éliminés.
		# Ensuite les fichiers .mo sont copiés dans chaque répertoire de langue
		# anglaise
		for parcEN in contenu_locale_EN:
			parc_EN = parcEN + os.sep + 'LC_MESSAGES' + os.sep
			if 'ekd.mo' in os.listdir(parc_EN):
				os.remove(parc_EN+'ekd.mo')
			shutil.copy('locale'+os.sep+'en_EN'+os.sep+'LC_MESSAGES'+os.sep+'ekd.mo', parc_EN)
			if 'ekdDoc.mo' in os.listdir(parc_EN):
				os.remove(parc_EN+'ekdDoc.mo')
			shutil.copy('locale'+os.sep+'en_EN'+os.sep+'LC_MESSAGES'+os.sep+'ekdDoc.mo', parc_EN)

		# Même chose qu'au dessus mais pour la langue espagnole
		for parcES in contenu_locale_ES:
			parc_ES = parcES + os.sep + 'LC_MESSAGES' + os.sep
			if 'ekd.mo' in os.listdir(parc_ES):
				os.remove(parc_ES+'ekd.mo')
			shutil.copy('locale'+os.sep+'es_ES'+os.sep+'LC_MESSAGES'+os.sep+'ekd.mo', parc_ES)
			if 'ekdDoc.mo' in os.listdir(parc_ES):
				os.remove(parc_ES+'ekdDoc.mo')
			shutil.copy('locale'+os.sep+'es_ES'+os.sep+'LC_MESSAGES'+os.sep+'ekdDoc.mo', parc_ES)
			
		# Détection de la langue
		self.langue_locale = str(QLocale.system().name())
			
		# Liste des pays francophones et provinces d'outre-mer (dont au moins la 2ème langue parlée est le français).
		# fr_FR --> France métropolitaine, fr_BE --> Belgique, fr_CA --> Canada, fr_LU --> Luxembourg, fr_CH --> Suisse, fr_MC --> Monaco,
		# fr_TF --> French Southern and Antartics Lands, fr_Yt --> Myotte, fr_CF --> Centrafrique, fr_CI --> Côte d'Ivoire, fr_CM --> Cameroun,
		# fr fr_DZ --> Algérie, fr_GA --> Gabon, fr_GP --> Guadeloupe, fr_GQ --> Guinée Equatoriale, fr_GY --> Guyane, fr_HT --> Haïti, 
		# fr_MG --> Madagascar, fr_ML --> Mali, fr_MQ --> Martinique, fr_BJ --> Bénin, fr_BF --> Burkina Faso, fr_DJ --> Djibouti,
		# fr_NE --> Niger, fr_CD --> Congo, fr_PF --> Polynésie Française, fr_PM -> St Pierre et Miquelon, fr_RE --> Réunion, 
		# fr_SC --> Seychelles, fr_SN --> Sénégal, fr_RW --> Rwanda, fr_TD --> Tchad, fr_TG --> Togo
			
		# Si on a spécifiquement une locale en_EN ou es_ES, la
		# fonction n'est pas exécutée
		if self.langue_locale not in ['en_EN', 'es_ES']:
			# De même si la langue française est détectée, la
			# fonction n'est pas exécutée
			if self.langue_locale[0:2] != 'fr':
				self.langue_autre()
		

	def langue_autre(self):
	
		# -------------------------------------------------------
		# Cette fonction sert à afficher l'interface d'EKD en anglais pour toutes les langues non gérées par EKD
		# -------------------------------------------------------
	
		# Détection des répertoires langue gérés par EKD
		listeRepLocale = [os.path.basename(parcLoc) for parcLoc in glob.glob('locale'+os.sep+'*') if '_' in parcLoc and len(parcLoc) == 12]
		listeRepLocale.sort()

		# Chemin interne langue d'EKD
		arborescence_nouvelle_langue = os.sep+'locale'+os.sep+self.langue_locale+os.sep+'LC_MESSAGES'
		
		# Supression du chemin du répertoire langue (avec lequel on travaille)
		if os.path.isdir(os.path.dirname(os.getcwd()+os.sep+arborescence_nouvelle_langue)) is True:
			shutil.rmtree(os.path.dirname(os.getcwd()+os.sep+arborescence_nouvelle_langue))
		
		# L'arborescence de langue est crée
		os.makedirs(os.getcwd()+arborescence_nouvelle_langue, 0755)
		
		liste_langue_locale = []
		
		for parcLocale in listeRepLocale:
			# Si les langues contenues dans self.langue_locale (les langues 
			# officiellement gérées par EKD) sont différentes de la langue détectée ...
			if parcLocale != self.langue_locale:
				liste_langue_locale.append(self.langue_locale)
			
		# Si la liste contient au moins un élément, les fichiers .mo (compilés) sont copiés dans le nouveau répertoire langue 
		# qui vient d'être crée. Cela permet d'afficher l'interface en anglais pour les langues non gérées par EKD.
		if len(liste_langue_locale) >= 1:	
			shutil.copy(os.getcwd()+os.sep+'locale'+os.sep+'en_EN'+os.sep+'LC_MESSAGES'+os.sep+'ekd.mo', os.getcwd()+arborescence_nouvelle_langue+os.sep+'ekd.mo')
			shutil.copy(os.getcwd()+os.sep+'locale'+os.sep+'en_EN'+os.sep+'LC_MESSAGES'+os.sep+'ekdDoc.mo', os.getcwd()+arborescence_nouvelle_langue+os.sep+'ekdDoc.mo')
							
# Appel de la classe
main = GestionLangues()
