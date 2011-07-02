#! /usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, shutil, locale
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############


####################################################################
# Script pour installer/mettre à jour/désisntaller EKD sur la 
# machine (et ce en tant qu'administrateur). Ce script a été crée 
# par Lama Angelo et est mis en GPL v3. Pour la licence référez-vous
# à l'entête contenu dans le fichier ekd_gui.py
####################################################################
# Installation/Mise à jour:
# -------------------------
# Pour installer EKD en mode administrateur, procédez comme suit:
# 1) Après avoir téléchargé ekd_linux_source_numéro-de-version_date-de-version.tar.gz,
# déposez l'archive dans votre /home/utilisateur et dé-tar-gzippez la --> tapez 
# dans la console: tar zxvf ekd_linux_source_numéro-de-version_date-de-version.tar.gz
# 2) Entrez dans le répertoire, tapez ce coup-ci dans la console:
# cd ekd_linux_source_numéro-de-version_date-de-version/
# 3) Installez maintenant en mode administrateur, on tape dans la console ...
# * Pour les distributions à base de sudo:
# sudo python install_ekd_linux_admin.py (entrez le mot de passe de 
# l'utilisateur administrateur)
# * Pour les distribution n'utilisant pas sudo:
# su (entrez le mot de l'administrateur)
# python install_ekd_linux_admin.py
# .... et suivez la procédure décrite à l'écran
# Désinstallation:
# ----------------
# 1) Allez de nouveau dans le répertoire d'EKD
# --> cd ekd_linux_source_numéro-de-version_date-de-version/
# 2) Tapez dans la console en mode administrateur, ...
# * Pour les distributions à base de sudo:
# sudo python install_ekd_linux_admin.py (entrez le mot de passe de 
# l'utilisateur administrateur)
# * Pour les distribution n'utilisant pas sudo:
# su (entrez le mot de l'administrateur)
# python install_ekd_linux_admin.py
# .... et suivez la procédure s'affichant à l'écran.
####################################################################


class InstDesinstEKD(object):
	def __init__(self):
		
		# Nom
		self.nom = 'EKD'
		# Version
		self.version = '2.0.8'
		# Version de la locale (fr pour langue française)
		self.langue = locale.getdefaultlocale()[0][:2]
		
		# Conditions pour la langue (et textes dans les variables)
		
		if self.langue == 'fr': # français
			
			# Menu
			entete_1 = u"INSTALLATION/MISE A JOUR/DESINSTALLATION D'%s \nEN VERSION %s POUR LINUX"
			annonce_inst_maj = u"* Tapez 1 sur le clavier pour installer ou faire une mise à jour"
			annonce_desinst = u"* Tapez 2 sur le clavier pour désinstaller"
			annonce_quitter = u"* Tapez 0 sur le clavier pour QUITTER sans rien faire"
			annonce_choix = u"Quel est votre choix ; 1, 2 or 0 (?):"
			# Installation
			self.inst_entete = u"INSTALLATION OU MISE A JOUR D'%s \nEN VERSION %s POUR LINUX"
			self.creat_rep_ekd = u"* Création du répertoire /usr/share/ekd: OK"
			self.copie_fich_rep_ekd = u"* Copie des fichiers et répertoires dans /usr/share/ekd: OK"
			self.verif_pres_exec_ekd = u"* Vérification de la présence de /usr/bin/ekd: OK"
			self.racc_ekd = u"* Création du raccourci pour l'exécution de \n%s en version %s: OK"
			self.inst_terminee = u"INSTALLATION OU MISE A JOUR DE %s %s TERMINEE !."
			self.inst_prob_1 = u"IL Y A UN PROBLEME !!!:"
			self.int_prob_2 = u"VOUS AVEZ DU ELIMINER PAR ACCIDENT LE FICHIER /usr/bin/ekd,"
			self.int_prob_3 = u"POUR RESOUDRE CELA, REINSTALLEZ ... ET LE FICHIER SERA DE NOUVEAU"
			self.int_prob_4 = u"CREE."
			# Désinstallation
			self.desinst_entete = u"DESINSTALLATION D'%s VERSION %s \nPOUR LINUX"
			self.elimin_racc_1 = u"* Elimination du raccourci pour %s: OK"
			self.elimin_racc_2 = u"* Elimination du fichier /usr/share/applications/ekd.desktop:\n--> CE FICHIER N'EXISTE PAS OU A DEJA ETE SUPPRIME !!!"
			self.elimin_usr_share_ekd_1 = u"* Elimination du repertoire /usr/share/ekd: OK"
			self.elimin_usr_share_ekd_2 = u"* Elimination du repertoire /usr/share/ekd:\n--> CE REPERTOIRE N'EXISTE PAS OU A DEJA ETE SUPPRIME !!!"
			self.elimin_usr_bin_ekd_1 = u"* Elimination du fichier /usr/bin/ekd: OK"
			self.elimin_usr_bin_ekd_2 = u"* Elimination du fichier /usr/bin/ekd:\n--> CE FICHIER N'EXISTE PAS OU A DEJA ETE SUPPRIME !!!"
			self.desinst_terminee = u"DESINSTALLATION D'%s %s TERMINEE !."
			self.desinst_prob_1 = u"IL Y A UN PROBLEME !!!."
			
		elif self.langue == 'es': # espagnol
			
			# Menu
			entete_1 = u"INSTALACIÓN/ACTUALIZACIÓN/ELIMINACIÓN DE %s \nEN VERSIÓN %s PARA LINUX"
			annonce_inst_maj = u"* Pulse 1 en el teclado para instalar o hacer una actualización"
			annonce_desinst = u"* Pulse 2 en el teclado para eliminar"
			annonce_quitter = u"* Pulse 0 en el teclado para SALIR sin hacer nada"
			annonce_choix = u"Seleccione 1, 2 or 0 :"
			# Installation
			self.inst_entete = u"INSTALACIÓN O ACTUALIZACIÓN DE %s \nEN VERSIÓN %s PARA LINUX"
			self.creat_rep_ekd = u"* Creación de la carpeta /usr/share/ekd: OK"
			self.copie_fich_rep_ekd = u"* Copia de los ficheros y carpetas en /usr/share/ekd: OK"
			self.verif_pres_exec_ekd = u"* Vérificación de la presencia de /usr/bin/ekd: OK"
			self.racc_ekd = u"* Creación de un acceso directo para la ejecución de \n%s en versión %s: OK"
			self.inst_terminee = u"INSTALACIÓN O ACTUALIZACIÓN DE %s %s TERMINADA !."
			self.inst_prob_1 = u"HAY UN PROBLEMA !!!:"
			self.int_prob_2 = u"HA ELIMINADO POR ERROR EL FICHERO /usr/bin/ekd,"
			self.int_prob_3 = u"PARA RESOLVER ESO, REINICIE LA INSTALACIÓN ... Y"
			self.int_prob_4 = u"EL FICHERO SERA CREADO DE NUEVO CREADO."
			# Désinstallation
			self.desinst_entete = u"ELIMINACIÓN DE %s VERSIÓN %s \nPARA GNU/LINUX"
			self.elimin_racc_1 = u"* Eliminación del acceso directo para %s: OK"
			self.elimin_racc_2 = u"* Eliminación del fichero /usr/share/applications/ekd.desktop:\n--> ESE FICHERO NO EXISTE O HA SIDO SUPRIMIDO"
			self.elimin_usr_share_ekd_1 = u"* Eliminación de la carpeta /usr/share/ekd: OK"
			self.elimin_usr_share_ekd_2 = u"* Eliminación de la carpeta /usr/share/ekd:\n--> ESTA CARPETA NO EXISTE O HA SIDO SUPRIMIDA"
			self.elimin_usr_bin_ekd_1 = u"* Eliminación del fichero /usr/bin/ekd: OK"
			self.elimin_usr_bin_ekd_2 = u"* Eliminación del fichero /usr/bin/ekd:\n--> ESE FICHERO NO EXISTE O HA SIDO SUPRIMIDO"
			self.desinst_terminee = u"ELIMINACIÓN DE %s %s TERMINADA."
			self.desinst_prob_1 = u"HAY UN PROBLEMA."
			
		elif self.langue not in  ['fr', 'es']: # pour toutes les autres langues que fr et es, l'interface sera en english.
			
			# Menu
			entete_1 = u"%s INSTALLATION OR UPDATE\nVERSION %s FOR LINUX"
			annonce_inst_maj = u"* Enter 1 on your keyboard to install EKD or to make an update"
			annonce_desinst = u"* Enter 2 on your keyboard to disinstall"
			annonce_quitter = u"* Enter 0 on your keyboard to QUIT without do anything"
			annonce_choix = u"What's your choice ; 1, 2 or 0 (?):"
			# Installation
			self.inst_entete = u"%s %s INSTALLATION/UPDATE FOR LINUX ..."
			self.creat_rep_ekd = u"* Creation of /usr/share/ekd repertory: OK"
			self.copie_fich_rep_ekd = u"* Files and repertories copy in /usr/share/ekd repertory: OK"
			self.verif_pres_exec_ekd = u"* Checking of the /usr/bin/ekd file presence: OK"
			self.racc_ekd = u"* Creation of a short cut for \n%s execution version %s: OK"
			self.inst_terminee = u"INSTALLATION (OR UPDATE) OF %s %s COMPLETED !!!."
			self.inst_prob_1 = u"THERE WAS A PROBLEM !!!:"
			self.int_prob_2 = u"YOU MIGHT ERASE BY ACCIDENT THE FILE /usr/bin/ekd,FOR RESOLVE"
			self.int_prob_3 = u"THIS PROBLEM START A NEW INSTALLATION, AND FOR CREATED AGAIN"
			self.int_prob_4 = u"THIS FILE."
			# Désinstallation
			self.desinst_entete = u"%s %s DISINSTALLATION FOR LINUX"
			self.elimin_racc_1 = u"* %s shortcut eradication: OK"
			self.elimin_racc_2 = u"* Eradication of the /usr/share/applications/ekd.desktop file:\n--> THIS FILE DON'T EXIST OR HAS BEEN ERASED !!!"
			self.elimin_usr_share_ekd_1 = u"* Eradication of the /usr/share/ekd repertory: OK"
			self.elimin_usr_share_ekd_2 = u"* Eradication of the /usr/share/ekd repertory:\n--> THIS FILE DON'T EXIST OR HAS BEEN ERASED !!!"
			self.elimin_usr_bin_ekd_1 = u"* Eradication of the /usr/bin/ekd file: OK"
			self.elimin_usr_bin_ekd_2 = u"* Eradication of the /usr/bin/ekd file:\n--> THIS FILE DON'T EXIST OR HAS BEEN ERASED !!!"
			self.desinst_terminee = u"%s %s DISINSTALLATION COMPLETED !."
			self.desinst_prob_1 = u"THERE WAS A PROBLEM !!!."

		# ---------------------------------------------------------------------------------
		# MENU PRINCIPAL DU SCRIPT 
		# ---------------------------------------------------------------------------------
		'''
		print
		print "==================================================================="
		print entete_1 % (self.nom, self.version)
		print "==================================================================="
		print annonce_inst_maj
		print "-------------------------------------------------------------------"
		print annonce_desinst
		print "-------------------------------------------------------------------"
		print annonce_quitter
		print "-------------------------------------------------------------------"
		'''
		EkdPrint(u'')
		EkdPrint(u"===================================================================")
		EkdPrint(u"%s" % entete_1 % (self.nom, self.version))
		EkdPrint(u"===================================================================")
		EkdPrint(u"%s" % annonce_inst_maj)
		EkdPrint(u"-------------------------------------------------------------------")
		EkdPrint(u"%s" % annonce_desinst)
		EkdPrint(u"-------------------------------------------------------------------")
		EkdPrint(u"%s" % annonce_quitter)
		EkdPrint(u"-------------------------------------------------------------------")
		choix = input(annonce_choix(sys.stdout.encoding))
		if choix == 1: self.installation_admin()
		elif choix == 2: self.desinstallation_admin()
		elif choix == 0: sys.exit()
		EkdPrint(u'')


	def installation_admin(self) :
	
		try :
        		# Recup du chemin du rep.courant
			repCourISU=os.getcwd()
	
			# =====================================================================================
			# Si EKD n'a jamais ete installe ... ou pour faire une mise à jour (2 en 1)
			# =====================================================================================
			'''
			print "-------------------------------------------------------------------"
			print self.inst_entete % (self.nom, self.version)
			print "-------------------------------------------------------------------"
			'''
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(self.inst_entete % (self.nom, self.version))
			EkdPrint(u"-------------------------------------------------------------------")
			
			# Ecriture du fichier executable dans /usr/bin (/usr/bin/ekd). 
			# Il suffira de taper : ekd dans un terminal pour l'executer .
			ecrireAppliInstEKD=open("/usr/bin/ekd", 'w') 
			ecrireAppliInstEKD.write("# ------------------------------------------\n"+"# Ne pas eliminer ce fichier !!! ."+"\n# ------------------------------------------\n\ncd /usr/share/ekd && python ekd_gui.py")
			ecrireAppliInstEKD.close()
	
			# Changement des droits du fichier executable .
			os.chmod('/usr/bin/ekd', 0755)
	
			# -----------------------------------------------------------------------------
			# * Supression du repertoire /usr/share/ekd (s'il existe)
			# * Creation du rep. /usr/share/ekd ... et en meme temps ... copie (en dessous)
			# * Copie de tous les reps. et fichiers d'EKD dans /usr/share/ekd
			# * Modification des droits des reps. et fichiers dans /usr/share/ekd
			# * Creation du raccourci dans Graphisme
			# * Verification de la presence de /usr/bin/ekd
			# -----------------------------------------------------------------------------
	
			# Si le repertoire /usr/share/ekd existe deja ... supression de ce rep.
			# ... car cela sert aussi bien que pour une install que pour une maj
			if os.path.isdir('/usr/share/ekd') is True: 
				os.system('rm -rf /usr/share/ekd')
		
			# Information sur la creation du rep. /usr/share/ekd
			#print self.creat_rep_ekd
			#if self.langue == 'en': EkdPrint(self.creat_rep_ekd)
			EkdPrint(u"%s" % self.creat_rep_ekd)
			
			# Info sur la copie des reps. et fichiers dans /usr/share/ekd
			#print self.copie_fich_rep_ekd
			EkdPrint(u"%s" % self.copie_fich_rep_ekd)
	
			# Création de /usr/share/ekd et copie de tous les reps. et fichiers d'EKD dedans 
			copRepFich1=shutil.copytree(repCourISU, '/usr/share/ekd')
	
			# Le fichier divx2pass.log doit être crée pendant
			# l'install et il doit être en chmod 777 (-rwxrwxrwx)
			os.system('touch /usr/share/ekd/divx2pass.log')
			os.system('chmod 777 /usr/share/ekd/divx2pass.log')
			# Attention ici le script de gestion des langues est lancé
			os.system('python /usr/share/ekd/langues_inst_deb/gestion_des_langues_usr_share_ekd.py')
		
			# Changement des droits du fichier executable (le script principal) 
			# en rwxr-xr-x (755)
			os.chmod('/usr/share/ekd/ekd_gui.py', 0755)
		
			# Verification de la presence du fichier executable ekd dans /usr/bin
			if 'ekd' in os.listdir('/usr/bin'):
				#print self.verif_pres_exec_ekd
				EkdPrint(u"%s" % self.verif_pres_exec_ekd)
		
			'''
			# Ecriture du raccourci
			ecrireRaccEKD=open('/usr/share/applications/ekd.desktop', 'w')
			ecrireRaccEKD.write("[Desktop Entry]\nVersion=1.0\nEncoding=UTF-8\nName=%s\nGenericName=%s\nGenericName[fr]=%s\nComment=Post-production software four video or pictures\nComment[fr]=Application de post-production (pour videos ou images)\nExec='/usr/bin/ekd'\nIcon=/usr/share/ekd/icone_ekd.png\nTerminal=false\nMultipleArgs=false\nType=Application\nCategories=AudioVideo;AudioVideoEditing;\nStartupNotify=true" % (self.nom, self.nom, self.nom))
			ecrireRaccEKD.close()
			'''
			
			# Ecriture du raccourci
			ecrireRaccEKD=open('/usr/share/applications/ekd.desktop', 'w')
			ecrireRaccEKD.write("[Desktop Entry]\nVersion=1.0\nEncoding=UTF-8\nName=ekd\nGenericName=EnKoDeur-Mixeur\nGenericName[fr]=EnKoDeur-Mixeur\nComment=Post-production software four video or pictures\nComment[fr]=Application de post-production (pour videos ou images)\nExec=python /usr/share/ekd/ekd_gui.py\nIcon=/usr/share/ekd/icone_ekd.png\nPath=/usr/share/ekd\nTerminal=true\nMultipleArgs=false\nType=Application\nCategories=AudioVideo;AudioVideoEditing;\nStartupNotify=true\nTerminalOptions=\s--noclose")
			ecrireRaccEKD.close()

			#print self.racc_ekd % (self.nom, self.version)
			EkdPrint(self.racc_ekd % (self.nom, self.version))
			
			'''
			print "-------------------------------------------------------------------"
			print self.inst_terminee % (self.nom, self.version)
			print "-------------------------------------------------------------------"
			'''
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(self.inst_terminee % (self.nom, self.version))
			EkdPrint(u"-------------------------------------------------------------------")
			
		except:
			'''
			print
			print "-------------------------------------------------------------------"
			print self.inst_prob_1
			print "-------------------------------------------------------------------"
			print self.int_prob_2
			print self.int_prob_3
			print self.int_prob_4
			print "-------------------------------------------------------------------"
			print
			'''
			EkdPrint(u'')
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(u"%s" % self.inst_prob_1)
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(u"%s" % self.int_prob_2)
			EkdPrint(u"%s" % self.int_prob_3)
			EkdPrint(u"%s" % self.int_prob_4)
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(u'')
	
	
	# ---------------------------------------------------------------------------------	
	def desinstallation_admin(self):
	
		try :
			'''
			print "-------------------------------------------------------------------"
			print self.desinst_entete % (self.nom, self.version)
			print "-------------------------------------------------------------------"
			'''
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(self.desinst_entete) % (self.nom, self.version))
			EkdPrint(u"-------------------------------------------------------------------")
			
			# ------------------------------------------------------------------------
			# Elimination du raccourci (fichier) avchdvc.desktop 
			# ------------------------------------------------------------------------
			# Si le fichier /usr/share/applications/ekd.desktop existe il est 
			# supprime, sinon il ne se passe rien et un message le precisant est affiche
			if os.path.exists('/usr/share/applications/ekd.desktop') is True:
				#print self.elimin_racc_1 % self.nom
				EkdPrint(self.elimin_racc_1) % self.nom)
				os.remove('/usr/share/applications/ekd.desktop')
			else :
				#print self.elimin_racc_2
				EkdPrint(u"%s" % self.elimin_racc_2)
		
			# ------------------------------------------------------------------------
			# Elimination du repertoire /usr/share/ekd existe
			# ------------------------------------------------------------------------
			# Si le repertoire /usr/share/ekd existe deja ...
			if os.path.isdir('/usr/share/ekd') is True:
				os.system('rm -rf /usr/share/ekd')
				#print self.elimin_usr_share_ekd_1
				EkdPrint(u"%s" % self.elimin_usr_share_ekd_1)
			else :
				#print self.elimin_usr_share_ekd_2
				EkdPrint(u"%s" % self.elimin_usr_share_ekd_2)

			# Si le fichier /usr/bin/ekd existe il est supprime, sinon
			# il ne se passe rien et un message le precisant est affiche
			if os.path.exists('/usr/bin/ekd') is True:
				#print self.elimin_usr_bin_ekd_1
				EkdPrint(u"%s" % self.elimin_usr_bin_ekd_1)
				os.remove('/usr/bin/ekd')
			else :
				#print self.elimin_usr_bin_ekd_2
				EkdPrint(u"%s" % self.elimin_usr_bin_ekd_2)
		
			'''
			print "-------------------------------------------------------------------"
			print self.desinst_terminee % (self.nom, self.version)
			print "-------------------------------------------------------------------"
			'''
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(self.desinst_terminee % (self.nom, self.version))
			EkdPrint(u"-------------------------------------------------------------------")

		except:
			'''
			print "-------------------------------------------------------------------"
			print self.desinst_prob_1
			print "-------------------------------------------------------------------"
			'''
			EkdPrint(u"-------------------------------------------------------------------")
			EkdPrint(u"%s" % self.desinst_prob_1)
			EkdPrint(u"-------------------------------------------------------------------")


# Appel de la classe
main = InstDesinstEKD()
