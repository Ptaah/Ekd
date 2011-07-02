		 ========================
		|  EKD: EnKoDeur-Mixeur  |
		 ========================

 --------------
| Description  |
 --------------
	- Ekd peut servir à réaliser des opérations de post-production pour vidéo et lots d'images

 --------------------------
| Site officiel du projet  |
 --------------------------
	http://ekd.tuxfamily.org

 ---------
| Licence |
 ---------
	- GPL3 (Licence publique générale GNU)

 -----------------------------------------------
| Dépendances à satisfaire avant de lancer ekd  |
 -----------------------------------------------
	- python-qt4 (>= 4.0.1) (correspond à python >= 2.4.4)
	- mplayer
	- mencoder
	- imagemagick
	- ffmpeg2theora
	- python-numpy (Numpy)
	- python-imaging (Python Imaging Library (PIL))
	- lame
	- mjpegtools
	- sox

 ----------------------------
| Installation et lancement  |
 ----------------------------
	- Installation depuis un paquet:
		* Installation des dépendances (voir ci-dessus)
		* Tapez une des commandes suivantes dans un terminal:
			# dpkg -i nom_paquet.deb
			# rpm -i nom_paquet.rpm
			... selon le type de paquets acceptés par votre distribution
		* Alt+F2 puis ekd puis Entrée
	- Installation depuis une archive (depuis le script install linux admin):
		* Installation des dépendances (voir ci-dessus)
		* Décompactez l'archive ekd_linux_source_numéro_de_version_DateDeVersion
		* Entrez dans le répertoire généré
		* Tapez la commande suivante dans un terminal (attention il faut avoir les droits 
		super-utilisateur ... donc mettre sudo avant cette commande si vous êtes par
		exemple sous Ubuntu):
			$ sudo python install_ekd_linux_admin.py
		* Suivez ensuite la procédure décrite ici: http://ekd.tuxfamily.org/index.php/INSTekd/Linux
	- Compilation d'EKD depuis une archive	
		* Installation des dépendances (voir ci-dessus)
		* Décompactez l'archive ekd_linux_source_numéro_de_version_DateDeVersion
		* Entrez dans le répertoire généré
		* Tapez la commande suivante dans un terminal (attention il faut avoir les droits 
		super-utilisateur ... donc mettre sudo avant cette commande si vous êtes par
		exemple sous Ubuntu):
			$ autoconf
			$ ./configure --prefix=/la_ou_je_veux
			... par exemple: ./configure --prefix=/usr/local/bin
			$ make
			$ sudo make install
		** En cas d'échec lors de la compilation, il faut nettoyer les fichiers makefile ayant 
		été créés automatiquement lors de la compilation avant de recommencer une nouvelle 
		compilation. Cela se fait grâce à la commande: 
			$ sudo make clean
	- Si vous executez EKD depuis une archive:
		* Depuis un terminal:
			$ cd chemin_vers_ekd_gui.py/
			$ python ekd_gui.py
		
	- Pour désinstaller le paquet:
		* Tapez une des commandes suivantes dans un terminal:
			# dpkg -P nom_paquet
			# rpm -e nom_paquet
			... selon le type de paquets acceptés par votre distribution
			
	- Pour désinstaller/décompiler après compilation:
		* Entrez dans le répertoire où vous avez précédemment compilé EKD
		$ sudo make uninstall

 -------------------------
| Systèmes d'exploitation |
 -------------------------
	- Systèmes d'exploitation testés:
		- Ubuntu Hardy, Jaunty, Karmic 32 et 64 bits
		- Suse 11.2
		- ArchLinux
		- Sous les différentes version de Debian, la nouvelle version d'EKD n'a pas encore été testée.
	- Logiquement EKD supporte tous les systèmes d'exploitations linux 32 ou 64 bits qui satisfont les dépendances indiquées ci-dessus.

 -------------------------
| Problème(s) éventuel(s) |
 -------------------------
	- Les vidéos affichées semblent tronquées si un pilote vidéo mplayer approprié n'est pas installé ou/et si un pilote vidéo mplayer approprié n'est pas donné dans les paramètres de configuration de mplayer (option "vo" du fichier /etc/mplayer/mplayer.conf). Des pilotes vidéos mplayer appropriés sont "xv", "gl" et "gl2". Ils ne fonctionneraient pas avec tous les pilotes de carte graphique mais avec la plupart des cartes graphiques.

 ------------------
| Report de bogues |
 ------------------
	- Vous pouvez créer un sujet sur le forum de EKD à l'adresse:
		http://ekd.tuxfamily.org/forum/forumdisplay.php?fid=8
	- Pour signalez efficacement un problème, veuillez reporter l'erreur en démarrant EKD depuis un terminal:
		$ cd /usr/share/ekd # ou cd chemin_vers_ekd si vous avez téléchargé directement les sources
		$ python ekd_gui.py
		... ou encore plus simple en utilisant l'éditeur de système de votre bureau et en cochant la case «Exécuter dans un terminal»
		... et reproduisez le bogue

 -------------
| Traduction  |
 -------------
	- Vous pouvez proposez une traduction ici:
		http://ekd.tuxfamily.org/forum/forumdisplay.php?fid=8
	- Ayez en tête le symbole de votre langue: symboleLangue (http://fr.wikipedia.org/wiki/Liste_des_domaines_de_premier_niveau_d'Internet#TLD_de_code_de_pays_.28country_code_TLD_ou_ccTLD.29). Ex. Italie: 'symboleLangue' sera à remplacer par 'it' dans ce qui suit
	- Importez les fichiers /usr/share/ekd/locale/ekd.pot et /usr/share/ekd/locale/ekdDoc.pot depuis Poedit et effectuer la traduction
	- Enregistrez votre travail dans un de vos répertoires locaux sous les noms ekd.po et ekdDoc.po
		-> ekd.mo et ekdDoc.mo sont automatiquement créés
	- Ouvrez un terminal avec les droits de l'administrateur:
		# mkdir -p /usr/share/ekd/locale/symboleLangue/LC_MESSAGES/
		# cd chemin_vers_les_fichiers_de_traduction_précemment_créés
		# cp ekd*.mo /usr/share/ekd/locale/symboleLangue/LC_MESSAGES/
	- Quand vous aurez vérifié que tout à bien été traduit vous pourrez nous transmettre les fichiers ekd.po et ekdDoc.po
	- La traduction des boites de dialogue est quasi-automatique. Copiez simplement le fichier qt_symboleLangue.qm dans /usr/share/ekd/locale/translations/. Vous pouvez trouver le fichier qt_symboleLangue.qm sur votre système avec la commande:
		$ locate qt_symboleLangue.qm

