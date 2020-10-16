import os, sys, inspect
import datetime as dt

CWD = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(CWD))

from messenger.models import *

# clean tables
Session.drop_table()
User.drop_table()

# create tables
User.create_table()
Session.create_table()
