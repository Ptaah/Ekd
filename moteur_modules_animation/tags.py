#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from moteur_modules_animation.mplayer import getParamVideo
from moteur_modules_common.EkdConfig import EkdConfig
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint

class Tags:
        MAX_TAGS = 6
        DEFAULT_TAGS = ["Title", "Artist", "Genre", "Subject", "Copyright", "Comments"]
        def __init__(self, fichier):
            infosTagNom = None
            self.fichier = fichier
            info = []
            tags_name = []
            infosTagNom = {}
            tags_raw = {}
            self.tags = {}
            for i in range(Tags.MAX_TAGS) :
                info.append("ID_CLIP_INFO_NAME%d" % i)

            getParamVideo(self.fichier, info, infosTagNom)

            # Setup the tags array to gather all tags from a video
            for i in range(Tags.MAX_TAGS) :
                try :
                    tags_name.append(" %s:" % infosTagNom[info[i]])
                except KeyError:
                    pass
            getParamVideo(self.fichier, tags_name, tags_raw)

            # Clean the dictionary keys
            for k in tags_raw.keys():
                # Filter to take into account only the tags managed by
                # mencoder
                clean_tag = k.strip(": ")
                # Correct the strange behaviour on some mplayer version
                # which encode Title as Name
                # http://ekd.tuxfamily.org/bugs/index.php?do=details&task_id=60&project=2
                if clean_tag == "Name" or clean_tag == "Title" :
                    self.tags["Title"] = tags_raw[k].strip()
                elif clean_tag in Tags.DEFAULT_TAGS :
                    self.tags[clean_tag] = tags_raw[k].strip()
            EkdPrint(u"Ensemble des tags de la vidéo :")
            EkdPrint(u"%s" % self.tags)

        def __str__(self):
            return "%s" % self.tags

        def __getitem__(self, index):
            return self.tags[index]

        def get_tags(self):
            return self.tags

        def delTag(self, t):
            del self.tags[t]

        def addTag(self, t, value):
            self.tags[t] = value

        def setTag(self, t, value):
            self.tags[t] = value

if __name__ == "__main__" :
    try :
        t = Tags(sys.argv[1])
    except IndexError:
        EkdPrint(u"Usage : %s <filename>" % sys.argv[0])
