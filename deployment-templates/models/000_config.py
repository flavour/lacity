#Z -*- coding: utf-8 -*-

"""
    Deployment settings
    All settings which are typically edited for a deployment should be done here
    Deployers shouldn't typically need to edit any other files.
    NOTE FOR DEVELOPERS:
    /models/000_config.py is NOT in the BZR repository, as this file will be changed
    during deployments.
    To for changes to be committed to trunk, please also edit:
    deployment-templates/models/000_config.py
"""

# Remind admin to edit this file
FINISHED_EDITING_CONFIG_FILE = False # change to True after you finish editing this file
if not FINISHED_EDITING_CONFIG_FILE:
    raise HTTP(501, body="Please edit models/000_config.py first")

# Database settings
deployment_settings.database.db_type = "sqlite"
deployment_settings.database.host = "localhost"
deployment_settings.database.port = None # use default
deployment_settings.database.database = "sahana"
deployment_settings.database.username = "sahana"
deployment_settings.database.password = "password" # NB Web2Py doesn't like passwords with an @ in them
deployment_settings.database.pool_size = 30

# Authentication settings
# This setting should be changed _before_ registering the 1st user
deployment_settings.auth.hmac_key = "akeytochange"
# These settings should be changed _after_ the 1st (admin) user is
# registered in order to secure the deployment
# Should users be allowed to register themselves?
deployment_settings.security.self_registration = True
deployment_settings.auth.registration_requires_verification = False
deployment_settings.auth.registration_requires_approval = False

# Uncomment this to request the Mobile Phone when a user registers
deployment_settings.auth.registration_requests_mobile_phone = False
# Uncomment this to have the Mobile Phone selection during registration be mandatory
#deployment_settings.auth.registration_mobile_phone_mandatory = True
# Uncomment this to request the Organisation when a user registers
#deployment_settings.auth.registration_requests_organisation = True
# Uncomment this to have the Organisation selection during registration be mandatory
#deployment_settings.auth.registration_organisation_mandatory = True
# Uncomment this to have the Organisation input hidden unless the user enters a non-whitelisted domain
#deployment_settings.auth.registration_organisation_hidden = True
# Uncomment this to direct newly-registered users to their volunteer page to be able to add extra details
# NB This requires Verification/Approval to be Off
#deployment_settings.auth.registration_volunteer = True
# Uncomment this to allow users to Login using OpenID
deployment_settings.auth.openid = False

# Always notify the approver of a new (verified) user, even if the user is automatically approved
deployment_settings.auth.always_notify_approver = False

# Base settings
deployment_settings.base.system_name = T("Give2LA")
deployment_settings.base.system_name_short = T("Give2LA")

# Set this to the Public URL of the instance
deployment_settings.base.public_url = "http://127.0.0.1:8000"

# Switch to "False" in Production for a Performance gain
# (need to set to "True" again when Table definitions are changed)
deployment_settings.base.migrate = True

# Enable/disable pre-population of the database.
# Should be non-zero on 1st_run to pre-populate the database
# - unless doing a manual DB migration
# Then set to zero in Production (to save 1x DAL hit every page)
# NOTE: the web UI will not be accessible while the DB is empty,
# instead run:
#   python web2py.py -N -S eden -M
# to create the db structure, then exit and re-import the data.
# This is a simple status flag with the following meanings
# 0 - No pre-population
# 1 - Base data entered in the database
# 2 - Regression (data used by the regression tests)
# 3 - Scalability testing
# 4-9 Reserved
# 10 - User (data required by the user typically for specialised test)
# 11-19 Reserved
# 20+ Demo (Data required for a default demo)
#     Each subsequent Demos can take any unique number >= 20
#     The actual demo will be defined by the file demo_folders.cfg
deployment_settings.base.prepopulate = 1 # LA Demo is 22

# Set this to True to use Content Delivery Networks to speed up Internet-facing sites
deployment_settings.base.cdn = False

# Set this to True to switch to Debug mode
# Debug mode means that uncompressed CSS/JS files are loaded
# JS Debug messages are also available in the Console
# can also load an individual page in debug mode by appending URL with
# ?debug=1
deployment_settings.base.debug = False

# Email settings
# Outbound server
deployment_settings.mail.server = "127.0.0.1:25"
#deployment_settings.mail.tls = True
# Useful for Windows Laptops:
#deployment_settings.mail.server = "smtp.gmail.com:587"
#deployment_settings.mail.tls = True
#deployment_settings.mail.login = "username:password"
# From Address
deployment_settings.mail.sender = "'Give2LA' <emd.admin@lacity.org>"
# Default email address to which requests to approve new user accounts gets sent
# This can be overridden for specific domains/organisations via the auth_domain table
#deployment_settings.mail.approver = "emd.admin@lacity.org"
deployment_settings.mail.approver = "test@aidiq.com"
# Daily Limit on Sending of emails
deployment_settings.mail.limit = 1000

# Frontpage settings
# RSS feeds
#deployment_settings.frontpage.rss = [
#    {"title": "ReadyLA",
#     "url": "http://twitter.com/statuses/user_timeline/34666476.rss"
#    },
#    {"title": "Red Cross LA",
#     "url": "http://twitter.com/statuses/user_timeline/14720319.rss"
#    },
#    {"title": "LAFD",
#     "url": "http://twitter.com/statuses/user_timeline/823860.rss"
#    }
#]

# L10n settings
#deployment_settings.L10n.default_country_code = 1
# Languages used in the deployment (used for Language Toolbar & GIS Locations)
# http://www.loc.gov/standards/iso639-2/php/code_list.php
deployment_settings.L10n.languages = OrderedDict([
    ("en", "English"),
    ("es", "Español"),
    ("tl", "Tagalog"),
    ("zh-tw", "中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("vi", "Tiếng Việt"),
])
# Default language for Language Toolbar (& GIS Locations in future)
#deployment_settings.L10n.default_language = "en"
# Display the language toolbar
#deployment_settings.L10n.display_toolbar = True
# Default timezone for users
deployment_settings.L10n.utc_offset = "UTC -0700"
# Uncomment these to use US-style dates in English (localisations can still convert to local format)
deployment_settings.L10n.date_format = T("%m-%d-%Y")
# NB this gets overridden for STAFF in 00_settings.py
deployment_settings.L10n.time_format = T("%I:%M:%S %p")
deployment_settings.L10n.datetime_format = T("%m-%d-%Y %I:%M:%S %p")
# Religions used in Person Registry
# @ToDo: find a better code
# http://eden.sahanafoundation.org/ticket/594
deployment_settings.L10n.religions = {
    "none":T("none"),
    "christian":T("Christian"),
    "muslim":T("Muslim"),
    "jewish":T("Jewish"),
    "buddhist":T("Buddhist"),
    "hindu":T("Hindu"),
    "bahai":T("Bahai"),
    "other":T("other")
}
# Make last name in person/user records mandatory
deployment_settings.L10n.mandatory_lastname = True

# Finance settings
#deployment_settings.fin.currencies = {
#    "USD" :T("United States Dollars"),
#    "EUR" :T("Euros"),
#    "GBP" :T("Great British Pounds")
#}
#deployment_settings.fin.currency_default = "USD"
#deployment_settings.fin.currency_readable = True
deployment_settings.fin.currency_writable = False # False currently breaks things 

# PDF settings
# Default page size for reports (defaults to A4)
deployment_settings.base.paper_size = T("Letter")
# Location of Logo used in pdfs headers
deployment_settings.ui.pdf_logo = "static/img/la/LA-BlackWhite.JPG"

# GIS (Map) settings
# Hide the Map-based selection tool in the Location Selector
#deployment_settings.gis.map_selector = False
# Hide LatLon boxes in the Location Selector
deployment_settings.gis.latlon_selector = False
# Use Building Names as a separate field in Street Addresses?
deployment_settings.gis.building_name = False
# Display Resources recorded to Admin-Level Locations on the map
# @ToDo: Move into gis_config?
#deployment_settings.gis.display_L0 = False
# Currently unused
#deployment_settings.gis.display_L1 = True

# Map settings that relate to locale, such as the number and names of the
# location hierarchy levels, are now in gis_config.  The site-wide gis_config
# will be populated from the settings here.
deployment_settings.gis.location_hierarchy = OrderedDict([
    ("L0", T("Country")),
    ("L1", T("State")),
    ("L2", T("County")),
    ("L3", T("City")),
    ("L4", T("Neighborhood")),
])
# Maximum hierarchy level to allow for any map configuration.
deployment_settings.gis.max_allowed_hierarchy_level = "L4"
deployment_settings.gis.default_symbology = "US"
# @ToDo: The id numbers of the projection and marker don't convey
# which they are to whoever's setting up the site. Web setup should
# deal with this.
# Default map configuration values for the site:
deployment_settings.gis.default_config_values = Storage(
    name = "Site Map Configuration",
    # Where the map is centered:
    lat = "34.0149248298",
    lon = "-118.107934628",
    # How close to zoom in initially -- larger is closer.
    zoom = 9,
    zoom_levels = 22,
    projection_id = 1,
    marker_id = 1,
    map_height = 600,
    map_width = 700,
    # Rough bounds for locations, used by onvalidation to filter out lon, lat
    # which are obviously wrong (e.g. missing minus sign) or far outside the
    # intended region.
    min_lon = -180,
    min_lat = -90,
    max_lon = 180,
    max_lat = 90,
    # Optional source of map tiles.
    #wmsbrowser_name = "Web Map Service",
    #wmsbrowser_url = "http://geo.eden.sahanafoundation.org/geoserver/wms?service=WMS&request=GetCapabilities",
    search_level = "L3",
    # Should locations that link to a hierarchy location be required to link
    # at the deepest level? (False means they can have a hierarchy location of
    # any level as parent.)
    strict_hierarchy = False,
    # Should all specific locations (e.g. addresses, waypoints) be required to
    # link to where they are in the location hierarchy?
    location_parent_required = False
)
# Set this if there will be multiple areas in which work is being done,
# and a menu to select among them is wanted. With this on, any map
# configuration that is designated as being available in the menu will appear
#deployment_settings.gis.menu = T("Maps")
# Maximum Marker Size
# (takes effect only on display)
#deployment_settings.gis.marker_max_height = 35
#deployment_settings.gis.marker_max_width = 30
# Duplicate Features so that they show wrapped across the Date Line?
# Points only for now
# lon<0 have a duplicate at lon+360
# lon>0 have a duplicate at lon-360
#deployment_settings.gis.duplicate_features = False
# Mouse Position: 'normal', 'mgrs' or 'off'
#deployment_settings.gis.mouse_position = "normal"

# Use 'soft' deletes
#deployment_settings.security.archive_not_delete = True

# AAA Settings

# Security Policy
# http://eden.sahanafoundation.org/wiki/S3AAA#System-widePolicy
# 1: Simple (default): Global as Reader, Authenticated as Editor
# 2: Editor role required for Update/Delete, unless record owned by session
# 3: Apply Controller ACLs
# 4: Apply both Controller & Function ACLs
# 5: Apply Controller, Function & Table ACLs
# 6: Apply Controller, Function, Table & Organisation ACLs
# 7: Apply Controller, Function, Table, Organisation & Facility ACLs
#
deployment_settings.security.policy = 6 # Organisation-ACLs
#acl = deployment_settings.aaa.acl
#deployment_settings.aaa.default_uacl =  acl.READ   # User ACL
#deployment_settings.aaa.default_oacl =  acl.CREATE | acl.READ | acl.UPDATE # Owner ACL

# Lock-down access to Map Editing
deployment_settings.security.map = True
# Allow non-MapAdmins to edit hierarchy locations? Defaults to True if not set.
# (Permissions can be set per-country within a gis_config)
#deployment_settings.gis.edit_Lx = False
# Allow non-MapAdmins to edit group locations? Defaults to False if not set.
#deployment_settings.gis.edit_GR = True
# Note that editing of locations used as regions for the Regions menu is always
# restricted to MapAdmins.

# Audit settings
# We Audit if either the Global or Module asks us to
# (ignore gracefully if module author hasn't implemented this)
# NB Auditing (especially Reads) slows system down & consumes diskspace
#deployment_settings.security.audit_write = False
#deployment_settings.security.audit_read = False

# UI/Workflow options
# Should user be prompted to save before navigating away?
#deployment_settings.ui.navigate_away_confirm = False
# Should user be prompted to confirm actions?
#deployment_settings.ui.confirm = False
# Should potentially large dropdowns be turned into autocompletes?
# (unused currently)
#deployment_settings.ui.autocomplete = True
#deployment_settings.ui.update_label = T("Edit")
# Enable this for a UN-style deployment
#deployment_settings.ui.cluster = True
# Enable this to use the label 'Camp' instead of 'Shelter'
#deployment_settings.ui.camp = True
# Enable this to change the label for 'Mobile Phone'
deployment_settings.ui.label_mobile_phone = T("Cell Phone")
# Enable this to change the label for 'Postcode'
deployment_settings.ui.label_postcode = T("ZIP Code")

# Request
deployment_settings.req.type_inv_label = T("Donations")
deployment_settings.req.type_hrm_label = T("Volunteers")
#Allow the status for requests to be set manually,
#rather than just automatically from commitments and shipments
deployment_settings.req.status_writable = False
deployment_settings.req.quantities_writable = True
deployment_settings.req.skill_quantities_writable = False
deployment_settings.req.show_quantity_transit = False
deployment_settings.req.multiple_req_items = False
deployment_settings.req.use_commit = True
# For Testing:
#deployment_settings.req.webeoc_is_master = False

# Custom Crud Strings for specific req_req types
deployment_settings.req.req_crud_strings = dict()
# req_req Crud Strings for Item Request (type=1)
ADD_ITEM_REQUEST = T("Make a Request for Donations")
LIST_ITEM_REQUEST = T("List Requests for Donations")
deployment_settings.req.req_crud_strings[1] = Storage(
    title_create = ADD_ITEM_REQUEST,
    title_display = T("Request for Donations Details"),
    title_list = LIST_ITEM_REQUEST,
    title_update = T("Edit Request for Donations"),
    title_search = T("Search Requests for Donations"),
    subtitle_create = ADD_ITEM_REQUEST,
    subtitle_list = T("Requests for Donations"),
    label_list_button = LIST_ITEM_REQUEST,
    label_create_button = ADD_ITEM_REQUEST,
    label_delete_button = T("Delete Request for Donations"),
    msg_record_created = T("Request for Donations Added"),
    msg_record_modified = T("Request for Donations Updated"),
    msg_record_deleted = T("Request for Donations Canceled"),
    msg_list_empty = T("No Requests for Donations"))
# req_req Crud Strings for People Request (type=3)
ADD_PEOPLE_REQUEST = T("Make a Request for Volunteers")
LIST_PEOPLE_REQUEST = T("List Requests for Volunteers")
deployment_settings.req.req_crud_strings[3] = Storage(
    title_create = ADD_PEOPLE_REQUEST,
    title_display = T("Request for Volunteers Details"),
    title_list = LIST_PEOPLE_REQUEST,
    title_update = T("Edit Request for Volunteers"),
    title_search = T("Search Requests for Volunteers"),
    subtitle_create = ADD_PEOPLE_REQUEST,
    subtitle_list = T("Requests for Volunteers"),
    label_list_button = LIST_PEOPLE_REQUEST,
    label_create_button = ADD_PEOPLE_REQUEST,
    label_delete_button = T("Delete Request for Volunteers"),
    msg_record_created = T("Request for Volunteers Added"),
    msg_record_modified = T("Request for Volunteers Updated"),
    msg_record_deleted = T("Request for Volunteers Canceled"),
    msg_list_empty = T("No Requests for Volunteers"))

# Human Resource Management
#deployment_settings.hrm.email_required = False

# Terms of Service to be able to Register on the system
deployment_settings.options.terms_of_service = T("Terms of Service.")
# Should we use internal Support Requests?
#deployment_settings.options.support_requests = True

# Comment/uncomment modules here to disable/enable them
# Modules menu is defined in 01_menu.py
deployment_settings.modules = OrderedDict([
    # Core modules which shouldn't be disabled
    ("default", Storage(
            name_nice = T("Home"),
            restricted = False, # Use ACLs to control access to this module
            access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
            module_type = 0     # This item is not shown in the menu
        )),
    ("admin", Storage(
            name_nice = T("Administration"),
            restricted = True,
            module_type = 0     # This item is handled separately for the menu
        )),
    ("sync", Storage(
            name_nice = T("Synchronization"),
            restricted = True,
            module_type = 0     # This item is handled separately for the menu
        )),
    ("appadmin", Storage(
            name_nice = T("Administration"),
            restricted = True,
            module_type = 0     # No Menu
        )),
    ("errors", Storage(
            name_nice = T("Ticket Viewer"),
            restricted = False,
            module_type = 0     # No Menu
        )),
    ("gis", Storage(
            name_nice = T("Map"),
            restricted = True,
            module_type = 6,     # 6th item in the menu
        )),
    ("pr", Storage(
            name_nice = T("Person Registry"),
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
            module_type = 10
        )),
    ("org", Storage(
            name_nice = T("Organization Registry"),
            restricted = True,
            module_type = 10
        )),
    # All modules below here should be possible to disable safely
    ("hrm", Storage(
            name_nice = T("Contacts"),
            restricted = True,
            module_type = 4,
        )),
    ("msg", Storage(
            name_nice = T("Messaging"),
            restricted = True,
            module_type = 10,
        )),
    ("supply", Storage(
            name_nice = T("Supply Chain Management"),
            restricted = True,
            module_type = None, # Not displayed
        )),
    #("inv", Storage(
    #        name_nice = T("Donations Management"),
    #        restricted = True,
    #        module_type = 3
    #    )),
    ("req", Storage(
            name_nice = T("Requests"),
            restricted = True,
            module_type = 2,
        )),
    # Event depends on HRM
    ("event", Storage(
            name_nice = T("Events"),
            restricted = True,
            module_type = 10,
        )),
    # Don depends on Supply & Req
    ("don", Storage(
            name_nice = T("Donate"),
            restricted = True,
            module_type = 0,
        )),
    # Vol depends on HRM
    ("vol", Storage(
            name_nice = T("My Volunteering"),
            restricted = True,
            module_type = 0,
        )),
    ("master", Storage(
            name_nice = T("Master Data"),
            restricted = True,
            module_type = 5,
        )),
])
