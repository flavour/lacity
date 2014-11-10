#!/usr/bin/python

# This is a script for Give2LA to have event-related data removed from the database whilst 

# Needs to be run in the web2py environment
# python web2py.py -S eden -M -R applications/eden/static/scripts/tools/archive.py

# Load all Models
s3mgr.model.load_all_models()

# Drop data for Event-related Tables
db.auth_event.truncate()
db.don_collect.truncate()
db.don_distribute.truncate()
db.event_event.truncate()
db.event_incident.truncate()
db.req_fulfill.truncate()
db.req_req.truncate()
db.req_req_item.truncate()
db.req_req_skill.truncate()
db.req_surplus_item.truncate()
db.s3_import_item.truncate()
db.s3_import_job.truncate()
db.s3_import_upload.truncate()
db.scheduler_run.truncate()
db.scheduler_worker.truncate()
db.vol_application.truncate()

db.commit()
