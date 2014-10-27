# -*- coding: utf-8 -*-

"""
    Donations
"""


module = request.controller
resourcename = request.function

# Options Menu (available in all Functions)
shn_menu(module)

# Load Models
load("don_collect")

# -----------------------------------------------------------------------------
def index():
    """ Custom View """
    if s3_has_role(STAFF) or s3_has_role(BOC):
        redirect(URL(f="req"))
    else:
        response.menu_options = []
        if session.s3.debug:
            s3.scripts.append( "%s/jquery.hoverIntent.js" % s3_script_dir )
        else:
            s3.scripts.append( "%s/jquery.hoverIntent.minified.js" % s3_script_dir )

        response.title = T("Donate")
        s3.jquery_ready.append(
'''$('.donate-popup').css('display','none')
$('.organizations-list li a').hoverIntent(donateFadeIn,donateFadeOut)''')
        s3.js_global.append(
'''function donateFadeIn(){$(this).next('.donate-popup').fadeIn()}
function donateFadeOut(){$(this).next('.donate-popup').fadeOut()}''')

        # Get Donation Drives List
        table = db.don_collect
        query = (table.end_datetime > request.utcnow) & \
                (table.deleted == False)
        rows = db(query).select(table.start_datetime,
                                table.end_datetime,
                                table.site_id,
                                orderby = table.start_datetime
                                )
        if rows:
            list = []
            offset = IS_UTC_OFFSET.get_offset_value(session.s3.utc_offset)
            if offset:
                timedelta = datetime.timedelta(seconds=offset)
            for row in rows:
                if offset:
                    start_datetime = row.start_datetime + timedelta
                    end_datetime = row.end_datetime + timedelta

                start_date = start_datetime.strftime("%b %d")
                start_time = start_datetime.strftime("%I:%M %p")
                end_date = end_datetime.strftime("%b %d")
                end_time = end_datetime.strftime("%I:%M %p")

                site = shn_site_represent(row.site_id, address = True)

                if start_date == end_date:
                    list.append(LI(SPAN(start_date, _class = "date"),
                                   " %s - %s" % (start_time, end_time),
                                   site,
                                   BR()
                                   )
                                )
                else:
                    list.append(LI(SPAN(start_date, _class = "date"),
                                   " %s - " % start_time,
                                   SPAN(end_date, _class = "date"),
                                   " %s" % end_time,
                                   site,
                                   BR()
                                   )
                                )
            donation_drives = TAG[""](*list)
        else:
            donation_drives = P(T("No Donation Drives Scheduled. Please check back later"))

        return dict(donation_drives = donation_drives)

# -----------------------------------------------------------------------------
def don_organisation_represent(id):
    """
        Represent a Donating Organisation
    """

    if isinstance(id, Row):
        # Do not repeat the lookup if already done by IS_ONE_OF or RHeader
        org = id
    else:
        table = db.org_organisation
        query = (table.id == id)
        org = db(query).select(table.name,
                               limitby=(0, 1)).first()
    if org:
        return A(org.name,
                 _href = URL(c="don", f="organisation", args = [id]))
    else:
        return NONE

# -----------------------------------------------------------------------------
def match():
    """
        Match Requests
    """

    # Get Req Resource Details
    tablename, req_id = request.vars.viewing.split(".")

    # create fake resource for rheader
    load("req_req")
    req = db(db.req_req.id == req_id).select(limitby=(0, 1)).first()
    r = Storage()
    r.record = req
    r.representation = "html"
    r.name = "don"
    r.function = "match"
    r.vars = request.vars
    rheader = req_rheader(r)

    # Get Item Filter
    req_item = db(db.req_req_item.req_id == req_id).select(db.req_req_item.item_id,
                                                           limitby=(0, 1)).first()
    if req_item:
        item_id = req_item.item_id
    else:
        item_id = None
    s3.filter = (db.don_don_item.item_id == item_id)

    # Configure don_don_item list
    db.don_don_item.organisation_id.represent = don_organisation_represent
    configure("don_don_item",
              insertable = False,
              list_fields = ["id",
                             "item_id",
                             "specs",
                             "item_pack_id",
                             "quantity",
                             "type",
                             "organisation_id",
                             (T("Contact Email"), "org_contact_email"),
                             (T("Org. Phone"), "org_phone"),
                             "comments"
                             ]
              )
    s3.actions = [dict(url = URL(c="don", f="req",
                                 args = [req_id, "commit"],
                                 vars = dict(don_item_id = "[id]")
                                 ),
                       _class = "action-btn",
                       label = str(T("Select")),
                       )
                    ]

    output = don_item()

    # Customize form
    output["rheader"] = rheader
    output["title"] = T("Request for Donations Details")
    output["subtitle"] = T("Matching Resources in Virtual Donation Inventory")
    s3.no_formats = True

    return output

# -----------------------------------------------------------------------------
def req_summary(r):
    """
    """

    rtable = db.req_req
    itable = db.req_req_item
    ctable = db.req_commit
    req = r.record
    item = req.req_req_item.select().first() or Storage()
    commit = req.req_commit.select().first() or Storage()

    item_str = s3.concat_item_pack_quantity(item.item,
                                            item.item_pack,
                                            item.quantity)

    summary = TABLE( TR( TH( rtable.status.label ),
                         rtable.status.represent(req.status),
                         TH( ctable.status.label ),
                         ctable.status.represent(commit.status),
                        ),
                     #TR( TH( rtable.event_id.label ),
                     #     rtable.event_id.represent(req.event_id),
                     #    TH( rtable.incident_id.label ),
                     #     rtable.incident_id.represent(req.incident_id),
                     #     ),
                     TR( TH( rtable.request_number.label ),
                         req.request_number,
                         TH( rtable.priority.label ),
                         rtable.priority.represent( req.priority ),
                        ),
                     TR( TH( rtable.date_required.label ),
                         req.date_required,
                         TH( rtable.site_id.label ),
                         rtable.site_id.represent( req.site_id ),
                        ),
                     TR( TH( itable.item.label ),
                         item_str,
                         TH( itable.item_id.label ),
                         itable.item_id.represent( item.item_id ),
                        ),
                     TR( 
                         TH( ctable.donated_by_id.label ),
                         ctable.donated_by_id.represent( commit.donated_by_id ),
                        ),
                     TR( #TH( rtable.purpose.label ),
                         #req.purpose,
                         TH( itable.specs.label ),
                         item.specs,
                        ),
                    )
    return summary

# -----------------------------------------------------------------------------
def req_form(r):
    """
    """

    form_btns = DIV(A(SPAN(T("Request for Donation Form"),
                             _class="wide-grey-button",
                             _style="display:inline-block;height:35px;margin-left:10px;vertical-align:bottom;"),
                    _href = URL(c=request.controller,
                                f="req_print",
                                args=r.id)
                    ),
                    # Also in controllers/vol.py - DRY
                    A(IMG(_src = "/%s/static/img/get_adobe_reader.png" % request.application,
                          _title = "%s - %s" % (T("Get Adobe Reader"),
                                                T("This link will open a new browser window.")),
                          _alt = T("Get Adobe Reader"),
                          _width = 158,
                          _height = 39,
                          _style = "float:right;"),
                      _href="http://www.adobe.com/products/acrobat/readstep2.html",
                      _target="_blank"),
                    )

    ftable = db.req_fulfill
    query = (ftable.req_id == r.id)
    frecord = db(query).select(limitby=(0, 1)).first()
    if frecord and frecord.datetime_fulfill != None:
        form_btns.append(A(SPAN(T("Donation Certificate"),
                                  _class="wide-grey-button",
                                  _style="display:inline-block;height:35px;margin-left:10px;vertical-align:bottom;"),
                           _href = URL(c = request.controller,
                                       f = "req_print",
                                       args = [r.id, True])
                          ))
    return form_btns

# -----------------------------------------------------------------------------
def req_rheader(r):
    """
        Resource Header for Requests for Donations
        - Staff View
    """

    record = r.record
    if r.representation == "html" and  record:
        tabs = [(T("Details"), None)]
        req_item_tab_label = T("Resource")
        tabs.append((req_item_tab_label, "req_item"))
        tabs.append((T("Find Match"), "match/"))
        if deployment_settings.get_req_use_commit():
            tabs.append((T("Donation"), "commit"))
        tabs.append(( T("Received"), "fulfill"))
        tabs.append(( T("Surplus"), "surplus_item"))
        if has_module("doc"):
            tabs.append((T("Documents"), "document"))

        rheader_tabs = s3_rheader_tabs(r, tabs)

        site_id = request.vars.site_id
        if site_id:
            site_name = shn_site_represent(site_id, show_link = False)
            commit_btn = TAG[""](
                        A( T("Commit from %s") % site_name,
                            _href = URL(c = "req",
                                        f = "commit_req",
                                        args = [r.id],
                                        vars = dict(site_id = site_id)
                                        ),
                            _class = "action-btn"
                           ),
                        A( T("Send from %s") % site_name,
                            _href = URL(c = "req",
                                        f = "send_req",
                                        args = [r.id],
                                        vars = dict(site_id = site_id)
                                        ),
                            _class = "action-btn"
                           )
                        )
        #else:
        #    commit_btn = A( T("Commit"),
        #                    _href = URL(c = "req",
        #                                f = "commit",
        #                                args = ["create"],
        #                                vars = dict(req_id = r.id)
        #                                ),
        #                    _class = "action-btn"
        #                   )
            s3.rfooter = commit_btn

        rheader = DIV( req_summary(r),
                       req_form(r)
                      )

        rheader.append(rheader_tabs)

        return rheader
    #else:
        # No Record means that we are either a Create or List Create
        # Inject the helptext script
        # Removed because causes an error if validation fails twice
        # return s3.req_helptext_script
    return None

# -----------------------------------------------------------------------------
def req():
    """
        /don/req
    """

    load("req_req")
    req_table = db.req_req

    req_type = 1
    req_table.type.default = req_type
    query = (db.req_req.type == req_type)
    if s3.filter:
        s3.filter = s3.filter & query
    else:
        s3.filter = query
    # -------------------------------------------------------------------------------------------
    configure("req_req",
              list_fields = ["id",
                             #"priority",
                             "status",
                             (T("BOC Status"), "req_commit_status"),
                             "date",
                             "created_on",
                             "date_required",
                             (T("Resource"), "item"),
                             "site_id",
                             ],
              sortby = [[3, "desc"]]
              )
                    
    if "iSortCol_0" not in request.vars:
        configure("req_req",
                  orderby= ~req_table.date )

    load("req_req")

    # -------------------------------------------------------------------------------------------
    ADD_ITEM_REQUEST = T("Make a Request for Donations")
    LIST_ITEM_REQUEST = T("List Requests for Donations")
    s3.crud_strings["req_req"] =  Storage(
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
        msg_list_empty = T("No Requests for Donations")
    )

    # Request for Donation labels
    req_table.purpose.label = T("What the Resources will be used for")
    req_table.site_id.label =T("Deliver To Facility")
    req_table.site_id.requires = IS_NULL_OR(req_table.site_id.requires)
    req_table.request_for_id.label = T("Deliver To Person")
    req_table.created_on.label = T("Pushed to BOC")
    req_table.created_on.represent = s3_utc_represent

    if "document" in request.args:
        load("doc_document")

    def prep(r):
        # Remove type from list_fields
        list_fields = s3mgr.model.get_config("req_req",
                                             "list_fields")
        try:
            list_fields.remove("type")
        except:
             # It has already been removed.
             # This can happen if the req controller is called
             # for a second time, such as when printing reports
             # see vol.print_assignment()
            pass
        configure(tablename, list_fields=list_fields)


        if r.interactive:
            # Set Fields and Labels
            req_table.type.readable = False
            req_table.type.writable = False

            if r.component and r.component.name == "req_item" and \
                deployment_settings.get_req_webeoc_is_master():
                # Disable Edit for fields where WebEOC is Master
                req_item_table = db.req_req_item
                req_item_table.item.writable = False
                req_item_table.specs.writable = False
                req_item_table.item_pack.writable = False
                req_item_table.quantity.writable = False

            if r.component and r.component.name == "fulfill" and \
                deployment_settings.get_req_webeoc_is_master():
                #configure("req_fulfill",
                #          insertable = False,
                #          editable = False
                #          )
                for field in db.req_fulfill:
                    field.writable = False
                    
            elif r.component and r.component.name == "surplus_item" and \
                deployment_settings.get_req_webeoc_is_master():
                for field in db.req_surplus_item:
                    field.writable = False

            #req_table.recv_by_id.label = T("Delivered To")
            # Update Donated By from selection on Match tab
            don_item_id = request.vars.don_item_id
            if r.component and r.component.name == "commit" and don_item_id:
                request.vars.pop("don_item_id")
                don_item_table = db.don_don_item
                don_item = db(don_item_table.id == don_item_id
                              ).select(don_item_table.organisation_id,
                                       don_item_table.specs ,
                                       don_item_table.pack_value ,
                                       limitby=[0,1]).first()
                if don_item:
                    req_commit_table = db.req_commit
                    req_commit_table.donated_by_id.default = don_item.organisation_id
                    req_commit_table.specs.default = don_item.specs
                    req_commit_table.pack_value.default = don_item.pack_value
                    db(req_commit_table.req_id == r.id).update(donated_by_id = don_item.organisation_id,
                                                               specs = don_item.specs,
                                                               pack_value = don_item.pack_value)
                    db.commit()

            if r.component and r.component.name == "req_item":
                s3mgr.s3.crud.submit_button = T("Save&Find Match")
                match_url = URL(c="don", f = "match",
                                vars = dict(viewing="req_req.%s" % r.id)
                                )
                configure("req_req_item",
                          update_next = match_url,
                          create_next = match_url
                          )

            if r.method != "update" and r.method != "read":
                if not r.component:
                    # Hide fields which don't make sense in a Create form
                    # - includes one embedded in list_create
                    # - list_fields over-rides, so still visible within list itself
                    s3.req_create_form_mods()

                    # Get the default Facility for this user
                    # @ToDo: Use site_id in User Profile (like current organisation_id)
                    if has_module("hrm"):
                        hrtable = db.hrm_human_resource 
                        query = (hrtable.person_id == s3_logged_in_person())
                        site = db(query).select(hrtable.site_id,
                                                limitby=(0, 1)).first()
                        if site:
                            r.table.site_id.default = site.site_id

                elif r.component.name == "document":
                    s3.crud.submit_button = T("Add")
                    table = r.component.table
                    # @ToDo: Fix for Link Table
                    #table.date.default = r.record.date
                    #if r.record.site_id:
                    #    stable = db.org_site
                    #    query = (stable.id == r.record.site_id)
                    #    site = db(query).select(stable.location_id,
                    #                            stable.organisation_id,
                    #                            limitby=(0, 1)).first()
                    #    if site:
                    #        table.location_id.default = site.location_id
                    #        table.organisation_id.default = site.organisation_id

                elif r.component.name == "req_item":
                    table = r.component.table
                    table.site_id.writable = table.site_id.readable = False
                    s3.req_hide_quantities(table)

        if r.component:
            if r.component.name == "document" or \
                 r.component.name == "req_item" or \
                 r.component.name == "req_skill":
                # Limit site_id to facilities the user has permissions for
                # @ToDo: Non-Item requests shouldn't be bound to a Facility?
                auth.permission.permitted_facilities(table=r.table,
                                                     error_msg=T("You do not have permission for any facility to make a request."))
        else:
            # Limit site_id to facilities the user has permissions for
            # @ToDo: Non-Item requests shouldn't be bound to a Facility?
            auth.permission.permitted_facilities(table=r.table,
                                                 error_msg=T("You do not have permission for any facility to make a request."))

        return True
    s3.prep = prep

    # Post-process
    def postp(r, output):
        if r.interactive:
            s3_action_buttons(r)
            if r.component and r.component.name == "req_item":
                req_item_don_item_btn = dict(url = URL(c = "req",
                                                       f = "req_item_don_item",
                                                       args = ["[id]"]
                                            ),
                     _class = "action-btn",
                     label = str(T("Find")), # Change to Fulfil? Match?
                     )
                s3.actions.append(req_item_don_item_btn)
        return output

    s3.postp = postp

    output = s3_rest_controller("req", "req", rheader=req_rheader)
    return output

# -----------------------------------------------------------------------------
def req_print():
    """ Print Donation Request Form """

    load("req_req")
    r = s3base.S3Request(s3mgr,
                         prefix="req",
                         name="req",
                         extension="pdf",
                         args = request.args[0])
    if len(request.args) > 1:
        s3mgr.configure("req_req",
                        callback = s3.donationCertificate,
                        formname = T("Donation Certificate"),
                        header = s3.donCertBorder,
                        footer = lambda x, y: None,
                        )
    else:
        s3mgr.configure("req_req",
                        callback = s3.donationRequest,
                        formname = T("Request for Donations"),
                        footer = s3.donationFooter
                        )
    return r()

# -----------------------------------------------------------------------------
def loan():
    """ Loans REST Controller """

    load("req_commit")
    ctable = db.req_commit

    # Filter for Loans
    s3.filter = (ctable.status == 9 )
    configure("req_commit",
              list_fields = ["donated_by_id",
                             "specs",
                             # Site virtual Field?
                             "datetime_return",
                             ],
              orderby = ["datetime_return"])
    output = s3_rest_controller("req", "commit")
    if isinstance(output, dict):
        output["title"] = T("Donations on Loan Report")
        output["subtitle"] = T("Donations on Loan")
    s3.actions = [dict(url = URL(c = "don",
                                 f = "req",
                                 args = ["commit","[id]"],
                                 ),
                       _class = "action-btn",
                       label = str(T("Open")),
                       ),
                    ]
    return output

# -----------------------------------------------------------------------------
configure("don_don_item",
          list_fields = ["id",
                         "organisation_id",
                         "item_category_id",
                         "item_id",
                         "item_pack_id",
                         "pack_value",
                         "quantity",
                         ]
          )

ADD_ITEM = T("Add Donation Resource")
LIST_ITEMS = T("List Donation Resources")
crud_strings["don_don_item"] = Storage(
    title_create = ADD_ITEM,
    title_display = T("Donation Resource Details"),
    title_list = LIST_ITEMS,
    title_update = T("Edit Donation Resource"),
    title_search = T("Search Donation Resources"),
    subtitle_create = ADD_ITEM,
    subtitle_list = T("Donation Resources"),
    label_list_button = LIST_ITEMS,
    label_create_button = ADD_ITEM,
    label_delete_button = T("Remove Donation Resource"),
    msg_record_created = T("Donation Resource Added"),
    msg_record_modified = T("Donation Resource updated"),
    msg_record_deleted = T("Donation Resource removed"),
    msg_list_empty = T("No Donation Resources for this Corporation"))

ADD_GOODS = T("In the event of a declared disaster we MAY be able to donate the following Goods:")
LIST_GOODS = T("List Donation Goods")
crud_strings["don_good"] = Storage(
    title_create = ADD_GOODS,
    title_display = T("Donation Good Details"),
    title_list = LIST_GOODS,
    title_update = T("Edit Donation Goods"),
    title_search = T("Search Donation Goods"),
    subtitle_create = ADD_GOODS,
    subtitle_list = T("Donate Goods"),
    label_list_button = LIST_GOODS,
    label_create_button = ADD_GOODS,
    label_delete_button = T("Remove Donation Goods"),
    msg_record_created = T("Donation Goods Added"),
    msg_record_modified = T("Donation Goods updated"),
    msg_record_deleted = T("Donation Goods removed"),
    msg_list_empty = T("No Donation Goods for this Corporation"))

ADD_SERVICE = T("In the event of a declared disaster we MAY be able to donate the following Services:")
LIST_SERVICES = T("List Donation Services")
crud_strings["don_service"] = Storage(
    title_create = ADD_SERVICE,
    title_display = T("Donation Service Details"),
    title_list = LIST_SERVICES,
    title_update = T("Edit Donation Service"),
    title_search = T("Search Donation Services"),
    subtitle_create = ADD_SERVICE,
    subtitle_list = T("Donate Services"),
    label_list_button = LIST_SERVICES,
    label_create_button = ADD_SERVICE,
    label_delete_button = T("Remove Donation Service"),
    msg_record_created = T("Donation Service Added"),
    msg_record_modified = T("Donation Service updated"),
    msg_record_deleted = T("Donation Service removed"),
    msg_list_empty = T("No Donation Services for this Corporation"))

ADD_FACILITY = T("In the event of a declared disaster we MAY be able to donate the following Facilities:")
LIST_FACILITYS = T("List Donation Facilities")
crud_strings["don_facility"] = Storage(
    title_create = ADD_FACILITY,
    title_display = T("Donation Facility Details"),
    title_list = LIST_FACILITYS,
    title_update = T("Edit Donation Facility"),
    title_search = T("Search Donation Facilities"),
    subtitle_create = ADD_FACILITY,
    subtitle_list = T("Donate Facilities"),
    label_list_button = LIST_FACILITYS,
    label_create_button = ADD_FACILITY,
    label_delete_button = T("Remove Donation Facility"),
    msg_record_created = T("Donation Facility Added"),
    msg_record_modified = T("Donation Facility updated"),
    msg_record_deleted = T("Donation Facility removed"),
    msg_list_empty = T("No Donation Facilities for this Corporation"))

# -----------------------------------------------------------------------------
def don_item_filter(don_item_add_filter_func):
    """
        Filter donated 'items' by category
            Services = category 'SERVICES'
            Facilities = category 'FACILITY'
            Goods = everything else
    """

    itable = db.don_don_item
    ctable = db.supply_item_category

    query = (ctable.code == "FACILITY")
    record = db(query).select(ctable.id,
                                       limitby = (0, 1),
                                       cache = gis.cache).first()
    if record:
        facility_cat_id = record.id
    else:
        facility_cat_id = None
        
    query = (ctable.code == "SERVICES")
    record = db(query).select(ctable.id,
                                       limitby = (0, 1),
                                       cache = gis.cache).first()
    if record:
        service_cat_id = record.id
    else:
        service_cat_id = None

    itable.organisation_id.widget = None # Implement SearchACWidget for Organisations
    itable.organisation_id.requires = IS_NULL_OR(IS_ONE_OF(db, "org_organisation.id",
                                                           organisation_represent,
                                                           orderby="org_organisation.name",
                                                           sort=True,
                                                           filterby = "has_items",
                                                           filter_opts = [True])
                                                 )
    itable.item_id.widget = None

    if not s3_has_role(STAFF):
        # Only Staff can add Categories
        itable.item_category_id.comment = ""
        # Only Staff can add Item Types
        # @ToDo: Allow adding Items to 'OTHER' category
        itable.item_id.comment = ""
        # Only Staff can add Item Units
        # @ToDo: Should Units for Services/Facilities be hardcoded/hidden?
        #        (always day/ea)
        comment = DIV(_class="tooltip",
                      _title="%s|%s" % (T("Resource Units"),
                                        T("The way in which an item is normally distributed")))
        script = SCRIPT(
'''S3FilterFieldChange({
 'FilterField':'item_id',
 'Field':'item_pack_id',
 'FieldResource':'item_pack',
 'FieldPrefix':'supply',
 'msgNoRecords':S3.i18n.no_packs,
 'fncPrep':fncPrepItem,
 'fncRepresent':fncRepresentItem
})''')
        itable.item_pack_id.comment = TAG[""](comment, script)

    item_type = request.vars.item
    itable.item_category_id.comment = None
    itable.item_id.comment = None
    if item_type == "goods":
        s3.crud_strings["don_don_item"] = s3.crud_strings["don_good"]
        itable.item_id.label = T("Type of Goods")
        itable.lead_time.readable = True
        itable.lead_time.writable = True
        itable.type.readable = True
        itable.type.writable = True
        itable.item_pack_id.readable = True
        itable.item_pack_id.writable = True
        itable.item_category_id.requires = IS_NULL_OR(IS_ONE_OF(db,
                                                    "supply_item_category.id",
                                                    "%(name)s",
                                                    not_filterby = "id",
                                                    not_filter_opts = [facility_cat_id, service_cat_id],
                                                    sort=True))
        #//'url':             S3.Ap.concat('/req/req_item_packs/'),
        #//'msgNoRecords':    S3.i18n.no_packs,
        #//'fncPrep':        fncPrepItem,
        #//'fncRepresent':    fncRepresentItem
        s3.jquery_ready = [
'''S3FilterFieldChange({
 'FilterField':'item_category_id',
 'Field':'item_id',
 'FieldResource':'item',
 'FieldPrefix':'supply',
})'''
]
        query = (itable.item_category_id != facility_cat_id) & \
                (itable.item_category_id != service_cat_id)
        don_item_add_filter_func( query )
    elif item_type in ["services", "facilities"]:
        if item_type == "services":
            s3.crud_strings["don_don_item"] = s3.crud_strings["don_service"]

            item_category_filter = service_cat_id
            itable.item_id.label = T("Service Type")
            if s3_has_role(STAFF):
                itable.item_id.comment = DIV(A(T("Add Service Type"),
                                             _class="colorbox",
                                             _href=URL(c="supply", f="item",
                                                       args="create",
                                                       vars=dict(format="popup")),
                                             _target="top",
                                             _title=T("Add Service Type")))
            itable.quantity.label = T("Duration of Donated Services")
            itable.item_pack_id.label = T("Unit of Time")
            itable.item_pack_id.readable = True
            itable.item_pack_id.writable = True
            itable.pack_value.label = T("Estimated Value ($) per Unit of Time")

        elif item_type == "facilities":
            s3.crud_strings["don_don_item"] = s3.crud_strings["don_facility"]

            item_category_filter = facility_cat_id
            itable.item_id.label = T("Facility Type")
            if s3_has_role(STAFF):
                itable.item_id.comment = DIV(A(T("Add Facility Type"),
                                             _class="colorbox",
                                             _href=URL(c="supply", f="item",
                                                       args="create",
                                                       vars=dict(format="popup")),
                                             _target="top",
                                             _title=T("Add Facility Type")))
            itable.specs.label = T("Specifications (Square Feet, Building Type, Stories, Services)")

        itable.item_category_id.readable = itable.item_category_id.writable = False
        itable.item_category_id.default = item_category_filter

        itable.item_id.requires = IS_ONE_OF(db, "supply_item.id",
                                            lambda id: s3.item_represent(id,
                                                            show_um = False,
                                                            show_link = False),
                                            filterby = "item_category_id",
                                            filter_opts = [item_category_filter],
                                            sort=True)

        query = (itable.item_category_id == item_category_filter)
        don_item_add_filter_func(query)

# -----------------------------------------------------------------------------
def organisation():
    """
        Corporation view of org_organisation
    """

    otable = db.org_organisation

    otable.acronym.readable = False
    otable.acronym.writable = False
    field = otable.sector_id
    field.readable = True
    field.writable = True
    field.label = T("Industry Sector")
    org_has_items_field = otable.has_items
    org_has_items_field.default = True
    s3.filter = (org_has_items_field == True)

    if not s3_has_role(STAFF):
        # Tweak the breadcrumb
        breadcrumbs[2] = (T("Organization Profile"), False,
                          URL(c=request.controller,
                              f=request.function,
                              args=request.args))

    def corporation_rheader(r, tabs = []):
        """ Corporation rheader """

        if r.representation == "html":

            if r.record is None:
                # List or Create form: rheader makes no sense here
                return None

            tabs = [(T("Basic Details"), None),
                    (T("Contacts"), "contact"),
                    (T("Donate Goods"), "don_item", dict(item="goods")),
                    (T("Donate Services "), "don_item", dict(item="services")),
                    (T("Donate Facilities "), "don_item", dict(item="facilities")),
                    ]
            if "register" not in request.vars:
                tabs.append( (T("Donations"), "commit") )
            rheader_tabs = s3_rheader_tabs(r, tabs)

            organisation = r.record
            if organisation.sector_id:
                _sectors = org_sector_represent(organisation.sector_id)
            else:
                _sectors = None

            sector_label = T("Industry Sector(s)")

            rheader = DIV(TABLE(
                TR(
                    TH("%s: " % T("Corporation")),
                    organisation.name,
                    TH("%s: " % sector_label),
                    _sectors
                    )),
                rheader_tabs
            )
            return rheader
        return None

    ADD_CORPORATION = T("Add Corporation / Organization")
    LIST_CORPORATIONS = T("List Corporations & Organizations")
    s3.crud_strings["org_organisation"] = Storage(
        title_create = ADD_CORPORATION,
        title_display = T("Corporation / Organization Details"),
        title_list = LIST_CORPORATIONS,
        title_update = T("Edit Corporation / Organization"),
        title_search = T("Search Corporations & Organizations"),
        subtitle_create = T("Add New Corporation / Organization"),
        subtitle_list = T("Corporations & Organizations"),
        label_list_button = LIST_CORPORATIONS,
        label_create_button = ADD_CORPORATION,
        label_delete_button = T("Delete Corporation / Organization"),
        msg_record_created = T("Corporation / Organization added"),
        msg_record_modified = T("Corporation / Organization updated"),
        msg_record_deleted = T("Corporation / Organization deleted"),
        msg_list_empty = T("No Corporations & Organizations currently registered"))

    def prep(r):
        don_item_filter(lambda query: \
                            r.resource.add_component_filter("don_item", query))
        if r.component:
            if r.component.name == "don_item":
                itable = db.don_don_item
                itable.currency.readable = False
            elif r.component.name == "human_resource":
                hrtable = db.hrm_human_resource
                hrtable.type.writable = hrtable.type.readable = False
                hrtable.status.writable = hrtable.status.readable = False
                hrtable.focal_point.writable = hrtable.focal_point.readable = False
                hrtable.job_title.readable = hrtable.job_title.writable = False
                s3.jquery_ready.append("$('#hrm_human_resource_person_id__row1').hide();")

                s3.crud_strings["hrm_human_resource"] = Storage(
                    title_create = T("Add Contact"),
                    title_display = T("Contact Details"),
                    title_list = T("Contacts"),
                    title_update = T("Edit Contact"),
                    title_search = T("Search Contacts"),
                    subtitle_create = T("Additional Contacts (optional)"),
                    subtitle_list = T("Contacts"),
                    label_list_button = T("List Contacts"),
                    label_create_button = T("Add Contacts"),
                    label_delete_button = T("Delete Contact"),
                    msg_record_created = T("Contact added"),
                    msg_record_modified = T("Contact updated"),
                    msg_record_deleted = T("Contact deleted"),
                    msg_no_match = T("No Contacts Found"),
                    msg_list_empty = T("Currently there are no Contact registered"))

                list_fields = s3mgr.model.get_config("hrm_human_resource", "list_fields")
                list_fields.remove("job_title")
                configure("hrm_human_resource",
                          list_fields = list_fields
                          )
            elif r.component.name == "contact":
                # Donation Organization Registration Workflow
                if "register" in request.vars:
                    # Only force the open on 1st run
                    s3.show_listadd = True
                    configure("org_contact",
                              create_next = URL(c="don", f="organisation",
                                                args = [r.record.id, "don_item"],
                                               vars = dict(item="goods"))
                              )
            elif r.component.name == "commit":
                s3.crud_strings["req_commit"].subtitle_list = T("Donations")
                configure("req_commit",
                          list_fields = ["req_id",
                                         "status",
                                         "donated_by_id",
                                         "datetime",
                                         (T("Donated Resource"),"item"),
                                         "specs",
                                         "quantity_commit",
                                         "pack_value",
                                         "datetime_available",
                                         "type",
                                         "loan_value",
                                         "return_contact_id",
                                         "site_id",
                                         "datetime_return",
                                         "return_penalty",
                                         "return_instruct",
                                         "insured",
                                         "insure_details",
                                         "warrantied",
                                         "warranty_details",
                                         "transport_req",
                                         "security_req",
                                         "committer_id",
                                         "upload",
                                         "upload_additional",
                                         "comments"
                                         ],
                          insertable = False,
                          editable = False,
                          deletable = False,
                          )
                    

    configure("org_organisation",
              list_fields = ["id",
                             "name",
                             #"type",
                             "sector_id",
                             "address",
                             "address_2",
                             "L3",
                             "L1",
                             "upload",
                             "phone",
                             (T("Contact Email"), "org_contact_email"),
                             #"country",
                             #"website"
                             ])

    # req CRUD strings
    REQ = T("Donation")
    #ADD_REQ = T("Add Donation")
    LIST_REQ = T("List Donations")
    s3.crud_strings["req_req"] = Storage(
        #title_create = ADD_REQ,
        title_display = T("Donation Details"),
        title_list = LIST_REQ,
        #title_update = T("Edit Donation"),
        title_search = T("Search Donations"),
        #subtitle_create = ADD_REQ,
        subtitle_list = T("Donations"),
        label_list_button = LIST_REQ,
        #label_create_button = ADD_REQ,
        #label_delete_button = T("Remove Donations"),
        #msg_record_created = T("Donation Added"),
        #msg_record_modified = T("Donation updated"),
        #msg_record_deleted = T("Donation removed"),
        msg_list_empty = T("No Donations from this Corporation"))

    return organisation_controller(organisation_rheader = corporation_rheader,
                                   org_prep = prep)

# -----------------------------------------------------------------------------
def don_item():
    """ REST Controller """

    def don_item_add_filter_func(query):
        s3.filter = query
    don_item_filter(don_item_add_filter_func)

    # Tweak the breadcrumb
    type = request.get_vars.item
    if type == "goods":
        label = T("Goods")
    elif type == "services":
        label = T("Services")
    elif type == "facilities":
        label = T("Facilities")
    else:
        # Error!
        label = ""
    breadcrumbs[2] = (label, False,
                      URL(c=request.controller,
                          f=request.function,
                          vars=request.vars))

    def postp(r, output):
        # maintain the ?items= type
        if "type" in request.vars:
            s3.actions = [
                dict(label=str(UPDATE),
                     _class="action-btn",
                     url=URL(args = ["[id]"] + ["update"],
                             vars=request.vars)),
            ]
        return output
    s3.postp = postp

    output = s3_rest_controller(module, "don_item")
    return output

# -----------------------------------------------------------------------------
def collect():
    """ REST Controller """

    def prep(r):
        configure("don_collect",
                  list_fields = ["id",
                                 "start_datetime",
                                 "end_datetime",
                                 "site_id",
                                 "organisation_id",
                                 ])
        return True

    s3.prep = prep
    output = s3_rest_controller(module, resourcename)
    return output

# -----------------------------------------------------------------------------
def distribute():
    """ REST Controller """

    output = s3_rest_controller(module, resourcename)
    return output

# END =========================================================================