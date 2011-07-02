# -*- coding: utf-8 -*-
"""
    Various function common to all Ekd modules
"""

from moteur_modules_common.EkdConfig import EkdConfig
from PyQt4.QtCore import QString

def debug( message ):
    """
        Affiche un message de sur la console en fonction du codage de la machine
    """
    if type(message) != QString :
        print "Debug:: %s" % message.encode(EkdConfig.coding)
    else :
        print "Debug:: %s" % message
