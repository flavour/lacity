# -*- coding: utf-8 -*-

"""
    Import Modules
    Configure the Database
    Instantiate Classes
"""

# Keep all S3 framework-level elements stored off here, so as to avoid polluting global namespace & to make it clear which part of the framework is being interacted with
# Avoid using this where a method parameter could be used: http://en.wikipedia.org/wiki/Anti_pattern#Programming_anti-patterns
s3 = response.s3

# Are we running in debug mode?
s3.debug = request.vars.get("debug", None) or \
                    deployment_settings.get_base_debug()

if s3.debug:
    # Needed for s3_include_debug
    import sys
import copy
import datetime
import re
import time
import traceback
import uuid

from lxml import etree

from gluon.sql import Row
from gluon.sql import SQLCustomType
from gluon.sqlhtml import RadioWidget

import gluon.contrib.simplejson as json

# All dates should be stored in UTC for Sync to work reliably
request.utcnow = datetime.datetime.utcnow()

########################
# Database Configuration
########################

migrate = deployment_settings.get_base_migrate()

if migrate:
    check_reserved = ["mysql", "postgres"]
else:
    check_reserved = None

db_string = deployment_settings.get_database_string()
if db_string[0].find("sqlite") != -1:
    db = DAL(db_string[0], check_reserved=check_reserved,
             migrate_enabled = migrate)
    # on SQLite 3.6.19+ this enables foreign key support (included in Python 2.7+)
    # db.executesql("PRAGMA foreign_keys=ON")
else:
    # Tuple (inc pool_size)
    try:
        if db_string[0].find("mysql") != -1:
            # Use MySQLdb where available (pymysql has given broken pipes)
            try:
                import MySQLdb
                from gluon.dal import MySQLAdapter
                MySQLAdapter.driver = MySQLdb
            except ImportError:
                # Fallback to pymysql
                pass
            if check_reserved:
                check_reserved = ["postgres"]
            db = DAL(db_string[0], check_reserved=check_reserved,
                     pool_size=db_string[1], migrate_enabled = migrate)
        else:
            # PostgreSQL
            if check_reserved:
                check_reserved = ["mysql"]
            db = DAL(db_string[0], check_reserved=check_reserved,
                     pool_size=db_string[1], migrate_enabled = migrate)
    except:
        db_type = db_string[0].split(":", 1)[0]
        db_location = db_string[0].split("@", 1)[1]
        raise(HTTP(503, "Cannot connect to %s Database: %s" % (db_type, db_location)))

current.db = db

#if request.env.web2py_runtime_gae:        # if running on Google App Engine
#session.connect(request, response, db=db) # Store sessions and tickets in DB
### or use the following lines to store sessions in Memcache (GAE-only)
# from gluon.contrib.memdb import MEMDB
# from google.appengine.api.memcache import Client
# session.connect(request, response, db=MEMDB(Client())

####################################################################
# Instantiate Classes from Modules                                 #
# - store instances in current to be accessible from other modules #
####################################################################

from gluon.tools import Mail
mail = Mail()
current.mail = mail
# AAA
auth = s3base.AuthS3()
current.auth = auth
s3_audit = s3base.S3Audit()
current.s3_audit = s3_audit
s3_logged_in_person = auth.s3_logged_in_person
s3_logged_in_human_resource = auth.s3_logged_in_human_resource
aURL = auth.permission.accessible_url

# Shortcuts
s3_has_role = auth.s3_has_role
s3_has_permission = auth.s3_has_permission
s3_accessible_query = auth.s3_accessible_query

# Custom classes which extend default Gluon
MENUS3 = s3base.S3Menu
crud = s3base.CrudS3()
current.crud = crud
S3Comment = s3base.S3Comment
S3DateTime = s3base.S3DateTime

from gluon.tools import Service
service = Service()

from gluon.tools import callback

# S3 Custom Validators,
# imported here into the global namespace in order
# to access them without the s3base namespace prefix
exec("from applications.%s.modules.s3.s3validators import *" % request.application)
# Faster for Production (where app-name won't change):
#from applications.eden.modules.s3.s3validators import *

# S3 Custom Utilities and Widgets
# imported here into the global namespace in order
# to access them without the s3base namespace prefix
exec("from applications.%s.modules.s3.s3utils import *" % request.application)
exec("from applications.%s.modules.s3.s3widgets import *" % request.application)
# Faster for Production (where app-name won't change):
#from applications.eden.modules.s3.s3utils import *
#from applications.eden.modules.s3.s3widgets import *

# VITA
vita = s3base.S3Vita()
current.vita = vita

# GIS Module
gis = s3base.GIS()
current.gis = gis

# S3RequestManager
s3.crud = Storage()
s3mgr = s3base.S3RequestManager()
current.manager = s3mgr

# MSG
msg = s3base.S3Msg()
current.msg = msg

# Tracking System
s3tracker = s3base.S3Tracker()
current.s3tracker = s3tracker

# -----------------------------------------------------------------------------
def s3_auth_on_login(form):
    """
        Actions to be performed upon successful login
            Do not redirect from here!
    """

    # S3XRC last seen records (rcvars)
    s3mgr.clear_session()

    # Session-owned records
    if "owned_records" in session:
        del session["owned_records"]

    # HRM session vars
    if "hrm" in session:
        del session["hrm"]

# -----------------------------------------------------------------------------
def s3_auth_on_logout(user):
    """
        Actions to be performed after logout
            Do not redirect from here!
    """

    # S3XRC last seen records (rcvars)
    s3mgr.clear_session()

    # HRM session vars
    if "hrm" in session:
        del session["hrm"]

    # Reset UTC offset
    try:
        del session.s3["utc_offset"]
    except:
        pass

# END
# *****************************************************************************
