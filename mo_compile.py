#!/usr/bin/python
"""
# This script generate the binary .mo files.
# .mo files are needed to translate the Ekd interface
#
# How does it work :
#  - search all po files in locale
#  - for each file compile it with msgfmt if the .po source file is newer
#    than the already existing .mo file
"""
import glob, os

###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

# Find *.po
source_files = glob.glob("locale/??_??/LC_MESSAGES/*.po")

# Generate *.mo files
for po_file in source_files :
    mo_file = "%s.mo" % po_file.split('.')[0]
    if not os.path.exists(mo_file) or \
            os.stat(po_file).st_mtime > os.stat(mo_file).st_mtime :
        #print "Updating %s" % mo_file
        EkdPrint(u"Updating %s" % mo_file)
        os.system("./msgfmt.py -o %s %s" % (mo_file, po_file))
