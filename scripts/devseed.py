import os, sys, inspect
import datetime as dt

CWD = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(CWD))

from messenger.models import *

User.create_table()
