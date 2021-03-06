# -*- coding: utf-8 -*-

# 1st-run initialisation
# designed to be called from Crontab's @reboot
# however this isn't reliable (doesn't work on Win32 Service) so still in models for now...

# Deployments can change settings live via appadmin
if populate > 0:

    # Allow debug
    import sys

    # Load all Models to ensure all DB tables present
    s3mgr.model.load_all_models()

    # Add core data as long as at least one populate setting is on

    # Scheduled Tasks
    if deployment_settings.has_module("msg"):
        # Send Messages from Outbox
        # SMS every minute
        s3task.schedule_task("process_outbox",
                             vars={"contact_method":"SMS"},
                             period=60,  # seconds
                             timeout=60, # seconds
                             repeats=0   # unlimited
                            )
        # Emails every 5 minutes
        s3task.schedule_task("process_outbox",
                             vars={"contact_method":"EMAIL"},
                             period=300,  # seconds
                             timeout=300, # seconds
                             repeats=0    # unlimited
                            )

    # Person Registry
    tablename = "pr_person"
    table = db[tablename]
    # Should work for our 3 supported databases: sqlite, MySQL & PostgreSQL
    field = "first_name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % (field, tablename, field))
    field = "middle_name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % (field, tablename, field))
    field = "last_name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % (field, tablename, field))

    # Synchronisation
    table = db.sync_config
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
       table.insert()

    # Messaging Module
    if deployment_settings.has_module("msg"):
        #table = db.msg_email_settings
        #if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        #    table.insert(
        #        inbound_mail_server = "imap.gmail.com",
        #        inbound_mail_type = "imap",
        #        inbound_mail_ssl = True,
        #        inbound_mail_port = 993,
        #        inbound_mail_username = "username",
        #        inbound_mail_password = "password",
        #        inbound_mail_delete = False,
        #        #outbound_mail_server = "mail:25",
        #        #outbound_mail_from = "demo@sahanafoundation.org",
        #    )
        # Need entries for the Settings/1/Update URLs to work
        table = db.msg_setting
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( outgoing_sms_handler = "WEB_API" )
        #table = db.msg_modem_settings
        #if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        #    table.insert( modem_baud = 115200 )
        #table = db.msg_api_settings
        #if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        #    table.insert( to_variable = "to" )
        table = db.msg_smtp_to_sms_settings
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( address="changeme" )
        #table = db.msg_tropo_settings
        #if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        #    table.insert( token_messaging = "" )
        #table = db.msg_twitter_settings
        #if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        #    table.insert( pin = "" )

    # Human Resources
    #if deployment_settings.has_module("hrm"):
    #    table = db.hrm_certificate
    #    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
    #        table.insert( name = "CPA - Certified Public Accountant")
    #        table.insert( name = "CSW - Certified Social Worker")
    #        table.insert( name = "DR1 - Driver's License - Car")
    #        table.insert( name = "DR2 - Driver's License - Lt truck")
    #        table.insert( name = "DR3 - Driver's License Heavy truck")
    #        table.insert( name = "DR4 - Driver's License Bus")
    #        table.insert( name = "DR5 - Driver's License Commercial")
    #        table.insert( name = "DR6 - Driver's License Motorcycle")
    #        table.insert( name = "EMT - Emergency Medical Technician")
    #        table.insert( name = "HRO - Ham Radio Operator")
    #        table.insert( name = "LPC - Licensed Professional Counselor")
    #        table.insert( name = "LPN - Licensed Practical Nurse")
    #        table.insert( name = "LSW - Licensed Social Worker")
    #        table.insert( name = "LVN - Licensed Vocational Nurse")
    #        table.insert( name = "MD - Medical Doctor")
    #        table.insert( name = "MFT - Marriage and Family Therapist")
    #        table.insert( name = "MT - Medical Technician")
    #        table.insert( name = "PA - Physician Assistant")
    #        table.insert( name = "PSY - Psychologist")
    #        table.insert( name = "RN - Registered Nurse")

    # GIS Module
    # -CUT-

    tablename = "gis_location"
    table = db[tablename]
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # L0 Countries
        import_file = os.path.join(request.folder,
                                   "private",
                                   "import",
                                   "countries.csv")
        table.import_from_csv_file(open(import_file, "r"))
        query = (db.auth_group.uuid == sysroles.MAP_ADMIN)
        map_admin = db(query).select(db.auth_group.id,
                                     limitby=(0, 1)).first().id
        db(table.level == "L0").update(owned_by_role=map_admin)
    # Should work for our 3 supported databases: sqlite, MySQL & PostgreSQL
    field = "name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % \
        (field, tablename, field))

    # Ensure DB population committed when running through shell
    db.commit()

    # Prepopulate import (from CSV)

    # Override authorization
    auth.override = True

    # Disable table protection
    protected = s3mgr.PROTECTED
    s3mgr.PROTECTED = []

    # Additional settings for user table imports:
    s3mgr.configure("auth_user",
                    onaccept = lambda form: \
                        auth.s3_link_to_person(user=form.vars))
    s3mgr.model.add_component("auth_membership", auth_user="user_id")

    # Create the bulk Importer object
    bi = s3base.S3BulkImporter(s3mgr, s3base)

    # Allow population via shell scripts
    if not request.env.request_method:
        request.env.request_method = "GET"

    # Import data specific to the prepopulate setting
    if populate == 1:
        # Populate with the default data
        path = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "default")
        bi.perform_tasks(path)
    
    elif populate == 2:
        # Populate data for the regression tests
        path = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "regression")
        bi.perform_tasks(path)
    
    elif populate == 3:
        # Populate data for scalability testing
        # This is different from the repeatable imports that use csv files
        # This will generate millions of records of data for selected tables.
    
        # Code needs to go here to generate a large volume of test data
        pass
    
    elif populate == 10:
        # Populate data for user specific data
        path = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "user")
        bi.perform_tasks(path)
    
    elif populate >= 20:
        # Populate data for a deployment default demo
        """
            Read the demo_folders file and extract the folder for the specific demo
        """
        file = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "demo",
                            "demo_folders.cfg")
        source = open(file, "r")
        values = source.readlines()
        source.close()
        demo = ""
        for demos in values:
            # strip out the new line
            demos = demos.strip()
            if demos == "":
                continue
            # split at the comma
            details = demos.split(",")
            if len(details) == 2:
                 # remove any spaces and enclosing double quote
                index = details[0].strip('" ')
                if int(index) == populate:
                    directory = details[1].strip('" ')
                    path = os.path.join(request.folder,
                                        "private",
                                        "prepopulate",
                                        "demo",
                                        directory)
                    demo = directory
                    if os.path.exists(path):
                        bi.perform_tasks(path)
                    else:
                        print >> sys.stderr, "Unable to install demo %s no demo directory found" % index

        if demo == "":
            print >> sys.stderr, "Unable to install a demo with of an id '%s', please check 000_config and demo_folders.cfg" % populate
        else:
            print >> sys.stderr, "Installed demo '%s'" % demo

    for errorLine in bi.errorList:
        print >> sys.stderr, errorLine
    # Restore table protection
    s3mgr.PROTECTED = protected

    # Restore view
    response.view = "default/index.html"
