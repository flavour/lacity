#!/usr/bin/python

# This is a no-op script to allow a migration to occur

# Needs to be run in the web2py environment
# python web2py.py -S eden -M -R applications/eden/static/scripts/tools/noop.py

# Load all Models
s3mgr.model.load_all_models()

from s3 import S3Importer, S3ImportJob
S3Importer().define_upload_table()
ij = S3ImportJob(s3mgr, None)
ij.define_job_table()
ij.define_item_table()
