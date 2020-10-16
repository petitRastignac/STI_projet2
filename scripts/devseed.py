# ---------------------------
#Fichier : models.py
#Date : 14.10.2020
#But : Supprimer et recréer les tables puis créer un admin
#Remarque :
#------------------------------

import os, sys, inspect
import datetime as dt

CWD = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(CWD))

from messenger.models import *
from messenger.security import hash_pw

# clean tables
Session.drop_table()
Message.drop_table()
User.drop_table()

# create tables
User.create_table()
Session.create_table()
Message.create_table()

# create one admin
User.insert(True, 'admin', 'admin', 'admin', hash_pw('admin'))