#!/usr/bin/python3
#License: WTFPL <http://www.wtfpl.net/>
#Author: zertap
import re
import configparser
import os
import shutil
from nexusscraper import NexusScraper

###----------------USER-VARIABLES----------------###

#USE FORWARD SLASHES OR DOUBLE BACKSLASHES IN PATHS!#

#cookie_path:
#  Path to your firefox cookies.sqlite
#  On windows, its usually %AppData%/Mozilla/Firefox/Profiles/<profile_id>/cookies.sqlite
#    Remember to replace <profile_id> with the one you have in the Profiles folder
cookie_path         = ""

#categories_dat_path:
#  Path to your categories.dat (you have to have one, if you don't, edit your MO categories and save before running this)
#  It is located in the MO main folder (the same folder as the .exe)
categories_dat_path = ""

#mods_path:
#  Path to your MO mods folder (For example, G:/Mod Organizer/mods)
mods_path           = ""

#only_set_missing:
#  Set this to True if you don't want to overwrite categories for mods that already have one set.
only_set_missing    = False

###------------------BEGIN-CODE------------------###

scraper         = NexusScraper(os.path.expandvars(cookie_path))
metadata        = dict()
category_parser = re.compile(r"(?P<MO_id>\d*)\|(?P<MO_cat_name>.*)\|(?P<nexus_id>\d*)\|(?P<MO_parent_id>\d*)")
categories      = dict()

print("Parsing categories from categories.dat...")
with open(os.path.expandvars(categories_dat_path)) as category_data:
    for line in category_data:
        match       = category_parser.match(line)
        mo_id       = match.group("MO_id")
        mo_catname  = match.group("MO_cat_name")
        mo_parentid = match.group("MO_parent_id")
        nexus_id    = match.group("nexus_id")

        if not nexus_id:
            nexus_id = -1
        
        categories[nexus_id] = (mo_id, mo_catname, mo_parentid)

print("Gathering metafiles...")
for root, dirnames, filenames in os.walk(os.path.expandvars(mods_path)):
    for filename in filenames:
        if filename == "meta.ini":
            metafile = os.path.join(root, filename)
            meta = configparser.ConfigParser()
            meta.read(metafile)
            metadata[metafile] = meta

print("Getting info from the Nexus and updating metafiles... (This may take a while.)")
for metafile, data in metadata.items():
    modid    = data["General"]["modid"]
    category = data["General"]["category"]

    if only_set_missing and int(category) != int(-1):
        continue
    if int(modid) <= int(0):
        continue
    
    nexus_id = scraper.get_category(modid)
    try:
        mo_cat = categories[nexus_id]
    except KeyError:
        continue

    mo_id, mo_catname, mo_parentid = mo_cat
    data["General"]["category"] = "\"%s,\"" % mo_id

    try:
        shutil.move(metafile, metafile + '.bak')
    except FileExistsError:
        shutil.copy2(metafile, metafile + '.bak')
    
    with open(metafile, 'w') as metafile:
        data.write(metafile)


print("Done! ^^")
    
