# -*- coding: utf-8 -*-
"""
    1st RUN:

    - Import the S3 Framework Extensions
    - If needed, copy deployment specific templates to the live installation.
      Developers: note that the templates are version-controlled, while their
                  site-specific copies are not (to avoid leaking of sensitive
                  or irrelevant information into the repository).
                  If you add something new to these files, you should also
                  make the change at deployment-templates and commit it.
"""
import os
from gluon import current
from gluon.storage import Storage
from gluon.contrib.simplejson.ordered_dict import OrderedDict

current.cache = cache

# Import the S3 Framework
import s3 as s3base
# Per-request values, e.g. for views, can be stored here to avoid conflict
# with web2py data.
response.s3 = Storage()
response.s3.gis = Storage()  # Defined early for use by S3Config.

deployment_settings = s3base.S3Config()
current.deployment_settings = deployment_settings

copied_from_template = False

dst_path = os.path.join("applications", request.application, "models", "000_config.py")
try:
    os.stat(dst_path)
except OSError:
    # not found, copy from template
    import shutil
    shutil.copy(os.path.join("applications", request.application, "deployment-templates", "models", "000_config.py"), dst_path)
    copied_from_template = True

if copied_from_template:
    raise HTTP(501, body="The following file was copied from templates and should be edited: models/000_config.py")

