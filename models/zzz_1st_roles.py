# -*- coding: utf-8 -*-

# Populate default roles and permissions

# Set deployment_settings.base.prepopulate to 0 in Production
# (to save 1x DAL hit every page).
populate = deployment_settings.get_base_prepopulate()
if populate:
    table = db[auth.settings.table_group_name]
    # The query used here takes 2/3 the time of .count().
    if db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        populate = 0

# Add core roles as long as at least one populate setting is on
if populate > 0:

    # Shortcuts
    acl = auth.permission
    sysroles = auth.S3_SYSTEM_ROLES
    create_role = auth.s3_create_role
    update_acls = auth.s3_update_acls

    # Do not remove or change order of these 5 definitions (System Roles):

    # Administrator
    create_role("Administrator",
                "System Administrator - can access & make changes to any data",
                uid=sysroles.ADMIN,
                system=True, protected=True)

    # Authenticated (i.e. Volunteers)
    create_role("Authenticated",
                "Authenticated - all logged-in users",
                # Authenticated users can only see/edit their own PR records
                dict(c="pr", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                dict(t="pr_person", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                # Allow volunteers to manage their own Organization affiliations
                dict(t="vol_organisation", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                # Allow authenticated users to manage their personal details
                dict(c="vol", f="index", uacl=acl.READ),
                dict(c="vol", f="profile", uacl=acl.NONE, oacl=acl.ALL),
                dict(c="vol", f="skill", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                dict(c="vol", f="contact", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                # Allow authenticated users to View & Pledge to Requests (i.e. Manipulate their own Components)
                dict(c="vol", f="req_skill", uacl=acl.READ),
                dict(c="vol", f="req", uacl=acl.ALL, oacl=acl.ALL, organisation="all"), # General Delegation
                dict(c="vol", f="application", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                # But not be able to edit the request itself, by making editable=False in the controller
                dict(t="req_req", uacl=acl.READ, oacl=acl.ALL, organisation="all"), # General Delegation
                # @ToDo: Restrict Read to just own Applications
                dict(t="vol_application", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                # Allow authenticated users to view details of their tasks
                dict(c="vol", f="assignment", uacl=acl.CREATE, oacl=acl.ALL),
                # @ToDo: Restrict Read to just own Assignments
                dict(t="vol_assignment", uacl=acl.CREATE, oacl=acl.ALL),
                # Allow authenticated users to view the Skill Catalog
                dict(t="hrm_skill", uacl=acl.READ),
                uid=sysroles.AUTHENTICATED,
                protected=True)

    # Anonymous
    create_role("Anonymous",
                "Unauthenticated users",
                # Allow unauthenticated users to view the Donations page
                dict(c="don", f="index", uacl=acl.READ),
                # Allow unauthenticated users to Register
                dict(c="don", f="register", uacl=acl.READ),
                dict(c="vol", f="register", uacl=acl.READ),
                # Some menu links go here - don't know why
                dict(c="vol", f="index", uacl=acl.READ),
                # Allow unauthenticated users to view the list of organisations
                # so they can select an organisation when registering
                #dict(t="org_organisation", uacl=acl.READ),
                # Allow unauthenticated users to view Requests
                dict(c="vol", f="req_skill", uacl=acl.READ),
                #dict(t="req_skill", uacl=acl.READ),
                uid=sysroles.ANONYMOUS,
                protected=True)

    # Editor - unused for LA
    # (Primarily for Security Policy 2)
    create_role("Editor",
                "Editor - can access & make changes to any unprotected data",
                uid=sysroles.EDITOR,
                system=True, protected=True)

    # MapAdmin - unused for LA
    create_role("MapAdmin",
                "MapAdmin - allowed access to edit the MapService Catalogue",
                dict(c="gis", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="gis", f="location", uacl=acl.ALL, oacl=acl.ALL),
                uid=sysroles.MAP_ADMIN,
                system=True, protected=True)

    # -------------------------------------------------------------------------
    # LA
    # -------------------------------------------------------------------------
    create_role("Staff",
                "Staff - EOC, Field Site, ITA",
                # General Delegation
                dict(t="org_organisation", uacl=acl.ALL, oacl=acl.ALL, organisation="all"),
                # Allow staff to View Requests & check Vols In/Out
                dict(c="vol", f="req_skill", uacl=acl.READ),
                dict(c="vol", f="req", uacl=acl.ALL, oacl=acl.ALL),
                # Allow staff to check Vols In/Out
                dict(t="vol_assignment", uacl=acl.READ|acl.UPDATE, oacl=acl.ALL),
                dict(c="vol", f="activity", uacl=acl.ALL, oacl=acl.ALL),
                # But not be able to edit the request itself, by making editable=False in the controller
                dict(t="req_req", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to View Requests
                dict(c="don", f="req", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to Manage Corporations
                dict(c="don", f="organisation", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to Manage Virtual Warehouses
                dict(c="don", f="item", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to Report on Loans
                dict(c="don", f="loan", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to Manage Collections & Distributions
                dict(c="don", f="collect", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="don", f="distribute", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to access Master Data
                dict(c="master", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="event", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="hrm", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="org", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to view the Map
                dict(c="gis", uacl=acl.READ, oacl=acl.ALL),
                dict(c="project", f="activity", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to cache Map feeds
                dict(c="gis", f="cache_feed", uacl=acl.ALL, oacl=acl.ALL),
                # Allow Staff to view feature queries
                dict(c="gis", f="feature_query", uacl=acl.NONE, oacl=acl.ALL),
                # Allow Staff to view the Supply Catalogue
                dict(c="supply", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                dict(t="supply_item", uacl=acl.ALL, oacl=acl.ALL),
                dict(t="supply_catalog", uacl=acl.ALL, oacl=acl.ALL),
                dict(t="supply_catalog_item", uacl=acl.ALL, oacl=acl.ALL),
                dict(t="supply_item_category", uacl=acl.ALL, oacl=acl.ALL),
                uid="STAFF",
                system=True, protected=True)

    create_role("BOC",
                "Business Operations Center",
                dict(t="org_organisation", uacl=acl.ALL, oacl=acl.ALL, organisation="all"),
                # Allow BOC to View Requests
                dict(c="don", f="req", uacl=acl.ALL, oacl=acl.ALL),
                # But not be able to edit the request itself, by making editable=False in the controller
                dict(t="req_req", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to Manage Corporations
                dict(c="don", f="organisation", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to Manage Virtual Warehouses
                dict(c="don", f="item", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to Report on Loans
                dict(c="don", f="loan", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to Manage Collections & Distributions
                dict(c="don", f="collect", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="don", f="distribute", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to access Master Data
                dict(c="master", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="hrm", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="org", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to view the Map
                dict(c="gis", uacl=acl.READ, oacl=acl.ALL),
                dict(c="project", f="activity", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to cache Map feeds
                dict(c="gis", f="cache_feed", uacl=acl.ALL, oacl=acl.ALL),
                # Allow BOC to view feature queries
                dict(c="gis", f="feature_query", uacl=acl.NONE, oacl=acl.ALL),
                # Allow BOC to view the Supply Catalogue
                dict(c="supply", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                dict(t="supply_item", uacl=acl.ALL, oacl=acl.ALL),
                dict(t="supply_catalog", uacl=acl.ALL, oacl=acl.ALL),
                dict(t="supply_catalog_item", uacl=acl.ALL, oacl=acl.ALL),
                dict(t="supply_item_category", uacl=acl.ALL, oacl=acl.ALL),
                uid="BOC",
                system=True, protected=True)

    create_role("OrgVol",
                "Volunteer Organisations",
                # Allow vol orgs to edit their own Organisation
                dict(c="vol", f="profile", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                # Allow vol orgs to search for their HRs
                dict(c="hrm", f="human_resource", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                # Allow uacl=CREATE in Controller to be able to add Components
                dict(c="vol", f="organisation", uacl=acl.CREATE, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                # Then restrict Tables
                dict(t="org_organisation", uacl=acl.READ, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                dict(t="org_contact", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                dict(t="hrm_human_resource", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                dict(t="project_activity", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                dict(c="vol", f="activity", uacl=acl.ALL, oacl=acl.ALL),
                # Allow vol orgs to View & Pledge to Requests (i.e. Manipulate their own Components)
                dict(c="vol", f="req_skill", uacl=acl.READ),
                dict(c="vol", f="req", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="vol", f="application", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                # But not be able to edit the request itself, by making editable=False in the controller
                dict(t="req_req", uacl=acl.ALL, oacl=acl.ALL),
                # @ToDo: Restrict Read to just own Applications
                #dict(t="vol_application", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                dict(t="vol_application", uacl=acl.READ|acl.CREATE, oacl=acl.READ|acl.UPDATE),
                # Allow vol orgs to view details of their tasks
                dict(c="vol", f="assignment", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                # @ToDo: Restrict Read to just own Assignments
                #dict(t="vol_assignment", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                dict(t="vol_assignment", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                dict(c="vol", f="task_evaluation", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                dict(t="vol_task_evaluation", uacl=acl.CREATE, oacl=acl.READ|acl.UPDATE),
                # Allow vol orgs to view the Skill Catalog
                dict(t="hrm_skill", uacl=acl.READ),
                # Allow vol orgs to view the Map
                dict(c="gis", uacl=acl.READ, oacl=acl.ALL),
                dict(c="project", f="activity", uacl=acl.ALL, oacl=acl.ALL), # OrgAuth will filter out the Activities of other Orgs
                # Allow vol orgs to cache Map feeds
                dict(c="gis", f="cache_feed", uacl=acl.ALL, oacl=acl.ALL),
                # Allow vol orgs to view feature queries
                dict(c="gis", f="feature_query", uacl=acl.NONE, oacl=acl.ALL),
                uid="ORG_VOL",
                system=True, protected=True)

    create_role("OrgDon",
                "Corporations donating Resources",
                # Allow corps to edit their own Organisation
                dict(c="don", f="profile", uacl=acl.READ, oacl=acl.ALL),
                # Allow uacl=CREATE in Controller to be able to add Components
                dict(c="don", f="organisation", uacl=acl.CREATE, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                # Then restrict Tables
                dict(t="org_organisation", uacl=acl.READ, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                dict(t="org_sector", uacl=acl.READ),
                dict(t="org_contact", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                dict(t="hrm_human_resource", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                # Allow corps to update their Virtual Warehouse
                dict(t="inv_item", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                # Allow corps to make donations
                dict(t="commit", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                #dict(c="don", f="item", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                # Allow corps to view the Map
                #dict(c="gis", uacl=acl.READ, oacl=acl.ALL),
                # Allow corps to cache Map feeds
                #dict(c="gis", f="cache_feed", uacl=acl.ALL, oacl=acl.ALL),
                # Allow corps to view feature queries
                #dict(c="gis", f="feature_query", uacl=acl.NONE, oacl=acl.ALL),
                # Allow corps to view the Supply Catalogue
                dict(c="supply", uacl=acl.READ|acl.CREATE, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                dict(t="supply_item", uacl=acl.READ),
                dict(t="supply_catalog", uacl=acl.READ),
                dict(t="supply_catalog_item", uacl=acl.READ),
                dict(t="supply_item_category", uacl=acl.READ),
                uid="ORG_DON",
                system=True, protected=True)

# END =========================================================================
