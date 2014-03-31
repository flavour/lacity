# -*- coding: utf-8 -*-

"""
    Global menus & breadcrumbs
"""

# Enable for Testing
# (also think about making this evaluated on-demand by shn_menu() to avoid having to process this for non-interactive calls & make the aURLs Lazy)
#def _01_menu_definitions(s3,
#                         T,
#                         auth,
#                         URL,
#                         aURL,
#                         deployment_settings,
#                         request,
#                         response,
#                         s3_has_role,
#                         ADMIN,
#                         STAFF,
#                         ORG_DON,
#                         ORG_VOL,
#                         **rest_of_environment
#                         ):
# Indent for testing
# =============================================================================
# Language Menu (available in all screens)

s3.menu_lang = [ T("Language"), True, "#"]
_menu_lang = []
for language in s3.l10n_languages.keys():
    _menu_lang.append([s3.l10n_languages[language], False, language])
s3.menu_lang.append(_menu_lang)

# -----------------------------------------------------------------------------
# Help Menu (available in all screens)
#s3.menu_help = [ T("Help"), True, "#",
#        [
#            [T("Contact us"), False,
#             URL(c="default", f="contact")],
#            [T("About"), False, URL(c="default", f="about")],
#        ]
#    ]

# -----------------------------------------------------------------------------
# Auth Menu (available in all screens)
if not auth.is_logged_in():

    login_next = URL(args=request.args, vars=request.vars)
    if request.controller == "default" and \
       request.function == "user" and \
       "_next" in request.get_vars:
           login_next = request.get_vars["_next"]

    self_registration = deployment_settings.get_security_self_registration()

    if self_registration:
        s3.menu_auth = [[T("Register"), True,
                        URL(c="vol", f="register"), None],
                        [T("Sign In"), True,
                        URL(c="default", f="user/login",
                            vars=dict(_next=login_next)),
                [
                    [T("Sign In"), False,
                     URL(c="default", f="user/login",
                         vars=dict(_next=login_next))],
                    #[T("Register"), False,
                    # URL(c="default", f="register",
                          #vars=dict(_next=login_next))],
                    [T("Lost Password"), False,
                     URL(c="default", f="user/retrieve_password")]
                ]
            ]]
    else:
        s3.menu_auth = [[T("Sign In"), True,
                        URL(c="default", f="user/login",
                            vars=dict(_next=login_next)),
                [
                    [T("Lost Password"), False,
                     URL(c="default", f="user/retrieve_password")]
                ]
            ]]
else:
    s3.menu_auth = [[auth.user.email, True, None,
            [
                [T("My Skills"), False,
                 URL("vol", "skill/my")],
                #[T("Personal Data"), False,
                # URL(c="pr", f="person",
                #     vars={"person.uid" : auth.user.person_uuid})],
                #[T("Contact details"), False,
                # URL(c="pr", f="person",
                #     args="contact",
                #     vars={"person.uid" : auth.user.person_uuid})],
                #[T("Subscriptions"), False,
                # URL(c="pr", f="person",
                #     args="pe_subscription",
                #     vars={"person.uid" : auth.user.person_uuid})],
                [T("Change Password"), False,
                 URL(c="default", f="user/change_password")],
                #["----", False, None],
                #[{"name": T("Rapid Data Entry"),
                #  "id": "rapid_toggle",
                #  "value": session.s3.rapid_data_entry is True},
                # False, URL(c="default", f="rapid")]
            ]
        ],
        [T("Sign Out"), True, URL(c="default", 
                                  f="user/logout")],
        ]
    if auth.s3_has_role("Admin"):
        pass
    elif auth.s3_has_role("ORG_VOL"):
        s3.menu_auth.append([T("Profile"), True, URL(c="vol", 
                                                     f="organisation",
                                                     args=[auth.user.organisation_id])])
    elif auth.s3_has_role("ORG_DON"):
        s3.menu_auth.append([T("Profile"), True, URL(c="don", 
                                                     f="organisation",
                                                     args=[auth.user.organisation_id])])
    elif not auth.s3_has_role("Staff"):
        s3.menu_auth.append([T("My Profile"), True, URL(c="vol", 
                                                        f="profile")])

# -----------------------------------------------------------------------------
# Menu for Admin module
# (defined here as used in several different Controller files)
admin_menu_messaging = [
            [T("Roster Email Addresses"), False,
             URL(c="admin", f="rostermail")],
            [T("Email Settings"), False,
             URL(c="msg", f="email_settings", args=[1, "update"])],
            [T("SMS Settings"), False,
             URL(c="msg", f="setting", args=[1, "update"])],
            [T("Twitter Settings"), False,
             URL(c="msg", f="twitter_settings", args=[1, "update"])],
    ]
admin_menu_options = [
    [T("Settings"), False, URL(c="admin", f="settings"), 
        admin_menu_messaging,
        # Hidden until useful again
        #[T("Edit Themes"), False, URL(c="admin", f="theme")]
    ],
    [T("User Management"), False, URL(c="admin", f="user"), [
        [T("Users"), False, URL(c="admin", f="user")],
        [T("Roles"), False, URL(c="admin", f="role")],
        #[T("Organizations"), False, URL(c="admin", f="organisation")],
        #[T("Roles"), False, URL(c="admin", f="group")],
        #[T("Membership"), False, URL(c="admin", f="membership")],
    ]],
    [T("Database"), False, URL(c="appadmin", f="index"), [
        #[T("Import"), False, URL(c="admin", f="import_file")],
        #[T("Import"), False, URL(c="admin", f="import_data")],
        #[T("Export"), False, URL(c="admin", f="export_data")],
        #[T("Import Jobs"), False, URL(c="admin", f="import_job")],
        [T("Raw Database access"), False, URL(c="appadmin", f="index")]
    ]],
    # Hidden until ready for production
    [T("Synchronization"), False, URL(c="sync", f="index"), [
        [T("Settings"), False, aURL(p="update", c="sync", f="config",
                                    args=["1", "update"])],
        [T("Repositories"), False, URL(c="sync", f="repository")],
        [T("Log"), False, URL(c="sync", f="log")],
    ]],
    #[T("Edit Application"), False,
    # URL(a="admin", c="default", f="design", args=[request.application])],
    [T("Tickets"), False, URL(c="admin", f="errors")],
    [T("Portable App"), False, URL(c="admin", f="portable")],
]

# -----------------------------------------------------------------------------
# Modules Menu (available in all Controllers)
# NB This is just a default menu - most deployments will customise this
s3.menu_modules = []
# Home always 1st
_module = deployment_settings.modules["default"]
s3.menu_modules.append([_module.name_nice, False,
                        URL(c="default", f="index")])

# Public/Volunteers/Volunteer Organisations gets this set of Menus
don_menu = [T("Donate"), False,
            URL(c="don", f="index")]
vol_menu = [T("Volunteer"), False,
            URL(c="vol", f="req_skill")]
third_menu = [T("Why?"), False,
              URL(c="default", f="why")]

if s3_has_role("Staff"):
    # Staff get this set of menus, based on Permissions
    don_menu = [T("Donations"), False,
                URL(c="don", f="req")]
    vol_menu = [T("Volunteers"), False,
                URL(c="vol", f="req")]
    third_menu = [T("Master Data"), False,
                  URL(c="master", f="index")]
elif s3_has_role("OrgDon") or s3_has_role(BOC):
    # Corporations get this menu, based on Permissions
    don_menu = [T("Donations"), False,
                URL(c="don", f="req")]

s3.menu_modules.append(don_menu)
s3.menu_modules.append(vol_menu)
s3.menu_modules.append(third_menu)
  
# Modules to hide due to insufficient permissions
#hidden_modules = auth.permission.hidden_modules()

# The Modules to display at the top level (in order)
#for module_type in [1, 2, 3, 4, 5, 6]:
#    for module in deployment_settings.modules:
#        if module in hidden_modules:
#            continue
#        _module = deployment_settings.modules[module]
#        if (_module.module_type == module_type):
#            if not _module.access:
#                s3.menu_modules.append([_module.name_nice, False,
#                                        aURL(c=module, f="index")])
#            else:
#                authorised = False
#                groups = re.split("\|", _module.access)[1:-1]
#                for group in groups:
#                    if s3_has_role(group):
#                        authorised = True
#                if authorised == True:
#                    s3.menu_modules.append([_module.name_nice, False,
#                                            URL(c=module, f="index")])

# Modules to display off the 'more' menu
#modules_submenu = []
#for module in deployment_settings.modules:
#    if module in hidden_modules:
#        continue
#    _module = deployment_settings.modules[module]
#    if (_module.module_type == 10):
#        if not _module.access:
#            modules_submenu.append([_module.name_nice, False,
#                                    aURL(c=module, f="index")])
#        else:
#            authorised = False
#            groups = re.split("\|", _module.access)[1:-1]
#            for group in groups:
#                if s3_has_role(group):
#                    authorised = True
#            if authorised == True:
#                modules_submenu.append([_module.name_nice, False,
#                                        URL(c=module, f="index")])
#if modules_submenu:
    # Only show the 'more' menu if there are entries in the list
#    module_more_menu = ([T("more"), False, "#"])
#    module_more_menu.append(modules_submenu)
#    s3.menu_modules.append(module_more_menu)

# Admin always last
if s3_has_role(ADMIN):
    _module = deployment_settings.modules["admin"]
    s3.menu_admin = [_module.name_nice, True,
                     URL(c="admin", f="index"), [
                        [T("Settings"), False, URL(c="admin", f="settings")],
                        [T("Users"), False, URL(c="admin", f="user")],
                        [T("Database"), False, URL(c="appadmin", f="index")],
                        [T("Import"), False, URL(c="admin", f="import_file")],
                        [T("Synchronization"), False, URL(c="sync", f="index")],
                        [T("Tickets"), False, URL(c="admin", f="errors")],
                     ]]
else:
    s3.menu_admin = []

# -----------------------------------------------------------------------------
# Build overall menu out of components
response.menu = s3.menu_modules
#response.menu.append(s3.menu_help)
#response.menu.append(s3.menu_auth)
response.menu += s3.menu_auth
if deployment_settings.get_gis_menu():
    # Do not localize this string.
    s3.gis_menu_placeholder = "GIS menu placeholder"
    # Add a placeholder for the regions menu, which cannot be constructed
    # until the gis_config table is available. Put it near the language menu.
    response.menu.append(s3.gis_menu_placeholder)
if s3.menu_admin:
    response.menu.append(s3.menu_admin)
# this check is handled by s3tools for personal menu, 
# language select isn't rendered like other menu items in la
#if deployment_settings.get_L10n_display_toolbar():
#    response.menu.append(s3.menu_lang)


# Menu helpers ================================================================
def shn_menu(controller, postp=None, prep=None):
    """
        appends controller specific options to global menu
        picks up from 01_menu, called from controllers
        
        @postp - additional postprocessor, 
                 assuming postp acts on response.menu_options
        @prep  - pre-processor
        @ToDo: FIXIT - alter here when you alter controller name
    """
    if controller in s3_menu_dict:
        
        if prep:
            prep()
        
        # menu    
        menu_config = s3_menu_dict[controller]
        menu = menu_config["menu"]
        
        # role hooks
        if s3_has_role(AUTHENTICATED) and "on_auth" in menu_config:
            menu.extend(menu_config["on_auth"])
        
        if s3_has_role(ADMIN) and "on_admin" in menu_config:
            menu.extend(menu_config["on_admin"])
        
        if s3_has_role(EDITOR) and "on_editor" in menu_config:
            menu.extend(menu_config["on_editor"])
        
        # conditionals
        conditions = [x for x in menu_config if re.match(r"condition[0-9]+", x)]
        for condition in conditions:
            if menu_config[condition]():
                menu.extend(menu_config["conditional%s" % condition[9:]])
        
        needle = request["wsgi"]["environ"]["PATH_INFO"]
        for i in xrange(len(menu)):
            if str(menu[i][2]) in needle:
                menu[i][1]=True
                if len(menu[i]) >= 4:
                    # if has submenus to it
                    for j in xrange(len(menu[i][3])):
                        if str(menu[i][3][j][2]) == needle:
                            menu[i][3][j][1]=True
                            break
                break
                
        response.menu_options = menu
        
        if postp:
            postp()

# =============================================================================
# Role-dependent Menu options
# =============================================================================
if s3_has_role(ADMIN):
    pr_menu = [
            [T("Person"), False, aURL(f="person", args=None), [
                [T("New"), False, aURL(p="create", f="person", args="create")],
                [T("Search"), False, aURL(f="index")],
                [T("List All"), False, aURL(f="person")],
            ]],
            [T("Groups"), False, aURL(f="group"), [
                [T("New"), False, aURL(p="create", f="group", args="create")],
                [T("List All"), False, aURL(f="group")],
            ]],
        ]
else:
    pr_menu = []

req_menu = don_menu = vol_menu = master_menu = []
if not auth.is_logged_in():
    # No menus
    pass
elif s3_has_role(STAFF):
    req_menu = [
        [T("Requests"), False, aURL(c="req", f="req"), [
            [T("New"), False, aURL(p="create", c="req", f="req",
                                   args="create")],
            [T("List All"), False, aURL(c="req", f="req")],
            [T("List All Requested Resources"), False, aURL(c="req",
                                                        f="req_item")],
            [T("List All Requested Skills"), False, aURL(c="vol",
                                                         f="req_skill")],
            #[T("Search Requested Items"), False, aURL(c="req",
            #                                          f="req_item",
            #                                          args="search")],
        ]],
        [T("Commitments"), False, aURL(c="req", f="commit"), [
            [T("List All"), False, aURL(c="req", f="commit")]
        ]]
    ]
    don_menu = [
        [T("Requests for Donations"), False, aURL(c="don", f="req"), [
            #[T("Add New Request for Donation"), False, aURL(p="create", c="don", f="req",
            #                       args="create")],
            [T("Donations on Loan Report"), False, aURL(p="create", c="don", f="loan")],
        ]],
        [T("Corporations & Organizations"), False, aURL(c="don", f="organisation"), [
            [T("Add New Corporations / Organizations"), False, aURL(p="create", c="don", f="organisation",
                                   args="create")],
        ]],
        [T("Virtual Donation Inventory"), False, None, [
            [T("Goods"), False, aURL( c="don", f="don_item",
                                    vars = dict(item="goods")
                                    )],
            [T("Services"), False, aURL( c="don", f="don_item",
                                         vars = dict(item="services")
                                    )],
            [T("Facilities"), False, aURL( c="don", f="don_item",
                                           vars = dict(item="facilities")
                                           )],
            ]
        ],
        [T("Donation Drive"), False, aURL(c="don", f="collect"), [
            [T("Add New Donation Drive"), False, aURL(p="create", c="don", f="collect",
                                   args="create")],
        ]],
        [T("Voucher Distribution"), False, aURL(c="don", f="distribute"), [
            [T("Add New Voucher Distribution"), False, aURL(p="create", c="don", f="distribute",
                                   args="create")],
        ]],
    ]
    vol_menu = [
        [T("Requests for Volunteers"), False, aURL(c="vol", f="req"), [
            #[T("Add New Request for Volunteers"), False, aURL(p="create", c="vol", f="req",
            #                       args="create")],
            #[T("List All"), False, aURL(c="vol", f="req")],
        ]],
        [T("Volunteer List"), False, aURL(c="vol", f="person"), [
            #[T("List All"), False, aURL(c="vol", f="person")],
        ]],
        #[T("Completed Activities"), False, aURL(c="vol", f="activity"), [
        #    [T("Add New Completed Activities"), False, aURL(p="create", c="vol", f="activity",
        #                           args="create")],
        #    #[T("List All"), False, aURL(c="vol", f="activity")],
        #]],
        #[T("Organizations"), False, aURL(c="org", f="organisation"), [
        #    [T("List All"), False, aURL(c="org", f="organisation")],
        #]],
    ]
    master_menu = [
            [T("Events"),
             False, aURL(c="event", f="event"), [
                [T("New"),
                 False, aURL(p="create", c="event", f="event",
                             args="create")],
                [T("Search"),
                 False, aURL(c="event", f="event",
                             args="search")],
                [T("List All"),
                 False, aURL(c="event", f="event")],
            ]],
            [T("Incidents"),
             False, aURL(c="event", f="incident"), [
                [T("New"),
                 False, aURL(p="create", c="event", f="incident",
                             args="create")],
                #[T("Search"),
                # False, aURL(c="event", f="incident",
                #             args="search")],
                [T("List All"),
                 False, aURL(c="event", f="incident")],
            ]],
            [T("Organizations"),
             False, aURL(c="org", f="organisation"), [
                [T("New"),
                 False, aURL(p="create", c="org", f="organisation",
                             args="create")],
                [T("Search"),
                 False, aURL(c="org", f="organisation",
                             args="search")],
                [T("List All"),
                 False, aURL(c="org", f="organisation")],
            ]],
            [T("Staff"),
             False, aURL(c="hrm", f="human_resource"), [
                [T("New"),
                 False, aURL(p="create", c="hrm", f="human_resource",
                             args="create")],
                [T("Search"),
                 False, aURL(c="hrm", f="human_resource",
                             args="search")],
                [T("List All"),
                 False, aURL(c="hrm", f="human_resource")],
            ]],
            [T("Facilities"),
             False, aURL(c="org", f="office"), [
                [T("New"),
                 False, aURL(p="create", c="org", f="office",
                             args="create")],
                [T("Search"),
                 False, aURL(c="org", f="office",
                             args="search")],
                [T("List All"),
                 False, aURL(c="org", f="office")],
            ]],
            [T("Skills"),
             False, aURL(c="hrm", f="skill"), [
                [T("New"),
                 False, aURL(p="create", c="hrm", f="skill",
                             args="create")],
                [T("Search"),
                 False, aURL(c="hrm", f="skill",
                             args="search")],
                [T("List All"),
                 False, aURL(c="hrm", f="skill")],
            ]],
            [T("Goods"), 
             False, aURL( c="supply", f="item", vars = dict(item="goods") ), [
                [T("New"),
                 False, aURL(p="create", c="supply", f="item", vars = dict(item="goods"),
                             args="create")],
                [T("List All"),
                 False, aURL(c="supply", f="item", vars = dict(item="goods"))],
            ]],
            [T("Services"), 
             False, aURL( c="supply", f="item", vars = dict(item="services") ), [
                [T("New"),
                 False, aURL(p="create", c="supply", f="item", vars = dict(item="services"),
                             args="create")],
                [T("List All"),
                 False, aURL(c="supply", f="item", vars = dict(item="services"))],
            ]],
            [T("Facility Types"), 
             False, aURL( c="supply", f="item", vars = dict(item="facilities") ), [
                [T("New"),
                 False, aURL(p="create", c="supply", f="item", vars = dict(item="facilities"),
                             args="create")],
                [T("List All"),
                 False, aURL(c="supply", f="item", vars = dict(item="facilities"))],
            ]],
            [T("Resource Categories"),
             False, aURL(c="supply", f="item_category"), [
                [T("New"),
                 False, aURL(p="create", c="supply", f="item_category",
                             args="create")],
                [T("Search"),
                 False, aURL(c="supply", f="item_category",
                             args="search")],
                [T("List All"),
                 False, aURL(c="supply", f="item_category")],
            ]]
        ]
    if s3_has_role(ADMIN):
        master_menu.append(
            [T("Users"),
             False, aURL(c="admin", f="user"), [
                [T("New"),
                 False, aURL(p="create", c="admin", f="user",
                             args="create")],
                #[T("Search"),
                # False, aURL(c="admin", f="user",
                #             args="search")],
                [T("List All"),
                 False, aURL(c="admin", f="user")],
            ]])
elif s3_has_role(BOC):
    req_menu = [
        [T("Requests"), False, aURL(c="req", f="req"), [
            [T("New"), False, aURL(p="create", c="req", f="req",
                                   args="create")],
            [T("List All"), False, aURL(c="req", f="req")],
            [T("List All Requested Items"), False, aURL(c="req",
                                                        f="req_item")],
            #[T("Search Requested Items"), False, aURL(c="req",
            #                                          f="req_item",
            #                                          args="search")],
        ]],
        [T("Commitments"), False, aURL(c="req", f="commit"), [
            [T("List All"), False, aURL(c="req", f="commit")]
        ]]
    ]
    don_menu = [
        [T("Requests for Donations"), False, aURL(c="don", f="req"), [
            [T("Donations on Loan Report"), False, aURL(p="create", c="don", f="loan")],
        ]],
        [T("Corporations & Organizations"), False, aURL(c="don", f="organisation"), [
            [T("Add New Corporations & Organizations"), False, aURL(p="create", c="don", f="organisation",
                                   args="create")],
        ]],
        [T("Virtual Donation Inventory"), False, None, [
            [T("Goods"), False, aURL( c="don", f="don_item",
                                    vars = dict(item="goods")
                                    )],
            [T("Services"), False, aURL( c="don", f="don_item",
                                         vars = dict(item="services")
                                    )],
            [T("Facilities"), False, aURL( c="don", f="don_item",
                                           vars = dict(item="facilities")
                                           )],
            ]
        ],
        [T("Donation Drive"), False, aURL(c="don", f="collect"), [
            [T("Add New Donation Drive"), False, aURL(p="create", c="don", f="collect",
                                   args="create")],
        ]],
        [T("Voucher Distribution"), False, aURL(c="don", f="distribute"), [
            [T("Add New Voucher Distribution"), False, aURL(p="create", c="don", f="distribute",
                                   args="create")],
        ]],
    ]
    master_menu = [
            [T("Organizations"),
             False, aURL(c="org", f="organisation"), [
                [T("New"),
                 False, aURL(p="create", c="org", f="organisation",
                             args="create")],
                [T("Search"),
                 False, aURL(c="org", f="organisation",
                             args="search")],
                [T("List All"),
                 False, aURL(c="org", f="organisation")],
            ]],
            [T("Staff"),
             False, aURL(c="hrm", f="human_resource"), [
                [T("New"),
                 False, aURL(p="create", c="hrm", f="human_resource",
                             args="create")],
                [T("Search"),
                 False, aURL(c="hrm", f="human_resource",
                             args="search")],
                [T("List All"),
                 False, aURL(c="hrm", f="human_resource")],
            ]],
            [T("Facilities"),
             False, aURL(c="org", f="office"), [
                [T("New"),
                 False, aURL(p="create", c="org", f="office",
                             args="create")],
                [T("Search"),
                 False, aURL(c="org", f="office",
                             args="search")],
                [T("List All"),
                 False, aURL(c="org", f="office")],
            ]],
            [T("Goods"), 
             False, aURL( c="don", f="don_item", vars = dict(item="goods") ), [
                [T("New"),
                 False, aURL(p="create", c="don", f="don_item", vars = dict(item="goods"),
                             args="create")],
                [T("Search"),
                 False, aURL(c="don", f="don_item", vars = dict(item="goods"),
                             args="search")],
                [T("List All"),
                 False, aURL(c="don", f="don_item", vars = dict(item="goods"))],
            ]],
            [T("Services"), 
             False, aURL( c="don", f="don_item", vars = dict(item="services") ), [
                [T("New"),
                 False, aURL(p="create", c="don", f="don_item", vars = dict(item="services"),
                             args="create")],
                [T("List All"),
                 False, aURL(c="don", f="don_item", vars = dict(item="services"))],
            ]],
            [T("Facility Types"), 
             False, aURL( c="don", f="don_item", vars = dict(item="facilities") ), [
                [T("New"),
                 False, aURL(p="create", c="don", f="don_item", vars = dict(item="facilities"),
                             args="create")],
                [T("List All"),
                 False, aURL(c="don", f="don_item", vars = dict(item="facilities"))],
            ]],
            [T("Resource Categories"),
             False, aURL(c="supply", f="item_category"), [
                [T("New"),
                 False, aURL(p="create", c="supply", f="item_category",
                             args="create")],
                [T("List All"),
                 False, aURL(c="supply", f="item_category")],
            ]],
        ]
elif s3_has_role(ORG_VOL) and not s3_has_role(ADMIN):
    vol_menu = [
        [T("Requests for Volunteers"), False, aURL(c="vol", f="req_skill")],
        [T("Organization Assignments"), False, aURL(c="vol", f="assignment"), [
            [T("Current Assignments"), False, aURL(c="vol", f="assignment",
                                                   vars=dict(show="current"))],
            [T("Past Assignments"), False, aURL(c="vol", f="assignment",
                                                vars=dict(show="past"))],
        ]],
        #[T("Organization Activities"), False, aURL(c="vol", f="activity")],
        [T("Organization Profile"), False, URL(c="vol", f="organisation",
                                               args=[auth.user.organisation_id])],
    ]
elif s3_has_role(ORG_DON):
    # Add Don menu later, so that can co-exist with Vol
    pass
else:
    # Volunteers
    vol_menu = [
        [T("Requests for Volunteers"), False, aURL(c="vol", f="req_skill")],
        [T("My Assignments"), False, aURL(c="vol", f="assignment"), [
            [T("Current Assignments"), False, aURL(c="vol", f="assignment",
                                                   vars=dict(show="current"))],
            [T("Past Assignments"), False, aURL(c="vol", f="assignment",
                                                vars=dict(show="past"))],
        ]],
        [T("My Profile"), False, URL(c="vol", f="profile"), [
            [T("Skills"), False, aURL(c="vol", f="skill", args=["my"])],
            [T("Emergency Contacts"), False, aURL(c="vol", f="contact",
                                                  args=["my"])],
        ]],
    ]

if s3_has_role(ORG_DON) and not s3_has_role(ADMIN):
    don_menu = []
    #don_menu = [
    #    #[T("Requests for Donations"), False, aURL(c="don", f="req")],
    #    #[T("Potential Items for Donation"), False, aURL(c="don", f="item")],
    #    [T("Organization Profile"), False, URL(c="don", f="organisation",
    #                                           args=[auth.user.organisation_id])],
    #]

# =============================================================================
# Settings-dependent Menu options
# =============================================================================
# CRUD strings for inv_recv
# (outside condtional model load since need to be visible to menus)
if deployment_settings.get_inv_shipment_name() == "order":
    ADD_RECV = T("Add Order")
    LIST_RECV = T("List Orders")
    s3.crud_strings["inv_recv"] = Storage(
        title_create = ADD_RECV,
        title_display = T("Order Details"),
        title_list = LIST_RECV,
        title_update = T("Edit Order"),
        title_search = T("Search Orders"),
        subtitle_create = ADD_RECV,
        subtitle_list = T("Orders"),
        label_list_button = LIST_RECV,
        label_create_button = ADD_RECV,
        label_delete_button = T("Delete Order"),
        msg_record_created = T("Order Created"),
        msg_record_modified = T("Order updated"),
        msg_record_deleted = T("Order canceled"),
        msg_list_empty = T("No Orders registered")
    )
else:
    ADD_RECV = T("Receive Shipment")
    LIST_RECV = T("List Received Shipments")
    s3.crud_strings["inv_recv"] = Storage(
        title_create = ADD_RECV,
        title_display = T("Received Shipment Details"),
        title_list = LIST_RECV,
        title_update = T("Edit Received Shipment"),
        title_search = T("Search Received Shipments"),
        subtitle_create = ADD_RECV,
        subtitle_list = T("Received Shipments"),
        label_list_button = LIST_RECV,
        label_create_button = ADD_RECV,
        label_delete_button = T("Delete Received Shipment"),
        msg_record_created = T("Shipment Created"),
        msg_record_modified = T("Received Shipment updated"),
        msg_record_deleted = T("Received Shipment canceled"),
        msg_list_empty = T("No Received Shipments")
    )

# =============================================================================
# Default Menu Configurations for Controllers
# =============================================================================
"""
    Dict structure - 
        Key - controller name
        Value - Dict
            - menu      : default menu options
            - on_admin  : extensions for ADMIN role
            - on_editor : extensions for EDITOR role
        @NOTE: subject to change depending on changes in S3Menu / requirements
"""

s3_menu_dict = {

    # DOC / Document Library
    # -------------------------------------------------------------------------
    "doc": {
        "menu": [ 
            [T("Documents"), False, aURL(f="document"),[
                [T("New"), False, aURL(p="create", f="document", args="create")],
                [T("List All"), False, aURL(f="document")],
                #[T("Search"), False, aURL(f="ireport", args="search")]
            ]],
              [T("Photos"), False, aURL(f="image"),[
                [T("New"), False, aURL(p="create", f="image", args="create")],
                [T("List All"), False, aURL(f="image")],
                #[T("Search"), False, aURL(f="ireport", args="search")]
            ]]],
    },

    # EVENT / Event Module
    # -------------------------------------------------------------------------
    "event": {
        "menu": master_menu,
    },

    # GIS / GIS Controllers
    # -------------------------------------------------------------------------
    "gis": {
        "menu": [
            #[T("Locations"), False, aURL(f="location"), [
            #    [T("New Location"), False, aURL(p="create", f="location",
            #                                    args="create")],
            #    [T("New Location Group"), False, aURL(p="create", f="location",
            #                                          args="create",
            #                                          vars={"group": 1})],
            #    [T("List All"), False, aURL(f="location")],
            #    [T("Search"), False, aURL(f="location", args="search")],
            #    #[T("Geocode"), False, aURL(f="geocode_manual")],
            #]],
            [T("Fullscreen Map"), False, aURL(f="map_viewing_client")],
            # Currently not got geocoding support
            #[T("Bulk Uploader"), False, aURL(c="doc", f="bulk_upload")]
        ],

        "condition1": lambda: not deployment_settings.get_security_map() or s3_has_role(MAP_ADMIN),
        "conditional1": [[T("Service Catalogue"), False, URL(f="map_service_catalogue")]]
    },

    # HRM
    # -------------------------------------------------------------------------
    "hrm": {
        "menu": master_menu,
    },

    # INV / Inventory
    # -------------------------------------------------------------------------
    "inv": {
        "menu": [
                #[T("Home"), False, aURL(c="inv", f="index")],
                [T("Warehouses"), False, aURL(c="inv", f="warehouse"), [
                    [T("New"), False, aURL(p="create", c="inv",
                                           f="warehouse",
                                           args="create")],
                    [T("List All"), False, aURL(c="inv", f="warehouse")],
                    [T("Search"), False, aURL(c="inv", f="warehouse",
                                              args="search")],
                    [T("Import"), False, aURL(p="create", c="inv", f="warehouse",
                                              args=["import.xml"])],
                ]],
                [T("Inventories"), False, aURL(c="inv", f="warehouse"), [
                    [T("Search Inventory Items"), False, aURL(c="inv", f="inv_item",
                                                              args="search")],
                    [s3.crud_strings.inv_recv.title_search, False, aURL(c="inv", f="recv",
                                                                 args="search")],
                    [T("Import"), False, aURL(p="create", c="inv", f="warehouse",
                                              args=["import.xml"],
                                              vars={"extra_data":True})],
                ]],
                [s3.crud_strings.inv_recv.subtitle_list, False, aURL(c="inv", f="recv"), [
                    [T("New"), False, aURL(p="create", c="inv",
                                           f="recv",
                                           args="create")],
                    [T("List All"), False, aURL(c="inv", f="recv")],
                    [s3.crud_strings.inv_recv.title_search, False, aURL(c="inv", f="recv",
                                             args="search")],
                ]],
                [T("Sent Shipments"), False, aURL(c="inv", f="send"), [
                    [T("New"), False, aURL(p="create", c="inv",
                                           f="send",
                                           args="create")],
                    [T("List All"), False, aURL(c="inv", f="send")],
                ]],
                [T("Resources"), False, aURL(c="supply", f="item"), [
                    [T("New"), False, aURL(p="create", c="supply",
                                           f="item",
                                           args="create")],
                    [T("List All"), False, aURL(c="supply", f="item")],
                    [T("Search"), False, aURL(c="supply", f="item",
                                             args="search")],
                ]],
                
                # Catalog Items moved to be next to the Item Categories
                #[T("Catalog Items"), False, aURL(c="supply", f="catalog_item"), [
                #    [T("New"), False, aURL(p="create", c="supply", f="catalog_item",
                #                          args="create")],
                #    [T("List All"), False, aURL(c="supply", f="catalog_item")],
                #    [T("Search"), False, aURL(c="supply", f="catalog_item",
                #                             args="search")],
                ##]],
                # 
                [T("Catalogs"), False, aURL(c="supply", f="catalog"), [
                    [T("New"), False, aURL(p="create", c="supply",
                                           f="catalog",
                                           args="create")],
                    [T("List All"), False, aURL(c="supply", f="catalog")],
                    #[T("Search"), False, aURL(c="supply", f="catalog",
                    #                         args="search")],
                ]]
            ],
        
        "on_admin": [[T("Resource Categories"), False, aURL(c="supply", f="item_category"), [
                [T("New Resource Category"), False, aURL(p="create",
                                                     c="supply",
                                                     f="item_category",
                                                     args="create")],
                [T("List All"), False, aURL(c="supply", f="item_category")]
            ]]]
    },

    # Master Data
    # -------------------------------------------------------------------------
    "master": {
        "menu": master_menu,
    },

    # MSG / Messaging Controller
    # -------------------------------------------------------------------------
    "msg": {
        "menu": [
            [T("Compose"), False, URL(c="msg", f="compose")],
            [T("Distribution groups"), False, aURL(f="group"), [
                [T("List/Add"), False, aURL(f="group")],
                [T("Group Memberships"), False, aURL(f="group_membership")],
            ]],
            [T("Log"), False, aURL(f="log")],
            [T("Outbox"), False, aURL(f="outbox")],
            #[T("Search Twitter Tags"), False, aURL(f="twitter_search"),[
            #    [T("Queries"), False, aURL(f="twitter_search")],
            #    [T("Results"), False, aURL(f="twitter_search_results")]
            #]],
            #["CAP", False, aURL(f="tbc")]
        ],
        
        "on_admin": [
            [T("Administration"), False, URL(f="#"), admin_menu_messaging],
        ]
    },

    # ORG / Organization Registry
    # -------------------------------------------------------------------------
    "org": {
        "menu": master_menu,
    },

    # PR / VITA Person Registry
    # --------------------------------------------------------------------------
    "pr": {
        "menu": pr_menu
    },

    # REQ / Request Management
    # -------------------------------------------------------------------------
    "req": {
        "menu": req_menu
    },

    # SYNC 
    # -------------------------------------------------------------------------
    "sync": {
        "menu": admin_menu_options
    },

    # DON / Donate 
    # -------------------------------------------------------------------------
    "don": {
        "menu": don_menu
    },

    # VOL / Volunteer
    # -------------------------------------------------------------------------
    "vol": {
        "menu": vol_menu
    },

    # ADMIN
    # -------------------------------------------------------------------------
    "admin": {
        "menu": admin_menu_options
    },

    "default": {
        "menu": [
            [T("Site"), False, aURL(c="default"),
            [
                [T("Sign in"), True, aURL(c="default", f="user", args="login")],
            ]
        ]]
    }
}

# Duplicate menus - some controllers might re-use menu defined in certain models
s3_menu_dict["appadmin"] = s3_menu_dict["admin"]
s3_menu_dict["supply"] = s3_menu_dict["master"]
s3_menu_dict["scenario"] = s3_menu_dict["event"]

# =============================================================================
# Enable for Testing Menus
#    return locals()
#globals().update(
#    _01_menu_definitions(**globals())
#)

# =============================================================================
# Breadcrumbs
# =============================================================================
def get_menu_label_and_state(menu_dict, # yikes
                             controller,
                             function,
                             args = None
                            ):
    """ Support Breadcrumbs """

    # Look at the menu for this Controller
    menu_spec = menu_dict[controller]["menu"]
    # Go through each entry in turn to find a match
    # Main menu
    for menu_item in menu_spec:
        (label, active, url) = menu_item[:3]
        if url:
            url_parts = url.split("/")[1:]
            # Check we're in the correct function
            url_app, url_controller, url_function = url_parts[:3]
            if url_function == function:
                if not args or url_parts[3:] == args:
                    # We found the correct menu entry
                    return label, active
        # Try the submenus
        try:
            submenus = menu_item[3]
        except IndexError:
            # No Submenus defined for this main menu
            pass
        else:
            for submenu_item in submenus:
                if submenu_item:
                    (sub_label, sub_active, sub_url) = submenu_item[:3]
                    if sub_url:
                        sub_url_parts = sub_url.split("/")[1:]
                        # Check we're in the correct function
                        sub_url_app, sub_url_con, sub_url_func = sub_url_parts[:3]
                        if sub_url_func == function:
                            if not args or sub_url_parts[3:] == args:
                                # We found the correct menu entry
                                return sub_label, sub_active

    return ("", False)

# -----------------------------------------------------------------------------
def define_breadcrumbs():
    breadcrumbs = [(deployment_settings.modules["default"].name_nice, True,
                    "/%s" % request.application)]
    if request.controller != "default":
        try:
            controllerLabel = deployment_settings.modules[request.controller].name_nice
        except KeyError:
            controllerLabel = "."
        breadcrumbs.append(
            (controllerLabel,
             True,
             "/%s/%s" % (request.application, request.controller)
            )
        )
    if request.function != "index":
        breadcrumbs.append(
            (get_menu_label_and_state(s3_menu_dict,
                                      request.controller,
                                      request.function) + \
             (URL(c=request.controller,
                  f=request.function),)
            )
        )
    if request.args(0):
        try:
            # Ignore this argument if it's the ID of a record
            int(request.args[0])
        except ValueError:
            breadcrumbs.append(
                (get_menu_label_and_state(s3_menu_dict,
                                          request.controller,
                                          request.function,
                                          request.args) + \
                 (URL(c=request.controller,
                      f=request.function,
                      args = request.args),)
                )
            )
    return breadcrumbs

breadcrumbs = define_breadcrumbs()

# END =========================================================================
