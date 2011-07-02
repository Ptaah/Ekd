#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser, os, getpass
from xml.dom import minidom
from xml.dom.minidom import Document
from PyQt4.QtCore import QDir, QObject, Qt
from PyQt4.QtGui import QStyleFactory

class EkdConfig(QObject):
    if os.name == 'nt':
        defaultLocation = unicode('windows' + os.sep + 'config.ekd')
        coding = "cp1252"
    else :
        defaultLocation = unicode(QDir.homePath() + os.sep + '.config' +
                                  os.sep + 'ekd' + os.sep + 'config.ekd')
        coding = "utf-8"

    location = unicode(QDir.homePath() + os.sep + '.config' +
                                  os.sep + 'ekd' + os.sep + 'config.ekd')

    configuration = None

    # -------------------------------------------------------------------------
    # En suivant l'idée de Florent sur la liste lprod (très bonne idée et justifiée):
    # "Je me suis rendu compte que tu mettais le traitement dans le répertoire /tmp,
    # je pense que c'est risqué. Il vaut mieux le mettre dans ~/tmp. Généralement (et
    # c'est mon cas) j'accorde plus de place aux données qu'au système. Dans notre cas,
    # le fichier final devrait faire 7,9 Go et ma racine / ne dispose que de 6,1 Go"
    # -------------------------------------------------------------------------
    # On pourra toujours revenir à la normale si problème il y avait --> j'ai juste
    # laissé toute la section en commentaire plus bas.
    # -------------------------------------------------------------------------

    # Pour windows uniquement
    if os.name == 'nt':
        temp = os.path.expanduser('~') + os.sep + "ekd_tmp"
    # Pour Linux et MacOSX
    elif os.name in ['posix', 'mac']:
        temp = os.path.expanduser('~') + os.sep + ".ekd_tmp"


    defaultConf=u"""\
            <ekdconfig>
                    <general>
                        <boite_de_dialogue_de_fermeture>1</boite_de_dialogue_de_fermeture>
                        <sauvegarder_parametres>2</sauvegarder_parametres>
                        <charger_split>0</charger_split>
                        <show_warning_messages>"""+ str(Qt.Checked) +"""</show_warning_messages>
                        <effacer_config>0</effacer_config>
                        <temporaire>""" + temp + """</temporaire>
                        <qtstyle>Cleanlooks</qtstyle>
                        <video_input_path>""" + os.path.expanduser('~') + os.sep + """</video_input_path>
                        <image_input_path>""" + os.path.expanduser('~') + os.sep + """</image_input_path>
                        <sound_input_path>""" + os.path.expanduser('~') + os.sep + """</sound_input_path>
                        <video_output_path>""" + os.path.expanduser('~') + os.sep + """</video_output_path>
                        <image_output_path>""" + os.path.expanduser('~') + os.sep + """</image_output_path>
                        <sound_output_path>""" + os.path.expanduser('~') + os.sep + """</sound_output_path>
                        <show_hidden_files>0</show_hidden_files>
                        <ignore_case>0</ignore_case>
                        <display_mode>auto</display_mode>
                        <interval_speed>2.0</interval_speed>
                    </general>
                    <animation_encodage_general>
			<codec>copie</codec>
			<codec_mov_ffmpeg>94</codec_mov_ffmpeg>
			<codecmotionjpeg>94</codecmotionjpeg>
                        <codecoggtheora>5</codecoggtheora>
                        <codec_vob_ffmpeg>94</codec_vob_ffmpeg>
                        <codecmpeg2>94</codecmpeg2>
			<codecdivx4>94</codecdivx4>
                        <codecmpeg1>94</codecmpeg1>
                        <macromediaflashvideo>94</macromediaflashvideo>
                        <codecwmv2>94</codecwmv2>
                    </animation_encodage_general>
		    <animation_encodage_general_bitrate_video>
			<codec_mov_ffmpeg>1200</codec_mov_ffmpeg>
			<codecmotionjpeg>1200</codecmotionjpeg>
			<codecmpeg2>1200</codecmpeg2>
		    	<codech264mpeg4>1200</codech264mpeg4>
			<codech264mpeg4_ext_h264>1200</codech264mpeg4_ext_h264>
			<codecdivx4>1200</codecdivx4>
			<codecxvid>1200</codecxvid>
			<codecmpeg1>1200</codecmpeg1>
			<macromediaflashvideo>500</macromediaflashvideo>
			<codecwmv2>1200</codecwmv2>
		    </animation_encodage_general_bitrate_video>
                    <animation_encodage_web>
                        <codec>youtube_16/9_HQ</codec>
                    </animation_encodage_web>
                    <animation_encodage_hd>
                        <codec>hd_1920x1080_mov__pcm_s16be__16/9</codec>
                    </animation_encodage_hd>
                    <animation_encodage_avchd>
                        <codec>0</codec>
                        <resolution>0</resolution>
			<spec_DNxHD>0</spec_DNxHD>
			<audio_DNxHD>0</audio_DNxHD>
                        <images_par_seconde>25</images_par_seconde>
                        <qualite>2</qualite>
                    </animation_encodage_avchd>
                    <animation_filtresvideo>
                        <codec>niveaudegris</codec>
                        <valeur_bruit_luma>23</valeur_bruit_luma>
                        <valeur_bruit_chroma>25</valeur_bruit_chroma>
                        <type_bruit_luma>bruituniforme</type_bruit_luma>
                        <type_bruit_chroma>bruituniforme</type_bruit_chroma>
                        <luminosite>0</luminosite>
                        <contraste>0</contraste>
                        <decouper_largeur>800</decouper_largeur>
                        <decouper_hauteur>600</decouper_hauteur>
                        <decouper_position_largeur>0</decouper_position_largeur>
                        <decouper_position_hauteur>0</decouper_position_hauteur>
                        <couleur>0</couleur>
                        <saturation>0</saturation>
                        <flou_boite_rayon>1</flou_boite_rayon>
                        <flou_boite_puissance>1</flou_boite_puissance>
                        <resolution_redim_largeur>640</resolution_redim_largeur>
                        <resolution_redim_hauteur>480</resolution_redim_hauteur>
                        <codec>tournervideo</codec>
                        <codec>desentrelacer</codec>
                    </animation_filtresvideo>
                    <animation_separer_audio_et_video>
                        <type_extraction>video_audio</type_extraction>
                    </animation_separer_audio_et_video>
                    <animation_convertir_des_images_en_video>
                        <codec>mpeg1video</codec>
                        <nbr_img_sec>25</nbr_img_sec>
                        <nbr_img_sec_mpeg1video>25</nbr_img_sec_mpeg1video>
                    </animation_convertir_des_images_en_video>
                    <animation_convertir_une_video_en_images>
                    </animation_convertir_une_video_en_images>
                    <animation_decouper_une_video>
                    </animation_decouper_une_video>
                    <animation_montage_video_seul>
                        <type_ordre_montage>sans_ordre_alpha</type_ordre_montage>
                    </animation_montage_video_seul>
                    <animation_montage_video_et_audio>
                        <type_ordre_montage>sans_ordre_alpha</type_ordre_montage>
                    </animation_montage_video_et_audio>
                    <animation_conversion_video_16_9_4_3>
                        <type>16_9</type>
                    </animation_conversion_video_16_9_4_3>
                    <animation_reglages_divers>
                        <spin>22</spin>
                    </animation_reglages_divers>
		    <animation_tag_video>
		    </animation_tag_video>
                    <image_divers_infos>
                    </image_divers_infos>
                    <image_filtres_image>
                        <filtre>vieux_films</filtre>
                        <pointillisme>impulse</pointillisme>
                        <couleurs_predefinies>bleu_roi</couleurs_predefinies>
                        <evanescence>fond_blanc_lignes_noires</evanescence>
                        <negatif>negatif_couleur</negatif>
                        <encadre_photo>noir</encadre_photo>
                        <laplacien_1>laplacien_1_noir_et_blanc</laplacien_1>
                        <contraste_couleur>6</contraste_couleur>
                        <sepia>60</sepia>
                        <charcoal_traits_noirs>1</charcoal_traits_noirs>
                        <edge>40</edge>
                        <huile>1</huile>
                        <gamma>1</gamma>
                        <fonce_clair>100</fonce_clair>
                        <liquidite>6</liquidite>
                        <bas_relief>1</bas_relief>
                        <charcoal_crayon_1>1</charcoal_crayon_1>
                        <spread_crayon_1>1</spread_crayon_1>
                        <radius>1</radius>
                        <sigma>1</sigma>
                        <precision_trait>1</precision_trait>
                        <largeur_trait>1</largeur_trait>
                        <seuillage_bas>1</seuillage_bas>
                        <seuillage_haut>128</seuillage_haut>
                        <intensite_du_trait_bd_1>28</intensite_du_trait_bd_1>
                        <reduction_couleur>2</reduction_couleur>
                        <peinture_huile>6</peinture_huile>
                        <couleur_11></couleur_11>
                        <couleur_12></couleur_12>
                        <couleur_13></couleur_13>
                        <couleur_21></couleur_21>
                        <couleur_22></couleur_22>
                        <couleur_23></couleur_23>
                        <couleur_31></couleur_31>
                        <couleur_32></couleur_32>
                        <couleur_33></couleur_33>
                        <taille_mini_forme>14</taille_mini_forme>
                        <taille_maxi_forme>18</taille_maxi_forme>
                        <coul_omb_lum_a_la_coul_11></coul_omb_lum_a_la_coul_11>
                        <coul_omb_lum_a_la_coul_12></coul_omb_lum_a_la_coul_12>
                        <coul_omb_lum_a_la_coul_21></coul_omb_lum_a_la_coul_21>
                        <coul_omb_lum_a_la_coul_22></coul_omb_lum_a_la_coul_22>
                        <coul_omb_lum_a_la_coul_31></coul_omb_lum_a_la_coul_31>
                        <coul_omb_lum_a_la_coul_32></coul_omb_lum_a_la_coul_32>
                        <coul_omb_lum_a_la_coul_41></coul_omb_lum_a_la_coul_41>
                        <coul_omb_lum_a_la_coul_42></coul_omb_lum_a_la_coul_42>
                        <intensite_du_trait_bd_2>28</intensite_du_trait_bd_2>
                        <flou_couleurs>8</flou_couleurs>
                        <coul_contour_couleur_00></coul_contour_couleur_00>
                        <coul_contour_couleur_11></coul_contour_couleur_11>
                        <coul_contour_couleur_12></coul_contour_couleur_12>
                        <coul_contour_couleur_13></coul_contour_couleur_13>
                        <coul_contour_couleur_21></coul_contour_couleur_21>
                        <coul_contour_couleur_22></coul_contour_couleur_22>
                        <coul_contour_couleur_23></coul_contour_couleur_23>
                        <coul_contour_couleur_31></coul_contour_couleur_31>
                        <coul_contour_couleur_32></coul_contour_couleur_32>
                        <coul_contour_couleur_33></coul_contour_couleur_33>
                        <coul_contour_couleur_41></coul_contour_couleur_41>
                        <coul_contour_couleur_42></coul_contour_couleur_42>
                        <coul_contour_couleur_43></coul_contour_couleur_43>
			<iterations_cubisme_analytique>240</iterations_cubisme_analytique>
			<taille_bloc_cubisme_analytique>8</taille_bloc_cubisme_analytique>
			<angle_cubisme_analytique>114</angle_cubisme_analytique>
			<nbre_img_ligne_andy_warhol>3</nbre_img_ligne_andy_warhol>
			<nbre_img_colonne_andy_warhol>3</nbre_img_colonne_andy_warhol>
			<lissage_andy_warhol>1</lissage_andy_warhol>
			<couleur_andy_warhol>40</couleur_andy_warhol>
			<seuil_coul_correct_yeux_rouges>80</seuil_coul_correct_yeux_rouges>
			<lissage_correct_yeux_rouges>1</lissage_correct_yeux_rouges>
			<attenuation_correct_yeux_rouges>1</attenuation_correct_yeux_rouges>
			<resol_x_bull_en_tableau>1024</resol_x_bull_en_tableau>
			<resol_y_bull_en_tableau>1024</resol_y_bull_en_tableau>
			<rayon_bull_en_tableau>70</rayon_bull_en_tableau>
			<nbre_par_ligne_bull_en_tableau>3</nbre_par_ligne_bull_en_tableau>
			<nbre_par_ligne_bull_en_tableau>3</nbre_par_ligne_bull_en_tableau>
			<larg_bordur_bull_en_tableau>25</larg_bordur_bull_en_tableau>
			<haut_bordur_bull_en_tableau>25</haut_bordur_bull_en_tableau>
			<larg_final_img_bull_en_tableau>800</larg_final_img_bull_en_tableau>
			<haut_final_img_bull_en_tableau>800</haut_final_img_bull_en_tableau>
			<pos_doubles_planete_1>2</pos_doubles_planete_1>
			<rayon_planete_1>100</rayon_planete_1>
			<dilatation_planete_1>60</dilatation_planete_1>
			<larg_final_img_planete_1>800</larg_final_img_planete_1>
			<haut_final_img_planete_1>800</haut_final_img_planete_1>
			<abstraction_expressionnisme>2</abstraction_expressionnisme>
			<lissage_expressionnisme>180</lissage_expressionnisme>
			<couleur_expressionnisme>340</couleur_expressionnisme>
			<dessin_13_amplitude>1874</dessin_13_amplitude>
			<dessin_14_taille>3</dessin_14_taille>
			<taill_bord_polaroid>10</taill_bord_polaroid>
			<taill_larg_ombre_polaroid>4</taill_larg_ombre_polaroid>
			<taill_haut_ombre_polaroid>4</taill_haut_ombre_polaroid>
			<rot_photo_polaroid>10</rot_photo_polaroid>
			<taill_larg_ombre_vieil_photo>4</taill_larg_ombre_vieil_photo>
			<taill_haut_ombre_vieil_photo>4</taill_haut_ombre_vieil_photo>
			<rot_photo_vieil_photo>10</rot_photo_vieil_photo>
			<pos_larg_oeilleton>50</pos_larg_oeilleton>
			<pos_haut_oeilleton>50</pos_haut_oeilleton>
			<rayon_oeilleton>50</rayon_oeilleton>
			<amplitude_oeilleton>1</amplitude_oeilleton>
			<vision_thermique_min>1</vision_thermique_min>
			<vision_thermique_max>255</vision_thermique_max>
			<nett_trait_bord_tendu>1</nett_trait_bord_tendu>
			<fluct_coul_bord_tendu>1</fluct_coul_bord_tendu>
			<transp_trait_bord_tendu>1</transp_trait_bord_tendu>
			<floutage_bord_tendu>1</floutage_bord_tendu>
			<coul_debut_bord_tendu>1</coul_debut_bord_tendu>
			<coul_fin_img_bord_tendu>255</coul_fin_img_bord_tendu>
			<erosion>5</erosion>
			<dilatation>5</dilatation>
			<amplitude_figuration_libre>1238</amplitude_figuration_libre>
			<abstraction_figuration_libre>1</abstraction_figuration_libre>
			<douc_peint_figuration_libre>150</douc_peint_figuration_libre>
			<couleur_figuration_libre>200</couleur_figuration_libre>
			<seuil_bord_figuration_libre>310</seuil_bord_figuration_libre>
			<douc_seg_figuration_libre>1</douc_seg_figuration_libre>
			<intensite_du_trait_peint_aguarelle>22</intensite_du_trait_peint_aguarelle>
			<flou_couleurs_peint_aguarelle>7</flou_couleurs_peint_aguarelle>
			<amplitude_peint_aguarelle>80</amplitude_peint_aguarelle>
			<abstraction_peint_aguarelle>4</abstraction_peint_aguarelle>
			<douc_peint_peint_aguarelle>202</douc_peint_peint_aguarelle>
			<couleur_peint_aguarelle>254</couleur_peint_aguarelle>
			<seuil_bord_peint_aguarelle>310</seuil_bord_peint_aguarelle>
			<douc_seg_peint_aguarelle>102</douc_seg_peint_aguarelle>
			<opacite_ombre_peint_aguarelle>100</opacite_ombre_peint_aguarelle>
			<tail_bord_horiz_peint_aguarelle>20</tail_bord_horiz_peint_aguarelle>
			<tail_bord_vertic_peint_aguarelle>20</tail_bord_vertic_peint_aguarelle>
			<distors_bord_peint_aguarelle>30</distors_bord_peint_aguarelle>
			<douceur_bord_peint_aguarelle>3</douceur_bord_peint_aguarelle>
			<palette_coul_effet_flamme>4</palette_coul_effet_flamme>
			<amplitude_effet_flamme>478</amplitude_effet_flamme>
			<echantillonnage_effet_flamme>145</echantillonnage_effet_flamme>
			<lissage_effet_flamme>43</lissage_effet_flamme>
			<opacite_effet_flamme>2</opacite_effet_flamme>
			<bord_effet_flamme>15</bord_effet_flamme>
			<amplitude_liss_anisotropique_effet_flamme>594</amplitude_liss_anisotropique_effet_flamme>
			<nettete_effet_flamme>83</nettete_effet_flamme>
			<anisotropie_effet_flamme>92</anisotropie_effet_flamme>
			<gradiant_lissage_effet_flamme>50</gradiant_lissage_effet_flamme>
			<tenseur_lissage_effet_flamme>360</tenseur_lissage_effet_flamme>
			<precision_spatiale_effet_flamme>57</precision_spatiale_effet_flamme>
			<precision_angulaire_effet_flamme>33</precision_angulaire_effet_flamme>
			<valeur_precision_effet_flamme>200</valeur_precision_effet_flamme>
			<repetitions_effet_flamme>2</repetitions_effet_flamme>
                    </image_filtres_image>
                    <image_masque_alpha_3d>
                        <methode>methode1</methode>
                        <masque>masque_alpha</masque>
                        <qualite>bonne</qualite>
                        <nettete>par_defaut</nettete>
                        <reglage>fond_bleu</reglage>
                        <forme_fond>fon_noir_for_blanch</forme_fond>
                        <teinte_debut></teinte_debut>
                        <saturation_debut></saturation_debut>
                        <luminosite></luminosite>
                        <saturation_fin></saturation_fin>
                        <teinte_fin></teinte_fin>
                    </image_masque_alpha_3d>
                    <image_pour_le_web>
                        <methode>gif_anime</methode>
                        <nombre_morceaux_vertical></nombre_morceaux_vertical>
                        <nombre_morceaux_horizontal></nombre_morceaux_horizontal>
                        <nombre_couleurs></nombre_couleurs>
                        <nouvelle_largeur></nouvelle_largeur>
                        <delai></delai>
                    </image_pour_le_web>
                    <image_redimensionner>
                        <methode>gif_anime</methode>
                        <largeur_ratio></largeur_ratio>
                        <largeur_sans_ratio></largeur_sans_ratio>
                        <longueur_sans_ratio></longueur_sans_ratio>
                    </image_redimensionner>
                    <image_changer_format>
                        <format>.jpg</format>
                    </image_changer_format>
                    <image_planche-contact>
                        <format>.jpg</format>
                        <orientation>form_port</orientation>
			<taille>taille_planche_842x595</taille>
                        <couleur_fond>blanc</couleur_fond>
                        <passage_image>1</passage_image>
                        <largeur_marge>10</largeur_marge>
                        <nombre_images_largeur>4</nombre_images_largeur>
                        <nombre_images_longueur>6</nombre_images_longueur>
                    </image_planche-contact>
                    <image_multiplication>
                        <mult_duree_sec></mult_duree_sec>
                        <mult_nbre_img_sec></mult_nbre_img_sec>
                        <mult_format_ext>.jpg</mult_format_ext>
                        <mult_action_a_effectuer></mult_action_a_effectuer>
                    </image_multiplication>
                    <image_image_composite>
                    </image_image_composite>
                    <image_transition_spirale>
                    </image_transition_spirale>
                    <image_transition_fondu>
                    </image_transition_fondu>
                    <image_renommer>
                        <increment>1</increment>
                        <classement></classement>
                    </image_renommer>
                    <son_musique_encodage>
                        <format>wav</format>
                    </son_musique_encodage>
                    <son_joindre_multiple_fichier_audio>
                        <format>wav</format>
                    </son_joindre_multiple_fichier_audio>
                    <son_normaliser_convertir_musique_ou_son>
                        <format>wav</format>
                    </son_normaliser_convertir_musique_ou_son>
                    <son_decoupe_musiques_et_sons>
                        <format>wav</format>
                    </son_decoupe_musiques_et_sons>
             <videoporamaconfig>
                 <imgmgkdir>/usr/bin/</imgmgkdir>
                 <mjpegtoolsdir>/usr/bin/</mjpegtoolsdir>
                 <soxdir>/usr/bin/</soxdir>
                 <time>5</time>
                 <typet>1</typet>
                 <speedt>2</speedt>
                 <bgcolor>0</bgcolor>
            </videoporamaconfig>
            </ekdconfig>
        """


    def init(configPath = None):
        if not configPath:
            configPath = EkdConfig.defaultLocation

        EkdConfig.initVars()
        EkdConfig.location = configPath
        EkdConfig.creationFichierConf()
        EkdConfig.configuration = minidom.parseString(EkdConfig.defaultConf)
        EkdConfig.completerFichierConf()

    init = staticmethod(init)

    def initVars():
        ### Sections de la configuration
        EkdConfig.SECTIONS = {
            u"general" : _(u"Général"),
            u"animation_encodage_general" : _(u"Vidéo:Encodage général"),
            u"animation_encodage_web" : _(u"Vidéo:Encodage Web"),
            u"animation_encodage_hd" : _(u"Vidéo:Encodage HD"),
            u"animation_filtresvideo" : _(u"Vidéo:Filtres"),
            u"animation_montage_video_seul": _(u"Vidéo:Montage vidéo seulement"),
            u"animation_montage_video_et_audio": _(u"Vidéo:Montage vidéo et audio"),
            u"animation_decouper_une_video" : _(u"Vidéo:Découpage d'une vidéo"),
            u"animation_separer_audio_et_video": _(u"Vidéo:Séparation audio-vidéo"),
            u"animation_convertir_des_images_en_video" : _(u"Vidéo:Conversion d'images en vidéo"),
            u"animation_convertir_une_video_en_images" : _(u"Vidéo:Conversion d'une vidéo en images"),
            u"animation_reglages_divers": _(u"Vidéo:Nombre d'image par seconde"),
            u"animation_conversion_video_16_9_4_3" : _(u"Vidéo:Convertir une vidéo en 16/9 ou 4/3"),
            u"videoporamaconfig" : _(u"Vidéo:Diaporama d'images en vidéo"),
            u"image_planche-contact": _(u"Image:Planche contact"),
            u"image_changer_format": _(u"Image:Changer de format"),
            u"image_redimensionner" : _(u"Image:Redimension"),
            u"image_renommer": _(u"Image:Renommage d'images"),
            u"image_pour_le_web" : _(u"Image:Pour le Web "),
            u"image_multiplication": _(u"Image:Multiplication d'images"),
            u"image_filtres_image": _(u"Image:Filtres d'images"),
            u"image_masque_alpha_3d" : _(u"Image:Masque alpha 3D"),
            u"image_image_composite" : _(u"Image:Image composite"),
            u"image_transition_fondu" : _(u"Image:Transition fondu enchainé"),
            u"image_transition_spirale" : _(u"Image:Transition spirale"),
            u"son_musique_encodage": _(u"Audio:Transcodage audio"),
            u"son_joindre_multiple_fichier_audio": _(u"Audio:Joindre plusieurs fichiers audio"),
            u"son_decoupe_musiques_et_sons" : _(u"Audio:Découpe dans un fichier audio"),
            u"son_normaliser_convertir_musique_ou_son": _(u"Audio:Nomaliser et convertir un fichier audio")
            }
        ### Sections de la configuration
        EkdConfig.PROPERTIES = {
            u"charger_split": _(u"Charger la disposition des fenêtres"),
            u"display_mode": _(u"Mode d'affichage"),
            u"show_warning_messages": _(u"Voir les avertissements"),
            u"effacer_config": _(u"Réinitialiser la configuration"),
            u"boite_de_dialogue_de_fermeture": _(u"Confirmer la sauvegarde avant fermeture"),
            u'sauvegarder_parametres': _(u"Sauvegarder les paramêtres"),
            u"temporaire": _(u"Répertoire temporaire"),
            u"video_input_path": _(u"Répertoire de chargement des vidéos"),
            u"sound_input_path": _(u"Répertoire de chargement des sons"),
            u"image_input_path": _(u"Répertoire de chargement des images"),
            u"video_output_path": _(u"Répertoire de sauvegarde des vidéos"),
            u"sound_output_path": _(u"Répertoire de sauvegarde des sons"),
            u"image_output_path": _(u"Répertoire de sauvegarde des images"),
            u"show_hidden_files": _(u"Afficher les fichiers cachés"),
            u"imgmgkdir": _(u"Répertoire de ffmpeg"), u"soxdir": _(u"Répertoire de SoX"),
            u"mjpegtoolsdir": _(u"Répertoire de mjpegtools"),
            u"macromediaflashvideo": _(u"MacroMediaFlash"),
            u"codecmpeg1": _(u"Mpeg1"),  u"codecwmv2": _(u"WMV2"),
            u"codecmpeg2": _(u"Mpeg2"), u"codecdivx4": _(u"Divx4"),
            u"codecmotionjpeg": _(u"Motion Jpeg"), u"codecoggtheora": _(u"Ogg Theora"),
            u"codec_vob_ffmpeg": _(u"FFMpeg"), u"mult_nbre_img_sec": _(u"Nombre d'images par seconde"),
            u"mult_duree_sec": _(u"Durée"), u"nbr_img_sec": _(u"Nombre d'images par seconde"),
            u"nbr_img_sec_mpeg1video": _(u"Nombre d'images par seconde"), u"increment": _(u"Incrémentation") ,
            u"delai": _(u"Délai"), u"nombre_couleurs": _(u"Nomde de couleurs"), u"nombre_morceaux_horizontal": _(u"Nombre de morceaux horizontal"),
            u"nombre_morceaux_vertical": _(u"Nombre de morceaux vertical"),
            u"nouvelle_largeur": _(u"Nouvel largeur"), u"spin": _(u"Spin"), u"largeur_sans_ratio": _(u"Largeur sans ratio"),
            u"longueur_sans_ratio": _(u"Longueur sans ratio"),
            u"largeur_ratio": _(u"Largeur avec ratio"), u"valeur_bruit_luma": _(u"Valeur du bruit luma"),
            u"valeur_bruit_chroma": _(u"Valeur du bruit chroma"), u"luminosite": _(u"Luminosité"),
            u"contraste": _(u"Contraste"), u"decouper_largeur": _(u"Découper la largeur"), u"decouper_hauteur": _(u"Découper la hauteur"),
            u"decouper_position_largeur": _(u"Découper la position en largeur"),
            u"decouper_position_hauteur": _(u"Découper la position en hauteur"), u"couleur": _(u"Couleur"), u"saturation": _(u"Saturation"),
            u"flou_boite_rayon": _(u"Rayon du flou"),
            u"flou_boite_puissance": _(u"Puissance"), u"resolution_redim_largeur": _(u"Redimention largeur"),
                                                        u"resolution_redim_hauteur": _(u"Redimention hauteur"),
            u"contraste_couleur": _(u"Contraste"), u"sepia": _(u"Sépia"), u"charcoal_traits_noirs": _(u"Traits noirs"), u"edge": _(u"Edge"),
            u"huile": _(u"Huile"), u"gamma": _(u"Gamma"), u"fonce_clair": _(u"Foncé clair"), u"liquidite": _(u"Liquidité"),
            u"bas_relief": _(u"Bas relief"), u"charcoal_crayon": _(u"Crayon charcoal"), u"spread_crayon": _(u"Crayon spread"),
            u"radius": _(u"Rayon"), u"sigma": _(u"Sigma"), u"precision_trait": _(u"Précision du trait"),
            u"largeur_trait": _(u"Largeur du trait"), u"seuillage_bas": _(u"Seuillage bas"), u"seuillage_haut": _(u"Seuillage haut"),
            u"intensite_du_trait": _(u"Intensité du trait"), u"reduction_couleur": _(u"Réduction de la couleur"),
            u"peinture_huile": _(u"Peinture à l'huile"), u"passage_image": _(u"Passage de l'image"),
            u"largeur_marge": _(u"Largeur de l'image"), u"nombre_images_largeur": _(u"Nombre d'images en largeur"),
            u"nombre_images_longueur": _(u"Nombre d'images en longueur"), u"time": _(u"Temps"),
            u"typet": _(u"Type transition"), u"speedt": _(u"Vitesse de transition"),
            u"qtstyle": _(u"Style QT"), u"codec": _(u"Codec"),
            u"bgcolor": _(u"Couleur de fond"), u"couleur_11": _(u"Couleur 11"), u"couleur_12": _(u"Couleur 12"),
            u"couleur_13": _(u"Couleur 13"), u"couleur_21": _(u"Couleur 21"), u"couleur_22": _(u"Couleur 22"),
            u"couleur_23": _(u"Couleur 23"), u"couleur_31": _(u"Couleur 31"),
            u"couleur_32": _(u"Couleur 32"), u"couleur_33": _(u"Couleur 33"),
            u"taille_mini_forme": _(u"Taille minimale"), u"taille_maxi_forme": _(u"Taille maximale"),
            u"coul_omb_lum_a_la_coul_11": _(u"Ombre Couleur 11"), u"coul_omb_lum_a_la_coul_12": _(u"Ombre Couleur 12"),
            u"coul_omb_lum_a_la_coul_21": _(u"Ombre Couleur 21"),
            u"coul_omb_lum_a_la_coul_22": _(u"Ombre Couleur 22"),
            u"coul_omb_lum_a_la_coul_31": _(u"Ombre Couleur 31"),
            u"coul_omb_lum_a_la_coul_32": _(u"Ombre Couleur 32"),
            u"coul_omb_lum_a_la_coul_41": _(u"Ombre Couleur 41"),
            u"coul_omb_lum_a_la_coul_42": _(u"Ombre Couleur 42"),
            u"coul_contour_couleur_00": _(u"Contour couleur 00"),
            u"coul_contour_couleur_11": _(u"Contour couleur 11"),
            u"coul_contour_couleur_12": _(u"Contour couleur 12"),
            u"coul_contour_couleur_13": _(u"Contour couleur 13"),
            u"coul_contour_couleur_21": _(u"Contour couleur 21"),
            u"coul_contour_couleur_22": _(u"Contour couleur 22"),
            u"coul_contour_couleur_23": _(u"Contour couleur 23"),
            u"coul_contour_couleur_31": _(u"Contour couleur 31"),
            u"coul_contour_couleur_32": _(u"Contour couleur 32"),
            u"coul_contour_couleur_33": _(u"Contour couleur 33"),
            u"coul_contour_couleur_41": _(u"Contour couleur 41"),
            u"coul_contour_couleur_42": _(u"Contour couleur 42"),
            u"coul_contour_couleur_43": _(u"Contour couleur 43"),
            u"ignore_case": _(u"Tri sensible à la casse"),
            u"interval_speed": _(u"Vitesse de lecture des images (ms)")
            }

        ## Chk ne peut pas être enlevé car utilisé dans vidéoporama, il faut supprimer les référence de cette
        ## option dans videoporama avant de pouvoir la retirer - Travail effectué -> chk retiré
        EkdConfig.PROPERTIES_MASK = [ u"sources", u"codec", u"chk", u"sauvegarder_parametres" ]
        if os.name == 'nt':
            EkdConfig.PROPERTIES_MASK.extend([u"imgmgkdir", u"mjpegtoolsdir", u"soxdir", u"show_hidden_files"])
        EkdConfig.SECTION_MASK = [
            u"animation_encodage_general", u"animation_encodage_web", u"animation_encodage_hd",
            u"animation_filtresvideo", u"animation_montage_video_seul",
            u"animation_montage_video_et_audio", u"animation_decouper_une_video" ,
            u"animation_separer_audio_et_video", u"animation_convertir_des_images_en_video" ,
            u"animation_convertir_une_video_en_images", u"animation_reglages_divers",
            u"animation_conversion_video_16_9_4_3", u"image_planche-contact",
            u"image_changer_format", u"image_redimensionner", u"image_renommer",u"image_image_composite",
            u"image_transition_fondu", u"image_transition_spirale", u"image_pour_le_web", u"image_multiplication",
            u"image_filtres_image",  u"image_masque_alpha_3d", u"son_musique_encodage",
            u"son_joindre_multiple_fichier_audio",  u"son_decoupe_musiques_et_sons",
            u"son_normaliser_convertir_musique_ou_son"
            ]

        EkdConfig.BOOLEAN_PROPERTIES = [ u"charger_split", u"effacer_config", u"boite_de_dialogue_de_fermeture",
                               u'sauvegarder_parametres', u"show_hidden_files", u"show_warning_messages", u"ignore_case" ]

        EkdConfig.STYLE_PROPERTIES = { u"qtstyle": map(str, QStyleFactory.keys()),
                                       u"codec" : ['copie', 'avirawsanscompression', 'codec_dv_ffmpeg',
                                                   'codec_mov_ffmpeg', 'codec_hfyu_ffmpeg', 'codecmotionjpeg',
                                                   'codecoggtheora', 'codec_vob_ffmpeg', 'codecmpeg2',
                                                   'codech264mpeg4', 'codech264mpeg4_ext_h264', 'codecxvid',
                                                   'codecdivx4', 'codecmpeg1', 'macromediaflashvideo',
                                                   'codecwmv2', 'codec_3GP_ffmpeg', 'codec_AMV_ffmpeg'],
                                       u"display_mode": [ "auto", "1280x800", "1024x768", "1024x600", "800x600", "800x480"]
                                       }
        EkdConfig.CODEC_PROPERTIES = {
            u"speedt": [u'Très lent', u'Lent', u'Moyen', u'Moyen+', u'Rapide', u'Très rapide'],
            u"typet": [u'Aucun', u'Fondu', u'Apparaît', u'Disparaît', u'Slide', u'Cube', u'Pousser', u'Luma' ] }

        EkdConfig.PATH_PROPERTIES = [ u"temporaire", u"video_input_path", u"sound_input_path", u"image_input_path",
                                      u"video_output_path", u"sound_output_path", u"image_output_path",
                                      u"imgmgkdir", u"soxdir", u"mjpegtoolsdir"]

        EkdConfig.COLOR_PROPERTIES = [ u"bgcolor", u"couleur_11", u"couleur_12",
                                       u"couleur_13", u"couleur_21", u"couleur_22", u"couleur_23", u"couleur_31",
                                       u"couleur_32", u"couleur_33", u"taille_mini_forme", u"taille_maxi_forme",
                                       u"coul_omb_lum_a_la_coul_11", u"coul_omb_lum_a_la_coul_12", u"coul_omb_lum_a_la_coul_21",
                                       u"coul_omb_lum_a_la_coul_22", u"coul_omb_lum_a_la_coul_31", u"coul_omb_lum_a_la_coul_32",
                                       u"coul_omb_lum_a_la_coul_41", u"coul_omb_lum_a_la_coul_42",
                                       u"coul_contour_couleur_00", u"coul_contour_couleur_11", u"coul_contour_couleur_12",
                                       u"coul_contour_couleur_13", u"coul_contour_couleur_21", u"coul_contour_couleur_22",
                                       u"coul_contour_couleur_23", u"coul_contour_couleur_31", u"coul_contour_couleur_32",
                                       u"coul_contour_couleur_33", u"coul_contour_couleur_41", u"coul_contour_couleur_42",
                                       u"coul_contour_couleur_43"]

        EkdConfig.NUM_PROPERTIES = [ u"macromediaflashvideo", u"codecmpeg1", u"codecmpeg2", u"codecdivx4", u"codecwmv2",
                           u"codecmotionjpeg", u"codecoggtheora", u"codec_vob_ffmpeg", u"mult_nbre_img_sec",
                           u"mult_duree_sec", u"nbr_img_sec", u"nbr_img_sec_mpeg1video", u"increment", u"delai",
                           u"nombre_couleurs", u"nombre_morceaux_horizontal", u"nombre_morceaux_vertical",
                           u"nouvelle_largeur", u"spin", u"largeur_sans_ratio", u"longueur_sans_ratio",
                           u"largeur_ratio", u"valeur_bruit_luma", u"valeur_bruit_chroma", u"luminosite",
                           u"contraste", u"decouper_largeur", u"decouper_hauteur", u"decouper_position_largeur",
                           u"decouper_position_hauteur", u"couleur", u"saturation", u"flou_boite_rayon",
                           u"flou_boite_puissance", u"resolution_redim_largeur", u"resolution_redim_hauteur",
                           u"contraste_couleur", u"sepia", u"charcoal_traits_noirs", u"edge",
                           u"huile", u"gamma", u"fonce_clair", u"liquidite", u"bas_relief",
                           u"charcoal_crayon", u"spread_crayon", u"radius", u"sigma", u"precision_trait",
                           u"largeur_trait", u"seuillage_bas", u"seuillage_haut", u"intensite_du_trait",
                           u"reduction_couleur", u"peinture_huile", u"passage_image",
                           u"largeur_marge", u"nombre_images_largeur", u"nombre_images_longueur",
                           u"time" ]

        EkdConfig.TIME_PROPERTIES = [ u"interval_speed" ]
    initVars = staticmethod(initVars)

    def creationFichierConf(config=None):
        """
        Crée le fichier de configuration s'il n'existe pas, on le crée
        """
        if not config:
            config = EkdConfig.defaultLocation
        try:
            file(config)
        except:
            configdir = os.path.dirname(config)
            if not os.path.isdir(configdir):
                os.makedirs(configdir)
            fichierOb=open(config,'w')
            default = EkdConfig.newSection("ekdconfig")
            print >>fichierOb, default.toprettyxml(encoding=EkdConfig.coding)
            fichierOb.close()
    creationFichierConf = staticmethod(creationFichierConf)

    def completerConf(config):
        """
        On sépare la gestion de la complétion de la configuration
        """

        for mainsec in EkdConfig.configuration.childNodes[0].childNodes:
            # Pour chacune des sections par défaut
            for section in mainsec.childNodes:
                sectionName = section.parentNode.tagName.strip()

                # Est-ce que la section existe dans le fichier de conf ?
                try:
                    EkdConfig.getConfigSection(sectionName, config)
                except:
                    print u"DEBUG:: On crée la section ".encode(EkdConfig.coding), sectionName
                    config.childNodes[0].appendChild(EkdConfig.newSection(sectionName))

                # Vérification des propriétés:
                #       * Récupérer l'ensemble des propriété par défaut
                #       * Pour chaque propriété de la conf par défaut, si la propriété n'existe pas dans la conf spécifiée, il faut la créer
                for option in section.childNodes: # est-ce que toutes les options existent?
                    optionName = option.parentNode.tagName.strip()
                    try:
                        EkdConfig.get(sectionName, optionName, config)
                    except:
                        try :
                            value = EkdConfig.get(sectionName, optionName).strip()
                        except:
                            print u"Pb lorse de la récupération de : ".encode(EkdConfig.coding), sectionName, " - ", optionName
                        print "DEBUG:: Option non trouvée, on la définie à : ".encode(EkdConfig.coding), value
                        EkdConfig.set(sectionName, optionName, value, config)
    completerConf = staticmethod(completerConf)

    def completerFichierConf(configfile=None):
        """
        Si le fichier de configuration est incomplet on y ajoute des paramètres
        """

        if not configfile:
            configfile = EkdConfig.location
            print u"DEBUG:: Completion du fichier de config".encode(EkdConfig.coding), configfile
        try:
            userConf = minidom.parse(configfile)
        except Exception, e:
            print u"Problème lors du parsing de la configuration : ".encode(EkdConfig.coding), configfile
            userConf = EkdConfig.configuration

        EkdConfig.completerConf(userConf)
        EkdConfig.configuration = userConf
        EkdConfig.save(configfile, EkdConfig.configuration)
    completerFichierConf = staticmethod(completerFichierConf)

    def save(configfile=None, config=None):
        """
        Sauve le fichier de configuration
        """
        if configfile == None :
            configfile = EkdConfig.location
        if config == None :
            config = EkdConfig.configuration

        ## Nettoyage avant écriture
        EkdConfig.cleanConfig("\t", "\n", config)
        try :
            fd=open(configfile,'w')
            fd.write(config.toprettyxml(encoding=EkdConfig.coding))
            fd.close()
        except Exception, e:
            print u"Erreur lors de la sauvegarde du fichier de configuration : ".encode(EkdConfig.coding), configfile
            raise e
    save = staticmethod(save)


    def cleanConfig(indent="",newl="", config=None):
        '''
        Cette fonction permet de nettoyer, des espaces supplémentaires, la configuration avant de l'écrire
        '''
        if config == None :
            config = EkdConfig.configuration
        node=config.documentElement
        EkdConfig.cleanNode(node,indent,newl)
    cleanConfig = staticmethod(cleanConfig)

    def cleanNode(currentNode,indent,newl):
        '''
        Cette fonction permet de nettoyer, des espaces supplémentaires, des noeuds de la configuration avant de l'écrire
        '''
        filter=indent+newl
        if currentNode.hasChildNodes:
            for node in currentNode.childNodes:
                if node.nodeType == 3:
                    node.nodeValue = node.nodeValue.lstrip(filter).strip(filter)
                    if node.nodeValue == "":
                        currentNode.removeChild(node)
        for node in currentNode.childNodes:
            EkdConfig.cleanNode(node,indent,newl)
    cleanNode = staticmethod(cleanNode)


    def get(sectionName, proprieteName, config=None):
        """
        Renvoie la valeur de la propriété choisie dans la section donnée
        """
        if not config:
            config = EkdConfig.configuration
        try :
            domSection = EkdConfig.getConfigSection(sectionName, config)
            value = EkdConfig.getConfigPropriete(domSection, proprieteName).childNodes[0].data.strip()
            #print "Debug: Configuration value : section[", sectionName,"] propriete [", proprieteName,"] value[", value, "]"
            return unicode(value)
        except Exception, e :
            print u"Erreur dans la récupération de la propriété :".encode(EkdConfig.coding), proprieteName, " dans la section : ", sectionName
            raise e
    get = staticmethod(get)

    def set(sectionName, proprieteName, value, config=None):
        """
        Définie une nouvelle valeur pour la propriété donnée dans la section choisie
        """
        if config == None :
            config = EkdConfig.configuration
        try:
            domSection = EkdConfig.getConfigSection(sectionName, config)
        except:
            #print " Debug:: On crée la section ", sectionName, " qui n'existait pas !"
            domSection = config.childNodes[0].childNodes[0].appendChild(EkdConfig.newSection(sectionName))
        try:
            oldProp = EkdConfig.getConfigPropriete(domSection, proprieteName)
        except:
            #print "---- On va certainement définir une propriété toute neuve ----"
            None

        newProp = EkdConfig.newPropriete(proprieteName, value)
        #print "Debug: Setting configuration value : section[", sectionName,"] propriete [", proprieteName,"] value[", value, "]"
        try:
            domSection.removeChild(oldProp)
        except:
            #print "---- Impossible de supprimer une propriété inexistante ----"
            None
        domSection.appendChild(newProp)
    set = staticmethod(set)

    def newPropriete(proprieteName, value):
        """
        Crée une nouvelle propriété text Xml
        """
        try:
            doc = minidom.Document()
            prop = doc.createElement(proprieteName)
            val = doc.createTextNode(unicode(value))
            prop.appendChild(val)
            return prop
        except Exception, e:
            print u"Erreur dans la création de la propriété :".encode(EkdConfig.coding), proprieteName
            raise e
    newPropriete = staticmethod(newPropriete)

    def newSection(sectionName):
        """
        Crée une nouvelle section dans le fichier de configuration courant
        """
        doc = minidom.Document()
        section = doc.createElement(sectionName)
        return section
    newSection = staticmethod(newSection)

    def getConfigSection(sectionName, config=None):
        """
        Renvoie la section Xml correspondant au nom de section donnée
        """
        if not config:
            config = EkdConfig.configuration
        try:
            return config.getElementsByTagName(sectionName)[0]
        except Exception, e:
            print u"Erreur dans la récupération de la section :".encode(EkdConfig.coding), sectionName
            raise  e
    getConfigSection = staticmethod(getConfigSection)

    def getConfigPropriete(section, proprieteName):
        """
        Renvoie la propriété Xml de la section donnée
        """
        try:
            return section.getElementsByTagName(proprieteName)[0]
        except Exception, e:
            raise e
    getConfigPropriete = staticmethod(getConfigPropriete)

    def printConfig():
        """
        Affiche la sortie xml de la configuration actuelle
        """
        print EkdConfig.configuration.toprettyxml(encoding=EkdConfig.coding)
    printConfig = staticmethod(printConfig)

    def getTempDir():
        """
        Renvoie le répertoire temporaire pour l'utilisateur courant
        """
        tmpBase = EkdConfig.get("general", "temporaire")
        tmp = tmpBase + os.sep + "ekd_" + getpass.getuser()
        return unicode(tmp)
    getTempDir = staticmethod(getTempDir)

    def getAllProperties(section):
        """
        Renvoie un tableau associatif contenant l'ensemble des propriétés de la section
        en paramètre
        """
        sectionProperties = {}
        try:
            proprietes = section.getElementsByTagName("*")
        except Exception, e:
            raise e
        #print proprietes
        for prop in proprietes :
            try:
                sectionProperties[prop.tagName] = prop.childNodes[0].data.strip()
            except :
                sectionProperties[prop.tagName] = ""
        return sectionProperties
    getAllProperties = staticmethod(getAllProperties)

    def purge(config=None):
        """
        Supprime le fichier de configuration
        """
        if not config:
            config = EkdConfig.defaultLocation
        try:
            os.unlink(config)
        except OSError, e:
            print _(u"Impossible de purger la configuration %s" % e)
    purge = staticmethod(purge)
